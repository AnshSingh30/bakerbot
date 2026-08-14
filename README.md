# BakerBot — WhatsApp-style ordering assistant demo

A web app **styled to look like WhatsApp** (not a real WhatsApp bot) that answers a
bakery's customer questions from that bakery's own catalog, refuses dates it can't
deliver, and captures orders. Send the link to a prospect on Instagram; she opens it
on her phone and sees her own name and prices.

---

## Run it locally

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your OPENROUTER_API_KEY (https://openrouter.ai/keys)
uvicorn app.main:app --reload

# frontend (second terminal)
cd frontend
npm install
npm run dev                   # http://localhost:5173/?b=tinyd_lights
```

The vector store indexes itself on the first question — no setup step needed. Embeddings run
locally (all-MiniLM through the ONNX runtime chromadb already ships), so the only paid call is
the chat completion. First run downloads the ~80MB embedding model once.

Sanity-check before sending a link:

```bash
cd backend
python scripts/seed_questions.py --business tinyd_lights   # 20 real customer questions
pytest                                                     # grounding + lead-time checks
```

---

## Adding a new prospect in 10 minutes

1. Copy `backend/app/catalog/overlays/_template.py` → `overlays/<handle>.py` and fill in
   `business_id` (= filename), `business_name`, `location`, `brand_voice`,
   `signature_items`, plus any `price_overrides` / `faq_overrides` she's told you.
2. Drop her profile photo into `frontend/public/avatars/<handle>.jpg`.
3. Rebuild the index: `python scripts/reindex.py --business <handle>`
   (or hit `POST /api/admin/reindex/<handle>` with header `X-Admin-Token: $ADMIN_TOKEN`
   against the deployed backend).
4. Share `https://<deployment>/?b=<handle>`.

Everything not in the overlay is inherited from `backend/app/catalog/baseline.py`, so a
half-filled overlay still gives a complete, working demo.

---

## How it works

- `catalog/baseline.py` — shared India-market price list + FAQ, the default for every demo.
- `catalog/merge.py` — baseline + overlay → one business dict. `price_overrides` and
  `faq_overrides` replace, `extra_faq` appends, `always_eggless` drops the egg-based FAQ.
- `rag/ingest.py` — one atomic chunk per catalog item and per FAQ entry (small chunks
  retrieve far better than one menu blob), into a local persistent Chroma.
- `logic/lead_time.py` — **deterministic**. Parses "tomorrow / kal / parso / next Friday /
  25th / in 3 days", compares against the category's lead time, and hands the LLM a verdict.
  The model phrases the answer; it never decides whether a date is possible.
- `rag/chain.py` — retrieve top-5 → lead-time verdict → one LLM call returning the reply
  *and* the order slots → price guard that rejects any rupee figure not in the catalog
  (multiples allowed for quantities). `grounded: false` marks a reply that had to decline.
- Session memory is an in-process dict (last 10 turns + partial order). A restart loses it;
  that's fine for a demo.

The LLM is any **tool-calling** model on **OpenRouter** — OpenRouter speaks the OpenAI API, so
`get_llm()` in `backend/app/config.py` is `ChatOpenAI` plus a `base_url`. Tool calling is not
optional: the reply and the order slots come back as one structured-output call.

`LLM_MODEL` defaults to `nvidia/nemotron-3-super-120b-a12b:free`. Measured trade-off on the
seed questions:

| | free nemotron-120b | paid gemini-2.5-flash |
|---|---|---|
| Reply latency | ~26s | ~1.9s |
| Seed questions answered | 18/20 | 20/20 |
| Lead-time alternatives | sometimes muddled | correct |
| Cost | ₹0 | ~₹0.06 / message |

`FALLBACK_MODELS` is a comma-separated list OpenRouter routes to when the free pool returns 429.
To switch to paid, change one env var — no code change, no redeploy of the repo.

## API

| | |
|---|---|
| `GET /api/business/{id}` | header branding |
| `GET /api/catalog/{id}` | merged catalog for the carousel |
| `POST /api/chat` | `{business_id, session_id, message}` → `{reply, order_draft, grounded, sources}` |
| `POST /api/orders` | OrderDraft + name + phone → `{order_id, status}` |
| `GET /api/orders/{id}` | captured orders (proves order capture during the pitch) |
| `POST /api/admin/reindex/{id}` | rebuild the index, gated by `X-Admin-Token` |

## Deploy

- **Backend → Railway**: point it at `backend/`, set `OPENROUTER_API_KEY`, `ADMIN_TOKEN` and
  `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`. `railway.json` has the start command.
  Note: Chroma and SQLite live on the container's disk — attach a volume, or just re-index
  after a redeploy (it takes seconds).
- **Frontend → Vercel**: point it at `frontend/`, set `VITE_API_URL` to the Railway URL.

## Not in scope (deliberately)

No real WhatsApp Business API (that's the paid deliverable — Meta approval takes weeks),
no auth, no billing, no baker dashboard, no Redis/Postgres/Docker.
