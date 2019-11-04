import json

fallbackProfile = "DCS"

labelMap = [
    # 0  1  2  3  4  5  6  7  8  9 10 11   // align flags
    [0, 6, 2, 8, 9, 11, 3, 5, 1, 4, 7, 10],  # 0 = no centering
    [1, 7, -1, -1, 9, 11, 4, -1, -1, -1, -1, 10],  # 1 = center x
    [3, -1, 5, -1, 9, 11, -1, -1, 4, -1, -1, 10],  # 2 = center y
    [4, -1, -1, -1, 9, 11, -1, -1, -1, -1, -1, 10],  # 3 = center x & y
    [0, 6, 2, 8, 10, -1, 3, 5, 1, 4, 7, -1],  # 4 = center front (default)
    [1, 7, -1, -1, 10, -1, 4, -1, -1, -1, -1, -1],  # 5 = center front & x
    [3, -1, 5, -1, 10, -1, -1, -1, 4, -1, -1, -1],  # 6 = center front & y
    [4, -1, -1, -1, 10, -1, -1, -1, -1, -1, -1, -1],  # 7 = center front & x & y
]

def parse_profile(profileString, homing):
    """Parse profile strings into standard models"""
    ret = profileString.upper().replace("R", "").replace("0", "").replace("5", "").replace(
        "6", "").replace("7", "").replace("8", "").replace("9", "").replace(" ", "")

    if ret != "SASPACE":
        ret = ret.replace("SPACE", "")

    # Normalize unsculpted SA profile to SA ROW 3
    if ret == "SA":
        ret = "SA3"

    if ret == "" or ret not in ["DSA", "DCS", "SA1", "SA2", "SA3", "SA4", "SASPACE"]:
        ret = fallbackProfile

    # Set homing profile for supported profiles (currently only SA)
    if homing and ret in ["SA1", "SA2", "SA3", "SA4"]:
        ret = "SA3D"

    return ret

def reorder_labels(labels, align):
    """Reorders labels based on alignment"""
    ret = ["", "", "", "", "", "", "", "", "", "", "", ""]
    for pos, label in enumerate(labels):
        ret[labelMap[align][pos]] = label
    return ret


def reorder_sizes(primary, secondary, individual, align):
    """Reorders font sizes for labels"""
    if secondary is None:
        secondary = primary
    ret = [primary, secondary, secondary, secondary, secondary, secondary,
         secondary, secondary, secondary, secondary, secondary, secondary]
    if individual:
        for pos, size in enumerate(individual):
            if size == 0:
                ret[labelMap[align][pos]] = primary
            else:
                ret[labelMap[align][pos]] = size
    else:
        ret = [primary, secondary, secondary, secondary, secondary, secondary,
             secondary, secondary, secondary, secondary, secondary, secondary]
    return ret


def reorder_colors(default, colors, align):
    """Reorders label colors"""
    ret = [default, default, default, default, default, default,
           default, default, default, default, default, default]

    individual = colors.split('\n')

    if len(individual) > 1:
        for pos, color in enumerate(individual):
            if color is not None and color is not '':
                ret[labelMap[align][pos]] = color
    else:
        ret = [individual[0], individual[0], individual[0], individual[0], individual[0], individual[
            0], individual[0], individual[0], individual[0], individual[0], individual[0], individual[0]]
    return ret

def load(filePath):
    """Parses KLE Raw JSON into dict"""
    # load JSON file
    layout = json.load(open(filePath, encoding="UTF-8",
                            errors="replace"), strict=False)
    # make empty keyboard dict
    keyboard = {}
    rowData = {}
    # add list of keyboard rows
    keyboard["rows"] = []
    keyboard["keyCount"] = 0
    y = 0
    # default align
    align = 4
    # iterate over rows
    for rowNum, row in enumerate(layout):
        x = 0
        # add empty row
        keyboard["rows"].append([])
        # check if item is a row or if it is a dict of keyboard properties
        if type(row) != dict:
            # get row data from previous row
            rowData = rowData
            rowData["y"] = y
            # iterate over keys in row
            for pos, value in enumerate(row):
                # check if item is a key or dict of key properties
                if type(value) == str:
                    # key is a dict with all the key's properties
                    key = {}
                    # if the previous item is a dict add the data to the rest
                    # of the row, or the current key, depending on what the
                    # property is
                    if type(row[pos - 1]) == dict:
                        # prev is the previous item in the row
                        prev = row[pos - 1]
                        # if prev has property set then add it to key
                        if "x" in prev:
                            key["xCoord"] = prev["x"]
                            x += key["xCoord"]
                        else:
                            key["xCoord"] = 0
                        if "y" in prev:
                            rowData["yCoord"] = prev["y"]
                            rowData["y"] += prev["y"]
                            y += prev["y"]
                        if "w" in prev:
                            key["w"] = prev["w"]
                        else:
                            key["w"] = 1
                        if "h" in prev:
                            key["h"] = prev["h"]
                        else:
                            key["h"] = 1
                        if "fa" in prev:
                            key["fa"] = prev["fa"]
                        if "x2" in prev:
                            key["x2"] = prev["x2"]
                        if "y2" in prev:
                            key["y2"] = prev["y2"]
                        if "w2" in prev:
                            key["w2"] = prev["w2"]
                        if "h2" in prev:
                            key["h2"] = prev["h2"]
                        if "l" in prev:
                            key["l"] = prev["l"]
                        if "n" in prev:
                            key["n"] = prev["n"]
                        if "c" in prev:
                            rowData["c"] = prev["c"]
                        if "t" in prev:
                            rowData["t"] = prev["t"]
                        if "g" in prev:
                            rowData["g"] = prev["g"]
                        if "a" in prev:
                            rowData["a"] = prev["a"]
                        if "f" in prev:
                            rowData["f"] = prev["f"]
                        if "f2" in prev:
                            rowData["f2"] = prev["f2"]
                        if "p" in prev:
                            rowData["p"] = prev["p"]
                        if "d" in prev:
                            key["d"] = prev["d"]
                        else:
                            key["d"] = False
                        if "r" in prev:
                            rowData["r"] = prev["r"]
                            rowData["rRow"] = 0
                        if "rx" in prev:
                            rowData["rx"] = prev["rx"]
                        if "ry" in prev:
                            if "yCoord" in rowData:
                                rowData["ry"] = prev["ry"]
                                rowData["y"] = prev["ry"] + rowData["yCoord"]
                                y = prev["ry"] + rowData["yCoord"]
                            else:
                                rowData["ry"] = prev["ry"]
                                rowData["y"] = prev["ry"]
                                y = prev["ry"]
                        elif "r" in prev and "ry" in rowData:
                            if "yCoord" in rowData:
                                rowData["y"] = rowData["ry"] + rowData["yCoord"]
                                y = rowData["ry"] + rowData["yCoord"]
                            else:
                                rowData["y"] = rowData["ry"]
                                y = rowData["ry"]
                        elif "r" in prev:
                            if "yCoord" in rowData:
                                rowData["ry"] = 0
                                rowData["y"] = rowData["yCoord"]
                                y = rowData["yCoord"]
                            else:
                                rowData["ry"] = 0
                                rowData["y"] = 0
                                y = 0

                        # if rowData has property set then add it to key
                        if "a" in rowData:
                            align = rowData["a"]

                    # if the previous item isn't a dict
                    else:
                        key["xCoord"] = 0
                        key["d"] = False
                        key["w"] = 1
                        key["h"] = 1

                    # if rowData has property set then add it to key
                    if "c" in rowData:
                        key["c"] = rowData["c"]
                    else:
                        key["c"] = "#cccccc"
                    if "t" in rowData:
                        key["t"] = rowData["t"]
                    else:
                        key["t"] = "#111111"
                    if "g" in rowData:
                        key["g"] = rowData["g"]
                    if "a" in rowData:
                        key["a"] = rowData["a"]
                    if "f" in rowData:
                        key["f"] = rowData["f"]
                    else:
                        key["f"] = 3
                    if "f2" in rowData:
                        key["f2"] = rowData["f2"]
                    else:
                        key["f2"] = None
                    if "r" in rowData:
                        key["r"] = rowData["r"]
                    if "rx" in rowData:
                        key["rx"] = rowData["rx"]
                    if "ry" in rowData:
                        key["ry"] = rowData["ry"]

                    if "p" not in rowData:
                        key["p"] = fallbackProfile
                    else:
                        key["p"] = parse_profile(rowData["p"], "n" in key)

                    if "fa" not in key:
                        key["fa"] = None

                    # set the text on the key
                    key["v"] = {}
                    key["v"]["labels"] = reorder_labels(value.split('\n'), align)
                    key["f"] = reorder_sizes(key["f"], key["f2"], key["fa"], align)
                    key["t"] = reorder_colors(None, key["t"], align)
                    key["v"]["raw"] = value

                    # set the row and column of the key
                    key["row"] = rowNum
                    key["col"] = pos
                    # set x and y coordinates of key
                    key["x"] = x
                    key["y"] = rowData["y"]

                    if "rx" in key:
                        key["x"] += key["rx"]

                    # add the key to the current row
                    keyboard["rows"][key["row"]].append(key)
                    keyboard["keyCount"] += 1
                    x += key["w"]
            y += 1
        else:
            # if the current item is a dict then add the backcolor property to
            # the keyboard
            if "backcolor" in row:
                keyboard["backcolor"] = row["backcolor"]
            if "switchType" in row:
                keyboard["switchType"] = row["switchType"]
            if "led" in row:
                keyboard["led"] = row["led"]
            if "css" in row:
                keyboard["css"] = row["css"]
    return keyboard
