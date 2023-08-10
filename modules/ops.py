

# ops
# --------------------------------------------

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
    
    clear: bpy.props.BoolProperty(name="clear", default = False)
    fc_spill: bpy.props.BoolProperty(name="Face Corner Spill", default = False)

    @classmethod
    def poll(self, context):
        return (context.active_object
                and context.active_object.mode == 'EDIT' 
                and context.active_object.type == 'MESH' 
                and context.active_object.data.attributes.active 
                and func.get_is_attribute_valid(context.active_object.data.attributes.active.name))


    def execute(self, context):
        obj = context.active_object
        active_attrib_name = obj.data.attributes.active.name 

        bpy.ops.object.mode_set(mode='OBJECT')
        if etc.verbose_mode:
            print( f"Working on {active_attrib_name} attribute" )

        attribute = obj.data.attributes[active_attrib_name] #!important

        # Get value from GUI
        prop_group = context.object.MAME_PropValues
        dt = attribute.data_type
        if dt == "FLOAT":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_float
        elif dt == "INT":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_int
        elif dt == "FLOAT_VECTOR":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_vector
        elif dt == "FLOAT_COLOR":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_color
        elif dt == "BYTE_COLOR":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_bytecolor
        elif dt == "STRING":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_string
        elif dt == "BOOLEAN":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_bool
        elif dt == "FLOAT2":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_vector2d
        elif dt == "INT8":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_int8
        elif dt == "INT32_2D":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_int32_2d
        elif dt == "QUATERNION":
            value = func.get_attrib_default_value(attribute) if self.clear else prop_group.val_quaternion
        else:
            self.report({'ERROR', "Unsupported data type!"})

        # Set the value
        func.set_attribute_value_on_selection(self, context, obj, attribute, value, face_corner_spill=self.fc_spill)
        
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

    attrib_name: bpy.props.StringProperty(name="Attribute Name", default="", description="New attribute name. Leave blank for automatic name")

    domain_data_type: bpy.props.EnumProperty(
        name="Domain Data",
        description="Select an option",
        items=func.get_source_data_enum
    )

    target_attrib_domain: bpy.props.EnumProperty(
        name="Attribute Domain",
        description="Select an option",
        items=func.get_natively_supported_domains_enum
    )

    batch_convert_enabled: bpy.props.BoolProperty(
        name="Batch Convert And Create Attributes", 
        description="Convert all vertex groups/shape keys/face maps/... at once", 
        default=False)
    
    # used for batch shape key offset attribute creation
    batch_convert_sk_offset_src_toggle: bpy.props.BoolProperty(
        name="Set \"Offset to\" instead of \"Offset From\"", 
        description="", 
        default=False)
    
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

    enum_shape_keys_offset_source: bpy.props.EnumProperty(
        name="Offset from",
        description="Select an option",
        items=func.get_shape_keys_enum
    )
    
    # Converter props

    auto_convert: bpy.props.BoolProperty(name="Convert Attribute", description="Auto converts created attribute to another domain or type", default=False)
    
    enum_attrib_converter_mode:bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=[("GENERIC", "Generic", ""),
               ("VERTEX_GROUP", "Vertex Group", ""),],
        default="GENERIC",
    )

    enum_attrib_converter_domain:bpy.props.EnumProperty(
        name="Domain",
        description="Select an option",
        items=func.get_attribute_domains_enum,
    )

    enum_attrib_converter_datatype: bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=func.get_attribute_data_types_enum,
    )

    def perform_user_input_test(self):
        """
        Checks for all user input in gui
        """

        #check if selection even exists
        if not self.domain_data_type in data.object_data_sources:
            self.report({'ERROR'}, f"Can't find this data source {self.domain_data_type}. Contact developer.")
            return False

        # Check if the user has selected input data if applicable to specific sources:
        if self.domain_data_type in ["FACE_FROM_FACE_MAP"]:
            if self.enum_face_maps == 'NULL':
                if not self.batch_convert_enabled:
                    self.report({'ERROR'}, f"No Face Map Selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No Face Maps. Nothing done")
                
                return False
                
    
        # material slots
        if self.domain_data_type in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"]:
            if self.enum_material_slots == 'NULL':
                if not self.batch_convert_enabled:
                    self.report({'ERROR'}, f"No material slot selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No Material slots. Nothing done")

                return False
    
        # materials
        if self.domain_data_type in ["FACE_IS_MATERIAL_ASSIGNED"]:
            if self.enum_materials == 'NULL':
                if not self.batch_convert_enabled:
                    self.report({'ERROR'}, f"No Materials assigned. Nothing done")
                else:
                    self.report({'ERROR'}, f"No Materials. Nothing done")
                
                return False
    
        # shape keys
        if self.domain_data_type ==  "VERT_SHAPE_KEY_POSITION_OFFSET":

            if self.batch_convert_enabled:
                if not self.batch_convert_sk_offset_src_toggle and self.enum_shape_keys_offset_source == 'NULL':
                        self.report({'ERROR'}, f"Source shape key to get offset from is invalid. Nothing done")
                        return False

                if self.batch_convert_sk_offset_src_toggle and self.enum_shape_keys == 'NULL':
                    self.report({'ERROR'}, f"Target shape key to get offset from is invalid. Nothing done")
                    return False
                
            
        if self.domain_data_type ==  "VERT_SHAPE_KEY_POSITION":
            if self.enum_shape_keys == 'NULL':
                if not self.batch_convert_enabled:
                    self.report({'ERROR'}, f"No shape key selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No shape keys. Nothing done")
                return False
        
        # vertex groups
        if self.domain_data_type in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"]: # ???????????
            if self.enum_vertex_groups == 'NULL':
                if not self.batch_convert_enabled:
                    self.report({'ERROR'}, f"No vertex group selected. Nothing done")
                else:
                    self.report({'ERROR'}, f"No vertex groups. Nothing done")
                return False

        # invalid domain enum for multiple choices
        if len(data.object_data_sources[self.domain_data_type].domains_supported) > 1 and self.target_attrib_domain == '':
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

        # Check for user input
        if not self.perform_user_input_test():
            bpy.ops.object.mode_set(mode=mode)
            return {'CANCELLED'}


        # Get default value if default was chosen
        if self.target_attrib_domain =="DEFAULT":
            self.target_attrib_domain = data.object_data_sources[self.domain_data_type].attribute_domain_on_default

        # Read prefixes and suffixes of automatic naming
        data_type = data.object_data_sources[self.domain_data_type].data_type
        

        # Single assignment to single attribute
        if etc.verbose_mode:
            print(f"Batch mode supported & enabled: {not (not data.object_data_sources[self.domain_data_type].batch_convert_support or not self.batch_convert_enabled) }")
        if not data.object_data_sources[self.domain_data_type].batch_convert_support or not self.batch_convert_enabled:
            
            # Automatic name
            
            if self.attrib_name == "":
                name = data.object_data_sources[self.domain_data_type].attribute_auto_name
                # this is dirty but it already gets the right data so...
                # If the enum is NONE then likely this option in GUI was hidden, and is not used. Checks for user input validity in given context were done before
                name = name.format(domain=func.get_friendly_domain_name(self.target_attrib_domain, plural=True), 
                                face_map=func.get_face_maps_enum(self, context)[int(self.enum_face_maps)][1] if self.enum_face_maps != 'NULL' else None,
                                shape_key=func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None, 
                                shape_key_offset_from=func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_source)][1] if self.enum_shape_keys_offset_source != 'NULL' else None, 
                                vertex_group=func.get_vertex_groups_enum(self, context)[int(self.enum_vertex_groups)][1] if self.enum_vertex_groups != 'NULL' else None, 
                                material=func.get_materials_enum(self, context)[int(self.enum_materials)][1] if self.enum_materials != 'NULL' else None, 
                                material_slot=func.get_material_slots_enum(self, context)[int(self.enum_material_slots)][1] if self.enum_material_slots != 'NULL' else None) 
            else:
                name = self.attrib_name
            name = func.get_safe_attrib_name(obj, name) # naming the same way as vertex group will crash blender.
            attrib = obj.data.attributes.new(name=name, type=data_type, domain=self.target_attrib_domain)
            obj_data = func.get_mesh_data(obj, 
                                        self.domain_data_type, 
                                        self.target_attrib_domain, 
                                        vg_index=self.enum_vertex_groups,
                                        sk_index=self.enum_shape_keys,
                                        sk_offset_index=self.enum_shape_keys_offset_source,
                                        fm_index=self.enum_face_maps,
                                        sel_mat=self.enum_materials,
                                        mat_index=self.enum_material_slots)
            if etc.verbose_mode:
                print(f"Creating attribute from data: {obj_data}")
            func.set_attribute_values(attrib, obj_data)

            # convert if enabled
            if self.auto_convert:
                func.convert_attribute(self, obj, attrib.name, mode=self.enum_attrib_converter_mode, 
                                               domain=self.enum_attrib_converter_domain, 
                                               data_type=self.enum_attrib_converter_datatype)

        # Assign all of type to n amount of attributes
        # This currently applies only to:
        # "VERT_IS_IN_VERTEX_GROUP", 
        # "VERT_FROM_VERTEX_GROUP", 
        # "VERT_SHAPE_KEY_POSITION_OFFSET", 
        # "VERT_SHAPE_KEY_POSITION",
        # "FACE_IS_MATERIAL_ASSIGNED", 
        # "FACE_IS_MATERIAL_SLOT_ASSIGNED", 
        # "FACE_FROM_FACE_MAP"
        else:
            for element in func.get_all_mesh_data_ids_of_type(obj, self.domain_data_type):
                
                if etc.verbose_mode:
                    print(f"Batch converting #{element}")

                # case: check for each group if vertex is in it, or get vertex weight for each vertex group for each vertex
                # each case, iterate over every vertex group
                if self.domain_data_type in ['VERT_IS_IN_VERTEX_GROUP', "VERT_FROM_VERTEX_GROUP"]: 
                    vertex_group_name = func.get_vertex_groups_enum(self, context)[element][1]

                    vg_index = element
                else:
                    vertex_group_name = None
                    vg_index = None


                shape_key = None
                shape_key_offset_from = None
                sk_index = None
                sk_offset_index = None

                # case: get shape key position for each shape key 
                if self.domain_data_type in ["VERT_SHAPE_KEY_POSITION"]:
                    shape_key = func.get_shape_keys_enum(self, context)[element][1]
                    sk_index = element
                    if etc.verbose_mode:
                        print(f"Source is shape key POS ({shape_key}), \nFROM: {func.get_shape_keys_enum(self, context)[element]} ")
                      

                # case: get shape key offset from specific one
                elif self.domain_data_type == 'VERT_SHAPE_KEY_POSITION_OFFSET':

                    # case: user wants to set offset from
                    if self.batch_convert_sk_offset_src_toggle:
                        shape_key = func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_source)][1]
                        shape_key_offset_from = func.get_shape_keys_enum(self, context)[element][1]
                        sk_index = self.enum_shape_keys
                        sk_offset_index = element
                    # case: user wants to set offset to
                    else:
                        shape_key = func.get_shape_keys_enum(self, context)[element][1]
                        shape_key_offset_from = func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1]
                        sk_index = element
                        sk_offset_index = self.enum_shape_keys_offset_source

                    if etc.verbose_mode:
                        print(f"Source is shape key offset, \n FROM: {func.get_shape_keys_enum(self, context)[element]} \n TO: {func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)]}")
                        
                # case: check for each material if it's assigned
                #iterate over every material
                if self.domain_data_type == "FACE_IS_MATERIAL_ASSIGNED":
                    material = func.get_materials_enum(self, context)[element][1]
                    sel_mat = element
                else:
                    material = None
                    sel_mat = None

                #case; check for each material slot if it's assigned
                # iterate over every material slot
                if self.domain_data_type == "FACE_IS_MATERIAL_SLOT_ASSIGNED":
                    material_slot = func.get_material_slots_enum(self, context)[element][1]
                    mat_index = element
                else:
                    material_slot = None
                    mat_index = None

                #case: check for each face map if it's assigned
                #iterate over every face map
                if self.domain_data_type == "FACE_FROM_FACE_MAP":
                    face_map = func.get_face_maps_enum(self, context)[element][1]
                    fm_index = element
                else:
                    face_map = None
                    fm_index = None

                # set name
                if self.attrib_name == "":
                    xname = data.object_data_sources[self.domain_data_type].attribute_auto_name
                    xname = xname.format(domain=func.get_friendly_domain_name(self.target_attrib_domain, plural=True), 
                                    face_map=face_map,
                                    shape_key=shape_key, 
                                    shape_key_offset_from=shape_key_offset_from, 
                                    vertex_group=vertex_group_name, 
                                    material=material, 
                                    material_slot=material_slot) 
                else:
                    xname = self.attrib_name

                xname = func.get_safe_attrib_name(obj, xname) # better be safe than sorry

                attrib = obj.data.attributes.new(name=xname, type=data_type, domain=self.target_attrib_domain)

                # There is a single exception: shape key offset, where user has to input from what this offset has to be
                
                obj_data = func.get_mesh_data(obj, 
                                        self.domain_data_type, 
                                        self.target_attrib_domain, 
                                        vg_index=vg_index,
                                        sk_index=sk_index,
                                        sk_offset_index=sk_offset_index,
                                        fm_index=fm_index,
                                        sel_mat=sel_mat,
                                        mat_index=mat_index)
                func.set_attribute_values(attrib, obj_data)

                # convert if enabled
                if self.auto_convert:
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
        batch_convert_support = False if self.domain_data_type == '' else data.object_data_sources[self.domain_data_type].batch_convert_support

        row = self.layout
        # if not (batch_convert_support and self.batch_convert_enabled):
        row.prop(self, "attrib_name", text="Name")
        if self.attrib_name == '':
            row.label(text="Using auto-generated name", icon='INFO')

        row.prop(self, "domain_data_type", text="Data")
        
        # read from domain, hide if only single is supported
        if len(func.get_natively_supported_domains_enum(self, context)) > 1:
            row.prop(self, "target_attrib_domain", text="From")

        row.label(text="")
        
        # face maps
        if self.domain_data_type in ["FACE_FROM_FACE_MAP"] and not self.batch_convert_enabled:
            row.prop(self, "enum_face_maps", text="Face Map")
        
        # material slots
        if self.domain_data_type in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"] and not self.batch_convert_enabled:
            row.prop(self, "enum_material_slots", text="Material Slot")
        
        # materials
        if self.domain_data_type in ["FACE_IS_MATERIAL_ASSIGNED"] and not self.batch_convert_enabled:
            row.prop(self, "enum_materials", text="Material")
        
        # shape keys
        if self.domain_data_type == "VERT_SHAPE_KEY_POSITION_OFFSET" or (self.domain_data_type == "VERT_SHAPE_KEY_POSITION" and not self.batch_convert_enabled):
            
            if self.domain_data_type ==  "VERT_SHAPE_KEY_POSITION_OFFSET":

                if not self.batch_convert_enabled or (not self.batch_convert_sk_offset_src_toggle):
                    row.prop(self, "enum_shape_keys_offset_source", text="Offset from")

                if not self.batch_convert_enabled or self.batch_convert_sk_offset_src_toggle:
                    row.prop(self, "enum_shape_keys", text="Offset To")
                
                if self.batch_convert_enabled:
                    row.prop(self, "batch_convert_sk_offset_src_toggle", text="Set \"Offset to\" instead of \"Offset From\"")

            if self.domain_data_type ==  "VERT_SHAPE_KEY_POSITION":
                row.prop(self, "enum_shape_keys", text="Shape Key")
                 
        # vertex groups
        if self.domain_data_type in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"] and not self.batch_convert_enabled:
            row.prop(self, "enum_vertex_groups", text="Vertex Group")
            
        # convert all of type to attrib
        if batch_convert_support:
            row.prop(self, "batch_convert_enabled", text="Batch Convert To Attributes")

        row.prop(self, "auto_convert", text="Convert Attribute After Creation")
        if self.auto_convert:
            row.label(text="Conversion Options")
            row.prop(self, "enum_attrib_converter_mode", text="Mode")
            if self.enum_attrib_converter_mode == 'GENERIC':
                row.prop(self, "enum_attrib_converter_domain", text="Domain")
                row.prop(self, "enum_attrib_converter_datatype", text="Data Type")

class DuplicateAttribute(bpy.types.Operator):
    """
    Simply duplicates an attribute"""

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

    def invert_attrib_color_mode_enum(self, context):
        # reverse
        return func.get_attribute_invert_modes(self, context)[::-1]

    edit_mode_selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Affect only selected in edit mode",
        default=False
    )

    edit_mode_face_corner_spill: bpy.props.BoolProperty(
        name="Face Corner Spill",
        description="Allow inverting value to nearby corners of selected vertices or limit it only to selected face",
        default=False
    )

    invert_mode: bpy.props.EnumProperty(
        name="Invert Mode",
        description="Select an option",
        items=func.get_attribute_invert_modes
    )

    color_invert_mode: bpy.props.EnumProperty(
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
        selected = [domain.index for domain in func.get_mesh_selected_by_domain(obj, src_attrib.domain, self.edit_mode_face_corner_spill)]
        if etc.verbose_mode:
            print(f"Selected domain indexes: {selected}")
        
        # No selection and selection mode is enabled?
        if not len(selected) and self.edit_mode_selected_only:
            self.report({'ERROR'}, f"No selection to perform the operations onto")
            bpy.ops.object.mode_set(mode=current_mode)
            return {'CANCELLED'}

        # # strings are different
        # if src_attrib.data_type == 'STRING':
        #     for i, dom in enumerate(src_attrib.data):
        #         if not self.edit_mode_selected_only or i in selected:
        #             dom.value = dom.value[::-1]
        
        # # numbers:
        # else:
        prop_name = func.get_attrib_value_propname(src_attrib)
        
        storage = func.get_attrib_values(src_attrib, obj)

        # create storage
        # if src_attrib.domain == 'POINT':
        #     storage = [func.get_attrib_default_value(src_attrib)] * len(obj.data.vertices)
        # elif src_attrib.domain == 'EDGE':
        #     storage = [func.get_attrib_default_value(src_attrib)] * len(obj.data.edges)
        # elif src_attrib.domain == 'FACE':
        #     storage = [func.get_attrib_default_value(src_attrib)] * len(obj.data.polygons)
        # else:
        #     storage = [func.get_attrib_default_value(src_attrib)] * len(obj.data.loops)

        # storage = list(storage)
        
        # int just get and multiply by -1
        if src_attrib.data_type in ['INT','INT8']:
            src_attrib.data.foreach_get(prop_name, storage)
            storage = [-v if not self.edit_mode_selected_only or i in selected else v for i, v in enumerate(storage) ]
        
        # strings reverse them
        elif src_attrib.data_type in ['STRING']:
            storage = [string[::-1] if not self.edit_mode_selected_only or i in selected else string for i, string in enumerate(storage) ]

        # for floats just get it as there is multiple modes
        elif src_attrib.data_type in ['FLOAT']:
            src_attrib.data.foreach_get(prop_name, storage)
        
        # booleans just not them
        elif src_attrib.data_type =='BOOLEAN':
            src_attrib.data.foreach_get(prop_name, storage)
            storage = [not v if not self.edit_mode_selected_only or i in selected else v for i, v in enumerate(storage)]
        
        # vectors get them as a single list
        elif src_attrib.data_type in ['FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR', 'QUATERNION', 'INT32_2D']:
            storage = [val for vec in storage for val in vec]
            src_attrib.data.foreach_get(prop_name, storage)

        # invert modes for vectors and float
        if src_attrib.data_type in ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR', 'QUATERNION', 'INT32_2D']:
            invert_mode = self.color_invert_mode if src_attrib.data_type in ['FLOAT_COLOR', 'BYTE_COLOR'] else self.invert_mode

            #ah vectors, yes
            skip = len(func.get_attrib_default_value(src_attrib)) if not src_attrib.data_type == 'FLOAT' else 1
            if invert_mode == "MULTIPLY_MINUS_ONE":
                storage = [v * -1 if not self.edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)]
            elif invert_mode == "SUBTRACT_FROM_ONE":
                storage = [1-v if not self.edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)] 
            elif invert_mode == "ADD_TO_MINUS_ONE":
                storage = [-1+v if not self.edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)] 
        
        func.set_attribute_values(src_attrib, storage, flat_list=True)
        
        obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}
    
    multiple_invert_modes_datatypes = ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR', 'QUATERNION', 'INT32_2D']

    def invoke(self, context, event):
        if context.active_object.data.attributes.active.data_type in self.multiple_invert_modes_datatypes or context.active_object.mode == 'EDIT':
            # display props
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        row = self.layout
        obj = context.active_object

        # invert mode for float and vectors
        if obj.data.attributes.active.data_type in self.multiple_invert_modes_datatypes:
            prop = "invert_mode" if context.active_object.data.attributes.active.data_type not in ['FLOAT_COLOR', 'BYTE_COLOR'] else "color_invert_mode"
            row.prop(self, prop, text="Invert Mode")
        
        # selected only
        if obj.mode =='EDIT':
            row.prop(self, "edit_mode_selected_only", text="Selected only")
            # spill face corners
            if context.active_object.data.attributes.active.domain == 'CORNER':
                row.prop(self, "edit_mode_face_corner_spill", text="Face Corner Spill")

class RemoveAllAttribute(bpy.types.Operator):
    """
    Removes all valid attributes
    """
    bl_idname = "mesh.attribute_remove_all"
    bl_label = "Remove All"
    bl_description = "Removes all attributes"
    bl_options = {'REGISTER', 'UNDO'}

    bool_include_uvs: bpy.props.BoolProperty(
        name="Include UVMaps", 
        description="All Vector2D attributes stored in Face Corners", 
        default=False
        )
    
    bool_include_color_attribs: bpy.props.BoolProperty(
        name="Include Color Attributes", 
        description="All Color attributes stored in Vertices or Face Corners", 
        default=False
        )


    @classmethod
    def poll(self, context):
        return context.active_object and len(func.get_valid_attributes(context.active_object))

    def is_uvmap(self, a):
        return a.domain == 'CORNER' and a.data_type == 'FLOAT2'

    def is_color_attrib(self, a):
        return (a.domain == 'CORNER' or a.domain == 'POINT') and (a.data_type == 'FLOAT_COLOR' or a.data_type == 'BYTE_COLOR') 
    
    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        num = 0

        attrib_names = [a.name for a in obj.data.attributes]
        
        for name in attrib_names:
            if not func.get_is_attribute_valid(name) or name not in obj.data.attributes:
                continue
            
            a = obj.data.attributes[name]
            
            if ((self.bool_include_uvs if self.is_uvmap(a) else True) and 
                (self.bool_include_color_attribs if self.is_color_attrib(a) else True)):
                    if etc.verbose_mode:
                        print(f"Attribute removed - {a.name}: {a.domain}, {a.data_type}")
                    obj.data.attributes.remove(a)
                    num += 1
        
        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, (f"Removed {str(num)} attribute" + ("s" if num > 1 else "") if num else "None of attributes removed!"))
        return {'FINISHED'}

    def invoke(self, context, event):
        # show prompt only if uvs or color attribs were found
        if len(context.active_object.data.uv_layers) or len(context.active_object.data.color_attributes):
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        row = self.layout
        row.label(text="WARNING")
        row.separator()
        warn_text = "Attributes include Color Attributes"
        if bpy.app.version >= (3,5,0):
            warn_text += " and UVMaps"
        row.label(text=warn_text)
        row.label(text="Potentially more data in newer versions of blender")
        row.separator()
        row.label(text="Include:")
        if bpy.app.version >= (3,5,0):
            row.prop(self, "bool_include_uvs", text="UVMaps")
        row.prop(self, "bool_include_color_attribs", text="Color Attributes")

class ConvertToMeshData(bpy.types.Operator):
    bl_idname = "mesh.attribute_convert_to_mesh_data"
    bl_label = "Convert To Mesh Data"
    bl_description = "Converts attribute to vertex group, shape key, normals..."
    bl_options = {'REGISTER', 'UNDO'}

    append_to_current: bpy.props.BoolProperty(name="Append", default=False)

    apply_to_first_shape_key: bpy.props.BoolProperty(name="Apply to first shape key too", default=True, description="With this disabled, it might produce result you did not expect")
    create_shape_key_if_not_present: bpy.props.BoolProperty(name="Also create Basis shape key", default=True, description="Creates a basis shape key before converting")
    
    delete_if_converted: bpy.props.BoolProperty(name="Delete after conversion", default=False)

    data_target: bpy.props.EnumProperty(
        name="Target",
        description="Select an option",
        items=func.get_target_data_enum
    )

    attrib_name: bpy.props.StringProperty(name="Name", default="")

    convert_to_domain: bpy.props.EnumProperty(
        name="Store in",
        description="Select an option",
        items=func.get_target_compatible_domains
    )

    enable_auto_smooth: bpy.props.BoolProperty(name="Enable Auto Smooth",
                                               description="Custom split normals are visible only when Auto Smooth is enabled", 
                                               default=True)
    
    to_vgindex_weight: bpy.props.FloatProperty(name='Weight Value',
                                                          description="Weight value to apply to vertex group at index defined in this attribute",
                                                          default=1.0
                                                          )
    
    to_vgindex_weight_mode: bpy.props.EnumProperty(
        name="Weighting mode",
        description="Select an option",
        items=[("STATIC", "Use float value to weight", "Use predefined float value to weight vertices"),
               ("ATTRIBUTE", "Use float attribute to weight", "Use float attribute to weight vertices")]
    )
    
    to_vgindex_source_attribute: bpy.props.EnumProperty(
        name="Float Attribute",
        description="Select an option",
        items=func.get_float_int_attributes
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
        src_attrib_domain = src_attrib.domain
        src_attrib_data_type = src_attrib.data_type
        data_target_data_type = data.object_data_targets[self.data_target].data_type
        data_target_compatible_domains = func.get_target_compatible_domains(self, context)

        if etc.verbose_mode:
            print(f"Converting attribute {src_attrib.name} to {self.data_target}")

        # Check for user input validity
        input_invalid = False
        if self.data_target == "TO_FACE_MAP_INDEX" and not len(obj.face_maps):
            self.report({'ERROR'}, "No Face Maps. Nothing done")
            input_invalid = True

        elif self.data_target == "TO_MATERIAL_INDEX" and not len(obj.material_slots):
            self.report({'ERROR'}, "No material slots. Nothing done")
            input_invalid = True
        
        elif self.data_target == "TO_VERTEX_GROUP_INDEX" and not len(obj.vertex_groups):
            self.report({'ERROR'}, "No vertex groups. Nothing done")
            input_invalid = True

        elif self.data_target == "TO_VERTEX_GROUP_INDEX" and self.to_vgindex_weight_mode == 'ATTRIBUTE' and self.to_vgindex_source_attribute =='NULL':
            self.report({'ERROR'}, "Invalid source weights attribute. Nothing done")
            input_invalid = True

        if input_invalid:
            bpy.ops.object.mode_set(mode=current_mode)
            return {'CANCELLED'}
        

        # add basis shape key if none present and enabled in gui
        if self.data_target in ['TO_SHAPE_KEY'] and not hasattr(obj.data.shape_keys, 'key_blocks') and self.create_shape_key_if_not_present:
            bpy.ops.object.shape_key_add(from_mix=False)
            if etc.verbose_mode:
                print("Creating basis shape key...")

        # Convert if needed, use copy

        def create_temp_converted_attrib(convert_from_name:str, name_suffix:str, target_domain:str, target_data_type:str):
                """
                Returns name of temporary converted attribute. (not reference to avoid various issues)
                """

                convert_from = obj.data.attributes[convert_from_name]
                if etc.verbose_mode:
                    print(f"Conversion required! Source: {convert_from.data_type} in  {convert_from.domain}, len {len(convert_from.data)}. Target: {self.convert_to_domain} in {data_target_data_type}")
                new_attrib = obj.data.attributes.new(name=convert_from.name + " " + name_suffix, type=convert_from.data_type, domain=convert_from.domain)
                new_attrib_name = new_attrib.name
                if etc.verbose_mode:
                    print(f"Created temporary attribute {new_attrib_name}")
                
                convert_from = obj.data.attributes[convert_from_name] # After the new attribute has been created, reference is invalid
                func.set_attribute_values(new_attrib, func.get_attrib_values(convert_from, obj))
                func.convert_attribute(self, obj, new_attrib.name, 'GENERIC', target_domain, target_data_type)
                if etc.verbose_mode:
                    print(f"Successfuly converted attribute ({new_attrib_name}), datalen = {len(obj.data.attributes[new_attrib_name].data)}")
                return new_attrib_name

        domain_compatible = src_attrib_domain in [dom[0] for dom in data_target_compatible_domains] 
        data_type_compatible = src_attrib_data_type == data_target_data_type
        
        attrib_to_convert = src_attrib

        if not domain_compatible or not data_type_compatible:
            attribute_to_convert_name = create_temp_converted_attrib(src_attrib.name, "temp", self.convert_to_domain, data_target_data_type)
            attrib_to_convert = obj.data.attributes[attribute_to_convert_name]
        else:
            attribute_to_convert_name = src_attrib_name
        
        # If target is vertex group index, with attribute weight, make sure the weight attribute is float
        used_conveted_vgweight_attrib = False
        if self.to_vgindex_weight_mode == 'ATTRIBUTE':
            vg_weight_attrib = obj.data.attributes[self.to_vgindex_source_attribute]
            if vg_weight_attrib.data_type != 'FLOAT' or vg_weight_attrib.domain != 'POINT':
                if etc.verbose_mode:
                    print(f"Source attribute for weights ({vg_weight_attrib.name}) is is not correct type, converting...")

                vg_weight_attrib_name = create_temp_converted_attrib(vg_weight_attrib.name, "vgweight", 'POINT', "FLOAT")
                vg_weight_attrib =  obj.data.attributes[vg_weight_attrib_name]
                used_conveted_vgweight_attrib = True
        else:
            vg_weight_attrib = None

        if etc.verbose_mode:
            print(f"attribute -> data: {attrib_to_convert.name} -> {self.data_target}")
        
        # Welp, new attribute might be added in vgweight convert and the reference to attrib_to_convert is gone...
        attrib_to_convert = obj.data.attributes[attribute_to_convert_name]

        # Set mesh data
        func.set_mesh_data(obj, self.data_target, 
                           attrib_to_convert, 
                           face_map_name=self.attrib_name, 
                           vertex_group_name=self.attrib_name, 
                           enable_auto_smooth=self.enable_auto_smooth, 
                           apply_to_first_shape_key=self.apply_to_first_shape_key,
                           to_vgindex_weight=self.to_vgindex_weight,
                           to_vgindex_weight_mode=self.to_vgindex_weight_mode,
                           to_vgindex_src_attrib=vg_weight_attrib)
        
        #post-conversion cleanup
        if not domain_compatible or not data_type_compatible:
            obj.data.attributes.remove(obj.data.attributes[attribute_to_convert_name])

        if used_conveted_vgweight_attrib:
             obj.data.attributes.remove(obj.data.attributes[vg_weight_attrib_name])

        # remove if user enabled
        if self.delete_if_converted:
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
        data_target_data_type = data.object_data_targets[self.data_target].data_type
        data_target_compatible_domains = func.get_target_compatible_domains(self, context)
        domain_compatible = src_attrib_domain in [dom[0] for dom in data_target_compatible_domains] 
        data_type_compatible = src_attrib_data_type == data_target_data_type


        row = self.layout
        row.prop(self, "data_target", text="Target")

        # TO avoid unexpected results
        if self.data_target in ['TO_POSITION'] and hasattr(obj.data.shape_keys, 'key_blocks'):
            row.prop(self, 'apply_to_first_shape_key')

        if self.data_target in ['TO_VERTEX_GROUP']:
            row.label(icon='INFO', text=f"Name will contain \"Group\" suffix")

        if self.data_target in ['TO_SHAPE_KEY'] and not obj.data.shape_keys:
            row.prop(self, 'create_shape_key_if_not_present')

        # Custom name for face maps and vertex groups
        if self.data_target in ['TO_FACE_MAP', 'TO_VERTEX_GROUP']:
            row.prop(self, "attrib_name", text="Name")
        
        if self.data_target in ['TO_SPLIT_NORMALS']:
            row.label(icon='INFO', text=f"Blender expects normal vectors to be normalized")

            if not obj.data.use_auto_smooth:
                row.prop(self, 'enable_auto_smooth')
                row.label(icon='ERROR', text=f"Custom normals are visible only with Auto Smooth")
        
        if self.data_target in ['TO_VERTEX_GROUP_INDEX']:
            row.prop(self, 'to_vgindex_weight_mode', text="Mode")
            if self.to_vgindex_weight_mode == "ATTRIBUTE":
                row.prop(self, 'to_vgindex_source_attribute', text='Attribute')

                # inform user if the weights attribute is invalid
                if self.to_vgindex_source_attribute != "NULL":
                    src_weight_attrib = obj.data.attributes[self.to_vgindex_source_attribute]
                    if src_weight_attrib.data_type  != 'FLOAT' or src_weight_attrib.domain  != 'POINT':
                        if src_weight_attrib.data_type  != 'FLOAT':
                            row.label(icon='ERROR', text=f"Weights Attribute values should be of Float data type")
                        if src_weight_attrib.domain  != 'POINT':
                            row.label(icon='ERROR', text=f"Weights Attribute should be stored in Vertex domain")
                        row.label(icon='ERROR', text=f"This might not yield good results")
                    

            else:
                row.prop(self, 'to_vgindex_weight')

            

            
        # Show conversion options if data type or domain of attribute is not compatible
        if not domain_compatible or not data_type_compatible:
            
            # Not compatible domain
            if not domain_compatible:   
                row.label(icon='ERROR', text=f"This data cannot be stored in {func.get_friendly_domain_name(src_attrib_domain)}")
                if len(data_target_compatible_domains) == 1:
                    row.label(text=f"Will be stored in {func.get_friendly_domain_name(self.convert_to_domain)}")
                else:
                    row.prop(self, "convert_to_domain")
            
            # Not compatible data type
            if not data_type_compatible:
                row.label(icon='ERROR', text=f"This data does not store {func.get_friendly_data_type_name(src_attrib_data_type)}")
                row.label(text=f"Converting to {func.get_friendly_data_type_name(data_target_data_type)}")
            
            row.label(icon='ERROR', text=f"This might not yield good results")
        
        row.prop(self, 'delete_if_converted')

class CopyAttributeToSelected(bpy.types.Operator):
    bl_idname = "mesh.attribute_copy"
    bl_label = "Copy Attribute to selected"
    bl_description = "Copies attribute from active mesh to selected meshes, by index"
    bl_options = {'REGISTER', 'UNDO'}

    overwrite: bpy.props.BoolProperty(name="Overwrite", default=True, description="Overwrite on target if exists, and is same data type or domain")
    overwrite_different_type: bpy.props.BoolProperty(name="Overwrite different type", default=True, description="For the attribute in target that has a different domain or data type")

    extend_mode: bpy.props.EnumProperty(
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
        valid_attribute = func.get_is_attribute_valid(active_attrib.name)
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
                if not self.overwrite:
                    continue
                
                #overwrite different type?
                not_same_type = sel_obj_attr.domain != src_attrib.domain or sel_obj_attr.data_type != src_attrib.domain
                if not_same_type and not self.overwrite_different_type:
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
                if self.extend_mode not in ["REPEAT", "PING_PONG"]: 
                    
                    # With value on last index
                    if self.extend_mode =='LAST_VAL':
                        fill_value = [a_vals[-1]]

                    # With 'zero' value
                    elif self.extend_mode =='ZERO':
                        fill_value = func.get_attrib_default_value(src_attrib)
                        fill_value = [fill_value]

                    target_a_vals = a_vals + (fill_value * (target_size-source_size))
                
                # Fill extra with non-single value
                else:
                    times = target_size - source_size

                    # Repeat from start
                    if self.extend_mode =="REPEAT":
                        target_a_vals = a_vals * times
                    
                    # Repeat but from end to start then from start to end
                    elif self.extend_mode == "PING_PONG":
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
        row.prop(self, "overwrite", text="Overwrite if exists")
        row.prop(self, "overwrite_different_type", text="Overwrite different type")
        row.prop(self, "extend_mode", text="Extend Mode")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class ConditionalSelection(bpy.types.Operator):
    bl_idname = "mesh.attribute_conditioned_select"
    bl_label = "Select in edit mode by condition"
    bl_description = "Select mesh domain by attribute value with specified conditions"
    bl_options = {'REGISTER', 'UNDO'}

    deselect: bpy.props.BoolProperty(name="Deselect", default=False)


    # conditions
    
    def get_numeric_conditions_enum(self,context):
        return [
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
            ("EQORGR", "Equal or greater", ">="),
            ("EQORLS", "Equal or lesser", "<="),
            ("GR", "Greater than", ">"),
            ("LS", "Lesser than", "<"),
        ]

    numeric_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    
    bool_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
        ],
        default="EQ"
    )

    string_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
            ("CONTAINS", "Contains", "in"),
            ("STARTS_WITH", "Starts with", "startswith"),
            ("ENDS_WITH", "Ends with", "endswith"),
        ],
        default="EQ"
    )

    string_case_sensitive_bool: bpy.props.BoolProperty(
        name="Case sensitive", 
        description="Is \"BLENDER\" different than \"blEnDer\"?", 
        default=False
        )

    # RGB HSV
    color_value_type_enum: bpy.props.EnumProperty(
        name="Color Mode",
        description="Select an option",
        items=[
            ("RGBA", "RGBA", ""),
            ("HSVA", "HSVA", ""),
        ],
        default="RGBA"
    )

    color_gui_mode_enum: bpy.props.EnumProperty(
        name="Color Mode",
        description="Select an option",
        items=[
            ("COLOR", "Color", ""),
            ("VALUE", "Value", ""),
        ],
        default="COLOR"
    )

    vector_value_cmp_type: bpy.props.EnumProperty(
        name="Operation",
        description="Select an option",
        items=[
            ("AND", "And", "All of the conditions above need to be met"),
            ("OR", "Or", "Any of the conditions above need to be met"),
        ],
        default="AND"
    )

    # do same for vectors

    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_bool: bpy.props.BoolProperty(name="Boolean Value", default=False)
    val_vector2d: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if func.get_blender_support(data.attribute_data_types['INT32_2D'].min_blender_ver, data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))

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

    val_vector_x_toggle: bpy.props.BoolProperty(name="X", default=False)
    val_vector_y_toggle: bpy.props.BoolProperty(name="Y", default=False)
    val_vector_z_toggle: bpy.props.BoolProperty(name="Z", default=False)
    val_vector_w_toggle: bpy.props.BoolProperty(name="W", default=False)

    vec_x_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    vec_y_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    vec_z_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    vec_w_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
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
                case_sensitive_comp = self.string_case_sensitive_bool

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
                
                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type)

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
                        if etc.verbose_mode:
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

                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type)

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

                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type)
        
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

                filtered_indexes = compare_float_individual_vals(vals_to_cmp, self.vector_value_cmp_type)

        if etc.verbose_mode:
            debug_print()

        func.set_selection_or_visibility_of_mesh_domain(obj, attrib.domain, filtered_indexes, not self.deselect)

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
            grid.prop(self, "bool_condition_enum", text="")
            grid.prop(self, "val_bool", text="Value")

        elif attribute.data_type == 'STRING':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "string_condition_enum", text="")
            grid.prop(self, "val_string", text="Value")

            row.prop(self, "string_case_sensitive_bool", text="Case Sensitive")

        elif attribute.data_type == 'INT':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "numeric_condition_enum", text="")
            grid.prop(self, "val_int", text="Value")

        elif attribute.data_type == 'INT8':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "numeric_condition_enum", text="")
            grid.prop(self, "val_int8", text="Value")
        
        elif attribute.data_type == 'FLOAT':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "numeric_condition_enum", text="")
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
            row.prop(self, 'vector_value_cmp_type')

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
                    
                row.prop(self, 'vector_value_cmp_type')

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
            row.prop(self, 'vector_value_cmp_type') 
            

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

            row.prop(self, 'vector_value_cmp_type') 

        row.prop(self, 'deselect')         

class SelectDomainWithAttributeZeroValue(bpy.types.Operator):
    """
    Used in gui to select domains with non-zero value
    """
    bl_idname = "mesh.attribute_zero_value_select"
    bl_label = "Select Domain With Zero Value of Current Attribute"
    bl_description = "Select attribute with zero value"
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
                                                deselect = False,
                                                val_float = 0.0,
                                                val_int = 0,
                                                numeric_condition_enum = 'NEQ',
                                                vec_x_condition_enum = "NEQ",
                                                vec_y_condition_enum = "NEQ",
                                                vec_z_condition_enum = "NEQ",
                                                vec_w_condition_enum = "NEQ",
                                                string_condition_enum = 'NEQ',
                                                vector_value_cmp_type = 'OR',
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
    bl_description = "Deselect attribute with zero value"
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
                                                deselect = True,
                                                val_float = 0.0,
                                                val_int = 0,
                                                numeric_condition_enum = 'NEQ',
                                                vec_x_condition_enum = "NEQ",
                                                vec_y_condition_enum = "NEQ",
                                                vec_z_condition_enum = "NEQ",
                                                vec_w_condition_enum = "NEQ",
                                                string_condition_enum = 'NEQ',
                                                vector_value_cmp_type = 'OR',
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

class MAMETestAll(bpy.types.Operator):
    """
    DEBUG TEST EVERYTHING
    """
    bl_idname = "mame.tester"
    bl_label = "mame test"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # bpy.ops.mesh.primitive_monkey_add()
        # obj = context.active_object
        excs = []
        for source_data in [el[0] for el in func.get_source_data_enum_without_separators(self, context)]:
            for target_domain in ['POINT','EDGE','FACE','CORNER']:
                # for convert_domain in func.get_attribute_domains_enum(self, context):
                #     for convert_dt in func.get_attribute_data_types_enum(self, context):
                    
                    
                        bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT',
                                                                attrib_name='',
                                                                domain_data_type=source_data)
                                                                #target_attrib_domain=target_domain)#,
                    
        if excs:
            raise Exception(excs)   
        
                                # batch_convert_enabled= True,
                                # auto_convert = True,
                                # enum_attrib_converter_mode='GENERIC')
                                # enum_attrib_converter_domain=convert_domain,
                                # enum_attrib_converter_datatype=convert_dt)
    
    # enum_face_maps=''
    # enum_material_slots: bpy.props.EnumProperty(
    # enum_materials: bpy.props.EnumProperty(
    # enum_vertex_groups: bpy.props.EnumProperty(
    # enum_shape_keys: bpy.props.EnumProperty(
    # enum_shape_keys_offset_source: bpy.props.EnumProperty(

 
                            

        return {'FINISHED'}
        for domain in func.get_target_compatible_domains(self, context):
            for data_target in func.get_target_data_enum(self, context):
                bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT',
                                                            append_to_current=False,
                                                            apply_to_first_shape_key=True,
                                                            delete_if_converted=False,
                                                            data_target=data_target,
                                                            attrib_name="",
                                                            convert_to_domain=domain,
                                                            enable_auto_smooth=True)
                                                

        return {'FINISHED'}


    @classmethod
    def poll(self, context):
        return True


class AttributeResolveNameCollisions(bpy.types.Operator):
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
            if etc.verbose_mode:
                print(f"{a} {i}")
                
            if obj.data.attributes[i].name in restricted_names:
                if (not func.get_is_attribute_valid(obj.data.attributes[i].name) 
                    or (obj.data.attributes[i].data_type == 'FLOAT2' and obj.data.attributes[i].domain == 'CORNER') #ignore uvmaps, they're auto renamed
                    or (obj.data.attributes[i].data_type in ['FLOAT_COLOR', 'BYTE_COLOR'] and obj.data.attributes[i].domain in ['POINT', 'CORNER'])): # same for color attribs
                    failed += 1
                else:
                    renamed +=1
                    j = 0
                    while obj.data.attributes[i].name in restricted_names:
                        j += 1
                        obj.data.attributes[i].name = str(obj.data.attributes[i].name) + "." + str(j).zfill(3)
                    
        self.report({'INFO'}, f"Renamed {str(renamed)} attribute" + ("s" if renamed > 1 else "") + (f", did not rename {failed} (reserved attribute names/auto renamed)" if failed else ""))

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

class ReadValueFromActiveDomain(bpy.types.Operator):
    bl_idname = "mesh.attribute_read_value_from_active_domain"
    bl_label = "Sample from active domain"
    bl_description = "Reads the attribute value under active domain and sets it in GUI"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

#
# Quick buttons
#

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

class QuickUVMapToAttribute(bpy.types.Operator):
    # this is for pre blender 3.5
    bl_idname = "mesh.attribute_quick_from_uvmap"
    bl_label = "Convert UVMap to Vector 2D Attribute"
    bl_description = "Converts active UVMap to Vector 2D Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 
    
class QuickAllUVMapToAttributes(bpy.types.Operator):
    # this is for pre blender 3.5
    bl_idname = "mesh.attribute_quick_from_all_uvmaps"
    bl_label = "Convert all UVMaps to Vector 2D Attributes"
    bl_description = "Converts all UVMaps to Vector 2D Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickFaceMapAssignmentToAttribute(bpy.types.Operator):
    # this is for pre blender 4.0
    bl_idname = "mesh.attribute_quick_from_face_map"
    bl_label = "Convert Face Map assignment to Boolean Face Attribute"
    bl_description = "Convert assignment of active Face Map to Boolean Face Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 
    
class QuickFaceMapIndexToAttribute(bpy.types.Operator):
    # this is for pre blender 4.0
    bl_idname = "mesh.attribute_quick_from_face_map_index"
    bl_label = "Convert Face Map index assignment to Integer Face Attribute"
    bl_description = "Converts Face Map index assignment to Integer Face Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickSculptMaskToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_sculpt_mask"
    bl_label = "Convert Sculpt Mask to Float Vertex Attribute"
    bl_description = "Converts Sculpt Mask to Float Vertex Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickFaceSetsToAttribute(bpy.types.Operator):
    bl_idname = "mesh.attribute_quick_from_face_sets"
    bl_label = "Convert Face Sets to Integer Vertex Attribute"
    bl_description = "Converts Face Sets to Integer Vertex Attribute"
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

class QuickNamedAttributeNodeGN(bpy.types.Operator):
    bl_idname = "mesh.attribute_create_named_attribute_gn"
    bl_label = "Create Named Attribute Node (Geometry Nodes)"
    bl_description = "Creates a Named Attribute node in active geometry nodes editor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Not implemented yet...")
        # check if its a mesh
        return False

    def execute(self, context):
        return 

class QuickNamedAttributeNodeShader(bpy.types.Operator):
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
