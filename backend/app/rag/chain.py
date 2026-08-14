"""The LCEL chat chain: retrieve -> deterministic lead-time verdict -> one LLM call
that returns the reply and the order slots together -> price guard."""
import re
import traceback
from datetime import date
from functools import lru_cache

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..catalog.merge import get_business, prices
from ..config import get_llm
from ..logic import lead_time
from ..logic.order_intent import BotTurn, merge_slots, to_draft
from ..models import ChatResponse
from .retriever import retrieve

SYSTEM = """You are the WhatsApp ordering assistant for {business_name}, a home bakery in {location}.
Today is {today} ({weekday}).

BRAND VOICE: {brand_voice}
{eggless_rule}

RULES
- Answer ONLY from the CATALOG CONTEXT below. Never invent an item, a price or a policy.
- Never write a rupee figure that does not appear verbatim in the context. If the price isn't
  there, ask which item and size they want instead of guessing.
- If something is not on the menu, say so plainly and suggest the closest thing that IS on it.
  Set grounded=false whenever you decline or cannot answer from the context.
- Reply in the customer's language: English, Hindi or Hinglish. Match how they write — if they
  type Hinglish in Latin script, answer in Latin script. Never switch them to Devanagari.
- WhatsApp length: 2-4 short lines. No bullet points unless you are listing menu items.
  No markdown, no headings, no emoji spam (one is fine).
- Never promise a date that the LEAD TIME CHECK says is impossible. Follow that check exactly.
- Fill in every order slot you know. Set ready=true only once item, size/quantity, delivery date
  and delivery area are all known and the date passes the lead-time check — then summarise the
  order in one line and ask them to confirm.

CATALOG CONTEXT
{context}

LEAD TIME CHECK
{lead_note}

ORDER SO FAR
{slots}"""

PRICE_RE = re.compile(r"(?:₹|\brs\.?|\binr)\s*([\d,]{2,7})|\b([\d,]{3,7})\s*(?:rs\b|rupees|/-)", re.I)

SESSIONS: dict[str, dict] = {}   # session_id -> {"history": [...], "slots": {}, "category": str}


@lru_cache
def _chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM),
        MessagesPlaceholder("history"),
        ("human", "{message}"),
    ])
    # function_calling, not the json_schema default: the free models support tools but several
    # ignore response_format and hand back prose.
    return prompt | get_llm().with_structured_output(BotTurn, method="function_calling")


def unverified_prices(text: str, allowed: set[int]) -> list[int]:
    """Rupee figures in `text` that aren't a catalog price (or a whole multiple of one)."""
    bad = []
    for match in PRICE_RE.finditer(text):
        value = int((match.group(1) or match.group(2)).replace(",", ""))
        if any(value == p * n for p in allowed for n in range(1, 13)):
            continue
        bad.append(value)
    return bad


def respond(business_id: str, session_id: str, message: str) -> ChatResponse:
    business = get_business(business_id)
    session = SESSIONS.setdefault(session_id, {"history": [], "slots": {}, "category": None})

    # Retrieve on the message PLUS the item already being discussed — otherwise a follow-up
    # like "next Wednesday, Bistupur" retrieves no cake chunk and the bot declares its own
    # item off-menu.
    known = " ".join(str(session["slots"][k]) for k in ("item", "flavour") if session["slots"].get(k))
    docs = retrieve(business_id, f"{known} {message}".strip(), k=5)
    category = next((d.metadata["category"] for d in docs if d.metadata["kind"] == "item"),
                    session["category"])
    session["category"] = category

    requested = lead_time.parse_date(message)
    if requested is None and session["slots"].get("delivery_date"):
        requested = date.fromisoformat(session["slots"]["delivery_date"])
    verdict = lead_time.evaluate(business, category, requested)

    today = date.today()
    inputs = {
        "business_name": business["business_name"],
        "location": business.get("location", ""),
        "brand_voice": business.get("brand_voice", ""),
        "eggless_rule": ("EGG RULE: this bakery is 100% eggless. Never offer an egg-based option."
                         if business.get("always_eggless") else
                         "EGG RULE: both eggless and egg-based are available; ask their preference."),
        "today": today.isoformat(),
        "weekday": today.strftime("%A"),
        "context": "\n".join(f"- {d.page_content}" for d in docs),
        "lead_note": lead_time.describe(verdict),
        "slots": session["slots"] or "nothing yet",
        "history": session["history"],
        "message": message,
    }
    turn = None
    for attempt in range(2):        # free models 429 and sometimes skip the tool call entirely
        try:
            turn = _chain().invoke(inputs)
            if turn is None:
                raise ValueError("model answered without calling the tool")
            break
        except Exception as exc:
            traceback.print_exc()   # a prospect never sees this; the terminal does
            last_error = exc
    if turn is None:
        return ChatResponse(
            reply="Sorry, I missed that — could you send it once more?",
            grounded=False, sources=[str(last_error)[:200]])

    reply, grounded = turn.reply.replace("�", ""), turn.grounded
    if unverified_prices(reply, prices(business_id)):
        # ponytail: guard, not repair — one clarifying question beats a hallucinated price.
        reply = "Let me get you the exact price — which item and what size were you looking for?"
        grounded = False

    session["slots"] = merge_slots(session["slots"], turn)
    if session["slots"].get("item") in business["catalog"] and session["slots"].get("flavour"):
        session["slots"]["item"] = session["slots"]["flavour"]   # model filed the category as the item
    if requested is not None:
        session["slots"]["delivery_date"] = requested.isoformat()   # the parser, not the model
    if verdict and verdict.get("ok") is False:
        session["slots"].pop("delivery_date", None)
        turn.ready = False
    session["history"] = (session["history"] + [HumanMessage(message), AIMessage(reply)])[-20:]

    return ChatResponse(
        reply=reply,
        order_draft=to_draft(session["slots"], category) if turn.ready else None,
        grounded=grounded,
        sources=[d.metadata.get("item", "") for d in docs],
    )
