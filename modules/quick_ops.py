"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Convenience buttons and operator callers from ops.py
"""

import bpy
from . import ops
from . import func
from . import static_data

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


# Quick UV

class QuickUVMapToAttribute(bpy.types.Operator):
    # this is for pre blender 3.5
    bl_idname = "mesh.attribute_quick_from_uvmap"
    bl_label = "Convert UVMap to Vector 2D Attribute"
    bl_description = "Converts active UVMap to Vector 2D Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        obj = context.active_object

        if not obj:
            self.poll_message_set("No active object")
            return False
        elif obj.type != 'MESH':
            self.poll_message_set("Object is not a mesh")
            return False
        elif not len(obj.data.uv_layers):
            self.poll_message_set("No UVMaps")
            return False
        elif obj.data.uv_layers.active is None:
            self.poll_message_set("No active UVMap")
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        
        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "UVMAP"
        args['target_attrib_domain_enum'] = 'CORNER'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_uvmaps'] = str(obj.data.uv_layers.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)
    
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

# Quick Sculpt Masks

def sculpt_facemap_poll(self, context):
    obj = context.active_object

    if not obj:
        self.poll_message_set("No active object")
        return False
    elif obj.type != 'MESH':
        self.poll_message_set("Object is not a mesh")
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

        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
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
    

        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
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
        return True

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
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
    bl_label = "Overwrite"
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
            args['b_normalize_mask'] = prop_group.qops_sculpt_mode_mask_normalize
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
        return True
    

    def execute(self, context):
        prop_group = context.window_manager.MAME_GUIPropValues
        obj = context.active_object
        func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
        return apply_mask_attrib('REPLACE', inverted=True)

# Quick nodes


class QuickAttributeNode(bpy.types.Operator):
    bl_idname = "mesh.attribute_create_attribute_node"
    bl_label = "Create Attribute Node"
    bl_description = "Creates Attribute node in selected nodes editor"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # The area to create the node
    areaid: bpy.props.IntProperty(name="AreaID")
    windowid: bpy.props.IntProperty(name="windowid")
    area = None

    @classmethod
    def poll(self, context):
        obj =  bpy.context.active_object
        if not obj:
            self.poll_message_set("No active object")
            return False
        elif obj.type != 'MESH':
            self.poll_message_set("Object is not a mesh")
            return False
        elif not obj.data.attributes.active:
            self.poll_message_set("No active attribute")
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        attribute = obj.data.attributes.active
        self.area = bpy.context.window_manager.windows[self.windowid].screen.areas[self.areaid]
        node_tree_type = func.get_node_editor_type(self.area, return_enum=True)
        region = self.area.regions[3]
        node_tree = self.area.spaces[0].node_tree
        
        node_spawn_location = region.view2d.region_to_view(region.width / 2,  region.height / 2)
        # Widen the node if the name is long
        
        extra_width = max(0,(len(attribute.name) - 10) * 9)


        if node_tree_type == static_data.ENodeEditor.GEOMETRY_NODES:
            node = node_tree.nodes.new("GeometryNodeInputNamedAttribute")
            node.inputs[0].default_value = attribute.name
            node.data_type = static_data.attribute_data_types[attribute.data_type].geonodes_attribute_node_datatype
            node.width = node.width + extra_width
        elif node_tree_type == static_data.ENodeEditor.SHADER:
            node = node_tree.nodes.new("ShaderNodeAttribute")
            node.attribute_type = 'GEOMETRY'
            node.attribute_name = attribute.name
            node.width = node.width + extra_width
        # elif node_tree_type == static_data.ENodeEditor.ANIMATION_NODES:
        #     node = node_tree.nodes.new("an_GetCustomAttributeNode")
        #     node.inputs[1].value = attribute.name
        #     node.dataType = static_data.attribute_data_types[attribute.data_type].animnodes_attribute_node_datatype

        else:
            self.report({'ERROR'}, "Unsupported node group")
            return {'CANCELLED'}
        
        node.select = False
        node.location = node_spawn_location

        return {'FINISHED'}


# Select and deselect buttons


class SelectDomainButton(bpy.types.Operator):
    """
    Used in gui to select domains with non-zero value
    """
    bl_idname = "mesh.attribute_select_button"
    bl_label = "Select"
    bl_description = "Select attribute domains"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    deselect: bpy.props.BoolProperty(name="deselet", default=False)

    def execute(self, context):
        prop_group = context.object.MAME_PropValues
        select_nonzero = prop_group.val_select_non_zero_toggle

        dt = context.active_object.data.attributes.active.data_type
        params = {}
        params['b_deselect'] = self.deselect
        params['b_single_condition_vector'] = True
        params['b_use_color_picker'] =  False
        params['b_single_value_vector'] = False
        # select true booleans though
        params['attribute_comparison_condition_enum'] = 'NEQ' if (select_nonzero and dt != 'BOOLEAN') else 'EQ'
        params['b_string_case_sensitive'] = True
        params['color_value_type_enum'] = 'RGBA'
        params['vector_value_cmp_type_enum'] = 'AND'
        
        # compare all for vectors
        if static_data.attribute_data_types[dt].gui_prop_subtype in [static_data.EDataTypeGuiPropType.VECTOR, 
                                                                     static_data.EDataTypeGuiPropType.COLOR]:
            for i in range(0,len(static_data.attribute_data_types[dt].vector_subelements_names)):
                params[f'val_vector_{i}_toggle'] = True

        # do not compare alpha
        if static_data.attribute_data_types[dt].gui_prop_subtype in [static_data.EDataTypeGuiPropType.COLOR]:
            params['val_vector_3_toggle'] = False
        params['vec_0_condition_enum'] = 'NEQ' if select_nonzero else 'EQ'

        if select_nonzero:
            params[f'val_{dt.lower()}'] = func.get_attrib_default_value(datatype=dt)
        else:
            params[f'val_{dt.lower()}'] = getattr(prop_group, f'val_{dt.lower()}')

        return  bpy.ops.mesh.attribute_conditioned_select('EXEC_DEFAULT', **params)


    @classmethod
    def poll(self, context):
        return func.conditional_selection_poll(self, context)

class DeSelectDomainButton(bpy.types.Operator):
    """
    Used in gui to deselect domains with non-zero value
    """
    bl_idname = "mesh.attribute_deselect_button"
    bl_label = "Deselect"
    bl_description = "Deselect attribute domains"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        return  bpy.ops.mesh.attribute_select_button('EXEC_DEFAULT', 
                                                     deselect=True)

    @classmethod
    def poll(self, context):
        return func.conditional_selection_poll(self, context)