import os
import random
import sys

split = lambda x: x.split("\n")

def load_stats(file):
    with open(os.path.join(CONSTS["home"], "data", file + ".txt"), "r") as f:
        text = list(map(split, f.read().rstrip().split("\n\n")))
    data = []
    for item in text:
        stats = {}
        for stat in item:
            stat_name = stat[:stat.index(": ")]
            stat_val = stat[stat.index(": ") + 2:]
            if stat_val.isdecimal():
                stat_val = int(stat_val)
            stats[stat_name] = stat_val
        data.append(stats)
    return data

CONSTS = {
    "home": os.path.dirname(os.path.abspath(__file__)),
    "speed": 0.03, "multiplier": 10,
    "available_commands": [
        "help", "stats", "save", "cls", "clear", "gifts", "location", "shop", "items",
        "equipment", "sleep", "travel", "roam"],
    "currency": random.choice(["Alyf", "Ryn", "Iysa"]),
    "directions": [
        "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"],
}
CONSTS.update({"towns": load_stats("towns"), "items": load_stats("items"),
               "monsters": load_stats("monsters")})
if os.name == "nt":
    CONSTS["clear"] = "cls"
else:
    CONSTS["clear"] = "clear"

starting_town = CONSTS["towns"].pop(0)
random.shuffle(CONSTS["towns"])
CONSTS["towns"].insert(0, starting_town)

if "--test" in sys.argv or "-t" in sys.argv:
    CONSTS["speed"] = 0
    from .tests import get_input
    input = get_input  # Comment out if not testing
elif "--fast" in sys.argv or "-f" in sys.argv:
    CONSTS["speed"] = 0

with open(os.path.join(CONSTS["home"], "data", "help.txt"), "r") as f:
    lines = f.read().rstrip().splitlines()
CONSTS["help_commands"] = {cmd: line for cmd,
                           line in zip(CONSTS["available_commands"], lines)}

with open(os.path.join(CONSTS["home"], "data", "intro.txt"), "r") as f:
    CONSTS["intro"] = f.read().rstrip().splitlines()
