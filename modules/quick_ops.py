import bpy

from . import ops
from . import func
from . import data
#
# Quick buttons
#

# Quick Shape Key

class QuickShapeKeyToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_shape_key"
    bl_label = "Convert to Vertex Vector Attribute"
    bl_description = "Converts active Shape Key to Vertex Vector Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickAllShapeKeyToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_all_shape_keys"
    bl_label = "Convert all to Vertex Vector Attributes"
    bl_description = "Converts all Shape Keys to Vertex Vector Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 
    
class QuickShapeKeyOffsetToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_offset_from_shape_key"
    bl_label = "Convert to Vertex Vector Attribute as offset"
    bl_description = "Converts active Shape Key offset to Vertex Vector Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickAllShapeKeyToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_all_shape_keys"
    bl_label = "Convert all to Vertex Vector Attributes as offsets"
    bl_description = "Converts all Shape Keys to Vertex Vector Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickAllShapeKeyOffsetToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_offset_from_all_shape_keys"
    bl_label = "Convert all to Vertex Vector Attributes as offsets"
    bl_description = "Converts all Shape Keys offsets to Vertex Vector Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

# Quick Vertex Groups

class QuickVertexGroupToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_vertex_group"
    bl_label = "Convert to Vertex Float Attribute"
    bl_description = "Converts active vertex group to Vertex Float Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 
    
class QuickAllVertexGroupToAttributes(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_all_vertex_groups"
    bl_label = "Convert all to Vertex Float Attributes"
    bl_description = "Converts all vertex groups to Vertex Float Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickVertexGroupAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_vertex_group_assignment"
    bl_label = "Convert to Vertex Boolean Attribute from assignment"
    bl_description = "Converts vertex group verte assignent to Vertex Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 
    
# Quick Material

class QuickMaterialAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_material_assignment"
    bl_label = "Convert to Face Boolean Attribute from assignment"
    bl_description = "Converts vertex group verte assignent to Vertex Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 
    
class QuickMaterialIndexToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_material_index"
    bl_label = "Convert to Face Boolean Attribute from assignment"
    bl_description = "Converts vertex group verte assignent to Vertex Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickMaterialSlotAssignmentToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_material_slot_assignment"
    bl_label = "Convert to Face Boolean Attribute from assignment"
    bl_description = "Converts vertex group verte assignent to Vertex Boolean Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

# Quick UV

# class QuickUVMapToAttribute(bpy.types.Operator):
#     # this is for pre blender 3.5
#     bl_idname = "mesh.attribute_quick_from_uvmap"
#     bl_label = "Convert UVMap to Vector 2D Attribute"
#     bl_description = "Converts active UVMap to Vector 2D Attribute"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         # check if its a mesh
#         return False

#     def execute(self, context):
#         return 
    
# class QuickAllUVMapToAttributes(bpy.types.Operator):
#     # this is for pre blender 3.5
#     bl_idname = "mesh.attribute_quick_from_all_uvmaps"
#     bl_label = "Convert all UVMaps to Vector 2D Attributes"
#     bl_description = "Converts all UVMaps to Vector 2D Attributes"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         # check if its a mesh
#         return False

#     def execute(self, context):
#         return 

# Quick Face Maps

# class QuickFaceMapAssignmentToAttribute(bpy.types.Operator):
#     # this is for pre blender 4.0
#     bl_idname = "mesh.attribute_quick_from_face_map"
#     bl_label = "Convert Face Map assignment to Boolean Face Attribute"
#     bl_description = "Convert assignment of active Face Map to Boolean Face Attribute"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         # check if its a mesh
#         return False

#     def execute(self, context):
#         return 
    
# class QuickFaceMapIndexToAttribute(bpy.types.Operator):
#     # this is for pre blender 4.0
#     bl_idname = "mesh.attribute_quick_from_face_map_index"
#     bl_label = "Convert Face Map index assignment to Integer Face Attribute"
#     bl_description = "Converts Face Map index assignment to Integer Face Attribute"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         # check if its a mesh
#         return False

#     def execute(self, context):
#         return 

# Quick Sculpt Masks

class QuickCurrentSculptMaskToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_current_sculpt_mask"
    bl_label = "Current Mask to Float Attribute"
    bl_description = "Converts Sculpt Mask to Float Vertex Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickActiveAttributeToSculptMask(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_sculpt_mask_from_active_attribute"
    bl_label = "Active Attribute to Mask"
    bl_description = "Converts Active Mesh Attribute to Sculpt Mode Face Sets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

# Quick Face Sets

class QuickFaceSetsToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_face_sets"
    bl_label = "Face Sets to Integer Attribute"
    bl_description = "Converts Face Sets to Integer Vertex Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickActiveAttributeToFaceSets(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_face_sets_from_attribute"
    bl_label = "Active Attribute to Face Sets"
    bl_description = "Converts Active Mesh Attribute to Sculpt Mode Face Sets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

# Quick Sculpt Mode Menu

class QuickSculptModeApplyAttribute(bpy.types.Operator):
    """
    Used for add attribute button in sculpt mode menu bar extension.
    """

    bl_idname = "mesh.mame_attribute_sculpt_mode_apply"
    bl_label = "Active Attribute to Mask/FaceSet"
    bl_description = "Converts Active Mesh Attribute to Sculpt Mode Face Sets or Mask"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        prop_group = context.object.MAME_PropValues
        return (context.active_object
                and context.active_object.mode == 'SCULPT' 
                and context.active_object.type == 'MESH'
                and (prop_group.enum_sculpt_mode_attribute_selector is not None
                     or prop_group.enum_sculpt_mode_attribute_selector is not 'NULL')
                )

    def execute(self, context):
        prop_group = context.object.MAME_PropValues
        obj = context.active_object
        print(prop_group.enum_sculpt_mode_attribute_selector)
        func.set_active_attribute(obj, prop_group.enum_sculpt_mode_attribute_selector)
        bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT',
                                                    enum_expand_sculpt_mask_mode ='REPLACE')
        return {'FINISHED'}

class QuickSculptModeExtendAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_extend"
    bl_label = "Active Attribute add to Mask/FaceSet"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickSculptModeSubtractAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_subtract"
    bl_label = "Active Attribute add to Mask/FaceSet"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickSculptModeRemoveAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_remove"
    bl_label = "Remove attribute from the selector"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        prop_group = context.object.MAME_PropValues
        return (context.active_object
                and context.active_object.mode == 'SCULPT' 
                and context.active_object.type == 'MESH'
                and hasattr(context.active_object.data.attributes, prop_group.enum_sculpt_mode_attribute_selector)
                )


    def execute(self, context):
        # Toggle to object mode to change data
        bpy.ops.object.mode_set(mode='OBJECT')

        prop_group = context.object.MAME_PropValues
        attrib_name = prop_group.enum_sculpt_mode_attribute_selector
        obj = context.active_object
        
        # Remove the attribute
        attrib = obj.data.attributes[attrib_name]
        obj.data.attributes.remove(attrib)

        # Go back to sculpt mode
        bpy.ops.object.mode_set(mode='SCULPT')

        # Set the selector to currently active attribute, if there is any
        # if not obj.data.attributes.active:
        #     attrib = obj.data.attributes[0]
        #     func.set_active_attribute(attrib)

        # prop_group.enum_sculpt_mode_attribute_selector = obj.data.attributes.active.name 
        return {'FINISHED'}

class QuickSculptModeNewAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_new"
    bl_label = "Active Attribute add to Mask/FaceSet"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return (context.active_object
                and context.active_object.mode == 'SCULPT' 
                and context.active_object.type == 'MESH')
    
    def execute(self, context):
        bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT',
                                 attrib_name='',
                                 domain_data_type="SCULPT_MODE_MASK",
                                 target_attrib_domain='POINT',
                                 batch_convert_enabled=False,
                                 b_overwrite=False,
                                 b_enable_name_formatting=True,
                                 auto_convert=False)
        
        # Set the new group in sculpt mode attribute selector
        prop_group = context.object.MAME_PropValues
        prop_group.enum_sculpt_mode_attribute_selector = context.active_object.data.attributes.active.name
    
        return {'FINISHED'}

class QuickSculptModeOverwriteAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_overwrite"
    bl_label = "Active Attribute add to Mask/FaceSet"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickSculptModeInvertAttribute(bpy.types.Operator):
    bl_idname = "mesh.mame_attribute_sculpt_mode_invert"
    bl_label = "Active Attribute add to Mask/FaceSet"
    bl_description = "asdfsadf"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 


#
# Quick nodes
#

# class QuickNamedAttributeNodeGN(bpy.types.Operator):
#     bl_idname = "mesh.attribute_create_named_attribute_gn"
#     bl_label = "Create Named Attribute Node (Geometry Nodes)"
#     bl_description = "Creates a Named Attribute node in active geometry nodes editor"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         # check if its a mesh
#         return False

#     def execute(self, context):
#         return 

# class QuickNamedAttributeNodeShader(bpy.types.Operator):
    bl_idname = "mesh.attribute_create_named_attribute_shader"
    bl_label = "Create Named Attribute Node (Shader)"
    bl_description = "Creates a Named Attribute node in active shader editor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 