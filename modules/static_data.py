"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Data

This file stores all pre-defined static data to use in the addon

"""

import bpy
from collections import namedtuple
from . import etc
from enum import Enum
import string

# Defines all UI categories for object_data_sources
class EObjectDataSourceUICategory(Enum):
    OTHER = 0
    VISIBILITY = 1
    SCULPTING = 2
    COMMON = 3
    SHADING = 4
    SUBDIV_MODIFIER = 5
    VERTEX_GROUPS = 6
    SHAPE_KEYS = 7
    UV = 8
    EFFECTS = 9
    MISC_DATA = 10
    SELECTION = 11

# Defines object data source
ObjectDataSource = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",                                   # Friendly name shown in UI
    "enum_gui_description",                                     # Friendly item description
    "attribute_auto_name",                                      # Automatic name with formatting elements
    "attribute_domain_on_default",                              # Default domain choice for this data source
    "domains_supported",                                        # All supported domains for this data source
    "data_type",                                                # Datatype of the attribute created
    "min_blender_ver",                                          # Minimum blender version to support this mesh data
    "unsupported_from_blender_ver",                             # Minimum blender version that removed support for this data
    "batch_convert_support",                                    # Whether the converting of multiple mesh data is supported, eg. shape keys.
    "valid_data_sources",                                       # futureproofing for other object types (unused, set to 'MESH')
    "icon",                                                     # Icon in UI
    "quick_ui_exec_type",                                       # Used when operator is called and is meant to be executed instantly (no menu) INVOKE_DEFAULT or EXEC_DEFAULT
    "ui_category",                                              # Used to place the element in UI categories (EObjectDataSourceUICategory)
])





# Contains object data sources
object_data_sources = {
    # Formattable string values:
    #   face_map shape_key domain vertex_group material material_slot shape_key_to shape_key_from
    
    # ON ALL DOMAINS
    # --------------------------------------

    "INDEX": ObjectDataSource(
        enum_gui_friendly_name="Index",
        enum_gui_description="Create attribute from domain index",
        attribute_auto_name="{domain} Index",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH', 'CURVES', 'POINTCLOUD'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.COMMON,
    ),

    # ON VERTEX EDGE FACE
    # --------------------------------------

    "VISIBLE": ObjectDataSource(
        enum_gui_friendly_name="Visible in Edit Mode",
        enum_gui_description="Create boolean attribute from domain visiblity",
        attribute_auto_name="Visible {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "HIDE_OFF",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.VISIBILITY,
    ),

    "HIDDEN": ObjectDataSource(
        enum_gui_friendly_name="Hidden in Edit Mode",
        enum_gui_description="Create boolean attribute from domain visiblity",
        attribute_auto_name="Hidden {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "HIDE_OFF",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.VISIBILITY,
    ),

    "POSITION": ObjectDataSource(
        enum_gui_friendly_name="Position",
        enum_gui_description="Create vertex attribute from domain position",
        attribute_auto_name="{domain} Position",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE','SPLINE'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH', 'CURVES', 'POINTCLOUD'],
        icon= "GIZMO",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.COMMON,
    ),
    
    # ON VERTEX FACE
    # --------------------------------------

    "NORMAL": ObjectDataSource(
        enum_gui_friendly_name="Normal",
        enum_gui_description="Create attribute from domain normals",
        attribute_auto_name="{domain} Normal",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'FACE'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "NORMALS_FACE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    # QUICK BOOLEANS
    # --------------------------------------

    "SELECTED": ObjectDataSource(
        enum_gui_friendly_name="Selected in Edit Mode",
        enum_gui_description="Create boolean attribute from domain selection",
        attribute_auto_name="Selected {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE', 'CURVE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH', 'CURVES'],
        icon= "RESTRICT_SELECT_OFF",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SELECTION,
    ),

    "NOT_SELECTED": ObjectDataSource(
        enum_gui_friendly_name="Not Selected in Edit Mode",
        enum_gui_description="Create boolean attribute from domain that is not selected",
        attribute_auto_name="Not selected {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE', 'CURVE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH', 'CURVES'],
        icon= "RESTRICT_SELECT_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SELECTION,
    ),
    
    # VERTEX ONLY
    # --------------------------------------

    "SCULPT_MODE_MASK": ObjectDataSource(
        enum_gui_friendly_name="Sculpt mode mask",
        enum_gui_description="Create float vertex attribute from masked vertices in sculpt mode",
        attribute_auto_name="Masked Vertices",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "MOD_MASK",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SCULPTING,
    ),

    "VERT_MEAN_BEVEL": ObjectDataSource(
        enum_gui_friendly_name="Vertex Mean Bevel Weight",
        enum_gui_description="Create float vertex attribute from Mean Bevel Weight",
        attribute_auto_name="Vertex Mean Bevel",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "MOD_BEVEL",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SUBDIV_MODIFIER,
    ),

    "VERT_MEAN_CREASE": ObjectDataSource(
        enum_gui_friendly_name="Mean Vertex Crease",
        enum_gui_description="Create float vertex attribute from Mean Vertex Crease",
        attribute_auto_name="Vertex Mean Crease",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINCURVE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SUBDIV_MODIFIER,
    ),

    "VERT_FROM_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="Vertex Group Weight",
        enum_gui_description="Create float vertex attribute from vertex group values",
        attribute_auto_name="{vertex_group} Vertex Weight",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "GROUP_VERTEX",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.VERTEX_GROUPS,
    ),

    "VERT_IS_IN_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="Is In Vertex Group",
        enum_gui_description="Create boolean vertex attribute from vertex group assignment",
        attribute_auto_name="Vertex in {vertex_group}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "GROUP_VERTEX",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.VERTEX_GROUPS,
    ),

    "VERT_SHAPE_KEY_POSITION": ObjectDataSource(
        enum_gui_friendly_name="Position from Shape Key",
        enum_gui_description="Create float vector attribute from shape key vertex position",
        attribute_auto_name="Position from {shape_key}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "SHAPEKEY_DATA",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHAPE_KEYS,
    ),

    "VERT_SHAPE_KEY_POSITION_OFFSET": ObjectDataSource(
        enum_gui_friendly_name="Position Offset from Shape Key",
        enum_gui_description="Create float vector attribute from shape key vertex position offset from other shape key",
        attribute_auto_name="Position Offset from {shape_key} to {shape_key_to}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "SHAPEKEY_DATA",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHAPE_KEYS,
    ),

    # EDGE ONLY
    # --------------------------------------

    "EDGE_SEAM": ObjectDataSource(
        enum_gui_friendly_name="Edge Seam",
        enum_gui_description="Create boolean edge attribute from seams",
        attribute_auto_name="Edge Seam",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "OUTLINER_DATA_EMPTY",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.UV,
    ),

    "EDGE_BEVEL_WEIGHT": ObjectDataSource(
        enum_gui_friendly_name="Edge Bevel Weight",
        enum_gui_description="Create float edge attribute from Bevel Weight",
        attribute_auto_name="Edge Bevel Weight",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "MOD_BEVEL",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SUBDIV_MODIFIER,
    ),

    "EDGE_CREASE": ObjectDataSource(
        enum_gui_friendly_name="Edge Crease",
        enum_gui_description="Create float edge attribute from Crease",
        attribute_auto_name="Edge Crease",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINCURVE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SUBDIV_MODIFIER,
    ),

    "EDGE_SHARP": ObjectDataSource(
        enum_gui_friendly_name="Edge Sharp",
        enum_gui_description="Create boolean edge attribute from Edge Sharp",
        attribute_auto_name="Edge Sharp",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "SHARPCURVE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SUBDIV_MODIFIER,
    ),

    "EDGE_FREESTYLE_MARK": ObjectDataSource(
        enum_gui_friendly_name="Edge Freestyle Mark",
        enum_gui_description="Create boolean edge attribute from Freestyle Mark",
        attribute_auto_name="Edge Freestyle Mark",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "OUTLINER_OB_EMPTY",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.EFFECTS,
    ),

    "EDGE_IS_LOOSE": ObjectDataSource(
        enum_gui_friendly_name="Loose Edges",
        enum_gui_description="Create boolean edge attribute on loose edges",
        attribute_auto_name="Loose Edges",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "MOD_EDGESPLIT",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "EDGE_VERTICES": ObjectDataSource(
        enum_gui_friendly_name="Edge Vertices",
        enum_gui_description="Create 2D vector edge attribute with indexes of edge vertices",
        attribute_auto_name="Edge Vertex Indexes",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='FLOAT2',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "VERTEXSEL",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    # FACE ONLY
    # --------------------------------------

    "SCULPT_MODE_FACE_SETS": ObjectDataSource(
        enum_gui_friendly_name="Sculpt Mode Face Set Index",
        enum_gui_description="Create float face attribute from face sets in sculpt mode",
        attribute_auto_name="Sculpt Mode Face Set Index",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "FACE_MAPS",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SCULPTING,
    ),

    "FACE_USE_SMOOTH": ObjectDataSource(
        enum_gui_friendly_name="Face Use Smooth",
        enum_gui_description="Create boolean face attribute from smooth shading of a face",
        attribute_auto_name="Is Face Smooth Shaded",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "SMOOTHCURVE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    "FACE_AREA": ObjectDataSource(
        enum_gui_friendly_name="Face Area",
        enum_gui_description="Create float face attribute from area of each face",
        attribute_auto_name="Face Area",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "SNAP_FACE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_MATERIAL_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Material Index",
        enum_gui_description="Create integer face attribute from material index",
        attribute_auto_name="Face Material Index",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "MATERIAL",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    # "FACE_MATERIAL_SLOT_INDEX": ObjectDataSource(
    #     enum_gui_friendly_name="Material Slot Index",
    #   enum_gui_description="Create integer face attribute from material slot index",
    #     attribute_auto_name="Face Material Slot Index",
    #     attribute_domain_on_default='FACE',
    #     domains_supported=['FACE'],
    #     data_type='INT',
    #     min_blender_ver=None,
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['MESH'],
    #     icon= ""
    # ),

    "FACE_VERTS": ObjectDataSource(
        enum_gui_friendly_name="All Vertex Indexes in a Face",
        enum_gui_description="Create color (4D Vector) face attribute from indexes of vertices of a face",
        attribute_auto_name="Face Vertex Indexes",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='FLOAT_COLOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_CORNER_INDEXES": ObjectDataSource(
        enum_gui_friendly_name="All Corner Indexes of a Face",
        enum_gui_description="Create color (4D Vector) face attribute from indexes of face corners of a face",
        attribute_auto_name="Corner Indexes of a Face",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='FLOAT_COLOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_CORNER_TOTAL": ObjectDataSource(
        enum_gui_friendly_name="Corner Count in a Face",
        enum_gui_description="Create integer face attribute from count of face corners in a face",
        attribute_auto_name="Corners Count in a Face",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_CORNER_START_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Corner Start Index in a Face",
        enum_gui_description="Create integer face attribute from lowest index from face corners in a face",
        attribute_auto_name="Corner Start Index in a Face",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_FROM_FACE_MAP": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Face Map",
        enum_gui_description="Create boolean face attribute from face map assignment",
        attribute_auto_name="Is face in {face_map}",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=(4,0),
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "FACE_MAPS",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_MAP_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Map Index",
        enum_gui_description="Create boolean face attribute from face map assignment",
        attribute_auto_name="Assigned Face Map Index",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=(4,0),
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "FACE_IS_MATERIAL_ASSIGNED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Material Assignment",
        enum_gui_description="Create boolean face attribute from material assignment",
        attribute_auto_name="Is {material} assigned",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "MATERIAL",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    "FACE_IS_MATERIAL_SLOT_ASSIGNED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Material Slot Assignment",
        enum_gui_description="Create boolean face attribute from material slot assignment",
        attribute_auto_name="Is {material_slot} slot assigned",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "MATERIAL",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    # FACE CORNER ONLY
    # --------------------------------------
    
    "SPLIT_NORMALS": ObjectDataSource(
        enum_gui_friendly_name="Split Normals",
        enum_gui_description="Create vector face corner attribute from split normals",
        attribute_auto_name="Split Normals",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "MOD_NORMALEDIT",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    "CORNER_TANGENT": ObjectDataSource(
        enum_gui_friendly_name="Tangent",
        enum_gui_description="Create vector face corner attribute from tangent",
        attribute_auto_name="Tangent",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "DRIVER_ROTATIONAL_DIFFERENCE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    "CORNER_BITANGENT": ObjectDataSource(
        enum_gui_friendly_name="Bitangent",
        enum_gui_description="Create vector face corner attribute from bitangent",
        attribute_auto_name="Bitangent",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "DRIVER_ROTATIONAL_DIFFERENCE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    "CORNER_BITANGENT_SIGN": ObjectDataSource(
        enum_gui_friendly_name="Bitangent Sign",
        enum_gui_description="Create float face corner attribute from corner bitangent sign",
        attribute_auto_name="Bitangent Sign",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "DRIVER_ROTATIONAL_DIFFERENCE",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.SHADING,
    ),

    "CORNER_EDGE_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Corner Edge Index",
        enum_gui_description="Create integer face corner attribute from assigned edge index",
        attribute_auto_name="Face Corner Edge Index",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "CORNER_VERTEX_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Corner Vertex Index",
        enum_gui_description="Create integer face corner attribute from assigned vertex index",
        attribute_auto_name="Face Corner Vertex Index",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT',
        ui_category = EObjectDataSourceUICategory.MISC_DATA,
    ),

    "UVMAP": ObjectDataSource(
        enum_gui_friendly_name="UVMap",
        enum_gui_description="Create Vector2D UVMap attribute from selected UVMap",
        attribute_auto_name="UVMap",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT2',
        min_blender_ver=None,
        unsupported_from_blender_ver=(3,5),
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "UV",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.UV,
    ),

    

    # # SPECIAL
    # # UV
    # --------------------------------------

    "SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataSource(
        enum_gui_friendly_name="UV Editor Selected Vertices",
        enum_gui_description="Create Selected Vertices attribute from selected UVMap",
        attribute_auto_name="UVMap Selected Vertices",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='BOOLEAN',
        min_blender_ver=(3,5,0),
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "UV",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.UV,
    ),


    "SELECTED_EDGES_IN_UV_EDITOR": ObjectDataSource(
        enum_gui_friendly_name="UV Editor Selected Edges",
        enum_gui_description="Create Selected Edges attribute from selected UVMap",
        attribute_auto_name="UVMap Selected Edges",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='BOOLEAN',
        min_blender_ver=(3,5,0),
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "UV",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.UV,
    ),

    "PINNED_VERTICES_IN_UV_EDITOR": ObjectDataSource(
        enum_gui_friendly_name="UV Editor Pinned Vertices",
        enum_gui_description="Create Pinned Vertices attribute from selected UVMap",
        attribute_auto_name="UVMap Pinned Vertices",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='BOOLEAN',
        min_blender_ver=(3,5,0),
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "UV",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.UV,
    ),

}

# Defines an object data target
ObjectDataTarget = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",
    "enum_gui_friendly_name_no_special_characters",
    "enum_gui_description",
    "domains_supported",
    "data_type",
    "min_blender_ver",
    "unsupported_from_blender_ver",
    "icon",
    "batch_convert_support"
])

# Contains object data sources
object_data_targets = {
    # Special Entries
    #   "INSERT_SEPARATOR_": None,         will add a separator in enum menu
    #   "INSERT_NEWLINE_": None,           will add a new column in enum menu
    #
    # Formattable string values:
    #   NONE, FORMAT DOES NOT PLAY NICE WITH ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ STRINGS and spills out garbage

    #POINT EDGE FACE
    # --------------------------------------
    "TO_VISIBLE": ObjectDataTarget(
            enum_gui_friendly_name="To Visible In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Visible In Edit Mode",
            enum_gui_description="Convert this attribute to visible in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="HIDE_OFF",
            batch_convert_support=False
        ),

    "TO_HIDDEN": ObjectDataTarget(
            enum_gui_friendly_name="To Hidden In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Hidden In Edit Mode",
            enum_gui_description="Convert this attribute to hidden in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="HIDE_ON",
            batch_convert_support=False
        ),

    "TO_SELECTED": ObjectDataTarget(
            enum_gui_friendly_name="To Selected In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Selected In Edit Mode",
            enum_gui_description="Convert this attribute to selected in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="RESTRICT_SELECT_OFF",
            batch_convert_support=False
        ),

    "TO_NOT_SELECTED": ObjectDataTarget(
            enum_gui_friendly_name="To Not Selected In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Not Selected In Edit Mode",
            enum_gui_description="Convert this attribute to selected in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="RESTRICT_SELECT_ON",
            batch_convert_support=False
        ),

    # # VERTEX EDGE
    # --------------------------------------
    "INSERT_SEPARATOR_VE": None,  

    "TO_MEAN_BEVEL_WEIGHT": ObjectDataTarget(
            enum_gui_friendly_name="To Bevel Weight ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ",
            enum_gui_friendly_name_no_special_characters="To Mean Bevel Weight",
            enum_gui_description="Convert this attribute to bevel weight",
            
            domains_supported=['POINT', 'EDGE'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MOD_BEVEL",
            batch_convert_support=False
        ),

    "TO_MEAN_CREASE": ObjectDataTarget(
            enum_gui_friendly_name="To Mean Crease ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ",
            enum_gui_friendly_name_no_special_characters="To Mean Crease",
            enum_gui_description="Convert this attribute to mean crease",
            
            domains_supported=['POINT', 'EDGE'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="LINCURVE",
            batch_convert_support=False
        ),

    # VERTEX CORNER
    # --------------------------------------
    "INSERT_SEPARATOR_VC": None,  

    'TO_SPLIT_NORMALS': ObjectDataTarget(
            enum_gui_friendly_name="To Split Normals ⁻ ᵛᵉʳᵗᵉˣ ᶜᵒʳⁿᵉʳ",
            enum_gui_friendly_name_no_special_characters="To Split Normals",
            enum_gui_description="Convert this attribute to split normals",
            
            domains_supported=['POINT', 'CORNER'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MOD_NORMALEDIT",
            batch_convert_support=False
        ),

    # VERTEX
    # --------------------------------------
    "INSERT_NEWLINE_V": None, 

    "TO_POSITION": ObjectDataTarget(
            enum_gui_friendly_name="To Position ⁻ ᵛᵉʳᵗᵉˣ",
            enum_gui_friendly_name_no_special_characters="To Position",
            enum_gui_description="Convert this attribute to mesh positon",
            
            domains_supported=['POINT'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="GIZMO",
            batch_convert_support=False
        ),

    "TO_SCULPT_MODE_MASK": ObjectDataTarget(
            enum_gui_friendly_name="To Sculpt Mode Mask ⁻ ᵛᵉʳᵗᵉˣ",
            enum_gui_friendly_name_no_special_characters="To Sculpt Mode Mask",
            enum_gui_description="Convert this attribute to sculpt mode mask",
            
            domains_supported=['POINT'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MOD_MASK",
            batch_convert_support=False
        ),

    "TO_VERTEX_GROUP": ObjectDataTarget(
            enum_gui_friendly_name="To Vertex Group  ⁻ ᵛᵉʳᵗᵉˣ",
            enum_gui_friendly_name_no_special_characters="To Vertex Group",
            enum_gui_description="Convert this attribute to vertex group",
            
            domains_supported=['POINT'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="GROUP_VERTEX",
            batch_convert_support=True
        ),
        
    "TO_SHAPE_KEY": ObjectDataTarget(
            enum_gui_friendly_name="To Shape Key ⁻ ᵛᵉʳᵗᵉˣ",
            enum_gui_friendly_name_no_special_characters="To Shape Key",
            enum_gui_description="Convert this attribute to mesh shape key",
            
            domains_supported=['POINT'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="SHAPEKEY_DATA",
            batch_convert_support=True
        ),

    "TO_VERTEX_GROUP_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="To Vertex Group Index ⁻ ᵛᵉʳᵗᵉˣ",
            enum_gui_friendly_name_no_special_characters="To Vertex Group Index",
            enum_gui_description="Convert this attribute to vertex group index for use with armatures",
            domains_supported=['POINT'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="GROUP_VERTEX",
            batch_convert_support=False
        ),

    # EDGE
    # --------------------------------------
    "INSERT_SEPARATOR_E": None, 

    "TO_SEAM": ObjectDataTarget(
            enum_gui_friendly_name="To Seams ⁻ ᵉᵈᵍᵉ",
            enum_gui_friendly_name_no_special_characters="To Seams",
            enum_gui_description="Convert this attribute to edge seams",
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="EMPTY_DATA",
            batch_convert_support=False
        ),

    "TO_SHARP": ObjectDataTarget(
            enum_gui_friendly_name="To Sharp ⁻ ᵉᵈᵍᵉ",
            enum_gui_friendly_name_no_special_characters="To Sharp",
            enum_gui_description="Convert this attribute to edge sharps",         
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="SHARPCURVE",
            batch_convert_support=False
        ),

    "TO_FREESTYLE_MARK": ObjectDataTarget(
            enum_gui_friendly_name="To Freestyle Mark ⁻ ᵉᵈᵍᵉ",
            enum_gui_friendly_name_no_special_characters="To Freestyle Mark",
            enum_gui_description="Convert this attribute to edge freestyle mark",
            
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="OUTLINER_OB_EMPTY",
            batch_convert_support=False
        ),

    # FACE
    # --------------------------------------
    "INSERT_NEWLINE_F": None, 

    "TO_FACE_SHADE_SMOOTH": ObjectDataTarget(
            enum_gui_friendly_name="To Face Shade Smooth ⁻ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Face Shade Smooth",
            enum_gui_description="Convert this attribute to face shade smooth",
            
            domains_supported=['FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="SMOOTHCURVE",
            batch_convert_support=False
        ),

    "TO_FACE_MAP": ObjectDataTarget(
            enum_gui_friendly_name="To Face Map ⁻ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Face Map",
            enum_gui_description="Convert this attribute to face map",
            
            domains_supported=['FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=(4,0),
            icon="FACE_MAPS",
            batch_convert_support=True
        ),

    "TO_SCULPT_MODE_FACE_SETS": ObjectDataTarget(
            enum_gui_friendly_name="To Sculpt Mode Face Sets ⁻ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Sculpt Mode Face Sets",
            enum_gui_description="Convert this attribute to Sculpt Mode Face Sets",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="UV_FACESEL",
            batch_convert_support=False
        ),

    "TO_MATERIAL_SLOT_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="To Material Slot Index ⁻ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="To Material Slot Index",
            enum_gui_description="Convert this attribute to Material Slot Index",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MATERIAL",
            batch_convert_support=False
        ),

    "TO_FACE_MAP_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="Set Face Map Index ⁻ ᶠᵃᶜᵉ",
            enum_gui_friendly_name_no_special_characters="Set Face Map Index",
            enum_gui_description="Convert this attribute to set face map index",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=(4,0),
            icon="FACE_MAPS",
            batch_convert_support=False
        ),  

    # CORNER
    # --------------------------------------
    "INSERT_SEPARATOR_FC": None, 

    "TO_UVMAP": ObjectDataTarget(
            enum_gui_friendly_name="To UVMap ⁻ ᶜᵒʳⁿᵉʳ",
            enum_gui_friendly_name_no_special_characters="To UVMap",
            enum_gui_description="Convert this attribute to UVMap",
            
            domains_supported=['CORNER'],
            data_type='FLOAT2',
            min_blender_ver=None,
            unsupported_from_blender_ver=(3,5),
            icon="UV",
            batch_convert_support=True
        ),  

    # # SPECIAL
    # --------------------------------------
    "INSERT_SEPARATOR_SPECIAL": None, 

    "TO_SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataTarget(
            enum_gui_friendly_name="Selected UV Editor Vertices ⁻ ᵘᵛ",
            enum_gui_friendly_name_no_special_characters="Selected UV Vertices (UV Editor)",
            enum_gui_description="Convert this attribute to selected vertices in UV Editor Panel",
            domains_supported=['CORNER'],
            data_type='BOOLEAN',
            min_blender_ver=(3,5,0),
            unsupported_from_blender_ver=None,
            icon="UV",
            batch_convert_support=False
        ),    
    
    "TO_SELECTED_EDGES_IN_UV_EDITOR": ObjectDataTarget(
            enum_gui_friendly_name="Selected UV Editor  Edges ⁻ ᵘᵛ",
            enum_gui_friendly_name_no_special_characters="Selected UV Edges (UV Editor)",
            enum_gui_description="Convert this attribute to selected edges in UV Editor Panel",
            domains_supported=['CORNER'],
            data_type='BOOLEAN',
            min_blender_ver=(3,5,0),
            unsupported_from_blender_ver=None,
            icon="UV",
            batch_convert_support=False
        ),    

    "TO_PINNED_VERTICES_IN_UV_EDITOR": ObjectDataTarget(
            enum_gui_friendly_name="Pinned UV Editor Vertices ⁻ ᵘᵛ",
            enum_gui_friendly_name_no_special_characters="Pinned UV Vertices (UV Editor)",
            enum_gui_description="Convert this attribute to pinned vertices in UV Editor Panel",
            domains_supported=['CORNER'],
            data_type='BOOLEAN',
            min_blender_ver=(3,5,0),
            unsupported_from_blender_ver=None,
            icon="UV",
            batch_convert_support=False
        ),    

}

# Defines all supported mesh data types as enum
class EAttributeDataType(Enum):
    FLOAT = 0
    INT = 1
    INT8 = 2
    FLOAT_VECTOR = 3
    FLOAT_COLOR = 4
    BYTE_COLOR = 5
    STRING = 6
    BOOLEAN = 7
    FLOAT2 = 8
    INT32_2D = 9
    QUATERNION = 10

# Defines the type of GUI input to show 
class EDataTypeGuiPropType(Enum):
    SCALAR = 0          #int float int8
    VECTOR = 1          #float vector, vector 2d, quaternion
    COLOR  = 3          # float color byte color
    STRING = 4          # string
    BOOLEAN = 5         # boolean

# Defines all supported node editors
class ENodeEditor(Enum):
    UNSUPPORTED = 0
    GEOMETRY_NODES = 1
    SHADER = 2
    ANIMATION_NODES = 3

# Defines an node editor
NodeEditor = namedtuple("NodeEditor", [
    "gui_friendly_name",
    "gui_description",
    "enum",
    "icon"
])

# Contains info about all node editors
node_editors = {
    "ShaderNodeTree": NodeEditor(
            gui_friendly_name="Shader Editor",
            gui_description="Shader Edtior",
            enum=ENodeEditor.SHADER,
            icon="MATERIAL"
        ),
    "GeometryNodeTree": NodeEditor(
            gui_friendly_name="Geometry Nodes Editor",
            gui_description="Geometry Nodes Editor",
            enum=ENodeEditor.GEOMETRY_NODES,
            icon="GEOMETRY_NODES" if etc.get_blender_support(minver=(3,3,0)) else "NODE"
        ),
    "an_AnimationNodeTree": NodeEditor(
            gui_friendly_name="Animation Nodes Editor",
            gui_description="Animation Nodes Editor",
            enum=ENodeEditor.ANIMATION_NODES,
            icon="ONIONSKIN_ON"
        ), #OUTLINER_DATA_POINTCLOUD
}

# Define mesh data type entries
AttributeDataType = namedtuple("AttributeDataType", [
    "friendly_name",                            # The name presented to the user
    "min_blender_ver",                          # Minimum blender version that this data type is supported from
    "unsupported_from_blender_ver",             # First blender version that this data type is unsupported from
    "supported_attribute_invert_modes",         # Supported invert modes, from attribute_invert_modes
    "supported_comparison_modes",               # Supported comparison modes, from attribute_comparison_modes
    "gui_prop_subtype",                         # Type of the gui to display for this attribute data type (EDataTypeGuiPropType)
    "vector_subelements_names",                 # Names of subelements in a vector value, eg X Y Z or None    
    "bpy_ops_set_attribute_param_name",         # Name of the parameter passed to bpy.ops.mesh.attribute_set to assign the value to this data type. None means it is not supported.
    "default_value",                            # The default or zero value
    "compatible_node_editors",                  # The supported node editors, ENodeEditor enum
    "geonodes_attribute_node_datatype",         # The name of the data type used in Named Attribute node in Geometry nodes. 'FLOAT', 'INT', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'BOOLEAN', 'QUATERNION'
    "animnodes_attribute_node_datatype",        # The name of the data type used in Get Custom Attribute node in Animation nodes. ('INT', 'FLOAT', 'FLOAT2', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'BYTE_COLOR', 'BOOLEAN')
    "default_randomize_value_min",              # The suggested minimum random value for this datatype
    "default_randomize_value_max",              # The suggested maximum random value for this datatype 
    "cast_type",                                # The type to cast the value to to ensure it is valid
    "large_capacity_vector",                    # Toggle to use custom UI for matrices and other values that can be stored in long vectors (Currently (4.2) no native suppport for UI elemens for matrices)
    "large_capacity_vector_size",               # Number of elements in the vector. It may not be columnx*rows from values below
    "large_capacity_vector_size_height",        # Number of columns, for a 4x3 matrix it would be 4
    "large_capacity_vector_size_width",         # Number of rows, for a 4x3 matrix it would be 3
])

# Defines all supported mesh data types
attribute_data_types = {
    "FLOAT": AttributeDataType(
        friendly_name="Float",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR,
        bpy_ops_set_attribute_param_name="value_float",
        default_value=0.0,
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT",
        animnodes_attribute_node_datatype="FLOAT",
        default_randomize_value_min=0.0,
        default_randomize_value_max=1.0,
        cast_type=float,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "INT": AttributeDataType(
        friendly_name="Integer",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR,
        bpy_ops_set_attribute_param_name="value_int",
        default_value=0,
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="INT",
        animnodes_attribute_node_datatype="INT",
        default_randomize_value_min=0,
        default_randomize_value_max=100,
        cast_type=int,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "INT8": AttributeDataType(
        friendly_name="8-bit Integer",
        min_blender_ver=(3,2,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR,
        bpy_ops_set_attribute_param_name="value_int",
        default_value=0,
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="INT",
        animnodes_attribute_node_datatype="INT",
        default_randomize_value_min=-127,
        default_randomize_value_max=128,
        cast_type=int,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "FLOAT_VECTOR": AttributeDataType(
        friendly_name="Vector",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['X','Y','Z'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR,
        bpy_ops_set_attribute_param_name="value_float_vector_3d",
        default_value=(0.0, 0.0, 0.0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT_VECTOR",
        animnodes_attribute_node_datatype="FLOAT_VECTOR",
        default_randomize_value_min=(0,0,0),
        default_randomize_value_max=(1,1,1),
        cast_type=tuple,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "FLOAT_COLOR": AttributeDataType(
        friendly_name="Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['R','G','B','A'],
        gui_prop_subtype=EDataTypeGuiPropType.COLOR,
        bpy_ops_set_attribute_param_name="value_color",
        default_value=(0.0, 0.0, 0.0, 1.0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT_COLOR",
        animnodes_attribute_node_datatype="FLOAT_COLOR",
        default_randomize_value_min=(0.0,0.0,0.0,1.0),
        default_randomize_value_max=(1.0,1.0,1.0,1.0),
        cast_type=tuple,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "BYTE_COLOR": AttributeDataType(
        friendly_name="Byte Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['R','G','B','A'],
        gui_prop_subtype=EDataTypeGuiPropType.COLOR,
        bpy_ops_set_attribute_param_name="value_color",
        default_value=(0.0, 0.0, 0.0, 1.0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT_COLOR",
        animnodes_attribute_node_datatype="BYTE_COLOR",
        default_randomize_value_min=(0.0,0.0,0.0,1.0),
        default_randomize_value_max=(1.0,1.0,1.0,1.0),
        cast_type=tuple,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "STRING": AttributeDataType(
        friendly_name="String",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["REVERSE_ORDER"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.STRING,
        bpy_ops_set_attribute_param_name=None,
        default_value="",
        compatible_node_editors=[],
        geonodes_attribute_node_datatype="",
        animnodes_attribute_node_datatype="",
        default_randomize_value_min=5, # used as length
        default_randomize_value_max=10,
        cast_type=str,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "BOOLEAN": AttributeDataType(
        friendly_name="Boolean",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["NOT"],
        supported_comparison_modes=['EQ','NEQ'],
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.BOOLEAN,
        bpy_ops_set_attribute_param_name="value_bool",
        default_value=False,
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="BOOLEAN",
        animnodes_attribute_node_datatype="BOOLEAN",
        default_randomize_value_min=False,
        default_randomize_value_max=True,
        cast_type=bool,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "FLOAT2": AttributeDataType(
        friendly_name="Vector 2D",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['X','Y'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR,
        bpy_ops_set_attribute_param_name="value_float_vector_2d",
        default_value=(0.0, 0.0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT_VECTOR",
        animnodes_attribute_node_datatype="FLOAT2",
        default_randomize_value_min=(0.0,0.0),
        default_randomize_value_max=(1.0,1.0),
        cast_type=tuple,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "INT32_2D": AttributeDataType(
        friendly_name='2D Integer Vector',
        min_blender_ver=(3,6,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['X','Y'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR,
        bpy_ops_set_attribute_param_name="value_int_vector_2d",
        default_value=(0, 0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT_VECTOR",
        animnodes_attribute_node_datatype="FLOAT2",
        default_randomize_value_min=(0,0),
        default_randomize_value_max=(100,100),
        cast_type=tuple,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "QUATERNION": AttributeDataType(
        friendly_name='Quaternion',
        min_blender_ver=(4,0,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['X','Y','Z','W'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR,
        bpy_ops_set_attribute_param_name="value_quat",
        default_value=(1.0, 0.0, 0.0, 0.0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],
        geonodes_attribute_node_datatype="QUATERNION",
        animnodes_attribute_node_datatype="",
        default_randomize_value_min=(-1.0,-1.0,-1.0,-1.0),
        default_randomize_value_max=(1.0,1.0,1.0,1.0),
        cast_type=tuple,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
    ),
    "FLOAT4X4": AttributeDataType(
        friendly_name='4x4 Matrix',
        min_blender_ver=(4,2,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["INVERSE_OF_A_MATRIX"], 
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        vector_subelements_names=['X1','Y1','Z1','W1','X2','Y2','Z2','W2','X3','Y3','Z3','W3','X4','Y4','Z4','W4'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR,
        bpy_ops_set_attribute_param_name=None,
        default_value=(1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],
        geonodes_attribute_node_datatype="FLOAT4X4",
        animnodes_attribute_node_datatype="",
        default_randomize_value_min=(-1.0,-1.0,-1.0,-1.0, -1.0,-1.0,-1.0,-1.0, -1.0,-1.0,-1.0,-1.0, -1.0,-1.0,-1.0,-1.0),
        default_randomize_value_max=(1.0,1.0,1.0,1.0, 1.0,1.0,1.0,1.0, 1.0,1.0,1.0,1.0, 1.0,1.0,1.0,1.0),
        cast_type=tuple,
        large_capacity_vector=True,
        large_capacity_vector_size=16,
        large_capacity_vector_size_height=4,
        large_capacity_vector_size_width=4,
    ),
}

# Defines mesh domain entries
AttributeDomain = namedtuple("AttributeDomain", [
    "friendly_name",
    "friendly_name_plural",
    "friendly_name_short",                      # The name presented to the user (shorter)
    "friendly_name_veryshort",                  # The name presented to the user (shorter)
    "min_blender_ver",
    "unsupported_from_blender_ver",
    "icon",
])

# Defines all mesh domains
attribute_domains = {
    "POINT": AttributeDomain(
        friendly_name="Vertex / Point",
        friendly_name_plural="Vertices / Points",
        friendly_name_short="Vertex",
        friendly_name_veryshort="V",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='VERTEXSEL'
    ),
    "EDGE": AttributeDomain(
        friendly_name="Edge",
        friendly_name_plural="Edges",
        friendly_name_short="Edge",
        friendly_name_veryshort="E",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='EDGESEL'
    ),
    "FACE": AttributeDomain(
        friendly_name="Face",
        friendly_name_plural="Faces",
        friendly_name_short="Face",
        friendly_name_veryshort="V",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='FACE_MAPS'
    ),
    "CORNER": AttributeDomain(
        friendly_name="Face Corner",
        friendly_name_plural="Face Corners",
        friendly_name_short="Corner",
        friendly_name_veryshort="C",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='FACE_CORNER'
    ),
    "CURVE": AttributeDomain(
        friendly_name="Spline",
        friendly_name_plural="Splines",
        friendly_name_short="Spline",
        friendly_name_veryshort="S",
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        icon='CURVE_DATA'
    ),
}

# Defines convert attribute modes
ConvertAttributeMode = namedtuple("ConvertAttributeMode", [
    "friendly_name",
    "min_blender_ver",
    "unsupported_from_blender_ver",
])

# Defines all convert attribute modes
convert_attribute_modes = {
    "GENERIC": ConvertAttributeMode(
        friendly_name="Generic",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "VERTEX_GROUP": ConvertAttributeMode(
        friendly_name="Vertex Group",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
}

# All attribute types. Used to limit operator scope
# Some of them might be unused for now
class EAttributeType(Enum):
    NORMAL = 0                  # For attributes created by user or other
    HIDDEN = 1                  # For attributes starting with . for a reason
    READONLY = 2                # For attributes that are read only
    INTERNAL = 3                # For attributes for internal use only eg .pn.UVMap
    AUTOGENERATED = 4           # For attributes auto generated by blender, eg sharp_face. 
    NOTPROCEDURAL = 5           # Not used for procedural context (geonodes)
    DONOTREMOVE = 6             # Attributes that should not be removed
    CANTREMOVE = 7              # Attributes that CANNOT be removed. 

# Used to describe an entry in defined_attributes
BuiltInAttribute = namedtuple("AttriubteType", [
    "friendly_name",                    # Name used in GUI
    "description",                      # Description, just in case
    "types",                            # List of EAttributeType
    "object_types",                     # Found on object types, eg MESH
    "min_blender_ver",                  # Minimum blender version that this attribute appeared
    "unsupported_from_blender_ver",     # First blender version that removed this attribute
    "domains",                          # Domains that this attribute is created on
    "data_types",                       # Data types that this attribute holds
    "friendly_value_name",              # Value name show in UI, for tilt it is "Tilt Value"
    "friendly_value_names_override",    # Overrides the UI integer input to selectable enum list eg. spline type in text not int
    "default_value",                    # Default value of the attribute to assign on creation
    "minimum_value",                    # The value used to limit user input. Can be None if there is no limit.
    "maximum_value",                    # The value used to limit user input. Can be None if there is no limit.
    "cannot_create",                    # Attributes that cannot be creates, eg. position is always present
    "extra_message",                    # Extra info shown in attribute creation UI
    "warning_message",                  # Extra message shown if attribute is active
    "procedural_context_read",          # Whether the value can be read in Geometry Nodes. Usually attributes starting with a dot cannot
    "procedural_context_write",         # Whether the value can be modified in Geometry Nodes. Usually attributes starting with a dot cannot
    "icon",                             # Icon in enum dropdown list
])  

# Stores all explicitly defined attributes that are generated by blender.
built_in_attributes = {

    "position": BuiltInAttribute(
        
        friendly_name = "Vertex / Spline Control Point Position",                    
        description = "The position of vertices in a mesh or points in a Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.CANTREMOVE, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH', 'CURVES'],                        
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ["POINT"],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Position Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = True,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'EMPTY_DATA',
    ),

    "normal": BuiltInAttribute(
        
        friendly_name = "Vertex / Spline Control Normal Vector",                    
        description = "The normal vector of vertices in a mesh or points in a Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.CANTREMOVE, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH', 'CURVES'],                        
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ["POINT"],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Normal Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = (0,0,0),
        maximum_value = (1,1,1),
        cannot_create = True,
        extra_message = "The value should be normalized",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = False,
        icon = 'NORMALS_FACE',
    ),

    "radius": BuiltInAttribute(
        
        friendly_name = "Curve or Point Cloud Radius",                    
        description = "The radius of the point cloud points or curves",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES', 'POINT_CLOUD'], # I have no idea what is the object name for this, as it seems to be removed. Left just in case.                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT'],
        friendly_value_name='Curve/Point Cloud Radius Value',
        friendly_value_names_override = [],
        default_value = 1.0,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "Spline at index 0 sets the visual radius for all other splines",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'DRIVER_DISTANCE',
    ),

    "id": BuiltInAttribute(
        
        friendly_name = "ID",                    
        description = "Unique index of a point or curve control point (auto-generated by geometry nodes)",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH, CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['INT'],
        friendly_value_name='ID Value',
        friendly_value_names_override = [],
        default_value = 0,
        minimum_value = 0,
        maximum_value = None,
        cannot_create = False,
        extra_message = "ID should be unique",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'COPY_ID',
    ),

    "spline_id": BuiltInAttribute(
        
        friendly_name = "Spline ID",                    
        description = "Unique index of a spline(auto-generated by geometry nodes)",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['INT'],
        friendly_value_name='ID Value',
        friendly_value_names_override = [],
        default_value = 0,
        minimum_value = 0,
        maximum_value = None,
        cannot_create = False,
        extra_message = "ID should be unique",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'COPY_ID',
    ),

    "material_index": BuiltInAttribute(
        
        friendly_name = "Material Index",                    
        description = "Index of applied material to a face",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['FACE'],
        data_types = ['INT'],
        friendly_value_name='Face Material Index Value',
        friendly_value_names_override = [],
        default_value = 0,
        minimum_value = 0,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'MATERIAL',
    ),

    "crease": BuiltInAttribute(
        friendly_name = "Edge Crease",                    
        description = "Edge Crease",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['EDGE'],
        data_types = ['FLOAT'],
        friendly_value_name='Edge Crease Value',
        friendly_value_names_override = [],
        default_value = 0.0,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "The value should be normalized",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'NOCURVE',
        
    ),

    "sharp_face": BuiltInAttribute(
        friendly_name = "Face Sharp",                    
        description = "Flat shading of a face, aka. disabled smooth shading",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['FACE'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Flat Shaded Face',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'SNAP_VOLUME',
    ),

    "resolution": BuiltInAttribute(
        friendly_name = "Bézier Spline/NURBS Resolution",                    
        description = "Number of subdivision points between two control points of a Bézier Spline/NURBS Spline",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVE'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['INT'],
        friendly_value_name='Spline Points Resolution Value',
        friendly_value_names_override = [],
        default_value = 8,
        minimum_value = 1,
        maximum_value = 64,
        cannot_create = False,
        extra_message = "The value should be above 0",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'IPO_QUINT',
    ),

    "cyclic": BuiltInAttribute(
        friendly_name = "Spline Cyclic",                    
        description = "\"Is the spline cyclic\" boolean",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Spline Cyclic Toggle',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'RECORD_OFF',
    ),

    "handle_left": BuiltInAttribute(
        friendly_name = "Bézier Curve Handle Left",                    
        description = "The position of left handle of a Bézier Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Bézier Curve Left Handle Position Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'TRIA_LEFT',
    ),

    "handle_right": BuiltInAttribute(
        
        friendly_name = "Bézier Curve Handle Right",                    
        description = "The position of right handle of a Bézier Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Bézier Curve Right Handle Position Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'TRIA_RIGHT',
    ),

    "handle_type_left": BuiltInAttribute(
        friendly_name = "Bézier Curve Left Handle Type",                    
        description = "The type of left handle of a Bézier Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['INT8'],
        friendly_value_name='Bézier Curve Left Handle Type',
        friendly_value_names_override = [("0", 'Free', f""),
                                         ("1", 'Automatic', f""),
                                         ("2", 'Vector', f""),
                                         ("3", 'Aligned', f"")],
        default_value = 1,
        minimum_value = 0,
        maximum_value = 3,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'TRIA_LEFT',
    ),

    "handle_type_right": BuiltInAttribute(
        
        friendly_name = "Bézier Curve Right Handle Type ",                    
        description = "The type of right handle of a Bézier Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['INT8'],
        friendly_value_name='Bézier Curve Right Handle Type',
        friendly_value_names_override = [("0", 'Free', f""),
                                         ("1", 'Automatic', f""),
                                         ("2", 'Vector', f""),
                                         ("3", 'Aligned', f"")],
        default_value = 1,
        minimum_value = 0,
        maximum_value = 3,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'TRIA_RIGHT',
    ),
    
    "velocity": BuiltInAttribute(
        friendly_name = "Velocity",                    
        description = "Velocity vector value used for motion blur",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH', 'POINT_CLOUD'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Motion Blur Velocity Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'OUTLINER_OB_FORCE_FIELD',
    ),

    "rest_position": BuiltInAttribute(
        friendly_name = "Mesh Rest Position",                    
        description = "The position of vertices or spline control points without shape keys and modifiers",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH', 'CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Rest Position Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0), # Unused, sample position from mesh instead.
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'FILE_3D',
    ),

    "surface_uv_coordinate": BuiltInAttribute(
        friendly_name = "Surface UV Coordinate",                    
        description = "Curves attachment location to a mesh",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['FLOAT2'],
        friendly_value_name='Curves Parent Mesh Surface UV Coordinate',
        friendly_value_names_override = [],
        default_value = (0,0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'MOD_UVPROJECT',
    ),
    
    ".sculpt_mask": BuiltInAttribute(

        friendly_name = "Sculpt Mask",                    
        description = "The value of mask in sculpt mode",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],  
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT'],
        friendly_value_name='Sculpt Mask Value',
        friendly_value_names_override = [],
        default_value = 0.0,
        minimum_value = 0.0,
        maximum_value = 1.0,
        cannot_create = False,
        extra_message = "The value should be normalized",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'MOD_MASK',
    ),

    "surface_normal": BuiltInAttribute(
        friendly_name = "Curves Surface Mesh Normal Vector",                    
        description = "Normal vector of the surface mesh at curve root",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Spline Parent Mesh Surface Normal Vector',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'NORMALS_FACE',
    ),

    "normal_mode": BuiltInAttribute(
        friendly_name = "Curve Normal Mode (Twist Method)",                    
        description = "The mode to calculate normals of a curve",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['INT8'],
        friendly_value_name='Curve Normal Generation Mode',
        friendly_value_names_override = [("0", 'Minimum Twist', f"Calculate normals with the smallest twist around the curve tangent across the whole curve."),
                                         ("1", 'Z Up', f"Calculate normals perpendicular to the Z axis and the curve tangent. If a series of points is vertical, the X axis is used."),
                                         ("2", 'Free', f"Use the stored custom normal attribute as the final normals.")],
        default_value = 0,
        minimum_value = 0,
        maximum_value = 2,
        cannot_create = False,
        extra_message = "The value should be 0, 1 or 2",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'IPO_EASE_IN_OUT',
    ),

    "knots_mode": BuiltInAttribute(
        friendly_name = "NURBS Spline Knot Vector Adjustments",                    
        description = "Built-in adjustments to control Knot Vector of a NURBS spline",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['INT8'],
        friendly_value_name='NURBS Curve Knot Vector Mode',
        friendly_value_names_override = [("0", 'No Bézier U, No Endpoint U', f"Act like a poly curve"),
                                         ("1", 'Endpoint U', f"Make this NURBS curve or surface meet the endpoints in U direction"),
                                         ("2", 'Bézier U', f"Make this NURBS curve or surface act like a Bézier curve in U direction"),
                                         ("3", 'Bézier U, Endpoint U', f"Make this NURBS curve or surface act like a Bézier curve and meet the endpoints in U direction")],
        default_value = 0,
        minimum_value = 0,
        maximum_value = 3,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'IPO_EASE_IN_OUT',
    ),

    "nurbs_order": BuiltInAttribute(
        
        friendly_name = "NURBS Order in U Direction",                    
        description = "Higher values make a NURBS curve point influence a greater area at a cost of performance",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['INT8'],
        friendly_value_name='NURBS Order',
        friendly_value_names_override = [],
        default_value = 2,
        minimum_value = 2,
        maximum_value = 6,
        cannot_create = False,
        extra_message = "Value should be in 2 to 6 range",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'IPO_EASE_IN_OUT',
    ),

    "curve_type": BuiltInAttribute(
        
        friendly_name = "Curve Type",                    
        description = "Type of the curve: Poly, Bezier or NURBS",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CURVE'],
        data_types = ['INT8'],
        friendly_value_name='Curve Type',
        friendly_value_names_override = [("0", 'Catmull Rom', f""),
                                         ("1", 'Poly', f""),
                                         ("2", 'Bézier', f""),
                                         ("3", 'NURBS', f"")],
        default_value = 0,
        minimum_value = 0,
        maximum_value = 3,
        cannot_create = False,
        extra_message = "The value should be 0, 1, 2 or 3",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'IPO_EASE_IN_OUT'
    ),

    "nurbs_weight": BuiltInAttribute(

        friendly_name = "NURBS Curve Weight",                    
        description = "Weight value of a point in NURBS Curve",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT'],
        friendly_value_name='NURBS Curve Point Weight Value',
        friendly_value_names_override = [],
        default_value = 0.0,
        minimum_value = 0.0,
        maximum_value = 1.0,
        cannot_create = False,
        extra_message = "The value should be normalized",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'IPO_EASE_IN_OUT',
    ),

    "tilt": BuiltInAttribute(

        friendly_name = "Spline Tilt",                    
        description = "Tilt value of a spline",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT'],
        friendly_value_name='Curve Point Tilt Value',
        friendly_value_names_override = [],
        default_value = 0.0,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'ANIM_DATA',
    ),

    ".sculpt_face_set": BuiltInAttribute(

        friendly_name = "Sculpt Face Set",                    
        description = "Index of sculpt face set",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['FACE'],
        data_types = ['INT'],
        friendly_value_name='Sculpt Mode Face Set Index',
        friendly_value_names_override = [],
        default_value = 0,
        minimum_value = 0,
        maximum_value = None,
        cannot_create = False,
        extra_message = "The value should be positive",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'FACE_MAPS',
        
    ),

    ".vs.": BuiltInAttribute(

        friendly_name = "Selected Vertices in UV Editor",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                       
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CORNER'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Selected Vertices in UV Editor State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'VERTEXSEL',
    ),

    ".es.": BuiltInAttribute(

        friendly_name = "Selected Edges in UV Editor",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CORNER'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Selected Edges in UV Editor State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'EDGESEL',
    ),

    ".pn.": BuiltInAttribute(
        friendly_name = "Pinned Vertices in UV Editor", # thanks to Etherlord for figuring this one out
        description = "Might not exist if there is no pinned vertices in UV Edtior",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.INTERNAL, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                      
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CORNER'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Pinned Vertices in UV Editor State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'PINNED',
    ),
    ".corner_edge": BuiltInAttribute(
        
        friendly_name = "Face Corner Edge Index",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CORNER'],
        data_types = ['INT'],
        friendly_value_name='Face Corner Edge Index',
        friendly_value_names_override = [],
        default_value = 0,
        minimum_value = 0,
        maximum_value = None,
        cannot_create = False,
        extra_message = "The value should contain a valid index of an edge",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'EDGESEL',
    ),
    ".corner_vert": BuiltInAttribute(

        friendly_name = "Face Corner Vertex Index",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['CORNER'],
        data_types = ['INT'],
        friendly_value_name='Face Corner Vertex Index',
        friendly_value_names_override = [],
        default_value = 0,
        minimum_value = 0,
        maximum_value = None,
        cannot_create = False,
        extra_message = "The value should contain a valid index of a vertex",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'VERTEXSEL',
    ),
    ".edge_verts": BuiltInAttribute(

        friendly_name = "Edge Vertex Indexes",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['EDGE'],
        data_types = ['FLOAT_VECTOR'],
        friendly_value_name='Edge Vertex Indices',
        friendly_value_names_override = [],
        default_value = (0,0,0),
        minimum_value = (0,0,0),
        maximum_value = None,
        cannot_create = False,
        extra_message = "The value should contain two valid indexes of vertices",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'VERTEXSEL',
    ),
    ".select_edge": BuiltInAttribute(

        friendly_name = "Selected Edges in Edit Mode",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['EDGE'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Edge Select State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'EDGESEL',
    ),
    ".select_poly": BuiltInAttribute(

        friendly_name = "Selected Faces",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['FACE'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Face Select State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'FACE_MAPS',
    ),
    ".select_vert": BuiltInAttribute(

        friendly_name = "Selected Vertices",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Vertex Select State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'VERTEXSEL',
    ),
    ".selection": BuiltInAttribute(

        friendly_name = "Selected Hair Curves Points or Splines",                    
        description = "Selected points or splines of Curves object",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['CURVES'],                     
        min_blender_ver = (3,5,0),                  
        unsupported_from_blender_ver = None,
        domains = ['POINT', 'CURVE'],
        data_types = ['BOOLEAN'],
        friendly_value_name='Point Select State',
        friendly_value_names_override = [],
        default_value = False,
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = False,
        procedural_context_write = False,
        icon = 'VERTEXSEL',
    ),
    "color": BuiltInAttribute(

        friendly_name = "Spline Point Color",                    
        description = "Color attribute of a spline point",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        min_blender_ver = (3,3,0),                  
        unsupported_from_blender_ver = None,
        domains = ['POINT'],
        data_types = ['FLOAT_COLOR'],
        friendly_value_name='Point Color',
        friendly_value_names_override = [],
        default_value = (1.0, 1.0, 1.0, 1.0),
        minimum_value = None,
        maximum_value = None,
        cannot_create = False,
        extra_message = "",
        warning_message = "",
        procedural_context_read = True,
        procedural_context_write = True,
        icon = 'TPAINT_HLT',
    ),


}


# Defines invert mode of the attribute
AttributeInvertMode = namedtuple("AttributeInvertMode", [
    "friendly_name",                    # Name used in GUI
    "description",                      # Description, just in case
])  

# Defines all supported invert modes for the attributes
# Some of them are vanity entries to inform the user about the action, and are not used in operators.
attribute_invert_modes = {
    "NOT": AttributeInvertMode(
        friendly_name='Not Operation',
        description='Sets the True values to False and False values to True',

    ),
    "MULTIPLY_MINUS_ONE": AttributeInvertMode(
        friendly_name='Multiply by -1',
        description='Multiply each attribute value by -1',

    ),
    "ADD_TO_MINUS_ONE": AttributeInvertMode(
        friendly_name='Add to -1',
        description='Add each attribute value to -1',

    ),
    "SUBTRACT_FROM_ONE": AttributeInvertMode(
        friendly_name='Subtract from 1',
        description='Subtract each attribute value from 1',

    ),
    "REVERSE_ORDER": AttributeInvertMode(
        friendly_name='Reverse Order',
        description='Reverse the order of elements',

    ),
}

# All supported modes for converting attributes to different type
attribute_convert_modes = [("GENERIC", "Generic", ""),
               ("VERTEX_GROUP", "Vertex Group", ""),]

# All modes used for comparing data in attributes
attribute_comparison_modes = {
    "EQ": ("EQ", "Equal to", "=="),
    "NEQ": ("NEQ", "Not equal to", "!="),
    "EQORGR": ("EQORGR", "Equal or greater than", ">="),
    "EQORLS": ("EQORLS", "Equal or lesser than", "<="),
    "GR": ("GR", "Greater than", ">"),
    "LS": ("LS", "Lesser than", "<"),
    "CONTAINS": ("CONTAINS", "That contain", "in"),
    "STARTS_WITH": ("STARTS_WITH", "That start with", "startswith"),
    "ENDS_WITH": ("ENDS_WITH", "That end with", "endswith"),
}
