"""
This script imports JSON File format files to Blender.

It uses the JSON file downloaded from keyboard-layout-editor.com

Usage:
Execute this script from the "File->Import" menu and choose a JSON file to
open.
"""

#import needed modules
import bpy
import json
import os

#convert HEX color to RGB
def hex2rgb(hex):
    hex = hex.lstrip("#");

    if len(hex) == 3:
      r = int(str(hex[0:1]) + str(hex[0:1]), 16);
      g = int(str(hex[1:2]) + str(hex[1:2]), 16);
      b = int(str(hex[2:3]) + str(hex[2:3]), 16);
    else:
      r = int(str(hex[0:2]), 16);
      g = int(str(hex[2:4]), 16);
      b = int(str(hex[4:6]), 16);

    rgb = [r, g, b];

    return rgb

#Make and modify materials
class Material:
    def set_cycles(self):
        scn = bpy.context.scene
        if not scn.render.engine == 'CYCLES':
            scn.render.engine = 'CYCLES'
    def make_material(self, name):
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

#parses KLE Raw JSON into dict
def getKey(filePath):
        #load JSON file
        layout = json.load(open(filePath, encoding="UTF-8", errors="replace"), strict=False)
        #make empty keyboard dict
        keyboard = {}
        rowData = {}
        #add list of keyboard rows
        keyboard["rows"] = []
        y = 0
        #iterate over rows
        for rowNum, row in enumerate(layout):
                x = 0
                #add empty row
                keyboard["rows"].append([])
                #check if item is a row or if it is a dict of keyboard properties
                if type(row) != dict:
                        #get row data from previous row
                        rowData = rowData
                        #iterate over keys in row
                        for pos, value in enumerate(row):
                                #check if item is a key or dict of key properties
                                if type(value) == str:
                                        #key is a dict with all the key's properties
                                        key = {};
                                        #if the previous item is a dict add the data to the rest of the row, or the current key, depending on what the property is
                                        if type(row[pos-1]) == dict:
                                                #prev is the previous item in the row
                                                prev = row[pos-1]
                                                #if prev has property set then add it to key
                                                if "x" in prev:
                                                        key["xCoord"] = prev["x"]
                                                        x += key["xCoord"]
                                                else:
                                                        key["xCoord"] = 0
                                                if "y" in prev:
                                                        key["yCoord"] = prev["y"]
                                                        y += prev["y"]
                                                if "w" in prev:
                                                        key["w"] = prev["w"]
                                                else:
                                                        key["w"] = 1
                                                if "h" in prev:
                                                        key["h"] = prev["h"]
                                                else:
                                                        key["h"] = 1
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

                                                #if rowData has property set then add it to key
                                                if "c" in rowData:
                                                        key["c"] = rowData["c"]
                                                if "t" in rowData:
                                                        key["t"] = rowData["t"]
                                                if "g" in rowData:
                                                        key["g"] = rowData["g"]
                                                if "a" in rowData:
                                                        key["a"] = rowData["a"]
                                                if "f" in rowData:
                                                        key["f"] = rowData["f"]
                                                if "f2" in rowData:
                                                        key["f2"] = rowData["f2"]
                                                if "p" in rowData:
                                                        key["p"] = rowData["p"].replace("R", "").replace("r", "").replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("SPACE", "").replace("space", "").replace(" ", "")
                                                else:
                                                        key["p"] = "DCS"

                                                if key["p"] == "" or key["p"] not in ["DSA", "DCS"]:
                                                        key["p"] = "DCS"

                                                #set the text on the key
                                                key["v"] = value
                                                #set the row and column of the key
                                                key["row"] = rowNum
                                                key["col"] = pos
                                                #set x and y coordinate of key
                                                key["x"] = x
                                                key["y"] = y
                                                #add the key to the current row
                                                keyboard["rows"][key["row"]].append(key)
                                        #if the previous item isn't a dict
                                        else:
                                                #if rowData has property set then add it to key
                                                if "c" in rowData:
                                                        key["c"] = rowData["c"]
                                                if "t" in rowData:
                                                        key["t"] = rowData["t"]
                                                if "g" in rowData:
                                                        key["g"] = rowData["g"]
                                                if "a" in rowData:
                                                        key["a"] = rowData["a"]
                                                if "f" in rowData:
                                                        key["f"] = rowData["f"]
                                                if "f2" in rowData:
                                                        key["f2"] = rowData["f2"]
                                                if "p" in rowData:
                                                        key["p"] = rowData["p"].replace("R", "").replace("r", "").replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("SPACE", "").replace("space", "").replace(" ", "")
                                                else:
                                                        key["p"] = "DCS"

                                                if key["p"] == "" or key["p"] not in ["DSA", "DCS"]:
                                                        key["p"] = "DCS"

                                                key["xCoord"] = 0
                                                key["w"] = 1
                                                key["h"] = 1

                                                #set the text on the key
                                                key["v"] = value
                                                #set the row and column of the key
                                                key["row"] = rowNum
                                                key["col"] = pos
                                                #set x and y coordinates of key
                                                key["x"] = x
                                                key["y"] = y
                                                #add the key to the current row
                                                keyboard["rows"][key["row"]].append(key)
                                        x += key["w"]
                        y += 1
                else:
                        #if the current item is a dict then add the backcolor property to the keyboard
                        if "backcolor" in row:
                            keyboard["backcolor"] = row["backcolor"]
        return keyboard

def read(filepath):
        #parse raw data into dict
        keyboard = getKey(filepath)

        #template objects that have to be appended in and then deleted at the end
        #defaultObjects = ["DCSL", "DCSMH", "DCSR", "DCST", "DCSMV", "DCSB", "DCSETL", "DCSETM", "DCSETR", "DCSEBL", "DCSEBM", "DCSEBR", "DSAL", "DSAMH", "DSAR", "DSAT", "DSAMV", "DSAB", "DSAETL", "DSAETM", "DSAETR", "DSAEBL", "DSAEBM", "DSAEBR", "side"]

        defaultObjects = ["DCSTL", "DCSTM", "DCSTR", "DCSML", "DCSMM", "DCSMR", "DCSBL", "DCSBM", "DCSBR", "DCSTLF", "DCSTMF", "DCSTRF", "DCSMLF", "DCSMMF", "DCSMRF", "DCSBLF", "DCSBMF", "DCSBRF", "DCSTLS", "DCSTMS", "DCSTRS", "DCSMLS", "DCSMMS", "DCSMRS", "DCSBLS", "DCSBMS", "DCSBRS", "DSATL", "DSATM", "DSATR", "DSAML", "DSAMM", "DSAMR", "DSABL", "DSABM", "DSABR", "DSATLF", "DSATMF", "DSATRF", "DSAMLF", "DSAMMF", "DSAMRF", "DSABLF", "DSABMF", "DSABRF", "DSATLS", "DSATMS", "DSATRS", "DSAMLS", "DSAMMS", "DSAMRS", "DSABLS", "DSABMS", "DSABRS", "side", "switch"]
        #blender file with template objects
        templateBlend = os.path.join(os.path.dirname(__file__), "template.blend", "Object")

        #append all the template objects
        for key in defaultObjects:
            bpy.ops.wm.append(filepath=templateBlend + key, directory=templateBlend, filename=key)

        #get the current scene and change display device so colors are accurate
        scn = bpy.context.scene
        scn.display_settings.display_device = "None"

        #set width and height of keyboard
        width = 0
        height = 0

        #iterate over rows in keyboard
        for row in keyboard["rows"]:
            #iterate over keys in row
            for key in row:
                #new material for key
                m = Material()
                m.set_cycles()
                m.make_material("%s-%s"%(key["row"], key["col"]))

                #make new diffuse node
                diffuseBSDF = m.nodes['Diffuse BSDF']

                #if key color is set convert hex to rgb and set diffuse color to that value, otherwise set it to rgba(0.8, 0.8, 0.8, 1)/#cccccc
                if "c" in key:
                    c = key["c"]
                    rgb = hex2rgb(key["c"])
                    diffuseBSDF.inputs["Color"].default_value = [rgb[0]/256, rgb[1]/256, rgb[2]/256, 1]
                else:
                    diffuseBSDF.inputs["Color"].default_value = [0.8, 0.8, 0.8, 1]

                #add material output node
                materialOutput = m.nodes['Material Output']
                #add glossy node
                glossyBSDF = m.makeNode('ShaderNodeBsdfGlossy', 'Glossy BSDF')
                #set glossy node color to white and roughness to 0.3
                glossyBSDF.inputs["Color"].default_value = [1, 1, 1, 1]
                glossyBSDF.inputs["Roughness"].default_value = 0.3
                #add mix node
                mixShader = m.makeNode('ShaderNodeMixShader', 'Mix Shader')
                #set mix node factor to 0.8
                mixShader.inputs['Fac'].default_value = 0.8
                #connect glossy and diffuse nodes to the mix node, and connect that to the material output
                m.link(glossyBSDF, 'BSDF', mixShader, 1)
                m.link(diffuseBSDF, 'BSDF', mixShader, 2)
                m.link(mixShader, 'Shader', materialOutput, 'Surface')

                new_obj_enter_tl = None

                TL = key["p"]+'TL'
                TM = key["p"]+'TM'
                TR = key["p"]+'TR'

                ML = key["p"]+'ML'
                MM = key["p"]+'MM'
                MR = key["p"]+'MR'

                BL = key["p"]+'BL'
                BM = key["p"]+'BM'
                BR = key["p"]+'BR'

                #if key is big ass enter or iso enter
                if "x2" in key or "y2" in key or "w2" in key or "h2" in key:
                    #set default values if they aren't set
                    if "x2" not in key:
                        key["x2"] = 0
                    if "y2" not in key:
                        key["y2"] = 0
                    if "w2" not in key:
                        key["w2"] = 1
                    if "h2" not in key:
                        key["h2"] = 1

                    if key["p"] == "DSA":
                        TL = key["p"]+'TLF'
                        TM = key["p"]+'TMF'
                        TR = key["p"]+'TRF'

                        ML = key["p"]+'MLF'
                        MM = key["p"]+'MMF'
                        MR = key["p"]+'MRF'

                        BL = key["p"]+'BLF'
                        BM = key["p"]+'BMF'
                        BR = key["p"]+'BRF'

                    #check if key is "stepped"
                    if "l" in key and key["l"] is True:
                        ETL = key["p"]+'TLS'
                        ETM = key["p"]+'TMS'
                        ETR = key["p"]+'TRS'

                        EML = key["p"]+'MLS'
                        EMM = key["p"]+'MMS'
                        EMR = key["p"]+'MRS'

                        EBL = key["p"]+'BLS'
                        EBM = key["p"]+'BMS'
                        EBR = key["p"]+'BRS'
                    else:
                        ETL = key["p"]+'TLF'
                        ETM = key["p"]+'TMF'
                        ETR = key["p"]+'TRF'

                        EML = key["p"]+'MLF'
                        EMM = key["p"]+'MMF'
                        EMR = key["p"]+'MRF'

                        EBL = key["p"]+'BLF'
                        EBM = key["p"]+'BMF'
                        EBR = key["p"]+'BRF'

                    #set the outcropping x and y
                    key["x2"] = key["x"] + key["x2"]
                    key["y2"] = key["y"] + key["y2"]

                    #add all the outcropping pieces
                    new_obj_enter_tl = bpy.data.objects[ETL].copy()
                    new_obj_enter_tl.data = bpy.data.objects[ETL].data.copy()
                    new_obj_enter_tl.animation_data_clear()
                    new_obj_enter_tl.location[0] = key["x2"]*-1 - 0.5
                    new_obj_enter_tl.location[1] = key["y2"]+0.5

                    new_obj_enter_tm = bpy.data.objects[ETM].copy()
                    new_obj_enter_tm.data = bpy.data.objects[ETM].data.copy()
                    new_obj_enter_tm.animation_data_clear()
                    new_obj_enter_tm.location[0] = (key["x2"]+key["w2"]/2)*-1
                    new_obj_enter_tm.location[1] = key["y2"]+0.5
                    new_obj_enter_tm.dimensions[0] = key["w2"]-1+0.2 if key["w2"]-1+0.2 > 0 else 0.2

                    new_obj_enter_tr = bpy.data.objects[ETR].copy()
                    new_obj_enter_tr.data = bpy.data.objects[ETR].data.copy()
                    new_obj_enter_tr.animation_data_clear()
                    new_obj_enter_tr.location[0] = key["x2"]*-1 - 0.5 - (key["w2"]-1)
                    new_obj_enter_tr.location[1] = key["y2"]+0.5

                    new_obj_enter_ml = bpy.data.objects[EML].copy()
                    new_obj_enter_ml.data = bpy.data.objects[EML].data.copy()
                    new_obj_enter_ml.animation_data_clear()
                    new_obj_enter_ml.location[0] = key["x2"]*-1 - 0.5
                    new_obj_enter_ml.location[1] = key["y2"] + 0.5 + (key["h2"]-1)/2
                    new_obj_enter_ml.dimensions[1] = key["h2"] - 1 + 0.2

                    new_obj_enter_mm = bpy.data.objects[EMM].copy()
                    new_obj_enter_mm.data = bpy.data.objects[EMM].data.copy()
                    new_obj_enter_mm.animation_data_clear()
                    new_obj_enter_mm.location[0] = (key["x2"]+key["w2"]/2)*-1
                    new_obj_enter_mm.location[1] = key["y2"]+0.5+(key["h2"]-1)/2
                    new_obj_enter_mm.dimensions = (key["w2"]-1+0.2 if key["w2"]-1+0.2 > 0 else 0.2, key["h2"] - 1 + 0.2, new_obj_enter_mm.dimensions[2])

                    new_obj_enter_mr = bpy.data.objects[EMR].copy()
                    new_obj_enter_mr.data = bpy.data.objects[EMR].data.copy()
                    new_obj_enter_mr.animation_data_clear()
                    new_obj_enter_mr.location[0] = (key["x2"])*-1 - 0.5 - (key["w2"]-1)
                    new_obj_enter_mr.location[1] = key["y2"]+0.5 + (key["h2"]-1)/2
                    new_obj_enter_mr.dimensions[1] = key["h2"] - 1 + 0.2

                    new_obj_enter_bl = bpy.data.objects[EBL].copy()
                    new_obj_enter_bl.data = bpy.data.objects[EBL].data.copy()
                    new_obj_enter_bl.animation_data_clear()
                    new_obj_enter_bl.location[0] = (key["x2"])*-1 - 0.5
                    new_obj_enter_bl.location[1] = key["y2"]+0.5+key["h2"] - 1

                    new_obj_enter_bm = bpy.data.objects[EBM].copy()
                    new_obj_enter_bm.data = bpy.data.objects[EBM].data.copy()
                    new_obj_enter_bm.animation_data_clear()
                    new_obj_enter_bm.location[0] = (key["x2"])*-1 - 0.5 - (key["w2"]-1)/2
                    new_obj_enter_bm.location[1] = key["y2"]+0.5+key["h2"]-1
                    new_obj_enter_bm.dimensions[0] = key["w2"]-1+0.2 if key["w2"]-1+0.2 > 0 else 0.2

                    new_obj_enter_br = bpy.data.objects[EBR].copy()
                    new_obj_enter_br.data = bpy.data.objects[EBR].data.copy()
                    new_obj_enter_br.animation_data_clear()
                    new_obj_enter_br.location[0] = (key["x2"])*-1 - 0.5 - (key["w2"]-1)
                    new_obj_enter_br.location[1] = key["y2"]+0.5+key["h2"]-1


                    #set outcropping material to the material that was just created
                    new_obj_enter_tl.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_tm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_tr.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_ml.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_mm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_mr.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_bl.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_bm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_enter_br.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]

                    #add outcropping to scene
                    scn.objects.link(new_obj_enter_tl)
                    scn.objects.link(new_obj_enter_tm)
                    scn.objects.link(new_obj_enter_tr)
                    scn.objects.link(new_obj_enter_ml)
                    scn.objects.link(new_obj_enter_mm)
                    scn.objects.link(new_obj_enter_mr)
                    scn.objects.link(new_obj_enter_bl)
                    scn.objects.link(new_obj_enter_bm)
                    scn.objects.link(new_obj_enter_br)

                    #deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    #combine all the pieces
                    new_obj_enter_tl.select = True
                    new_obj_enter_tm.select = True
                    new_obj_enter_tr.select = True
                    new_obj_enter_ml.select = True
                    new_obj_enter_mm.select = True
                    new_obj_enter_mr.select = True
                    new_obj_enter_bl.select = True
                    new_obj_enter_bm.select = True
                    new_obj_enter_br.select = True
                    bpy.context.scene.objects.active = new_obj_enter_tl
                    bpy.ops.object.join()

                else:
                    #set default values if they aren't set
                    if "x2" not in key:
                        key["x2"] = 0
                    if "y2" not in key:
                        key["y2"] = 0
                    if "w2" not in key:
                        key["w2"] = 1
                    if "h2" not in key:
                        key["h2"] = 1


                #add all the key pieces
                new_obj_tl = bpy.data.objects[TL].copy()
                new_obj_tl.data = bpy.data.objects[TL].data.copy()
                new_obj_tl.animation_data_clear()
                new_obj_tl.location[0] = key["x"]*-1 - 0.5
                new_obj_tl.location[1] = key["y"]+0.5

                new_obj_tm = bpy.data.objects[TM].copy()
                new_obj_tm.data = bpy.data.objects[TM].data.copy()
                new_obj_tm.animation_data_clear()
                new_obj_tm.location[0] = (key["x"]+key["w"]/2)*-1
                new_obj_tm.location[1] = key["y"]+0.5
                new_obj_tm.dimensions[0] = key["w"]-1+0.2 if key["w"]-1+0.2 > 0 else 0.2

                new_obj_tr = bpy.data.objects[TR].copy()
                new_obj_tr.data = bpy.data.objects[TR].data.copy()
                new_obj_tr.animation_data_clear()
                new_obj_tr.location[0] = key["x"]*-1 - 0.5 - (key["w"]-1)
                new_obj_tr.location[1] = key["y"]+0.5

                new_obj_ml = bpy.data.objects[ML].copy()
                new_obj_ml.data = bpy.data.objects[ML].data.copy()
                new_obj_ml.animation_data_clear()
                new_obj_ml.location[0] = key["x"]*-1 - 0.5
                new_obj_ml.location[1] = key["y"] + 0.5 + (key["h"]-1)/2
                new_obj_ml.dimensions[1] = key["h"] - 1 + 0.2

                new_obj_mm = bpy.data.objects[MM].copy()
                new_obj_mm.data = bpy.data.objects[MM].data.copy()
                new_obj_mm.animation_data_clear()
                new_obj_mm.location[0] = (key["x"]+key["w"]/2)*-1
                new_obj_mm.location[1] = key["y"]+0.5+(key["h"]-1)/2
                new_obj_mm.dimensions = (key["w"]-1+0.2 if key["w"]-1+0.2 > 0 else 0.2, key["h"] - 1 + 0.2, new_obj_mm.dimensions[2])

                new_obj_mr = bpy.data.objects[MR].copy()
                new_obj_mr.data = bpy.data.objects[MR].data.copy()
                new_obj_mr.animation_data_clear()
                new_obj_mr.location[0] = (key["x"])*-1 - 0.5 - (key["w"]-1)
                new_obj_mr.location[1] = key["y"]+0.5 + (key["h"]-1)/2
                new_obj_mr.dimensions[1] = key["h"] - 1 + 0.2

                new_obj_bl = bpy.data.objects[BL].copy()
                new_obj_bl.data = bpy.data.objects[BL].data.copy()
                new_obj_bl.animation_data_clear()
                new_obj_bl.location[0] = (key["x"])*-1 - 0.5
                new_obj_bl.location[1] = key["y"]+0.5+key["h"] - 1

                new_obj_bm = bpy.data.objects[BM].copy()
                new_obj_bm.data = bpy.data.objects[BM].data.copy()
                new_obj_bm.animation_data_clear()
                new_obj_bm.location[0] = (key["x"])*-1 - 0.5 - (key["w"]-1)/2
                new_obj_bm.location[1] = key["y"]+0.5+key["h"]-1
                new_obj_bm.dimensions[0] = key["w"]-1+0.2 if key["w"]-1+0.2 > 0 else 0.2

                new_obj_br = bpy.data.objects[BR].copy()
                new_obj_br.data = bpy.data.objects[BR].data.copy()
                new_obj_br.animation_data_clear()
                new_obj_br.location[0] = (key["x"])*-1 - 0.5 - (key["w"]-1)
                new_obj_br.location[1] = key["y"]+0.5+key["h"]-1


                #set key material to the material that was just created
                new_obj_tl.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_tm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_tr.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_ml.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_mm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_mr.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_bl.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_bm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                new_obj_br.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]

                #add key to scene
                scn.objects.link(new_obj_tl)
                scn.objects.link(new_obj_tm)
                scn.objects.link(new_obj_tr)
                scn.objects.link(new_obj_ml)
                scn.objects.link(new_obj_mm)
                scn.objects.link(new_obj_mr)
                scn.objects.link(new_obj_bl)
                scn.objects.link(new_obj_bm)
                scn.objects.link(new_obj_br)

                #deselect everything
                for obj in scn.objects:
                    obj.select = False

                #combine all the pieces
                new_obj_tl.select = True
                new_obj_tm.select = True
                new_obj_tr.select = True
                new_obj_ml.select = True
                new_obj_mm.select = True
                new_obj_mr.select = True
                new_obj_bl.select = True
                new_obj_bm.select = True
                new_obj_br.select = True
                #if outcropping exists add it to the key
                if new_obj_enter_tl is not None:
                    new_obj_enter_tl.select = True
                bpy.context.scene.objects.active = new_obj_tl
                bpy.ops.object.join()

                #name the key
                if key["v"] == "" and key["w"] < 4.5:
                    new_obj_tl.name = "Blank"
                elif key["v"] == "" and key["w"] >= 4.5:
                    new_obj_tl.name = "Space"
                else:
                    new_obj_tl.name = key["v"].replace("\n", " ")

                new_switch = bpy.data.objects["switch"].copy()
                new_switch.data = bpy.data.objects["switch"].data.copy()
                new_switch.animation_data_clear()
                new_switch.location[0] = (key["x"])*-1 - (key["w"])/2
                new_switch.location[1] = key["y"]+key["h"]/2
                scn.objects.link(new_switch)
                new_switch.name = "switch: %s-%s"%(key["row"], key["col"])

                #set the keyboard width and height if it was smaller than the current width
                if key["x"]+key["w"] > width:
                    width = key["x"]+key["w"]
                if key["y"] + key["h"] > height:
                    height = key["y"] + key["h"]

        m = Material()
        m.set_cycles()
        m.make_material("side")

        diffuseBSDF = m.nodes['Diffuse BSDF']

        #set case color if it is defined, otherwise set it to white
        if "backcolor" in keyboard:
            c = keyboard["backcolor"]
            rgb = hex2rgb(c)
            diffuseBSDF.inputs["Color"].default_value = [rgb[0]/255, rgb[1]/255, rgb[2]/255, 1]
        else:
            diffuseBSDF.inputs["Color"].default_value = [1, 1, 1, 1]

        #make the case material
        materialOutput = m.nodes['Material Output']
        glossyBSDF = m.makeNode('ShaderNodeBsdfGlossy', 'Glossy BSDF')
        glossyBSDF.inputs["Color"].default_value = [1, 1, 1, 1]
        glossyBSDF.inputs["Roughness"].default_value = 0.6
        mixShader = m.makeNode('ShaderNodeMixShader', 'Mix Shader')
        mixShader.inputs['Fac'].default_value = 0.8
        m.link(glossyBSDF, 'BSDF', mixShader, 1)
        m.link(diffuseBSDF, 'BSDF', mixShader, 2)
        m.link(mixShader, 'Shader', materialOutput, 'Surface')

        #create all the sides and the bottom of the case
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

        #set case pieces size and location and add them to the scene
        side1.location = (0.1, height/2, 0)
        side1.dimensions = (0.2, (height+0.4), 1)
        scn.objects.link(side1)

        side2.location = (width/-2, -0.1, 0)
        side2.dimensions = (width, 0.2, 1)
        scn.objects.link(side2)

        side3.location = ((width+0.1)*-1, height/2, 0)
        side3.dimensions = (0.2, (height+0.4), 1)
        scn.objects.link(side3)

        side4.location = (width/-2, (height+0.1), 0)
        side4.dimensions = (width, 0.2, 1)
        scn.objects.link(side4)

        side5.location = (width/-2, height/2, -0.25)
        side5.dimensions = (width, height, 0.5)
        scn.objects.link(side5)

        #deselect everything
        for obj in scn.objects:
            obj.select = False

        #select all case parts and join them together
        side1.select = True
        side2.select = True
        side3.select = True
        side4.select = True
        side5.select = True
        bpy.context.scene.objects.active = side5
        bpy.ops.object.join()
        #name the case
        side5.name = "Case"

        #deselect everything
        for obj in scn.objects:
            obj.select = False

        #remove all the template objects
        for object in defaultObjects:
            bpy.data.objects[object].select = True
        bpy.ops.object.delete()
