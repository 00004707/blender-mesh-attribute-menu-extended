
# ------------------------------------------
# gui
 
import bpy 
from . import func
from . import data
from . import etc

def attribute_assign_panel(self, context):
    """
    Buttons underneath the attributes list
    """

    layout = self.layout
    row = layout.row()
    ob = context.active_object

    if ( ob and ob.type == 'MESH'):
        if ( ob.mode == 'EDIT' and ob.data.attributes.active):

            # Do not edit hidden attributes
            if not func.get_is_attribute_valid(ob.data.attributes.active.name): 
                row.label(text="Editing of non-editable and hidden attributes is disabled.")
            else:
                friendly_domain_name = "mesh domain"
                if ob.data.attributes.active.domain == 'POINT':
                    friendly_domain_name = "Vertex"
                elif ob.data.attributes.active.domain == 'EDGE':
                    friendly_domain_name = "Edge"
                elif ob.data.attributes.active.domain == 'FACE':
                    friendly_domain_name = "Face"
                elif ob.data.attributes.active.domain == 'CORNER':
                    friendly_domain_name = "Face Corner"
                

                dt = ob.data.attributes.active.data_type
                prop_group = context.object.MAME_PropValues

                # Check for supported types
                if dt not in data.attribute_data_types:
                    layout.label(text="This attribute type is not supported.")
                else:
                    # Assignment buttons
                    sub = row.row(align=True)
                    btn_assign = sub.operator('object.set_active_attribute_to_selected', text=f"Assign")
                    btn_assign.clear = False
                    btn_assign.fc_spill = prop_group.face_corner_spill
                    btn_clear = sub.operator('object.set_active_attribute_to_selected', text=f"Clear")
                    btn_clear.clear = True
                    btn_clear.fc_spill = prop_group.face_corner_spill

                    #Selection buttons
                    sub = row.row(align=True)
                    sub.operator_context = 'EXEC_DEFAULT'
                    # Input fields for each type
                    if dt == "FLOAT":
                        sub.operator("mesh.attribute_zero_value_select", text="Select≠0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect≠0")
                        layout.prop(prop_group, "val_float", text=f"{friendly_domain_name} Float Value")

                    elif dt == "INT":
                        sub.operator("mesh.attribute_zero_value_select", text="Select≠0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect≠0")
                        layout.prop(prop_group, "val_int", text=f"{friendly_domain_name} Integer Value")

                    elif dt == "FLOAT_VECTOR":
                        sub.operator("mesh.attribute_zero_value_select", text="Select≠0,0,0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect≠0,0,0")
                        layout.prop(prop_group, "val_vector", text=f"{friendly_domain_name} Vector Value")

                    elif dt == "FLOAT_COLOR":
                        sub.operator("mesh.attribute_zero_value_select", text="Select Non Black")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect Non Black")
                        layout.prop(prop_group, "val_color", text=f"{friendly_domain_name} Color Value")

                    elif dt == "BYTE_COLOR":
                        sub.operator("mesh.attribute_zero_value_select", text="Select Non Black")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect Non Black")
                        layout.prop(prop_group, "val_bytecolor", text=f"{friendly_domain_name} Bytecolor Value")

                    elif dt == "STRING":
                        sub.operator("mesh.attribute_zero_value_select", text="Select Non Empty")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect Non Empty")
                        layout.prop(prop_group, "val_string", text=f"{friendly_domain_name} String Value")

                    elif dt == "BOOLEAN":
                        sub.operator("mesh.attribute_zero_value_select", text="Select True")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect True")
                        layout.prop(prop_group, "val_bool", text=f"{friendly_domain_name} Boolean Value")

                    elif dt == "FLOAT2":
                        sub.operator("mesh.attribute_zero_value_select", text="Select≠0,0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect≠0,0")
                        layout.prop(prop_group, "val_vector2d", text=f"{friendly_domain_name} Vector 2D Value")

                    elif dt == "INT32_2D":
                        sub.operator("mesh.attribute_zero_value_select", text="Select≠0,0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect≠0,0")
                        layout.prop(prop_group, "val_int32_2d", text=f"{friendly_domain_name} 2D Int Vector Value")

                    elif dt == "QUATERNION":
                        sub.operator("mesh.attribute_zero_value_select", text="Sel≠1,0,0,0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Desel≠1,0,0,0")
                        layout.prop(prop_group, "val_quaternion", text=f"{friendly_domain_name} Quaternion Value")

                    elif dt == "INT8":
                        sub.operator("mesh.attribute_zero_value_select", text="Select≠0")
                        sub.operator("mesh.attribute_zero_value_deselect", text="Deselect≠0")
                        layout.prop(prop_group, "val_int8", text=f"{friendly_domain_name} 8-bit Integer Value")
                        

                # Toggle Face Corner Spill 
                if ob.data.attributes.active.domain == "CORNER":
                    layout.prop(prop_group, "face_corner_spill", text=f"Face Corner Spill")
        else:
            # Extra tools
            # sub = row.row(align=True)
            if etc.enable_debug_tester:
                row.operator("mame.tester", text="debug tester")
            pass


def attribute_context_menu_extension(self, context):
    """
    Extra entries in ^ menu
    """
    self.layout.operator_context = "INVOKE_DEFAULT"
    self.layout.operator('mesh.attribute_set')
    self.layout.operator('mesh.attribute_create_from_data', icon='MESH_DATA')
    self.layout.operator('mesh.attribute_convert_to_mesh_data', icon='MESH_ICOSPHERE')
    self.layout.operator('mesh.attribute_duplicate', icon='DUPLICATE')
    self.layout.operator('mesh.attribute_invert', icon='UV_ISLANDSEL')
    self.layout.operator('mesh.attribute_copy', icon='COPYDOWN')
    self.layout.operator('mesh.attribute_resolve_name_collisions', icon='SYNTAX_OFF')
    # self.layout.operator('mesh.attribute_find', icon='VIEWZOOM')
    # self.layout.operator('mesh.attributes_sort', icon='SEQ_HISTOGRAM')
    self.layout.operator('mesh.attribute_conditioned_select', icon='CHECKBOX_HLT')
    #self.layout.operator('mesh.attribute_conditioned_remove', icon='X')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE') 
