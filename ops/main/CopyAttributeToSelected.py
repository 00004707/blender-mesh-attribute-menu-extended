import modules.ui.ui_common
from modules import LEGACY_etc, LEGACY_static_data


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

        active_attrib = context.active_object.data.attributes.active # todo

        if not active_attrib:
            self.poll_message_set("No active attribute")
            return False
        elif not len(context.selected_objects) > 1:
            self.poll_message_set("Select multiple objects")
            return False
        elif not True not in [obj.type != 'MESH' for obj in bpy.context.selected_objects]:
            self.poll_message_set("One of selected objects is not a mesh")
        # Check if the attribute can be copied
        elif any([atype == LEGACY_static_data.EAttributeType.READONLY for atype in func.attribute_func.get_attribute_types(active_attrib)]):
            self.poll_message_set("This attribute is read-only")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
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

            types = func.attribute_func.get_attribute_types(src_obj.data.attributes[a_name])
            print(f"{a_name} : {types}")
            if LEGACY_static_data.EAttributeType.READONLY in types:
                errors.append([a_name, "Attribute is read-only"])

            if self.copy_what_enum == 'ALL':

                if not self.b_all_filter_internal and LEGACY_static_data.EAttributeType.INTERNAL in types:
                    continue
                elif not self.b_all_filter_non_procedural and LEGACY_static_data.EAttributeType.NOTPROCEDURAL in types:
                    continue
                elif not self.b_all_filter_autogenerated and LEGACY_static_data.EAttributeType.AUTOGENERATED in types:
                    continue
                elif not self.b_all_filter_hidden and LEGACY_static_data.EAttributeType.HIDDEN in types:
                    continue

            valid_attrs.append(a_name)

        attribute_names_to_copy = valid_attrs

        if len(attribute_names_to_copy) == 0:
            self.report({'ERROR'},  "No valid attributes to copy")

        bpy.ops.object.mode_set(mode='OBJECT')

        for sel_obj in [sel_obj for sel_obj in bpy.context.selected_objects if sel_obj.type =='MESH' and sel_obj is not src_obj]:
            for src_attrib_name in attribute_names_to_copy:
                src_attrib = src_obj.data.attributes[src_attrib_name] # !important
                a_vals = func.attribute_func.get_attribute_values(src_attrib, src_obj)

                # get size of the source attribute domain
                source_size = self.get_attribute_data_length(src_obj, src_attrib)

                sel_obj_attr = None

                # check if present in target mesh
                if src_attrib_name in [a.name for a in sel_obj.data.attributes]:
                    LEGACY_etc.log(CopyAttributeToSelected, f"Attribute {src_attrib.name} exists on target", LEGACY_etc.ELogLevel.VERBOSE)

                    sel_obj_attr = sel_obj.data.attributes[src_attrib_name]

                    # overwrite if present?
                    if not self.b_overwrite:
                        continue

                    #overwrite different type?
                    not_same_type = sel_obj_attr.domain != src_attrib.domain or sel_obj_attr.data_type != src_attrib.data_type
                    if not_same_type and not self.b_overwrite_different_type:

                        LEGACY_etc.log(CopyAttributeToSelected, f"Attribute {src_attrib.name} is not the same type as {sel_obj_attr.name}, {sel_obj_attr.domain}!={src_attrib.domain} or {sel_obj_attr.data_type}!={src_attrib.data_type}", LEGACY_etc.ELogLevel.VERBOSE)

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
                            fill_value = func.attribute_func.get_attribute_default_value(src_attrib)
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

                func.attribute_func.set_attribute_values(sel_obj_attr, target_a_vals)

                sel_obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)

        if len(errors):
            errors = [f"Copy failed for {e[0]} attribute: {e[1]}" for e in errors]
            modules.ui.ui_common.set_message_box_function(modules.ui.ui_common.draw_error_list)
            modules.ui.ui_common.set_message_box_extra_data(errors)

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
            modules.ui.ui_common.draw_multi_attribute_select_uilist(row)

    def invoke(self, context, event):
        func.ui_func.refresh_attribute_UIList_elements(context)
        func.ui_func.configutre_attribute_uilist(False,False)
        return context.window_manager.invoke_props_dialog(self)