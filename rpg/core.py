import random
import time
import math
import datetime
# import turtle

from .utils import *
from .loader import CONSTS
from .values import *
from .commands import *

class Game:

    available_commands = CONSTS["available_commands"]
    help_commands = CONSTS["help_commands"]

    def __init__(self):
        self.started = False
        self.help = Game_help(self)
        self.stats = Game_stats(self)
        self.save = Game_save(self)
        self.cls = Any_Clear(self)
        self.clear = Any_Clear(self)
        self.gifts = Game_gifts(self)
        self.location = Game_location(self)
        self.items = Game_items(self)
        self.shop = Game_shop(self)
        self.equipment = Game_equipment(self)
        self.sleep = Game_sleep(self)
        self.travel = Game_travel(self)
        self.roam = Game_roam(self)

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

    def setup_floor1(self):
        self.town_data = CONSTS["towns"].copy()
        self.floors = [Floor(1, self.town_data[:5])]
        del self.town_data[:5]

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

    def mainloop(self):
        self.opening_time = datetime.datetime.now()
        if not self.started:
            self.setup_player()
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

    available_commands = ["stats", "items", "info", "buy"]
    stat_keys = {
        "attack": "Attack Boost", "defense": "Defense Boost", "desc": "Description", "effect": "Effect",
        "number": "Left in stock",
    }

    def __init__(self, items):
        items = items[1:]
        self.selling = []
        for item_num in items:
            item = Item.from_dict(CONSTS["items"][item_num])
            price = CONSTS["items"][item_num]["price"]
            self.selling.append([item, price, False])
        
        self.stats = Shop_stats(self)
        self.items = Shop_items(self)
        self.info = Shop_info(self)
        self.buy = Shop_buy(self)
        self.cls = Any_Clear(self)
        self.clear = Any_Clear(self)

    def mainloop(self, player):
        self.player = player
        mainloop(self, "Shop")
        self.player = None

class Floor:
    def __init__(self, num, town_info, prev_floor=None, next_floor=None):
        self.num = num
        self.prev_floor = prev_floor
        self.next_floor = next_floor
        self.towns = [Town(info,
            random.uniform(0.9 - 0.05 * self.num, 0.95 - 0.05 * self.num)
        ) for info in town_info]

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
    def __init__(self, info, spawn_rate):
        self.linked_to = {}
        self.max_connections = 2
        self.name, self.desc = info["name"], info["desc"]
        self.spawn_rate = spawn_rate
        self.shop = Shop(list(map(int, info["shop_info"].split(", "))))

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
