import random, time, sys, os, math, textwrap

# import testing; input = testing.get_input # Comment out if not testing

__all__ = ["CONSTS", "currency", "directions", "print_slow", "input_slow", "table"]

CONSTS = {"speed": 0.0, "multiplier": 10}

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
