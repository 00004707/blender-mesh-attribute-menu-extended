import func.util_func
from modules import LEGACY_etc, LEGACY_static_data


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
    if func.util_func.get_blender_support(LEGACY_static_data.attribute_data_types['INT8'].min_blender_ver, LEGACY_static_data.attribute_data_types['INT8'].unsupported_from_blender_ver):
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
    if func.util_func.get_blender_support(LEGACY_static_data.attribute_data_types['INT32_2D'].min_blender_ver, LEGACY_static_data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
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
    if func.util_func.get_blender_support(LEGACY_static_data.attribute_data_types['QUATERNION'].min_blender_ver, LEGACY_static_data.attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
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
        elif not context.active_object.data.attributes.active.data_type in LEGACY_static_data.attribute_data_types :
            self.poll_message_set("Data type is not yet supported!")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False

        # elif bool(len([atype for atype in func.get_attribute_types(context.active_object.data.attributes.active) if atype in [data.EAttributeType.NOTPROCEDURAL]])) :
        #     self.poll_message_set("This attribute is unsupported (Non-procedural)")
        #     return False
        return True

    def gui_values_check(self, context):
        active_attribute = context.active_object.data.attributes.active
        dt = active_attribute.data_type
        e_dt = LEGACY_static_data.EAttributeDataType[dt]

        # Strings check
        if e_dt == LEGACY_static_data.EAttributeDataType.STRING:
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
        elif LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.VECTOR:
            any_toggle_on = []
            for i in range(0, len(LEGACY_static_data.attribute_data_types[dt].vector_subelements_names)):
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
        if not func.util_func.get_attribute_compatibility_check(obj.data.attributes[active_attribute_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        attribute = obj.data.attributes[active_attribute_name]
        prop_group = context.object.data.MAME_PropValues
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
            on_domains = func.obj_func.get_mesh_selected_domain_indexes(obj, domain, self.b_face_corner_spill)
            if not len(on_domains):
                self.report({"ERROR"}, "No selection in edit mode. (\"on selected\" mode was used)")
                bpy.ops.object.mode_set(mode=current_mode)
                return {'CANCELLED'}

        else:
            on_domains = np.arange(0, len(attribute.data))

        # Get values set in UI
        rnd_min = None
        rnd_max = None
        e_dt = LEGACY_static_data.EAttributeDataType[dt]
        if e_dt in [LEGACY_static_data.EAttributeDataType.FLOAT,
                    LEGACY_static_data.EAttributeDataType.INT,
                    LEGACY_static_data.EAttributeDataType.INT8,
                    LEGACY_static_data.EAttributeDataType.INT32_2D,
                    LEGACY_static_data.EAttributeDataType.FLOAT2,
                    LEGACY_static_data.EAttributeDataType.FLOAT_COLOR,
                    LEGACY_static_data.EAttributeDataType.FLOAT_VECTOR,
                    LEGACY_static_data.EAttributeDataType.BYTE_COLOR,
                    LEGACY_static_data.EAttributeDataType.QUATERNION,
                    LEGACY_static_data.EAttributeDataType.STRING]:
            rnd_min = getattr(self, f"{dt.lower()}_val_min")
            rnd_max = getattr(self, f"{dt.lower()}_val_max")


        # Read current values
        storage = func.attribute_func.get_attribute_values(attribute, obj)
        LEGACY_etc.log(RandomizeAttributeValue, f"Current values:{np.array(storage)}", LEGACY_etc.ELogLevel.VERBOSE)

        # Get random values list
        rnd_vals = func.attribute_func.get_random_attribute_of_data_type(context,
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

        LEGACY_etc.log(RandomizeAttributeValue, f"Randomized values:{rnd_vals}", LEGACY_etc.ELogLevel.VERBOSE)

        # Set the values
        func.attribute_func.set_attribute_values(attribute, rnd_vals, on_domains)

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

        e_dt = LEGACY_static_data.EAttributeDataType[dt]
        gui_prop_subtype = LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype

        # ints & floats
        if gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.SCALAR:
            col = self.layout.column(align=True)
            col.prop(self, f"{dt.lower()}_val_min", text="Min")
            col.prop(self, f"{dt.lower()}_val_max", text="Max")

        # vectors & colors
        elif gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.VECTOR, LEGACY_static_data.EDataTypeGuiPropType.COLOR]:

            vector_is_a_color = gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR

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
                    for i in range(0,len(func.attribute_func.get_attribute_default_value(active_attribute))):
                        sub_row = row.row(align=True)
                        sub_row.enabled = getattr(self, f'val_vector_{i}_toggle')
                        sub_row.prop(self, f"{dt.lower()}_val_{minmax}", text="", index=i)

            # Each toggle for each vector subelement
            row = col2.row(align=True)
            for i in range(0,len(func.attribute_func.get_attribute_default_value(active_attribute))):
                if vector_is_a_color and self.color_randomize_type == 'HSVA':
                    gui_vector_subel = ['H','S','V','A'][i]
                else:
                    gui_vector_subel = LEGACY_static_data.attribute_data_types[dt].vector_subelements_names[i]
                row.prop(self, f"val_vector_{str(i)}_toggle", text=gui_vector_subel.upper(), toggle=True)

            row = col2.row(align=True)
            if vector_is_a_color:
                row.prop(self, "b_use_color_picker", toggle=True)

        # boolean
        elif gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.BOOLEAN:
            col = self.layout.column(align=True)
            col.prop(self, f"boolean_probability", text="Probability")

        # string
        elif gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.STRING:
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