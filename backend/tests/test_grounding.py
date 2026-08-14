"""Offline checks for the two things that can embarrass the demo: invented prices
and impossible delivery dates. Live LLM checks run only if GOOGLE_API_KEY is set."""
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.catalog.merge import get_business, prices        # noqa: E402
from app.config import OPENROUTER_API_KEY                     # noqa: E402
from app.logic import lead_time                           # noqa: E402
from app.rag.chain import unverified_prices               # noqa: E402

BID = "tinyd_lights"
ALLOWED = prices(BID)


def test_catalog_prices_pass():
    assert not unverified_prices("1kg chocolate truffle is ₹900, half kg ₹500.", ALLOWED)
    assert not unverified_prices("2 boxes of brownies = ₹700", ALLOWED)   # 2 x 350


def test_invented_price_is_caught():
    assert unverified_prices("Sugar-free cake is ₹1,111 for 1kg.", ALLOWED) == [1111]
    assert unverified_prices("That'll be 1234 rupees.", ALLOWED) == [1234]


def test_overlay_merge():
    b = get_business(BID)
    assert b["faq"]["eggless"].startswith("We bake 100% eggless")
    assert "egg_option" not in b["faq"]                    # always_eggless drops it
    assert b["catalog"]["cakes"]["items"]["Chocolate Truffle"]["1kg"] == 900


def test_relative_dates():
    today = date(2026, 8, 14)                              # a Friday
    assert lead_time.parse_date("chahiye kal", today) == today + timedelta(days=1)
    assert lead_time.parse_date("parso chahiye", today) == today + timedelta(days=2)
    assert lead_time.parse_date("day after tomorrow", today) == today + timedelta(days=2)
    assert lead_time.parse_date("in 3 days", today) == today + timedelta(days=3)
    assert lead_time.parse_date("this Sunday", today) == date(2026, 8, 16)
    assert lead_time.parse_date("next Sunday", today) == date(2026, 8, 23)
    assert lead_time.parse_date("on the 25th", today) == date(2026, 8, 25)
    assert lead_time.parse_date("just asking about prices", today) is None


def test_fondant_tomorrow_is_refused_with_alternatives():
    today = date(2026, 8, 14)
    verdict = lead_time.evaluate(get_business(BID), "theme_cakes",
                                 today + timedelta(days=1), today)
    assert verdict["ok"] is False
    assert verdict["earliest"] == "2026-08-20"             # 6-day lead time
    assert verdict["alternatives"]                          # something IS possible tomorrow
    assert "Do NOT confirm" in lead_time.describe(verdict)


def test_lead_time_satisfied():
    today = date(2026, 8, 14)
    verdict = lead_time.evaluate(get_business(BID), "cakes", today + timedelta(days=4), today)
    assert verdict["ok"] is True
    assert "DATE OK" in lead_time.describe(verdict)


@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="needs OPENROUTER_API_KEY")
@pytest.mark.parametrize("question", [
    "1kg chocolate cake kitna hai?",
    "Sugar-free cake?",
    "Do you make avocado toast?",
    "Fondant unicorn cake for tomorrow",
])
def test_live_replies_never_invent_a_price(question):
    from app.rag.chain import respond

    reply = respond(BID, f"pytest-{question}", question).reply
    assert not unverified_prices(reply, ALLOWED), reply
