# addon details
bl_info = {
    "name": "Import: KLE Raw JSON format -- wilder (.json)",
    "author": "/u/kdem007 /u/jacopods",
    "version": (2, 0),
    "blender": (2, 78, 0),
    "location": "File > Import-Export > Keyboard Layout Editor Raw TESTING (.json) ",
    "description": "Import Keyboard Layouts -- wilder TESTING version",
    "warning": "",
    "category": "Import-Export",
}

import bpy

# main addon class


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

# add to import menu


def menu_import(self, context):
    self.layout.operator(JSONImporter.bl_idname, text="KLE Raw Data --TESTING-- (.json)")

# register addon


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_import)

# unregister addon


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
