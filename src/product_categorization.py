
import pandas as pd



CATEGORY_RULES = {
    "Kitchen and Dining": [
        "MUG", "CUP", "PLATE", "BOWL", "CUTLERY",
        "TEASPOON", "KETTLE", "TEAPOT", "COASTER",
        "NAPKIN", "TABLECLOTH", "RECIPE BOX",
    ],
    "Home and Decor": [
        "CANDLE", "LANTERN", "ORNAMENT", "VASE",
        "FRAME", "HOLDER", "MIRROR", "HANGER",
        "HEART T-LIGHT", "WALL ART", "DOORMAT",
        "NESTING BOX", "BIRD ORNAMENT",
    ],
    "Clothing and Textiles": [
        "SCARF", "GLOVE", "APRON", "WOOLLY",
        "KNITTED", "CUSHION", "BLANKET", "TOWEL",
        "HOT WATER BOTTLE", "HAND WARMER",
    ],
    "Stationery and Paper": [
        "PAPER", "ENVELOPE", "NOTEBOOK", "PEN ",
        "PENCIL", "BOOKMARK", "WRITING SET",
        "GREETING CARD", "POSTCARD",
    ],
    "Accessories": [
        "BAG", "PURSE", "WALLET", "UMBRELLA",
        "KEYRING", "JEWELLERY", "JEWELRY",
        "BROOCH", "WATCH",
    ],
    "Toys and Games": [
        "DOLL", "TEDDY", "PUZZLE", "JIGSAW",
        "BUILDING BLOCK", "GAME", "TOY", "PLAYHOUSE",
    ],
    "Gifts and Seasonal": [
        "CHRISTMAS", "EASTER", "GIFT", "BABUSHKA",
        "UNION JACK", "UNION FLAG", "VALENTINE",
        "FESTIVE", "PARTY",
    ],
}



def assign_category(description):
    """Assign a broad category using transparent keyword rules."""

    if pd.isna(description) or not str(description).strip():
        return "Unclassified"

    text = str(description).upper()

    matches = [
        category
        for category, keywords in CATEGORY_RULES.items()
        if any(keyword in text for keyword in keywords)
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        return "Needs Review"

    return "Other / Unclassified"


def add_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with derived product categories."""

    if "Description" not in df.columns:
        raise ValueError("Description column is required.")

    result = df.copy()
    result["Category"] = result["Description"].apply(assign_category)

    return result
