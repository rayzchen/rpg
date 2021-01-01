import random
import time
import sys
import os
import textwrap
import string
import inspect
import re

__all__ = ["CONSTS", "print_slow", "input_slow",
           "table", "clear", "strfdelta", "mainloop"]

CONSTS = {
    "speed": 0.03, "multiplier": 10,
    "available_commands": [
        "help", "stats", "save", "cls", "clear", "gifts", "location", "shop", "items", "equipment", "sleep", "travel", "hunting"],
    "currency": random.choice(["Alyf", "Ryn", "Iysa"]),
    "directions": ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"],
}
if os.name == "nt":
    CONSTS["clear"] = "cls"
else:
    CONSTS["clear"] = "clear"

if "--test" in sys.argv or "-t" in sys.argv:
    CONSTS["speed"] = 0
    import testing
    input = testing.get_input  # Comment out if not testing
elif "--fast" in sys.argv or "-f" in sys.argv:
    CONSTS["speed"] = 0

with open(os.path.join("data", "help.txt"), "r") as f:
    lines = f.read().rstrip().splitlines()
CONSTS["help_commands"] = {cmd: line for cmd,
                           line in zip(CONSTS["available_commands"], lines)}

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
def write_slow(item, speed, multiplier):
    for char in str(item):
        sys.stdout.write(char)
        sys.stdout.flush()
        if char not in punc:
            time.sleep(speed)
        else:
            time.sleep(speed * multiplier)

def print_slow(*args, sep=" ", end="\n", speed=CONSTS["speed"], multiplier=CONSTS["multiplier"]):
    for i, item in enumerate(args):
        write_slow(item, speed, multiplier)
        if i < len(args) - 1:
            write_slow(sep, speed, multiplier)
    for char in str(end):
        write_slow(end, speed, multiplier)

def input_slow(text, speed=CONSTS["speed"], multiplier=CONSTS["multiplier"]):
    write_slow(text, speed, multiplier)
    return input()

def table(data, spaces):
    if sys.stdout.isatty():
        print_slow(textwrap.fill(
            ("\t" * spaces).join(data), width=os.get_terminal_size().columns, drop_whitespace=True))
    else:
        print_slow(("\t" * spaces).join(data))

def clear():
    os.system(CONSTS["clear"])

def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta) * 60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta) * 3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta) * 86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta) * 604800

    f = string.Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

def mainloop(cls, prompt):
    while True:
        try:
            command = re.subn(
                " +", input_slow(prompt + "> ").lstrip().rstrip().lower(), " ")[0]
            cmd_args = command.split(" ")
        except KeyboardInterrupt:
            print()
            break
        except EOFError:
            break
        if not len(cmd_args[0]) or not cmd_args[0]:
            print()
            continue
        if cmd_args[0] == "exit":
            break
        if cmd_args[0] in cls.available_commands:
            func = getattr(cls, cmd_args[0])
            if len(inspect.signature(func).parameters) >= len(cmd_args) - 1:
                if not func(*cmd_args[1:]) == -1:
                    print()
                    continue
        print_slow("\"" + command + "\"", "is not a valid command!\n")
