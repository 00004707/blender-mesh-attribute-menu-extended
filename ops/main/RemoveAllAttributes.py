import etc.property_groups
import func.util_func
from modules import LEGACY_etc, LEGACY_static_data
from ops.main.AssignActiveAttribValueToSelection import AssignActiveAttribValueToSelection


class RemoveAllAttributes(bpy.types.Operator):
    """
    Removes all attributes
    """
    bl_idname = "mesh.attribute_remove_all"
    bl_label = "Remove all by type"
    bl_description = "Removes multiple attributes"
    bl_options = {'REGISTER', 'UNDO'}

    # Whether to include the UVMaps when removing attributes
    b_include_uvs: bpy.props.BoolProperty(
        name="Include UVMaps",
        description="All Vector2D attributes stored in Face Corners",
        default=False
        )

    # Whether to include color attributes when removing attributes
    b_include_color_attribs: bpy.props.BoolProperty(
        name="Include Color Attributes",
        description="All Color attributes stored in Vertices or Face Corners",
        default=False
        )

    # Whether to include attributes tagged as DONOTREMOVE
    b_include_all: bpy.props.BoolProperty(
        name="Include non-recommended",
        description="Include attributes that you probably do not want to remove, like shade smooth.",
        default=False
        )

    # Whether to include attributes starting with a dot
    b_include_hidden: bpy.props.BoolProperty(
        name="Include Hidden attributes",
        description="Include hidden attributes starting with a dot in name",
        default=False
        )

    b_include_sculpt_mask: bpy.props.BoolProperty(
        name="Include Sculpt Mask",
        description=".sculpt_mask attribute",
        default=False
        )


    #Collection with all datatypes filter toggles
    remove_datatype_filter: bpy.props.CollectionProperty(type = LEGACY_etc.property_groups.GenericBoolPropertyGroup)

    #Collection with all domain filter toggles
    remove_domain_filter: bpy.props.CollectionProperty(type = LEGACY_etc.property_groups.GenericBoolPropertyGroup)



    # Quick check if an attribute is an UVMap
    def is_uvmap(self, a):
        return a.domain == 'CORNER' and a.data_type == 'FLOAT2'

    # Quick check if an attribute is a color attribute
    def is_color_attrib(self, a):
        return (a.domain == 'CORNER' or a.domain == 'POINT') and (a.data_type == 'FLOAT_COLOR' or a.data_type == 'BYTE_COLOR')

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH' :
            self.poll_message_set("Object is not a mesh")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, True):
            return False

        # Pinned mesh
        if func.util_func.is_pinned_mesh_used(context):
            obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
        else:
            obj = context.active_object

        # Pinned mesh ref can return None
        if not obj:
            return False

        # Check if there is any attibute that can be removed
        for a in obj.data.attributes:
            types = func.attribute_func.get_attribute_types(a)
            editable = True
            for e in [LEGACY_static_data.EAttributeType.CANTREMOVE]:
                if e in types:
                    editable = False
                    break
            if editable:
                return True

        self.poll_message_set("No removable attributes")
        return False

    def execute(self, context):
        try:
            # If it's pinned mesh, we need to get data and reference from somewhere else.
            b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
            if b_pinned_mesh_in_use:
                obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
                LEGACY_etc.log(RemoveAllAttributes, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
            else:
                obj = context.active_object

            # Operators below need to work on object level. If pinned switch to referenced object.
            if b_pinned_mesh_in_use:
                current_active_object = bpy.context.active_object
                current_selection_state_of_obj = obj.select_get()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

            current_mode = context.active_object.mode # use the active object in viewport for this, not pinned mesh
            bpy.ops.object.mode_set(mode='OBJECT')
            num = 0

            attrib_names = [a.name for a in obj.data.attributes]

            for name in attrib_names:

                # If the name is not in the attributes for some weird reason ignore.
                if name not in obj.data.attributes:
                    continue

                a = obj.data.attributes[name]
                a_types = func.attribute_func.get_attribute_types(a)

                # If the attribute cannot be removed, ignore
                if LEGACY_static_data.EAttributeType.CANTREMOVE in a_types :
                    continue
                conditions = []

                # Check if is an uvmap 
                conditions.append(self.b_include_uvs if self.is_uvmap(a) else True)

                # Check for color attributes
                conditions.append(self.b_include_color_attribs if self.is_color_attrib(a) else True)

                # Check if it is a sculpt mode mask
                if name == '.sculpt_mask' and func.util_func.get_blender_support(LEGACY_static_data.built_in_attributes['.sculpt_mask'].min_blender_ver):
                    conditions.append(self.b_include_sculpt_mask)

                # Check if it's hidden
                else:
                    conditions.append(self.b_include_hidden if LEGACY_static_data.EAttributeType.HIDDEN in a_types else True)

                # Check if it's non-recommended
                conditions.append(self.b_include_all if LEGACY_static_data.EAttributeType.DONOTREMOVE in a_types else True)

                # Check data type

                dt = obj.data.attributes[name].data_type
                allow = False
                for el in self.remove_datatype_filter:
                    if el.id == dt:
                        allow = el.b_value
                        break
                conditions.append(allow)

                # Check domain
                domain = obj.data.attributes[name].domain
                allow = False
                for el in self.remove_domain_filter:
                    if el.id == domain:
                        allow = el.b_value
                        break
                conditions.append(allow)

                if all(conditions):
                    LEGACY_etc.log(RemoveAllAttributes, f"Attribute removed - {a.name}: {a.domain}, {a.data_type}", LEGACY_etc.ELogLevel.VERBOSE)
                    obj.data.attributes.remove(a)
                    num += 1

            obj.data.update()

            # Switch back to the previous object if pinned mesh was used
            if b_pinned_mesh_in_use:
                bpy.context.view_layer.objects.active = current_active_object
                obj.select_set(current_selection_state_of_obj)

            bpy.ops.object.mode_set(mode=current_mode)
            self.report({'INFO'}, (f"Removed {str(num)} attribute" + ("s" if num > 1 else "") if num else "None of attributes removed!"))
            return {'FINISHED'}
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(AssignActiveAttribValueToSelection, exc)
            return {"CANCELLED"}

    def invoke(self, context, event):
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        list_elements = gui_prop_group.to_mesh_data_attributes_list

        # Get data type toggles 
        self.remove_datatype_filter.clear()
        for data_type in func.enum_func.get_attribute_data_types():
            b = self.remove_datatype_filter.add()
            b.b_value = True
            b.name = func.util_func.get_friendly_data_type_name(data_type)
            b.id = data_type

        # Get domain toggles 
        self.remove_domain_filter.clear()
        for domain in func.enum_func.get_attribute_domains():
            b = self.remove_domain_filter.add()
            b.b_value = True
            b.name = func.util_func.get_friendly_domain_name(domain)
            b.id = domain

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout

        row.label(text="Include")
        col = row.column(align=True)

        colrow = col.row(align=True)

        subcolprop = colrow.row(align=True)
        # subcolprop.enabled = bpy.app.version >= (3,5,0)
        subcolprop.prop(self, "b_include_uvs", text="UVMaps", toggle=True)
        colrow.prop(self, "b_include_color_attribs", text="Color Attributes", toggle=True)

        # Sculpt mode mask if supported
        if func.util_func.get_blender_support(LEGACY_static_data.built_in_attributes['.sculpt_mask'].min_blender_ver):
            colrow.prop(self, "b_include_sculpt_mask", text="Sculpt Mask", toggle=True)

        colrow = col.row(align=True)

        colrow.prop(self, "b_include_hidden", text="Hidden", toggle=True)
        colrow.prop(self, "b_include_all", text="Non-Recommended", toggle=True)


        col.label(text="Filter Domains")
        filter_row = col.row(align=True)
        filter_row = col.grid_flow(columns=4, even_columns=False, align=True)
        for boolprop in self.remove_domain_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)

        col.label(text="Filter Data Types")
        filter_row = col.grid_flow(columns=3, even_columns=False, align=True)
        for boolprop in self.remove_datatype_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)