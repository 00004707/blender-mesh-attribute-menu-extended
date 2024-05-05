"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit Face Maps

"""

# Quick Face Maps

def facemappoll(self, context):
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False
    elif not hasattr(obj, 'face_maps') or not len(obj.face_maps):
        self.poll_message_set("No Face Maps")
        return False
    elif obj.face_maps.active_index is None:
        self.poll_message_set("No active shape key")
        return False
    elif not func.poll_func.pinned_mesh_poll(self, context, False):
        return False
    return True


class QuickFaceMapAssignmentToAttribute(bpy.types.Operator):
    # this is for pre blender 4.0
    bl_idname = "mesh.attribute_quick_from_face_map"
    bl_label = "To Attribute from assignment"
    bl_description = "Convert assignment of active Face Map to Boolean Face Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return facemappoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "FACE_FROM_FACE_MAP"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_face_maps'] = str(obj.face_maps.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickFaceMapIndexToAttribute(bpy.types.Operator):
    # this is for pre blender 4.0
    bl_idname = "mesh.attribute_quick_from_face_map_index"
    bl_label = "To Attribute from index"
    bl_description = "Converts Face Map index assignment to Integer Face Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        return facemappoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "FACE_MAP_INDEX"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_face_maps'] = str(obj.face_maps.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)