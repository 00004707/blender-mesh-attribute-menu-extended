import func.util_func
from modules import LEGACY_etc, LEGACY_static_data
import modules.ui.ui_common
from ops.main.AssignActiveAttribValueToSelection import AssignActiveAttribValueToSelection


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
        items=func.enum_func.get_target_data_enum_with_separators
    )

    # The name of newly created mesh data, eg. vertex group or shape key. By default it is the name of the attribute itself.
    attrib_name: bpy.props.StringProperty(name="Name", default="")

    # The target domain to convert this attribute to. eg. Vertex Mean Bevel and Edge Mean Bevel
    convert_to_domain_enum: bpy.props.EnumProperty(
        name="Store in",
        description="Select an option",
        items=func.enum_func.get_supported_domains_for_selected_mesh_data_target_enum_entry
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
        items=func.enum_func.get_vertex_weight_attributes_enum
    )

    # Toggle to enable other attribute types than float to show up in a to_vgindex_weights_attribute_enum
    b_vgindex_weights_only_floats: bpy.props.BoolProperty(name="Show only Float Attributes",
                                               description="Disabling this will show all attribute types",
                                               default=True)

    # The UVMap to use
    uvmaps_enum: bpy.props.EnumProperty(
        name="UVMap",
        description="Select an option",
        items=func.enum_func.get_uvmaps_enum
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

        return not input_invalid

    def create_temp_converted_attrib(self, obj, convert_from_name:str, name_suffix:str, target_domain:str, target_data_type:str):
        """
        Copies the attribute and converts it to required type. Returns name of temporary converted attribute.
        """

        convert_from = obj.data.attributes[convert_from_name]
        LEGACY_etc.log(ConvertToMeshData, f"Conversion required! Source: {convert_from.data_type} in  {convert_from.domain}, len {len(convert_from.data)}. Target: {self.convert_to_domain_enum} in {target_data_type}", LEGACY_etc.ELogLevel.VERBOSE)

        # Make sure the new name is not starting with dot, as this will create a non-convertable internal attribute
        new_attrib_name = convert_from.name[1:] if convert_from.name.startswith('.') else convert_from.name
        new_attrib_name += " " + name_suffix
        new_attrib = obj.data.attributes.new(name=new_attrib_name, type=convert_from.data_type, domain=convert_from.domain)
        new_attrib_name = new_attrib.name

        LEGACY_etc.log(ConvertToMeshData, f"Created temporary attribute {new_attrib_name}", LEGACY_etc.ELogLevel.VERBOSE)

        convert_from = obj.data.attributes[convert_from_name] # After the new attribute has been created, reference is invalid
        func.attribute_func.set_attribute_values(new_attrib, func.attribute_func.get_attribute_values(convert_from, obj))
        func.attribute_func.convert_attribute(self, obj, new_attrib.name, 'GENERIC', target_domain, target_data_type)

        LEGACY_etc.log(ConvertToMeshData, f"Successfuly converted attribute ({new_attrib_name}), datalen = {len(obj.data.attributes[new_attrib_name].data)}", LEGACY_etc.ELogLevel.VERBOSE)

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
        elif not func.util_func.get_attribute_compatibility_check(context.active_object.data.attributes.active):
            self.poll_message_set("Addon update required for this attribute type")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False

        return True

    def execute(self, context):
        try:
            # If it's pinned mesh, we need to get data and reference from somewhere else.
            b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
            if b_pinned_mesh_in_use:
                obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
                LEGACY_etc.log(ConvertToMeshData, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
            else:
                obj = context.active_object
                obj_data = obj.data
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

            # Operators below need to work on object level. If pinned switch to referenced object.
            if b_pinned_mesh_in_use:
                current_active_object = bpy.context.active_object
                current_selection_state_of_obj = obj.select_get()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

            bpy.ops.object.mode_set(mode='OBJECT')

            for src_attrib_name in convert_attribute_list:
                src_attrib = obj.data.attributes[src_attrib_name]

                # Store original name to preserve if removal is enabled and target is vertex group
                original_attrib_name = src_attrib_name

                # check if the source attribute can be removed here as references to attrib might change 
                can_remove = LEGACY_static_data.EAttributeType.CANTREMOVE not in func.attribute_func.get_attribute_types(obj.data.attributes[src_attrib_name])

                # rename the attribute if converting to vertex group with same name as attribute
                if self.data_target_enum in ['TO_VERTEX_GROUP'] and self.b_delete_if_converted and can_remove:
                    src_attrib.name = func.attribute_func.get_safe_attrib_name(obj, src_attrib_name, check_attributes=True)
                    src_attrib_name = src_attrib.name

                src_attrib_domain = src_attrib.domain
                src_attrib_data_type = src_attrib.data_type
                data_target_data_type = LEGACY_static_data.object_data_targets[self.data_target_enum].data_type
                data_target_compatible_domains = func.enum_func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context)

                LEGACY_etc.log(ConvertToMeshData, f"Converting attribute {src_attrib.name} to {self.data_target_enum}", LEGACY_etc.ELogLevel.VERBOSE)

                # Add basis shape key if none present and enabled in gui
                if self.data_target_enum in ['TO_SHAPE_KEY'] and not hasattr(obj.data.shape_keys, 'key_blocks') and self.b_create_basis_shape_key:
                    bpy.ops.object.shape_key_add(from_mix=False)
                    LEGACY_etc.log(ConvertToMeshData, "Creating basis shape key...", LEGACY_etc.ELogLevel.VERBOSE)

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
                        LEGACY_etc.log(ConvertToMeshData, f"Source attribute for weights ({vg_weight_attrib.name}) is is not correct type, converting...", LEGACY_etc.ELogLevel.VERBOSE)

                        vg_weight_attrib_name = self.create_temp_converted_attrib(obj, vg_weight_attrib.name, "vgweight", 'POINT', "FLOAT")
                        vg_weight_attrib =  obj.data.attributes[vg_weight_attrib_name]
                        used_conveted_vgweight_attrib = True
                else:
                    vg_weight_attrib = None

                LEGACY_etc.log(ConvertToMeshData, f"attribute -> data: {attrib_to_convert.name} -> {self.data_target_enum}", LEGACY_etc.ELogLevel.VERBOSE)

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
                func.obj_func.set_mesh_data(obj, self.data_target_enum,
                                attrib_to_convert,
                                overwrite=self.b_overwrite,
                                **args
                                )


                # post-conversion cleanup
                if not domain_compatible or not data_type_compatible:
                    obj.data.attributes.remove(obj.data.attributes[attribute_to_convert_name])

                if used_conveted_vgweight_attrib:
                    obj.data.attributes.remove(obj.data.attributes[vg_weight_attrib_name])

                func.attribute_func.set_active_attribute(obj, src_attrib_name)
                # remove if user enabled
                if self.b_delete_if_converted and can_remove:
                    obj.data.attributes.remove(obj.data.attributes[src_attrib_name])

            obj.data.update()
            # Switch back to the previous object if pinned mesh was used
            if b_pinned_mesh_in_use:
                bpy.context.view_layer.objects.active = current_active_object
                obj.select_set(current_selection_state_of_obj)
            bpy.ops.object.mode_set(mode=current_mode)
            return {'FINISHED'}
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(AssignActiveAttribValueToSelection, exc)
            return {"CANCELLED"}

    def invoke(self, context, event):
        func.ui_func.refresh_attribute_UIList_elements(context)
        func.ui_func.configutre_attribute_uilist(True, True)
        return context.window_manager.invoke_props_dialog(self, width=350)

    last_selected_data_target = None

    def draw(self, context):
        b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
        if b_pinned_mesh_in_use:
            obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
            LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
        else:
            obj = context.active_object
        src_attrib = obj.data.attributes.active
        src_attrib_domain = src_attrib.domain
        src_attrib_data_type = src_attrib.data_type
        data_target_data_type = LEGACY_static_data.object_data_targets[self.data_target_enum].data_type
        data_target_compatible_domains = func.enum_func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context)
        data_supports_multiple = LEGACY_static_data.object_data_targets[self.data_target_enum].batch_convert_support
        gui_prop_group = context.window_manager.MAME_GUIPropValues

        # Apply compatible domain by default or set first one in a list if it is not supported
        if self.last_selected_data_target != self.data_target_enum:
            self.last_selected_data_target = self.data_target_enum
            if src_attrib_domain in [e[0] for e in data_target_compatible_domains]:
                self.convert_to_domain_enum = src_attrib_domain
            else:
                self.convert_to_domain_enum = data_target_compatible_domains[0][0]

        # Make sure the enum is not empty for to_vgindex_weights_attribute_enum
        vwa = func.enum_func.get_vertex_weight_attributes_enum(self, context)
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
            if not func.util_func.get_blender_support((4,1,0)) and not obj.data.use_auto_smooth:
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
                en = LEGACY_static_data.EAttributeType.CANTREMOVE not in func.attribute_func.get_attribute_types(src_attrib)
                text = "Delete After conversion" if alt_text == "" else alt_text
                text = "Non-removeable attribute" if not en else text
            else:
                gui_prop_group = context.window_manager.MAME_GUIPropValues
                list_elements = gui_prop_group.to_mesh_data_attributes_list

                possible_to_remove_attrs = []
                for el in [e for e in list_elements if e.b_select]:
                    possible_to_remove_attrs.append(LEGACY_static_data.EAttributeType.CANTREMOVE not in func.attribute_func.get_attribute_types(obj.data.attributes[el.attribute_name]))

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

            comp_datatype = LEGACY_static_data.object_data_targets[self.data_target_enum].data_type
            func.ui_func.set_attribute_uilist_compatible_attribute_type(self.convert_to_domain_enum, comp_datatype)

            # draw
            modules.ui.ui_common.draw_multi_attribute_select_uilist(row)

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
                row.label(text=f"{func.util_func.get_friendly_domain_name(src_attrib_domain)}")
            else:
                row.label(text=f"{func.util_func.get_friendly_domain_name(src_attrib_domain)}", icon='ERROR')
            row.label(text=f"{func.util_func.get_friendly_domain_name(self.convert_to_domain_enum)}")

            # Show second row comparing the Data Types
            row = col.row(align=True)
            row.label(text="Data Type")
            if data_type_compatible:
                row.label(text=f"{func.util_func.get_friendly_data_type_name(src_attrib_data_type)}")
            else:
                row.label(text=f"{func.util_func.get_friendly_data_type_name(src_attrib_data_type)}", icon='ERROR')
            row.label(text=f"{func.util_func.get_friendly_data_type_name(data_target_data_type)}")


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
                        friendly_domain = func.util_func.get_friendly_domain_name(src_weight_attrib.domain) if not static_val_mode else LEGACY_static_data.attribute_domains['POINT'].friendly_name

                        if src_weight_attrib.domain  != 'POINT' and not static_val_mode:
                            row.label(text=f"{friendly_domain}", icon='ERROR')
                        else:
                            row.label(text=f"{friendly_domain}")

                        row.label(text=f"{LEGACY_static_data.attribute_domains['POINT'].friendly_name}")

                # Show a row comparing the data types
                row = col.row(align=True)
                if self.data_target_enum in ['TO_VERTEX_GROUP_INDEX']:
                    row.label(text="Weight Data Type")
                    if self.to_vgindex_weights_attribute_enum != "NULL":
                        src_weight_attrib = obj.data.attributes[self.to_vgindex_weights_attribute_enum]
                        static_val_mode = self.to_vgindex_weight_mode_enum == "STATIC"
                        friendly_datatype = func.util_func.get_friendly_data_type_name(src_weight_attrib.data_type) if not static_val_mode else LEGACY_static_data.attribute_data_types["FLOAT"].friendly_name

                        if src_weight_attrib.data_type != 'FLOAT' and not static_val_mode:
                            row.label(text=f"{friendly_datatype}", icon='ERROR')
                        else:
                            row.label(text=f"{friendly_datatype}")

                        row.label(text=f"{LEGACY_static_data.attribute_data_types['FLOAT'].friendly_name}")

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