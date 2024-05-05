from modules import LEGACY_etc
from ops.main.AssignActiveAttribValueToSelection import AssignActiveAttribValueToSelection


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
        items=func.enum_func.get_attribute_invert_modes
    )

    # Trick to show the "Subtract from one" as first dropdown entry for color attributes
    def invert_attrib_color_mode_enum(self, context):
        # reverse
        return func.enum_func.get_attribute_invert_modes(self, context)[::-1]

    # The dropdown menu for inverting modes for selected color attributes
    color_invert_mode_enum: bpy.props.EnumProperty(
        name="Invert Mode",
        description="Select an option",
        items=invert_attrib_color_mode_enum
    )

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
        elif not func.poll_func.pinned_mesh_poll(self, context, True):
            return False
        return True

    def execute(self, context):
        try:
            # If it's pinned mesh, we need to get data and reference from somewhere else.
            b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
            if b_pinned_mesh_in_use:
                obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
                LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
            else:
                obj = context.active_object
            src_attrib_name = obj.data.attributes.active.name
            current_mode = context.active_object.mode

            # Compatibility Check
            if not func.util_func.get_attribute_compatibility_check(obj.data.attributes[src_attrib_name]):
                self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
                return {'CANCELLED'}

            # Operators below need to work on object level. If pinned switch to referenced object.
            if b_pinned_mesh_in_use:
                current_active_object = bpy.context.active_object
                current_selection_state_of_obj = obj.select_get()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

            bpy.ops.object.mode_set(mode='OBJECT')

            src_attrib = obj.data.attributes[src_attrib_name] # !important

            # get selected domain indexes
            selected = func.obj_func.get_mesh_selected_domain_indexes(obj, src_attrib.domain, self.b_face_corner_spill)

            LEGACY_etc.log(InvertAttribute, f"Selected domain indexes: {selected}", LEGACY_etc.ELogLevel.VERBOSE)

            # No selection and selection mode is enabled?
            if not len(selected) and self.b_edit_mode_selected_only:
                self.report({'ERROR'}, f"No selection to perform the operations onto")

                # Switch back to the previous object if pinned mesh was used
                if b_pinned_mesh_in_use:
                    bpy.context.view_layer.objects.active = current_active_object
                    obj.select_set(current_selection_state_of_obj)

                bpy.ops.object.mode_set(mode=current_mode)
                return {'CANCELLED'}

            # # numbers:
            # else:
            prop_name = func.attribute_func.get_attribute_value_propname(src_attrib)

            storage = func.attribute_func.get_attribute_values(src_attrib, obj)

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
                skip = len(func.attribute_func.get_attribute_default_value(src_attrib)) if not src_attrib.data_type == 'FLOAT' else 1
                if invert_mode == "MULTIPLY_MINUS_ONE":
                    storage = [v * -1 if not self.b_edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)]
                elif invert_mode == "SUBTRACT_FROM_ONE":
                    storage = [1-v if not self.b_edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)]
                elif invert_mode == "ADD_TO_MINUS_ONE":
                    storage = [-1+v if not self.b_edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)]

            func.attribute_func.set_attribute_values(src_attrib, storage, b_foreach_compatible_value_list=True)

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
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        row = self.layout
        b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
        if b_pinned_mesh_in_use:
            obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
            LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
        else:
            obj = context.active_object

        # Show the drop-down menu for invert mode types
        prop = "invert_mode_enum" if context.active_object.data.attributes.active.data_type not in ['FLOAT_COLOR', 'BYTE_COLOR'] else "color_invert_mode_enum"
        sub_box = row.row()
        sub_box.enabled = len(func.enum_func.get_attribute_invert_modes(self, context)) != 1
        sub_box.prop(self, prop, text="Invert Mode")

        # selected only
        if obj.mode =='EDIT':
            row.prop(self, "b_edit_mode_selected_only", text="Selected only")
            # spill face corners
            if context.active_object.data.attributes.active.domain == 'CORNER':
                row.prop(self, "b_face_corner_spill", text="Face Corner Spill")