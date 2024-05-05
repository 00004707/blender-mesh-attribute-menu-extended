import modules.ui.ui_common
from modules import LEGACY_etc


class CreateBuiltInAttribute(bpy.types.Operator):
    """
    Creates attributes that are generated by blender when using some nodes, built-in attributes
    """

    # BLENDER CLASS PROPERTIES
    # ---------------------------------

    bl_idname = "mesh.attribute_built_in_create"
    bl_label = "Create Built In Attribute"
    bl_description = "Creates built in attributes used and recognized by blender"
    bl_options = {'REGISTER', 'UNDO'}

    # COMMON
    # ---------------------------------

    b_pinned_mesh_support = True
    b_active_object_required = False
    supported_object_types = ['MESH', 'CURVES', 'POINTCLOUD']
    wiki_url = 'Create-Built‐In-Attribute'

    # OPTIONS
    # ---------------------------------

    # The dropdown menu for all predefined attributes
    built_in_attribute_enum: bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.enum_func.get_built_in_attributes_enum
    )

    # Dropdown menu for selecting attribute domain, if multiple
    built_in_attribute_domain: bpy.props.EnumProperty(
        name="Domain",
        description="Select an option",
        items=func.util_func.get_built_in_attribute_compatible_domains_enum
    )

    # Dropdown menu for selecting attribute data type, if multiple
    built_in_attribute_data_type: bpy.props.EnumProperty(
        name="Data Type",
        description="Select an option",
        items=func.util_func.get_built_in_attribute_compatible_data_types_enum
    )

    # Property group with all available attribute data types
    attribute_values_propgroup: bpy.props.PointerProperty(type=func.prop_group_func.get_all_attribute_data_types_property_group(False))

    # Show all attributes, even if usually those cannot be created
    b_show_persistent: bpy.props.BoolProperty(name="Show persistent attributes",
                                              description="Show attributes that usually cannot be created or modified",
                                              default=False)

    # Shows real attribute names instead of friendly string
    b_show_attribute_names: bpy.props.BoolProperty(name="Real Names",
                                              description="Show attribute names instead of friendly name",
                                              default=False)

    # Allow assigning custom value instead of default one to the selected attribute
    b_custom_value: bpy.props.BoolProperty(name="Custom Value",
                                              description="Use value outside of expected range",
                                              default=False)

    # Some attributes contain uvmap name
    uvmaps_enum: bpy.props.EnumProperty(
        name="UV Map",
        description="Select an option",
        items=func.enum_func.get_uvmaps_enum
    )

    # UTILITY METHODS
    # ---------------------------------

    def user_input_check(self):
        # Checks user input, returns cancelled if invalid

        if self.built_in_attribute_enum in [".vs.", ".es.", ".pn."] and self.uvmaps_enum == 'NULL':
            self.report({'ERROR'}, "No UV Maps - Attribute not created")
            return {'CANCELLED'}

    def enum_watchdog_attribute(self, context):
        "Bug bypass for blender handling of dynamically populated enums"
        try:
            if getattr(self, f'built_in_attribute_enum') == '':
                setattr(self, f'built_in_attribute_enum', func.enum_func.get_built_in_attributes_enum(self, context)[0][0])
        except TypeError:
            pass

    def enum_watchdog_domain(self, context):
        "Bug bypass for blender handling of dynamically populated enums"
        try:
            if getattr(self, f'built_in_attribute_domain') == '':
                setattr(self, f'built_in_attribute_domain', func.util_func.get_built_in_attribute_compatible_domains_enum(self, context)[0][0])
        except TypeError:
            pass

    def enum_watchdog_data_type(self, context):
        "Bug bypass for blender handling of dynamically populated enums"
        try:
            if getattr(self, f'built_in_attribute_data_type') == '':
                setattr(self, f'built_in_attribute_data_type', func.util_func.get_built_in_attribute_compatible_data_types_enum(self, context)[0][0])
        except TypeError:
            pass

    # FEATURE METHODS
    # ---------------------------------

    def create_built_in_attribute(self, context):
        # Creates a built-in attribute of choice

        self.user_input_check()

        obj, obj_data = func.obj_func.get_object_in_context(context)

        # Store current object mode of object in viewport to restore later
        current_mode = context.active_object.mode

        # Operators below need to work on object level. If pinned switch to referenced object.
        func.obj_func.set_object_in_context_as_active(self, context)

        # All attribute actions should be performed in object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get definition of built in attribute
        new_attr_def = func.util_func.get_built_in_attribute(self.built_in_attribute_enum)

        # Set new attribute name
        if self.built_in_attribute_enum in [".vs.", ".es.", ".pn."]:
            uvmaps = func.obj_data_func.get_uvmaps(obj_data)
            target_uvmap = uvmaps[int(self.uvmaps_enum)]
            new_attr_name = str(self.built_in_attribute_enum) + str(target_uvmap.name)
        else:
            new_attr_name = self.built_in_attribute_enum

        try:
            # Remove existing, if applicable

            if new_attr_name in obj_data.attributes:
                obj_data.attributes.remove(obj_data.attributes[new_attr_name])

            # Create new and assign valid reference

            new_attrib = obj_data.attributes.new(name=new_attr_name,
                                                type=self.built_in_attribute_data_type,
                                                domain=self.built_in_attribute_domain)
        except RuntimeError:
            pass # If cannot create or remove, ignore and overwrite value

        new_attrib = obj_data.attributes[new_attr_name] #!important

        # Set default value or set value if enabled
        if self.b_custom_value:
            value = func.prop_group_func.get_all_attribute_datatype_property_group_value(self.attribute_values_propgroup,
                                                                               self.built_in_attribute_data_type)
        else:
            value = new_attr_def.default_value
        func.attribute_func.set_attribute_values(new_attrib, value)

        # Switch back to the previous object if pinned mesh was used
        func.obj_func.set_object_by_user_as_active_back(self, context)

        # Restore previous object mode
        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, F"Created \"{new_attr_name}\" attribute")
        return {'FINISHED'}

    # BLENDER METHODS
    # ---------------------------------

    @classmethod
    def poll(self, context):
        obj, obj_data = func.obj_func.get_object_in_context(context)

        if not obj:
            self.poll_message_set("No active or invalid pinned object")
            return False
        elif not obj.type in self.supported_object_types :
            self.poll_message_set("Object type is not supported")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, self.b_pinned_mesh_support):
            return False
        return True

    def execute(self, context):
        try:
            return self.create_built_in_attribute(context)
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(CreateBuiltInAttribute, exc)
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
        obj, obj_data = func.obj_func.get_object_in_context(context)

        # Update enum so it won't be None (bug bypass)
        self.enum_watchdog_attribute(context)
        self.enum_watchdog_domain(context)
        self.enum_watchdog_data_type(context)

        # Show the drop-down menu
        sub_box = row.column()
        sub_box.label(text="Built-In Attribute")
        srow = sub_box.row(align=True)
        srow.prop(self, 'built_in_attribute_enum', text="")
        ssrow = srow.row(align=True)
        ssrow.ui_units_x = 3
        ssrow.prop(self, 'b_show_attribute_names', toggle=True)

        # Global options
        c = row.column()
        c.prop(self, 'b_show_persistent', toggle=True)

        # Domain selector (if applicable)
        c.separator()
        c.label(text='Domain')
        if len(func.util_func.get_built_in_attribute_compatible_domains_enum(self, context)) == 1:
            c.label(text=func.util_func.get_friendly_domain_name(self.built_in_attribute_domain),
                    icon=func.util_func.get_domain_icon(self.built_in_attribute_domain))
        else:
            c.prop(self, 'built_in_attribute_domain', text='')

        # Data type selector (if applicable)
        c.separator()
        c.label(text='Data Type')
        if len(func.util_func.get_built_in_attribute_compatible_data_types_enum(self, context)) == 1:
            c.label(text=func.util_func.get_friendly_data_type_name(self.built_in_attribute_data_type),
                    icon=func.util_func.get_data_type_icon(self.built_in_attribute_data_type))
        else:
            c.prop(self, 'built_in_attribute_data_type', text='')

        # Custom value
        c.separator()
        c.label(text='Custom value')
        c.prop(self, 'b_custom_value', toggle=True)
        val_row = c.row()
        if self.b_custom_value:
            modules.ui.ui_common.get_attribute_value_input_ui(val_row,
                                            self.attribute_values_propgroup,
                                            func.prop_group_func.get_property_name_by_data_type_in_all_attribute_property_group(self.built_in_attribute_data_type),
                                            self.built_in_attribute_data_type)
        else:
            val_row.label(text='')

        # Update again
        self.enum_watchdog_attribute(context)

        # Show UVMap selector for .pn. and other attributes
        c.separator()
        if self.built_in_attribute_enum in [".vs.", ".es.", ".pn."]:
            c.label(text="UV Map")
            c.prop(self, 'uvmaps_enum', text='')
        else:
            c.label(text="")
            c.label(text="")

        # Show that value exists and will be overwritten
        c.separator()
        if self.built_in_attribute_enum in obj_data.attributes:
            if self.b_custom_value:
                val_str = str(func.prop_group_func.get_all_attribute_datatype_property_group_value(self.attribute_values_propgroup,
                                                                               self.built_in_attribute_data_type))
            else:
                val_str = "default value"
            c.label(text="Attribute exists", icon="ERROR")
            c.label(text="Values will be set to " + val_str,)
        else:
            c.label(text='') # Occupy space to maintain window size
            c.label(text='')

        # Wiki
        modules.ui.ui_common.append_wiki_operator(self, context)