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

# Defines object data sourc,e
ObjectDataSource = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",                                   # Friendly name shown in UI
    "enum_gui_friendly_name_no_special_characters",             # Friendly name shown in UI without non-standard character set
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
    "quick_ui_exec_type"                                        # Used when operator is called and is meant to be executed instantly (no menu) INVOKE_DEFAULT or EXEC_DEFAULT
])

# Contains object data sources
object_data_sources = {
    # Special entries
    #   "INSERT_SEPARATOR_": None,         will add a separator in enum menu
    #   "INSERT_NEWLINE_": None,           will add a new column in enum menu
    #
    # Formattable string values:
    #   face_map shape_key domain vertex_group material material_slot shape_key_to shape_key_from
    
    # ON ALL DOMAINS
    # --------------------------------------
    "INDEX": ObjectDataSource(
        enum_gui_friendly_name="Index ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Index",
        enum_gui_description="Create attribute from domain index",
        attribute_auto_name="{domain} Index",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE', 'CORNER'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    # ON VERTEX EDGE FACE
    # --------------------------------------
    "INSERT_SEPARATOR_VEF": None, 
    
    "VISIBLE": ObjectDataSource(
        enum_gui_friendly_name="Visible ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Visible",
        enum_gui_description="Create boolean vertex attribute from domain visiblity",
        attribute_auto_name="Visible {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "HIDE_OFF",
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "POSITION": ObjectDataSource(
        enum_gui_friendly_name="Position ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Position",
        enum_gui_description="Create vertex attribute from domain position",
        attribute_auto_name="{domain} Position",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "GIZMO",
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),
    
    # ON VERTEX FACE
    # --------------------------------------
    "INSERT_SEPARATOR_VF": None,

    "NORMAL": ObjectDataSource(
        enum_gui_friendly_name="Normal ⁻ ᵛᵉʳᵗᵉˣ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Normal",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    # QUICK BOOLEANS
    # --------------------------------------
    "INSERT_SEPARATOR_QBOOL": None,

    "SELECTED": ObjectDataSource(
        enum_gui_friendly_name="Selected ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Boolean From Selected",
        enum_gui_description="Create boolean attribute from domain selection",
        attribute_auto_name="Selected {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "RESTRICT_SELECT_OFF",
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "NOT_SELECTED": ObjectDataSource(
        enum_gui_friendly_name="Not Selected ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Boolean From Not Selected",
        enum_gui_description="Create boolean attribute from domain that is not selected",
        attribute_auto_name="Not selected {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "RESTRICT_SELECT_ON",
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),
    
    # VERTEX ONLY
    # --------------------------------------
    "INSERT_NEWLINE_VERTEX": None,

    "SCULPT_MODE_MASK": ObjectDataSource(
        enum_gui_friendly_name="Sculpt mode mask ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Sculpt mode mask",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "VERT_MEAN_BEVEL": ObjectDataSource(
        enum_gui_friendly_name="Vertex Mean Bevel Weight ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Vertex Mean Bevel Weight",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "VERT_MEAN_CREASE": ObjectDataSource(
        enum_gui_friendly_name="Mean Vertex Crease ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Mean Vertex Crease",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "VERT_FROM_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="Vertex Group Weight ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Vertex Group Weight",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "VERT_IS_IN_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="Is In Vertex Group ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Is In Vertex Group",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "VERT_SHAPE_KEY_POSITION": ObjectDataSource(
        enum_gui_friendly_name="Position from Shape Key ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Position from Shape Key",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "VERT_SHAPE_KEY_POSITION_OFFSET": ObjectDataSource(
        enum_gui_friendly_name="Position Offset from Shape Key ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="Position Offset from Shape Key",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    # EDGE ONLY
    # --------------------------------------
    "INSERT_NEWLINE_EDGE": None,

    "EDGE_SEAM": ObjectDataSource(
        enum_gui_friendly_name="Edge Seam ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Edge Seam",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "EDGE_BEVEL_WEIGHT": ObjectDataSource(
        enum_gui_friendly_name="Edge Bevel Weight ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Edge Bevel Weight",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "EDGE_CREASE": ObjectDataSource(
        enum_gui_friendly_name="Edge Crease ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Edge Crease",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "EDGE_SHARP": ObjectDataSource(
        enum_gui_friendly_name="Edge Sharp ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Edge Sharp",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "EDGE_FREESTYLE_MARK": ObjectDataSource(
        enum_gui_friendly_name="Edge Freestyle Mark ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Edge Freestyle Mark",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "EDGE_IS_LOOSE": ObjectDataSource(
        enum_gui_friendly_name="Loose Edges ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Loose Edges",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "EDGE_VERTICES": ObjectDataSource(
        enum_gui_friendly_name="Edge Vertices ⁻ ᵉᵈᵍᵉ",
        enum_gui_friendly_name_no_special_characters="Edge Vertices",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    # FACE ONLY
    # --------------------------------------
    "INSERT_NEWLINE_FACE": None,  

    "SCULPT_MODE_FACE_SETS": ObjectDataSource(
        enum_gui_friendly_name="Sculpt Mode Face Set Index ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Sculpt Mode Face Set Index",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_USE_SMOOTH": ObjectDataSource(
        enum_gui_friendly_name="Face Use Smooth ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Face Use Smooth",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_AREA": ObjectDataSource(
        enum_gui_friendly_name="Face Area ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Face Area",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_MATERIAL_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Material Index ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Material Index",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    # "FACE_MATERIAL_SLOT_INDEX": ObjectDataSource(
    #     enum_gui_friendly_name="Material Slot Index ⁻ ᶠᵃᶜᵉ",
    #     enum_gui_friendly_name_no_special_characters="",
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
        enum_gui_friendly_name="All Vertex Indexes in a Face ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Vertices Indexes in a Face",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_CORNER_INDEXES": ObjectDataSource(
        enum_gui_friendly_name="All Corner Indexes of a Face ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Corner Indexes of a Face",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_CORNER_TOTAL": ObjectDataSource(
        enum_gui_friendly_name="Corner Count in a Face ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Corner Count in a Face",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_CORNER_START_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Corner Start Index in a Face ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Corner Start Index in a Face",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_FROM_FACE_MAP": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Face Map ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Boolean From Face Map",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "FACE_MAP_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Map Index ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Face Map Index",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "FACE_IS_MATERIAL_ASSIGNED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Material Assignment ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Boolean From Material Assignment",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "FACE_IS_MATERIAL_SLOT_ASSIGNED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Material Slot Assignment ⁻ ᶠᵃᶜᵉ",
        enum_gui_friendly_name_no_special_characters="Boolean From Material Slot Assignment",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    # FACE CORNER ONLY
    # --------------------------------------
    "INSERT_NEWLINE_FACE_CORNER": None,
    
    "SPLIT_NORMALS": ObjectDataSource(
        enum_gui_friendly_name="Split Normals ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Split Normals",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "CORNER_TANGENT": ObjectDataSource(
        enum_gui_friendly_name="Tangent ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Tangent",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "CORNER_BITANGENT": ObjectDataSource(
        enum_gui_friendly_name="Bitangent ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Bitangent",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "CORNER_BITANGENT_SIGN": ObjectDataSource(
        enum_gui_friendly_name="Bitangent Sign ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Bitangent Sign",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "CORNER_EDGE_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Corner Edge Index ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Face Corner Edge Index",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),

    "CORNER_VERTEX_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Corner Vertex Index ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="Face Corner Vertex Index",
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
        quick_ui_exec_type = 'EXEC_DEFAULT'
    ),
    "UVMAP": ObjectDataSource(
        enum_gui_friendly_name="UVMap ⁻ ᶜᵒʳⁿᵉʳ",
        enum_gui_friendly_name_no_special_characters="UVMap",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "INSERT_SEPARATOR_SPECIAL": None,

    # # SPECIAL
    # --------------------------------------
    
    # data len == len(loops) for both, idk how to proceed with this 

    "SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataSource(
        enum_gui_friendly_name="UV Editor Selected Vertices ⁻ ᵘᵛ",
        enum_gui_friendly_name_no_special_characters="Selected Vertices in UV Editor",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),


    "SELECTED_EDGES_IN_UV_EDITOR": ObjectDataSource(
        enum_gui_friendly_name="UV Editor Selected Edges ⁻ ᵘᵛ",
        enum_gui_friendly_name_no_special_characters="Selected Edges in UV Editor",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
    ),

    "PINNED_VERTICES_IN_UV_EDITOR": ObjectDataSource(
        enum_gui_friendly_name="UV Editor Pinned Vertices ⁻ ᵘᵛ",
        enum_gui_friendly_name_no_special_characters="Pinned Vertices in UV Editor",
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
        quick_ui_exec_type = 'INVOKE_DEFAULT'
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
    "bpy_ops_set_attribute_param_name",         # Name of the parameter passed to bpy.ops.mesh.attribute_set to assign the value to this data type
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
    # "FLOAT4X4": AttributeDataType(
    #     friendly_name='4x4 Matrix',
    #     min_blender_ver=(4,2,0),
    #     unsupported_from_blender_ver=None,
    #     supported_attribute_invert_modes=["INVERSE_OF_A_MATRIX"], # needs implementation
    #     supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
    #     vector_subelements_names=['X1','Y1','Z1','W1','X2','Y2','Z2','W2','X3','Y3','Z3','W3','X4','Y4','Z4','W4'],
    #     gui_prop_subtype=None, #EDataTypeGuiPropType.VECTOR,
    #     bpy_ops_set_attribute_param_name="value_quat",
    #     default_value=(1.0, 0.0, 0.0, 0.0),
    #     compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],
    #     geonodes_attribute_node_datatype="FLOAT4X4",
    #     animnodes_attribute_node_datatype="",
    #     default_randomize_value_min=(-1.0,-1.0,-1.0,-1.0, -1.0,-1.0,-1.0,-1.0, -1.0,-1.0,-1.0,-1.0, -1.0,-1.0,-1.0,-1.0),
    #     default_randomize_value_max=(1.0,1.0,1.0,1.0, 1.0,1.0,1.0,1.0, 1.0,1.0,1.0,1.0, 1.0,1.0,1.0,1.0),
    #     cast_type=tuple,
    #     large_capacity_vector=True,
    #     large_capacity_vector_size=16,
    #     large_capacity_vector_size_height=4,
    #     large_capacity_vector_size_width=4,
    # ),
}

# Defines mesh domain entries
AttributeDomain = namedtuple("AttributeDomain", [
    "friendly_name",
    "friendly_name_short",                      # The name presented to the user (shorter)
    "friendly_name_veryshort",                  # The name presented to the user (shorter)
    "min_blender_ver",
    "unsupported_from_blender_ver",
])

# Defines all mesh domains
attribute_domains = {
    "POINT": AttributeDomain(
        friendly_name="Vertex",
        friendly_name_short="Vertex",
        friendly_name_veryshort="V",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "EDGE": AttributeDomain(
        friendly_name="Edge",
        friendly_name_short="Edge",
        friendly_name_veryshort="E",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "FACE": AttributeDomain(
        friendly_name="Face",
        friendly_name_short="Face",
        friendly_name_veryshort="V",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "CORNER": AttributeDomain(
        friendly_name="Face Corner",
        friendly_name_short="Corner",
        friendly_name_veryshort="C",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "CURVE": AttributeDomain(
        friendly_name="Spline",
        friendly_name_short="Spline",
        friendly_name_veryshort="S",
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
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
AttributeType = namedtuple("AttriubteType", [
    "friendly_name",                    # Name used in GUI
    "description",                      # Description, just in case
    "types",                            # List of EAttributeType
    "object_types",                     # Found on object types, eg MESH
    "min_blender_ver",                  # Minimum blender version that this attribute appeared
    "unsupported_from_blender_ver",     # First blender version that removed this attribute
    # domains
    # data type
])  

# Stores all explicitly defined attributes that are generated by blender.
defined_attributes = {

    # "GENERIC": AttributeDomain(
    #     
    #     friendly_name = "",                    
    #     description = "",                      
    #     types = [],                            
    #     object_types = [],                     
    #     min_blender_ver = None,                  
    #     unsupported_from_blender_ver = None,
    #),

    "position": AttributeType(
        
        friendly_name = "Vertex Position",                    
        description = "The position of vertices in a mesh",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.CANTREMOVE, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH'],                        
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "radius": AttributeType(
        
        friendly_name = "Curve or Point Cloud Radius",                    
        description = "The radius of the point cloud points or curves",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVE', 'POINT_CLOUD'], # I have no idea what is the object name for this, as it seems to be removed. Left just in case.                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "id": AttributeType(
        
        friendly_name = "ID",                    
        description = "Unique index (auto-generated by geometry nodes)",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "material_index": AttributeType(
        
        friendly_name = "Material Index",                    
        description = "Index of applied material to a face",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "crease": AttributeType(
        
        friendly_name = "Edge Crease",                    
        description = "Edge Crease",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "sharp_face": AttributeType(
        
        friendly_name = "Face Sharp",                    
        description = "aka. smooth shading",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "resolution": AttributeType(
        
        friendly_name = "Bézier Spline/NURBs Resolution",                    
        description = "Number of points between two control points",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVE'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "cyclic": AttributeType(
        
        friendly_name = "Spline Cyclic",                    
        description = "\"Is the spline cyclic\" boolean",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
        # Boolean, spline
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "handle_left": AttributeType(
        
        friendly_name = "Bézier Curve Handle Left",                    
        description = "The position of right handle of Bézier Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "handle_right": AttributeType(
        
        friendly_name = "Bézier Curve Handle Right",                    
        description = "The position of right handle of Bézier Curve",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.DONOTREMOVE],                            
        object_types = ['CURVE'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    
    "velocity": AttributeType(
        
        friendly_name = "Velocity",                    
        description = "Velocity vector value used for motion blur",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "rest_position": AttributeType(
        
        friendly_name = "Mesh Rest Position",                    
        description = "The position of vertices without shape keys and modifiers",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['MESH', 'CURVES'],                     
        # spline or mesh point
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "surface_uv_coordinate": AttributeType(
        
        friendly_name = "Surface UV Coordinate",                    
        description = "Curves attachment location to a mesh",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # 2D Vector spline
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    
    ".sculpt_mask": AttributeType(

        friendly_name = "Sculpt Mask",                    
        description = "The value of mask in sculpt mode",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],  
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "surface_normal": AttributeType(
        friendly_name = "Curves Surface Mesh Normal Vector",                    
        description = "Normal vector of the surface mesh at curve root",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # spline, vector
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "normal_mode": AttributeType(
        
        friendly_name = "Unknown",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # spline, 8bit
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "knots_mode": AttributeType(
        
        friendly_name = "Unknown",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # spline, 8bit
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "nurbs_order": AttributeType(
        
        friendly_name = "Unknown",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # spline, 8bit
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "curve_type": AttributeType(
        
        friendly_name = "Curve Type",                    
        description = "Type of the curve: Poly, Bezier or NURBS",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # spline, 8bit
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "nurbs_weight": AttributeType(

        friendly_name = "NURBS Curve Weight",                    
        description = "Weight value of a point in NURBS Curve",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # float point on curves
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "tilt": AttributeType(

        friendly_name = "Spline Tilt",                    
        description = "Tilt value of a spline",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
        # point float
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    ".sculpt_face_set": AttributeType(
        
        friendly_name = "Sculpt face set",                    
        description = "Index of sculpt face set",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    ".vs.": AttributeType(
        
        friendly_name = "Selected Vertices in UV Editor",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                       
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    ".es.": AttributeType(
        friendly_name = "Selected Edges in UV Editor",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                     
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    ".pn.": AttributeType(
        friendly_name = "Pinned Vertices in UV Editor", # thanks to Etherlord for figuring this one out
        description = "Might not exist if there is no pinned vertices in UV Edtior",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.INTERNAL, EAttributeType.NOTPROCEDURAL],                            
        object_types = ['MESH'],                      
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    ".corner_edge": AttributeType(
        
        friendly_name = "Face Corner Edge Index",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    ".corner_vert": AttributeType(
        
        friendly_name = "Face Corner Vertex Index",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    ".edge_verts": AttributeType(
        friendly_name = "Edge Vertex Indexes",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    ".select_edge": AttributeType(
        friendly_name = "Selected Edges",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    ".select_poly": AttributeType(
        friendly_name = "Selected Faces",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),
    ".select_vert": AttributeType(
        friendly_name = "Selected Vertices",                    
        description = "",                      
        types = [EAttributeType.AUTOGENERATED, EAttributeType.NOTPROCEDURAL, EAttributeType.CANTREMOVE],                            
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
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
