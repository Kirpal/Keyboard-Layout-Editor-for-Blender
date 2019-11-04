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
from . import parse_json
from . import add_label
from . import helpers
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

gotham = bpy.data.fonts.load(os.path.join(os.path.dirname(
    __file__), "gotham.ttf"))
noto = bpy.data.fonts.load(os.path.join(os.path.dirname(
    __file__), "noto.ttf"))

fonts = [None for i in range(0, 12)]

googleFonts = json.load(open(os.path.join(os.path.dirname(
    __file__), "fonts.json")))

def hex2rgb(hex):
    """Convert HEX color to RGB"""
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

class Material:
    """Make and modify materials"""

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


def read(filepath):
    bpy.context.window.cursor_set("WAIT")
    # parse raw data into dict
    keyboard = parse_json.load(filepath)

    # template objects that have to be appended in and then deleted at the end

    defaultObjects = ["DCSTL", "DCSTM", "DCSTR", "DCSML", "DCSMM", "DCSMR", "DCSBL", "DCSBM", "DCSBR", "DCSTLF", "DCSTMF", "DCSTRF", "DCSMLF", "DCSMMF", "DCSMRF", "DCSBLF", "DCSBMF", "DCSBRF", "DCSTLS", "DCSTMS", "DCSTRS", "DCSMLS", "DCSMMS", "DCSMRS", "DCSBLS", "DCSBMS", "DCSBRS",
                      "DSATL", "DSATM", "DSATR", "DSAML", "DSAMM", "DSAMR", "DSABL", "DSABM", "DSABR", "DSATLF", "DSATMF", "DSATRF", "DSAMLF", "DSAMMF", "DSAMRF", "DSABLF", "DSABMF", "DSABRF", "DSATLS", "DSATMS", "DSATRS", "DSAMLS", "DSAMMS", "DSAMRS", "DSABLS", "DSABMS", "DSABRS",
                      "SA1TL", "SA1TM", "SA1TR", "SA1ML", "SA1MM", "SA1MR", "SA1BL", "SA1BM", "SA1BR",  # SA R1
                      "SA2TL", "SA2TM", "SA2TR", "SA2ML", "SA2MM", "SA2MR", "SA2BL", "SA2BM", "SA2BR",  # SA R2
                      "SA3TL", "SA3TM", "SA3TR", "SA3ML", "SA3MM", "SA3MR", "SA3BL", "SA3BM", "SA3BR",  # SA R3
                      "SA3DTL", "SA3DTM", "SA3DTR", "SA3DML", "SA3DMM", "SA3DMR", "SA3DBL", "SA3DBM", "SA3DBR",  # deep dish
                      "SA4TL", "SA4TM", "SA4TR", "SA4ML", "SA4MM", "SA4MR", "SA4BL", "SA4BM", "SA4BR",  # SA R4
                      "SASPACETL", "SASPACETM", "SASPACETR", "SASPACEML", "SASPACEMM", "SASPACEMR", "SASPACEBL", "SASPACEBM", "SASPACEBR",  # SA SPACE
                      "SATLF", "SATMF", "SATRF", "SAMLF", "SAMMF", "SAMRF", "SABLF", "SABMF", "SABRF", "SATLS", "SATMS", "SATRS", "SAMLS", "SAMMS", "SAMRS", "SABLS", "SABMS", "SABRS",
                      "case", "switch", "led"]
    # blender file with template objects
    templateBlend = os.path.join(os.path.dirname(
        __file__), "template.blend", "Object")

    # append all the template objects
    for key in defaultObjects:
        bpy.ops.wm.append(filepath=templateBlend + key,
                          directory=templateBlend, filename=key)

    # get the current scene and change display device so colors are accurate
    context = bpy.context
    scn = context.scene
    scn.display_settings.display_device = "None"

    if hasattr(bpy.data, "collections"):
        bpy.ops.collection.create(name="Keyboard")
    else:
        bpy.ops.group.create(name="Keyboard")

    keyboard_empty = bpy.data.objects.new("Keyboard_whole", None)
    keyboard_empty.location = (0, 0, 0)
    helpers.add_object(scn, keyboard_empty)

    # initialize font list with default font
    fonts = [gotham for i in range(0, 12)]
    # get fonts from css
    if "css" in keyboard:
        selectors = []
        props = []
        css = re.sub(
            r'(\@import [^;]+\;|\@font-face [^\}]+\}|\/\*.*\*\/)', "", keyboard["css"])
        css = re.findall(r'([^\{]*){([^\}]*)}', css)
        css = [[i.strip() for i in pair] for pair in css]

        for pair in css:
            props = pair[1].split(";")
            props = [i.strip() for i in props]
            props = filter(None, props)

            selectors = filter(None, pair[0].split(","))

            fontProperty = list(filter(lambda p: re.sub(r"\s+", "", p.split(":")[0]) == "font-family", props))
            if len(fontProperty) > 0:
                font = re.sub(r"(\'|\")", "", fontProperty[-1].split(":")[1]).strip()

                if font in googleFonts.keys():
                    tempDir = bpy.app.tempdir
                    urllib.request.urlretrieve(
                        googleFonts[font], os.path.join(tempDir, font + ".ttf"))
                    font = bpy.data.fonts.load(
                        os.path.join(tempDir, font + ".ttf"))

                else:
                    font = gotham

                for selector in selectors:
                    if selector == "*":
                        fonts = [font for i in range(0, 12)]
                    elif re.fullmatch(r".keylabel[0-9][1-2]?", selector) and int(selector.replace(".keylabel", "")) >= 0 and int(selector.replace(".keylabel", "")) <= 11:
                        fonts[int(selector.replace(
                            ".keylabel", ""))] = font

    bpy.context.window_manager.progress_begin(keyboard["keyCount"], 0)
    bpy.context.window.cursor_set("DEFAULT")
    currentKey = 0

    # iterate over rows in keyboard
    for row in keyboard["rows"]:
        # iterate over keys in row
        for key in row:
            if key["d"] is False:
                if key["c"] not in bpy.data.materials:
                    # new material for key
                    m = Material()
                    m.set_cycles()
                    m.make_material(key["c"])

                    # make new diffuse node
                    diffuseBSDF = m.makeNode(
                        'ShaderNodeBsdfDiffuse', 'Diffuse BSDF')

                    # convert key color to rgb and set material to that
                    rgb = hex2rgb(key["c"])
                    diffuseBSDF.inputs["Color"].default_value = [
                        rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]

                    # add material output node
                    materialOutput = m.nodes['Material Output']
                    # add glossy node
                    glossyBSDF = m.makeNode(
                        'ShaderNodeBsdfGlossy', 'Glossy BSDF')
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

                    profile_norow = key["p"].replace("1", "").replace(
                        "2", "").replace("3", "").replace("4", "")
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
                    new_obj_enter_tl.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_tm.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_tr.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_ml.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_mm.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_mr.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_bl.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_bm.active_material = bpy.data.materials[key["c"]]
                    new_obj_enter_br.active_material = bpy.data.materials[key["c"]]

                    # add outcropping to scene
                    helpers.add_object(scn, new_obj_enter_tl)
                    helpers.add_object(scn, new_obj_enter_tm)
                    helpers.add_object(scn, new_obj_enter_tr)
                    helpers.add_object(scn, new_obj_enter_ml)
                    helpers.add_object(scn, new_obj_enter_mm)
                    helpers.add_object(scn, new_obj_enter_mr)
                    helpers.add_object(scn, new_obj_enter_bl)
                    helpers.add_object(scn, new_obj_enter_bm)
                    helpers.add_object(scn, new_obj_enter_br)

                    helpers.unselect_all(scn)

                    # combine all the pieces
                    helpers.select_object(new_obj_enter_tl)
                    helpers.select_object(new_obj_enter_tm)
                    helpers.select_object(new_obj_enter_tr)
                    helpers.select_object(new_obj_enter_ml)
                    helpers.select_object(new_obj_enter_mm)
                    helpers.select_object(new_obj_enter_mr)
                    helpers.select_object(new_obj_enter_bl)
                    helpers.select_object(new_obj_enter_bm)
                    helpers.select_object(new_obj_enter_br)
                    helpers.set_active_object(context, new_obj_enter_mm)
                    bpy.ops.object.join()

                else:
                    # set default values if they aren't set
                    if "x2" not in key:
                        key["x2"] = key["x"]
                    if "y2" not in key:
                        key["y2"] = key["y"]
                    if "w2" not in key:
                        key["w2"] = key["w"]
                    if "h2" not in key:
                        key["h2"] = key["h"]

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
                overlap = 0.2 if key["p"] in ["DCS", "DSA"] else 0.0

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
                    new_obj_ml.location[1] = key["y"] + \
                        0.5 + (key["h"] - 1) / 2
                    new_obj_ml.dimensions[1] = key["h"] - 1 + overlap

                    if middlew_needed:
                        new_obj_mm = bpy.data.objects[MM].copy()
                        new_obj_mm.data = bpy.data.objects[MM].data.copy()
                        new_obj_mm.animation_data_clear()
                        new_obj_mm.location[0] = (key["x"] + key["w"] / 2) * -1
                        new_obj_mm.location[1] = key["y"] + \
                            0.5 + (key["h"] - 1) / 2
                        new_obj_mm.dimensions = (key["w"] - 1 + overlap if key["w"] - 1 + overlap >
                                                 0 else overlap, key["h"] - 1 + overlap, new_obj_mm.dimensions[2])

                    new_obj_mr = bpy.data.objects[MR].copy()
                    new_obj_mr.data = bpy.data.objects[MR].data.copy()
                    new_obj_mr.animation_data_clear()
                    new_obj_mr.location[0] = (
                        key["x"]) * -1 - 0.5 - (key["w"] - 1)
                    new_obj_mr.location[1] = key["y"] + \
                        0.5 + (key["h"] - 1) / 2
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
                new_obj_tl.active_material = bpy.data.materials[key["c"]]
                if middlew_needed:
                    new_obj_tm.active_material = bpy.data.materials[key["c"]]
                new_obj_tr.active_material = bpy.data.materials[key["c"]]

                if middleh_needed:
                    new_obj_ml.active_material = bpy.data.materials[key["c"]]
                    if middlew_needed:
                        new_obj_mm.active_material = bpy.data.materials[key["c"]]
                    new_obj_mr.active_material = bpy.data.materials[key["c"]]

                new_obj_bl.active_material = bpy.data.materials[key["c"]]
                if middlew_needed:
                    new_obj_bm.active_material = bpy.data.materials[key["c"]]
                new_obj_br.active_material = bpy.data.materials[key["c"]]

                # add key to scene
                helpers.add_object(scn, new_obj_tl)
                if middlew_needed:
                    helpers.add_object(scn, new_obj_tm)
                helpers.add_object(scn, new_obj_tr)

                if middleh_needed:
                    helpers.add_object(scn, new_obj_ml)
                    if middlew_needed:
                        helpers.add_object(scn, new_obj_mm)
                    helpers.add_object(scn, new_obj_mr)

                helpers.add_object(scn, new_obj_bl)
                if middlew_needed:
                    helpers.add_object(scn, new_obj_bm)
                helpers.add_object(scn, new_obj_br)

                helpers.unselect_all(scn)

                # combine all the pieces
                helpers.select_object(new_obj_tl)
                if middlew_needed:
                    helpers.select_object(new_obj_tm)
                helpers.select_object(new_obj_tr)

                if middleh_needed:
                    helpers.select_object(new_obj_ml)
                    if middlew_needed:
                        helpers.select_object(new_obj_mm)
                    helpers.select_object(new_obj_mr)

                helpers.select_object(new_obj_bl)
                if middlew_needed:
                    helpers.select_object(new_obj_bm)
                helpers.select_object(new_obj_br)
                # if outcropping exists add it to the key
                if new_obj_enter_mm is not None:
                    helpers.select_object(new_obj_enter_mm)
                helpers.set_active_object(context, new_obj_tl)
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.join()

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.mesh.faces_shade_smooth()
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
                helpers.add_object(scn, new_switch)
                new_switch.name = "switch: %s-%s" % (key["row"], key["col"])

                if "led" in keyboard:
                    # add led
                    new_led = bpy.data.objects["led"].copy()
                    new_led.data = bpy.data.objects["led"].data.copy()
                    new_led.animation_data_clear()
                    new_led.location[0] = (key["x"]) * -1 - (key["w"]) / 2
                    new_led.location[1] = key["y"] + key["h"] / 2
                    helpers.add_object(scn, new_led)
                    new_led.name = "led: %s-%s" % (key["row"], key["col"])

                for pos, label in enumerate(key["v"]["labels"]):
                    # make sure it's not a front legend
                    if pos < 9:
                        labelMaterial = key["t"][pos]
                        if label != "":
                            if "led" in keyboard and hex2rgb(labelMaterial) == keyboard["led"][:3]:
                                labelMaterial = "led: %s" % labelMaterial
                                if labelMaterial not in bpy.data.materials:
                                    # new material for legend
                                    m = Material()
                                    m.set_cycles()
                                    m.make_material(labelMaterial)
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
                            elif labelMaterial not in bpy.data.materials:
                                # new material for legend
                                m = Material()
                                m.set_cycles()
                                m.make_material(labelMaterial)
                                # make new diffuse node
                                diffuseBSDF = m.makeNode(
                                    'ShaderNodeBsdfDiffuse', 'Diffuse BSDF')
                                # convert hex to rgb
                                rgb = hex2rgb(labelMaterial)
                                diffuseBSDF.inputs["Color"].default_value = [
                                    rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]

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

                            try:
                                add_label.add(
                                    key["v"]["labels"][pos],
                                    fonts[pos],
                                    key["p"],
                                    pos,
                                    labelMaterial,
                                    key["f"][pos],
                                    key["x"],
                                    key["y"],
                                    key["w"],
                                    key["h"],
                                    new_obj_tl)
                            except AttributeError:
                                add_label.add(
                                    key["v"]["labels"][pos],
                                    noto,
                                    key["p"],
                                    pos,
                                    labelMaterial,
                                    key["f"][pos],
                                    key["x"],
                                    key["y"],
                                    key["w"],
                                    key["h"],
                                    new_obj_tl,
                                    0.0001)

                # rotate key
                if "r" in key:
                    if "rx" not in key:
                        key["rx"] = 0
                    if "ry" not in key:
                        key["ry"] = 0

                    empty = bpy.data.objects.new("rotate", None)
                    empty.location = (key["rx"] * -1, key["ry"], 0.3)
                    helpers.add_object(scn, empty)

                    helpers.unselect_all(scn)

                    helpers.select_object(empty)
                    helpers.select_object(new_obj_tl)
                    helpers.select_object(new_switch)

                    helpers.set_active_object(context, empty)
                    bpy.ops.object.parent_set(type="OBJECT")

                    empty.rotation_euler[2] = pi * (key["r"] * -1) / 180

                    helpers.unselect_all(scn)

                    helpers.select_object(new_obj_tl)
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                    helpers.select_object(new_switch)
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

                    helpers.unselect_all(scn)

                    helpers.select_object(empty)
                    bpy.ops.object.delete(use_global=False)

                helpers.select_object(new_obj_tl)
                helpers.select_object(new_switch)
                if "led" in keyboard:
                    helpers.select_object(new_led)
                helpers.set_active_object(context, keyboard_empty)
                bpy.ops.object.parent_set(type="OBJECT")

                helpers.unselect_all(scn)

            bpy.context.window_manager.progress_update(currentKey)
            currentKey += 1

    # get case height and width from generated keys
    helpers.set_active_object(context, keyboard_empty)
    bpy.ops.object.select_grouped(type="CHILDREN_RECURSIVE")
    bpy.ops.object.duplicate()
    helpers.set_active_object(context, bpy.context.selected_objects[0])
    bpy.ops.object.join()
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    if hasattr(context, "view_layer"):
        width = context.view_layer.objects.active.dimensions[0] + 0.5
        height = context.view_layer.objects.active.dimensions[1] + 0.5
        caseX = context.view_layer.objects.active.location[0]
        caseY = context.view_layer.objects.active.location[1]
    else:
        width = scn.objects.active.dimensions[0] + 0.5
        height = scn.objects.active.dimensions[1] + 0.5
        caseX = scn.objects.active.location[0]
        caseY = scn.objects.active.location[1]
    bpy.ops.object.delete(use_global=False)
    
    # create the case
    caseTemplate = bpy.data.objects['case']
    case = caseTemplate.copy()
    case.data = caseTemplate.data.copy()
    case.animation_data_clear()

    case.location = (caseX, caseY, -0.25)
    case.dimensions = (width, height, 0.5)

    helpers.add_object(scn, case)

    helpers.select_object(case)
    helpers.set_active_object(context, case)

    # set case color if it is defined, otherwise set it to white
    if "backcolor" in keyboard:
        c = keyboard["backcolor"]
        rgb = hex2rgb(c)
        bpy.data.materials["case"].node_tree.nodes["RGB"].outputs[0].default_value = [rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1]
    else:
        bpy.data.materials["case"].node_tree.nodes["RGB"].outputs[0].default_value = [1, 1, 1, 1]

    # name the case
    case.name = "Case"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    helpers.unselect_all(scn)

    helpers.select_object(case)
    helpers.set_active_object(context, keyboard_empty)
    bpy.ops.object.parent_set(type="OBJECT")

    # This assumes 1 blender unit = 10cm
    blender_scaling = .1905
    keyboard_empty.scale = (blender_scaling, blender_scaling, blender_scaling)
    keyboard_empty.rotation_euler[2] = pi
    keyboard_empty.location = (-blender_scaling*width*0.5,
                               blender_scaling*height*0.5, blender_scaling*0.5)

    helpers.unselect_all(scn)

    helpers.select_object(keyboard_empty)
    helpers.set_active_object(context, keyboard_empty)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    bpy.ops.object.delete(use_global=False)

    helpers.select_object(case)
    helpers.set_active_object(context, case)
    # bevel the corners
    bpy.ops.object.modifier_add(type="BEVEL")
    bpy.ops.object.modifier_apply(modifier="Bevel")

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

    helpers.unselect_all(scn)

    # remove all the template objects
    for object in defaultObjects:
        helpers.select_object(bpy.data.objects[object])
    bpy.ops.object.delete()

    bpy.context.window_manager.progress_end()
