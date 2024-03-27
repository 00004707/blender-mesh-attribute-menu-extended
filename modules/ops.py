"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
ops

All operators

"""

import bpy 
import colorsys
import bmesh
from . import func
from . import static_data
from . import etc
from bpy_types import bpy_types
from mathutils import Vector
import numpy as np
from . import gui

class AssignActiveAttribValueToSelection(bpy.types.Operator):
    """
    This operator will set active attribute value to values set in GUI or clear them to "zero" value.
    Operation is limited to edit mode selection
    """

    bl_idname = "object.set_active_attribute_to_selected"
    bl_label = "Assign Active Attribute Value To Selection in Edit Mode"
    bl_description = "Assigns active attribute value to selection in edit mode."
    bl_options = {'REGISTER', 'UNDO'}
    
    # The toggle to clear attribute value - set it's value to the zero value
    b_clear: bpy.props.BoolProperty(name="clear", default = False)

    # The toggle to enable face corner spilling to nearby face corners of selected vertices/edges/faces
    b_face_corner_spill_enable: bpy.props.BoolProperty(name="Face Corner Spill", 
                                                       default = False,
                                                       description="Allow setting value to nearby corners of selected vertices or limit it only to selected face",)

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        elif not context.active_object.mode  == 'EDIT' :
            self.poll_message_set("Not in edit mode")
            return False
        elif context.active_object.data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        elif not func.get_is_attribute_valid_for_manual_val_assignment(context.active_object.data.attributes.active)  :
            self.poll_message_set("Attribute is read-only or unsupported")
            return False
        
        return True

    def execute(self, context):
        etc.pseudo_profiler_init()
        obj = context.active_object
        active_attrib_name = obj.data.attributes.active.name 
        prop_group = context.object.MAME_PropValues
        mesh_selected_modes = bpy.context.scene.tool_settings.mesh_select_mode
        dt = obj.data.attributes[active_attrib_name].data_type

        if func.is_verbose_mode_enabled():
            print( f"Working on {active_attrib_name} attribute" )

        etc.pseudo_profiler("EXEC START")

        # Compatibility Check
        if not func.get_attribute_compatibility_check(obj.data.attributes[active_attrib_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}

        # Use bpy.ops.mesh_attribute_set()
        try:
            if (etc.get_blender_support((3,5,0))
                and not (dt == 'QUATERNION' and etc.get_preferences_attrib("set_attribute_raw_quaterion"))      # Operator will make sure the values are a valid quaternion
                and not (not prop_group.face_corner_spill and mesh_selected_modes[1])                               # Face corner spill feature is not supported by the operator
                and static_data.attribute_data_types[dt].bpy_ops_set_attribute_param_name is not None               # Strings are unsupported by this, oh well
                and not etc.get_preferences_attrib("disable_bpy_set_attribute")):                                   # Preferences toggle
                
                etc.pseudo_profiler("OPS_START")
                

                params = {}
                paramname = static_data.attribute_data_types[dt].bpy_ops_set_attribute_param_name
                params[paramname] = getattr(prop_group, f'val_{dt.lower()}')
                if func.is_verbose_mode_enabled():
                    print( f"Using ops.mesh_attribute_set()" )
                    # print(f"Setting value {prop_group.val_byte_color[:]}")
                bpy.ops.mesh.attribute_set(**params)
                
                etc.pseudo_profiler("OPS_END")
                return {"FINISHED"}
        except TypeError:
            if etc.get_blender_support((4,1,0)) and dt in ["INT32_2D", "QUATERNION", "FLOAT4X4"]:
                if func.is_verbose_mode_enabled():
                    print( f"Using ops.mesh_attribute_set() failed due to a blender bug, using pre 3.5 method")
        

        bpy.ops.object.mode_set(mode='OBJECT')
        etc.pseudo_profiler("OBJ MODE SW")
    
        

        attribute = obj.data.attributes[active_attrib_name] #!important

        # Get value from GUI
        if dt in static_data.attribute_data_types:
            
            gui_value = getattr(prop_group, f'val_{dt.lower()}')
            etc.pseudo_profiler("READ_ATTRIB")

            if type(gui_value) in [bpy_types.bpy_prop_array, Vector]:
                gui_value = tuple(gui_value)
            
            value = func.get_attribute_default_value(attribute) if self.b_clear else gui_value
            etc.pseudo_profiler("GET_DEFAULT_VAL")

            # Set the value
            func.set_attribute_value_on_selection(self, context, obj, attribute, value, face_corner_spill=self.b_face_corner_spill_enable)
            
            bpy.ops.object.mode_set(mode='EDIT')
        
            return {"FINISHED"}
        
        else:
            self.report({'ERROR', "Unsupported data type!"})
            bpy.ops.object.mode_set(mode='EDIT')
            return {"CANCELLED"}
          
class CreateAttribFromData(bpy.types.Operator):
    """
    This operator creates a new attribute from exisitng mesh data 
    """

    bl_label = 'Create From Mesh Data'
    bl_idname = 'mesh.attribute_create_from_data'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates attribute from mesh data, like seams or crease."
    
    # Main settings

    # The name of the created attribute.
    attrib_name: bpy.props.StringProperty(name="Attribute Name", default="", description="New attribute name. Leave blank for automatic name")

    # The source data to fill the created attribute
    domain_data_type_enum: bpy.props.EnumProperty(
        name="Domain Data",
        description="Select an option",
        items=func.get_source_data_enum_with_separators
    )

    # Optional selector for selecting the attribute domain, if source is available in multiple
    target_attrib_domain_enum: bpy.props.EnumProperty(
        name="Attribute Domain",
        description="Select an option",
        items=func.get_supported_domains_for_selected_mesh_data_source_enum_entry
    )

    # Enables batch mode to convert multiple mesh data to multiple attributes. Limited to selected mesh data that supports this function.
    b_batch_convert_enabled: bpy.props.BoolProperty(
        name="Batch Convert And Create Attributes", 
        description="Convert all vertex groups/shape keys/face maps/... at once", 
        default=False)
    
    # Switch "Offset From"<>"Offset to" when batch creating attributes from shape keys.
    b_offset_from_offset_to_toggle: bpy.props.BoolProperty(
        name="Set \"Offset to\" instead of \"Offset From\"", 
        description="", 
        default=False)
    
    # Overwrite toggle for attributes that already exist
    b_overwrite: bpy.props.BoolProperty(name="Overwrite", description="Overwrites the attribute if exists", default=False)

    # Description string used when hovering over the enable name formatting checkbox
    name_format_desc = """ Replaces wildcards with predefined names. using {uvmap} will replace it with current UVMap name.
• {domain} - Domain name
• {face_map} - Face map name
• {shape_key} - Shape key name, or name of the shape key that the offset is calculated to
• {shape_key_to} - Name of the shape key that the offset is calculated to
• {shape_key_from} - Name of the shape key that the offset is calculated from
• {vertex_group} - Vertex Group name
• {material} - Material name
• {material_slot} - Material slot index
• {uvmap} - UVMap name
• {index} - (Batch only) index of the processed element
"""
    # Toggle to enable name formatting by user with .format
    b_enable_name_formatting: bpy.props.BoolProperty(name="Enable Name Formatting (hover for info)", description=name_format_desc, default=True)

    # Data selectors
    enum_face_maps: bpy.props.EnumProperty(
        name="Face Map",
        description="Select an option",
        items=func.get_face_maps_enum
    )

    enum_material_slots: bpy.props.EnumProperty(
        name="Material Slot",
        description="Select an option",
        items=func.get_material_slots_enum
    )

    enum_materials: bpy.props.EnumProperty(
        name="Material",
        description="Select an option",
        items=func.get_materials_enum
    )

    enum_vertex_groups: bpy.props.EnumProperty(
        name="Vertex Group",
        description="Select an option",
        items=func.get_vertex_groups_enum
    )

    enum_shape_keys: bpy.props.EnumProperty(
        name="Shape Key",
        description="Select an option",
        items=func.get_shape_keys_enum
    )

    enum_shape_keys_offset_target: bpy.props.EnumProperty(
        name="Offset from",
        description="Select an option",
        items=func.get_shape_keys_enum
    )

    enum_uvmaps: bpy.props.EnumProperty(
        name="From UVMap",
        description="Select an option",
        items=func.get_uvmaps_enum
    )
    
    # Automatic Converter settings

    # Enable automatic converting of attribute to different type after creation
    b_auto_convert: bpy.props.BoolProperty(name="Convert Attribute", description="Auto converts created attribute to another domain or type", default=False)
    
    # Convert mode
    enum_attrib_converter_mode:bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=func.get_convert_attribute_modes_enum,
    )

    # The target domain to convert this attribute to
    enum_attrib_converter_domain:bpy.props.EnumProperty(
        name="Domain",
        description="Select an option",
        items=func.get_attribute_domains_enum,
    )

    # The target data type to convert this attribute to
    enum_attrib_converter_datatype: bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=func.get_attribute_data_types_enum,
    )

    def perform_user_input_test(self):
        """
        User input checks for valid mesh data and selections in GUI. Displays a message on failure to inform the user.
        """

        #check if selection even exists
        if not self.domain_data_type_enum in static_data.object_data_sources:
            self.report({'ERROR'}, f"Can't find this data source {self.domain_data_type_enum}. Contact developer.")
            return False

        # Check if the user has selected input data if applicable to specific sources:
        if self.domain_data_type_enum in ["FACE_FROM_FACE_MAP"]:
            if self.enum_face_maps == 'NULL':
                if not self.b_batch_convert_enabled:
                    self.report({'ERROR'}, f"No Face Map Selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No Face Maps. Nothing done")
                
                return False
                
    
        # material slots
        if self.domain_data_type_enum in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"]:
            if self.enum_material_slots == 'NULL':
                if not self.b_batch_convert_enabled:
                    self.report({'ERROR'}, f"No material slot selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No Material slots. Nothing done")

                return False
    
        # materials
        if self.domain_data_type_enum in ["FACE_IS_MATERIAL_ASSIGNED"]:
            if self.enum_materials == 'NULL':
                if not self.b_batch_convert_enabled:
                    self.report({'ERROR'}, f"No Materials assigned. Nothing done")
                else:
                    self.report({'ERROR'}, f"No Materials. Nothing done")
                
                return False
    
        # shape keys
        if self.domain_data_type_enum ==  "VERT_SHAPE_KEY_POSITION_OFFSET":

            if self.b_batch_convert_enabled:
                if not self.b_offset_from_offset_to_toggle and self.enum_shape_keys_offset_target == 'NULL':
                        self.report({'ERROR'}, f"Source shape key to get offset target is invalid. Nothing done")
                        return False

                if self.b_offset_from_offset_to_toggle and self.enum_shape_keys == 'NULL':
                    self.report({'ERROR'}, f"Target shape key to get offset from is invalid. Nothing done")
                    return False
                
            
        if self.domain_data_type_enum ==  "VERT_SHAPE_KEY_POSITION":
            if self.enum_shape_keys == 'NULL':
                if not self.b_batch_convert_enabled:
                    self.report({'ERROR'}, f"No shape key selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No shape keys. Nothing done")
                return False
        
        # vertex groups
        if self.domain_data_type_enum in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"]: # ???????????
            if self.enum_vertex_groups == 'NULL':
                if not self.b_batch_convert_enabled:
                    self.report({'ERROR'}, f"No vertex group selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No vertex groups. Nothing done")
                return False

        # UVMaps
        if self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", "PINNED_VERTICES_IN_UV_EDITOR", 'UVMAP']: 
            if self.enum_uvmaps == 'NULL':
                if not self.b_batch_convert_enabled:
                    self.report({'ERROR'}, f"No UVMap selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No UVMaps. Nothing done")
                return False


        # invalid domain enum for multiple choices
        if len(static_data.object_data_sources[self.domain_data_type_enum].domains_supported) > 1 and self.target_attrib_domain_enum == '':
            self.report({'ERROR'}, f"Invalid source domain. Nothing done")
            return False
        return True


    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        return True
    
    def execute(self, context):    

        obj = bpy.context.active_object
        attrib = None

        # Switch to object mode to modify data
        mode = obj.mode
        if mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Check for user input in dropdown menus for validity
        if not self.perform_user_input_test():
            bpy.ops.object.mode_set(mode=mode)
            return {'CANCELLED'}

        # Get default value if default was chosen
        if self.target_attrib_domain_enum =="DEFAULT" or self.target_attrib_domain_enum == "":
            self.target_attrib_domain_enum = static_data.object_data_sources[self.domain_data_type_enum].attribute_domain_on_default

        # Read prefixes and suffixes of automatic naming
        data_type = static_data.object_data_sources[self.domain_data_type_enum].data_type
        
        
        if func.is_verbose_mode_enabled():
            print(f"Batch mode supported & enabled: {not (not static_data.object_data_sources[self.domain_data_type_enum].batch_convert_support or not self.b_batch_convert_enabled) }")
        
        # [Batch mode off] Single assignment to single attribute
        if not static_data.object_data_sources[self.domain_data_type_enum].batch_convert_support or not self.b_batch_convert_enabled:
            
            def format_name(name:str):
                format_args = {
                    "domain": func.get_friendly_domain_name(self.target_attrib_domain_enum, plural=True), 
                    "face_map": func.get_face_maps_enum(self, context)[int(self.enum_face_maps)][1] if self.enum_face_maps != 'NULL' else None,
                    "shape_key": func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None, 
                    "shape_key_to": func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_target)][1] if self.enum_shape_keys_offset_target != 'NULL' else None, 
                    "shape_key_from": func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None, 
                    "vertex_group": func.get_vertex_groups_enum(self, context)[int(self.enum_vertex_groups)][1] if self.enum_vertex_groups != 'NULL' else None, 
                    "material": func.get_materials_enum(self, context)[int(self.enum_materials)][1] if self.enum_materials != 'NULL' else None, 
                    "material_slot": func.get_material_slots_enum(self, context)[int(self.enum_material_slots)][1] if self.enum_material_slots != 'NULL' else None,
                    "uvmap": func.get_uvmaps_enum(self, context)[int(self.enum_uvmaps)][1] if self.enum_uvmaps != 'NULL' else None
                }

                return name.format(**format_args) 
            
            # Automatic name formatting
            if self.attrib_name == "":
                name = static_data.object_data_sources[self.domain_data_type_enum].attribute_auto_name
                name = format_name(name)
            else:
                name = self.attrib_name
                if self.b_enable_name_formatting:
                    name = format_name(name)
            
            name = func.get_safe_attrib_name(obj, name) # naming the same way as vertex group will crash blender

            # Remove current attribute if overwrite is enabled
            if self.b_overwrite and name in obj.data.attributes:
                obj.data.attributes.remove(obj.data.attributes[name])

            attrib = obj.data.attributes.new(name=name, type=data_type, domain=self.target_attrib_domain_enum)
            obj_data = func.get_mesh_data(obj, 
                                        self.domain_data_type_enum, 
                                        self.target_attrib_domain_enum, 
                                        vg_index=self.enum_vertex_groups,
                                        sk_index=self.enum_shape_keys,
                                        sk_offset_index=self.enum_shape_keys_offset_target,
                                        fm_index=self.enum_face_maps,
                                        sel_mat=self.enum_materials,
                                        mat_index=self.enum_material_slots,
                                        uvmap_index=self.enum_uvmaps)
            if func.is_verbose_mode_enabled():
                print(f"Creating attribute from data: {obj_data}")
            
            # Assign new values to the attribute
            func.set_attribute_values(attrib, obj_data)

            # Convert to different type (optional)
            if self.b_auto_convert:
                func.convert_attribute(self, obj, name, mode=self.enum_attrib_converter_mode, 
                                               domain=self.enum_attrib_converter_domain, 
                                               data_type=self.enum_attrib_converter_datatype)
            func.set_active_attribute(obj, name)

        # [Batch mode on] Assign all of type to n amount of attributes 
        # This currently applies only to:
        # "VERT_IS_IN_VERTEX_GROUP", 
        # "VERT_FROM_VERTEX_GROUP", 
        # "VERT_SHAPE_KEY_POSITION_OFFSET", 
        # "VERT_SHAPE_KEY_POSITION",
        # "FACE_IS_MATERIAL_ASSIGNED", 
        # "FACE_IS_MATERIAL_SLOT_ASSIGNED", 
        # "FACE_FROM_FACE_MAP"
        # "SELECTED_VERTICES_IN_UV_EDITOR", 
        # "SELECTED_EDGES_IN_UV_EDITOR", 
        # "PINNED_VERTICES_IN_UV_EDITOR", 
        # 'UVMAP'
        else:
            if func.is_verbose_mode_enabled():
                print(f"Batch converting {self.domain_data_type_enum}, "\
                        f"element count: {func.get_all_mesh_data_indexes_of_type(obj, self.domain_data_type_enum)}")

            for element_index, element in enumerate(func.get_all_mesh_data_indexes_of_type(obj, self.domain_data_type_enum)):
                
                if func.is_verbose_mode_enabled():
                    print(f"Batch converting #{element}")

                vertex_group_name = None
                vg_index = None
                shape_key = None
                shape_key_to = None
                sk_index = None
                sk_offset_index = None
                material = None
                sel_mat = None
                material_slot = None
                mat_index = None
                face_map = None
                fm_index = None
                uvmap = None
                uvmap_index = None

                # case: vertex groups
                # VERT_IS_IN_VERTEX_GROUP: check for each group if vertex is in it 
                # VERT_FROM_VERTEX_GROUP: get vertex weight for each vertex group for each vertex
                # -> iterates over every vertex group
                if self.domain_data_type_enum in ['VERT_IS_IN_VERTEX_GROUP', "VERT_FROM_VERTEX_GROUP"]: 
                    vertex_group_name = func.get_vertex_groups_enum(self, context)[element][1]
                    vg_index = element

                # case: get shape key position for each shape key 
                elif self.domain_data_type_enum in ["VERT_SHAPE_KEY_POSITION"]:
                    shape_key = func.get_shape_keys_enum(self, context)[element][1]
                    sk_index = element
                    if func.is_verbose_mode_enabled():
                        print(f"Source is shape key POS ({shape_key}), \nFROM: {func.get_shape_keys_enum(self, context)[element]} ")
                      
                # case: get shape key offset from specific one
                elif self.domain_data_type_enum == 'VERT_SHAPE_KEY_POSITION_OFFSET':

                    # case: user wants to set offset from
                    if self.b_offset_from_offset_to_toggle:
                        shape_key = func.get_shape_keys_enum(self, context)[element][1]
                        shape_key_to = func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1]
                        sk_index = element
                        sk_offset_index = self.enum_shape_keys_offset_target

                    # case: user wants to set offset to
                    else:
                        shape_key = func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_target)][1]
                        shape_key_to = func.get_shape_keys_enum(self, context)[element][1]
                        sk_index = self.enum_shape_keys
                        sk_offset_index = element
                        

                    if func.is_verbose_mode_enabled():
                        print(f"Source is shape key offset, \n FROM: {func.get_shape_keys_enum(self, context)[element]} \n TO: {func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)]}")
                        
                # case: check for each material if it's assigned
                # -> iterates over every material
                elif self.domain_data_type_enum == "FACE_IS_MATERIAL_ASSIGNED":
                    if func.is_verbose_mode_enabled():
                        print(f"All materials: {func.get_materials_enum(self, context)}")
                    material = func.get_materials_enum(self, context)[element][1]
                    sel_mat = element    

                # case; check for each material slot if it's assigned
                # -> iterates over every material slot
                elif self.domain_data_type_enum == "FACE_IS_MATERIAL_SLOT_ASSIGNED":
                    material_slot = func.get_material_slots_enum(self, context)[element][1]
                    mat_index = element

                #case: check for each face map if it's assigned
                # -> iterates over every face map
                elif self.domain_data_type_enum == "FACE_FROM_FACE_MAP":
                    face_map = func.get_face_maps_enum(self, context)[element][1]
                    fm_index = element

                elif self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", "PINNED_VERTICES_IN_UV_EDITOR", 'UVMAP']:
                    uvmap = func.get_uvmaps_enum(self, context)[element][1]
                    uvmap_index = element

                def format_name_batch(xname:str):
                    format_args = {
                        "domain": func.get_friendly_domain_name(self.target_attrib_domain_enum, plural=True), 
                        "face_map": face_map,
                        "shape_key": shape_key, 
                        "shape_key_to": shape_key_to,
                        "shape_key_from": shape_key, 
                        "vertex_group": vertex_group_name, 
                        "material": material, 
                        "material_slot": material_slot,
                        "index": element_index,
                        "uvmap": uvmap
                    }
                    return xname.format(**format_args) 

                # Create formatted attribute name
                if self.attrib_name == "":
                    xname = static_data.object_data_sources[self.domain_data_type_enum].attribute_auto_name
                    xname = format_name_batch(xname)
                else:
                    xname = self.attrib_name
                    if self.b_enable_name_formatting:
                        xname = format_name_batch(xname)


                # Grab safe name for Vertex Groups to avoid blender crashing and possibly other cases in the future
                xname = func.get_safe_attrib_name(obj, xname) 

                # Remove current attribute if overwrite is enabled
                if self.b_overwrite and xname in obj.data.attributes:
                    obj.data.attributes.remove(obj.data.attributes[xname])
                
                # Create new attribute
                attrib = obj.data.attributes.new(name=xname, type=data_type, domain=self.target_attrib_domain_enum)

                # Fetch data
                args = {'vg_index': vg_index,
                        'sk_index': sk_index,
                        'sk_offset_index': sk_offset_index,
                        'fm_index': fm_index,
                        'sel_mat': sel_mat, 
                        'mat_index': mat_index,
                        'uvmap_index': uvmap_index
                        }
                obj_data = func.get_mesh_data(obj, 
                                        self.domain_data_type_enum, 
                                        self.target_attrib_domain_enum, 
                                        **args)
                
                # Store data in attribute
                func.set_attribute_values(attrib, obj_data)

                # Convert to different type (optional)
                if self.b_auto_convert:
                    func.convert_attribute(self, obj, attrib.name, mode=self.enum_attrib_converter_mode, 
                                               domain=self.enum_attrib_converter_domain, 
                                               data_type=self.enum_attrib_converter_datatype)

        obj.data.update()
        
        # Switch back to previous mode.
        bpy.ops.object.mode_set(mode=mode)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        
        # Make sure the enum is not empty for to_vgindex_weights_attribute_enum
        vwa = func.get_supported_domains_for_selected_mesh_data_source_enum_entry(self, context)
        if self.target_attrib_domain_enum not in [a[0] for a in vwa]:
            self.target_attrib_domain_enum = vwa[0][0]


        # get if the attrib supports batch conversion
        batch_convert_support = False if self.domain_data_type_enum == '' else static_data.object_data_sources[self.domain_data_type_enum].batch_convert_support

        row = self.layout

        # New attribute name
        row.prop(self, "attrib_name", text="Name")
        if self.attrib_name == '':
            row.label(text="Using auto-generated name", icon='INFO')
        else:
            row.label(text="") # occupy space to avoid resizing the window

        # Data to create the attribute from
        row.prop(self, "domain_data_type_enum", text="Data")
        
        # Source domain selector, if applicable to source attribute
        disabler = row.row()
        disabler.prop(self, "target_attrib_domain_enum", text="From")
        disabler.enabled = len(func.get_supported_domains_for_selected_mesh_data_source_enum_entry(self, context)) > 1

        
        # Specific data source GUI entries

        # face maps
        if self.domain_data_type_enum in ["FACE_FROM_FACE_MAP"] and not self.b_batch_convert_enabled:
            row.prop(self, "enum_face_maps", text="Face Map")
        
        # material slots
        elif self.domain_data_type_enum in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"] and not self.b_batch_convert_enabled:
            row.prop(self, "enum_material_slots", text="Material Slot")
        
        # materials
        elif self.domain_data_type_enum in ["FACE_IS_MATERIAL_ASSIGNED"] and not self.b_batch_convert_enabled:
            row.prop(self, "enum_materials", text="Material")
        
        # shape keys
        elif self.domain_data_type_enum == "VERT_SHAPE_KEY_POSITION_OFFSET" or (self.domain_data_type_enum == "VERT_SHAPE_KEY_POSITION" and not self.b_batch_convert_enabled):
            
            # Shape key "Offset From" and  "Offset To" selectors
            if self.domain_data_type_enum ==  "VERT_SHAPE_KEY_POSITION_OFFSET":

                if not self.b_batch_convert_enabled or (not self.b_offset_from_offset_to_toggle):
                    row.prop(self, "enum_shape_keys", text="Offset from")
                    
                if not self.b_batch_convert_enabled or self.b_offset_from_offset_to_toggle:
                    row.prop(self, "enum_shape_keys_offset_target", text="Offset to")
                
                # Batch convert toggle mode either to create multiple "offset from" attributes or mulitple "offset to" attributes
                if self.b_batch_convert_enabled:
                    row.prop(self, "b_offset_from_offset_to_toggle", text="Set \"Offset to\" instead of \"Offset From\"")

            # Simple shape key vertex position to attribute mode
            if self.domain_data_type_enum ==  "VERT_SHAPE_KEY_POSITION":
                row.prop(self, "enum_shape_keys", text="Shape Key")
                 
        # vertex groups
        elif self.domain_data_type_enum in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"] and not self.b_batch_convert_enabled:
            row.prop(self, "enum_vertex_groups", text="Vertex Group")
        
        # UVMap domain selection
        elif (self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", "PINNED_VERTICES_IN_UV_EDITOR", 'UVMAP'] and
                not self.b_batch_convert_enabled):
                row.prop(self, "enum_uvmaps", text="UV Map")
        else:
            row.label(text="") # occupy space to avoid resizing the window

        # convert all of type to attrib
        if batch_convert_support:
            row.prop(self, "b_batch_convert_enabled", text="Batch Convert All To Attributes")
        else:
            row.label(text="") # occupy space to avoid resizing the window

        # Overwrite toggle
        row.prop(self, "b_overwrite", text="Overwrite if exists")
        row.prop(self, "b_enable_name_formatting")
        
        # Automatic conversion to another type, toggleable
        row.prop(self, "b_auto_convert", text="Convert Attribute After Creation")
        if self.b_auto_convert:
            row.label(text="Conversion Options")
            row.prop(self, "enum_attrib_converter_mode", text="Mode")
            if self.enum_attrib_converter_mode == 'GENERIC':
                row.prop(self, "enum_attrib_converter_domain", text="Domain")
                row.prop(self, "enum_attrib_converter_datatype", text="Data Type")

class DuplicateAttribute(bpy.types.Operator):
    """
    Simply duplicates an attribute
    """

    bl_idname = "mesh.attribute_duplicate"
    bl_label = "Duplicate Attribute"
    bl_description = "Duplicate Active Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        elif context.active_object.data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode
        
        # Compatibility Check
        if not func.get_attribute_compatibility_check(obj.data.attributes[attrib_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}

        # All attribute actions should be performed in object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        src_attrib = obj.data.attributes[attrib_name] #!important

        new_attrib = obj.data.attributes.new(name=src_attrib.name, type=src_attrib.data_type, domain=src_attrib.domain)

        func.set_attribute_values(new_attrib, func.get_attribute_values(src_attrib, obj))
        
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

class InvertAttribute(bpy.types.Operator):
    """
    Inverts active attribute value, with edit mode selection support

    """

    bl_idname = "mesh.attribute_invert"
    bl_label = "Invert Attribute"
    bl_description = "Invert Active Attribute Value"
    bl_options = {'REGISTER', 'UNDO'}

    

    # Whether to perform this operation on selected domain in edit mode
    b_edit_mode_selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Affect only selected in edit mode",
        default=False
    )

    # The toggle to enable face corner spilling to nearby face corners of selected vertices/edges/faces
    b_face_corner_spill: bpy.props.BoolProperty(
        name="Face Corner Spill",
        description="Allow inverting value to nearby corners of selected vertices or limit it only to selected face",
        default=False
    )

    # The dropdown menu for invert modes for selected attribute.
    invert_mode_enum: bpy.props.EnumProperty(
        name="Invert Mode",
        description="Select an option",
        items=func.get_attribute_invert_modes
    )

    # Trick to show the "Subtract from one" as first dropdown entry for color attributes
    def invert_attrib_color_mode_enum(self, context):
        # reverse
        return func.get_attribute_invert_modes(self, context)[::-1]

    # The dropdown menu for inverting modes for selected color attributes
    color_invert_mode_enum: bpy.props.EnumProperty(
        name="Invert Mode",
        description="Select an option",
        items=invert_attrib_color_mode_enum
    )

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        elif context.active_object.data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        return True
    
    def execute(self, context):
        obj = context.active_object
        src_attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        # Compatibility Check
        if not func.get_attribute_compatibility_check(obj.data.attributes[src_attrib_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}


        bpy.ops.object.mode_set(mode='OBJECT')

        src_attrib = obj.data.attributes[src_attrib_name] # !important
        
        # get selected domain indexes
        selected = func.get_mesh_selected_domain_indexes(obj, src_attrib.domain, self.b_face_corner_spill)
        if func.is_verbose_mode_enabled():
            print(f"Selected domain indexes: {selected}")
        
        # No selection and selection mode is enabled?
        if not len(selected) and self.b_edit_mode_selected_only:
            self.report({'ERROR'}, f"No selection to perform the operations onto")
            bpy.ops.object.mode_set(mode=current_mode)
            return {'CANCELLED'}
        
        # # numbers:
        # else:
        prop_name = func.get_attribute_value_propname(src_attrib)
        
        storage = func.get_attribute_values(src_attrib, obj)
        
        # int just get and multiply by -1
        if src_attrib.data_type in ['INT','INT8']:
            src_attrib.data.foreach_get(prop_name, storage)
            storage = [-v if not self.b_edit_mode_selected_only or i in selected else v for i, v in enumerate(storage) ]
        
        # strings reverse them
        elif src_attrib.data_type in ['STRING']:
            storage = [string[::-1] if not self.b_edit_mode_selected_only or i in selected else string for i, string in enumerate(storage) ]

        # for floats just get it as there is multiple modes
        elif src_attrib.data_type in ['FLOAT']:
            src_attrib.data.foreach_get(prop_name, storage)
        
        # booleans just not them
        elif src_attrib.data_type =='BOOLEAN':
            src_attrib.data.foreach_get(prop_name, storage)
            storage = [not v if not self.b_edit_mode_selected_only or i in selected else v for i, v in enumerate(storage)]
        
        # vectors get them as a single list
        elif src_attrib.data_type in ['FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR', 'QUATERNION', 'INT32_2D']:
            storage = [val for vec in storage for val in vec]
            src_attrib.data.foreach_get(prop_name, storage)

        # invert modes for vectors and float
        if src_attrib.data_type in ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR', 'QUATERNION', 'INT32_2D']:
            invert_mode = self.color_invert_mode_enum if src_attrib.data_type in ['FLOAT_COLOR', 'BYTE_COLOR'] else self.invert_mode_enum

            #ah vectors, yes
            skip = len(func.get_attribute_default_value(src_attrib)) if not src_attrib.data_type == 'FLOAT' else 1
            if invert_mode == "MULTIPLY_MINUS_ONE":
                storage = [v * -1 if not self.b_edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)]
            elif invert_mode == "SUBTRACT_FROM_ONE":
                storage = [1-v if not self.b_edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)] 
            elif invert_mode == "ADD_TO_MINUS_ONE":
                storage = [-1+v if not self.b_edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)] 
        
        func.set_attribute_values(src_attrib, storage, flat_list=True)
        
        obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        row = self.layout
        obj = context.active_object

        # Show the drop-down menu for invert mode types
        prop = "invert_mode_enum" if context.active_object.data.attributes.active.data_type not in ['FLOAT_COLOR', 'BYTE_COLOR'] else "color_invert_mode_enum"
        sub_box = row.row()
        sub_box.enabled = len(func.get_attribute_invert_modes(self, context)) != 1
        sub_box.prop(self, prop, text="Invert Mode")
        
        # selected only
        if obj.mode =='EDIT':
            row.prop(self, "b_edit_mode_selected_only", text="Selected only")
            # spill face corners
            if context.active_object.data.attributes.active.domain == 'CORNER':
                row.prop(self, "b_face_corner_spill", text="Face Corner Spill")

class RemoveAllAttribute(bpy.types.Operator):
    """
    Removes all attributes
    """
    bl_idname = "mesh.attribute_remove_all"
    bl_label = "Remove All"
    bl_description = "Removes all attributes"
    bl_options = {'REGISTER', 'UNDO'}

    # Whether to include the UVMaps when removing attributes
    b_include_uvs: bpy.props.BoolProperty(
        name="Include UVMaps", 
        description="All Vector2D attributes stored in Face Corners", 
        default=False
        )
    
    # Whether to include color attributes when removing attributes
    b_include_color_attribs: bpy.props.BoolProperty(
        name="Include Color Attributes", 
        description="All Color attributes stored in Vertices or Face Corners", 
        default=False
        )
    
    # Whether to include attributes tagged as DONOTREMOVE
    b_include_all: bpy.props.BoolProperty(
        name="Include non-recommended", 
        description="Include attributes that you probably do not want to remove, like shade smooth.", 
        default=False
        )

    # Whether to include attributes starting with a dot
    b_include_hidden: bpy.props.BoolProperty(
        name="Include Hidden attributes", 
        description="Include hidden attributes starting with a dot in name", 
        default=False
        )
    
    b_include_sculpt_mask: bpy.props.BoolProperty(
        name="Include Sculpt Mask", 
        description=".sculpt_mask attribute", 
        default=False
        )
    

    #Collection with all datatypes filter toggles
    remove_datatype_filter: bpy.props.CollectionProperty(type = etc.GenericBoolPropertyGroup)

    #Collection with all domain filter toggles
    remove_domain_filter: bpy.props.CollectionProperty(type = etc.GenericBoolPropertyGroup)


    
    # Quick check if an attribute is an UVMap
    def is_uvmap(self, a):
        return a.domain == 'CORNER' and a.data_type == 'FLOAT2'

    # Quick check if an attribute is a color attribute
    def is_color_attrib(self, a):
        return (a.domain == 'CORNER' or a.domain == 'POINT') and (a.data_type == 'FLOAT_COLOR' or a.data_type == 'BYTE_COLOR') 
    
    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False

        # Check if there is any attibute that can be removed
        for a in context.active_object.data.attributes:
            types = func.get_attribute_types(a)
            editable = True
            for e in [static_data.EAttributeType.CANTREMOVE]:
                if e in types:
                    editable = False
                    break
            if editable:
                return True
            
        self.poll_message_set("No removable attributes")
        return False

    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        num = 0

        attrib_names = [a.name for a in obj.data.attributes]
        
        for name in attrib_names:
            
            # If the name is not in the attributes for some weird reason ignore.
            if name not in obj.data.attributes:
                continue
            
            a = obj.data.attributes[name]
            a_types = func.get_attribute_types(a)

            # If the attribute cannot be removed, ignore
            if static_data.EAttributeType.CANTREMOVE in a_types :
                continue
            conditions = []

            # Check if is an uvmap 
            conditions.append(self.b_include_uvs if self.is_uvmap(a) else True)

            # Check for color attributes
            conditions.append(self.b_include_color_attribs if self.is_color_attrib(a) else True)

            # Check if it is a sculpt mode mask
            if name == '.sculpt_mask' and etc.get_blender_support(static_data.defined_attributes['.sculpt_mask'].min_blender_ver):
                conditions.append(self.b_include_sculpt_mask)
            
            # Check if it's hidden
            else:
                conditions.append(self.b_include_hidden if static_data.EAttributeType.HIDDEN in a_types else True)

            # Check if it's non-recommended
            conditions.append(self.b_include_all if static_data.EAttributeType.DONOTREMOVE in a_types else True)
            
            # Check data type
            
            dt = obj.data.attributes[name].data_type
            allow = False
            for el in self.remove_datatype_filter:
                if el.id == dt:
                    allow = el.b_value
                    break
            conditions.append(allow)

            # Check domain
            domain = obj.data.attributes[name].domain
            allow = False
            for el in self.remove_domain_filter:
                if el.id == domain:
                    allow = el.b_value
                    break
            conditions.append(allow)

            if all(conditions):
                if func.is_verbose_mode_enabled():
                    print(f"Attribute removed - {a.name}: {a.domain}, {a.data_type}")
                obj.data.attributes.remove(a)
                num += 1
        
        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, (f"Removed {str(num)} attribute" + ("s" if num > 1 else "") if num else "None of attributes removed!"))
        return {'FINISHED'}

    def invoke(self, context, event):
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        list_elements = gui_prop_group.to_mesh_data_attributes_list

        # Get data type toggles 
        self.remove_datatype_filter.clear()
        for data_type in func.get_attribute_data_types():
            b = self.remove_datatype_filter.add()
            b.b_value = True
            b.name = func.get_friendly_data_type_name(data_type)
            b.id = data_type

        # Get domain toggles 
        self.remove_domain_filter.clear()
        for domain in func.get_attribute_domains():
            b = self.remove_domain_filter.add()
            b.b_value = True
            b.name = func.get_friendly_domain_name(domain)
            b.id = domain

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        
        row.label(text="Include")
        col = row.column(align=True)
        
        colrow = col.row(align=True)

        subcolprop = colrow.row(align=True)
        # subcolprop.enabled = bpy.app.version >= (3,5,0)
        subcolprop.prop(self, "b_include_uvs", text="UVMaps", toggle=True)
        colrow.prop(self, "b_include_color_attribs", text="Color Attributes", toggle=True)

        # Sculpt mode mask if supported
        if etc.get_blender_support(static_data.defined_attributes['.sculpt_mask'].min_blender_ver):
            colrow.prop(self, "b_include_sculpt_mask", text="Sculpt Mask", toggle=True)
        
        colrow = col.row(align=True)

        colrow.prop(self, "b_include_hidden", text="Hidden", toggle=True)
        colrow.prop(self, "b_include_all", text="Non-Recommended", toggle=True)
        
        
        col.label(text="Filter Domains")
        filter_row = col.row(align=True)
        filter_row = col.grid_flow(columns=4, even_columns=False, align=True)
        for boolprop in self.remove_domain_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)

        col.label(text="Filter Data Types")
        filter_row = col.grid_flow(columns=3, even_columns=False, align=True)
        for boolprop in self.remove_datatype_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)

class ConvertToMeshData(bpy.types.Operator):
    """
    Converts attribute to mesh data
    """
    bl_idname = "mesh.attribute_convert_to_mesh_data"
    bl_label = "Convert To Mesh Data"
    bl_description = "Converts attribute to vertex group, shape key, normals..."
    bl_options = {'REGISTER', 'UNDO'}


    # Setting the position attribute will not change the basis shape key, which might be unexpected.
    b_apply_to_first_shape_key: bpy.props.BoolProperty(name="Apply to first shape key too", default=True, description="With this disabled, it might produce result you did not expect")
    
    # Creates basis shape key when converting to shape keys, which is probably the expected result
    b_create_basis_shape_key: bpy.props.BoolProperty(name="Also create Basis shape key", default=True, description="Creates a basis shape key before converting")
    
    # Whether to remove the attribute after converting to mesh data
    b_delete_if_converted: bpy.props.BoolProperty(name="Delete after conversion", default=False)

    # Converts multiple attributes of this type at once. Limited to specific data targets with batch_convert_support set to true in static data
    b_convert_multiple: bpy.props.BoolProperty(name="Convert Multiple", default=False, description="Converts multiple attributes of this type at once")
    
    # Overwrites existing mesh data - Vertex Groups, Face Maps, Shape Keys, UVMaps...
    b_overwrite: bpy.props.BoolProperty(name="Overwrite", default=False, description="Overwrites existing mesh data - Vertex Groups, Face Maps, Shape Keys, UVMaps...")


    # The target to convert the active attribute to
    data_target_enum: bpy.props.EnumProperty(
        name="Target",
        description="Select an option",
        items=func.get_target_data_enum_with_separators
    )

    # The name of newly created mesh data, eg. vertex group or shape key. By default it is the name of the attribute itself.
    attrib_name: bpy.props.StringProperty(name="Name", default="")

    # The target domain to convert this attribute to. eg. Vertex Mean Bevel and Edge Mean Bevel
    convert_to_domain_enum: bpy.props.EnumProperty(
        name="Store in",
        description="Select an option",
        items=func.get_supported_domains_for_selected_mesh_data_target_enum_entry
    )

    # After converting to custom split normals to see the result auto smooth needs to be enabled.
    b_enable_auto_smooth: bpy.props.BoolProperty(name="Enable Auto Smooth",
                                               description="Custom split normals are visible only when Auto Smooth is enabled", 
                                               default=True)
    
    b_normalize_mask: bpy.props.BoolProperty(name="Normalize Mask Value",
                                               description="Make sure the mask value is between 0.0 and 1.0", 
                                               default=True)
    
    # The single float value to set the weight to all vertices when converting to vertex group index
    to_vgindex_weight: bpy.props.FloatProperty(name='Weight Value',
                                                          description="Weight value to apply to vertex group at index defined in this attribute",
                                                          default=1.0
                                                          )
    # The mode to use when converting to vertex group index
    to_vgindex_weight_mode_enum: bpy.props.EnumProperty(
        name="Weighting mode",
        description="Select an option",
        items=[("STATIC", "Use float value to weight", "Use predefined float value to weight vertices"),
               ("ATTRIBUTE", "Use attribute to weight", "Use float attribute to weight vertices")]
    )

    # The attribute to get weights from when converting to vertex group index
    to_vgindex_weights_attribute_enum: bpy.props.EnumProperty(
        name="Float Attribute",
        description="Select an option",
        items=func.get_vertex_weight_attributes_enum
    )
    
    # Toggle to enable other attribute types than float to show up in a to_vgindex_weights_attribute_enum
    b_vgindex_weights_only_floats: bpy.props.BoolProperty(name="Show only Float Attributes",
                                               description="Disabling this will show all attribute types", 
                                               default=True)

    # The UVMap to use
    uvmaps_enum: bpy.props.EnumProperty(
        name="UVMap",
        description="Select an option",
        items=func.get_uvmaps_enum
    )

    # Whether to invert the value of sculpt mask while converting
    b_invert_sculpt_mode_mask: bpy.props.BoolProperty(name="Invert Sculpt Mode Mask",
                                               description="Subtracts mask value from 1.0. The value is clamped in 0.0 to 1.0 values.", 
                                               default=False)

    # The mode to use when converting to sculpt mode mask
    enum_expand_sculpt_mask_mode: bpy.props.EnumProperty(
        name="Expand Mask Mode",
        description="Select an option",
        items=[("REPLACE", "Replace", "Replaces current mask to values from attribute"),
               ("EXPAND", "Expand", "Adds the values to current sculpt mask"),
               ("SUBTRACT", "Subtract", "Removes the values from current sculpt mask")]
    )

    def perform_user_input_test(self, obj, current_mode):    
        """ 
        Check for user input validity
        """

        input_invalid = False
        if self.data_target_enum == "TO_FACE_MAP_INDEX" and not len(obj.face_maps):
            self.report({'ERROR'}, "No Face Maps. Nothing done")
            input_invalid = True

        elif self.data_target_enum == "TO_MATERIAL_INDEX" and not len(obj.material_slots):
            self.report({'ERROR'}, "No material slots. Nothing done")
            input_invalid = True
        
        elif self.data_target_enum == "TO_VERTEX_GROUP_INDEX" and not len(obj.vertex_groups):
            self.report({'ERROR'}, "No vertex groups. Nothing done")
            input_invalid = True

        elif self.data_target_enum == "TO_VERTEX_GROUP_INDEX" and self.to_vgindex_weight_mode_enum == 'ATTRIBUTE' and self.to_vgindex_weights_attribute_enum =='NULL':
            self.report({'ERROR'}, "Invalid source weights attribute. Nothing done")
            input_invalid = True
        
        elif self.data_target_enum in ["TO_SELECTED_VERTICES_IN_UV_EDITOR", "TO_SELECTED_EDGES_IN_UV_EDITOR", "TO_PINNED_VERTICES_IN_UV_EDITOR"] and not len(obj.data.uv_layers):
            self.report({'ERROR'}, "No UVMaps. Nothing done")
            input_invalid = True
            print(self.data_target_enum)
        
        return not input_invalid

    def create_temp_converted_attrib(self, obj, convert_from_name:str, name_suffix:str, target_domain:str, target_data_type:str):
        """
        Copies the attribute and converts it to required type. Returns name of temporary converted attribute.
        """

        convert_from = obj.data.attributes[convert_from_name]
        if func.is_verbose_mode_enabled():
            print(f"Conversion required! Source: {convert_from.data_type} in  {convert_from.domain}, len {len(convert_from.data)}. Target: {self.convert_to_domain_enum} in {target_data_type}")
        
        # Make sure the new name is not starting with dot, as this will create a non-convertable internal attribute
        new_attrib_name = convert_from.name[1:] if convert_from.name.startswith('.') else convert_from.name 
        new_attrib_name += " " + name_suffix
        new_attrib = obj.data.attributes.new(name=new_attrib_name, type=convert_from.data_type, domain=convert_from.domain)
        new_attrib_name = new_attrib.name
        
        if func.is_verbose_mode_enabled():
            print(f"Created temporary attribute {new_attrib_name}")
        
        convert_from = obj.data.attributes[convert_from_name] # After the new attribute has been created, reference is invalid
        func.set_attribute_values(new_attrib, func.get_attribute_values(convert_from, obj))
        func.convert_attribute(self, obj, new_attrib.name, 'GENERIC', target_domain, target_data_type)
        if func.is_verbose_mode_enabled():
            print(f"Successfuly converted attribute ({new_attrib_name}), datalen = {len(obj.data.attributes[new_attrib_name].data)}")
        return new_attrib_name


    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        elif context.active_object.data.attributes.active is None:
            self.poll_message_set("No active attribute") 
            return False
        elif not func.get_attribute_compatibility_check(context.active_object.data.attributes.active):
            self.poll_message_set("Addon update required for this attribute type") 
            return False
        
        return True

    def execute(self, context):
        obj = context.active_object
        src_attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        # Check if user input is valid.
        if not self.perform_user_input_test(obj, current_mode):
            return {'CANCELLED'}

        # Get list of attributes to convert
        convert_attribute_list = []
        if not self.b_convert_multiple:
            convert_attribute_list.append(obj.data.attributes.active.name)
        else:
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            list_elements = gui_prop_group.to_mesh_data_attributes_list
            convert_attribute_list += [e.attribute_name for e in list_elements if e.b_select]
        
        bpy.ops.object.mode_set(mode='OBJECT')

        for src_attrib_name in convert_attribute_list:
            src_attrib = obj.data.attributes[src_attrib_name]

            # Store original name to preserve if removal is enabled and target is vertex group
            original_attrib_name = src_attrib_name

            # check if the source attribute can be removed here as references to attrib might change 
            can_remove = static_data.EAttributeType.CANTREMOVE not in func.get_attribute_types(obj.data.attributes[src_attrib_name])

            # rename the attribute if converting to vertex group with same name as attribute
            if self.data_target_enum in ['TO_VERTEX_GROUP'] and self.b_delete_if_converted and can_remove:
                src_attrib.name = func.get_safe_attrib_name(obj, src_attrib_name, check_attributes=True)
                src_attrib_name = src_attrib.name

            src_attrib_domain = src_attrib.domain
            src_attrib_data_type = src_attrib.data_type
            data_target_data_type = static_data.object_data_targets[self.data_target_enum].data_type
            data_target_compatible_domains = func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context)

            

            if func.is_verbose_mode_enabled():
                print(f"Converting attribute {src_attrib.name} to {self.data_target_enum}")

            # Add basis shape key if none present and enabled in gui
            if self.data_target_enum in ['TO_SHAPE_KEY'] and not hasattr(obj.data.shape_keys, 'key_blocks') and self.b_create_basis_shape_key:
                bpy.ops.object.shape_key_add(from_mix=False)
                if func.is_verbose_mode_enabled():
                    print("Creating basis shape key...")

            # Convert the attribute if required. Create a copy.
            domain_compatible = src_attrib_domain in [dom[0] for dom in data_target_compatible_domains] 
            data_type_compatible = src_attrib_data_type == data_target_data_type
            attrib_to_convert = src_attrib

            if not domain_compatible or not data_type_compatible:
                attribute_to_convert_name = self.create_temp_converted_attrib(obj, src_attrib.name, "temp", self.convert_to_domain_enum, data_target_data_type)
                attrib_to_convert = obj.data.attributes[attribute_to_convert_name]
            else:
                attribute_to_convert_name = src_attrib_name
            
            # If target is VERTEX GROUP INDEX, with attribute weight, make sure the weight attribute is float
            used_conveted_vgweight_attrib = False
            if self.to_vgindex_weight_mode_enum == 'ATTRIBUTE':
                vg_weight_attrib = obj.data.attributes[self.to_vgindex_weights_attribute_enum]
                if vg_weight_attrib.data_type != 'FLOAT' or vg_weight_attrib.domain != 'POINT':
                    if func.is_verbose_mode_enabled():
                        print(f"Source attribute for weights ({vg_weight_attrib.name}) is is not correct type, converting...")

                    vg_weight_attrib_name = self.create_temp_converted_attrib(obj, vg_weight_attrib.name, "vgweight", 'POINT', "FLOAT")
                    vg_weight_attrib =  obj.data.attributes[vg_weight_attrib_name]
                    used_conveted_vgweight_attrib = True
            else:
                vg_weight_attrib = None

            if func.is_verbose_mode_enabled():
                print(f"attribute -> data: {attrib_to_convert.name} -> {self.data_target_enum}")
            
            # Welp, new attribute might be added in vgweight convert and the reference to attrib_to_convert is gone...
            attrib_to_convert = obj.data.attributes[attribute_to_convert_name]

            args = {
                "new_data_name": original_attrib_name if self.attrib_name == "" else self.attrib_name,
                "enable_auto_smooth": self.b_enable_auto_smooth, 
                "apply_to_first_shape_key": self.b_apply_to_first_shape_key,
                "to_vgindex_weight": self.to_vgindex_weight,
                "to_vgindex_weight_mode": self.to_vgindex_weight_mode_enum,
                "to_vgindex_src_attrib": vg_weight_attrib,
                "uvmap_index": self.uvmaps_enum,
                "invert_sculpt_mask": self.b_invert_sculpt_mode_mask,
                "expand_sculpt_mask_mode": self.enum_expand_sculpt_mask_mode,
                "normalize_mask": self.b_normalize_mask
            }

            # Remove a dot to avoid potential crashes and un-resolveable name collisions
            args["new_data_name"] = args["new_data_name"] if not args["new_data_name"].startswith('.') else args["new_data_name"][1:]

            # Set mesh data
            func.set_mesh_data(obj, self.data_target_enum, 
                            attrib_to_convert, 
                            overwrite=self.b_overwrite,
                            **args
                            )
            
            
            # post-conversion cleanup
            if not domain_compatible or not data_type_compatible:
                obj.data.attributes.remove(obj.data.attributes[attribute_to_convert_name])

            if used_conveted_vgweight_attrib:
                obj.data.attributes.remove(obj.data.attributes[vg_weight_attrib_name])
            
            func.set_active_attribute(obj, src_attrib_name)
            # remove if user enabled
            if self.b_delete_if_converted and can_remove:
                obj.data.attributes.remove(obj.data.attributes[src_attrib_name])

        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        func.refresh_attribute_UIList_elements()
        func.configutre_attribute_uilist(True, True)
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    last_selected_data_target = None

    def draw(self, context):
        obj = context.active_object
        src_attrib = obj.data.attributes.active
        src_attrib_domain = src_attrib.domain
        src_attrib_data_type = src_attrib.data_type
        data_target_data_type = static_data.object_data_targets[self.data_target_enum].data_type
        data_target_compatible_domains = func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context)
        data_supports_multiple = static_data.object_data_targets[self.data_target_enum].batch_convert_support
        gui_prop_group = context.window_manager.MAME_GUIPropValues

        # Apply compatible domain by default or set first one in a list if it is not supported
        if self.last_selected_data_target != self.data_target_enum:
            self.last_selected_data_target = self.data_target_enum
            if src_attrib_domain in [e[0] for e in data_target_compatible_domains]:
                self.convert_to_domain_enum = src_attrib_domain
            else:
                self.convert_to_domain_enum = data_target_compatible_domains[0][0]

        # Make sure the enum is not empty for to_vgindex_weights_attribute_enum
        vwa = func.get_vertex_weight_attributes_enum(self, context)
        if self.to_vgindex_weights_attribute_enum not in [a[0] for a in vwa]:
            self.to_vgindex_weights_attribute_enum = vwa[0][0]

        domain_compatible = src_attrib_domain == self.convert_to_domain_enum
        data_type_compatible = src_attrib_data_type == data_target_data_type

        # Data target selector
        row = self.layout
        row.prop(self, "data_target_enum", text="Target")

        # Domain selector
        disabler = row.row()
        disabler.enabled = len(data_target_compatible_domains) > 1
        disabler.prop(self, "convert_to_domain_enum", text="Domain")
        
        # Data target toggles
        # ----------------------------------

        # Setting the position attribute will not change the basis shape key, which might be unexpected.
        if self.data_target_enum in ['TO_POSITION'] and hasattr(obj.data.shape_keys, 'key_blocks'):
            row.prop(self, 'b_apply_to_first_shape_key', text="Apply to \"Basis\" Shape Key as well")

        # Creates basis shape key when converting to shape keys, which is probably the expected result
        elif self.data_target_enum in ['TO_SHAPE_KEY'] and not obj.data.shape_keys:
            row.prop(self, 'b_create_basis_shape_key')
    
        # Custom name for face maps and vertex groups
        elif self.data_target_enum in ['TO_FACE_MAP', 'TO_VERTEX_GROUP', "TO_UVMAP", "TO_SHAPE_KEY"]:
            if not self.b_convert_multiple:
                row.prop(self, "attrib_name", text="Name")
            else:
                row.label(text="")
        
        # Show a toggle for enabling auto smooth to see the result auto smooth needs to be enabled.
        elif self.data_target_enum in ['TO_SPLIT_NORMALS']:
            if not etc.get_blender_support((4,1,0)) and not obj.data.use_auto_smooth:
                row.prop(self, 'b_enable_auto_smooth', text="Enable Auto Smooth (Required to preview)")
            else:
                row.label(text="")
        
        # Show modes to set the Vertex Group index
        elif self.data_target_enum in ['TO_VERTEX_GROUP_INDEX']:
            row.prop(self, 'to_vgindex_weight_mode_enum', text="Mode")
            # Show the dropdown menu to select the attribute with weights
            if self.to_vgindex_weight_mode_enum == "ATTRIBUTE":
                subrow = row.row()
                subrow2 = subrow.row()
                subrow2.ui_units_x = 3
                subrow2.prop(self, 'b_vgindex_weights_only_floats', text="Float Only" if self.b_vgindex_weights_only_floats else "All", toggle=True)
                subrow.prop(self, 'to_vgindex_weights_attribute_enum', text='')

            # Show slider to set the weight value
            else:
                row.prop(self, 'to_vgindex_weight')

        # UVMap selector
        elif self.data_target_enum in ["TO_SELECTED_VERTICES_IN_UV_EDITOR", "TO_SELECTED_EDGES_IN_UV_EDITOR", 'TO_PINNED_VERTICES_IN_UV_EDITOR']:
            row.prop(self, 'uvmaps_enum', text="UVMap")
        
        # Show options for sculpt mode mask conversion
        elif self.data_target_enum == 'TO_SCULPT_MODE_MASK':
            subrow = row.row()
            subrow.prop(self, "b_invert_sculpt_mode_mask")
            subrow.prop(self, 'b_normalize_mask')
            row.prop(self, "enum_expand_sculpt_mask_mode", text='Mode')
            
        
        # leave a space to avoid resizing the window
        else:
            row.label(text="") 

        toggles_row = row.row()
        sr = toggles_row.row()
        sr.prop(self, 'b_convert_multiple', toggle=True)
        sr.enabled = data_supports_multiple

        toggles_row.prop(self, 'b_overwrite', toggle=True)
        
        def remove_after_convert_menu(layout, alt_text = "", batch_conv_check_selected= False): # TODO
            subrow = layout.row()

            if not batch_conv_check_selected:
                en = static_data.EAttributeType.CANTREMOVE not in func.get_attribute_types(src_attrib)
                text = "Delete After conversion" if alt_text == "" else alt_text
                text = "Non-removeable attribute" if not en else text
            else:
                gui_prop_group = context.window_manager.MAME_GUIPropValues
                list_elements = gui_prop_group.to_mesh_data_attributes_list
                
                possible_to_remove_attrs = []
                for el in [e for e in list_elements if e.b_select]:
                    possible_to_remove_attrs.append(static_data.EAttributeType.CANTREMOVE not in func.get_attribute_types(obj.data.attributes[el.attribute_name]))
                
                en = True
                if not len(possible_to_remove_attrs) or all(possible_to_remove_attrs):
                    text = "Delete After conversion" if alt_text == "" else alt_text
                elif any(possible_to_remove_attrs):
                    text = "Delete all removeable after conversion"
                else:
                    text = "No removeable attributes" 
                    en = False
            
            subrow.label(text=text)
            subsr = subrow.row()
            subsr.ui_units_x = 4
            subsr.enabled = en
            subsr.prop(self, 'b_delete_if_converted', text="Delete", toggle=True)


        if self.b_convert_multiple and data_supports_multiple:
            # update table compatibility hightlighting

            comp_datatype = static_data.object_data_targets[self.data_target_enum].data_type
            func.set_attribute_uilist_compatible_attribute_type(self.convert_to_domain_enum, comp_datatype)

            # draw
            etc.draw_multi_attribute_select_uilist(row)

            # Conversion warning

            gui_prop_group = context.window_manager.MAME_GUIPropValues
            list_elements = gui_prop_group.to_mesh_data_attributes_list
            
            all_compatible = True
            for el in [e for e in list_elements if e.b_select]:
                if not el.b_domain_compatible or not el.b_data_type_compatible:
                    all_compatible = False
                    break
            col = self.layout.column()
            if not all_compatible:

                col.label(icon='ERROR', text=f"Some data will be converted. Result might be unexpected.")
            else:
                col.label(text=f"") # leave a space to not resize the window

            remove_after_convert_menu(col, "", True)


        else:

            # Data Type and Domains table
            # ----------------------------------

            box = self.layout.box()
            col = box.column(align=True)

            # Show titles
            row = col.row(align=True)
            row.label(text="")
            row.label(text="Source")
            row.label(text="Target")

            # Show first row comparing the Domains
            row = col.row(align=True)
            row.label(text="Domain")
            if domain_compatible:
                row.label(text=f"{func.get_friendly_domain_name(src_attrib_domain)}")
            else:
                row.label(text=f"{func.get_friendly_domain_name(src_attrib_domain)}", icon='ERROR')
            row.label(text=f"{func.get_friendly_domain_name(self.convert_to_domain_enum)}")
            
            # Show second row comparing the Data Types
            row = col.row(align=True)
            row.label(text="Data Type")
            if data_type_compatible:
                row.label(text=f"{func.get_friendly_data_type_name(src_attrib_data_type)}")
            else:
                row.label(text=f"{func.get_friendly_data_type_name(src_attrib_data_type)}", icon='ERROR')
            row.label(text=f"{func.get_friendly_data_type_name(data_target_data_type)}")


            # Showa additional box for comparing "To Vertex Group Index" weighting attribute data type and domains
            if self.data_target_enum in ['TO_VERTEX_GROUP_INDEX'] and self.to_vgindex_weight_mode_enum == "ATTRIBUTE":
                box = self.layout.box()
                col = box.column(align=True)

                # Show a row comparing the domains
                row = col.row(align=True)
                if self.data_target_enum in ['TO_VERTEX_GROUP_INDEX']:
                    row.label(text="Weight Domain")
                    if self.to_vgindex_weights_attribute_enum != "NULL":
                        src_weight_attrib = obj.data.attributes[self.to_vgindex_weights_attribute_enum]
                        static_val_mode = self.to_vgindex_weight_mode_enum == "STATIC"
                        friendly_domain = func.get_friendly_domain_name(src_weight_attrib.domain) if not static_val_mode else static_data.attribute_domains['POINT'].friendly_name

                        if src_weight_attrib.domain  != 'POINT' and not static_val_mode:
                            row.label(text=f"{friendly_domain}", icon='ERROR')
                        else:
                            row.label(text=f"{friendly_domain}")

                        row.label(text=f"{static_data.attribute_domains['POINT'].friendly_name}")

                # Show a row comparing the data types
                row = col.row(align=True)
                if self.data_target_enum in ['TO_VERTEX_GROUP_INDEX']:
                    row.label(text="Weight Data Type")
                    if self.to_vgindex_weights_attribute_enum != "NULL":
                        src_weight_attrib = obj.data.attributes[self.to_vgindex_weights_attribute_enum]
                        static_val_mode = self.to_vgindex_weight_mode_enum == "STATIC"
                        friendly_datatype = func.get_friendly_data_type_name(src_weight_attrib.data_type) if not static_val_mode else static_data.attribute_data_types["FLOAT"].friendly_name

                        if src_weight_attrib.data_type != 'FLOAT' and not static_val_mode:
                            row.label(text=f"{friendly_datatype}", icon='ERROR')
                        else:
                            row.label(text=f"{friendly_datatype}")

                        row.label(text=f"{static_data.attribute_data_types['FLOAT'].friendly_name}")
            
            # Occupy space if not applicable
            # else:
            #     row = self.layout.column(align=True)
            #     row.label(text="")
            #     row.label(text="")
            #     row.label(text="")

            # Info and error messages
            # ----------------------------------
            row = self.layout.column(align=True)
            
            # 1st row
            
            # Show error that the attribute will be converted if data type or domain is incompatible. Also for to vertex group index weighting attribute
            if not domain_compatible or not data_type_compatible or (
                (self.to_vgindex_weight_mode_enum == "ATTRIBUTE" and not static_val_mode) 
                and
                (src_weight_attrib.domain  != 'POINT' or src_weight_attrib.data_type != 'FLOAT')):

                row.label(icon='ERROR', text=f"Data will be converted. Result might be unexpected.")
            else:
                row.label(text=f"") # leave a space to not resize the window

            # 2nd row

            # Show a message that normals should be, well, normalized
            if self.data_target_enum in ['TO_SPLIT_NORMALS']:
                row.label(icon='INFO', text=f"Blender expects normal vectors to be normalized")

            # Inform user that the suffix will be added to avoid crashing of blender.
            if self.data_target_enum in ['TO_VERTEX_GROUP']:
                row.label(icon='INFO', text=f"Attributes & Vertex Groups cannot share names")
                remove_after_convert_menu(row, "Delete & use attribute name")
            else:
                row.label(text=f"") # leave a space to not resize the window
                remove_after_convert_menu(row)

class CopyAttributeToSelected(bpy.types.Operator):
    bl_idname = "mesh.attribute_copy"
    bl_label = "Copy Attribute to selected"
    bl_description = "Copies attribute from active mesh to selected meshes, by index"
    bl_options = {'REGISTER', 'UNDO'}

    # Whether to overwrite attributes that exist on target meshes
    b_overwrite: bpy.props.BoolProperty(name="Overwrite", default=True, description="Overwrite on target if exists, and is same data type or domain")
    
    # Whether to overwrite attributes that exist on target meshes but have different data type or domain
    b_overwrite_different_type: bpy.props.BoolProperty(name="Overwrite different type", default=True, description="For the attribute in target that has a different domain or data type")

    # What to fill the vertices/edges/faces/face corners with if the targets have more of them
    extend_mode_enum: bpy.props.EnumProperty(
        name="Extend Mode",
        description="If target has more vertices/faces/edges/face corners than source, what data should be stored inside of those?",
        items=[("LAST_VAL", "Repeat value at last index", ""),
        ("ZERO", "Fill with \"zero-value\"", ""),
        ("REPEAT", "Repeat", ""),
        ("PING_PONG", "Ping-Pong", "BlendeRRednelB"),
        ],
        default="REPEAT",
        
    )

    # Modes to select what to copy
    copy_what_enum: bpy.props.EnumProperty(
        name="Copy",
        description="Select attributes to copy",
        items=[("ACTIVE", "Active attribute", ""),
        ("ALL", "All attributes", ""),
        ("SELECT", "Multiple", ""),
        ],
        default="ACTIVE",
    )

    b_all_filter_internal: bpy.props.BoolProperty(name="Internal", default=False, description="Overwrite on target if exists, and is same data type or domain")
    b_all_filter_hidden: bpy.props.BoolProperty(name="Hidden", default=False, description="Overwrite on target if exists, and is same data type or domain")
    b_all_filter_autogenerated: bpy.props.BoolProperty(name="Auto-generated", default=False, description="Overwrite on target if exists, and is same data type or domain")
    b_all_filter_non_procedural: bpy.props.BoolProperty(name="Non-procedural", default=False, description="Overwrite on target if exists, and is same data type or domain")

    def get_attribute_data_length(self, obj, a):
        if a.domain == 'POINT':
            return len(obj.data.vertices)
        elif a.domain == 'EDGE':
            return len(obj.data.edges)
        elif a.domain == 'FACE':
            return len(obj.data.polygons)
        else:
            return len(obj.data.loops)

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        
        active_attrib = context.active_object.data.attributes.active

        if not active_attrib:
            self.poll_message_set("No active attribute")
            return False
        elif not len(context.selected_objects) > 1:
            self.poll_message_set("Select multiple objects") 
            return False
        elif not True not in [obj.type != 'MESH' for obj in bpy.context.selected_objects]:
            self.poll_message_set("One of selected objects is not a mesh")
        # Check if the attribute can be copied
        elif any([atype == static_data.EAttributeType.READONLY for atype in func.get_attribute_types(active_attrib)]):
            self.poll_message_set("This attribute is read-only")
            return False
        return True

    def execute(self, context):
        src_obj = context.active_object
        current_mode = src_obj.mode
        src_attrib_name = src_obj.data.attributes.active.name

        # Get attributes to copy
        if self.copy_what_enum == 'ACTIVE':
            attribute_names_to_copy = [src_obj.data.attributes.active.name]
        elif self.copy_what_enum == 'ALL':
            attribute_names_to_copy = [a.name for a in src_obj.data.attributes]
        else:
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            list_elements = gui_prop_group.to_mesh_data_attributes_list
            attribute_names_to_copy = [e.attribute_name for e in list_elements if e.b_select]

        valid_attrs = []
        errors = []
        # Check types
        for a_name in attribute_names_to_copy:

            types = func.get_attribute_types(src_obj.data.attributes[a_name])
            print(f"{a_name} : {types}")
            if static_data.EAttributeType.READONLY in types:
                errors.append([a_name, "Attribute is read-only"])

            if self.copy_what_enum == 'ALL':
                
                if not self.b_all_filter_internal and static_data.EAttributeType.INTERNAL in types:
                    continue
                elif not self.b_all_filter_non_procedural and static_data.EAttributeType.NOTPROCEDURAL in types:
                    continue
                elif not self.b_all_filter_autogenerated and static_data.EAttributeType.AUTOGENERATED in types:
                    continue
                elif not self.b_all_filter_hidden and static_data.EAttributeType.HIDDEN in types:
                    continue
            
            valid_attrs.append(a_name)

        attribute_names_to_copy = valid_attrs

        if len(attribute_names_to_copy) == 0:
            self.report({'ERROR'},  "No valid attributes to copy")

        bpy.ops.object.mode_set(mode='OBJECT')

        for sel_obj in [sel_obj for sel_obj in bpy.context.selected_objects if sel_obj.type =='MESH' and sel_obj is not src_obj]:
            for src_attrib_name in attribute_names_to_copy:
                src_attrib = src_obj.data.attributes[src_attrib_name] # !important
                a_vals = func.get_attribute_values(src_attrib, src_obj)

                # get size of the source attribute domain
                source_size = self.get_attribute_data_length(src_obj, src_attrib)

                sel_obj_attr = None
            
                # check if present in target mesh
                if src_attrib_name in [a.name for a in sel_obj.data.attributes]:
                    if func.is_verbose_mode_enabled():
                        print(f"Attribute {src_attrib.name} exists on target")
                    sel_obj_attr = sel_obj.data.attributes[src_attrib_name]

                    # overwrite if present?
                    if not self.b_overwrite:
                        continue
                    
                    #overwrite different type?
                    not_same_type = sel_obj_attr.domain != src_attrib.domain or sel_obj_attr.data_type != src_attrib.data_type
                    if not_same_type and not self.b_overwrite_different_type:
                        if func.is_verbose_mode_enabled():
                            print(f"Attribute {src_attrib.name} is not the same type as {sel_obj_attr.name}, {sel_obj_attr.domain}!={src_attrib.domain} or {sel_obj_attr.data_type}!={src_attrib.data_type}")
                        continue
                    
                    # remove current if overwriting
                    elif not_same_type:
                        sel_obj.data.attributes.remove(sel_obj_attr)

                else:
                    sel_obj_attr = sel_obj.data.attributes.new(name=src_attrib_name, type=src_attrib.data_type, domain=src_attrib.domain)
                    
                # size check

                # check if the target mesh has different amount of faces/verts/etc.
                target_size = self.get_attribute_data_length(sel_obj, sel_obj_attr)

                if sel_obj_attr.domain == 'POINT':
                    target_size = len(sel_obj.data.vertices)
                elif sel_obj_attr.domain == 'EDGE':
                    target_size = len(sel_obj.data.edges)
                elif sel_obj_attr.domain == 'FACE':
                    target_size = len(sel_obj.data.polygons)
                else:
                    target_size = len(sel_obj.data.loops)
                
                # case: target is larger
                if target_size > source_size:
                    
                    # Fill extra with single value
                    if self.extend_mode_enum not in ["REPEAT", "PING_PONG"]: 
                        
                        # With value on last index
                        if self.extend_mode_enum =='LAST_VAL':
                            fill_value = [a_vals[-1]]

                        # With 'zero' value
                        elif self.extend_mode_enum =='ZERO':
                            fill_value = func.get_attribute_default_value(src_attrib)
                            fill_value = [fill_value]

                        target_a_vals = a_vals + (fill_value * (target_size-source_size))
                    
                    # Fill extra with non-single value
                    else:
                        times = target_size - source_size

                        # Repeat from start
                        if self.extend_mode_enum =="REPEAT":
                            target_a_vals = a_vals * times
                        
                        # Repeat but from end to start then from start to end
                        elif self.extend_mode_enum == "PING_PONG":
                            target_a_vals = []
                            for t in range(0, times):
                                if t%2:
                                    target_a_vals += a_vals[::-1]
                                else:
                                    target_a_vals += a_vals

                        target_a_vals = target_a_vals[:target_size]

                # case: target is smaller
                elif target_size < source_size:
                    target_a_vals = a_vals[:target_size]
                
                # case: target is same size
                else:
                    target_a_vals = a_vals

                func.set_attribute_values(sel_obj_attr, target_a_vals)

                sel_obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)

        if len(errors):
            errors = [f"Copy failed for {e[0]} attribute: {e[1]}" for e in errors]
            gui.set_message_box_function(gui.draw_error_list)
            gui.set_message_box_extra_data(errors)

            bpy.ops.window_manager.mame_message_box(message="Cannot copy some of the attributes", custom_draw=True, width=700)

        return {'FINISHED'}

    def draw(self, context):
        row = self.layout
        row.label(text="Overwrite")
        subrow = row.row(align=False)
        subrow.prop(self, "b_overwrite", text="Existing", toggle=True)
        subrow.prop(self, "b_overwrite_different_type", text="Different domain/data type", toggle=True)
        row.label(text="Extend values mode for larger meshes")
        row.prop(self, "extend_mode_enum", text="")

        row.label(text="Copy")
        row.prop(self, "copy_what_enum", text="")
        if self.copy_what_enum == 'ALL':
            col = row.column(align=True)
            col.label(text="Include")
            rc = col.row(align=True)
            rc.prop(self, 'b_all_filter_hidden', toggle=True)
            rc.prop(self, 'b_all_filter_internal', toggle=True)
            
            rc = col.row(align=True)
            rc.prop(self, 'b_all_filter_autogenerated', toggle=True)
            rc.prop(self, 'b_all_filter_non_procedural', toggle=True)

        elif self.copy_what_enum == 'SELECT':
            etc.draw_multi_attribute_select_uilist(row)

    def invoke(self, context, event):
        func.refresh_attribute_UIList_elements()
        func.configutre_attribute_uilist(False,False)
        return context.window_manager.invoke_props_dialog(self)

class ConditionalSelection(bpy.types.Operator):
    bl_idname = "mesh.attribute_conditioned_select"
    bl_label = "Select in edit mode by condition"
    bl_description = "Select mesh domain by attribute value with specified conditions"
    bl_options = {'REGISTER', 'UNDO'}

    # Whether to deselect the domain that meets the condition
    b_deselect: bpy.props.BoolProperty(name="Deselect", default=False)

    # Whether to use single condition instead for each of the vector sub elements
    b_single_condition_vector: bpy.props.BoolProperty(name="Single Condition", default=False)

    # Whether to use color picker for color values
    b_use_color_picker: bpy.props.BoolProperty(name="Use Color Picker", default=False)

    # Whether to use single value instead of individual for each of vector sub values
    b_single_value_vector: bpy.props.BoolProperty(name="Single Value", default=False)

    # All conditions for attributes containing numeric values
    attribute_comparison_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum_for_property
    )
    
    # Whether to check strings with case sensitivity
    b_string_case_sensitive: bpy.props.BoolProperty(
        name="Case sensitive", 
        description="Is \"BLENDER\" different than \"blEnDer\"?", 
        default=False
        )

    # Toggle between comparing RGB or HSV values for color attributes.
    color_value_type_enum: bpy.props.EnumProperty(
        name="Color Mode",
        description="Select an option",
        items=[
            ("RGBA", "RGB + Alpha", ""),
            ("HSVA", "HSV + Alpha", ""),
        ],
        default="RGBA"
    )

    # The mode to check individual vector float values with. Either all of the values need to meet the conditions or one of them.
    vector_value_cmp_type_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("AND", "meeting all above conditions (AND)", "All of the conditions above need to be met"),
            ("OR", "meeting any of above conditions (OR)", "Any of the conditions above need to be met"),
        ],
        default="AND"
    )

    # ALL GUI INPUT BOXES
    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_float_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_boolean: bpy.props.BoolProperty(name="Boolean Value", default=False)
    val_float2: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    if etc.get_blender_support(static_data.attribute_data_types['INT8'].min_blender_ver, static_data.attribute_data_types['INT8'].unsupported_from_blender_ver):
        val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_float_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_byte_color: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if etc.get_blender_support(static_data.attribute_data_types['INT32_2D'].min_blender_ver, static_data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))
    if etc.get_blender_support(static_data.attribute_data_types['QUATERNION'].min_blender_ver, static_data.attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
        val_quaternion: bpy.props.FloatVectorProperty(name="Quaternion Value", size=4, default=(1.0,0.0,0.0,0.0))

    # Toggles for enabling comparing the individual vector/color values

    val_vector_0_toggle: bpy.props.BoolProperty(name="X", default=True)
    val_vector_1_toggle: bpy.props.BoolProperty(name="Y", default=True)
    val_vector_2_toggle: bpy.props.BoolProperty(name="Z", default=True)
    val_vector_3_toggle: bpy.props.BoolProperty(name="W", default=True)

    # The comparision modes between each of vector/color values

    vec_0_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum_for_property,
    )
    vec_1_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum_for_property,
    )
    vec_2_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum_for_property,
    )
    vec_3_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum_for_property,
    )


    @classmethod
    def poll(self, context):
        return func.conditional_selection_poll(self, context)
    
    def execute(self, context):
        if func.is_verbose_mode_enabled():
            print(f"conditional selection on attrib: {context.active_object.data.attributes.active}")

        obj = context.active_object
        current_mode = obj.mode
        
        attribute_name = obj.data.attributes.active.name
        bpy.ops.object.mode_set(mode='OBJECT')
        attrib = obj.data.attributes[attribute_name]

        condition = self.attribute_comparison_condition_enum
        comparison_value = None
        attrib_data_type = attrib.data_type
        case_sensitive_comp = False
        filtered_indexes = []
        
        def debug_print():
            print(f"""ConditionalSelectionTrigger
Cond: {condition}
CompVal: {comparison_value}
CmpType: {self.vector_value_cmp_type_enum}
DataType: {attrib_data_type}
CaseSensitive: {self.b_string_case_sensitive}
FiltIndex: {filtered_indexes}
VecSingleVal: {self.b_single_value_vector}
VecSingleCondition: {self.b_single_condition_vector}""")

        

        def compare_each_vector_dimension_indexes(vals_list, mode='AND'):
            """
            Compares each dimension of vals_list input if all of them contain that index (AND), or any of them (OR)
            """
            if mode == 'AND':
                common = np.array(vals_list[0], dtype=int)
                # check 2nd and higher dimension
                for i in range(1, len(vals_list)):
                    common = np.intersect1d(common, vals_list[i])
                return common
            
            elif mode == 'OR':
                r = []
                for dimension in vals_list:
                    r += dimension
                return np.unique(r)

        
        gui_prop_subtype = static_data.attribute_data_types[attrib_data_type].gui_prop_subtype
        
        #case 1: single number/value
        if gui_prop_subtype in [static_data.EDataTypeGuiPropType.SCALAR,
                                static_data.EDataTypeGuiPropType.BOOLEAN,
                                static_data.EDataTypeGuiPropType.STRING]:
            comparison_value = getattr(self, f'val_{attrib_data_type.lower()}')
            
            filtered_indexes = func.get_filtered_indexes_by_condition(func.get_attribute_values(attrib, obj), 
                                                                      condition, 
                                                                      comparison_value, 
                                                                      self.b_string_case_sensitive)

            
        # case 2: vectors/colors
        elif gui_prop_subtype in [static_data.EDataTypeGuiPropType.VECTOR,
                                  static_data.EDataTypeGuiPropType.COLOR]:
            vals_to_cmp = []
            filtered_indexes = []
            src_data = np.array(func.get_attribute_values(attrib, obj))
            use_hsv = self.color_value_type_enum == 'HSVA' and gui_prop_subtype == static_data.EDataTypeGuiPropType.COLOR
            
            if use_hsv:
                for i, subelement in enumerate(src_data):
                    if func.is_verbose_mode_enabled():
                        print("HSV mode enabled, converting all values to HSV")
                    src_data[i] = func.color_vector_to_hsv(subelement)
            
            # for each dimension of a vector
            for i in range(0, len(src_data[0])):
                if getattr(self, f'val_vector_{i}_toggle'):
                    condition = getattr(self, f'vec_0_condition_enum' if self.b_single_condition_vector else f'vec_{i}_condition_enum') 
                    comparison_value = getattr(self, f"val_{attrib_data_type.lower()}")[0] if self.b_single_value_vector else getattr(self, f"val_{attrib_data_type.lower()}")[i]
                    
                    srgb_convert = attrib.data_type == 'BYTE_COLOR'
                    if func.is_verbose_mode_enabled():
                        print(f"Checking vector[{i}], condition: {condition}, to value {comparison_value}")
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([vec[i] for vec in src_data], condition, comparison_value, vector_convert_to_srgb=srgb_convert))
            
            filtered_indexes = compare_each_vector_dimension_indexes(vals_to_cmp, self.vector_value_cmp_type_enum)

        if func.is_verbose_mode_enabled():
            debug_print()

        
        func.set_selection_or_visibility_of_mesh_domain(obj, attrib.domain, filtered_indexes, not self.b_deselect)

        bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):

        obj = context.active_object
        attribute_name = obj.data.attributes.active.name
        attribute = obj.data.attributes.active

        layout = self.layout
        dt = attribute.data_type
        domain = attribute.domain
        e_datatype = static_data.EAttributeDataType[dt]
        gui_prop_subtype = static_data.attribute_data_types[dt].gui_prop_subtype

        # For anything that holds a single value
        if gui_prop_subtype in [static_data.EDataTypeGuiPropType.SCALAR,
                            static_data.EDataTypeGuiPropType.STRING,
                            static_data.EDataTypeGuiPropType.BOOLEAN]:

            grid = layout.row(align=True)
            grid.prop(self, 'b_deselect', text=f"Select {func.get_friendly_domain_name(domain, True)}" if not self.b_deselect else f"Deselect {func.get_friendly_domain_name(domain, True)}", toggle=True, invert_checkbox=True) 
            grid.prop(self, "attribute_comparison_condition_enum", text="")

            # Get different text on value field
            if e_datatype == static_data.EAttributeDataType.STRING:
                text = ''
            elif e_datatype == static_data.EAttributeDataType.BOOLEAN:
                text = 'True' if self.val_boolean else 'False'
            else:
                text = "Value"

            grid.prop(self, f"val_{dt.lower()}", text=text, toggle=True)
            if e_datatype == static_data.EAttributeDataType.STRING:
                layout.prop(self, "b_string_case_sensitive", text="Not Case Sensitive" if not self.b_string_case_sensitive else "Case Sensitive", toggle=True)
        
        # For vectors of any type
        elif gui_prop_subtype in [static_data.EDataTypeGuiPropType.VECTOR, static_data.EDataTypeGuiPropType.COLOR]:
            row = layout.row(align=True)

            if gui_prop_subtype == static_data.EDataTypeGuiPropType.COLOR:
                row.prop_tabs_enum(self, "color_value_type_enum")
            
            col = layout.column(align=True)

            # Single condition/value toggles
            row = col.row(align=True)
            subrow = row.row(align=True)
            subrow.ui_units_x = 3
            subrow.label(text="") # leave a space
            row.prop(self, f"b_single_condition_vector", toggle=True)
            subrow = row.row(align=True)
            if not self.b_use_color_picker:
            #subrow.enabled = 
                subrow.prop(self, f"b_single_value_vector", toggle=True)
            else:
                subrow.label(text="")

            if gui_prop_subtype == static_data.EDataTypeGuiPropType.COLOR and self.color_value_type_enum == 'HSVA':
                    v_subelements = ['H','S','V','A']
            else:
                v_subelements = static_data.attribute_data_types[dt].vector_subelements_names 
            
            row2 = col.row(align=True)

            # Toggles
            row3 = row2.row(align=True)
            subrow = row3.column(align=True)
            for el in range(0, len(func.get_attribute_default_value(attribute))):
                subrow.ui_units_x = 3
                subrow.prop(self, f"val_vector_{el}_toggle", text=f"{v_subelements[el].upper()}", toggle=True)
            
            # Conditions
            row3 = row2.row(align=True)
            subrow = row3.column(align=True)

            for el in range(0, len(func.get_attribute_default_value(attribute))):
                disable_cond = not (el != 0 and self.b_single_condition_vector)
                disabler_row = subrow.row()
                if (getattr(self, f'val_vector_{el if not disable_cond else 0}_toggle') if not disable_cond else True) and disable_cond:
                    disabler_row.prop(self, f"vec_{el}_condition_enum", text="")
            
            # Values
            row3 = row2.row(align=True)
            subrow = row3.column(align=True)

            if not self.b_use_color_picker:
                for el in range(0, len(func.get_attribute_default_value(attribute))):
                    disable_cond = not (el != 0 and self.b_single_value_vector)
                    disabler_row = subrow.row()
                    if disable_cond:
                        disabler_row.prop(self, f"val_{dt.lower()}", text=f" ", index=el if disable_cond else 0)


            else:
                for el in range(0, len(func.get_attribute_default_value(attribute))):
                    subrow.prop(self, f"val_{dt.lower()}", text="")
            
            if gui_prop_subtype == static_data.EDataTypeGuiPropType.COLOR:
                row = col.row(align=True)
                subrow = row.row(align=True)
                subrow.ui_units_x = 3
                subrow.label(text="") # leave a space
                row.label(text="")
                row.prop(self, f"b_use_color_picker", toggle=True)
            
            
            row = layout.row(align=True)
            subrow = row.row(align=True)
            subrow.prop(self, 'b_deselect', text=f"Select {func.get_friendly_domain_name(domain, True)}" if not self.b_deselect else f"Deselect {func.get_friendly_domain_name(domain, True)}", toggle=True, invert_checkbox=True)   
            subrow.ui_units_x = 5
            row.prop(self, 'vector_value_cmp_type_enum', text="")

class AttributeResolveNameCollisions(bpy.types.Operator):
    """
    Adds suffix to attributes with colliding names
    """

    bl_idname = "mesh.attribute_resolve_name_collisions"
    bl_label = "Resolve name collisions"
    bl_description = "Renames attributes to avoid name collisions"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False  
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Selected object is not a mesh")
            return False
        elif not len(context.active_object.data.attributes):
            self.poll_message_set("No attributes")
            return False

        return True


    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        restricted_names = []

        # get vertex groups name, if any
        vg_names = [vg.name for vg in obj.vertex_groups]
        restricted_names += vg_names

        # get UVMap names, for blender 3.4 or lower
        if etc.get_blender_support(minver_unsupported=(3,5,0)):
            uvm_names = [uv.name for uv in obj.data.uv_layers]
            restricted_names += uvm_names

        # rename those, get by index, by name is fucky wucky
        renamed = 0
        failed = 0
        enumerate(obj.data.attributes)
        for i, a in enumerate(obj.data.attributes):
            if func.is_verbose_mode_enabled():
                print(f"{a} {i}")
                
            if obj.data.attributes[i].name in restricted_names:
                atypes = func.get_attribute_types(obj.data.attributes[i])

                is_removeable = not bool(len([atype for atype in atypes if atype in [static_data.EAttributeType.HIDDEN, static_data.EAttributeType.CANTREMOVE, static_data.EAttributeType.READONLY]]))


                renamed +=1
                j = 0
                while obj.data.attributes[i].name in restricted_names:
                    if (not is_removeable):
                        failed += 1
                        break
                    j += 1
                    obj.data.attributes[i].name = str(obj.data.attributes[i].name) + "." + str(j).zfill(3)
        
        if failed > 0:
            self.report({'WARNING'}, f"Renamed {str(renamed)}, cannot rename {str(failed)}")
        elif renamed == 0:
            self.report({'INFO'}, f"No name collisions found")
        else:
            self.report({'INFO'}, f"Renamed {str(renamed)} attribute" + ("s" if renamed > 1 else ""))

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

class ReadValueFromSelectedDomains(bpy.types.Operator):
    """
    Reads the active attribute value from selected domains (absolute if single domain, average if multiple), and sets it in GUI
    """

    bl_idname = "mesh.attribute_read_value_from_selected_domains"
    bl_label = "Sample from selected domains"
    bl_description = "Reads the attribute value under selected domains and sets it in GUI"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.mode == 'EDIT' :
            self.poll_message_set("Not in edit mode")
            return False
        elif context.active_object.data.attributes.active is None :
            self.poll_message_set("No active attribute")
            return False
        elif not context.active_object.data.attributes.active.data_type in static_data.attribute_data_types :
            self.poll_message_set("Data type is not yet supported!")
            return False
        elif bool(len([atype for atype in func.get_attribute_types(context.active_object.data.attributes.active) if atype in [static_data.EAttributeType.NOTPROCEDURAL]])) :
            self.poll_message_set("This attribute is unsupported (Non-procedural)")
            return False
        
        return True
    
    def execute(self, context):
        
        obj = context.active_object
        active_attribute_name = obj.data.attributes.active.name
        
        # Compatibility Check
        if not func.get_attribute_compatibility_check(obj.data.attributes[active_attribute_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        attribute = obj.data.attributes[active_attribute_name]
        prop_group = context.object.MAME_PropValues
        domain = obj.data.attributes[active_attribute_name].domain
        dt = attribute.data_type

        domain_indexes = func.get_mesh_selected_domain_indexes(obj, domain, prop_group.face_corner_spill)

        if not len(domain_indexes):
            self.report({'ERROR'}, f"No selected {func.get_friendly_domain_name(domain)}")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}

        # Get the value to set in GUI
        if dt in ['STRING', 'BOOLEAN']:
            # get the value from first index of selection
            if len(domain_indexes) > 1:
                self.report({'WARNING'}, f"It's best to select single {func.get_friendly_domain_name(domain)} instead to always get expected result for {func.get_friendly_data_type_name(dt)}s")
            attribute_value = getattr(obj.data.attributes[active_attribute_name].data[domain_indexes[0]], func.get_attribute_value_propname(attribute))
        else:
            # Get average for numeric


            # get default value to calc the avg
            attribute_value = func.get_attribute_default_value(attribute)
            if type(attribute_value) == list:
                    attribute_value = tuple(attribute_value)

            # get the total
            for vi in domain_indexes:
                val = getattr(obj.data.attributes[active_attribute_name].data[vi], func.get_attribute_value_propname(attribute))
                
                if type(val) in [bpy_types.bpy_prop_array, Vector]:
                    val = tuple(val)
                    attribute_value = tuple(vv+attribute_value[i] for i, vv in enumerate(val))
                else:
                    attribute_value += val

            # and the avg
            if type(attribute_value) == tuple:
                attribute_value = tuple(tv/len(domain_indexes) for tv in attribute_value)
            else:
                attribute_value /= len(domain_indexes)
        
        # Get int for ints
        if dt in ['INT']:
            attribute_value = int(round(attribute_value))

        # Set the attribute value in GUI
        setattr(prop_group, f'val_{dt.lower()}', attribute_value)

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class RandomizeAttributeValue(bpy.types.Operator):
    bl_idname = "mesh.attribute_randomize_value"
    bl_label = "Randomize Value"
    bl_description = "Sets attribute value to random value"
    bl_options = {'REGISTER', 'UNDO'}

    b_on_selection: bpy.props.BoolProperty(name="Only Selected", 
                                           default=True,
                                           description='Set random values only on selection in edit mode')
    
    b_face_corner_spill: bpy.props.BoolProperty(name="Face Corner Spill", 
                                                default=False,
                                                description="Allow setting random value to nearby corners of selected vertices or limit it only to selected face")
    
    b_single_random_value: bpy.props.BoolProperty(name="Single random value to all", 
                                                  default=False,
                                                  description="By default every single domain will have other random value. Enable this to select a single random value and assign it to all domains")
    
    

    # Probability that the random boolean will be true, in percent
    boolean_probability: bpy.props.FloatProperty(name="Probablity", default=50.0, min=0.0, max=100.0, subtype='PERCENTAGE',
                                                 description="Probability of random value to be True")

    # Integer values
    int_val_min:bpy.props.IntProperty(name="Min", default=0, description="Minimum Integer Value")
    int_val_max:bpy.props.IntProperty(name="Max", default=100, description="Maximum Integer Value")
    
    # 8-Bit Integer
    if etc.get_blender_support(static_data.attribute_data_types['INT8'].min_blender_ver, static_data.attribute_data_types['INT8'].unsupported_from_blender_ver):
        int8_val_min:bpy.props.IntProperty(name="Min", default=-128, min=-128, max=127, description="Minimum 8-bit Integer Value")
        int8_val_max:bpy.props.IntProperty(name="Max", default=127, min=-128, max=127, description="Maximum 8-bit Integer Value")
    
    # Float values
    float_val_min: bpy.props.FloatProperty(name="Min", default=0.0, description="Minimum Float Value")
    float_val_max: bpy.props.FloatProperty(name="Max", default=1.0, description="Maximum Float Value")

    # Vector (3D) values
    float_vector_val_min:bpy.props.FloatVectorProperty(name="Min", size=3, default=(0.0,0.0,0.0), description="Minumum Float Vector Value")
    float_vector_val_max:bpy.props.FloatVectorProperty(name="Max", size=3, default=(1.0,1.0,1.0), description="Maximum Float Vector Value")
    
    # Vector 2D values
    float2_val_min:bpy.props.FloatVectorProperty(name="Vector 2D Random Min", size=2, default=(0.0,0.0), description="Minimum Vector2D Value")
    float2_val_max:bpy.props.FloatVectorProperty(name="Vector 2D Random Max", size=2, default=(1.0,1.0), description="Maximum Vector2D Value")
    
    # 2D Integer Vector
    if etc.get_blender_support(static_data.attribute_data_types['INT32_2D'].min_blender_ver, static_data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        int32_2d_val_min: bpy.props.IntVectorProperty(name="Min", size=2, default=(0,0), description="Minimum 2D Integer Vector Value")
        int32_2d_val_max: bpy.props.IntVectorProperty(name="Max", size=2, default=(100,100), description="Maximum 2D Integer Vector Value")

    # String values 
    val_string: bpy.props.StringProperty(name="Only specified characters", default="", description="The characters to use to randomize the value")
    b_string_capital: bpy.props.BoolProperty(name="Capital letters", default=True, description="Whether to use the CAPITAL letters")
    b_string_lowercase: bpy.props.BoolProperty(name="Lowercase letters", default=True, description="Whether to use lowercase letters")
    b_string_numbers: bpy.props.BoolProperty(name="Numbers", default=False, description="Whether to use numbers")
    b_string_specials: bpy.props.BoolProperty(name="Special characters", default=False, description="Whether to use special characters like #$%^&")
    string_val_min:bpy.props.IntProperty(name="Min Length", default=0, min=0)
    string_val_max:bpy.props.IntProperty(name="Max Length", default=10, min=0)
    b_use_specified_characters: bpy.props.BoolProperty(name="Use specific characters", 
                                                  default=False,
                                                  description="Use specific characters in the characters field")
    # Quaternion values
    if etc.get_blender_support(static_data.attribute_data_types['QUATERNION'].min_blender_ver, static_data.attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
        quaternion_val_min: bpy.props.FloatVectorProperty(name="Min", size=4, default=(-1.0,-1.0,-1.0,-1.0), description="Minimum Quaternion Value")
        quaternion_val_max: bpy.props.FloatVectorProperty(name="Max", size=4, default=(1.0,1.0,1.0,1.0), description="Maximum Quaternion Value")
    
    # Color values
    color_randomize_type: bpy.props.EnumProperty(
        name="Color Randomize Type",
        description="Select an option",
        items=[
            ("RGBA", "RGB + Alpha", "RGBA"),
            ("HSVA", "HSV + Alpha", "HSVA"),
        ],
        default="RGBA"
    )
    b_use_color_picker: bpy.props.BoolProperty(name="Use Color Picker", 
                                                  default=False,
                                                  description="Use color picker instead of float values")

    float_color_val_min:bpy.props.FloatVectorProperty(name="Min", size=4, default=(0.0,0.0,0.0,1.0), subtype='COLOR', min=0.0, max=1.0, description="Minimum Color Values")
    float_color_val_max:bpy.props.FloatVectorProperty(name="Max", size=4, default=(1.0,1.0,1.0,1.0), subtype='COLOR', min=0.0, max=1.0, description="Maximum Color Values")

    byte_color_val_min:bpy.props.FloatVectorProperty(name="Min", size=4, default=(0.0,0.0,0.0,1.0), subtype='COLOR', min=0.0, max=1.0, description="Minimum Color Values")
    byte_color_val_max:bpy.props.FloatVectorProperty(name="Max", size=4, default=(1.0,1.0,1.0,1.0), subtype='COLOR', min=0.0, max=1.0, description="Maximum Color Values")

    # Color and vector toggles
    val_vector_0_toggle: bpy.props.BoolProperty(name="Vector X", default=True)
    val_vector_1_toggle: bpy.props.BoolProperty(name="Vector Y", default=True)
    val_vector_2_toggle: bpy.props.BoolProperty(name="Vector Z", default=True)
    val_vector_3_toggle: bpy.props.BoolProperty(name="Vector W", default=True)

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Selected object is not a mesh")
            return False
        elif context.active_object.data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        elif not context.active_object.data.attributes.active.data_type in static_data.attribute_data_types :
            self.poll_message_set("Data type is not yet supported!")
            return False
        
        # elif bool(len([atype for atype in func.get_attribute_types(context.active_object.data.attributes.active) if atype in [data.EAttributeType.NOTPROCEDURAL]])) :
        #     self.poll_message_set("This attribute is unsupported (Non-procedural)")
        #     return False
        return True

    def gui_values_check(self, context):
        active_attribute = context.active_object.data.attributes.active
        dt = active_attribute.data_type
        e_dt = static_data.EAttributeDataType[dt]
        
        # Strings check
        if e_dt == static_data.EAttributeDataType.STRING:
            if self.b_use_specified_characters:
                return bool(len(self.val_string))
            else:
                len_valid = (self.string_val_max - self.string_val_min) > 0 
                random_types_valid = any(self.b_string_lowercase,
                                         self.b_string_capital,
                                         self.b_string_numbers,
                                         self.b_string_specials)
                if not len_valid:
                    self.report({"ERROR"}, "Invalid string length")
                    return False
                elif not random_types_valid:
                    self.report({"ERROR"}, "No random character types selected")
                    return False
                
        # Vectors/colors check
        elif static_data.attribute_data_types[dt].gui_prop_subtype == static_data.EDataTypeGuiPropType.VECTOR:
            any_toggle_on = []
            for i in range(0, len(static_data.attribute_data_types[dt].vector_subelements_names)):
                any_toggle_on.append(getattr(self, f'val_vector_{i}_toggle'))
            
            if not any(any_toggle_on):
                self.report({"ERROR"}, "No selected vector/color subelements to randomize")
                return False

        # SELECTION CHECK IS IN EXECUTE TO AVOID RUNNING EXPENSIVE FUNCTIONS TWICE
        return True

    def execute(self, context):
        obj = context.active_object
        active_attribute_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        # Compatibility Check
        if not func.get_attribute_compatibility_check(obj.data.attributes[active_attribute_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        attribute = obj.data.attributes[active_attribute_name]
        prop_group = context.object.MAME_PropValues
        domain = obj.data.attributes[active_attribute_name].domain
        dt = attribute.data_type
        
        # General checks:

        # Check user input validity
        if not self.gui_values_check(context):
            return {'CANCELLED'}

        # Do not assign on selection if not in edit mode
        if current_mode != 'EDIT':
            self.b_on_selection = False

        # Avoid executing code for face corner spill
        if domain != 'CORNER' and not self.b_on_selection:
            self.b_face_corner_spill = False

        # Clear the string to not trigger any code
        if not self.b_use_specified_characters:
            self.val_string = ""

        # Actual function code:

        # Get domain ids for selection
        if self.b_on_selection:
            on_domains = func.get_mesh_selected_domain_indexes(obj, domain, self.b_face_corner_spill)
            if not len(on_domains):
                self.report({"ERROR"}, "No selection in edit mode. (\"on selected\" mode was used)")
                bpy.ops.object.mode_set(mode=current_mode)
                return {'CANCELLED'}

        else:
            on_domains = np.arange(0, len(attribute.data))

        # Get values set in UI
        rnd_min = None
        rnd_max = None
        e_dt = static_data.EAttributeDataType[dt]
        if e_dt in [static_data.EAttributeDataType.FLOAT,
                    static_data.EAttributeDataType.INT,
                    static_data.EAttributeDataType.INT8,
                    static_data.EAttributeDataType.INT32_2D,
                    static_data.EAttributeDataType.FLOAT2,
                    static_data.EAttributeDataType.FLOAT_COLOR,
                    static_data.EAttributeDataType.FLOAT_VECTOR,
                    static_data.EAttributeDataType.BYTE_COLOR,
                    static_data.EAttributeDataType.QUATERNION,
                    static_data.EAttributeDataType.STRING]:
            rnd_min = getattr(self, f"{dt.lower()}_val_min")
            rnd_max = getattr(self, f"{dt.lower()}_val_max")
        
        
        # Read current values
        storage = func.get_attribute_values(attribute, obj)
        if func.is_verbose_mode_enabled():
            print(f"Current values:{np.array(storage)}")

        # Get random values list
        rnd_vals = func.get_random_attribute_of_data_type(context, 
                                                              dt, 
                                                              len(on_domains),
                                                              no_list=False,
                                                              randomize_once=self.b_single_random_value,
                                                              range_min=rnd_min,
                                                              range_max=rnd_max,
                                                              bool_probability=self.boolean_probability/100,
                                                              color_randomize_type=self.color_randomize_type,
                                                              string_capital=self.b_string_capital,
                                                              string_lowercase=self.b_string_lowercase,
                                                              string_numbers=self.b_string_numbers,
                                                              string_special=self.b_string_specials,
                                                              string_custom=self.val_string,
                                                              b_vec_0=self.val_vector_0_toggle,
                                                              b_vec_1=self.val_vector_1_toggle,
                                                              b_vec_2=self.val_vector_2_toggle,
                                                              b_vec_3=self.val_vector_3_toggle,
                                                              src_attribute=attribute,
                                                              obj=obj)
        if func.is_verbose_mode_enabled():
            print(f"Randomized values:{rnd_vals}")

        # Set the values
        func.set_attribute_values(attribute, rnd_vals, on_domains)
        
        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

    def draw(self,context):
        
        active_attribute = context.active_object.data.attributes.active
        domain = active_attribute.domain
        dt = active_attribute.data_type
        
        # Avoid executing code for face corner spill
        if domain != 'CORNER':
            self.b_face_corner_spill = False
        
        e_dt = static_data.EAttributeDataType[dt]
        gui_prop_subtype = static_data.attribute_data_types[dt].gui_prop_subtype

        # ints & floats
        if gui_prop_subtype == static_data.EDataTypeGuiPropType.SCALAR:
            col = self.layout.column(align=True)
            col.prop(self, f"{dt.lower()}_val_min", text="Min")
            col.prop(self, f"{dt.lower()}_val_max", text="Max")

        # vectors & colors
        elif gui_prop_subtype in [static_data.EDataTypeGuiPropType.VECTOR, static_data.EDataTypeGuiPropType.COLOR]:
            
            vector_is_a_color = gui_prop_subtype == static_data.EDataTypeGuiPropType.COLOR

            # Create a column layout for uh, enum toggle atm
            row = self.layout.row(align = True)
            col = row.column(align=True)
            # If it's a color then show hsv rgb toggle
            if vector_is_a_color:
                row = col.row(align=True)
                row.prop_tabs_enum(self, "color_randomize_type")

            # Create column layout for each value
            col = self.layout.column(align=True)
            row2 = col.row(align=True)
            
            # Column 1: Text
            col2 = row2.column(align=True)
            col2.label(text="Min")
            col2.label(text="Max")
            col2.label(text="Enable")
            if vector_is_a_color:
                col2.label(text="")

            # Column 2: values
            col2 = row2.column(align=True)

            # Each row for min and max values
            for minmax in ['min', 'max']:

                if vector_is_a_color and self.b_use_color_picker:
                    row = col2.row(align=True)
                    row.prop(self, f"{dt.lower()}_val_{minmax}", text="")
                else:
                    row = col2.row(align=True)
                    for i in range(0,len(func.get_attribute_default_value(active_attribute))):
                        sub_row = row.row(align=True)
                        sub_row.enabled = getattr(self, f'val_vector_{i}_toggle')
                        sub_row.prop(self, f"{dt.lower()}_val_{minmax}", text="", index=i)
            
            # Each toggle for each vector subelement
            row = col2.row(align=True)
            for i in range(0,len(func.get_attribute_default_value(active_attribute))):
                if vector_is_a_color and self.color_randomize_type == 'HSVA':
                    gui_vector_subel = ['H','S','V','A'][i]
                else:
                    gui_vector_subel = static_data.attribute_data_types[dt].vector_subelements_names[i]
                row.prop(self, f"val_vector_{str(i)}_toggle", text=gui_vector_subel.upper(), toggle=True)
            
            row = col2.row(align=True)
            if vector_is_a_color:
                row.prop(self, "b_use_color_picker", toggle=True)

        # boolean
        elif gui_prop_subtype == static_data.EDataTypeGuiPropType.BOOLEAN:
            col = self.layout.column(align=True)
            col.prop(self, f"boolean_probability", text="Probability")

        # string
        elif gui_prop_subtype == static_data.EDataTypeGuiPropType.STRING:
            col = self.layout.column(align=True)
            col.prop(self, f"string_val_min", text="Min Length")
            col.prop(self, f"string_val_max", text="Max Length")
            
            row = self.layout.row(align=True)
            row.prop(self, "b_use_specified_characters", toggle=True)

            if self.b_use_specified_characters:
                col2 = self.layout.column(align=True)
                row = col2.row(align=True)
                col2.prop(self, "val_string", text="Characters")
                row = col2.row(align=True)
                col2.label(text="Any of the characters in the text field will be used") # leave a space
            else:
                 # Row for toggles
                col = self.layout.column(align=True)
                row2 = col.row(align=True)
                row2.prop(self, "b_string_capital", text="Capital", toggle=True)
                row2.prop(self, "b_string_lowercase", text="Lowercase", toggle=True)

                row2 = col.row(align=True)

                row2.prop(self, "b_string_numbers", text="Numbers", toggle=True)
                row2.prop(self, "b_string_specials", text="Special", toggle=True)
            
        else:
            row = self.layout.row(align=True)
            row.label(icon='ERROR', text=f"Unsupported data type")

        row = self.layout.row(align=True)
        row.prop(self, "b_single_random_value", text="Randomize each domain", toggle=True,  invert_checkbox=True)

        # Do not show face corner spill on attributes not stored in face corners
        sub_row = row.row(align=True)
        sub_row.enabled = domain == 'CORNER' and self.b_on_selection
        sub_row.prop(self, "b_face_corner_spill", text="Selection Face Corner Spill", toggle=True)

        # Row for toggles 2
        row = self.layout.row(align=True)

        # Do not show on selection in other than edit mode
        if context.active_object.mode == 'EDIT':
            row.prop(self, "b_on_selection", text="Selected Only", toggle=True)
        
        

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class AttributesToCSV(bpy.types.Operator):
    bl_idname = "mesh.attribute_to_csv"
    bl_label = "Export to CSV"
    bl_description = "Exports attribute data to CSV file"
    bl_options = {'REGISTER', 'INTERNAL'}

    # General

    filepath: bpy.props.StringProperty(name="File path", default="", description="File path", subtype="FILE_PATH")
    filename: bpy.props.StringProperty(name="File name", default="Attributes", description="File Name", subtype="FILE_PATH")

    b_dont_show_file_selector: bpy.props.BoolProperty(name="dont_show_file_selector", default=False)


    # To CSV Options

    which_attributes_enum: bpy.props.EnumProperty(
        name="Export",
        description="Select an option",
        items=[
            ("ACTIVE", "Active", "Export active attribute to file"),
            ("ALL", "All", "Export all attributes to file"),
            ("BYTYPE", "In Domain", "Export all attributes stored in specific domain to file"),
            ("SPECIFIC", "Multiple", "Export multiple attributes to file"),
        ],
        default="ALL"
    )

    b_add_domain_and_data_type_to_title_row: bpy.props.BoolProperty(name="Add domain and type to header row", default=True)

    domain_filter: bpy.props.EnumProperty(
        name="Filter",
        description="Select an option",
        items=func.get_attribute_domains_enum
    )


    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Selected object is not a mesh")
            return False
        elif context.active_object.data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        elif not context.active_object.data.attributes.active.data_type in static_data.attribute_data_types :
            self.poll_message_set("Data type is not yet supported!")
            return False
        return True
    
    def invoke(self, context, event):
        func.refresh_attribute_UIList_elements()
        func.configutre_attribute_uilist(False, False)
        self.filename = bpy.context.active_object.name + "_mesh_attributes"
        self.filepath = bpy.context.active_object.name + "_mesh_attributes"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.active_object
        current_mode = context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # Gather attributes

        # all
        if self.which_attributes_enum == 'ALL':
            attributes = [attrib for attrib in obj.data.attributes]
        
        # filter by domain or data type
        elif self.which_attributes_enum == 'BYTYPE':
            attributes = [attrib for attrib in obj.data.attributes]
            na = []
            for attribute in attributes:
                if attribute.domain == self.domain_filter:
                    na.append(attribute)
            attributes = na

        # just active attribute
        elif self.which_attributes_enum ==  "ACTIVE":
            attributes = [func.get_active_attribute(obj)]

        elif self.which_attributes_enum ==  "SPECIFIC":
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            attributes = []
            for a in [a for a in gui_prop_group.to_mesh_data_attributes_list if a.b_select]:
                attributes.append(obj.data.attributes[a.attribute_name])

        if not len(attributes):
            self.report({'ERROR'}, f'No attributes to export with selected filters.')
            return  {'CANCELLED'}

        
        try:
            func.write_csv_attributes_file(self.filepath, obj, attributes, self.b_add_domain_and_data_type_to_title_row)
        except PermissionError:
            self.report({'ERROR'}, f'Permission denied to write to file \"{self.filepath}\"')
            return {'CANCELLED'}
        except OSError as exc:
            self.report({'ERROR'}, f'System error: \"{str(exc)}\"')
        
        bpy.ops.object.mode_set(mode=current_mode)
        
        self.report({'INFO'}, f'File saved.')
        return {'FINISHED'}

    def draw(self, context):
        obj = context.active_object
        active_attribute = func.get_active_attribute(obj)
        domain = active_attribute.domain
        dt = active_attribute.data_type

        # add enum checks

        layout = self.layout
        col = layout.column()

            
        # toggle between single, all, and specific
        
        col.label(text="Export")
        row = col.row(align=True)
        row.prop_enum(self, "which_attributes_enum", 'ACTIVE')
        row.prop_enum(self, "which_attributes_enum", 'BYTYPE')
        row.prop_enum(self, "which_attributes_enum", 'ALL')
        row.prop_enum(self, "which_attributes_enum", 'SPECIFIC')

        if self.which_attributes_enum == 'ACTIVE':
            col.label(text=f"{active_attribute.name} will be exported.")

        elif self.which_attributes_enum == 'ALL':
            col.label(text=f"{str(len(obj.data.attributes))} attributes will be exported.")

        elif self.which_attributes_enum == 'BYTYPE':
            col.label(text="Export all stored in domain:")
            row = col.row(align=True)
            for domain in static_data.attribute_domains:
                row.prop_enum(self, "domain_filter", domain)
        
        elif self.which_attributes_enum == 'SPECIFIC':
            col.label(text="Export selected from list:")
            etc.draw_multi_attribute_select_uilist(col)

        col.label(text="")
        col.label(text="Extra options")
        col.prop(self, 'b_add_domain_and_data_type_to_title_row')

        col.label(text="")
        col.label(icon='INFO', text=f"Header row naming convention:")
        if self.b_add_domain_and_data_type_to_title_row:
            col.label(icon="LAYER_ACTIVE", text=f"AttributeName(DATATYPE)(DOMAIN)")
        else:
            col.label(icon="LAYER_ACTIVE", text=f"AttributeName")

class AttributesToImage(bpy.types.Operator):
    """
    Writes attributes to image texture
    """

    bl_idname = "mesh.attribute_to_image"
    bl_label = "Bake to Data Texture"
    bl_description = "Exports attribute data to data texture"
    bl_options = {'REGISTER'}

    # Toggle for selecting a new file or existing file
    image_source_enum: bpy.props.EnumProperty(
        name="Store in",
        description="Select an option",
        items=[
            ("NEW", "New image", "Stores data in new image"),
            ("EXISTING", "Existing image", "Stores data in existing image"),
        ],
        default="NEW"
    )
    
    # New image settings

    # New image width
    img_width: bpy.props.IntProperty(name="Width", default=1024, min=2, max=32768, step=2)
    
    # New image height
    img_height: bpy.props.IntProperty(name="Height", default=1024, min=2, max=32768, step=2)
    
    # forces image to use width x width values
    b_force_img_square: bpy.props.BoolProperty(name="Squared", default=True)
    
    # Name of the new image texture
    new_image_name: bpy.props.StringProperty(name="Name", default="Data Texture")

    # The color fill of the new image texture
    new_image_fill: bpy.props.FloatVectorProperty(name="Base Color", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))

    # Whether to add alpha channel or not to the new texture
    b_new_image_alpha: bpy.props.BoolProperty(name="Alpha Channel", default=False)
    
    # New image dimensions presets
    image_dimensions_presets_enum: bpy.props.EnumProperty(
        name="Image Dimensions",
        description="Select an option",
        items=[
            ("CUSTOM", "Custom", "Specify a resolution"),
            ("8", "8x8", "8px x 8px"),
            ("16", "16x16", "16px x 16px"),
            ("32", "32x32", "32px x 32px"),
            ("64", "64x64", "64px x 64px"),
            ("128", "128x128", "128px x 128px"),
            ("256", "256x256", "256px x 256px"),
            ("512", "512x512", "512px x 512px"),
            ("1024", "1024x1024 (1K)", "1024px x 1024px"),
            ("2048", "2048x2048 (2K)", "2048px x 2048px"),
            ("4096", "4096x4096 (4K)", "4096px x 4096px"),
            ("8192", "8192x8192 (8K)", "8192px x 8192px"),
            ("16384", "16384x16384 (16K)", "16384px x 16384px"),
        ],
        default="2048"
    )
    
    # Existing image settings
    
    # Whether to create a copy of existing image and work on it instead.
    b_create_image_copy: bpy.props.BoolProperty(name="Create a copy", default=False)

    # Data menu

    # Data write mode selector
    image_write_mode_enum: bpy.props.EnumProperty(
        name="Data Write Mode",
        description="Select an option",
        items=[
            ("SEQUENTAL", "Sequental", "Simply writes data one by one pixel starting from (0,0)"),
            ("ATTRIBUTE", "Specify Position", "Use Vector2D attribute to write data at given position"),
            ("UV", "Use UVMap", "Use UV Map to write data like baking textures in blender"),
        ],
        default="UV"
    )

    # UVMap write mode settings

    # UVMap to sample to write the data
    uvmap_selector_enum: bpy.props.EnumProperty(
        name="UVMap",
        description="Select an option",
        items=func.get_uvmaps_enum
    )

    # The margin type to use
    image_bake_margin_type_enum: bpy.props.EnumProperty(
        name="Margin type",
        description="Select an option",
        items=[
            ("ADJACENT_FACES", "Adjacent Faces", "Use pixels from adjacent UV seams"),
            ("EXTEND", "Extend", "Extend border pixels outwards"),
        ],
        default="EXTEND"
    )

    # The margin in pixels to bake
    image_bake_margin: bpy.props.IntProperty(name="Margin size (px)", default=0, min=0)

    # Attribute coordinate write mode settings

    # Selector of the attribute to sample coodrdinates from
    texture_coordinate_attribute_selector_enum: bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.get_texture_coordinate_attributes_enum
    )

    # Data settings
    
    # Channel selector
    image_channels_type_enum: bpy.props.EnumProperty(
        name="Image channels",
        description="Select an option",
        items=[
            ("GRAYSCALE", "All Channels", "Allows writing a single value to all channels"),
            ("ALL", "Separate Channels", "Allows writing three/four values (24/32-bit)"),
        ],
        default="GRAYSCALE"
    )
    
    # THE ATTRIBUTE/IMAGE selector enum for each image channel
    def get_image_channel_datasource_0_enum(self, context):
        return func.get_image_channel_datasource_enum(self, context, 0)
    
    def get_image_channel_datasource_1_enum(self, context):
        return func.get_image_channel_datasource_enum(self, context, 1)
    
    def get_image_channel_datasource_2_enum(self, context):
        return func.get_image_channel_datasource_enum(self, context, 2)
    
    def get_image_channel_datasource_3_enum(self, context):
        return func.get_image_channel_datasource_enum(self, context, 3)

    # THE XYZ XYZW X Y Z  or RGBA RGB R G B selectors for each image channel
    def get_image_channel_datasource_0_vector_element_enum(self, context):
        return func.get_image_channel_datasource_vector_element_enum(self, context, 0, func.get_alpha_channel_enabled_texture_bake_op(self))
    
    def get_image_channel_datasource_1_vector_element_enum(self, context):
        return func.get_image_channel_datasource_vector_element_enum(self, context, 1, func.get_alpha_channel_enabled_texture_bake_op(self))
    
    def get_image_channel_datasource_2_vector_element_enum(self, context):
        return func.get_image_channel_datasource_vector_element_enum(self, context, 2, func.get_alpha_channel_enabled_texture_bake_op(self))
    
    def get_image_channel_datasource_3_vector_element_enum(self, context):
        return func.get_image_channel_datasource_vector_element_enum(self, context, 3, func.get_alpha_channel_enabled_texture_bake_op(self))
    
    # The attribute to write in Red channel or all channels if GRAYSCALE was selected in image_channels_type_enum
    source_attribute_0_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_0_enum
    )

    # Toggle between attribute and image to select the input value in Red channel
    source_attribute_0_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.get_image_channel_datasource_type_enum
    )

    # Selector for vector/image channel eg xyz rgb to bake to given image channel RED
    source_attribute_0_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_0_vector_element_enum
    )
    
    # The attribute to write in Green channel
    source_attribute_1_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_1_enum
        )
    
    # Toggle between attribute and image to select the input value in Green channel
    source_attribute_1_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.get_image_channel_datasource_type_enum
    )

    source_attribute_1_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_1_vector_element_enum
    )

    # The attribute to write in Blue channel
    source_attribute_2_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_2_enum
    )

    # Toggle between attribute and image to select the input value in Blue channel
    source_attribute_2_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.get_image_channel_datasource_type_enum
    )

    source_attribute_2_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_2_vector_element_enum
    )

    # The attribute to write in Alpha channel if supported
    source_attribute_3_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_3_enum
    )

    # Toggle between attribute and image to select the input value in Alpha channel
    source_attribute_3_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.get_image_channel_datasource_type_enum
    )
    
    source_attribute_3_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_3_vector_element_enum
    )

    def is_selected_enum_entry_a_vector_value(self, context, enum, source_attribute_datasource_enum):
        "Checks if given enum entry is a vector or image to show XYZW selectors"
        if source_attribute_datasource_enum == 'IMAGE':
            return True
        if enum == 'NULL':
            return False
        elif enum in context.active_object.data.attributes:
            return static_data.attribute_data_types[context.active_object.data.attributes[enum].data_type].gui_prop_subtype in [static_data.EDataTypeGuiPropType.VECTOR, static_data.EDataTypeGuiPropType.COLOR]
        return False

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Selected object is not a mesh")
            return False
        elif not func.get_cycles_available():
            self.poll_message_set("Cycles render engine is disabled - required for this function to work")
            return False

        return True

    def invoke(self, context, event):
        func.refresh_attribute_UIList_elements()
        func.configutre_attribute_uilist(False, False)
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def get_user_set_new_image_size(self):
        
        # Get the values from input fields if custom is set
        if self.image_dimensions_presets_enum == 'CUSTOM':
            
            # Return width if it is supposed to be squared
            if self.b_force_img_square:
                return (self.img_width, self.img_width)
            
            # Return fully custom resoltuion
            else:
                return (self.img_width, self.img_height)
        else:
            # Return whatever is set in enum, squared.
            return (int(self.image_dimensions_presets_enum), int(self.image_dimensions_presets_enum))

    def bake_to_texture(self, context, obj, image):
        # Object has to be selected, (happens to be active but not selected)
        if not obj.select_get():
            obj.select_set(True)
        
        # Check if cycles is available
        elif not func.get_cycles_available():
            self.report({'ERROR'}, "Cycles Render Engine is disabled. It is required to bake the texture.")
            return {'CANCELLED'}

        # Get requried references
        scene = bpy.context.scene
        uvmap  = obj.data.uv_layers[int(self.uvmap_selector_enum)].name

        if uvmap == 'NULL':
            self.report({'ERROR'}, "No UVMap selected.")
            return {'CANCELLED'}

        # Create a new material
        mat = bpy.data.materials.new('MAME_ATTRIBUTE_BAKER')
        if func.is_verbose_mode_enabled():
            print(f"Created new material {mat.name}")
        mat.use_nodes = True
        mat_nt = mat.node_tree
        mat_nt.nodes.remove(mat_nt.nodes['Principled BSDF'])

        # Set-up the Image Texture node to bake RGB values, 
        sn_texture = mat_nt.nodes.new('ShaderNodeTexImage')
        sn_texture.location = (-300, 120)
        sn_texture.image = image
        sn_texture.select = True
        sn_texture.interpolation = "Linear"
        sn_texture.extension = "REPEAT"
        sn_texture.projection = "FLAT"
        if func.is_verbose_mode_enabled():
            print(f"Baking to {image.name}")
        
        # Set up UVMap input 
        sn_texture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
        sn_texture_uv.location = (-540, -320)
        sn_texture_uv.attribute_name = uvmap
        sn_texture_uv.attribute_type = 'GEOMETRY'
        mat_nt.links.new(sn_texture_uv.outputs['Vector'], sn_texture.inputs['Vector'])

        # Set up separate of the image texture node to select channels
        sn_texture_separate = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
        sn_texture_separate.location = (-80, -320)
        mat_nt.links.new(sn_texture.outputs['Color'], sn_texture_separate.inputs['Vector'])

        # Set up material output node
        sn_out = mat_nt.nodes['Material Output']
        sn_out.location = (660, 140)

        # Set-up emission node
        sn_emit = mat_nt.nodes.new('ShaderNodeEmission')
        sn_emit.location = (340,120)
        mat_nt.links.new(sn_emit.outputs['Emission'], sn_out.inputs['Surface'])

        # Set up RGB mix node 
        sn_colormix = mat_nt.nodes.new('ShaderNodeCombineColor')
        sn_colormix.location = (-140, 120) 
        mat_nt.links.new(sn_colormix.outputs['Color'], sn_emit.inputs['Color'])

        if func.is_verbose_mode_enabled():
            print(f"Bake mode {self.image_channels_type_enum}")
            print(f"Alpha {func.get_alpha_channel_enabled_texture_bake_op(self)}")

        
        #mat_nt.links.new(sn_alphacolormix.outputs['Color'], sn_emit.inputs['Color'])
        # before baking alpha mat_nt.links.new(sn_alphaemit.outputs['Emission'], sn_out.inputs['Surface'])

        # Set-up for RGB baking.
        # ----------------------------

        # Create attribute or texture nodes for input
        def create_attrib_to_combine_color_nodes(src_item_name,  
                                                 tgt_tex_channel_id, 
                                                 src_attrib_vector_id, 
                                                 sn_colormix, 
                                                 uvmap_ref,
                                                 input_type = 'ATTRIBUTE'):


            #vector_id = -1 # This means the attribute is not a vector nor image

            # Bypass
            if src_item_name == 'NULL':
                mat_nt.links.new(sn_texture_separate.outputs[tgt_tex_channel_id], sn_colormix.inputs[tgt_tex_channel_id])

            # Use attribute
            elif input_type == 'ATTRIBUTE': 
                sn_attrib = mat_nt.nodes.new('ShaderNodeAttribute')
                sn_attrib.attribute_name = src_item_name
                sn_attrib.attribute_type = 'GEOMETRY'

                # scalar value
                if src_attrib_vector_id == -1:
                    mat_nt.links.new(sn_attrib.outputs['Fac'], sn_colormix.inputs[tgt_tex_channel_id])

                # vector value, use separate xyz
                else:
                    sn_attrib_split = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                    mat_nt.links.new(sn_attrib.outputs['Vector'], sn_attrib_split.inputs['Vector'])
                    mat_nt.links.new(sn_attrib_split.outputs[src_attrib_vector_id], sn_colormix.inputs[tgt_tex_channel_id])
            
            # Use texture
            else:
                # Set up the texture image node with uv and split xyz
                sn_inputtexture = mat_nt.nodes.new('ShaderNodeTexImage')
                sn_inputtexture.image = bpy.data.images[src_item_name]
                sn_inputtexture.select = False
                sn_inputtexture.interpolation = "Linear"
                sn_inputtexture.extension = "REPEAT"
                sn_inputtexture.projection = "FLAT"

                # Set up UVMap input node 
                sn_inputtexture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
                sn_inputtexture_uv.attribute_name = uvmap_ref
                sn_inputtexture_uv.attribute_type = 'GEOMETRY'
                mat_nt.links.new(sn_inputtexture_uv.outputs['Vector'], sn_inputtexture.inputs['Vector'])
                
                # Split RGB
                sn_inputtexture_separate = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                mat_nt.links.new(sn_inputtexture.outputs['Color'], sn_inputtexture_separate.inputs['Vector'])

                mat_nt.links.new(sn_inputtexture_separate.outputs[src_attrib_vector_id], sn_colormix.inputs[tgt_tex_channel_id])
        
        # Bake single attribute or color texture 
        if self.image_channels_type_enum == 'GRAYSCALE':
            source_attribute_name = getattr(self, f'source_attribute_0_enum')
            
            if func.is_verbose_mode_enabled():
                print(f"Baking RGB from {source_attribute_name}")

            # Case: Not a vector attribute nor an image
            if not len(self.get_image_channel_datasource_0_vector_element_enum(context)):
                # For each RGB channel
                for texture_ch in range(0, 3):
                    create_attrib_to_combine_color_nodes(source_attribute_name, 
                                                         texture_ch, 
                                                         -1, # force not a vector
                                                         sn_colormix, 
                                                         uvmap, 
                                                         'ATTRIBUTE') # force attribute
            else:

                userinput = self.source_attribute_0_vector_element_enum 
            
                # User selected RGBA or RGB / XYZW or XYZ
                if userinput in ["6", '5']:
                    for texture_ch_and_vecid in range(0, 3):
                        create_attrib_to_combine_color_nodes(source_attribute_name, 
                                                             texture_ch_and_vecid, 
                                                             texture_ch_and_vecid, 
                                                             sn_colormix, 
                                                             uvmap, 
                                                             getattr(self, f'source_attribute_0_datasource_enum'))
                
                # User selected XY (no RG preset)
                elif userinput == '4':
                    for texture_ch_and_vecid in range(0, 2):
                        create_attrib_to_combine_color_nodes(source_attribute_name, 
                                                             texture_ch_and_vecid, 
                                                             texture_ch_and_vecid, 
                                                             sn_colormix, 
                                                             uvmap, 
                                                             'ATTRIBUTE') # no RG preset for images
                    # bypass B channel
                    create_attrib_to_combine_color_nodes('NULL', 
                                                         2, # connect to B
                                                         2, # sample B
                                                         sn_colormix, 
                                                         uvmap, 
                                                         'ATTRIBUTE')
                
                # User selected R G B or A
                else:
                    for texture_ch in range(0, 3):
                        create_attrib_to_combine_color_nodes(source_attribute_name, 
                                                             texture_ch, 
                                                             int(userinput), # use selected source channel
                                                             sn_colormix, 
                                                             uvmap, 
                                                             getattr(self, f'source_attribute_0_datasource_enum'))
                        
        # Separate channels to separate inputs
        else:
            for texture_ch in range(0, 3):
                source_attribute_name = getattr(self, f'source_attribute_{texture_ch}_enum')
                if func.is_verbose_mode_enabled():
                    print(f"Baking channel {texture_ch} from {source_attribute_name}")

                if len(self.get_image_channel_datasource_0_vector_element_enum(context)):
                    
                    attrib_vector_id = getattr(self, f'source_attribute_{texture_ch}_vector_element_enum')
                    if attrib_vector_id == '':
                        attrib_vector_id = -1
                else:
                    attrib_vector_id = -1
                create_attrib_to_combine_color_nodes(source_attribute_name, 
                                                     texture_ch, 
                                                     int(attrib_vector_id), 
                                                     sn_colormix, 
                                                     uvmap, 
                                                     getattr(self, f'source_attribute_{texture_ch}_datasource_enum'))
            
        # Setup alpha channel if applicable

        if self.image_channels_type_enum == 'GRAYSCALE':
            bake_alpha = (func.get_alpha_channel_enabled_texture_bake_op(self) and                              # check if the image supports alpha
                                len(self.get_image_channel_datasource_0_vector_element_enum(context))    # if the source attribute is even a vector/image
                                and self.source_attribute_0_vector_element_enum == '6')                        # and if the RGBA/XYZW was selected
            
        else:
            bake_alpha = func.get_alpha_channel_enabled_texture_bake_op(self) and self.source_attribute_3_enum != 'NULL'

        if bake_alpha:
            # The only way to trigger this is either XYZW value or RGBA value input.
            if self.image_channels_type_enum == 'GRAYSCALE':
                if self.source_attribute_0_datasource_enum == 'IMAGE':
                    sn_alphatexture = mat_nt.nodes.new('ShaderNodeTexImage')
                    sn_alphatexture.location = (-360, 600)
                    
                    sn_alphatexture.image = bpy.data.images[self.source_attribute_0_enum]
                    sn_alphatexture.interpolation = "Linear"
                    sn_alphatexture.extension = "REPEAT"
                    sn_alphatexture.projection = "FLAT"

                    # And it's UV input
                    sn_alphatexture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphatexture_uv.location = (-540, -600)
                    sn_alphatexture_uv.attribute_name = uvmap
                    sn_alphatexture_uv.attribute_type = 'GEOMETRY'
                    mat_nt.links.new(sn_alphatexture_uv.outputs['Vector'], sn_alphatexture.inputs['Vector'])
                    
                    alpha_source_node = [sn_alphatexture, 'Alpha']

                else:
                    sn_alphaattrib = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphaattrib.attribute_name = self.source_attribute_0_enum
                    sn_alphaattrib.attribute_type = 'GEOMETRY'

                    alpha_source_node = [sn_alphaattrib, 'Alpha']
            
            else:
                # if baking separate attributes 
                if self.source_attribute_3_datasource_enum == 'IMAGE':
                    # Set-up the SOURCE Alpha Image Texture node to bake to
                    sn_alphatexture = mat_nt.nodes.new('ShaderNodeTexImage')
                    sn_alphatexture.location = (-360, 600)
                    
                    sn_alphatexture.image = bpy.data.images[self.source_attribute_3_enum]
                    sn_alphatexture.interpolation = "Linear"
                    sn_alphatexture.extension = "REPEAT"
                    sn_alphatexture.projection = "FLAT"

                    # And it's UV input
                    sn_alphatexture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphatexture_uv.location = (-540, -600)
                    sn_alphatexture_uv.attribute_name = uvmap
                    sn_alphatexture_uv.attribute_type = 'GEOMETRY'
                    mat_nt.links.new(sn_alphatexture_uv.outputs['Vector'], sn_alphatexture.inputs['Vector'])

                    if self.source_attribute_3_vector_element_enum == 3:
                        alpha_source_node = [sn_alphatexture, 'Alpha']
                    else:
                        # Split RGB
                        sn_alphatexture_separate = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                        mat_nt.links.new(sn_alphatexture.outputs['Color'], sn_alphatexture_separate.inputs['Vector'])

                        alpha_source_node = [sn_alphatexture_separate, int(self.source_attribute_3_vector_element_enum)]

                else:
                    sn_alphaattrib = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphaattrib.attribute_name = self.source_attribute_3_enum
                    sn_alphaattrib.attribute_type = 'GEOMETRY'

                    # scalar
                    if not len(self.get_image_channel_datasource_3_vector_element_enum(context)):
                        alpha_source_node = [sn_alphaattrib, 'Fac']
                    # vector
                    else:
                        
                        sn_alphaattrib_split = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                        mat_nt.links.new(sn_alphaattrib.outputs['Vector'], sn_alphaattrib_split.inputs['Vector'])
                        alpha_source_node = [sn_alphaattrib, int(self.source_attribute_3_vector_element_enum)]
                
                
                

                
        # Replace all material slots or create a material slot.
        remove_slot = False
        if not len(obj.material_slots):
            remove_slot = True
            bpy.ops.object.material_slot_add()
        
        current_mats = [slot.material for slot in obj.material_slots]
        for slot in obj.material_slots:
            slot.material = mat
            
        # Set the render settings
        sn_texture.select = True

        # All settings to be changed
        change_settings = [
            [scene.render, "engine"],
            [scene.cycles, "feature_set"],
            [scene.cycles, "device"],
            [scene.cycles, "adaptive_threshold"],
            [scene.cycles, "samples"],
            [scene.cycles, "adaptive_min_samples"],
            [scene.cycles, "time_limit"],
            [scene.cycles, "use_denoising"],
            [scene.cycles, "bake_type"],
            [scene.render.bake, "target"],
            [scene.render.bake, "use_selected_to_active"],
            [scene.render.bake, "use_clear"]]
        
        if hasattr(bpy.context.scene.render.bake, 'margin_type'):
            change_settings += [
                [scene.render.bake, "margin_type"]]
            
        if hasattr(bpy.context.scene.cycles, "use_guiding"):
            change_settings += [
                [scene.cycles, "use_guiding"]]
        
        if hasattr(bpy.context.scene.render.bake, "view_from"):
            change_settings += [
                [scene.render.bake, "view_from"]]

        change_settings += [
            [scene.render.bake, "margin"]
        ]

        # Settings for render
        mame_settings = [
            'CYCLES',
            'SUPPORTED',
            'CPU',
            0.01,
            1,
            0,
            0,
            False,
            'EMIT',
            'IMAGE_TEXTURES',
            False,
            False,
            ]
        
        if hasattr(bpy.context.scene.render.bake, 'margin_type'):
            mame_settings += [
                self.image_bake_margin_type_enum]
            
        if hasattr(bpy.context.scene.cycles, "use_guiding"):
            mame_settings += [False]
        
        if hasattr(bpy.context.scene.render.bake, "view_from"):
            mame_settings += ['ABOVE_SURFACE']
        
        mame_settings +=[
            self.image_bake_margin
        ]


        # Store current settings to revert to after baking
        current_settings = []
        for a in change_settings:   
            current_settings.append(getattr(a[0], a[1]))

        # Change to settings optimized for baking attributes
        for i, a in enumerate(change_settings):
            setattr(a[0], a[1], mame_settings[i])

        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.context.active_object.data.update()
    
        # Bake RGB
        sn_texture.image = image
        sn_texture.select = True
        bpy.ops.object.bake(type='EMIT')
        
        # Write alpha to RGB
        if bake_alpha:
            # Create a new image to store the alpha in
                new_img_size = self.get_user_set_new_image_size()
                alpha_image = bpy.data.images.new("Temporary baked alpha texture (safe to remove)", new_img_size[0], new_img_size[1], float_buffer=True, is_data=True)
                alpha_image.alpha_mode = 'NONE'
                alpha_image.generated_color = self.new_image_fill

                # Set the image node to new image
                sn_texture.image = alpha_image
                sn_texture.select = True

                # Connect the node to emit shader input
                
                mat_nt.links.new(alpha_source_node[0].outputs[alpha_source_node[1]], sn_emit.inputs['Color'])

                # Bake again
                bpy.ops.object.bake(type='EMIT')

                # Copy red channel to alpha channel to first image
                pixelbuffer_RGB = np.zeros(len(image.pixels), dtype=np.float32)
                image.update()
                image.pixels.foreach_get(pixelbuffer_RGB)
                np.delete(pixelbuffer_RGB, [a for a in range(3,len(pixelbuffer_RGB), 4)]) # remove exising alpha

                alpha_image.update()
                pixelbuffer_A = np.zeros(len(alpha_image.pixels), dtype=np.float32)
                alpha_image.pixels.foreach_get(pixelbuffer_A)
                pixelbuffer_A = np.take(pixelbuffer_A, [a for a in range(0,len(pixelbuffer_A), 4)]) # get r channel

                np.put(pixelbuffer_RGB, [i for i in range(3, len(pixelbuffer_RGB), 4)], pixelbuffer_A) # insert new alpha

                image.pixels.foreach_set(pixelbuffer_RGB)
                image.update()
                # cleanup
                if not etc.get_preferences_attrib('bakematerial_donotdelete'):
                    bpy.data.images.remove(alpha_image)
        
        # Clean up
        for i, a in enumerate(change_settings):
            setattr(a[0], a[1], current_settings[i])

        if not remove_slot:
            for i, slot in enumerate(obj.material_slots):
                slot.material = current_mats[i]
        
        if not etc.get_preferences_attrib('bakematerial_donotdelete'):
            bpy.data.materials.remove(mat)
        
        if remove_slot:
            bpy.ops.object.material_slot_remove()

        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, f'Data written to \"{image.name}\" image texture')
        return {'FINISHED'}

    def execute(self, context):
        obj = context.active_object
        image = None
        
        # store references to images -_-
        enums = []
        for i in range(0, 4):
            enums.append(getattr(self, f'source_attribute_{i}_enum'))


        # Create a new image with specified dimensions and color fill
        if self.image_source_enum == 'NEW':
            new_img_size = self.get_user_set_new_image_size()
            image = bpy.data.images.new(self.new_image_name, new_img_size[0], new_img_size[1], float_buffer=False, is_data=True)
            image.alpha_mode = 'CHANNEL_PACKED' if self.b_new_image_alpha else 'NONE'
            image.generated_color = self.new_image_fill
        
        # Get existing image
        else:
            image = context.window_manager.mame_image_ref
            if image is None:
                self.report({'ERROR'}, 'No image selected')
                return {'CANCELLED'}
            
            # Copy the image if selected
            if self.b_create_image_copy:
                image = image.copy()

        for i in range(0, 4):
            enums.append(setattr(self, f'source_attribute_{i}_enum', enums[i]))

        return self.bake_to_texture(context, obj, image)

    def enum_watchdog(self, context):
        "Bugfix for blender handling of dynamic enums"
        for i in range(0, 4):
            try:
                if getattr(self, f'source_attribute_{i}_enum') == '':
                    setattr(self, f'source_attribute_{i}_enum', exec(f'self.get_image_channel_datasource_{i}_enum(context)[0][0]'))
            except TypeError:
                pass

        for i in range(0, 4):
            try:
                if getattr(self, f'source_attribute_{i}_datasource_enum') == '':
                    setattr(self, f'source_attribute_{i}_datasource_enum', func.get_image_channel_datasource_type_enum(self, context)[0][0])
            except TypeError:
                pass
                    
        for i in range(0, 4):
            try:
                if self.is_selected_enum_entry_a_vector_value(context, getattr(self, f'source_attribute_{i}_enum')):
                    ve = getattr(self, f'source_attribute_{i}_vector_element_enum')
                    if  ve == '' and len(exec(f'self.get_image_channel_datasource_{i}_vector_element_enum(context)')):
                        setattr(self, f'source_attribute_{i}_vector_element_enum', exec(f'self.get_image_channel_datasource_{i}_vector_element_enum(context)[0][0]'))
            except TypeError:
                pass
        
        
        
        

    def draw(self, context):
        obj = context.active_object
        active_attribute = func.get_active_attribute(obj)
        domain = active_attribute.domain
        dt = active_attribute.data_type

        # add enum checks
        self.enum_watchdog(context)

        layout = self.layout
        col = layout.column()

        rootcol = col.column()


        # Image File Settings
        rootcol.label(text='Image Texture File')
        box = rootcol.box()
        col = box.column()
        col.ui_units_y = 9
        sourceselect_row = col.row(align = True)
        sourceselect_row.prop_enum(self, 'image_source_enum', 'NEW')
        sourceselect_row.prop_enum(self, 'image_source_enum', 'EXISTING')

        # New image menu
        if self.image_source_enum == 'NEW':
            sr = col.row()
            sr.label(text="Texture Name")
            sr.prop(self, 'new_image_name', text="")
            sr = col.row()
            sr.label(text="Base Color Fill")
            sr.prop(self, 'new_image_fill', text="")

            sr = col.row()
            sr.label(text="Add Alpha Channel")
            sr.prop(self, 'b_new_image_alpha', text="Alpha Channel" if self.b_new_image_alpha else "No Alpha Channel", toggle=True)
            
            sr = col.row()
            sr.label(text='Dimensions')
            sr.prop(self, 'image_dimensions_presets_enum', text= '')

            if self.image_dimensions_presets_enum == 'CUSTOM':
                
                row = col.row()
                row.prop(self, "img_width", text="Width" if not self.b_force_img_square else "Width x Height")
                if not self.b_force_img_square:
                    row.prop(self, "img_height")

                col.prop(self, "b_force_img_square", toggle = True)

        # Existing image menu
        else:
            sr = col.row()
            sr.label(text="Texture Image")
            sr.template_ID(context.window_manager, 'mame_image_ref', open='image.open', text="")
            sr = col.row()
            sr.label(text="Copy image")
            sr.prop(self, 'b_create_image_copy', toggle = True)

            sr = col.row()
            sr.label(text="Alpha channel")
            img = context.window_manager.mame_image_ref
            if img is not None:
                alpha_en = img.alpha_mode != 'NONE'
            else:
                alpha_en = False
            sr.label(text="Supported" if alpha_en else 'Unsupported', icon="CHECKMARK" if alpha_en else "X")

            if context.window_manager.mame_image_ref is not None and not context.window_manager.mame_image_ref.is_float:
                sr = col.column()
                sr.label(icon="ERROR", text="This image stores bytes (0-255), not floats (0.0-1.0)")
                sr.label(icon="INFO", text="Some values might be rounded")
                
        

        # Data write mode menu
        # rootcol.label(text="Data write mode")
        rootcol.label(text="Settings")
        box = rootcol.box()
        subcol = box.column()
        # subcol.ui_units_y = 11
        subcol.ui_units_y = 6
        row = subcol.row()
        #row.prop_tabs_enum(self, 'image_write_mode_enum')

        # Sequental write menu
        if self.image_write_mode_enum == 'SEQUENTAL':
            subcol = subcol.column(align=False)
            infobox = subcol.box()
            infobox_col = infobox.column()
            infobox_col.label(icon="INFO", text="Write values from left lower corner, line by line")

            subcol.prop(self, 'pixel_index_offset')

            row = subcol.row(align=True)
            row.prop(self, 'x_pixel_offset')
            row.prop(self, 'y_pixel_offset')

            row = subcol.row(align=True)
            row.prop(self, 'x_max_height')
            row.prop(self, 'y_max_width')
            subcol.label(text="")

        # Specify position write menu
        elif self.image_write_mode_enum == 'ATTRIBUTE':
            subcol = subcol.column(align=True)
            infobox = subcol.box()
            infobox_col = infobox.column()
            infobox_col.label(icon="INFO", text="Write values at XY pixel coordinates from attribute")

            subcol.prop(self, 'texture_coordinate_attribute_selector_enum')


        # UVMap bake menu
        elif self.image_write_mode_enum == 'UV':
            subcol = subcol.column(align=False)

            if not func.get_cycles_available():
                subcol.label(text="")
                subcol.label(icon='ERROR', text="This mode requires Cycles Render Engine to be enabled")
            else:

                # infobox = subcol.box()
                # infobox_col = infobox.column()
                # infobox_col.label(icon="INFO", text="Bake interpolated values at UV coordinates")

                mr = subcol.row()
                mr.label(text="UVMap")
                mr.prop(self, 'uvmap_selector_enum', text = "")
                mr = subcol.row()
                mr.label(text="Margin Size (px)")
                mr.prop(self, 'image_bake_margin', text='')
                if hasattr(bpy.context.scene.render.bake, 'margin_type'):
                    mr = subcol.row()
                    mr.label(text="Margin Type")
                    mr.prop(self, 'image_bake_margin_type_enum', text = "")
                
                subcol.label(text="")
                subcol.label(icon='ERROR', text="Make sure modifiers and geometry nodes do not override materials")
                
        
        # Attribute and data selector menu
        rootcol.label(text="Data")
        box = rootcol.box()
        subcol = box.column()
        subcol.ui_units_y = 7
        row = subcol.row()
        row.prop_tabs_enum(self, 'image_channels_type_enum')

        channel_selector_text_x_units = 0.7
        channel_selector_datatype_x_units = 6
        vector_subelements_x_units = 3.5
        
        subcol = subcol.column(align=False)
        if self.image_channels_type_enum == 'GRAYSCALE':
            right_el_x_size = 16
            sr = subcol.row()
            sr_text = sr.row()
            sr_text.label(text="Source Type")
            ssr = sr_text.row()
            ssr.ui_units_x = right_el_x_size
            ssr.prop_tabs_enum(self, 'source_attribute_0_datasource_enum')
            
            sr_text = subcol.row()
            sr_text.label(text="Source")
            ssr = sr_text.row()
            ssr.ui_units_x = right_el_x_size
            ssr.prop(self, 'source_attribute_0_enum', text='')
            
            sr = subcol.row()
            if self.is_selected_enum_entry_a_vector_value(context, self.source_attribute_0_enum, self.source_attribute_0_datasource_enum) and len(self.get_image_channel_datasource_0_vector_element_enum(context)):
                sr.label(text="Source Channels")
                ssr = sr.row()
                ssr.ui_units_x = right_el_x_size
                ssr.prop_tabs_enum(self, 'source_attribute_0_vector_element_enum')

        else:
            sr = subcol.row()
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="R")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_0_datasource_enum')
            sr.prop(self, 'source_attribute_0_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_0_vector_element_enum')

            sr = subcol.row()
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="G")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_1_datasource_enum')
            sr.prop(self, 'source_attribute_1_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_1_vector_element_enum')


            sr = subcol.row()
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="B")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_2_datasource_enum')
            sr.prop(self, 'source_attribute_2_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_2_vector_element_enum')


            sr = subcol.row()
            
            sr.enabled = func.get_alpha_channel_enabled_texture_bake_op(self)
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="A")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_3_datasource_enum')
            sr.prop(self, 'source_attribute_3_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_3_vector_element_enum')
            
class AttributesFromCSV(bpy.types.Operator):
    bl_idname = "mesh.attribute_from_file"
    bl_label = "Import from CSV"
    bl_description = "Imports attribute data from external file"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(name="File path", default="", description="File path", subtype="FILE_PATH")

    domain_detect_enum: bpy.props.EnumProperty(
        name="Domain Detection",
        description="Select an option",
        items=[
            ("NAME", "Search in title row", "Looks for strings like \"(POINT)\" in first row to determine domain"),
            ("DEFINEDFORALL", "Specify domain", "Assume single domain for all columns"),
        ],
        default="NAME"
    )

    data_type_detect_enum: bpy.props.EnumProperty(
        name="Data Type Detection",
        description="Select an option",
        items=[
            ("NAME", "Search in title row", "Looks for strings like \"(FLOAT)\" in first row to determine data type"),
            ("DEFINEDFORALL", "Specify data type", "Assume single data type for all columns"),
        ],
        default="NAME"
    )

    domain_selector_enum: bpy.props.EnumProperty(
        name="Domain",
        description="Select an option",
        items=func.get_attribute_domains_enum
    )

    data_type_selector_enum: bpy.props.EnumProperty(
        name="Data Type",
        description="Select an option",
        items=func.get_attribute_data_types_enum
    )

    b_remove_domain_str_from_name: bpy.props.BoolProperty(name="Remove domain string from name", description="Removes parts like \"(POINT)\" from name", default=True)
    b_remove_data_type_str_from_name: bpy.props.BoolProperty(name="Remove data type string from name", description="Removes parts like \"(FLOAT)\" from name", default=True)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        args = {}
        if self.domain_detect_enum == "DEFINEDFORALL":
            args['force_domain'] = self.domain_selector_enum
        if self.data_type_detect_enum == "DEFINEDFORALL":
            args['force_data_type'] = self.data_type_selector_enum

        status, errors, count = func.csv_to_attributes(self.filepath, context.active_object, [], self.b_remove_domain_str_from_name, self.b_remove_data_type_str_from_name, **args)
        
        if not len(errors):
            # bpy.ops.window_manager.mame_message_box(icon='INFO', message=f'Successfully imported {count} attributes from CSV file.')
            self.report({'INFO'}, f'Successfully imported {count} attributes from CSV file.')
        else:
            gui.set_message_box_function(gui.draw_error_list)
            gui.set_message_box_extra_data(errors)

            bpy.ops.window_manager.mame_message_box(message="During import following errors occured:", custom_draw=True, width=700)

        return {'FINISHED'}
    

    def draw(self, context):
        obj = context.active_object
        col = self.layout.column()
        
        domain_col = col.column()
        domain_col.label(text="Domain")
        row = domain_col.row(align=True)
        row.prop_enum(self, 'domain_detect_enum', 'NAME')
        row.prop_enum(self, 'domain_detect_enum', 'DEFINEDFORALL')
        if self.domain_detect_enum == 'DEFINEDFORALL':
            domain_col.prop(self,'domain_selector_enum')
        else:
            domain_col.label(icon='INFO', text="Looking for strings like \"(FACE)\"")


        data_type_col = col.column()
        data_type_col.label(text="Data type")
        row = data_type_col.row(align=True)
        row.prop_enum(self, 'data_type_detect_enum', 'NAME')
        row.prop_enum(self, 'data_type_detect_enum', 'DEFINEDFORALL')
        if self.data_type_detect_enum == 'DEFINEDFORALL':
            data_type_col.prop(self,'data_type_selector_enum')
        else:
            data_type_col.label(icon='INFO', text="Looking for strings like \"(FLOAT)\"")

        toggles_col = col.column()
        toggles_col.label(text="Attribute Name")
        toggles_col.prop(self,'b_remove_data_type_str_from_name')
        toggles_col.prop(self, 'b_remove_domain_str_from_name')
    