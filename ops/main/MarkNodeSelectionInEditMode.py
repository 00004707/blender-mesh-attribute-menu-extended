from modules import LEGACY_etc
from modules.CreateBuiltInAttribute import CreateBuiltInAttribute
import modules.ui.ui_common


class MarkNodeSelectionInEditMode(bpy.types.Operator):
    """
    TODO
    """

    # BLENDER CLASS PROPERTIES
    # ---------------------------------

    bl_idname = "mesh.node_mark_selection"
    bl_label = "Mark selection input of this node in edit mode"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # COMMON
    # ---------------------------------

    b_pinned_mesh_support = True
    b_active_object_required = False
    supported_object_types = ['MESH', 'CURVES', 'POINTCLOUD']
    wiki_url = 'TODO'



    @classmethod
    def poll(self, context):

        obj, obj_data = func.obj_func.get_object_in_context(context)

        if not obj:
            self.poll_message_set("No active or invalid pinned object")
            return False
        elif not obj.type in self.supported_object_types :
            self.poll_message_set("Object type is not supported")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, self.b_pinned_mesh_support):
            return False
        return True

    def execute(self, context):
        try:
            return {'FINISHED'}
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(CreateBuiltInAttribute, exc)
            return {"CANCELLED"}


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        row = self.layout
        b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
        obj, obj_data = func.obj_func.get_object_in_context(context)

        # Show the drop-down menu
        sub_box = row.column()
        sub_box.label(text="Built-In Attribute")

        # Wiki
        modules.ui.ui_common.append_wiki_operator(self, context)