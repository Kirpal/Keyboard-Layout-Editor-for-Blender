def select_object(object, select=True):
    """Select an object (2.7/2.8)"""
    if hasattr(object, "select_set"):
        object.select_set(select)
    else:
        object.select = select


def set_active_object(context, obj):
    """Set the active object (2.7/2.8)"""
    if hasattr(context, "view_layer"):
        context.view_layer.objects.active = obj
    else:
        context.scene.objects.active = obj


def unselect_all(scene):
    """Unselect all the objects in a scene (2.7/2.8)"""
    for obj in scene.objects:
        select_object(obj, select=False)


def add_object(scene, object):
    """Add object to the scene (2.7/2.8)"""
    if hasattr(scene, "collection"):
        scene.collection.objects.link(object)
    else:
        scene.objects.link(object)
