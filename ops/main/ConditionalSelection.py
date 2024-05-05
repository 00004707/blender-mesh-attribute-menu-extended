import func.util_func
from modules import LEGACY_etc, LEGACY_static_data


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
        items=func.enum_func.get_attribute_comparison_conditions_enum_for_property
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
    if func.util_func.get_blender_support(LEGACY_static_data.attribute_data_types['INT8'].min_blender_ver, LEGACY_static_data.attribute_data_types['INT8'].unsupported_from_blender_ver):
        val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_float_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_byte_color: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if func.util_func.get_blender_support(LEGACY_static_data.attribute_data_types['INT32_2D'].min_blender_ver, LEGACY_static_data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))
    if func.util_func.get_blender_support(LEGACY_static_data.attribute_data_types['QUATERNION'].min_blender_ver, LEGACY_static_data.attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
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
        items=func.enum_func.get_attribute_comparison_conditions_enum_for_property,
    )
    vec_1_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.enum_func.get_attribute_comparison_conditions_enum_for_property,
    )
    vec_2_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.enum_func.get_attribute_comparison_conditions_enum_for_property,
    )
    vec_3_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=func.enum_func.get_attribute_comparison_conditions_enum_for_property,
    )


    @classmethod
    def poll(self, context):
        return func.poll_func.conditional_selection_poll(self, context)

    def execute(self, context):
        LEGACY_etc.log(ConditionalSelection, f"conditional selection on attrib: {context.active_object.data.attributes.active}", LEGACY_etc.ELogLevel.VERBOSE)

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
            LEGACY_etc.log(ConditionalSelection, f"""ConditionalSelectionTrigger
Cond: {condition}
CompVal: {comparison_value}
CmpType: {self.vector_value_cmp_type_enum}
DataType: {attrib_data_type}
CaseSensitive: {self.b_string_case_sensitive}
FiltIndex: {filtered_indexes}
VecSingleVal: {self.b_single_value_vector}
VecSingleCondition: {self.b_single_condition_vector}""", LEGACY_etc.ELogLevel.VERBOSE)

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


        gui_prop_subtype = LEGACY_static_data.attribute_data_types[attrib_data_type].gui_prop_subtype

        #case 1: single number/value
        if gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.SCALAR,
                                LEGACY_static_data.EDataTypeGuiPropType.BOOLEAN,
                                LEGACY_static_data.EDataTypeGuiPropType.STRING]:
            comparison_value = getattr(self, f'val_{attrib_data_type.lower()}')

            filtered_indexes = func.obj_func.get_filtered_indexes_by_condition(func.attribute_func.get_attribute_values(attrib, obj),
                                                                      condition,
                                                                      comparison_value,
                                                                      self.b_string_case_sensitive)


        # case 2: vectors/colors
        elif gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.VECTOR,
                                  LEGACY_static_data.EDataTypeGuiPropType.COLOR]:
            vals_to_cmp = []
            filtered_indexes = []
            src_data = np.array(func.attribute_func.get_attribute_values(attrib, obj))
            use_hsv = self.color_value_type_enum == 'HSVA' and gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR

            if use_hsv:
                for i, subelement in enumerate(src_data):
                    LEGACY_etc.log(ConditionalSelection, "HSV mode enabled, converting all values to HSV", LEGACY_etc.ELogLevel.VERBOSE)

                    src_data[i] = func.util_func.color_vector_to_hsv(subelement)

            # for each dimension of a vector
            for i in range(0, len(src_data[0])):
                if getattr(self, f'val_vector_{i}_toggle'):
                    condition = getattr(self, f'vec_0_condition_enum' if self.b_single_condition_vector else f'vec_{i}_condition_enum')
                    comparison_value = getattr(self, f"val_{attrib_data_type.lower()}")[0] if self.b_single_value_vector else getattr(self, f"val_{attrib_data_type.lower()}")[i]

                    srgb_convert = attrib.data_type == 'BYTE_COLOR'
                    LEGACY_etc.log(ConditionalSelection, f"Checking vector[{i}], condition: {condition}, to value {comparison_value}", LEGACY_etc.ELogLevel.VERBOSE)
                    vals_to_cmp.append(func.obj_func.get_filtered_indexes_by_condition([vec[i] for vec in src_data], condition, comparison_value, vector_convert_to_srgb=srgb_convert))

            filtered_indexes = compare_each_vector_dimension_indexes(vals_to_cmp, self.vector_value_cmp_type_enum)


        debug_print()


        func.obj_func.set_selection_or_visibility_of_mesh_domain(obj, attrib.domain, filtered_indexes, not self.b_deselect)

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
        e_datatype = LEGACY_static_data.EAttributeDataType[dt]
        gui_prop_subtype = LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype

        # For anything that holds a single value
        if gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.SCALAR,
                            LEGACY_static_data.EDataTypeGuiPropType.STRING,
                            LEGACY_static_data.EDataTypeGuiPropType.BOOLEAN]:

            grid = layout.row(align=True)
            grid.prop(self, 'b_deselect', text=f"Select {func.util_func.get_friendly_domain_name(domain, True)}" if not self.b_deselect else f"Deselect {func.util_func.get_friendly_domain_name(domain, True)}", toggle=True, invert_checkbox=True)
            grid.prop(self, "attribute_comparison_condition_enum", text="")

            # Get different text on value field
            if e_datatype == LEGACY_static_data.EAttributeDataType.STRING:
                text = ''
            elif e_datatype == LEGACY_static_data.EAttributeDataType.BOOLEAN:
                text = 'True' if self.val_boolean else 'False'
            else:
                text = "Value"

            grid.prop(self, f"val_{dt.lower()}", text=text, toggle=True)
            if e_datatype == LEGACY_static_data.EAttributeDataType.STRING:
                layout.prop(self, "b_string_case_sensitive", text="Not Case Sensitive" if not self.b_string_case_sensitive else "Case Sensitive", toggle=True)

        # For vectors of any type
        elif gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.VECTOR, LEGACY_static_data.EDataTypeGuiPropType.COLOR]:
            row = layout.row(align=True)

            if gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR:
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

            if gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR and self.color_value_type_enum == 'HSVA':
                    v_subelements = ['H','S','V','A']
            else:
                v_subelements = LEGACY_static_data.attribute_data_types[dt].vector_subelements_names

            row2 = col.row(align=True)

            # Toggles
            row3 = row2.row(align=True)
            subrow = row3.column(align=True)
            for el in range(0, len(func.attribute_func.get_attribute_default_value(attribute))):
                subrow.ui_units_x = 3
                subrow.prop(self, f"val_vector_{el}_toggle", text=f"{v_subelements[el].upper()}", toggle=True)

            # Conditions
            row3 = row2.row(align=True)
            subrow = row3.column(align=True)

            for el in range(0, len(func.attribute_func.get_attribute_default_value(attribute))):
                disable_cond = not (el != 0 and self.b_single_condition_vector)
                disabler_row = subrow.row()
                if (getattr(self, f'val_vector_{el if not disable_cond else 0}_toggle') if not disable_cond else True) and disable_cond:
                    disabler_row.prop(self, f"vec_{el}_condition_enum", text="")

            # Values
            row3 = row2.row(align=True)
            subrow = row3.column(align=True)

            if not self.b_use_color_picker:
                for el in range(0, len(func.attribute_func.get_attribute_default_value(attribute))):
                    disable_cond = not (el != 0 and self.b_single_value_vector)
                    disabler_row = subrow.row()
                    if disable_cond:
                        disabler_row.prop(self, f"val_{dt.lower()}", text=f" ", index=el if disable_cond else 0)


            else:
                for el in range(0, len(func.attribute_func.get_attribute_default_value(attribute))):
                    subrow.prop(self, f"val_{dt.lower()}", text="")

            if gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR:
                row = col.row(align=True)
                subrow = row.row(align=True)
                subrow.ui_units_x = 3
                subrow.label(text="") # leave a space
                row.label(text="")
                row.prop(self, f"b_use_color_picker", toggle=True)


            row = layout.row(align=True)
            subrow = row.row(align=True)
            subrow.prop(self, 'b_deselect', text=f"Select {func.util_func.get_friendly_domain_name(domain, True)}" if not self.b_deselect else f"Deselect {func.util_func.get_friendly_domain_name(domain, True)}", toggle=True, invert_checkbox=True)
            subrow.ui_units_x = 5
            row.prop(self, 'vector_value_cmp_type_enum', text="")