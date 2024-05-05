import bpy

import func.util_func
from modules import LEGACY_etc, LEGACY_static_data


class AssignActiveAttribValueToSelection(bpy.types.Operator):
    """
    This operator will set active attribute value to values set in GUI or clear them to "zero" value.
    Operation is limited to edit mode selection
    """

    # BLENDER CLASS PROPERTIES
    # ---------------------------------

    bl_idname = "object.set_active_attribute_to_selected"
    bl_label = "Assign Active Attribute Value To Selection in Edit Mode"
    bl_description = "Assigns active attribute value to selection in edit mode."
    bl_options = {'REGISTER', 'UNDO'}

    # COMMON
    # ---------------------------------

    # Operator supports working with pinned mesh in properties panel
    b_pinned_mesh_support = True

    # Operator supports working in nodegroup context instead of datablock context
    b_nodegroup_context_support = False

    # Operator required active object to work
    b_active_object_required = False

    # Operator can edit these types of meshes
    supported_object_types = ['MESH', 'CURVES']

    # Implemented data type support
    supported_data_types = ['FLOAT', 'INT', 'INT8',
                            'FLOAT_VECTOR', 'FLOAT_COLOR', 'BYTE_COLOR', 'STRING',
                            'BOOLEAN', 'FLOAT2', 'INT32_2D', 'QUATERNION', 'FLOAT4X4']

    # Implemented domain support
    supported_domains = ['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE']

    # Wiki URL suffix
    wiki_url = 'Assign-Value-to-Active-Attribute-on-Edit-Mode-Selection'

    # OPTIONS
    # ---------------------------------

    # The toggle to clear attribute value - set it's value to the "zero" value
    b_clear: bpy.props.BoolProperty(name="clear", default = False)

    # The toggle to enable face corner spilling to nearby face corners of selected vertices/edges/faces
    b_face_corner_spill_enable: bpy.props.BoolProperty(name="Face Corner Spill",
                                                       default = False,
                                                       description="Allow setting value to nearby corners of selected vertices or limit it only to selected face",)

    @classmethod
    def poll(self, context):

        obj, obj_data = func.obj_func.get_object_in_context(context)
        # gui_prop_group = context.window_manager.MAME_GUIPropValues

        if not func.poll_func.pinned_mesh_poll(self, context, self.b_pinned_mesh_support):
            self.poll_message_set("Pinned mesh mode unsupported")
            return False
        # if gui_prop_group.operators_context == 'NODEGROUP' and not self.b_nodegroup_context_support:
        #     self.poll_message_set("Geometry Nodes context not supported")
        #     return False
        elif self.b_active_object_required and not bpy.context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not obj:
            self.poll_message_set("No active object or no pinned object")
            return False
        elif obj.type not in self.supported_object_types:
            self.poll_message_set("Object type is not supported")
            return False
        elif obj.name not in bpy.context.scene.objects:
            self.poll_message_set("Pinned mesh not in scene")
            return False
        elif not obj.mode  == 'EDIT' :
            self.poll_message_set("Not in edit mode")
            return False
        elif obj_data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        elif not func.attribute_func.get_is_attribute_valid_for_manual_val_assignment(obj_data.attributes.active):
            self.poll_message_set("Attribute is read-only or unsupported")
            return False
        elif obj_data.attributes.active.data_type not in self.supported_data_types:
            self.poll_message_set("Attribute Data Type is not supported")
            return False
        elif obj_data.attributes.active.domain not in self.supported_domains:
            self.poll_message_set("Attribute Domain is not supported")
            return False
        return True

    def execute(self, context):
        try:
            obj, obj_data = func.obj_func.get_object_in_context(context)
            b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
            active_attrib_name = obj_data.attributes.active.name
            prop_group = obj_data.MAME_PropValues
            mesh_selected_modes = bpy.context.scene.tool_settings.mesh_select_mode
            dt = obj_data.attributes[active_attrib_name].data_type

            LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Working on {active_attrib_name} attribute", LEGACY_etc.ELogLevel.VERBOSE)

            # Compatibility Check
            if not func.util_func.get_attribute_compatibility_check(obj_data.attributes[active_attrib_name]):
                self.report({'ERROR'}, "Attribute data type or domain unsupported! Addon needs an update.")
                return {'CANCELLED'}

            # Operators below need to work on object level. If pinned switch to referenced object.
            func.obj_func.set_object_in_context_as_active(self, context)

            # Use bpy.ops.mesh_attribute_set()
            try:
                if ((obj.type == 'MESH' and func.util_func.get_blender_support((3,5,0)) or (obj.type == 'CURVES' and func.util_func.get_blender_support((4,1,0))))
                    # Operator will make sure the values are a valid quaternion
                    and not (dt == 'QUATERNION' and LEGACY_etc.preferences.get_preferences_attrib("set_attribute_raw_quaterion"))
                    # Face corner spill feature is not supported by the operator 
                    and not (not prop_group.face_corner_spill and mesh_selected_modes[1])
                    # Strings are unsupported by this operator                          
                    and LEGACY_static_data.attribute_data_types[dt].bpy_ops_set_attribute_param_name is not None
                    # Preferences toggle  
                    and not LEGACY_etc.preferences.get_preferences_attrib("disable_bpy_set_attribute")):

                    LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Using ops.mesh_attribute_set()", LEGACY_etc.ELogLevel.VERBOSE)

                    params = {}
                    paramname = LEGACY_static_data.attribute_data_types[dt].bpy_ops_set_attribute_param_name
                    params[paramname] = getattr(prop_group, f'val_{dt.lower()}')
                    if obj.type == 'MESH':
                        bpy.ops.mesh.attribute_set(**params)
                    elif obj.type == 'CURVES':
                        bpy.ops.curves.attribute_set(**params)

                    # Switch back to the previous object if pinned mesh was used
                    func.obj_func.set_object_by_user_as_active_back(self, context)
                    return {"FINISHED"}

            except TypeError:
                if func.util_func.get_blender_support((4,1,0)) and dt in ["INT32_2D", "QUATERNION", "FLOAT4X4"]:
                    LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Using ops.mesh_attribute_set() failed due to a blender bug, using pre 3.5 method", LEGACY_etc.ELogLevel.WARNING)

            # Use custom method
            bpy.ops.object.mode_set(mode='OBJECT')
            attribute = obj_data.attributes[active_attrib_name] #!important

            # Get value from GUI
            if dt in LEGACY_static_data.attribute_data_types:

                gui_value = getattr(prop_group, f'val_{dt.lower()}')
                LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Attribute data read", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                if type(gui_value) in [bpy_types.bpy_prop_array, Vector]:
                    gui_value = tuple(gui_value)

                value = func.attribute_func.get_attribute_default_value(attribute) if self.b_clear else gui_value
                LEGACY_etc.log(AssignActiveAttribValueToSelection, f"Value read - {value}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                # Set the value
                func.attribute_func.set_attribute_value_on_selection(self, context, obj, attribute, value, face_corner_spill=self.b_face_corner_spill_enable)

                # Switch back to the previous object if pinned mesh was used
                func.obj_func.set_object_by_user_as_active_back(self, context)
                bpy.ops.object.mode_set(mode='EDIT')

                return {"FINISHED"}
            else:
                self.report({'ERROR', "Unsupported data type!"})

                # Switch back to the previous object if pinned mesh was used
                func.obj_func.set_object_by_user_as_active_back(self, context)
                bpy.ops.object.mode_set(mode='EDIT')

                return {"CANCELLED"}

        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(AssignActiveAttribValueToSelection, exc)
            return {"CANCELLED"}