"""Deterministic date parsing + lead-time verdict.

The LLM phrases the answer; it never decides whether a date is possible.
"""
import re
from datetime import date, timedelta

WEEKDAYS = {
    "monday": 0, "mon": 0, "tuesday": 1, "tue": 1, "tues": 1, "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thurs": 3, "friday": 4, "fri": 4, "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6, "somvar": 0, "mangalvar": 1, "budhvar": 2, "shukravar": 4,
    "shanivar": 5, "ravivar": 6, "itwar": 6,
}
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
WORD_NUMBERS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "ten": 10}


def parse_date(text: str, today: date | None = None) -> date | None:
    """Best-effort natural-language date -> date. None if nothing date-like."""
    t = today or date.today()
    s = text.lower()

    if re.search(r"\b(today|aaj|abhi|right now)\b", s):
        return t
    if re.search(r"\b(day after tomorrow|day after|parso|parsoon)\b", s):
        return t + timedelta(days=2)
    if re.search(r"\b(tomorrow|tommorow|tmrw|tmr|kal)\b", s):
        return t + timedelta(days=1)

    m = re.search(r"\b(?:in|after)\s+(\d+|a|one|two|three|four|five|six|seven|ten)\s+days?\b", s)
    if m:
        n = m.group(1)
        return t + timedelta(days=int(n) if n.isdigit() else WORD_NUMBERS[n])

    m = re.search(r"\b(?:in|after)\s+(\d+|a|one|two|three|four)\s+weeks?\b", s)
    if m:
        n = m.group(1)
        return t + timedelta(weeks=int(n) if n.isdigit() else WORD_NUMBERS[n])

    m = re.search(rf"\b(next|this|coming)?\s*({'|'.join(WEEKDAYS)})\b", s)
    if m:
        wd = WEEKDAYS[m.group(2)]
        days = (wd - t.weekday()) % 7 or 7
        # ponytail: "next Friday" in the same week -> the following week. Ambiguous in
        # real usage; the bot echoes the resolved date back so the customer can correct it.
        if m.group(1) == "next" and wd > t.weekday():
            days += 7
        return t + timedelta(days=days)

    m = re.search(rf"\b(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+({'|'.join(MONTHS)})\w*\b", s)
    if m:
        return _on(t, int(m.group(1)), MONTHS[m.group(2)])

    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)\b", s)
    if m:
        return _on(t, int(m.group(1)))

    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", s)   # 25/12
    if m:
        return _on(t, int(m.group(1)), int(m.group(2)))

    return None


def _on(today: date, day: int, month: int | None = None) -> date | None:
    """Next occurrence of day-of-month (optionally in a named month)."""
    for offset in range(14):                         # scan forward a year, month by month
        mon = (today.month - 1 + offset) % 12 + 1
        year = today.year + (today.month - 1 + offset) // 12
        if month and mon != month:
            continue
        try:
            d = date(year, mon, day)
        except ValueError:
            continue
        if d >= today:
            return d
    return None


def evaluate(business: dict, category: str | None, requested: date | None,
             today: date | None = None) -> dict | None:
    """None if there's nothing to check. Otherwise the verdict the prompt gets."""
    t = today or date.today()
    if not category or category not in business["catalog"]:
        return None
    lead = business["catalog"][category]["lead_time_days"]
    earliest = t + timedelta(days=lead)
    if requested is None:
        return {"category": category, "lead_days": lead, "requested": None,
                "ok": None, "earliest": earliest.isoformat(), "alternatives": []}

    days_available = (requested - t).days
    ok = days_available >= lead
    return {
        "category": category,
        "lead_days": lead,
        "requested": requested.isoformat(),
        "days_available": days_available,
        "ok": ok,
        "earliest": earliest.isoformat(),
        "alternatives": [] if ok else _alternatives(business, category, days_available),
    }


def _alternatives(business: dict, category: str, days_available: int) -> list[str]:
    """Items that CAN be made in time, closest categories first."""
    order = ["cakes", "plum_cake", "cupcakes", "brownies", "cookies", "pastries", "hampers"]
    out = []
    for cat in sorted(business["catalog"], key=lambda c: order.index(c) if c in order else 99):
        block = business["catalog"][cat]
        if cat == category or block["lead_time_days"] > max(days_available, 0):
            continue
        for item in list(block["items"])[:2]:
            out.append(f"{item} ({cat.replace('_', ' ')}, needs {block['lead_time_days']} day(s))")
        if len(out) >= 4:
            break
    return out[:4]


def pretty(iso: str) -> str:
    """'2026-08-19 (Wednesday)' — the weekday stops the model pairing the wrong day with a date."""
    return f"{iso} ({date.fromisoformat(iso).strftime('%A')})"


def describe(verdict: dict | None) -> str:
    if not verdict:
        return "No delivery date mentioned yet."
    if verdict["requested"] is None:
        return (f"Category '{verdict['category']}' needs {verdict['lead_days']} day(s); "
                f"earliest possible date is {pretty(verdict['earliest'])}. No date asked for yet.")
    if verdict["ok"]:
        return (f"DATE OK: {pretty(verdict['requested'])} is fine for '{verdict['category']}' "
                f"(needs {verdict['lead_days']} day(s)). Use exactly that date — do not shift it "
                f"by a day. You may proceed to confirm.")
    alts = "; ".join(verdict["alternatives"]) or "nothing in the catalog is fast enough"
    return (f"DATE NOT POSSIBLE: '{verdict['category']}' needs {verdict['lead_days']} day(s) but "
            f"{pretty(verdict['requested'])} is only {verdict['days_available']} day(s) away. "
            f"Do NOT confirm. Offer exactly two options: (a) the same item on "
            f"{pretty(verdict['earliest'])}, and (b) something that IS possible by "
            f"{pretty(verdict['requested'])}: {alts}.")
