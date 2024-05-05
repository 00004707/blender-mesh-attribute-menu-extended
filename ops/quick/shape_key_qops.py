"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit Shape Key Data

"""

# Quick Shape Key

def quickshapekeypoll(self, context):
    """
    Poll function for all shape key quick ops
    """
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False
    elif obj.data.shape_keys is None:
        self.poll_message_set("No shape keys")
        return False
    elif obj.active_shape_key_index is None:
        self.poll_message_set("No active shape key")
        return False
    elif not func.poll_func.pinned_mesh_poll(self, context, False):
        return False
    return True

def dirtyquickshapekeypoll():
    """
    Dirty poll for same checks but without self reference
    """

    try:
        quickshapekeypoll(None, bpy.context)
    except AttributeError:
        return False

def get_first_shape_key_name():
    obj = bpy.context.active_object

    if not dirtyquickshapekeypoll():
        return ""
    else:
        return obj.data.shape_keys.key_blocks[0].name



class QuickShapeKeyToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_shape_key"
    bl_label = "To Attribute"
    bl_description = "Converts active Shape Key to Vertex Vector Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return quickshapekeypoll(self, context)

    def execute(self, context):
        obj = context.active_object
        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_SHAPE_KEY_POSITION"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = False
        args['b_offset_from_offset_to_toggle'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_shape_keys'] = str(obj.active_shape_key_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickAllShapeKeyToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_all_shape_keys"
    bl_label = "All to Attributes"
    bl_description = "Converts all Shape Keys to Vertex Vector Attributes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return quickshapekeypoll(self, context)

    def execute(self, context):
        obj = context.active_object
        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_SHAPE_KEY_POSITION"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = True
        args['b_offset_from_offset_to_toggle'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_shape_keys'] = str(obj.active_shape_key_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickShapeKeyOffsetToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_offset_from_shape_key"
    bl_label = f"To Attribute as offset from Basis"
    bl_description = "Converts active Shape Key offset to Vertex Vector Attribute as an offset from Basis Shape Key"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return quickshapekeypoll(self, context)

    def execute(self, context):
        obj = context.active_object
        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_SHAPE_KEY_POSITION_OFFSET"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = False
        args['b_offset_from_offset_to_toggle'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_shape_keys'] = str(0)
        args['enum_shape_keys_offset_target'] = str(obj.active_shape_key_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickAllShapeKeyOffsetToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_offset_from_all_shape_keys"
    bl_label = "All to Attributes as offsets from Basis"
    bl_description = "Converts all Shape Keys offsets to Vertex Vector Attributes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return quickshapekeypoll(self, context)

    def execute(self, context):
        obj = context.active_object
        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "VERT_SHAPE_KEY_POSITION_OFFSET"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = True
        args['b_offset_from_offset_to_toggle'] = True
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_shape_keys'] = str(obj.active_shape_key_index)
        args['enum_shape_keys_offset_target'] = str(0)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)