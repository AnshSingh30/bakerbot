OVERLAY = {
    "business_id": "tinyd_lights",
    "business_name": "Tiny Delights",
    "location": "Jamshedpur",
    "instagram_handle": "@tinyd_lights",
    "avatar_url": "/avatars/tinyd_lights.jpg",   # drop the file in frontend/public/avatars/
    "brand_voice": (
        "Warm, proud of craft. 100% eggless, made from scratch, no premixes. "
        "Values quality and finishing over cheap pricing — never apologise for price."
    ),
    "signature_items": ["Engagement Cake", "Mermaid Theme Cake"],
    "always_eggless": True,          # if True, bot never offers an egg-based option
    "price_overrides": {},           # e.g. {"cakes": {"Red Velvet": {"1kg": 1100}}}
    "faq_overrides": {
        "eggless": "We bake 100% eggless only — from scratch, never premix.",
    },
    "extra_faq": {
        "premix": "No premixes, ever. Everything is made from scratch.",
    },
}
