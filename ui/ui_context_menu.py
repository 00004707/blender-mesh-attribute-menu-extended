"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

UI Interface Definition in context menus

"""

import func.util_func
import func.node_func
from modules import LEGACY_etc, LEGACY_static_data


def attribute_context_menu_extension(self, context):
    """
    Extra entries in ^ menu
    """

    self.layout.operator_context = "INVOKE_DEFAULT"
    if LEGACY_etc.preferences.get_preferences_attrib('add_set_attribute') and bpy.app.version >= (3,5,0):
        self.layout.operator('mesh.attribute_set')
    self.layout.operator('mesh.attribute_create_from_data', icon='MESH_DATA')
    self.layout.operator('mesh.attribute_convert_to_mesh_data', icon='MESH_ICOSPHERE')
    self.layout.operator('mesh.attribute_duplicate', icon='DUPLICATE')
    self.layout.operator('mesh.attribute_invert', icon='UV_ISLANDSEL')
    self.layout.operator('mesh.attribute_copy', icon='COPYDOWN')
    self.layout.operator('mesh.attribute_resolve_name_collisions', icon='SYNTAX_OFF')
    self.layout.operator('mesh.attribute_conditioned_select', icon='CHECKBOX_HLT')
    self.layout.operator('mesh.attribute_built_in_create', icon='ADD')
    self.layout.operator('mesh.attribute_randomize_value', icon='SHADERFX')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE')
    self.layout.operator('mesh.attribute_to_image', icon="TEXTURE")
    self.layout.operator('mesh.attribute_export', icon='FILE_NEW')
    self.layout.operator('mesh.attribute_import', icon='FILEBROWSER')


class MameCustomAttributeContextMenu(bpy.types.Menu):
    """
    Context menu for panels that do not allow extending built-in context menus
    """

    bl_idname = "OBJECT_MT_mame_custom_attribute_context_menu"
    bl_label = "Attribute Context Menu"

    draw = attribute_context_menu_extension


def vertex_groups_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > Vertex Groups
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_vg'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_vertex_group', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_all_vertex_groups', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_vertex_group_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_vertex_group_assignment', icon='MESH_DATA')


def shape_keys_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > Shape Keys
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_sk'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_shape_key', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_offset_from_shape_key', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_all_shape_keys', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_offset_from_all_shape_keys', icon='MESH_DATA')


def material_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Material > Material
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_materials'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_material_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_material_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_material_slot_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_material_slot_assignment', icon='MESH_DATA')


def uvmaps_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > UVMaps
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_uvmaps') and func.util_func.get_blender_support(minver_unsupported=(3,5,0)):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator('mesh.attribute_quick_from_uvmap', icon='MESH_DATA')


def facemaps_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > Face Maps
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_fm') and func.util_func.get_blender_support(minver_unsupported=(4,0,0)):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator('mesh.attribute_quick_from_face_map', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_face_map_index', icon='MESH_DATA')


def color_attributes_menu_extension(self, context):
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_color_attributes'):
        self.layout.separator()
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator('mesh.color_attribute_quick_bake', icon='OUTPUT')


def geometry_nodes_node_context_menu_extension(self, context):
    self.layout.operator_context = "INVOKE_DEFAULT"

    layout = self.layout
    layout.separator()

    # That node does have some geometry outputs
    if len(func.node_func.get_geometry_node_geometry_output_pins(context.active_node)):
        nodelabel = context.active_node.label if context.active_node.label != '' else context.active_node.bl_label
        self.layout.operator('mesh.attribute_edit_on_nodes', text=f'Edit attributes on {nodelabel}\'s output', icon='EDITMODE_HLT')
        self.layout.operator('mesh.node_output_to_object', text=f'\"{nodelabel}\" node output to a new object', icon='OBJECT_DATAMODE')
    if len(func.node_func.get_geometry_node_boolean_inputs(context.active_node)):
        self.layout.operator('mesh.node_mark_selection', text=f'Mark selection in edit mode', icon='TRACKER')


def node_context_menu_extension(self, context):
    if (# If node editor is geometry nodes
        func.node_func.get_node_editor_type(space_data=context.space_data) == 'GeometryNodeTree'
        # And any node is selected
        and len(context.selected_nodes)
        # And any node is active
        and context.active_node is not None):
        # Show menu
        geometry_nodes_node_context_menu_extension(self, context)


def nodes_geometry_select_menu_extension(self, context):
    r= self.layout.column()
    r.label(text="ASDFASDddddd")
    r.label(text="ASDFASD")
    r.label(text="ASDFASD")


class VIEW3D_MT_edit_mesh_vertices_attribute_from_data(bpy.types.Menu):
    bl_label = "New Attribute from..."

    def draw(self, _context):
        layout = self.layout
        for edt in [edt for edt in func.enum_func.get_source_data_enum(self, bpy.context) if 'POINT' in LEGACY_static_data.object_data_sources[edt[0]].domains_supported]:
            row = layout.row()
            row.operator_context = LEGACY_static_data.object_data_sources[edt[0]].quick_ui_exec_type
            op = self.layout.operator('mesh.attribute_create_from_data',
                                      icon = func.enum_func.get_mesh_data_enum_entry_icon(LEGACY_static_data.object_data_sources[edt[0]]),
                                      text=edt[1])
            op.attrib_name = ''
            op.domain_data_type_enum = edt[0]
            op.target_attrib_domain_enum = 'POINT'
            op.b_batch_convert_enabled
            op.b_offset_from_offset_to_toggle
            op.b_overwrite
            op.b_enable_name_formatting
            op.b_auto_convert = False


def vertex_context_menu_extension(self,context):
    """
    Entries in Vertex context menu in edit mode
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_vertex_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.menu("VIEW3D_MT_edit_mesh_vertices_attribute_from_data")


class VIEW3D_MT_edit_mesh_edges_attribute_from_data(bpy.types.Menu):
    bl_label = "New Attribute from..."

    def draw(self, _context):
        layout = self.layout
        for edt in [edt for edt in func.enum_func.get_source_data_enum(self, bpy.context) if 'EDGE' in LEGACY_static_data.object_data_sources[edt[0]].domains_supported]:
            row = layout.row()
            row.operator_context = LEGACY_static_data.object_data_sources[edt[0]].quick_ui_exec_type
            op = self.layout.operator('mesh.attribute_create_from_data',
                                      icon = func.enum_func.get_mesh_data_enum_entry_icon(LEGACY_static_data.object_data_sources[edt[0]]),
                                      text=edt[1])
            op.attrib_name = ''
            op.domain_data_type_enum = edt[0]
            op.target_attrib_domain_enum = 'EDGE'
            op.b_batch_convert_enabled
            op.b_offset_from_offset_to_toggle
            op.b_overwrite
            op.b_enable_name_formatting
            op.b_auto_convert = False


def edge_context_menu_extension(self,context):
    """
    Entries in Edge context menu in edit mode
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_edge_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.menu("VIEW3D_MT_edit_mesh_edges_attribute_from_data")


class VIEW3D_MT_edit_mesh_faces_attribute_from_data(bpy.types.Menu):
    bl_label = "New Attribute from..."

    def draw(self, _context):
        layout = self.layout

        for edt in [edt for edt in func.enum_func.get_source_data_enum(self, bpy.context) if 'FACE' in LEGACY_static_data.object_data_sources[edt[0]].domains_supported]:
            row = layout.row()
            row.operator_context = LEGACY_static_data.object_data_sources[edt[0]].quick_ui_exec_type
            op = row.operator('mesh.attribute_create_from_data',
                                      icon = func.enum_func.get_mesh_data_enum_entry_icon(LEGACY_static_data.object_data_sources[edt[0]]),
                                      text=edt[1])
            op.attrib_name = ''
            op.domain_data_type_enum = edt[0]
            op.target_attrib_domain_enum = 'FACE'
            op.b_batch_convert_enabled
            op.b_offset_from_offset_to_toggle
            op.b_overwrite
            op.b_enable_name_formatting
            op.b_auto_convert = False


def face_context_menu_extension(self,context):
    """
    Entries in Face context menu in edit mode
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_face_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.menu("VIEW3D_MT_edit_mesh_faces_attribute_from_data")


def object_context_menu_extension(self,context):
    """
    Entries in Object context menu in object mode
    UNUSED
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_object'):
        self.layout.operator_context = "INVOKE_DEFAULT"


def sculpt_mode_mask_menu_extension(self, context):
    """
    Extra entries in sculpt mode mask menu on the menu bar
    """

    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_current_sculpt_mask', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_sculpt_mask_from_active_attribute', icon='MOD_MASK')
        self.layout.operator('mesh.selected_in_edit_mode_to_sculpt_mode_mask')


def sculpt_mode_face_sets_menu_extension(self, context):
    """
    Extra entries in sculpt mode face sets menu on the menu bar
    """
    if LEGACY_etc.preferences.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_face_sets', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_face_sets_from_attribute', icon='FACE_MAPS')