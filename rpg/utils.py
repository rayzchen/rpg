import time
import sys
import os
import textwrap
import string
import inspect
import re

from .loader import CONSTS

__all__ = ["CONSTS", "print_slow", "input_slow",
           "table", "clear", "strfdelta", "mainloop"]

if "--test" in sys.argv or "-t" in sys.argv:
    from . import tests
    input = tests.get_input  # Comment out if not testing

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
