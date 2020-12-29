import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

bl_info = {
    "name": "Import: KLE Raw JSON format (.json)",
    "author": "Kirpal Demian",
    "version": (3, 3),
    "blender": (2, 91, 0),
    "location": "File > Import > KLE Raw Data (.json) ",
    "description": "Import layouts from Keyboard Layout Editor",
    "warning": "",
    "doc_url": "https://github.com/kirpal/keyboard-layout-editor-for-blender",
    "category": "Import-Export",
}


class ImportKLEJson(bpy.types.Operator, ImportHelper):
    """Import data from Keyboard Layout Editor"""
    bl_idname = "import_mesh.json"
    bl_label = "Import KLE Raw JSON"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        from .src import import_keyboard

        return import_keyboard.load_json(self, self.filepath)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func_import(self, context):
    """Add item to import menu"""
    self.layout.operator(ImportKLEJson.bl_idname, text="KLE Raw Data (.json)")


def register():
    bpy.utils.register_class(ImportKLEJson)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportKLEJson)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
