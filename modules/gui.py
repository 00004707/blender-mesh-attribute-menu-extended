
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
from . import static_data
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
                    dt = ob.data.attributes.active.data_type
                    prop_group = context.object.MAME_PropValues

                    # Check for supported types
                    if not func.get_attribute_compatibility_check(ob.data.attributes.active):
                        sublayout = layout.column()
                        sublayout.alert = True
                        sublayout.label(text="This attribute type is not supported by MAME addon.", icon='ERROR')
                        sublayout.operator('mame.report_issue')
                    else:
                        col = layout.row()
                        #col.split = 0.5
                        col2 = col.row(align=True)
                        if dt == 'BOOLEAN':
                            title_str = "True" if prop_group.val_bool else "False"
                        else:
                            title_str = ""

                        col2.prop(prop_group, f"val_{dt.lower()}", text=title_str, toggle=True)
                        col2.operator('mesh.attribute_gui_value_randomize', text="", icon='FILE_REFRESH')
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
                        sub.operator("mesh.attribute_select_button", text=f"Select")
                        sub.operator("mesh.attribute_deselect_button", text=f"Deselect")
                        
                        
                        sub = col.row(align=True)
                        sub.ui_units_x = 1
                        sub.prop(prop_group, "val_select_non_zero_toggle", text=f"Ø", toggle=True)
                    
        else:
            if etc.get_preferences_attrib('debug_operators'):
                # Extra tools
                # sub = row.row(align=True)
                row.operator("mame.tester", text="run tests")
                row.operator("mame.create_all_attribs", text="attrib test")


        # Quick Attribute Node Menu
        

        if etc.get_preferences_attrib("quick_attribute_node_enable"):
            box = layout.box()
            row = box.row()
            row.label(text="Quick Attribute Node")
            
            obj = context.active_object
            if obj and obj.data.attributes.active:

                areas = func.get_supported_areas_for_attribute(obj.data.attributes.active, ids=True)

                if len(areas):
                    col = box.grid_flow(columns=2, align=False, even_columns=True, even_rows=True)
                    for i, area in enumerate(areas):
                        node_editor_icon = static_data.node_editors[func.get_node_editor_type(area, use_id=True)].icon
                        nt = func.get_area_node_tree(area, useid=True)
                        parent = func.get_node_tree_parent(nt)
                        if nt is None:
                            continue
                        elif parent is None:
                            parentname = nt.name
                        else:
                            parentname = parent.name
                        subrow = col.row(align=False)
                        op = subrow.operator("mesh.attribute_create_attribute_node", text=f"{i+1}: {parentname}", icon=node_editor_icon)
                        op.windowid = area[0]
                        op.areaid = area[1]
                elif not func.get_node_editor_areas():
                    box.label(text="No node editors are open", icon='ERROR') 
                else:
                   box.label(text="None of Node Editors support this attribute", icon='ERROR') 

            else:
                box.label(text="No active attribute", icon='ERROR')

            if etc.get_preferences_attrib('debug_operators'):
                areas = func.get_node_editor_areas()
                col = box.column(align=True)
                for i, area in enumerate(areas):
                    col.label(text=f"{i+1}: {func.get_node_editor_type(area)}")
        


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
    self.layout.operator('mesh.attribute_randomize_value', icon='SHADERFX')
    #self.layout.operator('mesh.attribute_conditioned_remove', icon='X')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE') 

def sculpt_mode_mask_menu_extension(self, context):
    """
    Extra entries in sculpt mode mask menu on the menu bar
    """
    
    if etc.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_current_sculpt_mask', icon='MESH_DATA') 
        self.layout.operator('mesh.attribute_quick_sculpt_mask_from_active_attribute', icon='MOD_MASK')

def sculpt_mode_face_sets_menu_extension(self, context):
    """
    Extra entries in sculpt mode face sets menu on the menu bar
    """
    if etc.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_face_sets', icon='MESH_DATA') 
        self.layout.operator('mesh.attribute_quick_face_sets_from_attribute', icon='FACE_MAPS')

class SculptMode3DViewHeaderSettings(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_select_test"
    bl_label = "Settings"

    def draw(self, context):
        layout = self.layout
        prop_group = context.object.MAME_PropValues
        layout.prop(prop_group, "qops_sculpt_mode_attribute_show_unsupported")

def sculpt_mode_3dview_header_extension(self, context):
    if bpy.context.mode == 'SCULPT':
        if etc.get_preferences_attrib('extra_header_sculpt'):
            prop_group = context.object.MAME_PropValues
            box = self.layout.box()
            row = box.row(align=True)

            row.ui_units_x = 14.0

            box2 = row.box()
            box2.ui_units_x = 1.0
            box2.prop(prop_group, "enum_sculpt_mode_attribute_mode_toggle", text="")

            box2 = row.box()
            box2.ui_units_x = 3.7
            box2.prop(prop_group, "enum_sculpt_mode_attribute_selector", text="")

            row.operator("mesh.mame_attribute_sculpt_mode_apply", text="", icon='ZOOM_PREVIOUS')
            row.operator("mesh.mame_attribute_sculpt_mode_extend", text="", icon='ZOOM_IN')
            row.operator("mesh.mame_attribute_sculpt_mode_subtract", text="", icon='ZOOM_OUT')
            row.operator("mesh.mame_attribute_sculpt_mode_invert", text="", icon='SELECT_SUBTRACT')
            row.operator("mesh.mame_attribute_sculpt_mode_new", text="", icon='FILE_NEW')
            row.operator("mesh.mame_attribute_sculpt_mode_remove", text="", icon='PANEL_CLOSE')
            row.operator("mesh.mame_attribute_sculpt_mode_overwrite", text="", icon='COPYDOWN')
            
            row.menu('VIEW3D_MT_select_test', text='', text_ctxt='', translate=True, icon='SETTINGS')

def vertex_groups_context_menu_extension(self,context):
    
    if etc.get_preferences_attrib('extra_context_menu_vg'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_vertex_group', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_all_vertex_groups', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_vertex_group_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_vertex_group_assignment', icon='MESH_DATA')

def shape_keys_context_menu_extension(self,context):
    if etc.get_preferences_attrib('extra_context_menu_sk'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_shape_key', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_offset_from_shape_key', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_all_shape_keys', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_offset_from_all_shape_keys', icon='MESH_DATA')

def material_context_menu_extension(self,context):
    if etc.get_preferences_attrib('extra_context_menu_materials'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_material_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_material_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_material_slot_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_material_slot_assignment', icon='MESH_DATA')

def edge_context_menu_extension(self,context):
    if etc.get_preferences_attrib('extra_context_menu_edge_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()

def face_context_menu_extension(self,context):
    if etc.get_preferences_attrib('extra_context_menu_face_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()

def object_context_menu_extension(self,context):
    if etc.get_preferences_attrib('extra_context_menu_object'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()


def sculpt_mode_mask_menu_extension(self, context):
    """
    Extra entries in sculpt mode mask menu on the menu bar
    """
    
    if etc.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_current_sculpt_mask', icon='MESH_DATA') 
        self.layout.operator('mesh.attribute_quick_sculpt_mask_from_active_attribute', icon='MOD_MASK')

def sculpt_mode_face_sets_menu_extension(self, context):
    """
    Extra entries in sculpt mode face sets menu on the menu bar
    """
    if etc.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_face_sets', icon='MESH_DATA') 
        self.layout.operator('mesh.attribute_quick_face_sets_from_attribute', icon='FACE_MAPS')

class SculptMode3DViewHeaderSettings(bpy.types.Menu):
    """
    Menu shown in sculpt mode tool n-panel menu, Mask Manager submenu
    
    Contains extra toggles that are not required to be visible by default
    """
    bl_idname = "VIEW3D_MT_select_test"
    bl_label = "Settings"

    def draw(self, context):
        layout = self.layout
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        layout.prop(gui_prop_group, "qops_sculpt_mode_attribute_show_unsupported")
        layout.prop(gui_prop_group, "qops_sculpt_mode_mask_normalize")

class MasksManagerPanel(bpy.types.Panel):
    """
    The panel menu in N-Panel Tool tab and properties panel Tool tab.

    Allows managing masks and face sets from attributes in a quicker way
    """
    bl_label = "Mask Manager"
    bl_idname = "TOOL_PT_MAME_Masks_Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'


    # Show only in sculpt mode and if enabled in preferences
    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and etc.get_preferences_attrib('extra_header_sculpt')

    def draw(self, context):

        obj_prop_group = context.active_object.MAME_PropValues
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        
        col = self.layout.column(align=True)

        # box2.ui_units_x = 1.0

        # Toggle between masks and face sets
        row2 = col.row(align=True)
        row2.label(text="Mode")
        row2 = col.row(align=True)
        
        row2.prop_enum(gui_prop_group, "enum_sculpt_mode_attribute_mode_toggle", "MASK")
        row2.prop_enum(gui_prop_group, "enum_sculpt_mode_attribute_mode_toggle", "FACE_SETS")

        # Attribute selector dropdown menu
        row2 = col.row(align=True)
        row2.label(text="Attribute")
        box2 = col.row(align=True)
        box2.ui_units_x = 5
        gui_prop_group.validify_enums() # make sure the selection in dropdown exists
        box2.prop(gui_prop_group, "enum_sculpt_mode_attribute_selector", text="")

        # Modify sub-menu
        row2 = col.row(align=True)
        row2.label(text=f"Modify {func.get_friendly_name_from_enum_function(context, gui_prop_group.get_enum_sculpt_mode_attribute_mode_toggle_enum, gui_prop_group.enum_sculpt_mode_attribute_mode_toggle)}")
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_apply", icon='ZOOM_PREVIOUS')
        row.operator("mesh.mame_attribute_sculpt_mode_apply_inverted",text="Inverted", icon='SELECT_SUBTRACT')
    
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_extend", text="Add", icon='ZOOM_IN')
        row.operator("mesh.mame_attribute_sculpt_mode_subtract", text="Subtract", icon='ZOOM_OUT')
        
        # Manage sub-menu
        row2 = col.row(align=True)
        row2.label(text="Manage")
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_new",text="Store", icon='FILE_NEW')
        row.operator("mesh.mame_attribute_sculpt_mode_remove",text="Remove", icon='PANEL_CLOSE')
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_overwrite",text="Overwrite", icon='COPYDOWN')
        
        col.menu('VIEW3D_MT_select_test', text='Settings', text_ctxt='', translate=True, icon='SETTINGS')

        # Show warning for multiresolution
        for mod in context.active_object.modifiers:
            if mod.type == 'MULTIRES':
                box = col.box()
                col = box.column(align=True)
                r= col.row()
                r.label(icon='ERROR', text="Warning")
                r.alert=True
                col.label(text="Multiresolution is not-compatible")
        