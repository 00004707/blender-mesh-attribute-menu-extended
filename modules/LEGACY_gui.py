"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Everything related to user interface.

"""
 
import bpy
import etc.preferences
import func.node_func
from modules.ui.ui_common import WM_OT_mame_confirm_box
from modules.ui.ui_common import GenericMessageBox
from modules.ui.ui_common import get_attribute_value_input_ui
from modules.ui.ui_common import ATTRIBUTE_UL_attribute_multiselect_list
from modules.ui.ui_context_menu import attribute_context_menu_extension
from modules.ui.ui_context_menu import MameCustomAttributeContextMenu
from modules.ui.ui_context_menu import vertex_groups_context_menu_extension
from modules.ui.ui_context_menu import shape_keys_context_menu_extension
from modules.ui.ui_context_menu import material_context_menu_extension
from modules.ui.ui_context_menu import uvmaps_context_menu_extension
from modules.ui.ui_context_menu import facemaps_context_menu_extension
from modules.ui.ui_context_menu import color_attributes_menu_extension
from modules.ui.ui_context_menu import node_context_menu_extension
from modules.ui.ui_context_menu import nodes_geometry_select_menu_extension
from modules.ui.ui_context_menu import VIEW3D_MT_edit_mesh_vertices_attribute_from_data
from modules.ui.ui_context_menu import vertex_context_menu_extension
from modules.ui.ui_context_menu import VIEW3D_MT_edit_mesh_edges_attribute_from_data
from modules.ui.ui_context_menu import edge_context_menu_extension
from modules.ui.ui_context_menu import VIEW3D_MT_edit_mesh_faces_attribute_from_data
from modules.ui.ui_context_menu import face_context_menu_extension
from modules.ui.ui_context_menu import object_context_menu_extension
from modules.ui.ui_context_menu import sculpt_mode_mask_menu_extension
from modules.ui.ui_context_menu import sculpt_mode_face_sets_menu_extension
from ui.ui_common import create_submenu
from ui.ui_nodeeditor import NODE_PT_MAME_panel_attributes
from ui.ui_nodeeditor import NODE_PT_MAME_panel_node_info
from . import func
from . import LEGACY_static_data
from . import LEGACY_etc
from . import debug
from ..ops.util import util_ops_ui


dynamic_spawned_class_idnames = []

def unregister_dynamic_spawned_ui_classes():
    """
    Removes all dynamically spawned UI objects, eg. submenus windows or other hacky things
    """

    global dynamic_spawned_class_idnames

    for id in dynamic_spawned_class_idnames:
        if hasattr(bpy.types, id):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, id))
            except Exception as exc:
                LEGACY_etc.log(unregister_dynamic_spawned_ui_classes, f"Cannot unregister {id}: {str(exc)}")
                continue

    dynamic_spawned_class_idnames = []

# Operator subelements
# -----------------------------------------



       
# Register
# ------------------------------------------
    
classes = [
    GenericMessageBox,
    ATTRIBUTE_UL_attribute_multiselect_list,
    MasksManagerPanel,
    SculptMode3DViewHeaderSettings,
    VIEW3D_MT_edit_mesh_vertices_attribute_from_data,
    VIEW3D_MT_edit_mesh_edges_attribute_from_data,
    VIEW3D_MT_edit_mesh_faces_attribute_from_data,
    MameCustomAttributeContextMenu,
    CreateFromDataMenu,
    WM_OT_mame_confirm_box,
    NODE_PT_MAME_panel_node_info,
    NODE_PT_MAME_panel_utility,
    NODE_PT_MAME_panel_attributes,
    DATA_PT_mesh_attributes_palette
]

def ui_register():
    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.append(attributes_panel_extension)
    bpy.types.MESH_MT_attribute_context_menu.append(attribute_context_menu_extension)
    bpy.types.VIEW3D_MT_mask.append(sculpt_mode_mask_menu_extension)
    bpy.types.VIEW3D_MT_face_sets.append(sculpt_mode_face_sets_menu_extension)
    bpy.types.MESH_MT_vertex_group_context_menu.append(vertex_groups_context_menu_extension)
    bpy.types.MESH_MT_shape_key_context_menu.append(shape_keys_context_menu_extension)
    bpy.types.MATERIAL_MT_context_menu.append(material_context_menu_extension)
    bpy.types.VIEW3D_MT_object.append(object_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(face_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(edge_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(vertex_context_menu_extension)
    bpy.types.DATA_PT_uv_texture.append(uvmaps_context_menu_extension)
    bpy.types.DATA_PT_pointcloud_attributes.append(attributes_panel_extension)
    bpy.types.NODE_MT_context_menu.append(node_context_menu_extension)
    bpy.types.VIEW3D_HT_header.append(nodes_geometry_select_menu_extension)
    bpy.types.NODE_HT_header.append(geometry_nodes_node_menubar_extension)

    if bpy.app.version >= (3,5,0):
        bpy.types.DATA_PT_CURVES_attributes.append(attributes_panel_extension)
    
    if bpy.app.version < (4,0,0):
        bpy.types.DATA_PT_face_maps.append(facemaps_context_menu_extension)
    
    if bpy.app.version >= (3,3,0):
        bpy.types.MESH_MT_color_attribute_context_menu.append(color_attributes_menu_extension)

def ui_unregister():
    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.remove(attributes_panel_extension)
    bpy.types.MESH_MT_attribute_context_menu.remove(attribute_context_menu_extension)
    bpy.types.VIEW3D_MT_mask.remove(sculpt_mode_mask_menu_extension)
    bpy.types.VIEW3D_MT_face_sets.remove(sculpt_mode_face_sets_menu_extension)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(vertex_groups_context_menu_extension)
    bpy.types.MESH_MT_shape_key_context_menu.remove(shape_keys_context_menu_extension)
    bpy.types.MATERIAL_MT_context_menu.remove(material_context_menu_extension)
    bpy.types.VIEW3D_MT_object.remove(object_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(face_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(edge_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(vertex_context_menu_extension)
    bpy.types.MESH_MT_attribute_context_menu.remove(attribute_context_menu_extension)
    bpy.types.DATA_PT_uv_texture.remove(uvmaps_context_menu_extension)
    bpy.types.DATA_PT_pointcloud_attributes.remove(attributes_panel_extension)
    bpy.types.NODE_MT_context_menu.remove(node_context_menu_extension)
    bpy.types.VIEW3D_HT_header.remove(nodes_geometry_select_menu_extension)
    bpy.types.NODE_HT_header.remove(geometry_nodes_node_menubar_extension)
    
    if bpy.app.version >= (3,5,0):
        bpy.types.DATA_PT_CURVES_attributes.remove(attributes_panel_extension)
    
    if bpy.app.version < (4,0,0):
        bpy.types.DATA_PT_face_maps.remove(facemaps_context_menu_extension)
    
    if bpy.app.version >= (3,3,0):
        bpy.types.MESH_MT_color_attribute_context_menu.remove(color_attributes_menu_extension)

    unregister_dynamic_spawned_ui_classes()


def register(init_module):
    "Register classes. Exception handing in init"
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except ValueError:
            bpy.utils.unregister_class(c)
            bpy.utils.register_class(c)

    ui_register()

def unregister(init_module):
    "Unregister classes. Exception handing in init"

    ui_unregister()

    for c in classes:
        bpy.utils.unregister_class(c)
