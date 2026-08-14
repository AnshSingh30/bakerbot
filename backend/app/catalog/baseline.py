BASELINE_CATALOG = {
    "cakes": {
        "unit": "per kg",
        "lead_time_days": 3,
        "items": {
            "Chocolate Truffle": {"0.5kg": 500, "1kg": 900, "1.5kg": 1600},
            "Red Velvet":        {"0.5kg": 550, "1kg": 950, "1.5kg": 1700},
            "Butterscotch":      {"0.5kg": 500, "1kg": 900, "1.5kg": 1500},
            "Pineapple":         {"0.5kg": 450, "1kg": 800, "1.5kg": 1300},
            "Black Forest":      {"0.5kg": 500, "1kg": 900, "1.5kg": 1600},
            "Vanilla":           {"0.5kg": 420, "1kg": 750, "1.5kg": 1250},
            "Mango (seasonal)":  {"0.5kg": 550, "1kg": 950, "1.5kg": 1650},
        },
    },
    "theme_cakes": {
        "unit": "custom quote",
        "lead_time_days": 6,
        "note": "Starting price shown; final quote depends on design complexity, tiers and toppers.",
        "items": {
            "Birthday Theme Cake":        {"starting_at": 1200},
            "Engagement / Anniversary":   {"starting_at": 2000},
            "Fondant Designer Cake":      {"starting_at": 2500},
            "Photo / Edible Print Cake":  {"starting_at": 1500},
            "Baby Shower Cake":           {"starting_at": 1500},
        },
    },
    "cupcakes": {
        "unit": "per box of 6",
        "lead_time_days": 1,
        "items": {"Chocolate": 280, "Red Velvet": 300, "Vanilla": 260, "Assorted": 320},
    },
    "brownies": {
        "unit": "per box of 4",
        "lead_time_days": 1,
        "items": {"Fudge Brownie": 350, "Walnut Brownie": 400, "Nutella Stuffed": 450},
    },
    "cookies": {
        "unit": "per box of 250g",
        "lead_time_days": 1,
        "items": {"Chocolate Chip": 300, "Shortbread": 320, "Assorted Cookies": 350},
    },
    "plum_cake": {
        "unit": "per 500g",
        "lead_time_days": 2,
        "note": "Dry cake, not cream-based. Festive and gift-friendly. Longer shelf life.",
        "items": {"Classic Plum Cake": 250, "Rich Fruit Plum Cake": 350},
    },
    "pastries": {
        "unit": "per piece",
        "lead_time_days": 1,
        "min_order_qty": 6,
        "items": {"Choco Lava Cake": 60, "Pastry Slice": 80, "Eclair": 90},
    },
    "hampers": {
        "unit": "per hamper",
        "lead_time_days": 4,
        "note": "Combination boxes for festivals and corporate gifting.",
        "items": {"Mini Festive Hamper": 700, "Premium Gift Hamper": 1500},
    },
}

BASELINE_FAQ = {
    "eggless": "Yes — everything on our menu is available eggless.",
    "egg_option": "We bake both eggless and egg-based. Just tell us your preference when ordering.",
    "delivery": "We deliver within the city. Share your area and we'll confirm availability and any delivery charge.",
    "payment": "We take 50% advance to confirm the order, balance on delivery. UPI accepted.",
    "customisation": "Yes — custom messages, colours, toppers and themes are all possible. Share a reference photo.",
    "cancellation": "Orders can be changed up to 48 hours before delivery. Advance is non-refundable inside 24 hours.",
    "bulk": "Yes, we take bulk and corporate orders. Please give us at least a week's notice.",
}
