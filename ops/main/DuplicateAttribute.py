from modules import LEGACY_etc


class DuplicateAttribute(bpy.types.Operator):
    """
    Simply duplicates an attribute
    """

    bl_idname = "mesh.attribute_duplicate"
    bl_label = "Duplicate Attribute"
    bl_description = "Duplicate Active Attribute"
    bl_options = {'REGISTER', 'UNDO'}

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
                LEGACY_etc.log(DuplicateAttribute, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
            else:
                obj_data = context.active_object.data
                obj = context.active_object

            attrib_name = obj_data.attributes.active.name
            current_mode = context.active_object.mode # Use active mesh in viewport for this, not pinned mesh

            # Compatibility Check
            if not func.util_func.get_attribute_compatibility_check(obj_data.attributes[attrib_name]):
                self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
                return {'CANCELLED'}

            # Operators below need to work on object level. If pinned switch to referenced object.
            if b_pinned_mesh_in_use:
                current_active_object = bpy.context.active_object
                current_selection_state_of_obj = obj.select_get()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

            # All attribute actions should be performed in object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            src_attrib = obj_data.attributes[attrib_name] #!important

            new_attrib = obj_data.attributes.new(name=src_attrib.name, type=src_attrib.data_type, domain=src_attrib.domain)

            func.attribute_func.set_attribute_values(new_attrib, func.attribute_func.get_attribute_values(src_attrib, obj))

            # Switch back to the previous object if pinned mesh was used
            if b_pinned_mesh_in_use:
                bpy.context.view_layer.objects.active = current_active_object
                obj.select_set(current_selection_state_of_obj)

            bpy.ops.object.mode_set(mode=current_mode)
            return {'FINISHED'}
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(DuplicateAttribute, exc)
            return {"CANCELLED"}