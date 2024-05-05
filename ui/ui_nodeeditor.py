"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

UI Interface Definition in node editors

"""


# Context Menus
# -----------------------------------------

import func.node_func


class NODE_PT_MAME_panel_utility(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "MAME"
    bl_label = "Utility"

    def draw(self, context):
        self.layout.operator_context = "INVOKE_DEFAULT"
    
        layout = self.layout
        layout.separator()
        
        # That node does have some geometry outputs
        if len(func.node_func.get_geometry_node_geometry_output_pins(context.active_node)):
            self.layout.operator('mesh.node_output_to_object', text=f'Output to a new object')
        if len(func.node_func.get_geometry_node_boolean_inputs(context.active_node)):
            self.layout.operator('mesh.node_mark_selection', text=f'Mark selection in edit mode', icon='TRACKER')

def geometry_nodes_node_menubar_extension(self, context):
    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"

    if (# If node editor is geometry nodes
        func.node_func.get_node_editor_type(space_data=context.space_data) == 'GeometryNodeTree' 
        # And any node is selected
        and len(context.selected_nodes)
        # And any node is active
        and context.active_node is not None):
        r = self.layout.row(align=True)
        r.operator('mesh.node_output_to_object', text=f'', icon='OBJECT_DATAMODE')
        r.operator('mesh.node_mark_selection', text=f'', icon='EDITMODE_HLT')
        r.operator('mesh.attribute_edit_on_nodes', text=f'', icon='OUTLINER_DATA_MESH')


class NODE_PT_MAME_panel_attributes(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "MAME"
    bl_label = "Attributes"

    def draw(self, context):
        self.layout.operator_context = "INVOKE_DEFAULT"

        layout = self.layout
        layout.separator()

        # That node does have some geometry outputs
        if len(func.node_func.get_geometry_node_geometry_output_pins(context.active_node)):
            self.layout.operator('mesh.attribute_edit_on_nodes', text=f'Edit attributes on output')


class NODE_PT_MAME_panel_node_info(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "MAME"
    bl_label = "Node"

    def draw(self, context):
        self.layout.operator_context = "INVOKE_DEFAULT"

        layout = self.layout
        layout.separator()

        if context.active_node:
            nodelabel = context.active_node.label if context.active_node.label != '' else context.active_node.bl_label
            self.layout.label(text='Name')
            self.layout.label(text=f'{nodelabel}', icon='NODE')
        else:
            self.layout.label(text='No node', icon='ERROR')
