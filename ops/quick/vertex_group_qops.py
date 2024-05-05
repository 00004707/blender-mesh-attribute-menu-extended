"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit Vertex Group Data

"""

# Quick Vertex Groups

def vertexgrouppoll(self, context):
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False
    elif not len(obj.vertex_groups):
        self.poll_message_set("No vertex groups")
        return False
    elif obj.vertex_groups.active_index  is None:
        self.poll_message_set("No active vertex group")
        return False
    elif not func.poll_func.pinned_mesh_poll(self, context, False):
        return False
    return True


class QuickVertexGroupToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_vertex_group"
    bl_label = "To Attribute"
    bl_description = "Converts active Vertex Group to Vertex Float Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return vertexgrouppoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_FROM_VERTEX_GROUP"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_vertex_groups'] = str(obj.vertex_groups.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickAllVertexGroupToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_all_vertex_groups"
    bl_label = "All Attributes"
    bl_description = "Converts all Vertex Groups to Vertex Float Attributes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return vertexgrouppoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_FROM_VERTEX_GROUP"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = True
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_vertex_groups'] = str(obj.vertex_groups.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickVertexGroupAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_vertex_group_assignment"
    bl_label = "To Attribute from assignment"
    bl_description = "Converts Vertex Group vertex assignent to Vertex Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return vertexgrouppoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_IS_IN_VERTEX_GROUP"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_vertex_groups'] = str(obj.vertex_groups.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickAllVertexGroupAssignmentToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_all_from_vertex_group_assignment"
    bl_label = "All to Attribute from assignment"
    bl_description = "Converts Vertex Group vertex assignent to Vertex Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return vertexgrouppoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_IS_IN_VERTEX_GROUP"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = True
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_vertex_groups'] = str(obj.vertex_groups.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)