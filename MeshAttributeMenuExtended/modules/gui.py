
# ------------------------------------------
# gui
 
import bpy 
from . import func

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
                if dt not in ['FLOAT', 'INT', 'INT8', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'BYTE_COLOR', 'STRING', 'BOOLEAN', 'FLOAT2']:
                    layout.label(text="This attribute type is not supported.")
                else:
                    # Assignment buttons
                    sub = row.row(align=True)
                    btn_assign = sub.operator('object.set_active_attribute_to_selected', text=f"Assign")
                    btn_assign.clear = False
                    btn_clear = sub.operator('object.set_active_attribute_to_selected', text=f"Clear")
                    btn_clear.clear = True

                    #Selection buttons
                    sub = row.row(align=True)
                    sub.operator_context = 'EXEC_DEFAULT'
                    # Input fields for each type
                    if dt == "FLOAT":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select≠0")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect≠0")
                        dsel_op.numeric_condition_enum = sel_op.numeric_condition_enum = "NEQ"
                        dsel_op.val_float = sel_op.val_float = 0.0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_float", text=f"{friendly_domain_name} Float Value")

                    elif dt == "INT":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select≠0")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect≠0")
                        dsel_op.numeric_condition_enum = sel_op.numeric_condition_enum = "NEQ"
                        dsel_op.val_int = sel_op.val_int = 0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_int", text=f"{friendly_domain_name} Integer Value")

                    elif dt == "FLOAT_VECTOR":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select≠0,0,0")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect≠0,0,0")
                        dsel_op.vec_x_condition_enum = sel_op.vec_x_condition_enum = "NEQ"
                        dsel_op.vec_y_condition_enum = sel_op.vec_y_condition_enum = "NEQ"
                        dsel_op.vec_z_condition_enum = sel_op.vec_z_condition_enum = "NEQ"
                        dsel_op.vec_w_condition_enum = sel_op.vec_w_condition_enum = "NEQ"
                        dsel_op.val_vector_x_toggle = sel_op.val_vector_x_toggle = True
                        dsel_op.val_vector_y_toggle = sel_op.val_vector_y_toggle = True
                        dsel_op.val_vector_z_toggle = sel_op.val_vector_z_toggle = True
                        dsel_op.val_vector_w_toggle = sel_op.val_vector_w_toggle = True
                        dsel_op.val_float_x = sel_op.val_float_x = 0.0
                        dsel_op.val_float_y = sel_op.val_float_y = 0.0
                        dsel_op.val_float_z = sel_op.val_float_z = 0.0
                        dsel_op.val_float_w = sel_op.val_float_w = 0.0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_vector", text=f"{friendly_domain_name} Vector Value")

                    elif dt == "FLOAT_COLOR":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select Non Black")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect Non Black")
                        dsel_op.vec_x_condition_enum = sel_op.vec_x_condition_enum = "NEQ"
                        dsel_op.vec_y_condition_enum = sel_op.vec_y_condition_enum = "NEQ"
                        dsel_op.vec_z_condition_enum = sel_op.vec_z_condition_enum = "NEQ"
                        dsel_op.vec_w_condition_enum = sel_op.vec_w_condition_enum = "NEQ"
                        dsel_op.val_vector_x_toggle = sel_op.val_vector_x_toggle = True
                        dsel_op.val_vector_y_toggle = sel_op.val_vector_y_toggle = True
                        dsel_op.val_vector_z_toggle = sel_op.val_vector_z_toggle = True
                        dsel_op.val_vector_w_toggle = sel_op.val_vector_w_toggle = True
                        dsel_op.val_float_x = sel_op.val_float_x = 0.0
                        dsel_op.val_float_y = sel_op.val_float_y = 0.0
                        dsel_op.val_float_z = sel_op.val_float_z = 0.0
                        dsel_op.val_float_w = sel_op.val_float_w = 0.0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_color", text=f"{friendly_domain_name} Color Value")

                    elif dt == "BYTE_COLOR":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select Non Black")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect Non Black")
                        dsel_op.vec_x_condition_enum = sel_op.vec_x_condition_enum = "NEQ"
                        dsel_op.vec_y_condition_enum = sel_op.vec_y_condition_enum = "NEQ"
                        dsel_op.vec_z_condition_enum = sel_op.vec_z_condition_enum = "NEQ"
                        dsel_op.vec_w_condition_enum = sel_op.vec_w_condition_enum = "NEQ"
                        dsel_op.val_vector_x_toggle = sel_op.val_vector_x_toggle = True
                        dsel_op.val_vector_y_toggle = sel_op.val_vector_y_toggle = True
                        dsel_op.val_vector_z_toggle = sel_op.val_vector_z_toggle = True
                        dsel_op.val_vector_w_toggle = sel_op.val_vector_w_toggle = True
                        dsel_op.val_float_x = sel_op.val_float_x = 0.0
                        dsel_op.val_float_y = sel_op.val_float_y = 0.0
                        dsel_op.val_float_z = sel_op.val_float_z = 0.0
                        dsel_op.val_float_w = sel_op.val_float_w = 0.0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_bytecolor", text=f"{friendly_domain_name} Bytecolor Value")

                    elif dt == "STRING":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select Non Empty")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect Non Empty")
                        dsel_op.numeric_condition_enum = sel_op.numeric_condition_enum = "NEQ"
                        dsel_op.val_string = sel_op.val_string = ""
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_string", text=f"{friendly_domain_name} String Value")

                    elif dt == "BOOLEAN":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select True")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect True")
                        dsel_op.bool_condition_enum = sel_op.bool_condition_enum = "EQ"
                        dsel_op.val_bool = sel_op.val_bool = True
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_bool", text=f"{friendly_domain_name} Boolean Value")

                    elif dt == "FLOAT2":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select≠0,0")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect≠0,0")
                        dsel_op.vec_x_condition_enum = sel_op.vec_x_condition_enum = "NEQ"
                        dsel_op.vec_y_condition_enum = sel_op.vec_y_condition_enum = "NEQ"
                        dsel_op.val_vector_x_toggle = sel_op.val_vector_x_toggle = True
                        dsel_op.val_vector_y_toggle = sel_op.val_vector_y_toggle = True
                        dsel_op.val_float_x = sel_op.val_float_x = 0.0
                        dsel_op.val_float_y = sel_op.val_float_y = 0.0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_vector2d", text=f"{friendly_domain_name} Vector 2D Value")

                    elif dt == "INT8":
                        sel_op = sub.operator("mesh.attribute_conditioned_select", text="Select≠0")
                        dsel_op = sub.operator("mesh.attribute_conditioned_select", text="Deselect≠0")
                        dsel_op.numeric_condition_enum = sel_op.numeric_condition_enum = "NEQ"
                        dsel_op.val_int8 = sel_op.val_int8 = 0
                        sel_op.deselect = False
                        dsel_op.deselect = True
                        layout.prop(prop_group, "val_int8", text=f"{friendly_domain_name} 8-bit Integer Value")
                        

                    
                
                # Toggle Face Corner Spill 
                if ob.data.attributes.active.domain == "CORNER":
                    layout.prop(prop_group, "face_corner_spill", text=f"Face Corner Spill")
        else:
            # Extra tools
            # sub = row.row(align=True)
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
    # self.layout.operator('mesh.attribute_find', icon='VIEWZOOM')
    # self.layout.operator('mesh.attributes_sort', icon='SEQ_HISTOGRAM')
    self.layout.operator('mesh.attribute_conditioned_select', icon='CHECKBOX_HLT')
    #self.layout.operator('mesh.attribute_conditioned_remove', icon='X')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE') 
