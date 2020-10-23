from bpy import context, ops, data
from typing import List, Tuple


def select_object(object, select=True):
    """Select an object (2.7/2.8)"""
    if hasattr(object, "select_set"):
        object.select_set(select)
    else:
        object.select = select


def set_active_object(obj):
    """Set the active object (2.7/2.8)"""
    select_object(obj)
    if hasattr(context, "view_layer"):
        context.view_layer.objects.active = obj
    else:
        context.scene.objects.active = obj


def select_all():
    """Select all the objects in a scene (2.7/2.8)"""
    ops.object.select_all(action='SELECT')


def unselect_all():
    """Unselect all the objects in a scene (2.7/2.8)"""
    ops.object.select_all(action='DESELECT')


def add_object(object, collection=None):
    """Add object to the scene (2.7/2.8)"""
    if collection is None:
        collection = context.scene.collection
    if hasattr(context.scene, "collection"):
        for c in object.users_collection:
            c.objects.unlink(object)
            if not c.objects:
                data.collections.remove(c)
        collection.objects.link(object)
    else:
        context.scene.objects.link(object)


def hex2rgb(hex: str):
    """Convert HEX color to Blender RGBA"""
    hex = hex.lstrip("#")

    if len(hex) == 3:
        r = int(str(hex[0:1]) + str(hex[0:1]), 16)
        g = int(str(hex[1:2]) + str(hex[1:2]), 16)
        b = int(str(hex[2:3]) + str(hex[2:3]), 16)
    else:
        r = int(str(hex[0:2]), 16)
        g = int(str(hex[2:4]), 16)
        b = int(str(hex[4:6]), 16)

    return [r / 255, g / 255, b / 255, 1]


def in_charset(char_code: int, ranges: List[Tuple[int]]):
    """Is the given code in any of the given ranges of charcodes?"""
    for bottom, top in ranges:
        if char_code >= bottom and char_code <= top:
            return True
    return False
