"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit Sculpt Mode Data

"""


# Quick Sculpt Masks

def sculpt_facemap_poll(self, context):
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False
    elif not func.poll_func.pinned_mesh_poll(self, context, False):
        return False
    return True


class QuickCurrentSculptMaskToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_current_sculpt_mask"
    bl_label = "Current Mask to Attribute"
    bl_description = "Converts Sculpt Mask to Float Vertex Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return sculpt_facemap_poll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = "Mask"
        args['domain_data_type_enum'] = "SCULPT_MODE_MASK"
        args['target_attrib_domain_enum'] = 'POINT'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = False
        args['b_enable_name_formatting'] = True
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickActiveAttributeToSculptMask(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_sculpt_mask_from_active_attribute"
    bl_label = "Active Attribute to Mask"
    bl_description = "Converts Active Mesh Attribute to Sculpt Mode Face Sets"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return sculpt_facemap_poll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['b_delete_if_converted'] = False
        args['data_target_enum'] = "TO_SCULPT_MODE_MASK"
        args['convert_to_domain_enum'] = 'POINT'
        args['enum_expand_sculpt_mask_mode'] = 'REPLACE'
        return bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT', **args)


class QuickSelectedInEditModeToSculptMask(bpy.types.Operator):
    bl_idname = "mesh.selected_in_edit_mode_to_sculpt_mode_mask"
    bl_label = "Mask from Edit Mode Selection (slow)"
    bl_description = "Converts selected domains in edit mode to mask"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return sculpt_facemap_poll(self, context)

    def execute(self, context):
        obj = context.active_object
        vals = np.zeros(len(obj.data.vertices), dtype=int)

        for i in func.obj_func.get_mesh_selected_domain_indexes(obj, 'POINT'):
            vals[i] = 1.0
        func.obj_func.set_mesh_data(obj, "TO_SCULPT_MODE_MASK", None, raw_data=vals, expand_sculpt_mask_mode='EXPAND', normalize_mask=True, invert_sculpt_mask=False)
        obj.data.update()
        return {'FINISHED'}


# Quick Face Sets

class QuickFaceSetsToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_face_sets"
    bl_label = "Face Sets to Attribute"
    bl_description = "Converts Face Sets to Integer Vertex Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return sculpt_facemap_poll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = "Face Set"
        args['domain_data_type_enum'] = "SCULPT_MODE_FACE_SETS"
        args['target_attrib_domain_enum'] = 'FACE'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = False
        args['b_enable_name_formatting'] = True
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickActiveAttributeToFaceSets(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_face_sets_from_attribute"
    bl_label = "Active Attribute to Face Sets"
    bl_description = "Converts Active Mesh Attribute to Sculpt Mode Face Sets"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        return sculpt_facemap_poll(self, context)

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['b_delete_if_converted'] = False
        args['data_target_enum'] = "TO_SCULPT_MODE_FACE_SETS"
        args['convert_to_domain_enum'] = 'FACE'
        return bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT', **args)