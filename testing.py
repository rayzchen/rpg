import os, shutil, sys
if os.path.isdir("save"):
    shutil.rmtree("save")

_n = 0
_items = [
    "Ray", "", "", # Initialization
    "help", "help gifts", "help x", "help help", # Help
    "stats", "stats attack", "stats defense", "stats money", "stats name", "stats experience", "stats x", # stats cmd
    "gifts", "gifts claim", "gifts x", "gifts 1", "gifts 2", "gifts claim 1", "gifts claim 2", "gifts claim 1", # gifts cmd
    "location", "location description", "location x", "location x x", # location cmd
    "shop", # Shop
    "items", "items 1", "items 2", "items x", # items cmd (shop)
    "info", "info 1", "info 2", "info x", # info cmd (shop)
    "buy", "buy 1", "y", "buy 2", "y", "buy 1", "buy x", "buy 3", # buy cmd (shop)
    "x", "exit", # illegal cmd and exiting shop
    "items", "items 1", "items 2", "items x", "items x x", "items stats", "items stats 1", "items stats 2", "items stats x", "x", # items cmd and illegal cmd
    "equipment", "equipment x", "equipment equip", "equipment equip 1", "equipment equip 2", "equipment equip 1", "equipment equip x", "equipment unequip", "equipment unequip sword", "equipment unequip shield", "equipment unequip x", # equipment cmd
    "save", "", "save", "1", "save 1", "n", "save 1", "y", # save cmd
]

if "--fast" in sys.argv or "-f" in sys.argv:
    _items = [
        "Ray", "", "", # Initialization
        "gifts claim 1", # Gifts
        "shop", "buy 1", "y", "buy 2", "y", "exit", # Shop
        "equipment equip 1", "equipment equip 2", # Equipment
        "hunting", "\n", "\n", "\n", "\n",
        "travel", "y", "travel", "102", "travel", "\n", # Travel
        "save 1", # Save
    ]

def get_input():
    global _n
    if _n >= len(_items):
        return input()
    else:
        if _items[_n] == "\n":
            _n += 1
            return input()
        print(_items[_n])
        _n += 1
        return _items[_n - 1]
