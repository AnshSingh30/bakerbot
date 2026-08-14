"""Copy me to <instagram_handle>.py and fill in. Everything else is inherited
from baseline.py, so a blank-ish overlay already gives a working demo."""

OVERLAY = {
    "business_id": "",                # must match the filename, e.g. "sweet_crumbs"
    "business_name": "",              # shown in the WhatsApp header
    "location": "",                   # city
    "instagram_handle": "@",
    "avatar_url": "/avatars/<handle>.jpg",   # drop the photo in frontend/public/avatars/
    "brand_voice": (
        ""                            # 1-2 sentences: tone + what they're proud of
    ),
    "signature_items": [],            # appended to the catalog context, e.g. ["Bento Cake"]
    "always_eggless": False,          # True -> bot never offers an egg-based option
    "price_overrides": {},            # {"cakes": {"Red Velvet": {"1kg": 1100}}}
    "faq_overrides": {},              # replaces a baseline FAQ answer by key
    "extra_faq": {},                  # adds new FAQ entries, {"parking": "..."}
}
