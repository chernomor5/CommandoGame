# constants.py

TERRAIN_INDEX = {
    "sea": 0,
    "swamp": 1,
    "plain": 2,
    "forest": 3,
    "road": 4,
    "railroad": 5,
    "shore": 6,
    "building": 7,
}

BUILDING_TYPE = {
    "none": 0,
    "shop": 1,
    "hospital": 2,
    "bank": 3,
    "car_rental": 4,
    "train_station": 5,
    "airport": 6,
    "boat_rental": 7,
    "user_home": 8,
}

# ANSI escape codes for console coloring
class Ansi:
    RESET = "\033[0m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    DARK_GREEN = "\033[32;1m"
    YELLOW = "\033[33m"
    GRAY = "\033[90m"
    WHITE = "\033[37m"
    
# ASCII visualization rules
# Order matters: first match wins
ASCII_TILE_RULES = [
    ("building", "B", Ansi.WHITE),
    ("railroad", "#", Ansi.GRAY),
    ("road", "=", Ansi.YELLOW),
    ("swamp_forest", "S", Ansi.DARK_GREEN),
    ("swamp", "s", Ansi.GREEN),
    ("forest", "F", Ansi.DARK_GREEN),
    ("sea", "~", Ansi.BLUE),
    ("plain", ".", Ansi.GREEN),
]

BALANCE = {
    "h2h": {
        "walk_ap": 6,
        "swim_ap": 3,
        "stance_ap": 1,
    },
    "gun": {
        "range": 6,
    },
    "rocket": {
        "min_range": 2,
        "max_range": 19,
    },
}

# -------------------------------------------------
# Helicopter part constants
# -------------------------------------------------

HELICOPTER_COLORS = {"RED", "GREEN", "BLUE"}

MAX_PARTS_OF_COLOR = 2
MAX_PARTS = MAX_PARTS_OF_COLOR * len(HELICOPTER_COLORS)

