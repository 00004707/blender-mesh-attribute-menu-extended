"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

UI Interface Definition in 3D View

"""

# Sculpt Mode
# -----------------------------------------

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
        return context.mode == 'SCULPT' and etc.preferences.get_preferences_attrib('extra_header_sculpt')

    def draw(self, context):

        obj_prop_group = context.active_object.data.MAME_PropValues
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
        row2.label(text=f"Modify {func.util_func.get_friendly_name_from_enum_function(context, gui_prop_group.get_enum_sculpt_mode_attribute_mode_toggle_enum, gui_prop_group.enum_sculpt_mode_attribute_mode_toggle)}")
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_apply", icon='ZOOM_PREVIOUS')
        row.operator("mesh.mame_attribute_sculpt_mode_apply_inverted",text="Inverted", icon='SELECT_SUBTRACT')
    
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_extend", text="Add", icon='ZOOM_IN')
        row.operator("mesh.mame_attribute_sculpt_mode_subtract", text="Subtract", icon='ZOOM_OUT')
        col.operator('mesh.selected_in_edit_mode_to_sculpt_mode_mask', text="From Edit Mode Selection", icon='RESTRICT_SELECT_OFF')
        
        # Manage sub-menu
        row2 = col.row(align=True)
        row2.label(text="Manage")
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_new",text="Store", icon='FILE_NEW')
        row.operator("mesh.mame_attribute_sculpt_mode_remove",text="Remove", icon='PANEL_CLOSE')
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_overwrite",text="Overwrite Attribute", icon='COPYDOWN')
        
        col.menu('VIEW3D_MT_select_test', text='Settings', text_ctxt='', translate=True, icon='SETTINGS')

        
        # Show warning for multiresolution
        for mod in context.active_object.modifiers:
            if mod.type == 'MULTIRES':
                box = col.box()
                col2 = box.column(align=True)
                r= col2.row()
                r.label(icon='ERROR', text="Warning")
                r.alert=True
                col2.label(text="Multiresolution is not-compatible")
                break

        if len(context.active_object.data.vertices) > etc.LARGE_MESH_VERTICES_COUNT:
            box = col.box()
            col2 = box.column(align=True)
            r= col2.row()
            r.label(icon='ERROR', text="Warning")
            r.alert=True
            col2.label(text="HiPoly mesh - slow operatons")
