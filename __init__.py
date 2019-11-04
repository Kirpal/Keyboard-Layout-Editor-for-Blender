import bpy

bl_info = {
    "name": "Import: KLE Raw JSON format (.json)",
    "author": "Kirpal Demian",
    "version": (3, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > Keyboard Layout Editor Raw (.json) ",
    "description": "Import Keyboard Layouts",
    "warning": "",
    "category": "Import-Export",
}


class JSONImporter(bpy.types.Operator):
    """Load Keyboard Layout data"""
    bl_idname = "import_mesh.json"
    bl_label = "Import KLE Raw JSON"
    bl_options = {'UNDO'}

    filepath = bpy.props.StringProperty(
        subtype='FILE_PATH',
    )
    filter_glob = bpy.props.StringProperty(
        default="*.json", options={'HIDDEN'})

    def execute(self, context):
        from . import import_keyboard
        import_keyboard.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import(self, context):
    """Add item to import menu"""
    self.layout.operator(JSONImporter.bl_idname, text="KLE Raw Data (.json)")


def register():
    if hasattr(bpy.types, "TOPBAR_MT_file_import"):
        bpy.utils.register_class(JSONImporter)
        bpy.types.TOPBAR_MT_file_import.append(menu_import)
    else:
        bpy.utils.register_module(__name__)
        bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    if hasattr(bpy.types, "TOPBAR_MT_file_import"):
        bpy.utils.unregister_class(JSONImporter)
        bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    else:
        bpy.utils.unregister_module(__name__)
        bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
