import random, time, sys, os, math, textwrap

# import testing; input = testing.get_input # Comment out if not testing

__all__ = ["CONSTS", "currency", "directions", "print_slow", "input_slow", "table"]

CONSTS = {
    "speed": 0.0, "multiplier": 10,
    "available_commands": ["help", "stats", "save", "cls", "clear", "gifts", "location", "shop", "items"],
}

with open(os.path.join("data", "help.txt"), "r") as f:
    lines = f.read().rstrip().splitlines()
CONSTS["help_commands"] = {cmd: line for cmd, line in zip(CONSTS["available_commands"], lines)}

with open(os.path.join("data", "towns.txt"), "r") as f:
    text = f.read().rstrip()
town_info = text.split("\n\n")
CONSTS["towns"] = list(map(lambda x: x.split("\n"), town_info))

with open(os.path.join("data", "items.txt"), "r") as f:
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

punc = ".,?!:;\n"
directions = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
currency = random.choice(["Alyf", "Ryn", "Iysa"])

def print_slow(*args, sep=" ", end="\n", speed=CONSTS["speed"], multiplier=CONSTS["multiplier"]):
# def print_slow(*args, sep=" ", end="\n", speed=0, multiplier=10):
    for i, item in enumerate(args):
        for char in str(item):
            print(end=char)
            sys.stdout.flush()
            if char not in punc:
                time.sleep(speed)
            else:
                time.sleep(speed * multiplier)
        if i < len(args) - 1:
            for char in str(sep):
                print(end=char)
                sys.stdout.flush()
                if char not in punc:
                    time.sleep(speed)
                else:
                    time.sleep(speed * multiplier)
    for char in str(end):
        print(end=char)
        sys.stdout.flush()
        if char not in punc:
            time.sleep(speed)
        else:
            time.sleep(speed * multiplier)

def input_slow(text, speed=CONSTS["speed"], multiplier=CONSTS["multiplier"]):
# def input_slow(text, speed=0, multiplier=10):
    print_slow(end=text)
    return input()

def table(data, spaces):
    if sys.stdout.isatty():
        print_slow(textwrap.fill(
            ("\t" * spaces).join(data), width=os.get_terminal_size().columns, drop_whitespace=True))
    else:
        print_slow(("\t" * spaces).join(data))
