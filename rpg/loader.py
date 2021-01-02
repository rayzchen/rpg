import os
import random
import sys

CONSTS = {}

CONSTS = {
    "speed": 0.03, "multiplier": 10,
    "available_commands": [
        "help", "stats", "save", "cls", "clear", "gifts", "location", "shop", "items",
        "equipment", "sleep", "travel", "roam"],
    "currency": random.choice(["Alyf", "Ryn", "Iysa"]),
    "directions": [
        "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"],
}
if os.name == "nt":
    CONSTS["clear"] = "cls"
else:
    CONSTS["clear"] = "clear"

if "--test" in sys.argv or "-t" in sys.argv:
    CONSTS["speed"] = 0
    from . import tests
    input = tests.get_input  # Comment out if not testing
elif "--fast" in sys.argv or "-f" in sys.argv:
    CONSTS["speed"] = 0

directory = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(directory, "data", "help.txt"), "r") as f:
    lines = f.read().rstrip().splitlines()
CONSTS["help_commands"] = {cmd: line for cmd,
                           line in zip(CONSTS["available_commands"], lines)}

with open(os.path.join(directory, "data", "towns.txt"), "r") as f:
    text = f.read().rstrip()
town_info = text.split("\n\n")
CONSTS["towns"] = list(map(lambda x: x.split("\n"), town_info))

with open(os.path.join(directory, "data", "items.txt"), "r") as f:
    items = list(map(lambda x: x.split("\n"), f.read().rstrip().split("\n\n")))
CONSTS["items"] = []
for item in items:
    item_dict = {}
    for stat in item:
        stat_name = stat[:stat.index(": ")]
        stat_val = stat[stat.index(": ") + 2:]
        if stat_val.isdecimal():
            stat_val = int(stat_val)
        item_dict.update({stat_name: stat_val})
    CONSTS["items"].append(item_dict)

with open(os.path.join(directory, "data", "intro.txt"), "r") as f:
    CONSTS["intro"] = f.read().rstrip().splitlines()
