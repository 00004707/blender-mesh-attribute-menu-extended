"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Object Data Target Class Definition

"""
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
    #   "INSERT_CATEGORY_": "Category Friendly Name"       Will put entries below into a category
    #   "INSERT_SEPARATOR_": None,                         Will add a separator in menu
    #   Unused:
    #   "INSERT_NEWLINE_": None,           will add a new column in enum menu, if there is a string it will be set on title bar
    #
    # Formattable string values:
    #   NONE, FORMAT DOES NOT PLAY NICE WITH ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ STRINGS and spills out garbage

    #POINT EDGE FACE
    # --------------------------------------
    "TO_VISIBLE": ObjectDataTarget(
            enum_gui_friendly_name="To Visible In Edit Mode",
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
