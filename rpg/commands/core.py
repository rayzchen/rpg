import os
import math
import time
import random
import datetime
import pickle
from ..utils import *
from .cmd import Command

__all__ = [
        "Game_help", "Game_stats", "Game_save", "Game_gifts",
        "Game_location", "Game_shop", "Game_items",
        "Game_equipment", "Game_sleep", "Game_travel", "Game_roam"]

class Game_help(Command):
    def __init__(self, owner):
        super(Game_help, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, item=None):
        if item is not None:
            if item not in self.owner.available_commands:
                return -1
            print_slow("Help on command", item + ":\n")
            if "%s" in self.owner.help_commands[item]:
                print_slow(self.owner.help_commands[item] % CONSTS["currency"])
            else:
                print_slow(self.owner.help_commands[item])
            return
        print_slow(self.owner.help_commands["help"])
        print()
        print_slow("Here are the available commands:")
        table(self.owner.available_commands, 2)

class Game_stats(Command):
    def __init__(self, owner):
        super(Game_stats, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, item=None):
        self = self.owner
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

class Game_save(Command):
    def __init__(self, owner):
        super(Game_save, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, name=None):
        self = self.owner
        play_time = datetime.datetime.now() - self.opening_time + self.play_time
        print_slow("Total play time:", strfdelta(
            play_time, "{D}d, {H}:{M:02}:{S:02}"))
        if not name:
            name = input_slow("Enter save name: ")
        if name == "":
            print_slow("Cancelled saving.")
            return
        # save_folder = os.path.expandvars(os.path.join("%localappdata%", "RPG", "saves"))
        directory = os.path.join(CONSTS["home"], "save")
        if os.path.isfile(os.path.join(directory, "save_" + name + ".rpg")):
            if input_slow("Do you want to overwrite the save file for the save name " +
                          name + "? (y/n) ").lower() != "y":
                return
        if not os.path.isdir(directory):
            os.mkdir(directory)
        with open(os.path.join(directory, "save_" + name + ".rpg"), "wb+") as f:
            self.play_time += datetime.datetime.now() - self.opening_time
            pickle.dump(self, f)
            print_slow("Saved successfully!")
            self.opening_time = datetime.datetime.now()

class Game_gifts(Command):
    def __init__(self, owner):
        super(Game_gifts, self).__init__(owner)
        self.min_args = 0
        self.max_args = 2

    def __call__(self, page="1"):
        self = self.owner
        if not page.isdecimal():
            return -1
        if len(self.player.gifts) == 0:
            print_slow(
                "Gifts\n\nYou have no Gifts. You can obtain Gifts from NPCs and other players.")
            return
        page = int(page) - 1
        if page * 10 >= len(self.player.gifts):
            print_slow("There is no page", page + 1, "of gifts!")
            return
        print_slow("Gifts\n")
        i = (page * 10)
        for gift in self.player.gifts[i:]:
            print_slow("Gift", str(i + 1) + ":", gift.item_name,
                        "received from", gift.from_who)
            i += 1
            if i > (page + 1) * 10:
                break
        print_slow("\nPage", page, "of",
                    math.ceil(len(self.player.gifts) / 10))
    
    def claim(self, number=None):
        self = self.owner
        if number is None:
            print_slow("Please provide the gift number to claim.")
        elif number == "all":
            for gift in reversed(self.player.gifts):
                gift.claim()
        else:
            if not number.isdecimal():
                return -1
            gift_num = int(number) - 1
            if gift_num >= len(self.player.gifts) or gift_num < 0:
                print_slow("There is no Gift at number",
                            number + "!")
                return
            self.player.gifts[gift_num].claim()

class Game_location(Command):
    def __init__(self, owner):
        super(Game_location, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, desc=None):
        self = self.owner
        if self.player.town is not None:
            if desc == "description":
                print()
                print_slow(self.player.town.desc)
            else:
                print_slow("You are on Floor", self.player.floor.num,
                           "and are at", self.player.town.name + ".")
        else:
            print_slow("You are OTM - off the map!")

class Game_items(Command):
    def __init__(self, owner):
        super(Game_items, self).__init__(owner)
        self.min_args = 0
        self.max_args = 2

    def __call__(self, page="1"):
        self = self.owner
        if not page.isdecimal():
            return -1
        if len(self.player.items) == 0:
            print_slow(
                "You have no items. You can obtain items from gifts or from Shops in towns.")
            return
        page_num = int(page) - 1
        if page_num * 10 >= len(self.player.items):
            print_slow("There is no page", page, "of items!")
            return
        print_slow("Your Items:\n")
        i = page_num * 10
        for item in self.player.items[i:]:
            if "number" in item.stats:
                print_slow("Item", str(i + 1) + ":", item.name,
                            "x" + str(item.stats["number"]))
            else:
                print_slow("Item", str(i + 1) + ":", item.name)
            i += 1
            if i >= (page_num + 1) * 10:
                break
        print_slow("\nPage", page_num + 1, "of",
                    math.ceil(len(self.player.items) / 10))
    
    def stats(self, num=""):
        self = self.owner
        if not num.isdecimal():
            return -1
        if len(self.player.items) == 0:
            print_slow(
                "You have no items. You can obtain items from gifts or from Shops in towns.")
            return
        num_int = int(num) - 1
        if num_int >= len(self.player.items) or num_int < 0:
            print_slow("There is no item at number", num + "!")
            return
        item = self.player.items[num_int]
        if "number" in item.stats:
            print_slow("This item has no stats!")
            return
        print_slow("Stats on item", num, "(" + item.name + "):\n")
        for stat_name, stat_value in item.stats.items():
            if stat_name in ["type", "number"]:
                continue
            if isinstance(stat_value, int):
                print_slow(self.player.town.shop.stat_keys[stat_name] +
                            ":", format(stat_value, ","))
            else:
                print_slow(self.player.town.shop.stat_keys[stat_name] + ":", stat_value)

class Game_shop(Command):
    def __init__(self, owner):
        super(Game_shop, self).__init__(owner)
        self.min_args = 0
        self.max_args = 0

    def __call__(self):
        self = self.owner
        print()
        print_slow("You have", format(self.player.money, ","), CONSTS["currency"] + "s.\n")
        self.player.town.shop.mainloop(self.player)

class Game_equipment(Command):
    def __init__(self, owner):
        super(Game_equipment, self).__init__(owner)
        self.min_args = 0
        self.max_args = 2

    def __call__(self, x=None):
        self = self.owner
        if x is not None:
            return -1
        print_slow("Equipped items:\n")
        print_slow("Sword:", self.player.equipment.sword)
        print_slow("Shield:", self.player.equipment.shield)
        print_slow("Cloak:", self.player.equipment.cloak)
        print_slow("Helmet:", self.player.equipment.helmet)
        print_slow("Shoes:", self.player.equipment.shoes)
    
    def equip(self, item_num=None):
        self = self.owner
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
    
    def unequip(self, item_num):
        self = self.owner
        if item_num is None:
            return -1
        if item_num not in self.player.equipment.equippable:
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

class Game_sleep(Command):
    def __init__(self, owner):
        super(Game_sleep, self).__init__(owner)
        self.min_args = 0
        self.max_args = 0
    
    def __call__(self):
        self = self.owner
        if self.player.town is not None:
            if input_slow("Are you sure you want to sleep? This costs 5 " + CONSTS["currency"] + "s. (y/n) ") == "y":
                self.player.money -= 5
                print_slow("Sleeping...")
                time.sleep(1)
                self.time_offset = (datetime.datetime.now() -
                                    self.opening_time) % datetime.timedelta(seconds=300)
                print_slow("Time offset is now", strfdelta(
                    self.time_offset, "{D}d, {H}:{M:02}:{S:02}"))
        else:
            print_slow("You are OTM - off the map!")

class Game_travel(Command):
    def __init__(self, owner):
        super(Game_travel, self).__init__(owner)
        self.min_args = 0
        self.max_args = 0
    
    def __call__(self):
        self = self.owner
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

        Route = type(choice)
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

class Game_roam(Command):
    def __init__(self, owner):
        super(Game_roam, self).__init__(owner)
        self.min_args = 0
        self.max_args = 0
    
    def __call__(self):
        self = self.owner
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
