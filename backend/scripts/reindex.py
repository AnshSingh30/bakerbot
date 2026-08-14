"""Rebuild the Chroma collection for one business (or all of them).

    python scripts/reindex.py --business tinyd_lights
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.catalog.merge import list_businesses          # noqa: E402
from app.rag.ingest import reindex                     # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--business", default=None, help="overlay id; omit for all")
args = parser.parse_args()

for business_id in [args.business] if args.business else list_businesses():
    print(f"{business_id}: {reindex(business_id)} chunks indexed")
