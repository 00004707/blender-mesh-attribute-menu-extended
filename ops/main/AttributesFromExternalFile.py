import modules.ui.ui_common


class AttributesFromExternalFile(bpy.types.Operator):
    bl_idname = "mesh.attribute_import"
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
        items=func.enum_func.get_attribute_domains_enum
    )

    data_type_selector_enum: bpy.props.EnumProperty(
        name="Data Type",
        description="Select an option",
        items=func.enum_func.get_attribute_data_types_enum
    )

    b_remove_domain_str_from_name: bpy.props.BoolProperty(name="Remove domain string from name", description="Removes parts like \"(POINT)\" from name", default=True)
    b_remove_data_type_str_from_name: bpy.props.BoolProperty(name="Remove data type string from name", description="Removes parts like \"(FLOAT)\" from name", default=True)

    @classmethod
    def poll(self, context):
        if not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        args = {}
        if self.domain_detect_enum == "DEFINEDFORALL":
            args['force_domain'] = self.domain_selector_enum
        if self.data_type_detect_enum == "DEFINEDFORALL":
            args['force_data_type'] = self.data_type_selector_enum

        status, errors, count = func.file_io_func.csv_to_attributes(self.filepath, context.active_object, [], self.b_remove_domain_str_from_name, self.b_remove_data_type_str_from_name, **args)

        if not len(errors):
            # bpy.ops.window_manager.mame_message_box(icon='INFO', message=f'Successfully imported {count} attributes from CSV file.')
            self.report({'INFO'}, f'Successfully imported {count} attributes from CSV file.')
        else:
            modules.ui.ui_common.set_message_box_function(modules.ui.ui_common.draw_error_list)
            modules.ui.ui_common.set_message_box_extra_data(errors)

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