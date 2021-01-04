import math
from ..utils import *
from .cmd import Command

__all__ = ["Shop_stats", "Shop_items", "Shop_info", "Shop_buy"]

class Shop_stats(Command):
    def __init__(self, owner):
        super(Shop_stats, self).__init__(owner)
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

class Shop_items(Command):
    def __init__(self, owner):
        super(Shop_items, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, page="1"):
        self = self.owner
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

class Shop_info(Command):
    def __init__(self, owner):
        super(Shop_info, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, index=None):
        self = self.owner
        if index is None or not index.isdecimal():
            return -1
        item_num = int(index) - 1
        if len(self.selling) <= item_num or item_num < 0:
            print_slow("There is no item at number", index + "!")
            return
        item = self.selling[item_num][0]
        print_slow("Info on item", index, "(" + item.name + "):\n")
        for stat_name, stat_value in item.stats.items():
            if stat_name == "type":
                continue
            if isinstance(stat_value, int):
                print_slow(self.stat_keys[stat_name] +
                           ":", format(stat_value, ","))
            else:
                print_slow(self.stat_keys[stat_name] + ":", stat_value)
        print_slow("Price:", self.selling[item_num][1])

class Shop_buy(Command):
    def __init__(self, owner):
        super(Shop_buy, self).__init__(owner)
        self.min_args = 0
        self.max_args = 1

    def __call__(self, index=None):
        self = self.owner
        if index is None or not index.isdecimal():
            return -1
        item_num = int(index) - 1
        if item_num >= len(self.selling) or item_num < 0:
            print_slow("There is no item at number", index + "!")
            return
        item = self.selling[item_num]
        if item[2]:
            print_slow("Item", index,
                       "(" + item[0].name + ") has already been sold!")
        elif item[1] > self.player.money:
            print_slow("You have insufficient funds to buy a" +
                       ("n" if item[0].name[0].lower() in "aeiou" else "") + " " + item[0].name + "!")
        else:
            if "number" in item[0].stats:
                if item[0].stats["number"] == 0:
                    print_slow("Item", index, "(" + item[0].name + ") has ran out of stock!")
                    return
                while (number := input_slow("How many do you want to buy? ")) != "":
                    if number.isdecimal():
                        num_int = int(number)
                        if num_int > item[0].stats["number"]:
                            print_slow("There are only", item[0].stats["number"], "left in stock!")
                            continue
                        elif num_int * item[1] > self.player.money:
                            print_slow("You have insufficient funds to buy", number + "x", item[0].name +
                                ("s" if num_int > 1 else "") + "!") 
                            continue
                        break
                    else:
                        print_slow("\"" + number + "\" is not a number!")
                answer = input_slow("Are you sure you want to buy " + number + "x " + item[0].name +
                                    ("s" if num_int > 1 else "") + " for " + str(num_int * item[1]) +
                                    " " + CONSTS["currency"] + "s? (y/n) ").lower()
                if answer == "y":
                    self.player.money -= num_int * item[1]
                    new_item = item[0].copy()
                    new_item.stats["number"] = num_int
                    self.player.items.append(new_item)
                    item[0].stats["number"] -= num_int
                    if item[0].stats["number"] == 0:
                        item[2] = True
                    print_slow("Item", index, "(" + item[0].name + ") has now sold out.")
                    print_slow("You have bought " + number + "x of item " + index + "(" +
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
                print_slow("You have bought item", index,
                           "(" + item[0].name + ") for", item[1], CONSTS["currency"] + "s.")
