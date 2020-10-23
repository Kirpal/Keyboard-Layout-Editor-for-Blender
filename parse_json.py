import json
import re
from .key import Key
from.keyboard import Keyboard


def select(obj: dict, keys: list) -> dict:
    """Return a copy of the given dict with only the listed keys"""
    return {k: obj[k] for k in keys if k in obj.keys()}


def load(filePath: str) -> Keyboard:
    """Parses KLE Raw JSON into a keyboard object"""
    # load JSON file
    layout = json.load(open(filePath, encoding="UTF-8",
                            errors="replace"), strict=False)
    # make empty keyboard
    keyboard = Keyboard()
    rowData = {}
    y = 0
    # iterate over rows
    for rowNum, row in enumerate(layout):
        x = 0
        # check if item is a row or if it is a dict of keyboard properties
        if type(row) != dict:
            # iterate over keys in row
            for pos, value in enumerate(row):
                # we skip over items that aren't keys (which are strings)
                if type(value) == str:
                    # default props values
                    props = {
                        "p": "",
                        "d": False,
                        "w": 1,
                        "h": 1,
                        "r": None,
                        "rx": 0,
                        "ry": 0,
                        "y": 0,
                        "c": "#cccccc",
                        "t": "#111111",
                        "f": 3,
                        "f2": 3,
                        "fa": None,
                        "a": 4,
                        # override defaults with any current row data
                        **rowData
                    }

                    # if the previous item is a dict add it to props and rowData
                    prev = row[pos - 1]
                    if type(prev) == dict:
                        props = {**props, **prev}
                        rowData = {**rowData, **select(prev, ["c", "t", "g", "a", "f", "f2", "p", "r", "rx"])}
                        if "x" in prev:
                            x += prev["x"]
                        if "y" in prev:
                            rowData["yCoord"] = prev["y"]
                            y += prev["y"]
                        if "ry" in prev:
                            rowData["ry"] = prev["ry"]
                            if "y" in prev:
                                y = prev["ry"] + rowData["yCoord"]
                            else:
                                y = prev["ry"]
                        elif ("r" in prev and "yCoord" not in rowData) or "rx" in prev:
                            if "ry" in rowData:
                                y = rowData["ry"]
                            else:
                                rowData["ry"] = 0
                                y = 0
                            if "y" in prev:
                                y += prev["y"]

                    props = {**props, **rowData}
                    key = Key(value, x, y, rowNum, pos, props)
                    # add the key to the current row
                    keyboard.add_key(key)
                    x += key.width
            y += 1
        else:
            # if the current item is a dict then add its properties to the keyboard
            if "backcolor" in row:
                keyboard.color = row["backcolor"]
            if "name" in row:
                keyboard.name = row["name"]
            if "switchType" in row:
                keyboard.switch_type = row["switchType"]
            if "notes" in row and (color_match := re.search(r'led_color:\s*#([a-fA-F0-9]{3,6})', row["notes"])) is not None:
                keyboard.led_color = '#' + color_match[1]
                if (brightness_match := re.search(r'led_brightness:\s*(1|0\.?[0-9]*)', row["notes"])) is not None:
                    keyboard.led_brightness = float(brightness_match[1])
            if "css" in row:
                keyboard.css = row["css"]
    return keyboard
