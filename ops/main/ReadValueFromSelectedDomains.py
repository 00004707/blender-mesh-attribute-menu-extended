from modules import LEGACY_static_data


class ReadValueFromSelectedDomains(bpy.types.Operator):
    """
    Reads the active attribute value from selected domains (absolute if single domain, average if multiple), and sets it in GUI
    """

    bl_idname = "mesh.attribute_read_value_from_selected_domains"
    bl_label = "Sample from selected domains"
    bl_description = "Reads the attribute value under selected domains and sets it in GUI"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        elif not context.active_object.mode == 'EDIT' :
            self.poll_message_set("Not in edit mode")
            return False
        elif context.active_object.data.attributes.active is None :
            self.poll_message_set("No active attribute")
            return False
        elif not context.active_object.data.attributes.active.data_type in LEGACY_static_data.attribute_data_types :
            self.poll_message_set("Data type is not yet supported!")
            return False
        elif bool(len([atype for atype in func.attribute_func.get_attribute_types(context.active_object.data.attributes.active) if atype in [LEGACY_static_data.EAttributeType.NOTPROCEDURAL]])) :
            self.poll_message_set("This attribute is unsupported (Non-procedural)")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False

        return True

    def execute(self, context):

        obj = context.active_object
        active_attribute_name = obj.data.attributes.active.name

        # Compatibility Check
        if not func.util_func.get_attribute_compatibility_check(obj.data.attributes[active_attribute_name]):
            self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        attribute = obj.data.attributes[active_attribute_name]
        prop_group = context.object.data.MAME_PropValues
        domain = obj.data.attributes[active_attribute_name].domain
        dt = attribute.data_type

        domain_indexes = func.obj_func.get_mesh_selected_domain_indexes(obj, domain, prop_group.face_corner_spill)

        if not len(domain_indexes):
            self.report({'ERROR'}, f"No selected {func.util_func.get_friendly_domain_name(domain)}")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}

        # Get the value to set in GUI
        if dt in ['STRING', 'BOOLEAN']:
            # get the value from first index of selection
            if len(domain_indexes) > 1:
                self.report({'WARNING'}, f"Tip: select single {func.util_func.get_friendly_domain_name(domain)} instead to always get expected result for {func.util_func.get_friendly_data_type_name(dt)}s")
            attribute_value = getattr(obj.data.attributes[active_attribute_name].data[domain_indexes[0]], func.attribute_func.get_attribute_value_propname(attribute))
        else:
            # Get average for numeric


            # get default value to calc the avg
            attribute_value = func.attribute_func.get_attribute_default_value(attribute)
            if type(attribute_value) == list:
                    attribute_value = tuple(attribute_value)

            # get the total
            for vi in domain_indexes:
                val = getattr(obj.data.attributes[active_attribute_name].data[vi], func.attribute_func.get_attribute_value_propname(attribute))

                if type(val) in [bpy_types.bpy_prop_array, Vector]:
                    val = tuple(val)
                    attribute_value = tuple(vv+attribute_value[i] for i, vv in enumerate(val))
                else:
                    attribute_value += val

            # and the avg
            if type(attribute_value) == tuple:
                attribute_value = tuple(tv/len(domain_indexes) for tv in attribute_value)
            else:
                attribute_value /= len(domain_indexes)

        # Get int for ints
        if dt in ['INT', 'INT8']:
            attribute_value = int(round(attribute_value))
        if dt in ['INT32_2D']:
            v = []
            for el in attribute_value:
                v.append(int(round(el)))
            attribute_value = tuple(v)

        # Set the attribute value in GUI
        setattr(prop_group, f'val_{dt.lower()}', attribute_value)

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}