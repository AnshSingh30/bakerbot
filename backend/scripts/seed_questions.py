"""The sanity-check script. Run before sending a demo link:

    python scripts/seed_questions.py --business tinyd_lights
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SEED_QUESTIONS = [
    "1kg chocolate cake kitna hai?",
    "Do you have eggless?",
    "Need a cake for tomorrow, possible?",
    "Fondant unicorn cake for my daughter's bday next Friday",
    "Do you do brownies?",
    "Plum cake available?",
    "Can you deliver to Bistupur?",
    "What's the advance?",
    "Do you make avocado toast?",            # must decline
    "Sugar-free cake?",                      # must decline, not invent
    "Red velvet 1.5kg ka price?",
    "Cupcakes ka box kitne ka hai?",
    "Engagement cake banate ho?",
    "Kal ke liye brownies mil jayenge?",
    "Photo print cake for 25th, how much?",
    "Half kg black forest, parso chahiye",
    "Do you take bulk orders for office?",
    "Cookies ka rate batao",
    "Anniversary cake with fondant, next Saturday, deliver to Sakchi",
    "Kya aap Zomato pe ho?",                 # must decline
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--business", default="tinyd_lights")
    args = parser.parse_args()

    from app.rag.chain import respond                   # noqa: E402

    for i, question in enumerate(SEED_QUESTIONS):
        answer = respond(args.business, f"seed-{i}", question)
        flag = "" if answer.grounded else "   [abstained — declined or couldn't confirm]"
        print(f"\n> {question}\n{answer.reply}{flag}")
        if answer.order_draft:
            print(f"  draft: {answer.order_draft.model_dump(exclude_none=True)}")
