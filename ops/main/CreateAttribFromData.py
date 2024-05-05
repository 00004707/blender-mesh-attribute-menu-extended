import etc.property_groups
import modules.ui.ui_common
from modules import LEGACY_etc, LEGACY_static_data
from ops.main.AssignActiveAttribValueToSelection import AssignActiveAttribValueToSelection


class CreateAttribFromData(bpy.types.Operator):
    """
    This operator creates a new attribute from exisitng datablock data 
    """

    # Disable converting if is pinned or curves/pointcloud or write converter

    # BLENDER CLASS PROPERTIES
    # ---------------------------------

    bl_label = 'Create From Data...'
    bl_idname = 'mesh.attribute_create_from_data'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates attribute from mesh, curves or points data, like seams or crease."

    # COMMON
    # ---------------------------------

    # Operator supports working with pinned mesh in properties panel
    b_pinned_mesh_support = True

    # Operator required active object to work
    b_active_object_required = False

    # Operator can edit these types of meshes
    supported_object_types = ['MESH', 'CURVES', 'POINTCLOUD']

    # Implemented data type support
    supported_data_types = ['FLOAT', 'INT', 'INT8',
                            'FLOAT_VECTOR', 'FLOAT_COLOR', 'BYTE_COLOR', 'STRING',
                            'BOOLEAN', 'FLOAT2', 'INT32_2D', 'QUATERNION', 'FLOAT4X4']

    # Implemented domain support
    supported_domains = ['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE']

    # Wiki URL suffix
    wiki_url = 'Create-Attribute-From-Data'

    # Attribute Convert Supported Object Types

    attribute_convert_object_types = ['MESH']

    # OPTIONS
    # ---------------------------------

    # Main settings

    # The name of the created attribute.
    attrib_name: bpy.props.StringProperty(name="Attribute Name", default="", description="New attribute name. Leave blank for automatic name")

    # The source data to fill the created attribute
    domain_data_type_enum: bpy.props.EnumProperty(
        name="Domain Data",
        description="Select an option",
        items=func.enum_func.get_source_data_enum)

    # Optional selector for selecting the attribute domain, if source is available in multiple
    target_attrib_domain_enum: bpy.props.EnumProperty(
        name="Attribute Domain",
        description="Select an option",
        items=func.enum_func.get_supported_domains_for_selected_datablock_source_enum_entry
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
• {data_type} - Data Type name
• {face_map} - Face map name
• {shape_key} - Shape key name, or name of the shape key that the offset is calculated to
• {shape_key_to} - Name of the shape key that the offset is calculated to
• {shape_key_from} - Name of the shape key that the offset is calculated from
• {vertex_group} - Vertex Group name
• {material} - Material name
• {material_slot} - Material slot index
• {uvmap} - UVMap name
• {attribute} - Name of the attribute
• {index} - (Batch only) index of the processed element
"""
    # Toggle to enable name formatting by user with .format
    b_enable_name_formatting: bpy.props.BoolProperty(name="Formatting",
                                                     description=name_format_desc,
                                                     default=True)

    # Data selectors
    enum_face_maps: bpy.props.EnumProperty(
        name="Face Map",
        description="Select an option",
        items=func.enum_func.get_face_maps_enum
    )

    enum_material_slots: bpy.props.EnumProperty(
        name="Material Slot",
        description="Select an option",
        items=func.enum_func.get_material_slots_enum
    )

    enum_materials: bpy.props.EnumProperty(
        name="Material",
        description="Select an option",
        items=func.enum_func.get_materials_enum
    )

    enum_vertex_groups: bpy.props.EnumProperty(
        name="Vertex Group",
        description="Select an option",
        items=func.enum_func.get_vertex_groups_enum
    )

    enum_shape_keys: bpy.props.EnumProperty(
        name="Shape Key",
        description="Select an option",
        items=func.enum_func.get_shape_keys_enum
    )

    enum_shape_keys_offset_target: bpy.props.EnumProperty(
        name="Offset from",
        description="Select an option",
        items=func.enum_func.get_shape_keys_enum
    )

    enum_uvmaps: bpy.props.EnumProperty(
        name="From UVMap",
        description="Select an option",
        items=func.enum_func.get_uvmaps_enum
    )

    enum_attributes: bpy.props.EnumProperty(
        name="From Attribute",
        description="Select an option",
        items=func.enum_func.get_attributes_enum
    )

    # Extras

    # Used in prop_search to search for attribute name
    collection_attributes: bpy.props.CollectionProperty(name="Attribute", type = LEGACY_etc.property_groups.AttributePropertyGroup)

    # Used in evaluated context, to evaluate on selected object in scene
    depsgraph_eval_object_enum: bpy.props.EnumProperty(
        name="Evaluate On",
        description="Select an option",
        items=func.enum_func.get_objects_with_same_datablock_enum
    )

    # Automatic Converter settings

    # Enable automatic converting of attribute to different type after creation
    b_auto_convert: bpy.props.BoolProperty(name="Convert Attribute", description="Auto converts created attribute to another domain or type", default=False)

    # Convert mode
    enum_attrib_converter_mode:bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=func.enum_func.get_convert_attribute_modes_enum,
    )

    # The target domain to convert this attribute to
    enum_attrib_converter_domain:bpy.props.EnumProperty(
        name="Domain",
        description="Select an option",
        items=func.enum_func.get_attribute_domains_enum,
    )

    # The target data type to convert this attribute to
    enum_attrib_converter_datatype: bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=func.enum_func.get_attribute_data_types_enum,
    )

    # The datablock source
    enum_datablock_source: bpy.props.EnumProperty(
        name="Source Datablock",
        description="Select an option",
        items=[
            ("DATABLOCK", "Normal (Without modifiers)", "Get data from the object data block - data without modifiers, armature deformations etc.", "MESH_DATA", 0),
            ("EVALUATED", "Evaluated (With modifiers)", "Get data from the evaluated data block - data with modifiers applied, deformed with armature, etc.", "MODIFIER", 1),
        ],
    )

    # Helper functions
    # ---------------------------------

    def update_attributes_collection(self, context):
        enums = func.enum_func.get_attributes_enum(self, context)
        self.collection_attributes.clear()

        for e in enums:
            c_el = self.collection_attributes.add()
            c_el.id = e[0]
            c_el.name = e[1]


    def perform_user_input_test(self):
        """
        User input checks for valid mesh data and selections in GUI. Displays a message on failure to inform the user.
        """

        #check if selection even exists
        if not self.domain_data_type_enum in LEGACY_static_data.object_data_sources:
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
        if len(LEGACY_static_data.object_data_sources[self.domain_data_type_enum].domains_supported) > 1 and self.target_attrib_domain_enum == '':
            self.report({'ERROR'}, f"Invalid source domain. Nothing done")
            return False
        return True

    def enum_watchdog_domain_data(self, context):
        # Make sure the enum is not empty for domain data selector
        valid_enums = func.enum_func.get_source_data_enum(self, context)
        if self.domain_data_type_enum not in [e[0] for e in valid_enums]:
            self.domain_data_type_enum = valid_enums[0][0]

    def enum_watchdog_domain(self, context):
        # Make sure the enum is not empty for to_vgindex_weights_attribute_enum
        valid_supported_domains = func.enum_func.get_supported_domains_for_selected_datablock_source_enum_entry(self, context)
        if self.target_attrib_domain_enum not in [a[0] for a in valid_supported_domains] and len(valid_supported_domains): #for special elements
            self.target_attrib_domain_enum = valid_supported_domains[0][0]

    def create_attribute(self, context):
        #TODO CHECK FOR PINNED MESH OR CURVES AND DISABLE CONVERSION
        #TODO IMPLEMENT HIDDEN
        try:

            obj, obj_data = func.obj_func.get_object_in_context(context)
            b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)

            if b_pinned_mesh_in_use:
                LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)


            attrib = None

            # Operators below need to work on object level. If pinned switch to referenced object.
            func.obj_func.set_object_in_context_as_active(self, context)

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
                self.target_attrib_domain_enum = LEGACY_static_data.object_data_sources[self.domain_data_type_enum].attribute_domain_on_default

            # Read prefixes and suffixes of automatic naming
            data_type = LEGACY_static_data.object_data_sources[self.domain_data_type_enum].data_type

            LEGACY_etc.log(CreateAttribFromData, f"Batch mode supported & enabled: {not (not LEGACY_static_data.object_data_sources[self.domain_data_type_enum].batch_convert_support or not self.b_batch_convert_enabled) }", LEGACY_etc.ELogLevel.VERBOSE)

            # [Batch mode off] Single assignment to single attribute
            if not LEGACY_static_data.object_data_sources[self.domain_data_type_enum].batch_convert_support or not self.b_batch_convert_enabled:

                def format_name(name:str):
                    format_args = {
                        "domain": func.util_func.get_friendly_domain_name(self.target_attrib_domain_enum, plural=True),
                        "data_type": func.util_func.get_friendly_data_type_name(data_type),
                        "face_map": func.enum_func.get_face_maps_enum(self, context)[int(self.enum_face_maps)][1] if self.enum_face_maps != 'NULL' else None,
                        "shape_key": func.enum_func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None,
                        "shape_key_to": func.enum_func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_target)][1] if self.enum_shape_keys_offset_target != 'NULL' else None,
                        "shape_key_from": func.enum_func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1] if self.enum_shape_keys != 'NULL' else None,
                        "vertex_group": func.enum_func.get_vertex_groups_enum(self, context)[int(self.enum_vertex_groups)][1] if self.enum_vertex_groups != 'NULL' else None,
                        "material": func.enum_func.get_materials_enum(self, context)[int(self.enum_materials)][1] if self.enum_materials != 'NULL' else None,
                        "material_slot": func.enum_func.get_material_slots_enum(self, context)[int(self.enum_material_slots)][1] if self.enum_material_slots != 'NULL' else None,
                        "uvmap": func.enum_func.get_uvmaps_enum(self, context)[int(self.enum_uvmaps)][1] if self.enum_uvmaps != 'NULL' else None,
                        "attribute": obj_data.attributes[self.enum_attributes].name if self.enum_attributes != 'NULL' else None
                    }

                    return name.format(**format_args)

                # Automatic name formatting
                if self.attrib_name == "":
                    name = LEGACY_static_data.object_data_sources[self.domain_data_type_enum].attribute_auto_name
                    name = format_name(name)
                else:
                    name = self.attrib_name
                    if self.b_enable_name_formatting:
                        name = format_name(name)

                name = func.attribute_func.get_safe_attrib_name(obj, name) # naming the same way as vertex group will crash blender

                # Remove current attribute if overwrite is enabled
                if self.b_overwrite and name in obj.data.attributes:
                    obj.data.attributes.remove(obj.data.attributes[name])

                attrib = obj.data.attributes.new(name=name, type=data_type, domain=self.target_attrib_domain_enum)
                obj_data = func.obj_func.get_mesh_data(obj,
                                            self.domain_data_type_enum,
                                            self.target_attrib_domain_enum,
                                            vg_index=self.enum_vertex_groups,
                                            sk_index=self.enum_shape_keys,
                                            sk_offset_index=self.enum_shape_keys_offset_target,
                                            fm_index=self.enum_face_maps,
                                            sel_mat=self.enum_materials,
                                            mat_index=self.enum_material_slots,
                                            uvmap_index=self.enum_uvmaps)

                LEGACY_etc.log(CreateAttribFromData, f"Creating attribute from data: {obj_data}", LEGACY_etc.ELogLevel.VERBOSE)

                # Assign new values to the attribute
                func.attribute_func.set_attribute_values(attrib, obj_data)

                # Convert to different type (optional)
                if self.b_auto_convert:
                    func.attribute_func.convert_attribute(self, obj, name, mode=self.enum_attrib_converter_mode,
                                                domain=self.enum_attrib_converter_domain,
                                                data_type=self.enum_attrib_converter_datatype)
                func.attribute_func.set_active_attribute(obj, name)

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
                LEGACY_etc.log(CreateAttribFromData, f"Batch converting {self.domain_data_type_enum}, "\
                            f"element count: {func.obj_func.get_all_mesh_data_indexes_of_type(obj, self.domain_data_type_enum)}", LEGACY_etc.ELogLevel.VERBOSE)


                for element_index, element in enumerate(func.obj_func.get_all_mesh_data_indexes_of_type(obj, self.domain_data_type_enum)):

                    LEGACY_etc.log(CreateAttribFromData, f"Batch converting #{element}", LEGACY_etc.ELogLevel.VERBOSE)

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
                        vertex_group_name = func.enum_func.get_vertex_groups_enum(self, context)[element][1]
                        vg_index = element

                    # case: get shape key position for each shape key 
                    elif self.domain_data_type_enum in ["VERT_SHAPE_KEY_POSITION"]:
                        shape_key = func.enum_func.get_shape_keys_enum(self, context)[element][1]
                        sk_index = element
                        LEGACY_etc.log(CreateAttribFromData, f"Source is shape key POS ({shape_key}), \nFROM: {func.enum_func.get_shape_keys_enum(self, context)[element]} ", LEGACY_etc.ELogLevel.VERBOSE)

                    # case: get shape key offset from specific one
                    elif self.domain_data_type_enum == 'VERT_SHAPE_KEY_POSITION_OFFSET':

                        # case: user wants to set offset from
                        if self.b_offset_from_offset_to_toggle:
                            shape_key = func.enum_func.get_shape_keys_enum(self, context)[element][1]
                            shape_key_to = func.enum_func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)][1]
                            sk_index = element
                            sk_offset_index = self.enum_shape_keys_offset_target

                        # case: user wants to set offset to
                        else:
                            shape_key = func.enum_func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys_offset_target)][1]
                            shape_key_to = func.enum_func.get_shape_keys_enum(self, context)[element][1]
                            sk_index = self.enum_shape_keys
                            sk_offset_index = element

                        LEGACY_etc.log(CreateAttribFromData, f"Source is shape key offset, \n FROM: {func.enum_func.get_shape_keys_enum(self, context)[element]} \n TO: {func.enum_func.get_shape_keys_enum(self, context)[int(self.enum_shape_keys)]}", LEGACY_etc.ELogLevel.VERBOSE)

                    # case: check for each material if it's assigned
                    # -> iterates over every material
                    elif self.domain_data_type_enum == "FACE_IS_MATERIAL_ASSIGNED":
                        LEGACY_etc.log(CreateAttribFromData, f"All materials: {func.enum_func.get_materials_enum(self, context)}", LEGACY_etc.ELogLevel.VERBOSE)

                        material = func.enum_func.get_materials_enum(self, context)[element][1]
                        sel_mat = element

                    # case; check for each material slot if it's assigned
                    # -> iterates over every material slot
                    elif self.domain_data_type_enum == "FACE_IS_MATERIAL_SLOT_ASSIGNED":
                        material_slot = func.enum_func.get_material_slots_enum(self, context)[element][1]
                        mat_index = element

                    #case: check for each face map if it's assigned
                    # -> iterates over every face map
                    elif self.domain_data_type_enum == "FACE_FROM_FACE_MAP":
                        face_map = func.enum_func.get_face_maps_enum(self, context)[element][1]
                        fm_index = element

                    elif self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", "PINNED_VERTICES_IN_UV_EDITOR", 'UVMAP']:
                        uvmap = func.enum_func.get_uvmaps_enum(self, context)[element][1]
                        uvmap_index = element

                    def format_name_batch(xname:str):
                        format_args = {
                            "domain": func.util_func.get_friendly_domain_name(self.target_attrib_domain_enum, plural=True),
                            "data_type": func.util_func.get_friendly_data_type_name(data_type),
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
                        xname = LEGACY_static_data.object_data_sources[self.domain_data_type_enum].attribute_auto_name
                        xname = format_name_batch(xname)
                    else:
                        xname = self.attrib_name
                        if self.b_enable_name_formatting:
                            xname = format_name_batch(xname)


                    # Grab safe name for Vertex Groups to avoid blender crashing and possibly other cases in the future
                    xname = func.attribute_func.get_safe_attrib_name(obj, xname)

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
                    obj_data = func.obj_func.get_mesh_data(obj,
                                            self.domain_data_type_enum,
                                            self.target_attrib_domain_enum,
                                            **args)

                    # Store data in attribute
                    func.attribute_func.set_attribute_values(attrib, obj_data)

                    # Convert to different type (optional)
                    if self.b_auto_convert:
                        func.attribute_func.convert_attribute(self, obj, attrib.name, mode=self.enum_attrib_converter_mode,
                                                domain=self.enum_attrib_converter_domain,
                                                data_type=self.enum_attrib_converter_datatype)

            obj.data.update()

            # Switch back to the previous object if pinned mesh was used
            func.obj_func.set_object_by_user_as_active_back(self, context)

            # Switch back to previous mode.
            bpy.ops.object.mode_set(mode=mode)
            bpy.context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        except Exception as exc:
            try:
                bpy.context.window_manager.event_timer_remove(self._timer)
            except Exception:
                pass
            LEGACY_etc.call_catastrophic_crash_handler(AssignActiveAttribValueToSelection, exc)
            return {"CANCELLED"}

    @classmethod
    def poll(self, context):
        obj, obj_data = func.obj_func.get_object_in_context(context)

        if not func.poll_func.pinned_mesh_poll(self, context, self.b_pinned_mesh_support):
            self.poll_message_set("Pinned mesh mode unsupported")
            return False
        elif self.b_active_object_required and not bpy.context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not obj:
            self.poll_message_set("No active object or no pinned object")
            return False
        elif obj.type not in self.supported_object_types:
            self.poll_message_set("Object type is not supported")
            return False
        elif obj.name not in bpy.context.scene.objects:
            self.poll_message_set("Pinned mesh not in scene")
        return True

    def modal(self, context, event):
        if event.type == 'TIMER':
            status = modules.ui.ui_common.get_confirm_box_status()

            if status == 'CANCEL':
                return {'CANCELLED'}

            elif status == 'OK':
                return self.create_attribute(context)

        return {'PASS_THROUGH'}

    def execute(self, context):

        # Get dependency graph if needed
        self._evaluated_dg = None
        self._evaluated_dg_obj = None

        if self.enum_datablock_source == 'EVALUATED':

            # Grab the object
            self._evaluated_dg = bpy.context.evaluated_depsgraph_get()
            self._evaluated_dg_obj = bpy.data.objects[self.depsgraph_eval_object_enum].evaluated_get(self._evaluated_dg)

            # Grab the object in context
            obj, obj_data = func.obj_func.get_object_in_context(context)

            # Just in case
            if obj is None:
                self.report({'ERROR'}, 'No active object')

            # Check if it has same domain count
            b_domain_len_higher = False
            if self.target_attrib_domain_enum == 'POINT':
                if obj.type == 'MESH':
                    b_domain_len_higher = len(obj.data.vertices) < len(self._evaluated_dg_obj.data.vertices)
                elif obj.type in ['CURVES', 'POINTCLOUD']:
                    b_domain_len_higher = len(obj.data.points) < len(self._evaluated_dg_obj.data.points)

            elif self.target_attrib_domain_enum == 'EDGE':
                b_domain_len_higher = len(obj.data.edges) < len(self._evaluated_dg_obj.data.edges)
            elif self.target_attrib_domain_enum == 'FACE':
                b_domain_len_higher = len(obj.data.polygons) < len(self._evaluated_dg_obj.data.polygons)
            elif self.target_attrib_domain_enum == 'CORNER':
                b_domain_len_higher = len(obj.data.loops) < len(self._evaluated_dg_obj.data.loops)
            elif self.target_attrib_domain_enum == 'CURVE':
                b_domain_len_higher = len(obj.data.curves) < len(self._evaluated_dg_obj.data.curves)

            # Warn user
            if b_domain_len_higher:
                modules.ui.ui_common.get_confirm_box(title=f'Modifiers have increased {func.util_func.get_friendly_domain_name(self.target_attrib_domain_enum)}'\
                                    f' count. New {func.util_func.get_friendly_domain_name(self.target_attrib_domain_enum, True)} will be ignored. Continue?')
                wm = context.window_manager
                self._timer = wm.event_timer_add(0.1, window=context.window)
                wm.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                return self.create_attribute(context)
        else:
            return self.create_attribute(context)


    def invoke(self, context, event):

        # Prepare create enum selector nested menu
        bpy.types.WM_MT_MAME_create_from_data_menu.init(bpy.types.WM_MT_MAME_create_from_data_menu, context, self)

        # Update list of attributes to show in search box
        self.update_attributes_collection(context)

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):

        obj, obj_data = func.obj_func.get_object_in_context(context)
        pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)

        # Enum watchdogs to avoid empty selector and warnings in console
        # self.enum_watchdog_domain_data(context)
        self.enum_watchdog_domain(context)

        # get if the attrib supports batch conversion
        def get_batch_convert_support():
            return False if self.domain_data_type_enum == '' else LEGACY_static_data.object_data_sources[self.domain_data_type_enum].batch_convert_support
        batch_convert_support = get_batch_convert_support()

        layout = self.layout

        row = layout.row(align=True)
        row.label(text='New Attribute Name')

        row = layout.row(align=True)
        # New attribute name
        row.prop(self, "attrib_name", text="")

        subrow = row.row(align=True)
        subrow.prop(self, "b_enable_name_formatting", toggle=True)
        subrow.ui_units_x = 5

        # Label with info about auto generated name
        row = layout.row()
        if self.attrib_name == '':
            row.label(text="Using auto-generated name", icon='INFO')
        else:
            row.label(text="") # occupy space to avoid resizing the window


        # Data to create the attribute from
        layout.separator()
        row = layout.row()
        row.label(text="Source")

        row = layout.row()
        row.prop_with_menu(self, "domain_data_type_enum", menu='WM_MT_MAME_create_from_data_menu', text="")

        # prop_with_menu is undocumented and will set the value of the enum in it to default value
        # even if prop_enum is correctly configured in menu in quesiton
        # so instead of wasting hours on figuring out how to use the damn thing
        # i'm setting propgroup value in menu, and overwriting it here
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        try:
            self.domain_data_type_enum = gui_prop_group.data_source_enum
        except TypeError:
            # Update if invalid
            gui_prop_group.data_source_enum = self.domain_data_type_enum



        # little spacing
        row = layout.row()

        # Source domain selector, if applicable to source attribute
        layout.separator()
        layout.label(text="Domain")

        # Refresh it manually... 
        self.enum_watchdog_domain(context)

        if len(func.enum_func.get_supported_domains_for_selected_datablock_source_enum_entry(self, context)) > 1:
            layout.prop(self, "target_attrib_domain_enum", text="")
        else:
            layout.label(text=func.util_func.get_friendly_domain_name(self.target_attrib_domain_enum, context=context),
                         icon=func.util_func.get_domain_icon(self.target_attrib_domain_enum))


        # Datablock evaluated or not
        layout.separator()
        layout.label(text="Datablock")
        layout.prop_tabs_enum(self, 'enum_datablock_source')
        if self.enum_datablock_source == 'EVALUATED':
            layout.prop(self, 'depsgraph_eval_object_enum')
        else:
            layout.label(text='')


        # Specific data source GUI entries
        layout.separator()
        layout.label(text="Options")
        # face maps
        if self.domain_data_type_enum in ["FACE_FROM_FACE_MAP"]:
            if not self.b_batch_convert_enabled:
                layout.prop(self, "enum_face_maps", text="Face Map")
            else:
                layout.label(text="Face Map: each one")
            layout.label(text="") # space filler to maintain fixed window size

        # material slots
        elif self.domain_data_type_enum in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"]:
            if not self.b_batch_convert_enabled:
                layout.prop(self, "enum_material_slots", text="Material Slot")
            else:
                layout.label(text="Material Slot: each one")
            layout.label(text="") # space filler to maintain fixed window size

        # materials
        elif self.domain_data_type_enum in ["FACE_IS_MATERIAL_ASSIGNED"]:
            if not self.b_batch_convert_enabled:
                layout.prop(self, "enum_materials", text="Material")
            else:
                layout.label(text="Material: each one")
            layout.label(text="") # space filler to maintain fixed window size

        # shape keys

        # Shape key "Offset From" and  "Offset To" selectors
        elif self.domain_data_type_enum ==  "VERT_SHAPE_KEY_POSITION_OFFSET":

            if not self.b_batch_convert_enabled or (not self.b_offset_from_offset_to_toggle):
                layout.prop(self, "enum_shape_keys", text="Offset from")
            else:
                layout.label(text="Offset from: each one")

            if not self.b_batch_convert_enabled or self.b_offset_from_offset_to_toggle:
                layout.prop(self, "enum_shape_keys_offset_target", text="Offset to")
            else:
                layout.label(text="Offset to: each one")


        # Simple shape key vertex position to attribute mode
        elif self.domain_data_type_enum ==  "VERT_SHAPE_KEY_POSITION":
            if not self.b_batch_convert_enabled:
                layout.prop(self, "enum_shape_keys", text="Shape Key")
            else:
                layout.label(text="Shape Key: All shape keys")
            layout.label(text="") # space filler to maintain fixed window size

        # vertex groups
        elif self.domain_data_type_enum in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"]:
            if not self.b_batch_convert_enabled:
                layout.prop(self, "enum_vertex_groups", text="Vertex Group")
            else:
                layout.label(text="Vertex Group: All Vertex Groups")
            layout.label(text="") # space filler to maintain fixed window size

        # UVMap domain selection
        elif (self.domain_data_type_enum in ["SELECTED_VERTICES_IN_UV_EDITOR",
                                             "SELECTED_EDGES_IN_UV_EDITOR",
                                             "PINNED_VERTICES_IN_UV_EDITOR",
                                             'UVMAP']):
                if not self.b_batch_convert_enabled:
                    layout.prop(self, "enum_uvmaps", text="UV Map")
                else:
                    layout.label(text="UV Map: All UV Maps")
                layout.label(text="") # space filler to maintain fixed window size

        # Attribute
        elif self.domain_data_type_enum in ["ATTRIBUTE"]:
            layout.prop_search(self, "enum_attributes", self, "collection_attributes", text="Attribute")
            layout.label(text="") # space filler to maintain fixed window size

        else:
            layout.label(text="No options for this source")
            layout.label(text="") # space filler to maintain fixed window size

        # refresh ui
        batch_convert_support = get_batch_convert_support()

        # convert all of type to attrib
        if batch_convert_support:
            layout.prop(self, "b_batch_convert_enabled", text="Batch Convert All To Attributes", toggle=True)

            # Batch convert toggle mode either to create multiple "offset from" attributes or mulitple "offset to" attributes (shape key)
            if self.b_batch_convert_enabled and self.domain_data_type_enum == "VERT_SHAPE_KEY_POSITION_OFFSET":
                layout.prop(self, "b_offset_from_offset_to_toggle", text="Set \"Offset to\" instead of \"Offset From\"", toggle=True)
            else:
                layout.label(text="")

        else:
            layout.label(text="") # occupy space to avoid resizing the window
            layout.label(text="")

        layout.separator()

        # Overwrite toggle
        layout.prop(self, "b_overwrite", text="Overwrite if exists", toggle=True)

        # Automatic conversion to another type, toggleable
        convert_en = obj.type in self.attribute_convert_object_types and not pinned_mesh_in_use

        r = layout.row()
        r.prop(self, "b_auto_convert", text="Convert Attribute After Creation", toggle=True)
        r.enabled = convert_en

        if self.b_auto_convert and convert_en:
            layout.label(text="Conversion Options")
            layout.prop(self, "enum_attrib_converter_mode", text="Mode")
            if self.enum_attrib_converter_mode == 'GENERIC':
                layout.prop(self, "enum_attrib_converter_domain", text="Domain")
                layout.prop(self, "enum_attrib_converter_datatype", text="Data Type")
        elif not convert_en:
            if pinned_mesh_in_use:
                layout.label(text=f"Converting attribute unavailable if mesh is pinned", icon="ERROR")
            else:
                layout.label(text=f"Converting attribute unavailable for this object type", icon="ERROR")

        op = layout.operator('window_manager.mame_open_wiki', icon='QUESTION')

        op.wiki_url = self.wiki_url

class CreateFromDataMenu(bpy.types.Menu):

    #Requires calling init() before use.

    bl_idname = "WM_MT_MAME_create_from_data_menu"
    bl_label = "Source Data"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    # Reference to the parent operator
    _parent_ref = None

    # The prefix of the suffix of newly created submenu eg. OBJECT_MT_MAME_DS_VERTEX
    suffix_s_prefix = 'MAME_DS_'

    # Created submenus {category:str, ref:menu}
    created_submenus = {}
 
    def spawn_submenu(self, submenu_idname, submenu_friendly_name):
        """Creates submenu, with some common settings. Do not call it, use get_or_ensure_submenu

        Args:
            submenu_name (_type_): _description_
        """
        # Create menu object
        menu_ref = create_submenu(submenu_idname, submenu_friendly_name)

        # Assign custom draw function
        def draw(self, context):
            layout = self.layout
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            column = layout.column()
            for enum_id in self.enum_ids:
                # subrow.label(text="", icon=static_data.object_data_sources[enum_id].icon) # breaks menu
                column.prop_enum(gui_prop_group, 
                                 "data_source_enum", 
                                 value=enum_id)#, 
                                 #icon=static_data.object_data_sources[enum_id].icon) # doesn't work

        menu_ref.draw = draw
        menu_ref.enum_ids = [] # used to display all enum properties, use enum IDs (keys)
        return menu_ref

    def get_or_ensure_unique_submenu(self, category:str, friendly_name: str, icon:str):
        """Returns exisitng submenu to add enum properties to or creates new

        Args:
            category (str): Category, also name of the menu
            friendly_name (str): Displayed name of the (sub)menu
            icon (str): Menu icon

        Returns:
            set: Submenu parameters, ref: reference to the menu object, idname: bpy.types entry (str), icon: icon (str)
        """

        # Find exisitng submenu
        try:
            return self.created_submenus[category]
        except KeyError:
            pass
        
        # Create new
        idname = self.suffix_s_prefix + category
        menu_ref = self.spawn_submenu(self, idname, friendly_name)
        submenu = {'ref': menu_ref, 'idname': menu_ref.bl_idname, 'icon': icon}
        self.created_submenus[category] = submenu
        return submenu

    def add_enum_to_submenu(menu_ref, enum_idname:str):
        """Simply adds another enum prop to the submenu

        Args:
            menu_ref (str): reference to the menu object
        """
        menu_ref.enum_ids.append(enum_idname)

    def init(self, context, parent):
        """Called in operator to cook the submenus, as it is prohibited to register classes in draw function

        Args:
            context (ref): context reference
            parent (ref): operator reference
        """
    
        # Sets parent
        self._parent_ref = parent
        
        # Clean submenus
        self.created_submenus = {}

        # Creates submenus for use in main menu
        for enum_tuple in func.enum_func.get_source_data_enum(self, context):
            if (type(LEGACY_static_data.object_data_sources[enum_tuple[0]]) == LEGACY_static_data.ObjectDataSource
                and type(LEGACY_static_data.object_data_sources[enum_tuple[0]].ui_category) == LEGACY_static_data.EObjectDataSourceUICategory):
                catname = LEGACY_static_data.object_data_sources[enum_tuple[0]].ui_category.name

                submenu_set = func.util_func.get_friendly_name_and_icon_for_EObjectDataSourceUICategory(LEGACY_static_data.object_data_sources[enum_tuple[0]].ui_category)
                friendly_name = submenu_set['name']
                icon = submenu_set['icon']
                sm = self.get_or_ensure_unique_submenu(self, catname, friendly_name, icon)
                self.add_enum_to_submenu(sm['ref'], enum_tuple[0])
                
                # and add to all category
                friendly_name = "All"
                sm = self.get_or_ensure_unique_submenu(self, 'ALL', friendly_name, 'ALIGN_JUSTIFY')
                self.add_enum_to_submenu(sm['ref'], enum_tuple[0])

    def draw(self, context):
        
        layout = self.layout
        gui_prop_group = context.window_manager.MAME_GUIPropValues

        # Reminder: set the gui_prop_group.data_source_enum, not the parent reference
        # It will set the value to enum index 0, idk why nor do i care if it works as is

        # There is _parent_ref passed in operator to this panel
        # If it is None, then init() was not called
        if not hasattr(self, '_parent_ref') or self._parent_ref is None:
            layout.alert = True
            layout.label(text="List failed to load", icon='ERROR')
            layout.operator("window_manager.mame_report_issue")
        
        # for key in self.created_submenus:
        #     layout.menu(self.created_submenus[key]['idname'])

        # If ever this list gets expanded/modified, it should be handled
        drawn_submenu_keys = ['ALL']

        #Draw other
        for new_menu_key in [menu_key for menu_key in self.created_submenus if menu_key not in drawn_submenu_keys]:
            layout.menu(self.created_submenus[new_menu_key]['idname'], icon=self.created_submenus[new_menu_key]['icon'])
        
        # Draw looong all list
        layout.separator()
        layout.menu(self.created_submenus['ALL']['idname'], icon='ALIGN_JUSTIFY')