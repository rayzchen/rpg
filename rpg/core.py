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
        self.starting_town = towns.pop(0)
        self.starting_town = {
            "name": self.starting_town[0], "desc": self.starting_town[1:]}
        random.shuffle(towns)
        self.town_names = list(map(lambda x: x[0], towns))
        self.town_descs = list(map(lambda x: x[1:], towns))

    def setup_floor1(self):
        self.floors = [Floor(1,
                [self.starting_town["name"]] + self.town_names[:4],
                [self.starting_town["desc"]] + self.town_descs[:4])]
        del self.town_names[:4], self.town_descs[:4]

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
            print_slow("Defense points:", format(self.player.total_defense, ","))
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
        directory = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(os.path.join(directory, "save", "save_" + name + ".rpg")):
            if input_slow("Do you want to overwrite the save file for the save name " +
                          name + "? (y/n) ").lower() != "y":
                return
        if not os.path.isdir(os.path.join(directory, "save")):
            os.mkdir(os.path.join(directory, "save"))
        with open(os.path.join(directory, "save", "save_" + name + ".rpg"), "wb+") as f:
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
        print_slow("You have", self.player.money, CONSTS["currency"] + "s.\n")
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
                if stat_name == "type":
                    continue
                if isinstance(stat_value, int):
                    print_slow(Shop.stat_keys[stat_name] + ":", format(stat_value, ","))
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
            if page_num * 5 > len(self.player.items):
                print_slow("There is no page", stats_or_page + "!")
                return
            print_slow("Your Items:\n")
            i = page_num * 5
            for item in self.player.items[i:]:
                print_slow("Item", str(i + 1) + ":", item.name)
                i += 1
                if i >= (page_num + 1) * 5:
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
                print_slow("There is no type of equipment called", item_num + "!")
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
        print_slow("Routes connected to this town (" + self.player.town.name + "):\n")
        for town2, route in self.player.town.linked_to.items():
            print_slow("Route", route.num, "(Connects to", town2.name + ")", end="")
            if town2.linked_to[self.player.town] is not route:
                print_slow(" Note: Double route via Route", town2.linked_to[self.player.town].num)
            else:
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
        print_slow("Travelling along", str(choice) + "...")
        
        print(choice.town1.name, choice.town2.name, self.player.town.name)

        time.sleep(1) # Replace with monster fighting

        if isinstance(choice.get_other(self.player.town), Route):
            print_slow("Reached the center of Double Route", str(choice.num) + "/" +
                str(choice.get_other(self.player.town).num) + ".")
            print_slow("Travelling along", str(choice.get_other(self.player.town)) + "...")

            time.sleep(1) # Replace with monster fighting

            print_slow("Reached", choice.get_other(self.player.town).get_other(choice).name + ".")
            self.player.town = choice.get_other(self.player.town).get_other(choice)
        else:
            print_slow("Reached", choice.get_other(self.player.town).name + ".")
            self.player.town = choice.get_other(self.player.town)
    
    def roam(self):
        print_slow("You go to the edge of the town, and start roaming around for a monster to fight.")
        while True:
            print_slow("Roaming around...")
            time.sleep(random.random() * 3 + 2)
            if random.random() < self.player.town.spawn_rate:
                print_slow("A twig snaps, and something emerges out of the shadows.")
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
    }

    def __init__(self):
        items = [0, 1]
        self.selling = []
        for item in items:
            name = CONSTS["items"][item]["name"]
            price = CONSTS["items"][item]["price"]
            stats = CONSTS["items"][item].copy()
            stats.pop("name")
            stats.pop("price")
            self.selling.append([Item(name, stats), price, False])

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
            print_slow("Defense points:", format(self.player.total_defense, ","))
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
            if sold:
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
                print_slow(self.stat_keys[stat_name] + ":", format(stat_value, ","))
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
            answer = input_slow("Are you sure you want to buy a" +
                                ("n" if item[0].name[0].lower() in "aeiou" else "") + " " + item[0].name +
                                " for " + str(item[1]) + " " + CONSTS["currency"] + "s? (y/n) ").lower()
            if answer == "y":
                self.player.money -= item[1]
                self.player.items.append(item[0])
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

        no_of_3_conenctions = round(1 / 3 * len(self.towns))
        for town in self.towns[-no_of_3_conenctions:]:
            town.max_connections = 3
        
        n = 90 + self.num * 10 + 1
        route1 = Route(self.towns[0], random.choice(self.towns[1:]), n)
        self.towns[0].linked_to[route1.town2] = route1
        route1.town2.linked_to[self.towns[0]] = route1
        self.routes = {n - 1: route1}
        n += 1

        not_fully_connected = list(range(1, len(self.towns)))
        while len(not_fully_connected) >= 2:
            temp = not_fully_connected.copy()
            random.shuffle(temp)
            a, b = temp.pop(), temp.pop()
            route = Route(self.towns[a], self.towns[b], n)
            self.routes[n] = route
            self.towns[a].linked_to[self.towns[b]] = route
            self.towns[b].linked_to[self.towns[a]] = route
            n += 1
            if len(self.towns[a].linked_to) == self.towns[a].max_connections:
                not_fully_connected.remove(a)
            if len(self.towns[b].linked_to) == self.towns[b].max_connections:
                not_fully_connected.remove(b)

        double_route = list(self.routes.values())[random.randrange(1, len(self.routes))]
        route1 = Route(double_route.town1, None, double_route.num)
        route2 = Route(route1, double_route.town2, double_route.num + 1)
        route1.town2 = route2
        double_route.town1.linked_to[double_route.town2] = route1
        double_route.town2.linked_to[double_route.town1] = route2

        self.routes[double_route.num] = route1
        if double_route.num + 1 not in self.routes:
            self.routes[double_route.num + 1] = route2
        else:
            replacement = self.routes[double_route.num + 1]
            self.routes[double_route.num + 1] = route2
            self.routes[n] = replacement
            replacement.num = n
        
        for town in self.towns:
            print_slow(town.max_connections)
            for town2, route in town.linked_to.items():
                print_slow(route, "(" + town.name, "to", town2.name + ")")

        # points = [(-50, -25), (-100, 50), (50, 100), (100, -50), (-50, -100)]
        # turtle.hideturtle()
        # turtle.speed(0)
        # turtle.penup()
        # for point in points:
        #     turtle.goto(*point)
        #     turtle.dot(10)
        
        # for route in self.routes.values():
        #     turtle.penup()
        #     turtle.goto(*points[self.towns.index(route.town1)])
        #     turtle.pendown()
        #     turtle.goto(*points[self.towns.index(route.town2)])

class Town:
    def __init__(self, name, desc, spawn_rate):
        self.linked_to = {}
        if name == "Starting Town":
            self.max_connections = 1
        else:
            self.max_connections = 2
        self.name, self.desc = name, desc
        self.spawn_rate = spawn_rate
        self.shop = Shop()

    def print_description(self):
        print_slow(self.desc)

class Route:
    def __init__(self, town1, town2, num):
        self.town1, self.town2, self.num = town1, town2, num
        self.name = "Route " + str(num)
    
    def __repr__(self):
        return self.name
    __str__ = __repr__
    
    def get_other(self, other):
        if other is self.town1:
            return self.town2
        elif other is self.town2:
            return self.town1
        else:
            raise ValueError(other.name + " is not part of this Route!")