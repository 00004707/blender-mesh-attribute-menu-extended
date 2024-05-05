from modules.ui import ui_common, static_data


class AttributesToExternalFile(bpy.types.Operator):
    bl_idname = "mesh.attribute_export"
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
        items=func.enum_func.get_attribute_domains_enum
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
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def invoke(self, context, event):
        func.ui_func.refresh_attribute_UIList_elements(context)
        func.ui_func.configutre_attribute_uilist(False, False)
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
            attributes = [func.attribute_func.get_active_attribute(obj)]

        elif self.which_attributes_enum ==  "SPECIFIC":
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            attributes = []
            for a in [a for a in gui_prop_group.to_mesh_data_attributes_list if a.b_select]:
                attributes.append(obj.data.attributes[a.attribute_name])

        if not len(attributes):
            self.report({'ERROR'}, f'No attributes to export with selected filters.')
            return  {'CANCELLED'}


        try:
            func.file_io_func.write_csv_attributes_file(self.filepath, obj, attributes, self.b_add_domain_and_data_type_to_title_row)
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
        active_attribute = func.attribute_func.get_active_attribute(obj)
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
            ui_common.draw_multi_attribute_select_uilist(col)

        col.label(text="")
        col.label(text="Extra options")
        col.prop(self, 'b_add_domain_and_data_type_to_title_row')

        col.label(text="")
        col.label(icon='INFO', text=f"Header row naming convention:")
        if self.b_add_domain_and_data_type_to_title_row:
            col.label(icon="LAYER_ACTIVE", text=f"AttributeName(DATATYPE)(DOMAIN)")
        else:
            col.label(icon="LAYER_ACTIVE", text=f"AttributeName")