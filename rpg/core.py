import random
import time
import os
import pickle
import math
import datetime
# import turtle

from .utils import *
from .loader import CONSTS
from .values import *

class Game:

    available_commands = CONSTS["available_commands"]
    help_commands = CONSTS["help_commands"]

    def __init__(self):
        self.started = False

    def setup_player(self):
        while not (name := input_slow("Please enter your name: ")):
            print_slow("That is not a valid username!")
        self.player = Player(
            name, 50, 50, Experience(), 5, 2, 0
        )
        self.time_offset = datetime.timedelta(0)
        self.play_time = datetime.timedelta(0)
        print_slow("Player creation complete...")
        print_slow("Loading player into world...")
        time.sleep(1)
        self.start_time = datetime.datetime.now()
        print()

    def load_town_data(self):
        towns = CONSTS["towns"]
        starting_town = towns.pop(0)
        random.shuffle(towns)
        towns.insert(0, starting_town)
        self.town_names = list(map(lambda x: x[0], towns))
        self.town_descs = list(map(lambda x: x[1:], towns))

    def setup_floor1(self):
        self.floors = [Floor(1, self.town_names[:5], self.town_descs[:5])]
        del self.town_names[:5], self.town_descs[:5]

        self.player.floor = self.floors[0]
        self.player.town = self.floors[0].towns[0]

    def introduction(self):
        lines = CONSTS["intro"]
        assert len(lines) == 3

        direction = random.randint(0, 7)
        route = list(self.player.town.linked_to.values())[0]
        print_slow(lines[0] % (self.player.name,
                               route.town2.name, CONSTS["directions"][direction]))
        input_slow("\nPress Enter to continue\n")
        self.player.print_stats()
        print()
        print_slow(lines[1] % CONSTS["currency"])
        Money("Tour Guide", 200).give(self.player)
        print_slow(lines[2] % CONSTS["currency"])
        input_slow("\nPress Enter to continue\n")

    def help(self, item=None):
        if item is None:
            print_slow(
                "This is the Menu bar, and will be indicated when you see the characters 'Menu> ' on the" +
                "screen. You can type commands here. To get help with any commands, type 'help" +
                " <command name>', replacing <command name> with the command you want help with.")
            print()
            print_slow("Here are the available commands:")
            table(self.available_commands, 2)
        elif item in self.available_commands:
            print_slow("Help on command", item + ":\n")
            if "%s" in self.help_commands[item]:
                print_slow(self.help_commands[item] % CONSTS["currency"])
            else:
                print_slow(self.help_commands[item])
        else:
            print_slow("\"" + item + "\"", "is not a valid command!")

    def stats(self, item=None):
        if item is None:
            self.player.print_stats()
        elif item == "name":
            print_slow("Name:", self.player.name)
        elif item == "health":
            print_slow("Health:", format(self.player.health, ",") +
                       "/" + format(self.player.max_health, ","))
        elif item == "experience":
            print_slow("Experience:", self.player.experience)
        elif item == "attack":
            print_slow("Attack damage:", format(self.player.total_attack, ","))
        elif item == "defense":
            print_slow("Defense points:", format(
                self.player.total_defense, ","))
        elif item == "money":
            print_slow("Money:", format(
                self.player.money, ",") + " " + CONSTS["currency"] + "s")
        else:
            print_slow(
                "There is no Stat that has the name of \"" + item + "\"!")

    def save(self, name=None):
        play_time = datetime.datetime.now() - self.opening_time + self.play_time
        print_slow("Total play time:", strfdelta(
            play_time, "{D}d, {H}:{M:02}:{S:02}"))
        if not name:
            name = input_slow("Enter save name: ")
        if name == "":
            print_slow("Cancelled saving.")
            return
        # save_folder = os.path.expandvars(os.path.join("%localappdata%", "RPG", "saves"))
        directory = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "save")
        if os.path.isfile(os.path.join(directory, "save_" + name + ".rpg")):
            if input_slow("Do you want to overwrite the save file for the save name " +
                          name + "? (y/n) ").lower() != "y":
                return
        if not os.path.isdir(os.path.join(directory, "save")):
            os.mkdir(directory)
        with open(os.path.join(directory, "save_" + name + ".rpg"), "wb+") as f:
            self.play_time += datetime.datetime.now() - self.opening_time
            pickle.dump(self, f)
            print_slow("Saved successfully!")
            self.opening_time = datetime.datetime.now()

    def cls(self):
        clear()
    clear = cls

    def clear(self):
        clear()

    def gifts(self, claim_or_page="1", claim_number=None):
        if claim_or_page == "claim":
            if claim_number == "all":
                for gift in reversed(self.player.gifts):
                    gift.claim()
            elif claim_number is not None:
                if not claim_number.isdecimal():
                    return -1
                gift_num = int(claim_number) - 1
                if gift_num >= len(self.player.gifts) or gift_num < 0:
                    print_slow("There is no Gift at number",
                               claim_number + "!")
                    return
                self.player.gifts[gift_num].claim()
            else:
                print_slow("Please provide the gift number to claim.")
        else:
            if not claim_or_page.isdecimal():
                return -1
            if len(self.player.gifts) == 0:
                print_slow(
                    "Gifts\n\nYou have no Gifts. You can obtain Gifts from NPCs and other players.")
                return
            page = int(claim_or_page) - 1
            if page * 10 >= len(self.player.gifts):
                print_slow("There is no page", claim_or_page, "of gifts!")
                return
            print_slow("Gifts\n")
            i = page * 10
            for gift in self.player.gifts[i:]:
                print_slow("Gift", str(i + 1) + ":", gift.item_name,
                           "received from", gift.from_who)
                i += 1
                if i > (page + 1) * 10:
                    break
            print_slow("\nPage", claim_or_page, "of",
                       math.ceil(len(self.player.gifts) / 10))

    def location(self, desc=None):
        if self.player.town is not None:
            if desc == "description":
                print()
                print_slow(self.player.town.desc)
            else:
                print_slow("You are on Floor", self.player.floor.num,
                           "and are at", self.player.town.name + ".")
        else:
            print_slow("You are OTM - off the map!")

    def shop(self):
        print()
        print_slow("You have", format(self.player.money, ","), CONSTS["currency"] + "s.\n")
        self.player.town.shop.mainloop(self.player)

    def items(self, stats_or_page="1", num=""):
        if stats_or_page == "stats":
            if not num.isdecimal():
                return -1
            num_int = int(num) - 1
            if num_int >= len(self.player.items) or num_int < 0:
                print_slow("There is no item at number", num + "!")
                return
            item = self.player.items[num_int]
            print_slow("Stats on item", num, "(" + item.name + "):\n")
            for stat_name, stat_value in item.stats.items():
                if stat_name in ["type", "number"]:
                    continue
                if isinstance(stat_value, int):
                    print_slow(Shop.stat_keys[stat_name] +
                               ":", format(stat_value, ","))
                else:
                    print_slow(Shop.stat_keys[stat_name] + ":", stat_value)
        else:
            if not stats_or_page.isdecimal():
                return -1
            if len(self.player.items) == 0:
                print_slow(
                    "You have no items. You can obtain items from gifts or from Shops in towns.")
                return
            page_num = int(stats_or_page) - 1
            if page_num * 10 >= len(self.player.items):
                print_slow("There is no page", stats_or_page + "!")
                return
            print_slow("Your Items:\n")
            i = page_num * 10
            for item in self.player.items[i:]:
                print_slow("Item", str(i + 1) + ":", item.name)
                i += 1
                if i >= (page_num + 1) * 10:
                    break
            print_slow("\nPage", stats_or_page, "of",
                       math.ceil(len(self.player.items) / 10))

    def equipment(self, equip=None, item_num=None):
        if equip is None:
            print_slow("Equipped items:\n")
            print_slow("Sword:", self.player.equipment.sword)
            print_slow("Shield:", self.player.equipment.shield)
            print_slow("Cloak:", self.player.equipment.cloak)
            print_slow("Helmet:", self.player.equipment.helmet)
            print_slow("Shoes:", self.player.equipment.shoes)
        elif equip == "equip":
            if item_num is None or not item_num.isdecimal():
                return -1
            item_int = int(item_num) - 1
            if item_int >= len(self.player.items):
                print_slow("There is no item at number", item_num + "!")
                return
            item = self.player.items[item_int]
            _type = item.stats["type"]
            if _type not in self.player.equipment.equippable:
                print_slow("Cannot equip", item, "because it is a" +
                           ("n" if _type[0].lower() in "aeiou" else ""), t_type)

            equipped = getattr(self.player.equipment, _type)
            if equipped is not None:
                if equipped is item:
                    print_slow("You already have", equipped, "equipped!")
                    return
                if input_slow("You have a" + ("n" if str(equipped)[0].lower() in "aeiou" else "") + " " +
                              str(equipped) + " equipped currently. Do you want to replace it? (y/n) ") != "y":
                    return
            setattr(self.player.equipment, _type, item)
            print_slow("Equipped", str(item) + ".")
        elif equip == "unequip":
            if item_num is None:
                return -1
            if item_num not in Equipment.equippable:
                print_slow("There is no type of equipment called",
                           item_num + "!")
                return
            item = getattr(self.player.equipment, item_num)
            if item is None:
                print_slow("You do not have a" + ("n" if item_num[0] in "aeiou" else ""),
                           item_num, "equipped!")
                return
            setattr(self.player.equipment, item_num, None)
            print_slow("Unequipped", str(item) + ".")
        else:
            return -1

    def sleep(self):
        if self.player.town is not None:
            if input_slow("Are you sure you want to sleep? This costs 5 " + CONSTS["currency"] + "s. (y/n) ") == "y":
                print_slow("Sleeping...")
                time.sleep(1)
                self.time_offset = (datetime.datetime.now() -
                                    self.opening_time) % datetime.timedelta(seconds=300)
                print_slow("Time offset is now", strfdelta(
                    self.time_offset, "{D}d, {H}:{M:02}:{S:02}"))
        else:
            print_slow("You are OTM - off the map!")

    def travel(self):
        print_slow("Routes connected to this town (" +
                   self.player.town.name + "):\n")
        for town2, route in self.player.town.linked_to.items():
            print_slow("Route", route.num,
                       "(Connects to", town2.name + ")", end="")
            if town2.linked_to[self.player.town] is not route:
                print_slow(" Note: Double route via Route",
                           town2.linked_to[self.player.town].num)
            else:
                print()
        print()

        towns = list(self.player.town.linked_to.keys())
        routes = list(self.player.town.linked_to.values())
        route_numbers = list(map(lambda x: str(x.num), routes))
        if len(towns) == 1:
            if input_slow("Would you like to travel along " + routes[0].name + " to " +
                          towns[0].name + "? (y/n) ") == "y":
                choice = routes[0]
            else:
                return
        else:
            while (answer := input_slow("Enter Route number to travel along: ")) not in route_numbers:
                if not answer:
                    return
                print_slow("That is not a valid Route!")
                print_slow("Available routes:", ", ".join(route_numbers))
            choice = routes[route_numbers.index(answer)]

        limit = self.player.furthest_route + 1
        if choice.num > limit:
            if not (isinstance(choice.get_other(self.player.town), Route) and
                    choice.get_other(self.player.town).num == limit):
                print_slow("You cannot travel on this route, because you must reach Route",
                           choice.num - 1, "to unlock this route. Route", choice.num - 1,
                           "can be found connected to",
                           self.player.floor.routes[choice.num -
                                                    1].town1.name, "and",
                           self.player.floor.routes[choice.num - 1].town2.name + ".")
                return
        print_slow("Travelling along", str(choice) + "...")

        time.sleep(1)  # Replace with monster fighting

        other_route = choice.get_other(self.player.town)
        if isinstance(choice.get_other(self.player.town), Route):
            print_slow("Reached the center of Double Route", str(choice.num) + "/" +
                       str(other_route.num) + ".")
            print_slow("Travelling along", str(other_route) + "...")

            time.sleep(1)  # Replace with monster fighting

            print_slow("Reached", other_route.get_other(choice).name + ".")
            self.player.furthest_route = max(
                self.player.furthest_route, choice.num, other_route.num)
            self.player.town = other_route.get_other(choice)
        else:
            print_slow("Reached", other_route.name + ".")
            self.player.furthest_route = max(
                self.player.furthest_route, choice.num)
            self.player.town = other_route

    def roam(self):
        print_slow(
            "You go to the edge of the town, and start roaming around for a monster to fight.")
        while True:
            print_slow("Roaming around...")
            time.sleep(random.random() * 3 + 2)
            if random.random() < self.player.town.spawn_rate:
                print_slow(
                    "A twig snaps, and something emerges out of the shadows.")
                # Fight
            if input_slow("Do you want to continue roaming around? (y/n) ") != "y":
                print_slow("You journey back to the town.")
                time.sleep(1)
                break

    def mainloop(self):
        self.opening_time = datetime.datetime.now()
        if not self.started:
            self.setup_player()
            self.load_town_data()
            self.setup_floor1()
            self.introduction()
            self.started = True
        mainloop(self, "Menu")

class LifeForm:
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

class Player(LifeForm):
    def __init__(self, name, health, max_health, experience, attack, defense, money):
        super(Player, self).__init__(name, health, max_health, attack, defense)
        self.experience = experience
        self.money = money
        self.gifts = []
        self.items = []
        self.town = None
        self.floor = None
        self.equipment = Equipment()
        self.thirst = 50
        self.hunger = 50

        self.furthest_route = 100

    @property
    def total_attack(self):
        total = self.attack
        for item in self.equipment:
            if item is None:
                continue
            total += item.stats["attack"]
        return total

    @property
    def total_defense(self):
        total = self.defense
        for item in self.equipment:
            if item is None:
                continue
            total += item.stats["defense"]
        return total

    def print_stats(self):
        print_slow("Player Stats\n")
        print_slow("Name:", self.name)
        print_slow("Health:", str(self.health) + "/" + str(self.max_health))
        print_slow("Experience:", self.experience)
        print_slow("Attack damage:", self.total_attack)
        print_slow("Defense points:", self.total_defense)
        print_slow("Money:", format(self.money, ","), CONSTS["currency"] + "s")

class Shop:

    available_commands = ["items", "info", "buy"]
    stat_keys = {
        "attack": "Attack Boost", "defense": "Defense Boost", "desc": "Description", "effect": "Effect",
        "number": "Left in stock",
    }

    def __init__(self):
        items = [0, 1, 2]
        self.selling = []
        for item_num in items:
            item = Item.from_dict(CONSTS["items"][item_num])
            price = CONSTS["items"][item_num]["price"]
            self.selling.append([item, price, False])

    def mainloop(self, player):
        self.player = player
        mainloop(self, "Shop")
        self.player = None

    def stats(self, item=None):
        if item is None:
            self.player.print_stats()
        elif item == "name":
            print_slow("Name:", self.player.name)
        elif item == "health":
            print_slow("Health:", format(self.player.health, ",") +
                       "/" + format(self.player.max_health, ","))
        elif item == "experience":
            print_slow("Experience:", self.player.experience)
        elif item == "attack":
            print_slow("Attack damage:", format(self.player.total_attack, ","))
        elif item == "defense":
            print_slow("Defense points:", format(
                self.player.total_defense, ","))
        elif item == "money":
            print_slow("Money:", format(
                self.player.money, ",") + " " + CONSTS["currency"] + "s")
        else:
            print_slow(
                "There is no Stat that has the name of \"" + item + "\"!")

    def items(self, page="1"):
        if not page.isdecimal():
            return -1
        page_num = int(page) - 1
        if page_num * 5 > len(self.selling):
            print_slow("There is no page", page + "!")
            return
        print_slow("Items in the shop:\n")
        i = page_num * 5
        for item, price, sold in self.selling[i:]:
            if "number" in item.stats:
                if sold:
                    print_slow("Item", str(i + 1) + ":", item.name, "(OUT OF STOCK)")
                else:
                    print_slow("Item", str(i + 1) + ":", item.name,
                               "\tPrice:", price, CONSTS["currency"] + "s", "(" + 
                               str(item.stats["number"]), "left in stock)")
            elif sold:
                print_slow("Item", str(i + 1) + ":", item.name, "(SOLD)")
            else:
                print_slow("Item", str(i + 1) + ":", item.name,
                        "\tPrice:", price, CONSTS["currency"] + "s")
            i += 1
            if i >= (page_num + 1) * 5:
                break
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
            if stat_name == "type":
                continue
            if isinstance(stat_value, int):
                print_slow(self.stat_keys[stat_name] +
                           ":", format(stat_value, ","))
            else:
                print_slow(self.stat_keys[stat_name] + ":", stat_value)
        print_slow("Price:", self.selling[item_num][1])

    def buy(self, item_index=None):
        if item_index is None or not item_index.isdecimal():
            return -1
        item_num = int(item_index) - 1
        if item_num >= len(self.selling) or item_num < 0:
            print_slow("There is no item at number", item_index + "!")
            return
        item = self.selling[item_num]
        if item[2]:
            print_slow("Item", item_index,
                       "(" + item[0].name + ") has already been sold!")
        elif item[1] > self.player.money:
            print_slow("You have insufficient funds to buy a" +
                       ("n" if item[0].name[0].lower() in "aeiou" else "") + " " + item[0].name + "!")
        else:
            if "number" in item[0].stats:
                if item[0].stats["number"] == 0:
                    print_slow("Item", item_index, "(" + item[0].name + ") has ran out of stock!")
                    return
                while (number := input_slow("How many do you want to buy? ")) != "":
                    if number.isdecimal():
                        num_int = int(number)
                        if num_int > item[0].stats["number"]:
                            print_slow("There are only", item[0].stats["number"], "left in stock!")
                            continue
                        break
                    else:
                        print_slow("\"" + number + "\" is not a number!")
                answer = input_slow("Are you sure you want to buy " + number + "x " + item[0].name +
                                    ("s" if num_int > 1 else "") + " for " + str(num_int * item[1]) +
                                    " " + CONSTS["currency"] + "s? (y/n) ").lower()
                if answer == "y":
                    self.player.money -= num_int * item[1]
                    self.player.items += [item[0].copy() for i in range(num_int)]
                    item[0].stats["number"] -= num_int
                    if item[0].stats["number"] == 0:
                        item[2] = True
                    print_slow("Item", item_index, "(" + item[0].name + ") has now sold out.")
                    print_slow("You have bought " + number + "x of item " + item_index + "(" +
                            item[0].name + ")" + ("s" if num_int > 1 else "") + " for " +
                            str(num_int * item[1]) + " " + CONSTS["currency"] + "s.")
                return
            answer = input_slow("Are you sure you want to buy a" +
                                ("n" if item[0].name[0].lower() in "aeiou" else "") + " " + item[0].name +
                                " for " + str(item[1]) + " " + CONSTS["currency"] + "s? (y/n) ").lower()
            if answer == "y":
                self.player.money -= item[1]
                self.player.items.append(item[0].copy())
                item[2] = True
                print_slow("You have bought item", item_index,
                           "(" + item[0].name + ") for", item[1], CONSTS["currency"] + "s.")

    def cls(self):
        clear()

    def clear(self):
        clear()

class Floor:
    def __init__(self, num, town_names, town_descs, prev_floor=None, next_floor=None):
        self.num = num
        self.prev_floor = prev_floor
        self.next_floor = next_floor
        assert len(town_names) == len(town_descs)
        self.towns = [Town(
            name, desc,
            random.uniform(0.9 - 0.05 * self.num, 0.95 - 0.05 * self.num)
        ) for name, desc in zip(town_names, town_descs)]

        self.towns[0].max_connections = 1
        no_of_3_conenctions = round(1 / 3 * len(self.towns))
        for town in self.towns[-no_of_3_conenctions:]:
            town.max_connections = 3
        a, b = self.towns.pop(), self.towns.pop(0)
        random.shuffle(self.towns)
        self.towns.insert(0, b)

        n = 90 + self.num * 10 + 1
        route = Route(self.towns[0], self.towns[-1], n)
        route.town1.linked_to[route.town2] = route
        route.town2.linked_to[route.town1] = route
        self.towns.insert(random.randint(1, len(self.towns) - 1), a)
        self.routes = [route]
        n += 1

        first_town = self.towns.pop(0)
        town_num = list(range(len(self.towns)))
        while len(town_num) > 1:
            route = Route(self.towns[town_num.pop()],
                          self.towns[town_num[-1]], n)
            self.routes.append(route)
            route.town1.linked_to[route.town2] = route
            route.town2.linked_to[route.town1] = route
            n += 1

        not_fully_connected = [a for a in range(1, len(self.towns) - 1) if (
            self.towns[a].max_connections == 3)] + [0]
        random.shuffle(not_fully_connected)

        while len(not_fully_connected) >= 2:
            route = Route(self.towns[not_fully_connected.pop()],
                          self.towns[not_fully_connected.pop()], n)
            if route.town2 in route.town1.linked_to:
                continue
            self.routes.append(route)
            route.town1.linked_to[route.town2] = route
            route.town2.linked_to[route.town1] = route
            n += 1

        random.shuffle(self.towns)
        self.towns.insert(0, first_town)

        double_routes = list(range(1, len(self.routes)))
        random.shuffle(double_routes)
        double_routes = double_routes[-len(self.towns) // 5:]
        for index, item in enumerate(double_routes):
            double_route = self.routes[item]
            route1 = Route(double_route.town1, None, double_route.num)
            route2 = Route(route1, double_route.town2, double_route.num + 1)
            route1.town2 = route2
            double_route.town1.linked_to[double_route.town2] = route1
            double_route.town2.linked_to[double_route.town1] = route2

            self.routes[item] = route1
            double_routes[index] = route2

        for route2 in double_routes:
            if route2.num < n:
                for route in self.routes:
                    if route.num >= route2.num:
                        route.num += 1
            self.routes.append(route2)
            n += 1

        self.routes = {route.num: route for route in self.routes}

        # for town in self.towns:
        #     print_slow(town.max_connections)
        #     for town2, route in town.linked_to.items():
        #         print_slow(route, "(" + town.name, "to",
        #                    route.get_other(town).name + ")")
        # print()

        # import turtle
        # points = [(0, 0)]
        # for i in range(len(self.towns) - 1):
        #     s = math.sin(2 * math.pi / (len(self.towns) - 1) * i)
        #     c = math.cos(2 * math.pi / (len(self.towns) - 1) * i)
        #     points.append((-s * 200, c * 200))
        # turtle.clear()
        # turtle.speed(1.5)
        # turtle.penup()
        # for i, point in enumerate(points):
        #     turtle.goto(*point[:2])
        #     turtle.dot(10)
        #     turtle.goto(point[0] * 1.1 - 5, point[1] * 1.1 - 10)
        #     turtle.write(str(self.towns[i].max_connections))

        # for route in self.routes.values():
        #     if isinstance(route.town1, Route):
        #         continue

        #     turtle.penup()
        #     turtle.goto(*points[self.towns.index(route.town1)])
        #     turtle.pendown()
        #     if isinstance(route.town2, Route):
        #         turtle.goto(*points[self.towns.index(route.town2.town2)])
        #     else:
        #         turtle.goto(*points[self.towns.index(route.town2)])
        # turtle.penup()
        # turtle.goto(0, 0)

class Town:
    def __init__(self, name, desc, spawn_rate):
        self.linked_to = {}
        self.max_connections = 2
        self.name, self.desc = name, desc
        self.spawn_rate = spawn_rate
        self.shop = Shop()

    def print_description(self):
        print_slow(self.desc)

class Route:
    def __init__(self, town1, town2, num):
        self.town1, self.town2, self.num = town1, town2, num

    @property
    def name(self):
        return "Route " + str(self.num)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name + " (" + self.town1.name + " to " + self.town2.name + ")"

    def get_other(self, other):
        if other is self.town1:
            return self.town2
        elif other is self.town2:
            return self.town1
        else:
            raise ValueError(other.name + " is not part of this Route!")
