"""
This script imports JSON File format files to Blender.

It uses the JSON file downloaded from keyboard-layout-editor.com

Usage:
Execute this script from the "File->Import" menu and choose a JSON file to
open.
"""

import bpy
from mathutils import Vector
import json
import urllib.request
import os
import re
from math import pi
from . import parse_json
from . import labels
from .helpers import *
from .materials import make_key_material, make_led_material
from .key import Label, Key, KeyBase, KeySegment, Profile


GOOGLE_FONTS = json.load(open(os.path.join(os.path.dirname(
    __file__), "fonts.json")))

# blender file with template objects
TEMPLATE_BLEND = os.path.join(os.path.dirname(__file__), "template.blend", "Object")

# keeps track of all objects that have been appended
appended_objects = []


def append_object(obj_name: str):
    """Append the given object from the template file"""
    bpy.ops.wm.append(filepath=TEMPLATE_BLEND + obj_name, directory=TEMPLATE_BLEND, filename=obj_name)

    object = bpy.data.objects[obj_name]
    set_active_object(object)
    for mod in object.modifiers:
        apply_modifier(mod.name)

    appended_objects.append(obj_name)


def copy_template(keyboard_collection, key: KeyBase, segment: KeySegment, material_name: str = None):
    """Copy in the given template object and set its location, returning the new object"""
    obj_name = key.segment_name(segment)
    x, y = key.segment_location(segment)
    width, height = key.segment_dimensions(segment)

    # If the object isn't already in the scene, copy it in
    if obj_name not in bpy.data.objects:
        append_object(obj_name)

    new_obj = bpy.data.objects[obj_name].copy()
    new_obj.data = bpy.data.objects[obj_name].data.copy()
    new_obj.animation_data_clear()
    new_obj.location[0] = x
    new_obj.location[1] = y
    # there's a bug in blender where you can't set multiple dimensions individually,
    # so we have to set width and height at the same time
    if width is not None or height is not None:
        new_dimensions = new_obj.dimensions.copy()
        if width is not None:
            new_dimensions[0] = width
        if height is not None:
            new_dimensions[1] = height
        new_obj.dimensions = new_dimensions
    new_obj.active_material = bpy.data.materials[material_name if material_name is not None else key.color]
    add_object(new_obj, keyboard_collection)

    return new_obj


def read(filepath: str):
    """Read the json file at the given filepath and load the keyboard"""
    bpy.context.window.cursor_set("WAIT")
    # parse raw data into dict
    keyboard = parse_json.load(filepath)

    keyboard_collection = bpy.data.collections.new(keyboard.name)
    bpy.context.scene.collection.children.link(keyboard_collection)

    # get the current scene and change display device so colors are accurate
    context = bpy.context
    scn = context.scene
    scn.display_settings.display_device = "None"
    scn.render.engine = 'CYCLES'

    if hasattr(bpy.data, "collections"):
        bpy.ops.collection.create(name="Keyboard")
    else:
        bpy.ops.group.create(name="Keyboard")

    keyboard_empty = bpy.data.objects.new("Keyboard_whole", None)
    keyboard_empty.location = (0, 0, 0)
    add_object(keyboard_empty, keyboard_collection)

    fonts = [None for i in range(0, 12)]
    # get fonts from css
    if keyboard.css:
        selectors = []
        props = []
        css = re.sub(r'(\@import [^;]+\;|\@font-face [^\}]+\}|\/\*.*\*\/)', "", keyboard.css)
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

                if font in GOOGLE_FONTS.keys():
                    font_path = os.path.join(bpy.app.tempdir, font + ".ttf")
                    urllib.request.urlretrieve(GOOGLE_FONTS[font], font_path)
                    font = bpy.data.fonts.load(font_path)
                else:
                    font = None

                for selector in selectors:
                    if selector == "*":
                        fonts = [font for i in range(0, 12)]
                    elif re.fullmatch(r".keylabel[0-9][1-2]?", selector) and int(selector.replace(".keylabel", "")) >= 0 and int(selector.replace(".keylabel", "")) <= 11:
                        fonts[int(selector.replace(".keylabel", ""))] = font

    bpy.context.window_manager.progress_begin(keyboard.key_count, 0)
    bpy.context.window.cursor_set("DEFAULT")
    currentKey = 0

    # iterate over keys in keyboard
    for key in keyboard:
        # only add the key if it is not a 'decal' key
        if not key.is_decal:
            # make new material for key
            make_key_material(key.color)

            added_segments = []

            # if key is big ass enter or iso enter
            if key.outcrop:
                outcrop_segments = [
                    KeySegment.TL,
                    KeySegment.TM,
                    KeySegment.TR,
                    KeySegment.ML,
                    KeySegment.MM,
                    KeySegment.MR,
                    KeySegment.BL,
                    KeySegment.BM,
                    KeySegment.BR
                ]

                for segment in outcrop_segments:
                    added_segments.append(
                        copy_template(keyboard_collection, key.outcrop, segment))

            key_segments = [
                KeySegment.TL,
                KeySegment.TR,
                KeySegment.BL,
                KeySegment.BR
            ]

            # check if we need the middle strip, force middle strip for DSA
            if key.profile is Profile.DSA or key.height - 1 - 0.1 > 0:
                key_segments += [
                    KeySegment.ML,
                    KeySegment.MR
                ]

            if key.profile is Profile.DSA or key.width - 1 - 0.1 > 0:
                key_segments += [
                    KeySegment.TM,
                    KeySegment.BM
                ]

                # If the horizontal and vertical strips are needed, also add the middle piece
                if key_segments.count(KeySegment.ML) > 0:
                    key_segments.append(KeySegment.MM)

            for segment in key_segments:
                added_segments.append(copy_template(keyboard_collection, key, segment))

            key_obj = added_segments[0]

            unselect_all()

            # combine all the pieces
            for obj in added_segments:
                select_object(obj)
            set_active_object(key_obj)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.join()

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.remove_doubles()
            # DCS looks bad when shaded smooth
            if key.profile is not Profile.DCS:
                bpy.ops.mesh.faces_shade_smooth()
            bpy.ops.object.mode_set(mode='OBJECT')

            # Name the new object based on the key's legend
            key_obj.name = key.name

            # add key switch
            new_switch = copy_template(keyboard_collection, key, KeySegment.SWITCH)
            new_switch.name = "switch: %s-%s" % (key.row, key.column)

            if keyboard.led_color:
                new_led = copy_template(keyboard_collection, key, KeySegment.LED, 'led')
                new_led.name = "led: %s-%s" % (key.row, key.column)

            for pos, label in enumerate(key.labels):
                # make sure it's not a front legend
                if pos < 9:
                    if label.text != "":
                        material_name = None
                        if keyboard.led_color and label.color == keyboard.led_color:
                            material_name = make_led_material(label.color, keyboard.led_brightness)
                        else:
                            material_name = make_key_material(label.color)

                        labels.add(
                            key,
                            fonts,
                            pos,
                            material_name,
                            key_obj)

            # rotate key
            if key.rotation:
                empty = bpy.data.objects.new("rotate", None)
                empty.location = (key.rx * -1, key.ry, 0.3)
                add_object(empty, keyboard_collection)

                unselect_all()

                select_object(key_obj)
                select_object(new_switch)
                if keyboard.led_color:
                    select_object(new_led)
                set_active_object(empty)
                bpy.ops.object.parent_set(type="OBJECT")

                empty.rotation_euler[2] = pi * (key.rotation * -1) / 180

                unselect_all()

                select_object(key_obj)
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                select_object(new_switch)
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                if keyboard.led_color:
                    select_object(new_led)
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

                unselect_all()

                select_object(empty)
                bpy.ops.object.delete(use_global=False)

            select_object(key_obj)
            select_object(new_switch)
            if keyboard.led_color:
                select_object(new_led)
            set_active_object(keyboard_empty)
            bpy.ops.object.parent_set(type="OBJECT")

            unselect_all()

        bpy.context.window_manager.progress_update(currentKey)
        currentKey += 1

    # get case height and width from generated keys
    set_active_object(keyboard_empty)
    bpy.ops.object.select_grouped(type="CHILDREN_RECURSIVE")
    min_x = 10000000.0
    max_x = -1000000.0
    min_y = 10000000.0
    max_y = -1000000.0
    for o in bpy.context.selected_objects:
        bbox_corners = [o.matrix_world @
                        Vector(corner) for corner in o.bound_box]
        for c in bbox_corners:
            min_x = min(min_x, c[0])
            max_x = max(max_x, c[0])
            min_y = min(min_y, c[1])
            max_y = max(max_y, c[1])

    width = (max_x - min_x) + 0.5
    height = (max_y - min_y) + 0.5
    caseX = (max_x + min_x) / 2.0
    caseY = (max_y + min_y) / 2.0

    # create the case
    append_object('case')
    caseTemplate = bpy.data.objects['case']
    case = caseTemplate.copy()
    case.data = caseTemplate.data.copy()
    case.animation_data_clear()

    case.location = (caseX, caseY, -0.25)
    case.dimensions = (width, height, 0.5)

    add_object(case, keyboard_collection)

    select_object(case)
    set_active_object(case)

    bpy.data.materials["case"].node_tree.nodes["RGB"].outputs[0].default_value = hex2rgb(keyboard.color)

    # name the case
    case.name = "Case"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    unselect_all()

    select_object(case)
    set_active_object(keyboard_empty)
    bpy.ops.object.parent_set(type="OBJECT")

    # This assumes 1 blender unit = 10cm
    blender_scaling = .1905
    keyboard_empty.scale = (blender_scaling, blender_scaling, blender_scaling)
    keyboard_empty.rotation_euler[2] = pi
    keyboard_empty.location = (-blender_scaling * width * 0.5,
                               blender_scaling * height * 0.5, blender_scaling * 0.5)

    unselect_all()

    select_object(keyboard_empty)
    set_active_object(keyboard_empty)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    bpy.ops.object.delete(use_global=False)

    select_object(case)
    set_active_object(case)
    # bevel the corners
    bpy.ops.object.modifier_add(type="BEVEL")
    apply_modifier("Bevel")

    bpy.data.materials["Stem"].node_tree.nodes[
        "Diffuse BSDF"].inputs["Color"].default_value = keyboard.stem_color

    if keyboard.led_color:
        bpy.data.materials["led"].node_tree.nodes["Emission"].inputs["Color"].default_value = hex2rgb(keyboard.led_color)
        bpy.data.materials["led"].node_tree.nodes["Emission"].inputs["Strength"].default_value = keyboard.led_brightness * 5


def cleanup():
    """Remove all the template objects in the scene"""
    unselect_all()
    for object in appended_objects:
        if object in bpy.data.objects:
            select_object(bpy.data.objects[object])
    bpy.ops.object.delete()

    bpy.context.window_manager.progress_end()


def load_json(operator, filepath):
    """Load the json file"""
    try:
        appended_objects = []
        read(filepath)
    except json.decoder.JSONDecodeError as e:
        cleanup()
        operator.report({'WARNING'}, "Unable to parse JSON, %s:%s for file %r" % (type(e).__name__, e, filepath))
        return {'CANCELLED'}
    except Exception:
        cleanup()
        raise

    cleanup()
    return {'FINISHED'}
