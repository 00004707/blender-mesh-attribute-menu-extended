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

This file stores all tuples and classes related to enum entries and user data input storage for use in GUI

"""

import bpy
from collections import namedtuple
from . import etc
from enum import Enum

# Defines object data sourc,e
ObjectDataSource = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",
    "enum_gui_friendly_name_no_special_characters",
    "enum_gui_description",
    "attribute_auto_name",
    "attribute_domain_on_default",
    "domains_supported",
    "data_type",
    "min_blender_ver",
    "unsupported_from_blender_ver",
    "batch_convert_support",
    "valid_data_sources", # futureproofing for other object types
    "icon"
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
        icon= "LINENUMBERS_ON"
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
        icon= "HIDE_OFF"
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
        icon= "GIZMO"
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
        icon= "NORMALS_FACE"
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
        icon= "RESTRICT_SELECT_OFF"
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
        icon= "RESTRICT_SELECT_ON"
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
        icon= "MOD_MASK"
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
        icon= "MOD_BEVEL"
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
        icon= "LINCURVE"
    ),

    "VERT_FROM_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="From Vertex Group ⁻ ᵛᵉʳᵗᵉˣ",
        enum_gui_friendly_name_no_special_characters="From Vertex Group",
        enum_gui_description="Create float vertex attribute from vertex group values",
        attribute_auto_name="{vertex_group} Vertex Weight",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH'],
        icon= "GROUP_VERTEX"
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
        icon= "GROUP_VERTEX"
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
        icon= "SHAPEKEY_DATA"
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
        icon= "SHAPEKEY_DATA"
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
        icon= "OUTLINER_DATA_EMPTY"
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
        icon= "MOD_BEVEL"
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
        icon= "LINCURVE"
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
        icon= "SHARPCURVE"
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
        icon= "OUTLINER_OB_EMPTY"
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
        icon= "MOD_EDGESPLIT"
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
        icon= "VERTEXSEL"
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
        icon= "FACE_MAPS"
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
        icon= "SMOOTHCURVE"
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
        icon= "SNAP_FACE"
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
        icon= "MATERIAL"
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
        icon= "LINENUMBERS_ON"
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
        icon= "LINENUMBERS_ON"
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
        icon= ""
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
        icon= "LINENUMBERS_ON"
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
        icon= "FACE_MAPS"
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
        icon= "LINENUMBERS_ON"
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
        icon= "MATERIAL"
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
        icon= "MATERIAL"
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
        icon= "MOD_NORMALEDIT"
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
        icon= "DRIVER_ROTATIONAL_DIFFERENCE"
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
        icon= "DRIVER_ROTATIONAL_DIFFERENCE"
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
        icon= "DRIVER_ROTATIONAL_DIFFERENCE"
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
        icon= "LINENUMBERS_ON"
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
        icon= "LINENUMBERS_ON"
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
        batch_convert_support=False,
        valid_data_sources = ['MESH'],
        icon= "UV"
    ),

    # "INSERT_SEPARATOR_SPECIAL": None,

    # # SPECIAL
    # --------------------------------------
    
    # data len == len(loops) for both, idk how to proceed with this 

    # "SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataSource(
    #     enum_gui_friendly_name="Selected UV Vertices ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if etc.get_enhanced_enum_titles_enabled() else "Selected UV Vertices (UV Editor)",
    #     enum_gui_friendly_name_no_special_characters="",
    #   enum_gui_description="Create boolean vertex attribute from selected vertices in UV Editor",
    #     attribute_auto_name="Selected {uvmap} UV Vertices",
    #     attribute_domain_on_default='POINT',
    #     domains_supported=['POINT'],
    #     data_type='BOOLEAN',
    #     min_blender_ver=None,
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['MESH'],
    #   icon= ""
    # ),

    # "SELECTED_EDGES_IN_UV_EDITOR": ObjectDataSource(
    #     enum_gui_friendly_name="Selected UV Edges ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if etc.get_enhanced_enum_titles_enabled() else "Selected UV Edges (UV Editor)",
    #     enum_gui_friendly_name_no_special_characters="",
    #   enum_gui_description="Create boolean edge attribute from selected edges in UV Editor",
    #     attribute_auto_name="Selected {uvmap} UV Edges",
    #     attribute_domain_on_default='EDGE',
    #     domains_supported=['EDGE'],
    #     data_type='BOOLEAN',
    #     min_blender_ver=None,
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['MESH'],
    #   icon= ""
    # ),

}

# Defines an object data target
ObjectDataTarget = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",
    "enum_gui_description",
    "domains_supported",
    "data_type",
    "min_blender_ver",
    "unsupported_from_blender_ver",
    "icon"
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
            enum_gui_friendly_name="To Visible In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Visible In Edit Mode",
            enum_gui_description="Convert this attribute to visible in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="HIDE_OFF",
        ),

    "TO_HIDDEN": ObjectDataTarget(
            enum_gui_friendly_name="To Hidden In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Hidden In Edit Mode",
            enum_gui_description="Convert this attribute to hidden in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="HIDE_ON",
        ),

    "TO_SELECTED": ObjectDataTarget(
            enum_gui_friendly_name="To Selected In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Selected In Edit Mode",
            enum_gui_description="Convert this attribute to selected in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="RESTRICT_SELECT_OFF",
        ),

    "TO_NOT_SELECTED": ObjectDataTarget(
            enum_gui_friendly_name="To Not Selected In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Not Selected In Edit Mode",
            enum_gui_description="Convert this attribute to selected in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="RESTRICT_SELECT_ON",
        ),

    # # VERTEX EDGE
    # --------------------------------------
    "INSERT_SEPARATOR_VE": None,  

    "TO_MEAN_BEVEL_WEIGHT": ObjectDataTarget(
            enum_gui_friendly_name="To Bevel Weight ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Mean Bevel Weight",
            enum_gui_description="Convert this attribute to bevel weight",
            
            domains_supported=['POINT', 'EDGE'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MOD_BEVEL",
        ),

    "TO_MEAN_CREASE": ObjectDataTarget(
            enum_gui_friendly_name="To Mean Crease ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Mean Crease",
            enum_gui_description="Convert this attribute to mean crease",
            
            domains_supported=['POINT', 'EDGE'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="LINCURVE",
        ),

    # VERTEX CORNER
    # --------------------------------------
    "INSERT_SEPARATOR_VC": None,  

    'TO_SPLIT_NORMALS': ObjectDataTarget(
            enum_gui_friendly_name="To Split Normals ⁻ ᵛᵉʳᵗᵉˣ ᶜᵒʳⁿᵉʳ" if etc.get_enhanced_enum_titles_enabled() else "To Split Normals",
            enum_gui_description="Convert this attribute to split normals",
            
            domains_supported=['POINT', 'CORNER'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MOD_NORMALEDIT",
        ),

    # VERTEX
    # --------------------------------------
    "INSERT_NEWLINE_V": None, 

    "TO_POSITION": ObjectDataTarget(
            enum_gui_friendly_name="To Position ⁻ ᵛᵉʳᵗᵉˣ" if etc.get_enhanced_enum_titles_enabled() else "To Position",
            enum_gui_description="Convert this attribute to mesh positon",
            
            domains_supported=['POINT'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="GIZMO",
        ),

    "TO_SCULPT_MODE_MASK": ObjectDataTarget(
            enum_gui_friendly_name="To Sculpt Mode Mask ⁻ ᵛᵉʳᵗᵉˣ" if etc.get_enhanced_enum_titles_enabled() else "To Sculpt Mode Mask",
            enum_gui_description="Convert this attribute to sculpt mode mask",
            
            domains_supported=['POINT'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MOD_MASK",
        ),

    "TO_VERTEX_GROUP": ObjectDataTarget(
            enum_gui_friendly_name="To Vertex Group  ⁻ ᵛᵉʳᵗᵉˣ" if etc.get_enhanced_enum_titles_enabled() else "To Vertex Group",
            enum_gui_description="Convert this attribute to vertex group",
            
            domains_supported=['POINT'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="GROUP_VERTEX",
        ),
        
    "TO_SHAPE_KEY": ObjectDataTarget(
            enum_gui_friendly_name="To Shape Key ⁻ ᵛᵉʳᵗᵉˣ" if etc.get_enhanced_enum_titles_enabled() else "To Shape Key",
            enum_gui_description="Convert this attribute to mesh shape key",
            
            domains_supported=['POINT'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="SHAPEKEY_DATA",
        ),

    "TO_VERTEX_GROUP_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="To Vertex Group Index ⁻ ᵛᵉʳᵗᵉˣ" if etc.get_enhanced_enum_titles_enabled() else "To Vertex Group Index",
            enum_gui_description="Convert this attribute to vertex group index for use with armatures",
            domains_supported=['POINT'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="GROUP_VERTEX",
        ),

    # EDGE
    # --------------------------------------
    "INSERT_SEPARATOR_E": None, 

    "TO_SEAM": ObjectDataTarget(
            enum_gui_friendly_name="To Seams ⁻ ᵉᵈᵍᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Seams",
            enum_gui_description="Convert this attribute to edge seams",
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="EMPTY_DATA",
        ),

    "TO_SHARP": ObjectDataTarget(
            enum_gui_friendly_name="To Sharp ⁻ ᵉᵈᵍᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Sharp",
            enum_gui_description="Convert this attribute to edge sharps",         
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="SHARPCURVE",
        ),

    "TO_FREESTYLE_MARK": ObjectDataTarget(
            enum_gui_friendly_name="To Freestyle Mark ⁻ ᵉᵈᵍᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Freestyle Mark",
            enum_gui_description="Convert this attribute to edge freestyle mark",
            
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="OUTLINER_OB_EMPTY",
        ),

    # FACE
    # --------------------------------------
    "INSERT_NEWLINE_F": None, 

    "TO_FACE_SHADE_SMOOTH": ObjectDataTarget(
            enum_gui_friendly_name="To Face Shade Smooth ⁻ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Face Shade Smooth",
            enum_gui_description="Convert this attribute to face shade smooth",
            
            domains_supported=['FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="SMOOTHCURVE",
        ),

    "TO_FACE_MAP": ObjectDataTarget(
            enum_gui_friendly_name="To Face Map ⁻ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Face Map",
            enum_gui_description="Convert this attribute to face map",
            
            domains_supported=['FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=(4,0),
            icon="FACE_MAPS",
        ),

    "TO_SCULPT_MODE_FACE_SETS": ObjectDataTarget(
            enum_gui_friendly_name="To Sculpt Mode Face Sets ⁻ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Sculpt Mode Face Sets",
            enum_gui_description="Convert this attribute to Sculpt Mode Face Sets",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="UV_FACESEL",
        ),

    "TO_MATERIAL_SLOT_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="To Material Slot Index ⁻ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "To Material Slot Index",
            enum_gui_description="Convert this attribute to Material Slot Index",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
            icon="MATERIAL",
        ),

    "TO_FACE_MAP_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="Set Face Map Index ⁻ ᶠᵃᶜᵉ" if etc.get_enhanced_enum_titles_enabled() else "Set Face Map Index",
            enum_gui_description="Convert this attribute to set face map index",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=(4,0),
            icon="FACE_MAPS",
        ),  

    # CORNER
    # --------------------------------------
    "INSERT_SEPARATOR_FC": None, 

    "TO_UVMAP": ObjectDataTarget(
            enum_gui_friendly_name="To UVMap ⁻ ᶜᵒʳⁿᵉʳ" if etc.get_enhanced_enum_titles_enabled() else "To UVMap",
            enum_gui_description="Convert this attribute to UVMap",
            
            domains_supported=['CORNER'],
            data_type='FLOAT2',
            min_blender_ver=None,
            unsupported_from_blender_ver=(3,5),
            icon="UV",
        ),  

    # # SPECIAL
    # --------------------------------------
    # "INSERT_SEPARATOR_SPECIAL": None, 

    # "TO_SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataTarget(
    #         enum_gui_friendly_name="Selected UV Vertices ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if etc.get_enhanced_enum_titles_enabled() else "Selected UV Vertices (UV Editor)",
    #         enum_gui_description="Convert this attribute to selected vertices in UV Editor Panel",
    #         domains_supported=['POINT'],
    #         data_type='BOOLEAN',
    #         min_blender_ver=None,
    #         unsupported_from_blender_ver=None,
    #         icon="",
    #     ),    
    
    # "TO_SELECTED_EDGES_IN_UV_EDITOR": ObjectDataTarget(
    #         enum_gui_friendly_name="Selected UV Edges ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if etc.get_enhanced_enum_titles_enabled() else "Selected UV Edges (UV Editor)",
    #         enum_gui_description="Convert this attribute to selected edges in UV Editor Panel",
    #         domains_supported=['EDGE'],
    #         data_type='BOOLEAN',
    #         min_blender_ver=None,
    #         unsupported_from_blender_ver=None,
    #         icon="",
    #     ),    

    # "TO_PINNED_VERTICES_IN_UV_EDITOR": ObjectDataTarget(
    #         enum_gui_friendly_name="Pinned UV Vertices ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if etc.get_enhanced_enum_titles_enabled() else "SPinned UV Vertices (UV Editor)",
    #         enum_gui_description="Convert this attribute to pinned vertices in UV Editor Panel",
    #         domains_supported=['POINT'],
    #         data_type='BOOLEAN',
    #         min_blender_ver=None,
    #         unsupported_from_blender_ver=None,
    #         icon="",
    #     ),    

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

class EDataTypeGuiPropType(Enum):
    SCALAR = 0          #int float int8
    VECTOR = 1          #float vector, vector 2d, quaternion
    COLOR  = 3          # float color byte color
    STRING = 4          # string
    BOOLEAN = 5         # boolean

# Define mesh data type entries
AttributeDataType = namedtuple("AttributeDataType", [
    "friendly_name",                            # The name presented to the user
    "min_blender_ver",                          # Minimum blender version that this data type is supported from
    "unsupported_from_blender_ver",             # First blender version that this data type is unsupported from
    "supported_attribute_invert_modes",         # Supported invert modes, from attribute_invert_modes
    "supported_comparison_modes",               # Supported comparison modes, from attribute_comparison_modes
    "gui_property_name",                        # The property name from MAME_PropValues class
    "gui_prop_subtype",                         # Type of the gui to display for this attribute data type (EDataTypeGuiPropType)
    "vector_subelements_names"                  # Names of subelements in a vector value, eg X Y Z or None    

])

# Defines all supported mesh data types
attribute_data_types = {
    "FLOAT": AttributeDataType(
        friendly_name="Float",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_float",
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR
    ),
    "INT": AttributeDataType(
        friendly_name="Integer",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_int",
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR
    ),
    "INT8": AttributeDataType(
        friendly_name="8-bit Integer",
        min_blender_ver=(3,2,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_int8",
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR
    ),
    "FLOAT_VECTOR": AttributeDataType(
        friendly_name="Vector",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_vector",
        vector_subelements_names=['X','Y','Z'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR
    ),
    "FLOAT_COLOR": AttributeDataType(
        friendly_name="Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_color",
        vector_subelements_names=['R','G','B','A'],
        gui_prop_subtype=EDataTypeGuiPropType.COLOR
    ),
    "BYTE_COLOR": AttributeDataType(
        friendly_name="Byte Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_bytecolor",
        vector_subelements_names=['R','G','B','A'],
        gui_prop_subtype=EDataTypeGuiPropType.COLOR
    ),
    "STRING": AttributeDataType(
        friendly_name="String",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["REVERSE_ORDER"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_string",
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.STRING
    ),
    "BOOLEAN": AttributeDataType(
        friendly_name="Boolean",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["NOT"],
        supported_comparison_modes=['EQ','NEQ'],
        gui_property_name="val_bool",
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.BOOLEAN
    ),
    "FLOAT2": AttributeDataType(
        friendly_name="Vector 2D",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_vector2d",
        vector_subelements_names=['X','Y'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR
    ),
    "INT32_2D": AttributeDataType(
        friendly_name='2D Integer Vector',
        min_blender_ver=(3,6,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_int32_2d",
        vector_subelements_names=['X','Y'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR
    ),
    "QUATERNION": AttributeDataType(
        friendly_name='Quaternion',
        min_blender_ver=(4,0,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=['EQ','NEQ','EQORGR','EQORLS','GR','LS'],
        gui_property_name="val_quaternion",
        vector_subelements_names=['X','Y','Z','W'],
        gui_prop_subtype=EDataTypeGuiPropType.VECTOR
    ),
}

# Defines mesh domain entries
AttributeDomain = namedtuple("AttributeDomain", [
    "friendly_name",
    "min_blender_ver",
    "unsupported_from_blender_ver",
])

# Defines all mesh domains
attribute_domains = {
    "POINT": AttributeDomain(
        friendly_name="Vertex",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "EDGE": AttributeDomain(
        friendly_name="Edge",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "FACE": AttributeDomain(
        friendly_name="Face",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "CORNER": AttributeDomain(
        friendly_name="Face Corner",
        min_blender_ver=None,
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
    "GENERIC": AttributeDomain(
        friendly_name="Generic",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "VERTEX_GROUP": AttributeDomain(
        friendly_name="Vertex Group",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
}

class MAME_PropValues(bpy.types.PropertyGroup):
    """
    All input entries in GUI
    """

    # Assign attribute value in edit mode entries
    # -------------------------------------------------

    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_bool: bpy.props.BoolProperty(name="Boolean Value", default=True)
    val_vector2d: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    if etc.get_blender_support(attribute_data_types['INT8'].min_blender_ver, attribute_data_types['INT8'].unsupported_from_blender_ver):
        val_int8: bpy.props.IntProperty(name="8-bit Integer Value", min=-128, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if etc.get_blender_support(attribute_data_types['INT32_2D'].min_blender_ver, attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))
    if etc.get_blender_support(attribute_data_types['QUATERNION'].min_blender_ver, attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
        val_quaternion: bpy.props.FloatVectorProperty(name="Quaternion Value", size=4, default=(1.0,0.0,0.0,0.0))
    
    # Assign/select options
    # -------------------------------------------------

    face_corner_spill: bpy.props.BoolProperty(name="Face Corner Spill", default = False, description="Allow setting value to nearby corners of selected vertices or limit it only to selected face")
    val_select_non_zero_toggle: bpy.props.BoolProperty(name="Select Non-Zero", default=True, description='Select buttons will select/deselect "non-zero" values instead')

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
        object_types = ['MESH'],                     
         
        min_blender_ver = None,                  
        unsupported_from_blender_ver = None,
    ),

    "surface_uv_coordinate": AttributeType(
        
        friendly_name = "Surface UV Coordinate",                    
        description = "Curves attachment location to a mesh",                      
        types = [EAttributeType.AUTOGENERATED],                            
        object_types = ['CURVES'],                     
         
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