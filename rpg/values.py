from .utils import *

__all__ = ["Experience", "Equipment", "Gift", "Item", "Money"]

class Experience:
    def __init__(self):
        self.exp = 0
        self.total_exp = 0
        self.level = 0

    def add(self, amount):
        self.exp += amount
        self.total_exp += amount
        if self.exp > self.level * 5 + 20:
            while self.exp > self.level * 5 + 20:
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
        return format(self.total_exp, ",") + " (Level " + format(self.level, ",") + \
            " + " + format(self.exp, ",") + ")"
    __str__ = __repr__

class Equipment:
    equippable = ["sword", "shield", "cloak", "helmet", "shoes"]
    def __init__(self):
        self.sword = None
        self.shield = None
        self.cloak = None
        self.helmet = None
        self.shoes = None
    
    def __list__(self):
        return [getattr(self, item) for item in self.equippable]
    
    def __iter__(self):
        return iter(getattr(self, item) for item in self.equippable)

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
            self.player.items.extend([self.item(*self.args)
                                      for i in range(self.amount)])
            self.player.gifts.remove(self)
            print_slow("Claimed", self.item_name, "from", self.from_who)
        else:
            raise Exception("Cannot claim gift before giving it to someone")

class Item:
    def __init__(self, name, stats={}):
        self.name = name
        self.level = 0
        self.stats = stats

    def __repr__(self):
        return self.name + " +" + str(self.level)
    __str__ = __repr__

    @staticmethod
    def from_dict(d):
        stats = d.copy()
        stats.pop("name")
        stats.pop("price")
        return Item(d["name"], stats)

class Money(Gift):
    def __init__(self, from_who, amount):
        super(Money, self).__init__(from_who, format(
            amount, ",") + " " + CONSTS["currency"] + "s", None, amount)

    def claim(self):
        if self.player is not None:
            self.player.money += self.amount
            self.player.gifts.remove(self)
            print_slow("Claimed", self.item_name, "from", self.from_who)
        else:
            raise Exception("Cannot claim gift before giving it to someone")
