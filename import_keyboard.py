"""
This script imports JSON File format files to Blender.

It uses the JSON file downloaded from keyboard-layout-editor.com

Usage:
Execute this script from the "File->Import" menu and choose a JSON file to
open.
"""

# import needed modules
import bpy
import json
import urllib.request
import os
import re
from math import pi
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

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

gotham = bpy.data.fonts.load(os.path.join(os.path.dirname(
    __file__), "gotham.ttf"))
noto = bpy.data.fonts.load(os.path.join(os.path.dirname(
    __file__), "noto.ttf"))

fonts = [None for i in range(0, 12)]

googleFonts = json.load(open(os.path.join(os.path.dirname(
    __file__), "fonts.json")))

# Function to parse legends


def reorderLabels(labels, align):
    ret = ["", "", "", "", "", "", "", "", "", "", "", ""]
    for pos, label in enumerate(labels):
        ret[labelMap[align][pos]] = label
    return ret


def reorderSizes(default, individual, align):
    ret = [default, default, default, default, default, default,
           default, default, default, default, default, default]
    if individual:
        for pos, size in enumerate(individual):
            if size == 0:
                ret[labelMap[align][pos]] = default
            else:
                ret[labelMap[align][pos]] = size
    else:
        ret = [default, default, default, default, default, default,
               default, default, default, default, default, default]
    return ret


def reorderColors(default, individual, align):
    ret = [default, default, default, default, default, default,
           default, default, default, default, default, default]
    if len(individual) > 1:
        for pos, color in enumerate(individual):
            ret[labelMap[align][pos]] = color
    else:
        ret = [individual[0], individual[0], individual[0], individual[0], individual[0], individual[
            0], individual[0], individual[0], individual[0], individual[0], individual[0], individual[0]]
    return ret

# convert HEX color to RGB


def hex2rgb(hex):
    hex = hex.lstrip("#")

    if len(hex) == 3:
        r = int(str(hex[0:1]) + str(hex[0:1]), 16)
        g = int(str(hex[1:2]) + str(hex[1:2]), 16)
        b = int(str(hex[2:3]) + str(hex[2:3]), 16)
    else:
        r = int(str(hex[0:2]), 16)
        g = int(str(hex[2:4]), 16)
        b = int(str(hex[4:6]), 16)

    rgb = [r, g, b]

    return rgb

# Make and modify materials


class Material:

    def set_cycles(self):
        scn = bpy.context.scene
        if not scn.render.engine == 'CYCLES':
            scn.render.engine = 'CYCLES'

    def make_material(self, name):
        matNames = []
        matPos = {}
        for position, material in enumerate(bpy.data.materials):
            matNames.append(material.name)
            matPos[material.name] = position

        if name in matNames:
            bpy.data.materials[matPos[name]].name = name + ".000"

        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        self.nodes = self.mat.node_tree.nodes

    def link(self, from_node, from_slot_name, to_node, to_slot_name):
        input = to_node.inputs[to_slot_name]
        output = from_node.outputs[from_slot_name]
        self.mat.node_tree.links.new(input, output)

    def makeNode(self, type, name):
        self.node = self.nodes.new(type)
        self.node.name = name
        self.xpos += 200
        self.node.location = self.xpos, self.ypos
        return self.node

    def new_row():
        self.xpos = 0
        self.ypos += 200

    def __init__(self):
        self.xpos = 0
        self.ypos = 0

# parses KLE Raw JSON into dict


def getKey(filePath):
    # load JSON file
    layout = json.load(open(filePath, encoding="UTF-8",
                            errors="replace"), strict=False)
    # make empty keyboard dict
    keyboard = {}
    rowData = {}
    # add list of keyboard rows
    keyboard["rows"] = []
    keyboard["keyCount"] = 0
    y = 0 + 0.05
    # default align
    align = 4
    # iterate over rows
    for rowNum, row in enumerate(layout):
        x = 0.05
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
                            key["w"] = prev["w"] - 0.05
                        else:
                            key["w"] = 1 - 0.05
                        if "h" in prev:
                            key["h"] = prev["h"]
                        else:
                            key["h"] = 1
                        if "x2" in prev:
                            key["x2"] = prev["x2"]
                        if "y2" in prev:
                            key["y2"] = prev["y2"]
                        if "w2" in prev:
                            key["w2"] = prev["w2"] - 0.05
                        if "h2" in prev:
                            key["h2"] = prev["h2"] - 0.05
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
                        if "fa" in prev:
                            rowData["fa"] = prev["fa"]
                        else:
                            rowData["fa"] = None
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
                            rowData["ry2"] = prev["ry"]
                            rowData["ry"] = prev["ry"]
                        elif "ry" in rowData and "r" in prev:
                            rowData["ry2"] = rowData["ry"]

                        # if rowData has property set then add it to key
                        if "c" in rowData:
                            key["c"] = rowData["c"]
                        if "t" in rowData:
                            key["t"] = rowData["t"]
                        else:
                            key["t"] = "#111111"
                        if "g" in rowData:
                            key["g"] = rowData["g"]
                        if "a" in rowData:
                            key["a"] = rowData["a"]
                            align = key["a"]
                        if "f" in rowData:
                            key["f"] = rowData["f"]
                        else:
                            key["f"] = 3
                        if "fa" in rowData:
                            key["fa"] = rowData["fa"]
                        else:
                            key["fa"] = None
                        if "f2" in rowData:
                            key["f2"] = rowData["f2"]
                        if "r" in rowData:
                            key["r"] = rowData["r"]
                        if "rx" in rowData:
                            key["rx"] = rowData["rx"]
                        if "ry" in rowData:
                            key["ry"] = rowData["ry"]
                        if "ry2" in rowData:
                            if "yCoord" in rowData:
                                key["ry2"] = rowData["ry2"] + rowData["yCoord"]
                            else:
                                key["ry2"] = rowData["ry2"]

                        if "p" in rowData:
                            key["p"] = rowData["p"].replace("R", "").replace("r", "").replace("0", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("SPACE", "").replace("space", "").replace(" ", "")
                        else:
                            key["p"] = "DCS"

                        if key["p"] == "" or key["p"] not in ["DSA", "DCS", "SA1","SA2", "SA3", "SA4"]:
                            key["p"] = "DCS"

                        # Use deep dish cap
                        if "n" in key and key["p"] in ["SA1","SA2", "SA3", "SA4"]:
                            key["p"] = "SA3D"

                        # set the text on the key
                        key["v"] = {}
                        key["v"]["labels"] = reorderLabels(
                            value.split('\n'), align)
                        key["f"] = reorderSizes(key["f"], key["fa"], align)
                        key["t"] = reorderColors(
                            None, key["t"].split('\n'), align)
                        key["v"]["raw"] = value

                        # set the row and column of the key
                        key["row"] = rowNum
                        key["col"] = pos
                        # set x and y coordinate of key
                        key["x"] = x
                        key["y"] = rowData["y"]

                        if "rx" in key:
                            key["x"] += key["rx"]
                        if "ry2" in key:
                            key["y"] = key["ry2"]

                        # add the key to the current row
                        keyboard["rows"][key["row"]].append(key)
                        keyboard["keyCount"] += 1
                    # if the previous item isn't a dict
                    else:
                        # if rowData has property set then add it to key
                        if "c" in rowData:
                            key["c"] = rowData["c"]
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
                        if "fa" in rowData:
                            key["fa"] = rowData["fa"]
                        else:
                            key["fa"] = None
                        if "f2" in rowData:
                            key["f2"] = rowData["f2"]
                        if "r" in rowData:
                            key["r"] = rowData["r"]
                        if "rx" in rowData:
                            key["rx"] = rowData["rx"]
                        if "ry" in rowData:
                            key["ry"] = rowData["ry"]
                        if "ry2" in rowData:
                            if "yCoord" in rowData:
                                key["ry2"] = rowData["ry2"] + rowData["yCoord"]
                            else:
                                key["ry2"] = rowData["ry2"]

                        if "p" in rowData:
                            key["p"] = rowData["p"].replace("R", "").replace("r", "").replace("0", "").replace(
                                "5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("SPACE", ""). replace("space", "").replace(" ", "")
                        else:
                            key["p"] = "DCS"

                        if key["p"] == "" or key["p"] not in ["DSA", "DCS", "SA1", "SA2", "SA3", "SA4"]:
                            key["p"] = "DCS"

                        if "n" in key and key["p"] in ["SA1","SA2", "SA3", "SA4"]:
                            key["p"] = "SA3D"

                        key["xCoord"] = 0
                        key["d"] = False
                        key["w"] = 1 - 0.05
                        key["h"] = 1

                        # set the text on the key
                        key["v"] = {}
                        key["v"]["labels"] = reorderLabels(
                            value.split('\n'), align)
                        key["f"] = reorderSizes(key["f"], key["fa"], align)
                        key["t"] = reorderColors(
                            None, key["t"].split('\n'), align)
                        key["v"]["raw"] = value

                        # set the row and column of the key
                        key["row"] = rowNum
                        key["col"] = pos
                        # set x and y coordinates of key
                        key["x"] = x
                        key["y"] = rowData["y"]

                        if "rx" in key:
                            key["x"] += key["rx"]
                        if "ry2" in key:
                            key["y"] = key["ry2"]

                        # add the key to the current row
                        keyboard["rows"][key["row"]].append(key)
                        keyboard["keyCount"] += 1
                    x += key["w"] + 0.05
            y += 1 + 0.05
            if "ry2" in key:
                rowData["ry2"] += 1
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


def read(filepath):
    bpy.context.window.cursor_set("WAIT")
    # parse raw data into dict
    keyboard = getKey(filepath)

    # template objects that have to be appended in and then deleted at the end

    defaultObjects = ["DCSTL", "DCSTM", "DCSTR", "DCSML", "DCSMM", "DCSMR", "DCSBL", "DCSBM", "DCSBR", "DCSTLF", "DCSTMF", "DCSTRF", "DCSMLF", "DCSMMF", "DCSMRF", "DCSBLF", "DCSBMF", "DCSBRF", "DCSTLS", "DCSTMS", "DCSTRS", "DCSMLS", "DCSMMS", "DCSMRS", "DCSBLS", "DCSBMS", "DCSBRS",
                      "DSATL", "DSATM", "DSATR", "DSAML", "DSAMM", "DSAMR", "DSABL", "DSABM", "DSABR", "DSATLF", "DSATMF", "DSATRF", "DSAMLF", "DSAMMF", "DSAMRF", "DSABLF", "DSABMF", "DSABRF", "DSATLS", "DSATMS", "DSATRS", "DSAMLS", "DSAMMS", "DSAMRS", "DSABLS", "DSABMS", "DSABRS",
                      "SA1TL", "SA1TM", "SA1TR", "SA1ML", "SA1MM", "SA1MR", "SA1BL", "SA1BM", "SA1BR", # SA R1
                      "SA2TL", "SA2TM", "SA2TR", "SA2ML", "SA2MM", "SA2MR", "SA2BL", "SA2BM", "SA2BR", # SA R2
                      "SA3TL", "SA3TM", "SA3TR", "SA3ML", "SA3MM", "SA3MR", "SA3BL", "SA3BM", "SA3BR", # SA R3
                      "SA3DTL", "SA3DTM", "SA3DTR", "SA3DML", "SA3DMM", "SA3DMR", "SA3DBL", "SA3DBM", "SA3DBR", #deep dish
                      "SA4TL", "SA4TM", "SA4TR", "SA4ML", "SA4MM", "SA4MR", "SA4BL", "SA4BM", "SA4BR", # SA R4
                      "SATLF", "SATMF", "SATRF", "SAMLF", "SAMMF", "SAMRF", "SABLF", "SABMF", "SABRF", "SATLS", "SATMS", "SATRS", "SAMLS", "SAMMS", "SAMRS", "SABLS", "SABMS", "SABRS",
                      "side", "switch", "led"]
    # blender file with template objects
    templateBlend = os.path.join(os.path.dirname(
        __file__), "template.blend", "Object")

    # append all the template objects
    for key in defaultObjects:
        bpy.ops.wm.append(filepath=templateBlend + key,
                          directory=templateBlend, filename=key)

    # get the current scene and change display device so colors are accurate
    scn = bpy.context.scene
    scn.display_settings.display_device = "None"

    # set width and height of keyboard
    width = 0
    height = 0

    # get fonts from css
    if "css" in keyboard:
        selectors = []
        props = []
        rules = []
        css = keyboard["css"]
        css = re.sub(r'(\@import [^;]+\;|\@font-face [^\}]+\})', "", css)
        css = re.split(r'\{|\}', css)

        css = filter(None, css)

        for idx, item in enumerate(css):
            if idx % 2 == 0:
                selectors.append(item)
            else:
                props.append(item)

        selectors = [re.split(r" |\,", i) for i in selectors]
        selectors = [filter(None, i) for i in selectors]
        selectors = [[re.sub(r"\s+", "", s) for s in sList]
                     for sList in selectors]

        props = [i.split(";") for i in props]

        fontProps = [None for i in props]
        for idx, propList in enumerate(props):
            for prop in propList:
                if re.sub(r"\s+", "", prop.split(":")[0]) == "font-family":
                    fontProps[idx] = re.sub(r"\s+", "", prop.split(":")[1])
            if fontProps[idx] == None:
                selectors[idx] = None

        for idx, selector in enumerate(selectors):
            if selector is not None and fontProps[idx] is not None:
                rules.append({"selectors": selector, "font": fontProps[idx]})

        for rule in rules:
            for selector in rule["selectors"]:
                if selector == "*":
                    for labelSelector in range(0, 12):
                        fonts[labelSelector] = rule["font"].replace(
                            '"', "").replace("'", "")
                elif int(selector.replace(".keylabel", "")) >= 0 and int(selector.replace(".keylabel", "")) <= 11:
                    fonts[int(selector.replace(
                        ".keylabel", ""))] = rule["font"].replace(
                            '"', "").replace("'", "")
    for pos, font in enumerate(fonts):
        if font == None or font not in googleFonts.keys():
            fonts[pos] = gotham
        else:
            tempDir = bpy.app.tempdir
            urllib.request.urlretrieve(
                googleFonts[font], os.path.join(tempDir, font + ".ttf"))
            fonts[pos] = bpy.data.fonts.load(
                os.path.join(tempDir, font + ".ttf"))

    bpy.context.window_manager.progress_begin(keyboard["keyCount"], 0)
    bpy.context.window.cursor_set("DEFAULT")
    currentKey = 0

    # iterate over rows in keyboard
    for row in keyboard["rows"]:
        # iterate over keys in row
        for key in row:
            if key["d"] is False:
                # new material for key
                m = Material()
                m.set_cycles()
                m.make_material("%s-%s" % (key["row"], key["col"]))

                # make new diffuse node
                diffuseBSDF = m.nodes['Diffuse BSDF']

                # if key color is set convert hex to rgb and set diffuse color
                # to that value, otherwise set it to rgba(0.8, 0.8, 0.8,
                # 1)/#cccccc
                if "c" in key:
                    c = key["c"]
                    rgb = hex2rgb(key["c"])
                    diffuseBSDF.inputs["Color"].default_value = [
                        rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]
                else:
                    diffuseBSDF.inputs["Color"].default_value = [
                        0.8, 0.8, 0.8, 1]

                # add material output node
                materialOutput = m.nodes['Material Output']
                # add glossy node
                glossyBSDF = m.makeNode('ShaderNodeBsdfGlossy', 'Glossy BSDF')
                # set glossy node color to white and roughness to 0.3
                glossyBSDF.inputs["Color"].default_value = [1, 1, 1, 1]
                glossyBSDF.inputs["Roughness"].default_value = 0.3
                # add mix node
                mixShader = m.makeNode('ShaderNodeMixShader', 'Mix Shader')
                # set mix node factor to 0.8
                mixShader.inputs['Fac'].default_value = 0.8
                # connect glossy and diffuse nodes to the mix node, and connect
                # that to the material output
                m.link(glossyBSDF, 'BSDF', mixShader, 1)
                m.link(diffuseBSDF, 'BSDF', mixShader, 2)
                m.link(mixShader, 'Shader', materialOutput, 'Surface')

                new_obj_enter_mm = None

                TL = key["p"] + 'TL'
                TM = key["p"] + 'TM'
                TR = key["p"] + 'TR'

                ML = key["p"] + 'ML'
                MM = key["p"] + 'MM'
                MR = key["p"] + 'MR'

                BL = key["p"] + 'BL'
                BM = key["p"] + 'BM'
                BR = key["p"] + 'BR'

                # if key is big ass enter or iso enter
                if "x2" in key or "y2" in key or "w2" in key or "h2" in key:
                    # set default values if they aren't set
                    if "x2" not in key:
                        key["x2"] = 0
                    if "y2" not in key:
                        key["y2"] = 0
                    if "w2" not in key:
                        key["w2"] = 1
                    if "h2" not in key:
                        key["h2"] = 1

                    # set the outcropping x and y
                    key["x2"] = key["x"] + key["x2"]
                    key["y2"] = key["y"] + key["y2"]

                    profile_norow = key["p"].replace("1","").replace("2","").replace("3","").replace("4","")
                    if profile_norow in ["DSA", "SA"]:
                        TL = profile_norow + 'TLF'
                        TM = profile_norow + 'TMF'
                        TR = profile_norow + 'TRF'

                        ML = profile_norow + 'MLF'
                        MM = profile_norow + 'MMF'
                        MR = profile_norow + 'MRF'

                        BL = profile_norow + 'BLF'
                        BM = profile_norow + 'BMF'
                        BR = profile_norow + 'BRF'

                    if profile_norow == "DCS" and key["x2"] + key["w2"] > key["x"] + key["w"]:
                        TR = profile_norow + 'TRF'
                        MR = profile_norow + 'MRF'
                        BR = profile_norow + 'BRF'

                    if profile_norow == "DCS" and key["x2"] < key["x"]:
                        TL = profile_norow + 'TLF'
                        ML = profile_norow + 'MLF'
                        BL = profile_norow + 'BLF'

                    # check if key is "stepped"
                    if "l" in key and key["l"] is True:
                        ETL = profile_norow + 'TLS'
                        ETM = profile_norow + 'TMS'
                        ETR = profile_norow + 'TRS'

                        EML = profile_norow + 'MLS'
                        EMM = profile_norow + 'MMS'
                        EMR = profile_norow + 'MRS'

                        EBL = profile_norow + 'BLS'
                        EBM = profile_norow + 'BMS'
                        EBR = profile_norow + 'BRS'
                    else:
                        ETL = profile_norow + 'TLF'
                        ETM = profile_norow + 'TMF'
                        ETR = profile_norow + 'TRF'

                        EML = profile_norow + 'MLF'
                        EMM = profile_norow + 'MMF'
                        EMR = profile_norow + 'MRF'

                        EBL = profile_norow + 'BLF'
                        EBM = profile_norow + 'BMF'
                        EBR = profile_norow + 'BRF'

                    # add all the outcropping pieces
                    new_obj_enter_tl = bpy.data.objects[ETL].copy()
                    new_obj_enter_tl.data = bpy.data.objects[ETL].data.copy()
                    new_obj_enter_tl.animation_data_clear()
                    new_obj_enter_tl.location[0] = key["x2"] * -1 - 0.5
                    new_obj_enter_tl.location[1] = key["y2"] + 0.5

                    new_obj_enter_tm = bpy.data.objects[ETM].copy()
                    new_obj_enter_tm.data = bpy.data.objects[ETM].data.copy()
                    new_obj_enter_tm.animation_data_clear()
                    new_obj_enter_tm.location[0] = (
                        key["x2"] + key["w2"] / 2) * -1
                    new_obj_enter_tm.location[1] = key["y2"] + 0.5
                    new_obj_enter_tm.dimensions[0] = key[
                        "w2"] - 1 + 0.2 if key["w2"] - 1 + 0.2 > 0 else 0.2

                    new_obj_enter_tr = bpy.data.objects[ETR].copy()
                    new_obj_enter_tr.data = bpy.data.objects[ETR].data.copy()
                    new_obj_enter_tr.animation_data_clear()
                    new_obj_enter_tr.location[0] = key[
                        "x2"] * -1 - 0.5 - (key["w2"] - 1)
                    new_obj_enter_tr.location[1] = key["y2"] + 0.5

                    new_obj_enter_ml = bpy.data.objects[EML].copy()
                    new_obj_enter_ml.data = bpy.data.objects[EML].data.copy()
                    new_obj_enter_ml.animation_data_clear()
                    new_obj_enter_ml.location[0] = key["x2"] * -1 - 0.5
                    new_obj_enter_ml.location[1] = key[
                        "y2"] + 0.5 + (key["h2"] - 1) / 2
                    new_obj_enter_ml.dimensions[1] = key["h2"] - 1 + 0.2

                    new_obj_enter_mm = bpy.data.objects[EMM].copy()
                    new_obj_enter_mm.data = bpy.data.objects[EMM].data.copy()
                    new_obj_enter_mm.animation_data_clear()
                    new_obj_enter_mm.location[0] = (
                        key["x2"] + key["w2"] / 2) * -1
                    new_obj_enter_mm.location[1] = key[
                        "y2"] + 0.5 + (key["h2"] - 1) / 2
                    new_obj_enter_mm.dimensions = (key["w2"] - 1 + 0.2 if key["w2"] - 1 + 0.2 > 0 else 0.2, key[
                                                   "h2"] - 1 + 0.2, new_obj_enter_mm.dimensions[2])

                    new_obj_enter_mr = bpy.data.objects[EMR].copy()
                    new_obj_enter_mr.data = bpy.data.objects[EMR].data.copy()
                    new_obj_enter_mr.animation_data_clear()
                    new_obj_enter_mr.location[0] = (
                        key["x2"]) * -1 - 0.5 - (key["w2"] - 1)
                    new_obj_enter_mr.location[1] = key[
                        "y2"] + 0.5 + (key["h2"] - 1) / 2
                    new_obj_enter_mr.dimensions[1] = key["h2"] - 1 + 0.2

                    new_obj_enter_bl = bpy.data.objects[EBL].copy()
                    new_obj_enter_bl.data = bpy.data.objects[EBL].data.copy()
                    new_obj_enter_bl.animation_data_clear()
                    new_obj_enter_bl.location[0] = (key["x2"]) * -1 - 0.5
                    new_obj_enter_bl.location[1] = key[
                        "y2"] + 0.5 + key["h2"] - 1

                    new_obj_enter_bm = bpy.data.objects[EBM].copy()
                    new_obj_enter_bm.data = bpy.data.objects[EBM].data.copy()
                    new_obj_enter_bm.animation_data_clear()
                    new_obj_enter_bm.location[0] = (
                        key["x2"]) * -1 - 0.5 - (key["w2"] - 1) / 2
                    new_obj_enter_bm.location[1] = key[
                        "y2"] + 0.5 + key["h2"] - 1
                    new_obj_enter_bm.dimensions[0] = key[
                        "w2"] - 1 + 0.2 if key["w2"] - 1 + 0.2 > 0 else 0.2

                    new_obj_enter_br = bpy.data.objects[EBR].copy()
                    new_obj_enter_br.data = bpy.data.objects[EBR].data.copy()
                    new_obj_enter_br.animation_data_clear()
                    new_obj_enter_br.location[0] = (
                        key["x2"]) * -1 - 0.5 - (key["w2"] - 1)
                    new_obj_enter_br.location[1] = key[
                        "y2"] + 0.5 + key["h2"] - 1

                    # set outcropping material to the material that was just
                    # created
                    new_obj_enter_tl.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_tm.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_tr.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_ml.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_mm.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_mr.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_bl.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_bm.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    new_obj_enter_br.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]

                    # add outcropping to scene
                    scn.objects.link(new_obj_enter_tl)
                    scn.objects.link(new_obj_enter_tm)
                    scn.objects.link(new_obj_enter_tr)
                    scn.objects.link(new_obj_enter_ml)
                    scn.objects.link(new_obj_enter_mm)
                    scn.objects.link(new_obj_enter_mr)
                    scn.objects.link(new_obj_enter_bl)
                    scn.objects.link(new_obj_enter_bm)
                    scn.objects.link(new_obj_enter_br)

                    # deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    # combine all the pieces
                    new_obj_enter_tl.select = True
                    new_obj_enter_tm.select = True
                    new_obj_enter_tr.select = True
                    new_obj_enter_ml.select = True
                    new_obj_enter_mm.select = True
                    new_obj_enter_mr.select = True
                    new_obj_enter_bl.select = True
                    new_obj_enter_bm.select = True
                    new_obj_enter_br.select = True
                    scn.objects.active = new_obj_enter_mm
                    bpy.ops.object.join()

                else:
                    # set default values if they aren't set
                    if "x2" not in key:
                        key["x2"] = 0
                    if "y2" not in key:
                        key["y2"] = 0
                    if "w2" not in key:
                        key["w2"] = 1
                    if "h2" not in key:
                        key["h2"] = 1

                # check if we need the middle strip;
                # force middle strip for DCS and DSA
                if key["p"] in ["DCS", "DSA"] or key["h"] - 1 - 0.1 > 0:
                    middleh_needed = True
                else:
                    middleh_needed = False
                if key["p"] in ["DCS", "DSA"] or key["w"] - 1 - 0.1 > 0:
                    middlew_needed = True
                else:
                    middlew_needed = False

                # define overlap
                overlap = 0.2 if key["p"] in [ "DCS", "DSA" ] else 0.0

                # add all the key pieces
                new_obj_tl = bpy.data.objects[TL].copy()
                new_obj_tl.data = bpy.data.objects[TL].data.copy()
                new_obj_tl.animation_data_clear()
                new_obj_tl.location[0] = key["x"] * -1 - 0.5
                new_obj_tl.location[1] = key["y"] + 0.5

                if middlew_needed:
                    new_obj_tm = bpy.data.objects[TM].copy()
                    new_obj_tm.data = bpy.data.objects[TM].data.copy()
                    new_obj_tm.animation_data_clear()
                    new_obj_tm.location[0] = (key["x"] + key["w"] / 2) * -1
                    new_obj_tm.location[1] = key["y"] + 0.5
                    new_obj_tm.dimensions[0] = key["w"] - 1 + \
                                               overlap if key["w"] - 1 + overlap > 0 else overlap

                new_obj_tr = bpy.data.objects[TR].copy()
                new_obj_tr.data = bpy.data.objects[TR].data.copy()
                new_obj_tr.animation_data_clear()
                new_obj_tr.location[0] = key["x"] * -1 - 0.5 - (key["w"] - 1)
                new_obj_tr.location[1] = key["y"] + 0.5

                if middleh_needed:
                    new_obj_ml = bpy.data.objects[ML].copy()
                    new_obj_ml.data = bpy.data.objects[ML].data.copy()
                    new_obj_ml.animation_data_clear()
                    new_obj_ml.location[0] = key["x"] * -1 - 0.5
                    new_obj_ml.location[1] = key["y"] + 0.5 + (key["h"] - 1) / 2
                    new_obj_ml.dimensions[1] = key["h"] - 1 + overlap

                    if middlew_needed:
                        new_obj_mm = bpy.data.objects[MM].copy()
                        new_obj_mm.data = bpy.data.objects[MM].data.copy()
                        new_obj_mm.animation_data_clear()
                        new_obj_mm.location[0] = (key["x"] + key["w"] / 2) * -1
                        new_obj_mm.location[1] = key["y"] + 0.5 + (key["h"] - 1) / 2
                        new_obj_mm.dimensions = (key["w"] - 1 + overlap if key["w"] - 1 + overlap > 0 else overlap, key["h"] - 1 + overlap, new_obj_mm.dimensions[2])

                    new_obj_mr = bpy.data.objects[MR].copy()
                    new_obj_mr.data = bpy.data.objects[MR].data.copy()
                    new_obj_mr.animation_data_clear()
                    new_obj_mr.location[0] = (key["x"]) * -1 - 0.5 - (key["w"] - 1)
                    new_obj_mr.location[1] = key["y"] + 0.5 + (key["h"] - 1) / 2
                    new_obj_mr.dimensions[1] = key["h"] - 1 + overlap

                new_obj_bl = bpy.data.objects[BL].copy()
                new_obj_bl.data = bpy.data.objects[BL].data.copy()
                new_obj_bl.animation_data_clear()
                new_obj_bl.location[0] = (key["x"]) * -1 - 0.5
                new_obj_bl.location[1] = key["y"] + 0.5 + key["h"] - 1

                if middlew_needed:
                    new_obj_bm = bpy.data.objects[BM].copy()
                    new_obj_bm.data = bpy.data.objects[BM].data.copy()
                    new_obj_bm.animation_data_clear()
                    new_obj_bm.location[0] = (
                        key["x"]) * -1 - 0.5 - (key["w"] - 1) / 2
                    new_obj_bm.location[1] = key["y"] + 0.5 + key["h"] - 1
                    new_obj_bm.dimensions[0] = key["w"] - 1 + \
                                               overlap if key["w"] - 1 + overlap > 0 else overlap

                new_obj_br = bpy.data.objects[BR].copy()
                new_obj_br.data = bpy.data.objects[BR].data.copy()
                new_obj_br.animation_data_clear()
                new_obj_br.location[0] = (key["x"]) * -1 - 0.5 - (key["w"] - 1)
                new_obj_br.location[1] = key["y"] + 0.5 + key["h"] - 1

                # set key material to the material that was just created
                new_obj_tl.active_material = bpy.data.materials[
                    "%s-%s" % (key["row"], key["col"])]
                if middlew_needed:
                    new_obj_tm.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                new_obj_tr.active_material = bpy.data.materials[
                    "%s-%s" % (key["row"], key["col"])]

                if middleh_needed:
                    new_obj_ml.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                    if middlew_needed:
                        new_obj_mm.active_material = bpy.data.materials[
                            "%s-%s" % (key["row"], key["col"])]
                    new_obj_mr.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]

                new_obj_bl.active_material = bpy.data.materials[
                    "%s-%s" % (key["row"], key["col"])]
                if middlew_needed:
                    new_obj_bm.active_material = bpy.data.materials[
                        "%s-%s" % (key["row"], key["col"])]
                new_obj_br.active_material = bpy.data.materials[
                    "%s-%s" % (key["row"], key["col"])]

                # add key to scene
                scn.objects.link(new_obj_tl)
                if middlew_needed:
                    scn.objects.link(new_obj_tm)
                scn.objects.link(new_obj_tr)

                if middleh_needed:
                    scn.objects.link(new_obj_ml)
                    if middlew_needed:
                        scn.objects.link(new_obj_mm)
                    scn.objects.link(new_obj_mr)

                scn.objects.link(new_obj_bl)
                if middlew_needed:
                    scn.objects.link(new_obj_bm)
                scn.objects.link(new_obj_br)

                # deselect everything
                for obj in scn.objects:
                    obj.select = False

                # combine all the pieces
                new_obj_tl.select = True
                if middlew_needed:
                    new_obj_tm.select = True
                new_obj_tr.select = True

                if middleh_needed:
                    new_obj_ml.select = True
                    if middlew_needed:
                        new_obj_mm.select = True
                    new_obj_mr.select = True

                new_obj_bl.select = True
                if middlew_needed:
                    new_obj_bm.select = True
                new_obj_br.select = True
                # if outcropping exists add it to the key
                if new_obj_enter_mm is not None:
                    new_obj_enter_mm.select = True
                scn.objects.active = new_obj_tl
                bpy.ops.object.join()

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT')

                # name the key
                if key["v"]["raw"] == "" and key["w"] < 4.5:
                    new_obj_tl.name = "Blank"
                elif key["v"]["raw"] == "" and key["w"] >= 4.5:
                    new_obj_tl.name = "Space"
                else:
                    new_obj_tl.name = HTMLParser().unescape(
                        key["v"]["raw"].replace("\n", " "))

                # add key switch
                new_switch = bpy.data.objects["switch"].copy()
                new_switch.data = bpy.data.objects["switch"].data.copy()
                new_switch.animation_data_clear()
                new_switch.location[0] = (key["x"]) * -1 - (key["w"]) / 2
                new_switch.location[1] = key["y"] + key["h"] / 2
                scn.objects.link(new_switch)
                new_switch.name = "switch: %s-%s" % (key["row"], key["col"])

                if "led" in keyboard:
                    # add led
                    new_led = bpy.data.objects["led"].copy()
                    new_led.data = bpy.data.objects["led"].data.copy()
                    new_led.animation_data_clear()
                    new_led.location[0] = (key["x"]) * -1 - (key["w"]) / 2
                    new_led.location[1] = key["y"] + key["h"] / 2
                    scn.objects.link(new_led)
                    new_led.name = "led: %s-%s" % (key["row"], key["col"])

                for pos, label in enumerate(key["v"]["labels"]):
                    if label != "":

                        # new material for legend
                        m = Material()
                        m.set_cycles()
                        m.make_material("legend: %s-%s" %
                                        (key["row"], key["col"]))

                        if "t" in key and key["t"][pos] != None and "led" in keyboard and hex2rgb(key["t"][pos]) == keyboard["led"]:
                            # make new emission node
                            emission = m.makeNode(
                                'ShaderNodeEmission', 'Emission')
                            # set legend color
                            emission.inputs["Color"].default_value = [
                                keyboard["led"][0] / 255, keyboard["led"][1] / 255, keyboard["led"][2] / 255, 1]
                            emission.inputs[
                                "Strength"].default_value = keyboard["led"][3] * 5

                            # add material output node
                            materialOutput = m.nodes['Material Output']
                            # attach emission to material output
                            m.link(emission, 'Emission',
                                   materialOutput, 'Surface')
                        else:
                            # make new diffuse node
                            diffuseBSDF = m.nodes['Diffuse BSDF']
                            # if legend color is set convert hex to rgb and set diffuse color
                            # to that value, otherwise set it to rgba(0.8, 0.8, 0.8,
                            # 1)/#cccccc
                            if "t" in key and key["t"][pos] != None:
                                if len(key["t"]) > 1:
                                    c = key["t"][pos]
                                    rgb = hex2rgb(key["t"][pos])
                                    diffuseBSDF.inputs["Color"].default_value = [
                                        rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]
                                else:
                                    c = key["t"][0]
                                    rgb = hex2rgb(key["t"][pos])
                                    diffuseBSDF.inputs["Color"].default_value = [
                                        rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]
                            else:
                                diffuseBSDF.inputs["Color"].default_value = [
                                    0, 0, 0, 1]

                            # add material output node
                            materialOutput = m.nodes['Material Output']
                            # add glossy node
                            glossyBSDF = m.makeNode(
                                'ShaderNodeBsdfGlossy', 'Glossy BSDF')
                            # set glossy node color to white and roughness to
                            # 0.3
                            glossyBSDF.inputs[
                                "Color"].default_value = [1, 1, 1, 1]
                            glossyBSDF.inputs[
                                "Roughness"].default_value = 0.3
                            # add mix node
                            mixShader = m.makeNode(
                                'ShaderNodeMixShader', 'Mix Shader')
                            # set mix node factor to 0.8
                            mixShader.inputs['Fac'].default_value = 0.8
                            # connect glossy and diffuse nodes to the mix node, and connect
                            # that to the material output
                            m.link(glossyBSDF, 'BSDF', mixShader, 1)
                            m.link(diffuseBSDF, 'BSDF', mixShader, 2)
                            m.link(mixShader, 'Shader',
                                   materialOutput, 'Surface')

                        alignText = [
                            ["LEFT", "TOP"],
                            ["CENTER", "TOP"],
                            ["RIGHT", "TOP"],
                            ["LEFT", "CENTER"],
                            ["CENTER", "CENTER"],
                            ["RIGHT", "CENTER"],
                            ["LEFT", "BOTTOM"],
                            ["CENTER", "BOTTOM"],
                            ["RIGHT", "BOTTOM"]
                        ]

                        # adjust legends based on keycap type
                        def alignLegendsProfile(p):
                            return {
                                "DCS": [0.25, 0.15, 0.25, 0.325],
                                "DSA": [0.2, 0.25, 0.2, 0.25],
                                "SA3D": [0.2, 0.30, 0.2, 0.30],
                                "SA1": [0.2, 0.30, 0.2, 0.30],
                                "SA2": [0.2, 0.30, 0.2, 0.30],
                                "SA3": [0.2, 0.30, 0.2, 0.30],
                                "SA4": [0.2, 0.30, 0.2, 0.30]
                            }.get(p, [0.25, 0.15, 0.25, 0.325])

                        # the SA caps are thicker and we need to lift the label more
                        cap_thickness = 0.001 if key["p"] in ["DCS", "DSA"] else 0.004
                        try:
                            # add text
                            new_label = bpy.data.curves.new(
                                type="FONT", name="keylabel")
                            new_label = bpy.data.objects.new(
                                "label", new_label)
                            new_label.data.body = key[
                                "v"]["labels"][pos].upper()

                            new_label.data.font = fonts[pos]
                            new_label.data.size = key["f"][pos] / 15
                            new_label.data.text_boxes[0].width = new_obj_tl.dimensions[
                                0] - (alignLegendsProfile(key["p"])[0] + alignLegendsProfile(key["p"])[2])
                            new_label.data.text_boxes[0].height = new_obj_tl.dimensions[
                                1] - (alignLegendsProfile(key["p"])[1] + alignLegendsProfile(key["p"])[3])
                            new_label.data.text_boxes[
                                0].y = -1 * (key["f"][pos] / 15)
                            new_label.data.align_x = alignText[pos][0]
                            new_label.data.align_y = alignText[pos][1]

                            new_label.location = [-1 * key["x"] - alignLegendsProfile(
                                key["p"])[0], key["y"] + alignLegendsProfile(key["p"])[1], 1]
                            new_label.rotation_euler[2] = pi

                            scn.objects.link(new_label)
                            scn.update()

                            # deselect everything
                            for obj in scn.objects:
                                obj.select = False

                            new_label.select = True
                            scn.objects.active = new_label

                            bpy.ops.object.modifier_add(type='SHRINKWRAP')
                            new_label.modifiers["Shrinkwrap"].offset = 0.0005
                            new_label.modifiers[
                                "Shrinkwrap"].target = new_obj_tl
                            new_label.to_mesh(scn, True, "PREVIEW")
                            new_label.active_material = bpy.data.materials[
                                "legend: %s-%s" % (key["row"], key["col"])]
                            bpy.ops.object.convert(target='MESH')
                            for edge in bpy.context.object.data.edges:
                                edge.crease = 1

                            new_label.location[2] += cap_thickness
                        except AttributeError:
                            # add text
                            new_label = bpy.data.curves.new(
                                type="FONT", name="keylabel")
                            new_label = bpy.data.objects.new(
                                "label", new_label)
                            new_label.data.body = key[
                                "v"]["labels"][pos].upper()

                            new_label.data.font = noto
                            new_label.data.size = key["f"][pos] / 15
                            new_label.data.text_boxes[0].width = new_obj_tl.dimensions[
                                0] - (alignLegendsProfile(key["p"])[0] + alignLegendsProfile(key["p"])[2])
                            new_label.data.text_boxes[0].height = new_obj_tl.dimensions[
                                1] - (alignLegendsProfile(key["p"])[1] + alignLegendsProfile(key["p"])[3])
                            new_label.data.text_boxes[
                                0].y = -1 * (key["f"][pos] / 15)
                            new_label.data.align_x = alignText[pos][0]
                            new_label.data.align_y = alignText[pos][1]

                            new_label.location = [-1 * key["x"] - alignLegendsProfile(
                                key["p"])[0], key["y"] + alignLegendsProfile(key["p"])[1], 1]
                            new_label.rotation_euler[2] = pi

                            scn.objects.link(new_label)
                            scn.update()

                            # deselect everything
                            for obj in scn.objects:
                                obj.select = False

                            new_label.select = True
                            scn.objects.active = new_label

                            bpy.ops.object.modifier_add(type='SHRINKWRAP')
                            new_label.modifiers["Shrinkwrap"].offset = 0.0005
                            new_label.modifiers[
                                "Shrinkwrap"].target = new_obj_tl
                            new_label.to_mesh(scn, True, "PREVIEW")
                            new_label.active_material = bpy.data.materials[
                                "legend: %s-%s" % (key["row"], key["col"])]
                            bpy.ops.object.convert(target='MESH')
                            for edge in bpy.context.object.data.edges:
                                edge.crease = 1

                            new_label.location[2] += cap_thickness

                        # deselect everything
                        for obj in scn.objects:
                            obj.select = False

                        new_label.select = True
                        new_obj_tl.select = True
                        scn.objects.active = new_obj_tl
                        bpy.ops.object.join()

                # rotate key
                if "r" in key:
                    if "rx" not in key:
                        key["rx"] = 0
                    if "ry" not in key:
                        key["ry"] = 0

                    empty = bpy.data.objects.new("rotate", None)
                    empty.location = (key["rx"] * -1, key["ry"], 0.3)
                    scn.objects.link(empty)

                    # deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    empty.select = True
                    new_obj_tl.select = True
                    new_switch.select = True

                    scn.objects.active = empty
                    bpy.ops.object.parent_set(type="OBJECT")

                    empty.rotation_euler[2] = pi * (key["r"] * -1) / 180

                    # deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    new_obj_tl.select = True
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                    new_switch.select = True
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

                    # deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    empty.select = True
                    bpy.ops.object.delete(use_global=False)

                # set the keyboard width and height if it was smaller than the
                # current width
                if key["x"] + key["w"] + 0.05 > width:
                    width = key["x"] + key["w"] + 0.05
                if key["y"] + key["h"] + 0.05 > height:
                    height = key["y"] + key["h"] + 0.05

            bpy.context.window_manager.progress_update(currentKey)
            currentKey += 1

    m = Material()
    m.set_cycles()
    m.make_material("side")

    diffuseBSDF = m.nodes['Diffuse BSDF']

    # set case color if it is defined, otherwise set it to white
    if "backcolor" in keyboard:
        c = keyboard["backcolor"]
        rgb = hex2rgb(c)
        diffuseBSDF.inputs["Color"].default_value = [
            rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]
    else:
        diffuseBSDF.inputs["Color"].default_value = [1, 1, 1, 1]

    # make the case material
    materialOutput = m.nodes['Material Output']
    glossyBSDF = m.makeNode('ShaderNodeBsdfGlossy', 'Glossy BSDF')
    glossyBSDF.inputs["Color"].default_value = [1, 1, 1, 1]
    glossyBSDF.inputs["Roughness"].default_value = 0.6
    mixShader = m.makeNode('ShaderNodeMixShader', 'Mix Shader')
    mixShader.inputs['Fac'].default_value = 0.8
    m.link(glossyBSDF, 'BSDF', mixShader, 1)
    m.link(diffuseBSDF, 'BSDF', mixShader, 2)
    m.link(mixShader, 'Shader', materialOutput, 'Surface')

    mp = Material()
    mp.set_cycles()
    mp.make_material("plate")

    # make the case material
    materialOutput = mp.nodes['Material Output']
    mixShader = mp.makeNode('ShaderNodeMixShader', 'Mix Shader')
    mixShader.inputs['Fac'].default_value = 0.8
    mp.link(glossyBSDF, 'BSDF', mixShader, 1)
    mp.link(diffuseBSDF, 'BSDF', mixShader, 2)
    mp.link(mixShader, 'Shader', materialOutput, 'Surface')

    # create all the sides and the bottom of the case
    side = bpy.data.objects['side']
    side1 = side.copy()
    side1.data = side.data.copy()
    side1.animation_data_clear()
    side1.active_material = bpy.data.materials["side"]
    side2 = side.copy()
    side2.data = side.data.copy()
    side2.animation_data_clear()
    side2.active_material = bpy.data.materials["side"]
    side3 = side.copy()
    side3.data = side.data.copy()
    side3.animation_data_clear()
    side3.active_material = bpy.data.materials["side"]
    side4 = side.copy()
    side4.data = side.data.copy()
    side4.animation_data_clear()
    side4.active_material = bpy.data.materials["side"]
    side5 = side.copy()
    side5.data = side.data.copy()
    side5.animation_data_clear()
    side5.active_material = bpy.data.materials["side"]

    # set case pieces size and location and add them to the scene
    side1.location = (0.1, height / 2, 0)
    side1.dimensions = (0.2, (height + 0.4), 1)
    scn.objects.link(side1)

    side2.location = (width / -2, -0.1, 0)
    side2.dimensions = (width, 0.2, 1)
    scn.objects.link(side2)

    side3.location = ((width + 0.1) * -1, height / 2, 0)
    side3.dimensions = (0.2, (height + 0.4), 1)
    scn.objects.link(side3)

    side4.location = (width / -2, (height + 0.1), 0)
    side4.dimensions = (width, 0.2, 1)
    scn.objects.link(side4)

    side5.location = (width / -2, height / 2, -0.25)
    side5.dimensions = (width, height, 0.5)
    scn.objects.link(side5)

    # deselect everything
    for obj in scn.objects:
        obj.select = False

    # select all case parts and join them together
    side1.select = True
    side2.select = True
    side3.select = True
    side4.select = True
    side5.select = True
    scn.objects.active = side5
    bpy.ops.object.join()
    # name the case
    side5.name = "Case"
    # deselect everything
    for obj in scn.objects:
        obj.select = False

    side5.select = True
    scn.objects.active = side5
    # bevel the corners
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)

    bpy.ops.object.mode_set(mode='OBJECT')

    side5.data.edges[24].select = True
    side5.data.edges[26].select = True
    side5.data.edges[53].select = True
    side5.data.edges[56].select = True

    bpy.ops.object.editmode_toggle()

    bpy.ops.mesh.bevel(vertex_only=False, offset=0.033,
                       offset_type='OFFSET', segments=5)
    bpy.ops.object.mode_set(mode='OBJECT')

    if "switchType" in keyboard:
        if keyboard["switchType"] == "MX1A-11xx" or keyboard["switchType"] == "KS-3-Black":
            stemColor = [0, 0, 0, 1]
        elif keyboard["switchType"] == "MX1A-A1xx":
            stemColor = [1, 1, 1, 1]
        elif keyboard["switchType"] == "MX1A-C1xx" or keyboard["switchType"] == "KS-3-White":
            stemColor = [1, 1, 1, 0.8]
        elif keyboard["switchType"] == "MX1A-E1xx":
            stemColor = [0, 0.7, 1, 1]
        elif keyboard["switchType"] == "MX1A-F1xx" or keyboard["switchType"] == "KS-3-Green":
            stemColor = [0, 0.6, 0.25, 1]
        elif keyboard["switchType"] == "MX1A-G1xx" or keyboard["switchType"] == "KS-3-Tea":
            stemColor = [0.6, 0.3, 0, 1]
        elif keyboard["switchType"] == "MX1A-L1xx" or keyboard["switchType"] == "KS-3-Red":
            stemColor = [1, 0, 0, 1]
        else:
            stemColor = [0, 0.7, 1, 1]
    else:
        stemColor = [0, 0.7, 1, 1]

    bpy.data.materials["Stem"].node_tree.nodes[
        "Diffuse BSDF"].inputs["Color"].default_value = stemColor

    if "led" in keyboard:
        bpy.data.materials["led"].node_tree.nodes["Emission"].inputs["Color"].default_value = [
            keyboard["led"][0] / 255, keyboard["led"][1] / 255, keyboard["led"][2] / 255, 1]
        bpy.data.materials["led"].node_tree.nodes["Emission"].inputs[
            "Strength"].default_value = keyboard["led"][3] * 5

    # deselect everything
    for obj in scn.objects:
        obj.select = False

    # remove all the template objects
    for object in defaultObjects:
        bpy.data.objects[object].select = True
    bpy.ops.object.delete()

    bpy.context.window_manager.progress_end()
