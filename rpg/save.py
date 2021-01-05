import datetime
import random
import os
import zlib
from .values import *
from .core import *
from .loader import CONSTS

_hexes = []
def randomHex():
    _hex = "%0x" % random.getrandbits(64)
    while _hex in _hexes:
        _hex = "%0x" % random.getrandbits(64)
    _hexes.append(_hex)
    return _hex

def experience_to_string(experience):
    return f"exp({experience.total_exp})"
def string_to_experience(string):
    exp = Experience()
    exp.add(int(string[4:-1]))
    return exp

def encode(string):
    out = ""
    string = list(reversed(string))
    offset = 1
    curr = ord(string.pop())
    while len(string):
        curr <<= 7
        curr += ord(string.pop())
        upper = curr & (0xFF << (7 - offset))
        out += chr(upper >> (7 - offset))
        curr -= upper
        offset += 1
        if offset == 7 and len(string):
            offset = 0
            curr <<= 7
            curr += ord(string.pop())
    curr <<= offset
    out += chr(curr)
    return out

def decode(string):
    out = ""
    string = list(reversed(string))
    offset = 1
    curr = 0
    while len(string):
        print(bin(curr))
        curr <<= 8
        curr += ord(string.pop())
        upper = curr & (0x7F << offset)
        out += chr(upper >> offset)
        curr -= upper
        offset += 1
        if offset == 8:
            out += chr(curr)
            curr = 0
            offset = 1
    return out

def dt_to_string(dt):
    return "dt" + repr(dt)[17:]
def string_to_dt(string):
    return datetime.datetime(*map(int, string[3:-1].split(", ")))

def td_to_string(td):
    return f"td({td.seconds}, {td.microseconds})"
def string_to_td(string):
    return datetime.timedelta(*(list(map(int, string[3:-1].split(", "))) + [0, 0, 0]))

class Pickler:
    def __init__(self):
        self.items = {"None": None}
    
    def item_to_string(self, item):
        if not hasattr(item, "id"):
            item.id = randomHex()
            self.items[item.id] = item
        text = f"Item|{item.id}|{item.name}|{item.level}|" + "{"
        i = 0
        for stat_name, stat_value in item.stats.items():
            i += 1
            text += f"{stat_name}: {stat_value}"
            if i != len(item.stats):
                text += ", "
        return text + "}"
    
    def string_to_item(self, string):
        parts = string.rstrip().split("|")[1:]
        item_id = parts[0]
        name = parts[1]
        level = int(parts[2])
        stats = map(lambda x: x.split(": "), parts[3][1:-1].split(", "))
        stats = {a[0]: a[1] for a in stats}
        for stat in stats:
            if stats[stat].isdecimal():
                stats[stat] = int(stats[stat])
        item = Item(name, stats)
        item.level = level
        item.id = item_id
        self.items[item.id] = item
        return item
    
    def gift_to_string(self, gift):
        if isinstance(Money, gift):
            return f"Money({gift.from_who}, {gift.amount})"
        else:
            return f"Money({gift.from_who}, {gift.item.id})"
    
    def string_to_gift(self, string):
        if string[:string.index("(")] == "Money":
            return Money(*string[5:-1].split(", "))
        else:
            from_who, item_id = string[5:-1].split(", ")
            return Gift(from_who, self.items[item_id])

    def equipment_to_string(self, equipment):
        ids = []
        for item_type in equipment.equippable:
            item = getattr(equipment, item_type)
            if item is None:
                ids.append("None")
                continue
            ids.append(item.id)
        return "Equipment|" + "|".join(ids)

    def string_to_equipment(self, string):
        ids = string.rstrip().split("|")[1:]
        items = list(map(lambda x: self.items[x], ids))
        equipment = Equipment()
        for item in items:
            if item:
                setattr(equipment, item.stats["type"], item)
        return equipment
    
    def player_to_string(self, player):
        items = player.items + list(map(lambda x: x.item, player.gifts))
        text = "\n".join(map(self.item_to_string, items))
        text += "\n" + self.equipment_to_string(player.equipment)
        text += f"\nPlayer|{player.name}|{player.health}|{player.max_health}|"
        text += experience_to_string(player.experience) + "|"
        text += f"{player.attack}|{player.defense}|{player.money}|"
        text += ", ".join(map(self.gift_to_string, player.gifts))
        text += "|" + ", ".join(map(lambda x: x.id, player.items)) + "|"
        text += f"{player.town.name}|{player.floor.num}|"
        text += f"{player.thirst}|{player.hunger}|{player.furthest_route}"
        return text
    
    def string_to_player(self, string):
        lines = [line for line in string.rstrip().split("\n") if line]
        player_line = lines.pop()
        equipment_line = lines.pop()
        items = []
        for line in lines:
            items.append(self.string_to_item(line))
        equipment = self.string_to_equipment(equipment_line)
        
        parts = player_line.split("|")[1:]
        parts[1:3] = list(map(int, parts[1:3]))
        parts[4:6] = list(map(int, parts[4:6]))
        parts[3] = string_to_experience(parts[3])
        parts[6] = int(parts[6])
        player = Player(*parts[:7])
        player.equipment = equipment

        player.gifts = list(map(self.string_to_gift, [gift for gift in parts[7].split(", ") if gift]))
        player.items = list(map(lambda x: self.items[x], [item for item in parts[8].split(", ") if item]))
        player.town = parts[9]
        player.floor = int(parts[10])
        player.thirst = int(parts[11])
        player.hunger = int(parts[12])
        player.furthest_route = int(parts[13])
        return player

    def town_to_string(self, town):
        text = "Town|" + str(CONSTS["towns"].index(town.info)) + "|"
        text += str(town.spawn_rate) + "|Shop("
        for item in town.shop.selling:
            text += f"[{int(item[2])} "
            text += "None" if "number" not in item[0].stats else str(item[0].stats["number"])
            text += "], "
        text = text[:-2] + ")"
        return text
    
    def string_to_town(self, string):
        parts = string.rstrip().split("|")[1:]
        town = Town(CONSTS["towns"][int(parts[0])], float(parts[1]))
        for i, item in enumerate(parts[2][5:-1].split(", ")):
            parts2 = item[1:-1].split(" ")
            town.shop.selling[i][2] = bool(int(parts2[0]))
            if parts2[1] != "None":
                town.shop.selling[i][0].stats["number"] = int(parts2[1])
        return town
    
    def floor_to_string(self, floor):
        text = "\n".join(map(self.town_to_string, floor.towns)) + "\n"
        
        for route in floor.routes.values():
            if isinstance(route.town1, Route):
                continue
            text += f"Route|{route.num}|{route.town1.name}|"
            if isinstance(route.town2, Route):
                text += route.town2.get_other(route).name + "|1\n"
            else:
                text += route.town2.name + "|0\n"
        text += "Floor|" + str(floor.num) + "|" + str(len(floor.towns))
        return text
    
    def string_to_floor(self, string):
        lines = string.rstrip().split("\n")
        parts = lines.pop().split("|")[1:]
        town_lines = lines[:int(parts[1])]
        route_lines = lines[int(parts[1]):]

        floor = Floor(int(parts[0]), None, pickle=True)
        floor.towns = list(map(self.string_to_town, town_lines))
        town_dict = {town.name: town for town in floor.towns}
        
        for line in route_lines:
            parts = line.split("|")[1:]
            if int(parts[3]):
                route1 = Route(town_dict[parts[1]], None, int(parts[0]))
                route2 = Route(route1, town_dict[parts[2]], int(parts[0]) + 1)
                route1.town2 = route2
                floor.routes[route1.num] = route1
                floor.routes[route2.num] = route2
                route1.town1.linked_to[route2.town2] = route1
                route2.town2.linked_to[route1.town1] = route2
            else:
                route = Route(town_dict[parts[1]], town_dict[parts[2]], int(parts[0]))
                floor.routes[route.num] = route
                route.town1.linked_to[route.town2] = route
        
        return floor
    
    def game_to_string(self, game):
        text = "\n\n".join(map(self.floor_to_string, game.floors))
        text += "\n\n" + self.player_to_string(game.player)
        text += "\n\nGame|" + dt_to_string(game.opening_time) + "|"
        text += td_to_string(game.time_offset) + "|"
        text += td_to_string(game.play_time) + "|"
        text += dt_to_string(game.start_time)
        return text
    
    def string_to_game(self, string):
        sections = string.rstrip().split("\n\n")
        player = self.string_to_player(sections[-2])
        floors = list(map(self.string_to_floor, sections[:-2]))
        game = Game()
        game.player = player
        game.floors = floors
        player.floor = game.floors[player.floor - 1]
        town_dict = {town.name: town for town in player.floor.towns}
        player.town = town_dict[player.town]

        parts = sections[-1].split("|")[1:]
        game.opening_time = string_to_dt(parts[0])
        game.time_offset = string_to_td(parts[1])
        game.play_time = string_to_td(parts[2])
        game.start_time = string_to_dt(parts[3])
        game.started = True
        return game
    
    def save_game(self, game, name):
        text = self.game_to_string(game).replace("\n", "\a")
        compress = zlib.compress(text.encode(), 9)
        with open(name, "wb+") as f:
            f.write(compress)
    
    def load_game(self, name):
        with open(name, "rb") as f:
            compress = f.read()
        text = zlib.decompress(compress).decode()
        return self.string_to_game(text.replace("\a", "\n"))