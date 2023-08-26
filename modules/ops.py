
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
from . import data
from . import etc

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
    b_face_corner_spill_enable: bpy.props.BoolProperty(name="Face Corner Spill", default = False)

    @classmethod
    def poll(self, context):
        return (context.active_object
                and context.active_object.mode == 'EDIT' 
                and context.active_object.type == 'MESH' 
                and context.active_object.data.attributes.active 
                and func.get_is_attribute_valid_for_manual_val_assignment(context.active_object.data.attributes.active)
                )

    def execute(self, context):
        obj = context.active_object
        active_attrib_name = obj.data.attributes.active.name 

        bpy.ops.object.mode_set(mode='OBJECT')
        if func.is_verbose_mode_enabled():
            print( f"Working on {active_attrib_name} attribute" )

        attribute = obj.data.attributes[active_attrib_name] #!important

        # Get value from GUI
        prop_group = context.object.MAME_PropValues
        dt = attribute.data_type
        if dt == "FLOAT":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_float
        elif dt == "INT":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_int
        elif dt == "FLOAT_VECTOR":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_vector
        elif dt == "FLOAT_COLOR":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_color
        elif dt == "BYTE_COLOR":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_bytecolor
        elif dt == "STRING":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_string
        elif dt == "BOOLEAN":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_bool
        elif dt == "FLOAT2":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_vector2d
        elif dt == "INT8":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_int8
        elif dt == "INT32_2D":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_int32_2d
        elif dt == "QUATERNION":
            value = func.get_attrib_default_value(attribute) if self.b_clear else prop_group.val_quaternion
        else:
            self.report({'ERROR', "Unsupported data type!"})

        # Set the value
        func.set_attribute_value_on_selection(self, context, obj, attribute, value, face_corner_spill=self.b_face_corner_spill_enable)
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        return {"FINISHED"}
    
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
        if not self.domain_data_type_enum in data.object_data_sources:
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
        if self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", 'UVMAP']: 
            if self.enum_uvmaps == 'NULL':
                self.report({'ERROR'}, f"No UVMap selected. Nothing done")
                return False


        # invalid domain enum for multiple choices
        if len(data.object_data_sources[self.domain_data_type_enum].domains_supported) > 1 and self.target_attrib_domain_enum == '':
            self.report({'ERROR'}, f"Invalid source domain. Nothing done")
            return False
        return True


    @classmethod
    def poll(self, context):
        return (context.active_object is not None) and context.active_object.type == "MESH"
    
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
            self.target_attrib_domain_enum = data.object_data_sources[self.domain_data_type_enum].attribute_domain_on_default

        # Read prefixes and suffixes of automatic naming
        data_type = data.object_data_sources[self.domain_data_type_enum].data_type
        
        
        if func.is_verbose_mode_enabled():
            print(f"Batch mode supported & enabled: {not (not data.object_data_sources[self.domain_data_type_enum].batch_convert_support or not self.b_batch_convert_enabled) }")
        
        # [Batch mode off] Single assignment to single attribute
        if not data.object_data_sources[self.domain_data_type_enum].batch_convert_support or not self.b_batch_convert_enabled:
            
            def format_name(name:str):
                # this is dirty but it already gets the right data so...
                return name.format(domain=func.get_friendly_domain_name(self.target_attrib_domain_enum, plural=True), 
                                face_map=func.get_face_maps_enum(self, context)[int(self.enum_face_maps)][1] if self.enum_face_maps != 'NULL' else None,
                                shape_key=func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None, 
                                shape_key_to=func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_target)][1] if self.enum_shape_keys_offset_target != 'NULL' else None, 
                                shape_key_from=func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None, 
                                vertex_group=func.get_vertex_groups_enum(self, context)[int(self.enum_vertex_groups)][1] if self.enum_vertex_groups != 'NULL' else None, 
                                material=func.get_materials_enum(self, context)[int(self.enum_materials)][1] if self.enum_materials != 'NULL' else None, 
                                material_slot=func.get_material_slots_enum(self, context)[int(self.enum_material_slots)][1] if self.enum_material_slots != 'NULL' else None,
                                uvmap=func.get_uvmaps_enum(self, context)[int(self.enum_uvmaps)][1] if self.enum_uvmaps != 'NULL' else None) 
            
            # Automatic name formatting
            if self.attrib_name == "":
                name = data.object_data_sources[self.domain_data_type_enum].attribute_auto_name
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
                func.convert_attribute(self, obj, attrib.name, mode=self.enum_attrib_converter_mode, 
                                               domain=self.enum_attrib_converter_domain, 
                                               data_type=self.enum_attrib_converter_datatype)

        # [Batch mode on] Assign all of type to n amount of attributes 
        # This currently applies only to:
        # "VERT_IS_IN_VERTEX_GROUP", 
        # "VERT_FROM_VERTEX_GROUP", 
        # "VERT_SHAPE_KEY_POSITION_OFFSET", 
        # "VERT_SHAPE_KEY_POSITION",
        # "FACE_IS_MATERIAL_ASSIGNED", 
        # "FACE_IS_MATERIAL_SLOT_ASSIGNED", 
        # "FACE_FROM_FACE_MAP"
        else:
            for element_index, element in enumerate(func.get_all_mesh_data_entries_of_type(obj, self.domain_data_type_enum)):
                
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

                # case: vertex groups
                # VERT_IS_IN_VERTEX_GROUP: check for each group if vertex is in it 
                # VERT_FROM_VERTEX_GROUP: get vertex weight for each vertex group for each vertex
                # -> iterates over every vertex group
                if self.domain_data_type_enum in ['VERT_IS_IN_VERTEX_GROUP', "VERT_FROM_VERTEX_GROUP"]: 
                    vertex_group_name = func.get_vertex_groups_enum(self, context)[element][1]
                    vg_index = element

                # case: get shape key position for each shape key 
                if self.domain_data_type_enum in ["VERT_SHAPE_KEY_POSITION"]:
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
                if self.domain_data_type_enum == "FACE_IS_MATERIAL_ASSIGNED":
                    material = func.get_materials_enum(self, context)[element][1]
                    sel_mat = element    

                # case; check for each material slot if it's assigned
                # -> iterates over every material slot
                if self.domain_data_type_enum == "FACE_IS_MATERIAL_SLOT_ASSIGNED":
                    material_slot = func.get_material_slots_enum(self, context)[element][1]
                    mat_index = element

                #case: check for each face map if it's assigned
                # -> iterates over every face map
                if self.domain_data_type_enum == "FACE_FROM_FACE_MAP":
                    face_map = func.get_face_maps_enum(self, context)[element][1]
                    fm_index = element

                def format_name_batch(xname:str):
                    return xname.format(domain=func.get_friendly_domain_name(self.target_attrib_domain_enum, plural=True), 
                                    face_map=face_map,
                                    shape_key=shape_key, 
                                    shape_key_to=shape_key_to,
                                    shape_key_from=shape_key, 
                                    vertex_group=vertex_group_name, 
                                    material=material, 
                                    material_slot=material_slot,
                                    index=element_index) 

                # Create formatted attribute name
                if self.attrib_name == "":
                    xname = data.object_data_sources[self.domain_data_type_enum].attribute_auto_name
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
                obj_data = func.get_mesh_data(obj, 
                                        self.domain_data_type_enum, 
                                        self.target_attrib_domain_enum, 
                                        vg_index=vg_index,
                                        sk_index=sk_index,
                                        sk_offset_index=sk_offset_index,
                                        fm_index=fm_index,
                                        sel_mat=sel_mat,
                                        mat_index=mat_index)
                
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
        
        # get if the attrib supports batch conversion
        batch_convert_support = False if self.domain_data_type_enum == '' else data.object_data_sources[self.domain_data_type_enum].batch_convert_support

        row = self.layout

        # New attribute name
        row.prop(self, "attrib_name", text="Name")
        if self.attrib_name == '':
            row.label(text="Using auto-generated name", icon='INFO')

        # Data to create the attribute from
        row.prop(self, "domain_data_type_enum", text="Data")
        
        # Source domain selector, if applicable to source attribute
        if len(func.get_supported_domains_for_selected_mesh_data_source_enum_entry(self, context)) > 1:
            row.prop(self, "target_attrib_domain_enum", text="From")
        
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
        
        # UVMap domain selection, or from UVMap for legacy blender versions
        elif self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", 'UVMAP']:
            row.prop(self, "enum_uvmaps", text="UV Map")

        # convert all of type to attrib
        if batch_convert_support:
            row.prop(self, "b_batch_convert_enabled", text="Batch Convert All To Attributes")

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
        self.poll_message_set("No active attribute")
        return context.active_object and context.active_object.data.attributes.active

    def execute(self, context):
        obj = context.active_object
        attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode
        
        # All attribute actions should be performed in object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        src_attrib = obj.data.attributes[attrib_name] #!important

        new_attrib = obj.data.attributes.new(name=src_attrib.name, type=src_attrib.data_type, domain=src_attrib.domain)

        func.set_attribute_values(new_attrib, func.get_attrib_values(src_attrib, obj))
        
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
        self.poll_message_set("No active attribute")
        return context.active_object and context.active_object.data.attributes.active
    
    def execute(self, context):
        obj = context.active_object
        src_attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        bpy.ops.object.mode_set(mode='OBJECT')

        src_attrib = obj.data.attributes[src_attrib_name] # !important
        
        # get selected domain indexes
        selected = [domain.index for domain in func.get_mesh_selected_by_domain(obj, src_attrib.domain, self.b_face_corner_spill)]
        if func.is_verbose_mode_enabled():
            print(f"Selected domain indexes: {selected}")
        
        # No selection and selection mode is enabled?
        if not len(selected) and self.b_edit_mode_selected_only:
            self.report({'ERROR'}, f"No selection to perform the operations onto")
            bpy.ops.object.mode_set(mode=current_mode)
            return {'CANCELLED'}
        
        # # numbers:
        # else:
        prop_name = func.get_attrib_value_propname(src_attrib)
        
        storage = func.get_attrib_values(src_attrib, obj)
        
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
            skip = len(func.get_attrib_default_value(src_attrib)) if not src_attrib.data_type == 'FLOAT' else 1
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
        sub_box = row.box()
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
    
    
    # Quick check if an attribute is an UVMap
    def is_uvmap(self, a):
        return a.domain == 'CORNER' and a.data_type == 'FLOAT2'

    # Quick check if an attribute is a color attribute
    def is_color_attrib(self, a):
        return (a.domain == 'CORNER' or a.domain == 'POINT') and (a.data_type == 'FLOAT_COLOR' or a.data_type == 'BYTE_COLOR') 
    
    @classmethod
    def poll(self, context):

        # Check if there is any attibute that can be removed
        if context.active_object and context.active_object.type == 'MESH':
            for a in context.active_object.data.attributes:
                types = func.get_attribute_types(a)
                editable = True
                for e in [data.EAttributeType.CANTREMOVE]:
                    if e in types:
                        editable = False
                        break
                if editable:
                    return True
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
            if data.EAttributeType.CANTREMOVE in a_types :
                continue
            
            if ((self.b_include_uvs if self.is_uvmap(a) else True) and 
                (self.b_include_color_attribs if self.is_color_attrib(a) else True) and
                (self.b_include_hidden if data.EAttributeType.HIDDEN in a_types else True) and
                (self.b_include_all if data.EAttributeType.DONOTREMOVE in a_types else True)):
                    if func.is_verbose_mode_enabled():
                        print(f"Attribute removed - {a.name}: {a.domain}, {a.data_type}")
                    obj.data.attributes.remove(a)
                    num += 1
        
        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, (f"Removed {str(num)} attribute" + ("s" if num > 1 else "") if num else "None of attributes removed!"))
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout

        row.label(text="Include:")
        if bpy.app.version >= (3,5,0):
            row.prop(self, "b_include_uvs", text="UVMaps")
        row.prop(self, "b_include_color_attribs", text="Color Attributes")
        row.prop(self, "b_include_hidden", text="Hidden")
        row.prop(self, "b_include_all", text="Non-Recommended")

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
               ("ATTRIBUTE", "Use float attribute to weight", "Use float attribute to weight vertices")]
    )
    
    # The atttribute data types in to_vgindex_source_attribute_enum
    data_types_filter = ['FLOAT', 'INT']

    # The attribute to get weights from when converting to vertex group index
    to_vgindex_weights_attribute_enum: bpy.props.EnumProperty(
        name="Float Attribute",
        description="Select an option",
        items=func.get_vertex_weight_attributes_enum
    )
    
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
        
        elif self.data_target_enum in ["TO_SELECTED_VERTICES_IN_UV_EDITOR", "TO_SELECTED_EDGES_IN_UV_EDITOR"] and not len(obj.data.uv_layers):
            self.report({'ERROR'}, "No UVMaps. Nothing done")
            input_invalid = True

        if input_invalid:
            bpy.ops.object.mode_set(mode=current_mode)
            return {'CANCELLED'}

    def create_temp_converted_attrib(self, obj, convert_from_name:str, name_suffix:str, target_domain:str, target_data_type:str):
        """
        Copies the attribute and converts it to required type. Returns name of temporary converted attribute.
        """

        convert_from = obj.data.attributes[convert_from_name]
        if func.is_verbose_mode_enabled():
            print(f"Conversion required! Source: {convert_from.data_type} in  {convert_from.domain}, len {len(convert_from.data)}. Target: {self.convert_to_domain_enum} in {target_data_type}")
        
        new_attrib = obj.data.attributes.new(name=convert_from.name + " " + name_suffix, type=convert_from.data_type, domain=convert_from.domain)
        new_attrib_name = new_attrib.name
        
        if func.is_verbose_mode_enabled():
            print(f"Created temporary attribute {new_attrib_name}")
        
        convert_from = obj.data.attributes[convert_from_name] # After the new attribute has been created, reference is invalid
        func.set_attribute_values(new_attrib, func.get_attrib_values(convert_from, obj))
        func.convert_attribute(self, obj, new_attrib.name, 'GENERIC', target_domain, target_data_type)
        if func.is_verbose_mode_enabled():
            print(f"Successfuly converted attribute ({new_attrib_name}), datalen = {len(obj.data.attributes[new_attrib_name].data)}")
        return new_attrib_name


    @classmethod
    def poll(self, context):
        self.poll_message_set("No active attribute")    
        return context.active_object and context.active_object.data.attributes.active

    def execute(self, context):
        obj = context.active_object
        src_attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        bpy.ops.object.mode_set(mode='OBJECT')

        src_attrib = obj.data.attributes[src_attrib_name] # !important
        src_attrib_domain = src_attrib.domain
        src_attrib_data_type = src_attrib.data_type
        data_target_data_type = data.object_data_targets[self.data_target_enum].data_type
        data_target_compatible_domains = func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context)

        # Check if user input is valid.
        self.perform_user_input_test(obj, current_mode)

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

        # Set mesh data
        func.set_mesh_data(obj, self.data_target_enum, 
                           attrib_to_convert, 
                           face_map_name=self.attrib_name, 
                           vertex_group_name=self.attrib_name, 
                           enable_auto_smooth=self.b_enable_auto_smooth, 
                           apply_to_first_shape_key=self.b_apply_to_first_shape_key,
                           to_vgindex_weight=self.to_vgindex_weight,
                           to_vgindex_weight_mode=self.to_vgindex_weight_mode_enum,
                           to_vgindex_src_attrib=vg_weight_attrib,
                           uvmap_index=self.uvmaps_enum,
                           invert_sculpt_mask=self.b_invert_sculpt_mode_mask,
                           expand_sculpt_mask_mode=self.enum_expand_sculpt_mask_mode)
        
        # post-conversion cleanup
        if not domain_compatible or not data_type_compatible:
            obj.data.attributes.remove(obj.data.attributes[attribute_to_convert_name])

        if used_conveted_vgweight_attrib:
             obj.data.attributes.remove(obj.data.attributes[vg_weight_attrib_name])

        # remove if user enabled
        if self.b_delete_if_converted:
            obj.data.attributes.remove(obj.data.attributes[src_attrib_name])

        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        obj = context.active_object
        src_attrib = obj.data.attributes.active
        src_attrib_domain = src_attrib.domain
        src_attrib_data_type = src_attrib.data_type
        data_target_data_type = data.object_data_targets[self.data_target_enum].data_type
        data_target_compatible_domains = func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context)
        domain_compatible = src_attrib_domain in [dom[0] for dom in data_target_compatible_domains] 
        data_type_compatible = src_attrib_data_type == data_target_data_type

        row = self.layout
        row.prop(self, "data_target_enum", text="Target")

        # Setting the position attribute will not change the basis shape key, which might be unexpected.
        if self.data_target_enum in ['TO_POSITION'] and hasattr(obj.data.shape_keys, 'key_blocks'):
            row.prop(self, 'b_apply_to_first_shape_key')

        # Inform user that the suffix will be added to avoid crashing of blender.
        elif self.data_target_enum in ['TO_VERTEX_GROUP']:
            row.label(icon='INFO', text=f"Name will contain \"Group\" suffix")
        # Creates basis shape key when converting to shape keys, which is probably the expected result
        elif self.data_target_enum in ['TO_SHAPE_KEY'] and not obj.data.shape_keys:
            row.prop(self, 'b_create_basis_shape_key')

        # Custom name for face maps and vertex groups
        elif self.data_target_enum in ['TO_FACE_MAP', 'TO_VERTEX_GROUP']:
            row.prop(self, "attrib_name", text="Name")
        
        # Show a message that normals should be, well, normalized
        elif self.data_target_enum in ['TO_SPLIT_NORMALS']:
            row.label(icon='INFO', text=f"Blender expects normal vectors to be normalized")

            if not obj.data.use_auto_smooth:
                # After converting to custom split normals to see the result auto smooth needs to be enabled.
                row.prop(self, 'b_enable_auto_smooth')
                row.label(icon='ERROR', text=f"Custom normals are visible only with Auto Smooth")
        
        # Show modes to set the Vertex Group index
        elif self.data_target_enum in ['TO_VERTEX_GROUP_INDEX']:
            row.prop(self, 'to_vgindex_weight_mode_enum', text="Mode")
            if self.to_vgindex_weight_mode_enum == "ATTRIBUTE":
                # Show the dropdown menu to select the attribute with weights
                row.prop(self, 'to_vgindex_weights_attribute_enum', text='Attribute')

                # inform user if the weights attribute is invalid
                if self.to_vgindex_weights_attribute_enum != "NULL":
                    src_weight_attrib = obj.data.attributes[self.to_vgindex_weights_attribute_enum]
                    if src_weight_attrib.data_type  != 'FLOAT' or src_weight_attrib.domain  != 'POINT':
                        if src_weight_attrib.data_type  != 'FLOAT':
                            row.label(icon='ERROR', text=f"Weights Attribute values should be of Float data type")
                        if src_weight_attrib.domain  != 'POINT':
                            row.label(icon='ERROR', text=f"Weights Attribute should be stored in Vertex domain")
                        row.label(icon='ERROR', text=f"This might not yield good results")
                    
            else:
                row.prop(self, 'to_vgindex_weight')

        # UVMap selector
        elif self.data_target_enum in ["TO_SELECTED_VERTICES_IN_UV_EDITOR", "TO_SELECTED_EDGES_IN_UV_EDITOR"]:
            row.prop(self, 'uvmaps_enum', text="UVMap")
        
        # Show options for sculpt mode mask conversion
        elif self.data_target_enum == 'TO_SCULPT_MODE_MASK':
            row.prop(self, "b_invert_sculpt_mode_mask")
            row.prop(self, "enum_expand_sculpt_mask_mode", text='Mode')
            
        # Show conversion options if data type or domain of attribute is not compatible
        if not domain_compatible or not data_type_compatible:
            
            # Not compatible domain
            if not domain_compatible:   
                row.label(icon='ERROR', text=f"This data cannot be stored in {func.get_friendly_domain_name(src_attrib_domain)}")
                if len(data_target_compatible_domains) == 1:
                    row.label(text=f"Will be stored in {func.get_friendly_domain_name(self.convert_to_domain_enum)}")
                else:
                    row.prop(self, "convert_to_domain_enum")
            
            # Not compatible data type
            if not data_type_compatible:
                row.label(icon='ERROR', text=f"This data does not store {func.get_friendly_data_type_name(src_attrib_data_type)}")
                row.label(text=f"Converting to {func.get_friendly_data_type_name(data_target_data_type)}")
            
            row.label(icon='ERROR', text=f"This might not yield good results")
        
        row.prop(self, 'b_delete_if_converted')

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

    def get_attribute_data_length(self, obj, a):
        if a.domain == 'POINT':
            return len(obj.data.vertices)
        elif a.domain == 'EDGE':
            return len(obj.data.edges)
        elif a.domain == 'FACE':
            return len(obj.data.faces)
        else:
            return len(obj.data.loops)

    @classmethod
    def poll(self, context):
        if not context.active_object:
            return False
        
        active_attrib = context.active_object.data.attributes.active
        selected_more_than_one_obj = len(context.selected_objects) > 1 
        valid_object_types = True not in [obj.type != 'MESH' for obj in bpy.context.selected_objects]
        
        # Check if the attribute can be copied
        if active_attrib:
            valid_attribute = not bool(len([atype for atype in func.get_attribute_types(active_attrib) if atype in [data.EAttributeType.INTERNAL, data.EAttributeType.READONLY]]))
        else:
            valid_attribute = False

        if not active_attrib:
            self.poll_message_set("No active attribute")
        elif not selected_more_than_one_obj:
            self.poll_message_set("Select multiple objects")  
        elif not valid_object_types:
            self.poll_message_set("One of selected objects is not a mesh")
        elif not valid_attribute:
            self.poll_message_set("Can't copy this attribute")

        return all([selected_more_than_one_obj, active_attrib, valid_object_types, valid_attribute])

    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        src_attrib_name = obj.data.attributes.active.name
        bpy.ops.object.mode_set(mode='OBJECT')
        src_attrib = obj.data.attributes[src_attrib_name] # !important
        a_vals = func.get_attrib_values(src_attrib, obj)

        # get size of the source attribute domain
        source_size = self.get_attribute_data_length(obj, src_attrib)

        for sel_obj in [sel_obj for sel_obj in bpy.context.selected_objects if sel_obj.type =='MESH' and sel_obj is not obj]:
            sel_obj_attr = None
        
            # check if present in target mesh
            if src_attrib_name in [a.name for a in sel_obj.data.attributes]:
                sel_obj_attr = sel_obj.data.attributes[src_attrib_name]

                # overwrite if present?
                if not self.b_overwrite:
                    continue
                
                #overwrite different type?
                not_same_type = sel_obj_attr.domain != src_attrib.domain or sel_obj_attr.data_type != src_attrib.domain
                if not_same_type and not self.b_overwrite_different_type:
                    continue
                
                # remove current if overwriting
                elif not_same_type:
                    sel_obj.data.attributes.remove(sel_obj_attr)
                    
            # create new attribute with target settings
            sel_obj_attr = sel_obj.data.attributes.new(name=src_attrib_name, type=src_attrib.data_type, domain=src_attrib.domain)
            
            # size check

            # check if the target mesh has different amount of faces/verts/etc.
            target_size = self.get_attribute_data_length(sel_obj, sel_obj_attr)

            if sel_obj_attr.domain == 'POINT':
                target_size = len(sel_obj.data.vertices)
            elif sel_obj_attr.domain == 'EDGE':
                target_size = len(sel_obj.data.edges)
            elif sel_obj_attr.domain == 'FACE':
                target_size = len(sel_obj.data.faces)
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
                        fill_value = func.get_attrib_default_value(src_attrib)
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

        obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

    def draw(self, context):
        row = self.layout
        row.prop(self, "b_overwrite", text="Overwrite if exists")
        row.prop(self, "b_overwrite_different_type", text="Overwrite different type")
        row.prop(self, "extend_mode_enum", text="Extend Mode")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class ConditionalSelection(bpy.types.Operator):
    bl_idname = "mesh.attribute_conditioned_select"
    bl_label = "Select in edit mode by condition"
    bl_description = "Select mesh domain by attribute value with specified conditions"
    bl_options = {'REGISTER', 'UNDO'}

    # Whether to deselect the domain that meets the condition
    b_deselect: bpy.props.BoolProperty(name="Deselect", default=False)

    # All conditions for attributes containing numeric values
    attribute_comparison_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum
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
            ("RGBA", "RGBA", ""),
            ("HSVA", "HSVA", ""),
        ],
        default="RGBA"
    )

    # The mode to check individual vector float values with. Either all of the values need to meet the conditions or one of them.
    vector_value_cmp_type_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("AND", "Needs to meet all of above (AND)", "All of the conditions above need to be met"),
            ("OR", "Needs to meet any of above (OR)", "Any of the conditions above need to be met"),
        ],
        default="AND"
    )

    # ALL GUI INPUT BOXES
    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_bool: bpy.props.BoolProperty(name="Boolean Value", default=False)
    val_vector2d: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if etc.get_blender_support(data.attribute_data_types['INT32_2D'].min_blender_ver, data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))

    # The values to compare to, for each type of vector attributes.

    val_float_x: bpy.props.FloatProperty(name="X", default=0.0)
    val_float_y: bpy.props.FloatProperty(name="Y", default=0.0)
    val_float_z: bpy.props.FloatProperty(name="Z", default=0.0)
    val_float_w: bpy.props.FloatProperty(name="W", default=0.0)

    val_int_x: bpy.props.IntProperty(name="X", default=0)
    val_int_y: bpy.props.IntProperty(name="Y", default=0)
    val_int_z: bpy.props.IntProperty(name="Z", default=0)
    val_int_w: bpy.props.IntProperty(name="W", default=0)

    val_float_color_x: bpy.props.FloatProperty(name="X", default=0.0, min=0.0, max=1.0)
    val_float_color_y: bpy.props.FloatProperty(name="Y", default=0.0, min=0.0, max=1.0)
    val_float_color_z: bpy.props.FloatProperty(name="Z", default=0.0, min=0.0, max=1.0)
    val_float_color_w: bpy.props.FloatProperty(name="W", default=0.0, min=0.0, max=1.0)

    # Toggles for enabling comparing the individual vector/color values

    val_vector_x_toggle: bpy.props.BoolProperty(name="X", default=False)
    val_vector_y_toggle: bpy.props.BoolProperty(name="Y", default=False)
    val_vector_z_toggle: bpy.props.BoolProperty(name="Z", default=False)
    val_vector_w_toggle: bpy.props.BoolProperty(name="W", default=False)

    # The comparision modes between each of vector/color values

    vec_x_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum,
    )
    vec_y_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum,
    )
    vec_z_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum,
    )
    vec_w_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.get_attribute_comparison_conditions_enum,
    )


    @classmethod
    def poll(self, context):
        return func.conditional_selection_poll(self, context)
    
    def execute(self, context):
        
        obj = context.active_object
        current_mode = obj.mode
        
        attribute_name = obj.data.attributes.active.name
        bpy.ops.object.mode_set(mode='OBJECT')
        attrib = obj.data.attributes[attribute_name]

        condition = ""
        comparison_value = None
        attrib_data_type = attrib.data_type
        case_sensitive_comp = False
        filtered_indexes = []
        
        def debug_print():
            print(f"""ConditionalSelectionTrigger
Cond: {condition}
CompVal: {comparison_value}
DataType: {attrib_data_type}
CaseSensitive: {case_sensitive_comp}
FiltIndex: {filtered_indexes}""")

        

        def compare_float_individual_vals(vals_list, mode='AND'):
            """
            Compares list of floats containing indiviual vertex values eg [X[x1,x2,x3] Y[y1,y2,y3] Z[z1,z2,z3]]"""
            if mode == 'AND':
            # compare to each other "and"
                for i in range(1, len(vals_list)):
                    for num in vals_list[0]:
                        if num not in vals_list[i]:
                            vals_list[0].remove(num)
                return vals_list[0]
            elif mode == 'OR':
                r = []
                for dimension in vals_list:
                    r += dimension
                return list(set(r))

        #case 1: single number/value
        if attrib_data_type in ['FLOAT', 'INT', 'INT8', 'STRING', 'BOOLEAN']:
            if attrib_data_type in ['FLOAT', 'INT', 'INT8']:
                condition = self.numeric_condition_enum
                if attrib_data_type == 'INT':
                    comparison_value = self.val_int
                elif attrib_data_type == 'INT8':
                    comparison_value = self.val_int8
                elif attrib_data_type == 'FLOAT':
                    comparison_value = self.val_float

            elif attrib_data_type == 'BOOLEAN':
                    condition = self.bool_condition_enum
                    comparison_value = self.val_bool

            elif attrib_data_type == 'STRING':
                condition = self.string_condition_enum
                comparison_value = self.val_string
                case_sensitive_comp = self.b_string_case_sensitive

            filtered_indexes = func.get_filtered_indexes_by_condition([entry.value for entry in attrib.data], condition, comparison_value, case_sensitive_comp)

            
        # case 2: multiple values
        elif attrib_data_type in ['FLOAT_VECTOR', 'FLOAT2']:
            vals_to_cmp = []
            filtered_indexes = []

            if self.val_vector_x_toggle or self.val_vector_y_toggle or self.val_vector_z_toggle:
                #x
                if self.val_vector_x_toggle:
                    condition = self.vec_x_condition_enum
                    comparison_value = self.val_float_x
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.vector[0] for entry in attrib.data], condition, comparison_value))

                #y
                if self.val_vector_y_toggle:
                    condition = self.vec_y_condition_enum
                    comparison_value = self.val_float_y
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.vector[1] for entry in attrib.data], condition, comparison_value))
                
                if attrib_data_type == 'FLOAT_VECTOR' and self.val_vector_z_toggle:
                    #z
                    condition = self.vec_z_condition_enum
                    comparison_value = self.val_float_z
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.vector[2] for entry in attrib.data], condition, comparison_value))
                
                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type_enum)

        elif attrib_data_type in ['FLOAT_COLOR', 'BYTE_COLOR']:
            vals_to_cmp = []
            filtered_indexes = []

            # value editor for RGB/hsv values
            if self.val_vector_x_toggle or self.val_vector_y_toggle or self.val_vector_z_toggle or self.val_vector_w_toggle:
                
                colors = []
                for entry in attrib.data:
                    color = entry.color

                    if self.color_value_type_enum == 'HSVA':
                        hsv = list(colorsys.rgb_to_hsv(color[0], color[1], color[2])) + [color[3]]
                        colors.append(hsv)
                        if func.is_verbose_mode_enabled():
                            print(f"rgb: {list(entry.color)} -> hsv: {hsv}")
                    else:
                        colors.append((color[0], color[1], color[2], color[3]))
                    
                #r
                if self.val_vector_x_toggle:
                    condition = self.vec_x_condition_enum
                    comparison_value = self.val_float_color_x #if self.color_gui_mode_enum == 'VALUE' else self.val_color[0]
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([c[0] for c in colors], condition, comparison_value))

                #g
                if self.val_vector_y_toggle:
                    condition = self.vec_y_condition_enum
                    comparison_value = self.val_float_color_y #if self.color_gui_mode_enum == 'VALUE' else self.val_color[1]
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([c[1] for c in colors], condition, comparison_value))
                
                #b
                if self.val_vector_z_toggle:
                    
                    condition = self.vec_z_condition_enum
                    comparison_value = self.val_float_color_z #if self.color_gui_mode_enum == 'VALUE' else self.val_color[2]
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([c[2] for c in colors], condition, comparison_value))

                #a
                if self.val_vector_w_toggle:
                    condition = self.vec_w_condition_enum
                    comparison_value = self.val_float_color_w #if self.color_gui_mode_enum == 'VALUE' else self.val_color[3]
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([c[3] for c in colors], condition, comparison_value))

                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type_enum)

        # case 3: integer vector values (.VALUE PROPERTY, NOT .VECTOR)
        elif attrib_data_type in ['INT32_2D']:
            vals_to_cmp = []
            filtered_indexes = []
            if self.val_vector_x_toggle or self.val_vector_y_toggle or self.val_vector_z_toggle:
                #x
                if self.val_vector_x_toggle:
                    condition = self.vec_x_condition_enum
                    comparison_value = self.val_int_x
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[0] for entry in attrib.data], condition, comparison_value))

                #y
                if self.val_vector_y_toggle:
                    condition = self.vec_y_condition_enum
                    comparison_value = self.val_int_y
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[1] for entry in attrib.data], condition, comparison_value))
                
                # if attrib_data_type in ['QUATERNION'] and self.val_vector_z_toggle:
                #     #z
                #     condition = self.vec_z_condition_enum
                #     comparison_value = self.val_int_z
                #     vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[2] for entry in attrib.data], condition, comparison_value))

                # if attrib_data_type in ['QUATERNION'] and self.val_vector_w_toggle:
                #     #w
                #     condition = self.vec_w_condition_enum
                #     comparison_value = self.val_int_w
                #     vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[3] for entry in attrib.data], condition, comparison_value))

                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type_enum)
        
        # case 4: float vector values with .value property
        elif attrib_data_type in ['QUATERNION']:
            vals_to_cmp = []
            filtered_indexes = []
            if self.val_vector_x_toggle or self.val_vector_y_toggle or self.val_vector_z_toggle:
                #x
                if self.val_vector_x_toggle:
                    condition = self.vec_x_condition_enum
                    comparison_value = self.val_float_x
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[0] for entry in attrib.data], condition, comparison_value))

                #y
                if self.val_vector_y_toggle:
                    condition = self.vec_y_condition_enum
                    comparison_value = self.val_float_y
                    vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[1] for entry in attrib.data], condition, comparison_value))
                
                # if attrib_data_type in ['QUATERNION'] and self.val_vector_z_toggle:
                    #z
                condition = self.vec_z_condition_enum
                comparison_value = self.val_float_z
                vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[2] for entry in attrib.data], condition, comparison_value))

                # if attrib_data_type in ['QUATERNION'] and self.val_vector_w_toggle:
                    #w
                condition = self.vec_w_condition_enum
                comparison_value = self.val_float_w
                vals_to_cmp.append(func.get_filtered_indexes_by_condition([entry.value[3] for entry in attrib.data], condition, comparison_value))

                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type_enum)

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

        row = self.layout

        if attribute.data_type == 'BOOLEAN':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "attribute_comparison_condition_enum", text="")
            grid.prop(self, "val_bool", text="Value")

        elif attribute.data_type == 'STRING':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "string_condition_enum", text="")
            grid.prop(self, "val_string", text="Value")

            row.prop(self, "string_case_sensitive_bool", text="Case Sensitive")

        elif attribute.data_type == 'INT':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "attribute_comparison_condition_enum", text="")
            grid.prop(self, "val_int", text="Value")

        elif attribute.data_type == 'INT8':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "attribute_comparison_condition_enum", text="")
            grid.prop(self, "val_int8", text="Value")
        
        elif attribute.data_type == 'FLOAT':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "attribute_comparison_condition_enum", text="")
            grid.prop(self, "val_float", text="Value")

        # VEC FLOAT2
        elif attribute.data_type in ['FLOAT2', 'FLOAT_VECTOR']:


            row.prop(self, "val_vector_x_toggle", text="X")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_x_toggle
            grid.prop(self, "vec_x_condition_enum", text="")
            grid.prop(self, "val_float_x", text="Value")


            row.prop(self, "val_vector_y_toggle", text="Y")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_y_toggle
            grid.prop(self, "vec_y_condition_enum", text="")
            grid.prop(self, "val_float_y", text="Value")  
            

            if attribute.data_type == 'FLOAT_VECTOR':
                row.prop(self, "val_vector_z_toggle", text="Z")

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_z_toggle
                grid.prop(self, "vec_z_condition_enum", text="")
                grid.prop(self, "val_float_z", text="Value") 
            row.prop(self, 'vector_value_cmp_type_enum')

        # COLOR
        elif attribute.data_type in ['FLOAT_COLOR', 'BYTE_COLOR']:
                #row.prop(self, "color_gui_mode_enum", text="Mode")
            
            

            # show normal color picker, if set to value then show values in grids
            # if self.color_gui_mode_enum == 'COLOR':
            #     row.prop(self, "val_color", text="Value")
                self.color_gui_mode_enum = 'VALUE'
                
            # elif self.color_gui_mode_enum == 'VALUE':
                # gui that compares individual values like a vector, with hsv mode too
                row.prop(self, "color_value_type_enum", text="Value Type")

                rgb = True if self.color_value_type_enum == 'RGBA' else False

                row.prop(self, "val_vector_x_toggle", text="Red" if rgb else 'Hue')

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_x_toggle
                grid.prop(self, "vec_x_condition_enum", text="")
                if self.color_gui_mode_enum == 'VALUE':
                    grid.prop(self, "val_float_color_x", text="Value")

                row.prop(self, "val_vector_y_toggle", text="Green" if rgb else 'Saturation')

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_y_toggle
                grid.prop(self, "vec_y_condition_enum", text="")
                if self.color_gui_mode_enum == 'VALUE':
                    grid.prop(self, "val_float_color_y", text="Value")  
                
                row.prop(self, "val_vector_z_toggle", text="Blue" if rgb else 'Value')

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_z_toggle
                grid.prop(self, "vec_z_condition_enum", text="")
                if self.color_gui_mode_enum == 'VALUE':
                    grid.prop(self, "val_float_color_z", text="Value") 

                row.prop(self, "val_vector_w_toggle", text="Alpha")
                
                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_w_toggle
                grid.prop(self, "vec_w_condition_enum", text="")
                if self.color_gui_mode_enum == 'VALUE':
                    grid.prop(self, "val_float_color_w", text="Value")
                    
                row.prop(self, 'vector_value_cmp_type_enum')

        # INT32_2D
        elif attribute.data_type in ['INT32_2D']:

            row.prop(self, "val_vector_x_toggle", text="X")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_x_toggle
            grid.prop(self, "vec_x_condition_enum", text="")
            grid.prop(self, "val_int_x", text="Value")


            row.prop(self, "val_vector_y_toggle", text="Y")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_y_toggle
            grid.prop(self, "vec_y_condition_enum", text="")
            grid.prop(self, "val_int_y", text="Value") 
            row.prop(self, 'vector_value_cmp_type_enum') 
            

            # if attribute.data_type in ['QUATERNION']:
            #     row.prop(self, "val_vector_z_toggle", text="Z")

            #     grid = row.grid_flow(columns=2, even_columns=True)
            #     grid.enabled = self.val_vector_z_toggle
            #     grid.prop(self, "vec_z_condition_enum", text="")
            #     grid.prop(self, "val_int_z", text="Value") 
            
            # if attribute.data_type in ['QUATERNION']:
            #     row.prop(self, "val_vector_w_toggle", text="W")

            #     grid = row.grid_flow(columns=2, even_columns=True)
            #     grid.enabled = self.val_vector_z_toggle
            #     grid.prop(self, "vec_w_condition_enum", text="")
            #     grid.prop(self, "val_int_w", text="Value") 

        # QUATERNION
        elif attribute.data_type in ['QUATERNION']:

            row.prop(self, "val_vector_x_toggle", text="X")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_x_toggle
            grid.prop(self, "vec_x_condition_enum", text="")
            grid.prop(self, "val_float_x", text="Value")


            row.prop(self, "val_vector_y_toggle", text="Y")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_y_toggle
            grid.prop(self, "vec_y_condition_enum", text="")
            grid.prop(self, "val_float_y", text="Value") 
            

            row.prop(self, "val_vector_z_toggle", text="Z")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_z_toggle
            grid.prop(self, "vec_z_condition_enum", text="")
            grid.prop(self, "val_float_z", text="Value") 
        

            row.prop(self, "val_vector_w_toggle", text="W")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_z_toggle
            grid.prop(self, "vec_w_condition_enum", text="")
            grid.prop(self, "val_float_w", text="Value") 

            row.prop(self, 'vector_value_cmp_type_enum') 

        row.prop(self, 'b_deselect')         

class SelectDomainWithAttributeZeroValue(bpy.types.Operator):
    """
    Used in gui to select domains with non-zero value
    """
    bl_idname = "mesh.attribute_zero_value_select"
    bl_label = "Select Domain With Zero Value of Current Attribute"
    bl_description = "Select attribute with non-zero value"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dt = context.active_object.data.attributes.active.data_type
        
        # do not compare alpha value
        if dt in ['FLOAT_COLOR', 'BYTE_COLOR']:
            w_toggle = False
        else:
            w_toggle = True

        # set default value to 1.0 for quats
        if dt == "QUATERNION":
            val_float_x = 1.0
        else:
            val_float_x = 0.0
        bpy.ops.mesh.attribute_conditioned_select('EXEC_DEFAULT', 
                                                b_deselect = False,
                                                val_float = 0.0,
                                                val_int = 0,
                                                numeric_condition_enum = 'NEQ',
                                                vec_x_condition_enum = "NEQ",
                                                vec_y_condition_enum = "NEQ",
                                                vec_z_condition_enum = "NEQ",
                                                vec_w_condition_enum = "NEQ",
                                                string_condition_enum = 'NEQ',
                                                vector_value_cmp_type_enum = 'OR',
                                                bool_condition_enum = "EQ",
                                                val_vector_x_toggle = True,
                                                val_vector_y_toggle = True,
                                                val_vector_z_toggle = True,
                                                val_vector_w_toggle = w_toggle,
                                                val_float_x = val_float_x,
                                                val_float_y = 0.0,
                                                val_float_z = 0.0,
                                                val_float_w = 0.0,
                                                val_float_color_x = 0.0,
                                                val_float_color_y = 0.0,
                                                val_float_color_z = 0.0,
                                                val_float_color_w = 0.0,
                                                val_string = "",
                                                val_bool = True,
                                                val_int_x = 0,
                                                val_int_y = 0,
                                                val_int8 = 0)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return func.conditional_selection_poll(self, context)

class DeSelectDomainWithAttributeZeroValue(bpy.types.Operator):
    """
    Used in gui to deselect domains with non-zero value
    """
    bl_idname = "mesh.attribute_zero_value_deselect"
    bl_label = "Deselect Domain With Zero Value of Current Attribute"
    bl_description = "Deselect attribute with non-zero value"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dt = context.active_object.data.attributes.active.data_type
        
        # do not compare alpha value
        if dt in ['FLOAT_COLOR', 'BYTE_COLOR']:
            w_toggle = False
        else:
            w_toggle = True

        # set default value to 1.0 for quats
        if dt == "QUATERNION":
            val_float_x = 1.0
        else:
            val_float_x = 0.0
        bpy.ops.mesh.attribute_conditioned_select('EXEC_DEFAULT', 
                                                b_deselect = True,
                                                val_float = 0.0,
                                                val_int = 0,
                                                numeric_condition_enum = 'NEQ',
                                                vec_x_condition_enum = "NEQ",
                                                vec_y_condition_enum = "NEQ",
                                                vec_z_condition_enum = "NEQ",
                                                vec_w_condition_enum = "NEQ",
                                                string_condition_enum = 'NEQ',
                                                vector_value_cmp_type_enum = 'OR',
                                                bool_condition_enum = "EQ",
                                                val_vector_x_toggle = True,
                                                val_vector_y_toggle = True,
                                                val_vector_z_toggle = True,
                                                val_vector_w_toggle = w_toggle,
                                                val_float_x = val_float_x,
                                                val_float_y = 0.0,
                                                val_float_z = 0.0,
                                                val_float_w = 0.0,
                                                val_float_color_x = 0.0,
                                                val_float_color_y = 0.0,
                                                val_float_color_z = 0.0,
                                                val_float_color_w = 0.0,
                                                val_string = "",
                                                val_bool = True,
                                                val_int_x = 0,
                                                val_int_y = 0,
                                                val_int8 = 0)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return func.conditional_selection_poll(self, context)

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
            return False
        
        valid_object_types = context.active_object.type == 'MESH'
        valid_attributes = len(context.active_object.data.attributes)
        if not valid_object_types:
            self.poll_message_set("Selected object is not a mesh")
        elif not valid_attributes:
            self.poll_message_set("No attributes")

        return all([valid_object_types, valid_attributes])

    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        restricted_names = []

        # get vertex groups name, if any
        vg_names = [vg.name for vg in obj.vertex_groups]
        restricted_names += vg_names

        # get UVMap names, if any
        uvm_names = [uv.name for uv in obj.data.uv_layers]
        restricted_names += uvm_names

        # get color attrib names, if any
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
                if (not bool(len([atype for atype in atypes if atype in [data.EAttributeType.HIDDEN, data.EAttributeType.CANTREMOVE, data.EAttributeType.READONLY]])) 
                    or (obj.data.attributes[i].data_type == 'FLOAT2' and obj.data.attributes[i].domain == 'CORNER' and bpy.app.version >= (3,5,0)) #ignore uvmaps, they're auto renamed if bl > 3,5
                    or (obj.data.attributes[i].data_type in ['FLOAT_COLOR', 'BYTE_COLOR'] and obj.data.attributes[i].domain in ['POINT', 'CORNER'])): # same for color attribs
                    failed += 1
                else:
                    renamed +=1
                    j = 0
                    while obj.data.attributes[i].name in restricted_names:
                        j += 1
                        obj.data.attributes[i].name = str(obj.data.attributes[i].name) + "." + str(j).zfill(3)
                    
        self.report({'INFO'}, f"Renamed {str(renamed)} attribute" + ("s" if renamed > 1 else ""))

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

# class ReadValueFromActiveDomain(bpy.types.Operator):
#     bl_idname = "mesh.attribute_read_value_from_active_domain"
#     bl_label = "Sample from active domain"
#     bl_description = "Reads the attribute value under active domain and sets it in GUI"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         # check if its a mesh
#         return False

#     def execute(self, context):
#         return 

# TODO
# class ConditionedRemoveAttribute(bpy.types.Operator):
#     bl_idname = "mesh.attribute_conditioned_remove"
#     bl_label = "Remove by Condition"
#     bl_description = "Removes attributes by condition"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         return False

#     def execute(self, context):
#         return 
