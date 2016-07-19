
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
                                                        key["p"] = rowData["p"]

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
                                                        key["p"] = rowData["p"]

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
                        keyboard["backcolor"] = row["backcolor"]
        return keyboard

def read(filepath):
        #parse raw data into dict
        keyboard = getKey(filepath)

        #template objects that have to be appended in and then deleted at the end
        defaultObjects = ["DCSL", "DCSMH", "DCSR", "DCST", "DCSMV", "DCSB", "DCSETL", "DCSETM", "DCSETR", "DCSEBL", "DCSEBM", "DCSEBR", "side"]
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

                new_obj_etl = None
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
                        key["h2"] = 1.5
                    else:
                        #make sure the key "outcropping" doesn't stick out of the other side
                        while (key["y2"]+key["h2"]) > 0.5:
                            key["h2"] -= 0.25

                    #add all the parts of the key outcropping
                    new_obj_etl = bpy.data.objects['DCSETL'].copy()
                    new_obj_etl.data = bpy.data.objects['DCSETL'].data.copy()
                    new_obj_etl.animation_data_clear()
                    new_obj_etl.location[0] = (key["x"]+key["x2"])*-1
                    new_obj_etl.location[1] = key["y"]+key["y2"]

                    new_obj_etm = bpy.data.objects['DCSETM'].copy()
                    new_obj_etm.data = bpy.data.objects['DCSETM'].data.copy()
                    new_obj_etm.animation_data_clear()
                    new_obj_etm.location[0] = (key["x"]+key["x2"]+key["w2"]/2)*-1
                    new_obj_etm.location[1] = key["y"]+key["y2"]+(key["h2"]/2)
                    new_obj_etm.dimensions[0] = (key["w2"]-1)+0.2 if key["w2"]-1+0.2 > 0 else 0

                    new_obj_etr = bpy.data.objects['DCSETR'].copy()
                    new_obj_etr.data = bpy.data.objects['DCSETR'].data.copy()
                    new_obj_etr.animation_data_clear()
                    new_obj_etr.location[0] = (key["x"]+key["x2"])*-1 - 0.5 - (key["w2"]-1)
                    new_obj_etr.location[1] = key["y"]+key["y2"]

                    new_obj_ebl = bpy.data.objects['DCSEBL'].copy()
                    new_obj_ebl.data = bpy.data.objects['DCSEBL'].data.copy()
                    new_obj_ebl.animation_data_clear()
                    new_obj_ebl.location[0] = (key["x"]+key["x2"])*-1
                    new_obj_ebl.location[1] = key["y"]+0.5+key["y2"]
                    new_obj_ebl.dimensions[1] = (key["h2"]-0.5)

                    new_obj_ebm = bpy.data.objects['DCSEBM'].copy()
                    new_obj_ebm.data = bpy.data.objects['DCSEBM'].data.copy()
                    new_obj_ebm.animation_data_clear()
                    new_obj_ebm.location[0] = (key["x"]+key["x2"]+key["w2"]/2)*-1
                    new_obj_ebm.location[1] = key["y"]+0.5+key["y2"]
                    new_obj_ebm.dimensions = ((key["w2"]-1)+0.2 if key["w2"]-1+0.2 > 0 else 0, (key["h2"]-0.5)+0.2, 0.466)

                    new_obj_ebr = bpy.data.objects['DCSEBR'].copy()
                    new_obj_ebr.data = bpy.data.objects['DCSEBR'].data.copy()
                    new_obj_ebr.animation_data_clear()
                    new_obj_ebr.location[0] = (key["x"]+key["x2"])*-1 - 0.5 - (key["w2"]-1)
                    new_obj_ebr.location[1] = key["y"]+0.5+key["y2"]
                    new_obj_ebr.dimensions[1] = (key["h2"]-0.5)


                    #set outcropping material to the material that was just created
                    new_obj_etl.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_etm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_etr.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_ebl.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_ebm.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_ebr.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]

                    #add outcropping to scene
                    scn.objects.link(new_obj_etl)
                    scn.objects.link(new_obj_etm)
                    scn.objects.link(new_obj_etr)
                    scn.objects.link(new_obj_ebl)
                    scn.objects.link(new_obj_ebm)
                    scn.objects.link(new_obj_ebr)

                    #deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    #combine all the pieces
                    new_obj_etl.select = True
                    new_obj_etm.select = True
                    new_obj_etr.select = True
                    new_obj_ebl.select = True
                    new_obj_ebm.select = True
                    new_obj_ebr.select = True
                    bpy.context.scene.objects.active = new_obj_etl
                    bpy.ops.object.join()

                #check if key is horizontal
                if key["w"] >= key["h"]:
                    #add all the key parts
                    new_obj_l = bpy.data.objects['DCSL'].copy()
                    new_obj_l.data = bpy.data.objects['DCSL'].data.copy()
                    new_obj_l.animation_data_clear()
                    new_obj_l.location[0] = key["x"]*-1
                    new_obj_l.location[1] = key["y"]

                    new_obj_mh = bpy.data.objects['DCSMH'].copy()
                    new_obj_mh.data = bpy.data.objects['DCSMH'].data.copy()
                    new_obj_mh.animation_data_clear()
                    new_obj_mh.location[0] = (key["x"]+0.5+(key["w"]-1)/2)*-1
                    new_obj_mh.location[1] = key["y"]
                    new_obj_mh.dimensions[0] = (key["w"]-1)+0.2

                    new_obj_r = bpy.data.objects['DCSR'].copy()
                    new_obj_r.data = bpy.data.objects['DCSR'].data.copy()
                    new_obj_r.animation_data_clear()
                    new_obj_r.location[0] = (key["x"]+0.5+(key["w"]-1))*-1
                    new_obj_r.location[1] = key["y"]


                    #set key material to the material that was just created
                    new_obj_l.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_mh.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_r.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]

                    #add key parts to scene
                    scn.objects.link(new_obj_l)
                    scn.objects.link(new_obj_mh)
                    scn.objects.link(new_obj_r)

                    #deselect everything
                    for obj in scn.objects:
                        obj.select = False
                    #select key outcropping if it exists
                    if new_obj_etl is not None:
                        new_obj_etl.select = True

                    #select key parts and join them together
                    new_obj_l.select = True
                    new_obj_mh.select = True
                    new_obj_r.select = True
                    bpy.context.scene.objects.active = new_obj_l
                    bpy.ops.object.join()

                    #set name of key
                    if key["v"] == "" and key["w"] < 4.5:
                        new_obj_l.name = "Blank"
                    elif key["v"] == "" and key["w"] >= 4.5:
                        new_obj_l.name = "Space"
                    else:
                        new_obj_l.name = key["v"].replace("\n", " ")

                #if key is vertical
                else:

                    #add key parts
                    new_obj_t = bpy.data.objects['DCST'].copy()
                    new_obj_t.data = bpy.data.objects['DCST'].data.copy()
                    new_obj_t.animation_data_clear()
                    new_obj_t.location[0] = key["x"]*-1
                    new_obj_t.location[1] = key["y"]

                    new_obj_mv = bpy.data.objects['DCSMV'].copy()
                    new_obj_mv.data = bpy.data.objects['DCSMV'].data.copy()
                    new_obj_mv.animation_data_clear()
                    new_obj_mv.location[0] = key["x"]*-1
                    new_obj_mv.location[1] = key["y"]-0.5+(key["h"]-1/2)
                    new_obj_mv.dimensions[1] = (key["h"]-1)+0.2

                    new_obj_b = bpy.data.objects['DCSB'].copy()
                    new_obj_b.data = bpy.data.objects['DCSB'].data.copy()
                    new_obj_b.animation_data_clear()
                    new_obj_b.location[0] = key["x"]*-1
                    new_obj_b.location[1] = key["y"]+0.5+key["h"]-1

                    #set key material to the material that was just created
                    new_obj_t.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_mv.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]
                    new_obj_b.active_material = bpy.data.materials["%s-%s"%(key["row"], key["col"])]

                    #add key to scene
                    scn.objects.link(new_obj_t)
                    scn.objects.link(new_obj_mv)
                    scn.objects.link(new_obj_b)

                    #deselect everything
                    for obj in scn.objects:
                        obj.select = False

                    #select outcropping if it exists
                    if new_obj_etl is not None:
                        new_obj_etl.select = True

                    #join all key parts
                    new_obj_t.select = True
                    new_obj_mv.select = True
                    new_obj_b.select = True
                    bpy.context.scene.objects.active = new_obj_t
                    bpy.ops.object.join()

                    new_obj_t.name = key["v"].replace("\n", " ") if key["v"] != "" else "Blank"

                #set the keyboard width and height if it was smaller than the current width
                if key["x"]+key["w"] > width:
                    width = key["x"]+key["w"]
                if key["y"] + key["h"] > height:
                    height = key["y"] + key["h"]

        m = Material()
        m.set_cycles()
        m.make_material("side")

        diffuseBSDF = m.nodes['Diffuse BSDF']

        #set backcolor if it is defined, otherwise set it to black
        if "backcolor" in keyboard:
            c = keyboard["backcolor"]
            rgb = hex2rgb(c)
            diffuseBSDF.inputs["Color"].default_value = [rgb[0]/255, rgb[1]/255, rgb[2]/255, 1]
        else:
            diffuseBSDF.inputs["Color"].default_value = [0, 0, 0, 1]

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
        side1.dimensions = (0.2, (height+0.4), 0.6)
        scn.objects.link(side1)

        side2.location = (width/-2, -0.1, 0)
        side2.dimensions = (width, 0.2, 0.6)
        scn.objects.link(side2)

        side3.location = ((width+0.1)*-1, height/2, 0)
        side3.dimensions = (0.2, (height+0.4), 0.6)
        scn.objects.link(side3)

        side4.location = (width/-2, (height+0.1), 0)
        side4.dimensions = (width, 0.2, 0.6)
        scn.objects.link(side4)

        side5.location = (width/-2, height/2, -0.15)
        side5.dimensions = (width, height, 0.3)
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
