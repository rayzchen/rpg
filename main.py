import random, time, sys, os, pickle, math, inspect, textwrap, re

import testing; input = testing.get_input # Comment out if not testing

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
        print_slow(textwrap.fill(("\t" * spaces).join(data), width=os.get_terminal_size().columns, drop_whitespace=True))
    else:
        print_slow(("\t" * spaces).join(data))

class Game:

    available_commands = ["help", "stats", "save", "cls", "clear", "gifts", "location", "shop", "items"]
    help_commands = {
        "help": "Typing 'help' will display this help text. To get help with any commands, type 'help <command name>', replacing <command name> with the command you want help with.",
        "stats": "Typing 'stats' will display your current stats. Typing 'stats' and then one of 'name', 'health', 'experience', 'attack', 'defense', or 'money' will display that exact Stat.",
        "save": "Typing 'save' will save your current state to a folder named 'save'. The save name will be called 'save_<name>.rpg'. Typing 'save <name>' will save with name <name>.",
        "cls": "Typing 'cls' or 'clear' clears the screen.",
        "clear": "Typing 'cls' or 'clear' clears the screen.",
        "gifts": "Typing 'gifts' will display page 1 of your Gifts, which you will receive from NPCs and other players. Typing 'gifts' and then a number will display that page. Typing 'gifts claim' and then a number will claim that gift number, which will be displayed next to the gift. Typing 'gift claim all' will claim all of your gifts.",
        "location": "Typing 'location' will tell you where you are. Typing 'location description' will tell you where you are, and also display the description of the current town you are in.",
        "shop": "Typing 'shop' will bring you to the Shop. A prompt, 'Shop> ', will appear. In the shop, you can look at things which you want to buy. Type 'items' to look at all the items, and type 'items' and then a number to look at that page. Type 'info' and then a number to look at an item's stats, and type 'buy' and then a number will buy that item. Type 'exit' to exit the shop. The 'stats' command works in the shop as well. For help on the 'stats' command, type 'help stats'. There is no help command inside the shop.",
        "items": "Typing 'items' will display page 1 of your Items, which you will get from gifts or from Shops in Towns. Typing 'items ' and then a number will display that page. Typing 'items stats ' and then a number will display the Stats for that item.",
    }

    def __init__(self):
        self.started = False

    def setup_player(self):
        while not (name := input_slow("Please enter your name: ")): print_slow("That is not a valid username!")
        self.player = Player(
            name, 50, 50, Experience(), 5, 2, 0
        )
        print_slow("Player creation complete...")
        print_slow("Loading player into world...")
        time.sleep(0.5)
        print()

    def load_town_data(self):
        with open("desc.txt", "r") as f:
            text = f.read().rstrip()
        town_info = text.split("\n\n")
        towns = list(map(lambda x: x.split("\n"), town_info))
        self.starting_town = towns.pop(0)
        self.starting_town = {"name": self.starting_town[0], "desc": self.starting_town[1:]}
        random.shuffle(towns)
        self.town_names = list(map(lambda x: x[0], towns))
        self.town_descs = list(map(lambda x: x[1:], towns))

    def setup_floor1(self):
        self.floors = [Floor(1, 4, self.town_names[:4], self.town_descs[:4])]
        del self.town_names[:4], self.town_descs[:4]

        starting_floor = self.floors[0]
        name, desc = self.starting_town["name"], self.starting_town["desc"]
        starting_town = Town(name, desc)

        road = Road(starting_town, random.choice(starting_floor.towns))
        direction = random.randint(0, 7)
        starting_town.linked_to = {direction: road}
        starting_floor.towns.append(starting_town)

        self.player.floor = self.floors[0]
        self.player.town = self.floors[0].towns[-1]

        print_slow("Hello, " + self.player.name + "! Welcome to my RPG Game, where you will embark on an exciting journey through a series of challenges to defeat the final boss and claim victory. I assure you, it will be a hard path to take, but feel free to get used to everything! Right now you are standing in the Starting Town, where you can buy things, take refuge in and start your journey. Once you have done everything you want to do in Starting Town, then you can make your way to the next town, " + road.town2.name + ". See there, in the " + directions[direction] + "? That's the road you want to take.")

    def introduction(self):
        input_slow("\nPress Enter to continue\n")

        self.player.print_stats()
        print_slow("\nTake a look at your Player Stats. You can level up your experience by fighting against monsters. The more experience you have, the stronger you are, but armour can drastically change that. Currency is measured in " + currency + "s. You don't have much money, do you? Here, I'll give you some to start you off. Take it, it's just a Gift!")

        Money("Tour Guide", 200).give(self.player)

        print_slow("Now, before I leave, I'll show you how to get around. You will get a dialogue that is shown as Menu> , where you can type what you want to do. Type 'stats' to show your Player Stats, and if you want to show only one of your Stats, type one of 'health', 'experience', 'attack', 'defense', or 'money' after 'stats' to show that exact Stat. Monsters will only spawn on roads while you go to other towns, unless the town you are at is not a safe zone. If so, when you get to the town, you will get a warning. Day and night are measured in realtime, and one day is 20 minutes. At night, there will be more monsters, each of which will be stronger, so make sure you get to an inn and sleep. Beware, this will cost 20 " + currency + "s, so make sure you have the money. Otherwise, come back in a few minutes and you'll be fine! Also, the Gift that I gave you can be claimed by typing 'gifts claim 1'. If you want any more help, type 'help'. Good luck!")

        input_slow("\nPress Enter to continue\n")

    def help(self, item=None):
        if item is None:
            print_slow("This is the Menu bar, and will be indicated when you see the characters 'Menu> ' on the screen. You can type commands here. To get help with any commands, type 'help <command name>', replacing <command name> with the command you want help with.\n")
            print_slow("Here are the available commands:")
            table(self.available_commands, 2)
        elif item in self.available_commands:
            print_slow("Help on command", item + ":\n")
            print_slow(self.help_commands[item])
        else:
            print_slow("\"" + item + "\"", "is not a valid command!")

    def stats(self, item=None):
        if item is None:
            self.player.print_stats()
        elif item == "name":
            print_slow("Name:", self.player.name)
        elif item == "health":
            print_slow("Health:", str(self.player.health) + "/" + str(self.player.max_health))
        elif item == "experience":
            print_slow("Experience:", self.player.experience)
        elif item == "attack":
            print_slow("Attack damage:", self.player.attack)
        elif item == "defense":
            print_slow("Defense points:", self.player.defense)
        elif item == "money":
            print_slow("Money:", format(self.player.money, ",") + " " + currency + "s")
        else:
            print_slow("There is no Stat that has the name of \"" + item + "\"!")

    def save(self, name=None):
        if not name: name = input_slow("Enter save name: ")
        if name == "":
            print_slow("Cancelled saving.")
            return
        if os.path.isfile(os.path.join("save", "save_" + name + ".rpg")):
            if input_slow("Do you want to overwrite the save file for the save name " + name + "? (y/n) ").lower() != "y":
                return
        if not os.path.isdir("save"): os.mkdir("save")
        with open(os.path.join("save", "save_" + name + ".rpg"), "wb+") as f:
            pickle.dump(self, f)
            print_slow("Saved successfully!")

    def cls(self):
        os.system("cls || clear")

    def clear(self):
        os.system("cls || clear")

    def gifts(self, claim_or_page="1", claim_number=None):
        if claim_or_page == "claim":
            if claim_number == "all":
                for gift in reversed(self.player.gifts):
                    gift.claim()
            elif claim_number is not None:
                gift_num = int(claim_number) - 1
                if gift_num >= len(self.player.gifts) or gift_num < 0:
                    print_slow("There is no Gift at number", claim_number + "!")
                    return
                self.player.gifts[gift_num].claim()
            else:
                print_slow("Please provide the gift number to claim.")
        else:
            if not claim_or_page.isdecimal():
                return -1
            if len(self.player.gifts) == 0:
                print_slow("Gifts\n\nYou have no Gifts. You can obtain Gifts from NPCs and other players.")
                return
            page = int(claim_or_page) - 1
            if page * 10 >= len(self.player.gifts):
                print_slow("There is no page", claim_or_page, "of gifts!")
                return
            print_slow("Gifts\n")
            i = page * 10
            for gift in self.player.gifts[i:]:
                print_slow("Gift", str(i + 1) + ":", gift.item_name, "received from", gift.from_who)
                i += 1
                if i > (page + 1) * 10: break
            print_slow("\nPage", claim_or_page, "of", math.ceil(len(self.player.gifts) / 10))

    def location(self, desc=None):
        if self.player.town is not None:
            if desc == "description":
                print()
                print_slow(*self.player.town.desc)
            else:
                print_slow("You are on Floor", self.player.floor.num, "and are at", self.player.town.name + ".")
        else:
            print_slow("You are OTM - off the map!")

    def shop(self):
        print_slow()
        print_slow("You have", self.player.money, currency + "s.\n")
        self.player.town.shop.mainloop(self.player)

    def items(self, stats_or_page="1", num="1"):
        if not num.isdecimal():
            return -1
        if stats_or_page == "stats":
            num_int = int(num) - 1
            if num_int >= len(self.player.items) or num_int < 0:
                print_slow("There is no item at number", num + "!")
                return
            item = self.player.items[num_int]
            print_slow("Stats on item", num, "(" + item.name + "):\n")
            for stat_name, stat_value in item.stats.items():
                print_slow(Shop.stat_keys[stat_name] + ":", stat_value)
        else:
            if not stats_or_page.isdecimal():
                return -1
            if len(self.player.items) == 0:
                print_slow("You have no items. You can obtain items from gifts or from Shops in towns.")
                return
            page_num = int(stats_or_page) - 1
            if page_num * 5 > len(self.player.items):
                print_slow("There is no page", stats_or_page + "!")
                return
            print_slow("Your Items:\n")
            i = page_num * 5
            for item in self.player.items[i:]:
                print_slow("Item", str(i + 1) + ":", item.name)
                i += 1
                if i >= (page_num + 1) * 5: break
            print_slow("\nPage", stats_or_page, "of", math.ceil(len(self.player.items) / 10))
    
    def sleep(self):
        if self.player.town is not None:
            if input_slow("Are you sure you want to sleep? This costs 5 " + currency + "s. (y/n) ") == "y":
                print_slow("Sleeping...")
        else:
            print_slow("You are OTM - off the map!")

    def mainloop(self):
        if not self.started:
            self.setup_player()
            self.load_town_data()
            self.setup_floor1()
            self.introduction()
            self.started = True
        while True:
            try:
                command = re.subn(" +", input_slow("Menu> ").rstrip().lower(), " ")[0]
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
            if cmd_args[0] in self.available_commands:
                func = getattr(self, cmd_args[0])
                if len(inspect.signature(func).parameters) >= len(cmd_args) - 1:
                    if not func(*cmd_args[1:]) == -1:
                        print()
                        continue
            print_slow("\"" + command + "\"", "is not a valid command!\n")

class Experience:
    def __init__(self):
        self.exp = 0
        self.total_exp = 0
        self.level = 0

    def add(self, amount):
        self.exp += amount
        self.total_exp += amount
        if self.exp > self.level * 5 + 20:
            self.exp -= self.level * 5 + 20
            self.level += 1
            return True
        return False

    def sub(self, amount):
        self.exp -= amount
        self.total_exp -= amount
        if self.exp < 0:
            self.level -= 1
            self.exp += self.level * 5 + 20

    def __repr__(self):
        return str(self.total_exp) + " (Level " + str(self.level) + " + " + str(self.exp) + ")"

class Alive:
    def __init__(self, name, health, max_health, attack, defense):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.attack = attack
        self.defense = defense

    def print_stats(self):
        print_slow("Monster Stats\n")
        print_slow("Name:", self.name)
        print_slow("Health:", str(self.health) + "/" + str(self.max_health))
        print_slow("Experience:", self.experience)
        print_slow("Attack damage:", self.attack)
        print_slow("Defense points:", self.defense)

class Player(Alive):
    def __init__(self, name, health, max_health, experience, attack, defense, money):
        super(Player, self).__init__(name, health, max_health, attack, defense)
        self.experience = experience
        self.money = money
        self.gifts = []
        self.items = []
        self.town = None
        self.floor = None
        self.equipment = Equipment()

    def print_stats(self):
        print_slow("Player Stats\n")
        print_slow("Name:", self.name)
        print_slow("Health:", str(self.health) + "/" + str(self.max_health))
        print_slow("Experience:", self.experience)
        print_slow("Attack damage:", self.attack)
        print_slow("Defense points:", self.defense)
        print_slow("Money:", format(self.money, ","), currency + "s")

class Equipment:
    def __init__(self):
        self.sword = None
        self.shield = None
        self.cloak = None
        self.helmet = None

class Gift:
    def __init__(self, from_who, item_name, item, amount, args=[]):
        self.from_who = from_who
        self.item_name = item_name
        self.item = item
        self.amount = amount
        self.args = args
        self.player = None

    def give(self, player):
        print_slow("\nReceived", self.item_name, "from", self.from_who + "\n")
        player.gifts.append(self)
        self.player = player

    def claim(self):
        if self.player is not None:
            self.player.items.extend([self.item(*self.args) for i in range(self.amount)])
            self.player.gifts.remove(self)
            print_slow("Claimed", self.item_name, "from", self.from_who)
        else:
            raise Exception("Cannot claim gift before giving it to someone")

class Item:
    def __init__(self, name, stats={}):
        self.name = name
        self.stats = stats

class Money(Gift):
    def __init__(self, from_who, amount):
        super(Money, self).__init__(from_who, format(amount, ",") + " " + currency + "s", None, amount)

    def claim(self):
        if self.player is not None:
            self.player.money += self.amount
            self.player.gifts.remove(self)
            print_slow("Claimed", self.item_name, "from", self.from_who)
        else:
            raise Exception("Cannot claim gift before giving it to someone")

class Inn:
    def sleep(self):
        print_slow("Sleeping...")

class Shop:

    available_commands = ["items", "info", "buy"]
    stat_keys = {"attack": "Attack Damage", "defense": "Defense Points", "desc": "Description", "effect": "Effect"}

    def __init__(self):
        self.selling = [
            [Item("Wooden Sword", {"attack": 6, "defense": 3, "desc": "A sword worthy for even beginners."}), False, 75],
            [Item("Wooden Shield", {"attack": 0, "defense": 4, "desc": "The ideal shield to deflect beasts and monsters."}), False, 70],
        ]

    def mainloop(self, player):
        self.player = player
        while True:
            try:
                command = re.subn(" +", input_slow("Shop> ").rstrip().lower(), " ")[0]
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
            if cmd_args[0] in self.available_commands:
                func = getattr(self, cmd_args[0])
                if len(inspect.signature(func).parameters) >= len(cmd_args) - 1:
                    if not func(*cmd_args[1:]) == -1:
                        print()
                        continue
            print_slow("\"" + command + "\"", "is not a valid command!\n")
        self.player = None

    def stats(self, item=None):
        if item is None:
            self.player.print_stats()
        elif item == "name":
            print_slow("Name:", self.player.name)
        elif item == "health":
            print_slow("Health:", str(self.player.health) + "/" + str(self.player.max_health))
        elif item == "experience":
            print_slow("Experience:", self.player.experience)
        elif item == "attack":
            print_slow("Attack damage:", self.player.attack)
        elif item == "defense":
            print_slow("Defense points:", self.player.defense)
        elif item == "money":
            print_slow("Money:", format(self.player.money, ",") + " " + currency + "s")
        else:
            print_slow("There is no Stat that has the name of \"" + item + "\"!")

    def items(self, page="1"):
        if not page.isdecimal():
            return -1
        page_num = int(page) - 1
        if page_num * 5 > len(self.selling):
            print_slow("There is no page", page + "!")
            return
        print_slow("Items in the shop:\n")
        i = page_num * 5
        for item, sold, price in self.selling[i:]:
            if sold:
                print_slow("Item", str(i + 1) + ":", item.name, "(SOLD)")
            else:
                print_slow("Item", str(i + 1) + ":", item.name, "\tPrice:", price, currency + "s")
            i += 1
            if i >= (page_num + 1) * 5: break
        print_slow("\nPage", page, "of", math.ceil(len(self.selling) / 10))

    def info(self, item_index=None):
        if item_index is None or not item_index.isdecimal():
            return -1
        item_num = int(item_index) - 1
        if len(self.selling) <= item_num or item_num < 0:
            print_slow("There is no item at number", item_index + "!")
            return
        item = self.selling[item_num][0]
        print_slow("Info on item", item_index, "(" + item.name + "):\n")
        for stat_name, stat_value in item.stats.items():
            print_slow(self.stat_keys[stat_name] + ":", stat_value)

    def buy(self, item_index=None):
        if item_index is None or not item_index.isdecimal():
            return -1
        item_num = int(item_index) - 1
        if item_num >= len(self.selling) or item_num < 0:
            print_slow("There is no item at number", item_index + "!")
            return
        item = self.selling[item_num]
        if item[1]:
            print_slow("Item", item_index, "(" + item[0].name + ") has already been sold!")
        elif item[2] > self.player.money:
            print_slow("You do not have enough money to buy this item (" + item[0].name + ")!")
        else:
            answer = input_slow("Are you sure you want to buy this item for " + str(item[2]) + " " + currency + "s? (y/n) ").lower()
            if answer == "y":
                self.player.money -= item[2]
                self.player.items.append(item[0])
                item[1] = True
                print_slow("You have bought item", item_index, "(" + item[0].name + ") for", item[2], currency + "s.")

    def cls(self):
        os.system("cls || clear")

    def clear(self):
        os.system("cls || clear")

class Floor:
    def __init__(self, num, no_of_towns, town_names, town_descs, prev_floor=None, next_floor=None):
        self.num = num
        self.prev_floor = prev_floor
        self.next_floor = next_floor
        self.towns = [Town(name, desc) for i, (name, desc) in enumerate(zip(town_names, town_descs))]

class Town:
    def __init__(self, name, desc, connect=None, side=None):
        if connect is None:
            self.linked_to = {}
        else:
            self.linked_to = {side: connect}
        self.name, self.desc = name, desc
        self.shop = Shop()
        self.inn = Inn()

    def print_description(self):
        print_slow(self.desc)

class Road:
    def __init__(self, town1, town2):
        self.town1, self.town2 = town1, town2

def main():
    if sys.stdout.isatty():
        os.system("cls || clear")
    if os.path.isdir("save") and len(os.listdir("save")):
        while not os.path.isfile(os.path.join("save", "save_" + (save_name := input_slow("Enter save name to be loaded: ")) + ".rpg")):
            if save_name != "":
                print_slow("There is no save file named " + save_name + "!")
            else:
                print_slow("Creating new world...\n")
                game = Game()
                game.mainloop()
                return
        with open(os.path.join("save", "save_" + save_name + ".rpg"), "rb") as f:
            save = pickle.load(f)
            save.mainloop()
    else:
        game = Game()
        game.mainloop()

if __name__ == "__main__":
    main()
    os.system("cls || clear")
