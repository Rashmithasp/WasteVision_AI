GUIDANCE = {
    "plastic": {
        "status": "Often recyclable where accepted",
        "steps": "Empty and rinse containers when practical. Check the item’s resin type and your local program before putting it in recycling.",
    },
    "paper": {
        "status": "Often recyclable when clean and dry",
        "steps": "Keep paper and cardboard dry. Food-soiled or laminated items may need a different route; follow local instructions.",
    },
    "glass": {
        "status": "May be accepted in glass collection",
        "steps": "Separate by local rules and avoid placing broken glass loose in a recycling bin. Use safe wrapping and clearly label it if required.",
    },
    "metal": {
        "status": "Often recyclable where accepted",
        "steps": "Empty containers and check local guidance for cans, foil, scrap metal, and pressurized containers.",
    },
    "organic": {
        "status": "Compostable in suitable programs",
        "steps": "Use a home compost system or a designated food-scrap collection. Accepted materials vary, especially for cooked food and packaging.",
    },
    "electronic": {
        "status": "Special collection recommended",
        "steps": "Take devices and batteries to an authorized e-waste or battery collection point. Do not place batteries or electronics in household recycling.",
    },
    "mixed": {
        "status": "Separate materials if practical",
        "steps": "Check whether components can be separated safely. If not, consult your local waste authority for the correct route.",
    },
}

TIPS = {category: details["steps"] for category, details in GUIDANCE.items()}
