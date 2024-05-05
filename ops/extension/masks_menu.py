"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Sculpt Mode Attribute Masks Manager

"""

# Quick Sculpt Mode Menu

def apply_mask_attrib(mode:str, inverted=False):
            prop_group = bpy.context.window_manager.MAME_GUIPropValues
            args = {}
            args['b_delete_if_converted'] = False
            args['data_target_enum'] = "TO_SCULPT_MODE_MASK"
            args['convert_to_domain_enum'] = 'POINT'
            args['enum_expand_sculpt_mask_mode'] = mode
            args['b_invert_sculpt_mode_mask'] = inverted
            args['b_normalize_mask'] = prop_group.qops_sculpt_mode_mask_normalize
            return bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT', **args)


class QuickSculptModeApplyAttribute(bpy.types.Operator):
    """
    Used for add attribute button in sculpt mode menu bar extension.
    """

    bl_idname = "mesh.mame_attribute_sculpt_mode_apply"
    bl_label = "Replace"
    bl_description = "Converts selected attribute to mask or face set"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif (prop_group.enum_sculpt_mode_attribute_selector is None
                     or prop_group.enum_sculpt_mode_attribute_selector == 'NULL'):
            self.poll_message_set("Invalid attribute selected in menu")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.attribute_func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
        if prop_group.enum_sculpt_mode_attribute_mode_toggle == 'MASK':
            return apply_mask_attrib('REPLACE')
        elif prop_group.enum_sculpt_mode_attribute_mode_toggle == 'FACE_SETS':
            args = {}
            args['b_delete_if_converted'] = False
            args['data_target_enum'] = "TO_SCULPT_MODE_FACE_SETS"
            args['convert_to_domain_enum'] = 'FACE'
            return bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT', **args)


class QuickSculptModeExtendAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_extend"
    bl_label = "Add to mask"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif (prop_group.enum_sculpt_mode_attribute_selector is None
                     or prop_group.enum_sculpt_mode_attribute_selector == 'NULL'):
            self.poll_message_set("Invalid attribute selected in menu")
            return False
        elif prop_group.enum_sculpt_mode_attribute_mode_toggle != 'MASK':
            self.poll_message_set("Only supported for masks")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False

        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.attribute_func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
        return apply_mask_attrib('EXPAND')


class QuickSculptModeSubtractAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_subtract"
    bl_label = "Subtract from mask"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif (prop_group.enum_sculpt_mode_attribute_selector is None
                     or prop_group.enum_sculpt_mode_attribute_selector == 'NULL'):
            self.poll_message_set("Invalid attribute selected in menu")
            return False
        elif prop_group.enum_sculpt_mode_attribute_mode_toggle != 'MASK':
            self.poll_message_set("Only supported for masks")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.attribute_func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
        return apply_mask_attrib('SUBTRACT')


class QuickSculptModeRemoveAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_remove"
    bl_label = "Remove attribute"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif prop_group.enum_sculpt_mode_attribute_selector not in context.active_object.data.attributes:
            self.poll_message_set("This attribute does not exist on this mesh")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True



    def execute(self, context):
        # Toggle to object mode to change data
        bpy.ops.object.mode_set(mode='OBJECT')

        prop_group = context.window_manager.MAME_GUIPropValues
        attrib_name = prop_group.enum_sculpt_mode_attribute_selector
        obj = context.active_object

        # Remove the attribute
        attrib = obj.data.attributes[attrib_name]
        obj.data.attributes.remove(attrib)

        # Go back to sculpt mode
        bpy.ops.object.mode_set(mode='SCULPT')

        return {'FINISHED'}


class QuickSculptModeNewAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_new"
    bl_label = "New Attribute from current mask/face set"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues

        if prop_group.enum_sculpt_mode_attribute_mode_toggle == 'MASK':
            bpy.ops.mesh.attribute_quick_from_current_sculpt_mask()
        else:
            bpy.ops.mesh.attribute_quick_from_face_sets()
        # Set the new group in sculpt mode attribute selector
        prop_group.enum_sculpt_mode_attribute_selector = bpy.context.active_object.data.attributes.active.name

        return {'FINISHED'}


class QuickSculptModeOverwriteAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_overwrite"
    bl_label = "Overwrite Attribute"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif (prop_group.enum_sculpt_mode_attribute_selector is None
                     or prop_group.enum_sculpt_mode_attribute_selector == 'NULL'):
            self.poll_message_set("Invalid attribute selected in menu")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        current_attrib = prop_group.enum_sculpt_mode_attribute_selector

        if prop_group.enum_sculpt_mode_attribute_mode_toggle == 'MASK':
            args = {}
            args['attrib_name'] = current_attrib
            args['domain_data_type_enum'] = "SCULPT_MODE_MASK"
            args['target_attrib_domain_enum'] = 'POINT'
            args['b_batch_convert_enabled'] = False
            args['b_overwrite'] = True
            args['b_enable_name_formatting'] = True
            # args['b_normalize_mask'] = prop_group.qops_sculpt_mode_mask_normalize
            return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)
        else:
            args = {}
            args['attrib_name'] = current_attrib
            args['domain_data_type_enum'] = "SCULPT_MODE_FACE_SETS"
            args['target_attrib_domain_enum'] = 'FACE'
            args['b_batch_convert_enabled'] = False
            args['b_overwrite'] = True
            args['b_enable_name_formatting'] = True
            return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)


class QuickSculptModeApplyInvertedAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_apply_inverted"
    bl_label = "Apply Inverted"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Not a mesh")
            return False
        elif not context.active_object.mode == 'SCULPT' :
            self.poll_message_set("Not in sculpt mode")
            return False
        elif (prop_group.enum_sculpt_mode_attribute_selector is None
                     or prop_group.enum_sculpt_mode_attribute_selector == 'NULL'):
            self.poll_message_set("Invalid attribute selected in menu")
            return False
        elif prop_group.enum_sculpt_mode_attribute_mode_toggle != 'MASK':
            self.poll_message_set("Only supported for masks")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True


    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.attribute_func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
        return apply_mask_attrib('REPLACE', inverted=True)