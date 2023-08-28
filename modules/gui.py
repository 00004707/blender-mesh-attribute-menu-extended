
"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
gui

Everything related to user interface.

"""
 
import bpy 
from . import func
from . import data
from . import etc
from . import debug

# Properties Panel
# -----------------------------------------

def attribute_assign_panel(self, context):
    """
    Buttons underneath the attributes list in Attributes Menu located in Properties Panel
    """

    layout = self.layout
    row = layout.row()
    ob = context.active_object

    if ( ob and ob.type == 'MESH'):

        # Edit mode menu
        if ( ob.mode == 'EDIT' and ob.data.attributes.active):

            if etc.get_preferences_attrib('attribute_assign_menu'):
                    
                # Do not edit hidden attributes
                if not func.get_is_attribute_valid_for_manual_val_assignment(ob.data.attributes.active):
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
                        col = layout.row()
                        #col.split = 0.5
                        col2 = col.row(align=True)
                        col2.prop(prop_group, data.attribute_data_types[dt].gui_property_name, text="Boolean Value" if dt == 'BOOLEAN' else f"")
                        col2.ui_units_x = 40
 
                        col2 = col.row(align=True)
                        #col2.ui_units_x = 4
                        if ob.data.attributes.active.domain == "CORNER":
                            col2.prop(prop_group, "face_corner_spill", text=f"Spill", toggle=True)
                        else:
                            col2.operator("mesh.always_disabled_face_corner_spill_operator", text=f"Spill")
                        col2.operator("mesh.attribute_read_value_from_selected_domains", text="Read")

                        col = layout.row()

                        # Assignment buttons
                        sub = col.row(align=True)
                        btn_assign = sub.operator('object.set_active_attribute_to_selected', text=f"Assign")
                        btn_assign.b_clear = False
                        btn_assign.b_face_corner_spill_enable = prop_group.face_corner_spill
                        btn_clear = sub.operator('object.set_active_attribute_to_selected', text=f"Clear")
                        btn_clear.b_clear = True
                        btn_clear.b_face_corner_spill_enable = prop_group.face_corner_spill

                        #Selection buttons
                        sub = col.row(align=True)
                        sub.operator_context = 'EXEC_DEFAULT'
                        sub.operator("mesh.attribute_zero_value_select", text=f"Select")
                        sub.operator("mesh.attribute_zero_value_deselect", text=f"Deselect")
                        
                    
        else:
            if etc.get_preferences_attrib('debug_operators'):
                # Extra tools
                # sub = row.row(align=True)
                row.operator("mame.tester", text="run tests")
                row.operator("mame.create_all_attribs", text="attrib test")


def attribute_context_menu_extension(self, context):
    """
    Extra entries in ^ menu
    """

    self.layout.operator_context = "INVOKE_DEFAULT"
    if etc.get_preferences_attrib('add_set_attribute') and bpy.app.version >= (3,5,0):
        self.layout.operator('mesh.attribute_set')
    self.layout.operator('mesh.attribute_create_from_data', icon='MESH_DATA')
    self.layout.operator('mesh.attribute_convert_to_mesh_data', icon='MESH_ICOSPHERE')
    self.layout.operator('mesh.attribute_duplicate', icon='DUPLICATE')
    self.layout.operator('mesh.attribute_invert', icon='UV_ISLANDSEL')
    self.layout.operator('mesh.attribute_copy', icon='COPYDOWN')
    self.layout.operator('mesh.attribute_resolve_name_collisions', icon='SYNTAX_OFF')
    self.layout.operator('mesh.attribute_conditioned_select', icon='CHECKBOX_HLT')
    #self.layout.operator('mesh.attribute_conditioned_remove', icon='X')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE') 

class FakeFaceCornerSpillDisabledOperator(bpy.types.Operator):
    """
    Fake operator to occupy GUI place
    .disabled is not available for properties in gui, so this is the hack
    """

    bl_idname = "mesh.always_disabled_face_corner_spill_operator"
    bl_label = "Fake operator to occupy GUI place"
    bl_description = "Enable Face Corner Spill"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Active attribute is not on Face Corner domain")
        return False