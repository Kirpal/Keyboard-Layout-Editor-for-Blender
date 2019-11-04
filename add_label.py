import bpy
import re
from math import pi
from . import helpers
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


def alignLegendsProfile(p):
    """Adjust legends based on keycap type"""
    return {
        "DCS": [0.25, 0.15, 0.25, 0.325],
        "DSA": [0.2, 0.25, 0.2, 0.25],
        "SA1": [0.2, 0.23, 0.2, 0.20],
        "SA2": [0.2, 0.23, 0.2, 0.23],
        "SA3": [0.2, 0.23, 0.2, 0.23],
        "SA3D": [0.2, 0.23, 0.2, 0.23],
        "SA4": [0.2, 0.23, 0.2, 0.23]
    }.get(p, [0.25, 0.15, 0.25, 0.325])


cap_thickness = 0.001

# Blender text vertical alignment accounts for line spacing, which is apparently set to ~1/.6 when aligning at top one
legendVerticalCorrection = [
    1.0, 1.0, 1.0,
    0.8, 0.8, 0.8,
    1.0, 1.0, 1.0,
    1.0, 1.0, 1.0
]

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


def add(label, font, profile, labelPosition, labelMaterial, labelSize, keyX, keyY, keyWidth, keyHeight, keyObject, offset=0.0005):
    """Add label to a key"""
    context = bpy.context
    scn = context.scene
    # add text
    new_label = bpy.data.curves.new(
        type="FONT", name="keylabel")
    new_label = bpy.data.objects.new(
        "label", new_label)
    label_text = re.sub(
        "<br ?/?>", "\n", HTMLParser().unescape(label))
    new_label.data.body = label_text

    new_label.data.font = font
    new_label.data.size = labelSize / 15

    # Here are some computations for the clipping boxes
    boxTop = keyY + \
        alignLegendsProfile(profile)[1]
    boxLeft = -1 * keyX - \
        alignLegendsProfile(profile)[0]

    label_verticalCorrection = - \
        0.1 if label_text in [
            ",", ";", ".", "[", "]"] else 0

    boxHeight = keyHeight - (alignLegendsProfile(
        profile)[1] + alignLegendsProfile(profile)[3])
    boxWidth = keyWidth - (alignLegendsProfile(
        profile)[0] + alignLegendsProfile(profile)[2])

    new_label.data.text_boxes[0].width = boxWidth
    new_label.data.text_boxes[0].height = boxHeight + \
        label_verticalCorrection * new_label.data.size

    new_label.data.text_boxes[0].y = -1 * (
        labelSize / 15) * legendVerticalCorrection[labelPosition]
    new_label.data.align_x = alignText[labelPosition][0]
    new_label.data.align_y = alignText[labelPosition][1]

    new_label.data.extrude = 0.01

    new_label.location = [boxLeft, boxTop, 2]
    new_label.rotation_euler[2] = pi

    helpers.add_object(scn, new_label)
    if hasattr(bpy.context, "view_layer"):
        bpy.context.view_layer.update()
    else:
        bpy.context.scene.update()

    helpers.unselect_all(scn)

    helpers.select_object(new_label)
    helpers.set_active_object(context, new_label)

    bpy.ops.object.convert()

    new_label.active_material = bpy.data.materials[labelMaterial]

    helpers.set_active_object(context, new_label)

    if labelSize > 6:
        bpy.ops.object.modifier_add(type='REMESH')
        new_label.modifiers["Remesh"].octree_depth = (
            4 if len(label_text) == 1 else 7)
        new_label.modifiers["Remesh"].use_remove_disconnected = False
        bpy.ops.object.modifier_apply(
            apply_as='DATA', modifier="Remesh")

    helpers.unselect_all(scn)

    helpers.select_object(new_label)
    helpers.set_active_object(context, new_label)

    bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.object.modifiers["Shrinkwrap"].offset = offset
    bpy.context.object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
    bpy.context.object.modifiers[
        "Shrinkwrap"].use_project_z = True
    bpy.context.object.modifiers[
        "Shrinkwrap"].use_positive_direction = True
    bpy.context.object.modifiers[
        "Shrinkwrap"].use_negative_direction = True
    bpy.context.object.modifiers[
        "Shrinkwrap"].target = keyObject
    bpy.ops.object.modifier_apply(
        apply_as='DATA', modifier="Shrinkwrap")

    # create clipping cube
    bpy.ops.mesh.primitive_cube_add(
        location=(boxLeft-boxWidth*0.5, boxTop+boxHeight*0.5, 1))
    cube = bpy.context.object
    cube.scale[0] = 0.5*boxWidth
    cube.scale[1] = 0.5*boxHeight
    cube.name = 'clipCube'

    helpers.unselect_all(scn)

    helpers.select_object(new_label)
    helpers.set_active_object(context, new_label)

    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
    bpy.context.object.modifiers["Boolean"].object = scn.objects["clipCube"]
    bpy.ops.object.modifier_apply(
        apply_as='DATA', modifier="Boolean")
    bpy.data.objects.remove(cube)

    for edge in bpy.context.object.data.edges:
        edge.crease = 1

    new_label.location[2] += cap_thickness

    helpers.unselect_all(scn)

    helpers.select_object(new_label)
    helpers.select_object(keyObject)
    helpers.set_active_object(context, keyObject)
    bpy.ops.object.join()
