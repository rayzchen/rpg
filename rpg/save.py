import datetime
import random
from .values import *

_hexes = []
def randomHex():
    _hex = ""
    while _hex in _hexes:
        _hex = "%0x" % random.getrandbits(64)
    _hexes.append(_hex)
    return _hex

def dt_to_string(dt):
    return "dt" + repr(dt)[17:]
def string_to_dt(string):
    return datetime.datetime(*map(int, string[3:-1].split(", ")))

def td_to_string(td):
    return f"td({td.seconds}, {td.microseconds})"
def string_to_td(string):
    return datetime.timedelta(*(list(map(int, string[3:-1].split(", "))) + [0, 0, 0]))

def item_to_string(item):
    item.id = randomHex()
    text = f"Item|{item.id}|{item.name}|{item.level}|" + "{"
    i = 0
    for stat_name, stat_value in item.stats.items():
        i += 1
        text += f"{stat_name}: {stat_value}"
        if i != len(item.stats):
            text += ", "
    return text + "}"
def string_to_item(string):
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
    return item

def equipment_to_string(equipment):
    items = []
    for item_type in equipment.equippable:
        item = getattr(equipment, item_type)
        if item is None:
            items.append(None)
            continue
        items.append(item_to_string(item))
    
    ids = []
    for item in items:
        if item:
            ids.append(item[5:31])
        else:
            ids.append("None")
    items = [item for item in items if item]

    text = "\n".join(items)
    text += "\nEquipment|" + "|".join(ids)
    return text.lstrip()
def string_to_equipment(string):
    parts = string.rstrip().split("\n")
    items = list(map(string_to_item, parts[:-1]))
    equipment_items = parts[-1].split("|")[1:]
    equipment_items2 = []
    for item in equipment_items:
        if item == "None":
            equipment_items2.append(None)
            continue
        for item2 in items:
            if item2.id == item:
                equipment_items2.append(item2)
            break
    print(equipment_items2)
    equipment = Equipment()
    for equippable, item in zip(equipment.equippable, equipment_items2):
        setattr(equipment, equippable, item)
    return equipment