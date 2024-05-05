"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit Material Data

"""

# Quick Material

def materialpoll(self, context):
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False
    elif not len(bpy.data.materials):
        self.poll_message_set("No Materials")
        return False
    elif obj.active_material is None:
        self.poll_message_set("No active Material")
        return False
    elif not func.poll_func.pinned_mesh_poll(self, context, False):
        return False
    return True


def materialslotpoll(self, context):
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False
    elif not len(obj.material_slots):
        self.poll_message_set("No Material Slots")
        return False
    elif not func.poll_func.pinned_mesh_poll(self, context, False):
        return False
    return True


class QuickMaterialAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_material_assignment"
    bl_label = "To Attribute from assignment"
    bl_description = "Converts Material assignent to Face Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return materialpoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "FACE_IS_MATERIAL_ASSIGNED"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_materials'] = str(list(bpy.data.materials).index(obj.active_material))
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickMaterialSlotAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_material_slot_assignment"
    bl_label = "To Attribute from slot assignment"
    bl_description = "Converts Material Slot assignent to Face Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        return materialslotpoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "FACE_IS_MATERIAL_SLOT_ASSIGNED"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_material_slots'] = str(obj.active_material_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickAllMaterialAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_all_from_material_assignment"
    bl_label = "All to Attribute from assignment"
    bl_description = "Converts Material assignent to Face Boolean Attributes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return materialpoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "FACE_IS_MATERIAL_ASSIGNED"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = True
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_materials'] = str(list(bpy.data.materials).index(obj.active_material))
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickAllMaterialSlotAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_all_from_material_slot_assignment"
    bl_label = "All to Attribute from slot assignment"
    bl_description = "Converts Material Slots assignent to Face Boolean Attributes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return materialslotpoll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "FACE_IS_MATERIAL_SLOT_ASSIGNED"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = True
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_material_slots'] = str(obj.active_material_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)