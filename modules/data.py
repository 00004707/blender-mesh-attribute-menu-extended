"""
Data


"""

import bpy
from collections import namedtuple
from . import etc

enhanced_enum_titles = bool(bpy.app.version > (3,2,9))

def get_blender_support(minver, minver_unsupported):
    return (minver is None or bpy.app.version >= minver) and (minver_unsupported is None or bpy.app.version < minver_unsupported)

# Defines object data sourc,e
ObjectDataSource = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",
    "enum_gui_description",
    "attribute_auto_name",
    "attribute_domain_on_default",
    "domains_supported",
    "data_type",
    "min_blender_ver",
    "unsupported_from_blender_ver",
    "batch_convert_support",
    "valid_data_sources" # futureproofing for other object types
])

# Contains object data sources
#
# "INSERT_SEPARATOR_": None,         will add a separator in enum menu
# "INSERT_NEWLINE_": None,           will add a new column in enum menu
#
# Formattable string values:
# face_map shape_key domain vertex_group material material_slot shape_key_offset_from
object_data_sources = {
    # ON ALL DOMAINS
    "INDEX": ObjectDataSource(
        enum_gui_friendly_name="Index ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ ᶜᵒʳⁿᵉʳ"  if enhanced_enum_titles else "Index",
        enum_gui_description="Create attribute from domain index",
        attribute_auto_name="{domain} Index",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE', 'CORNER'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    # ON VERTEX EDGE FACE
    "INSERT_SEPARATOR_VEF": None, 
    
    "VISIBLE": ObjectDataSource(
        enum_gui_friendly_name="Visible ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Visible",
        enum_gui_description="Create boolean vertex attribute from domain visiblity",
        attribute_auto_name="Visible {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "POSITION": ObjectDataSource(
        enum_gui_friendly_name="Position ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Position",
        enum_gui_description="Create vertex attribute from domain position",
        attribute_auto_name="{domain} Position",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),
    
    # ON VERTEX FACE
    "INSERT_SEPARATOR_VF": None,

    "NORMAL": ObjectDataSource(
        enum_gui_friendly_name="Normal ⁻ ᵛᵉʳᵗᵉˣ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Normal",
        enum_gui_description="Create attribute from domain normals",
        attribute_auto_name="{domain} Normal",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'FACE'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    # QUICK BOOLEANS
    "INSERT_SEPARATOR_QBOOL": None,

    "SELECTED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Selected ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Boolean From Selected",
        enum_gui_description="Create boolean attribute from domain selection",
        attribute_auto_name="Selected {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "NOT_SELECTED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Not Selected ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Boolean From Not Selected",
        enum_gui_description="Create boolean attribute from domain that is not selected",
        attribute_auto_name="Not selected {domain}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),
    
    # VERTEX ONLY
    "INSERT_NEWLINE_VERTEX": None,

    "SCULPT_MODE_MASK": ObjectDataSource(
        enum_gui_friendly_name="Sculpt mode mask ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "Sculpt mode mask",
        enum_gui_description="Create float vertex attribute from masked vertices in sculpt mode",
        attribute_auto_name="Masked Vertices",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "VERT_MEAN_BEVEL": ObjectDataSource(
        enum_gui_friendly_name="Vertex Mean Bevel Weight ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "Vertex Mean Bevel Weight",
        enum_gui_description="Create float vertex attribute from Mean Bevel Weight",
        attribute_auto_name="Vertex Mean Bevel",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "VERT_MEAN_CREASE": ObjectDataSource(
        enum_gui_friendly_name="Mean Vertex Crease ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "Mean Vertex Crease",
        enum_gui_description="Create float vertex attribute from Mean Vertex Crease",
        attribute_auto_name="Vertex Mean Crease",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "VERT_FROM_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="From Vertex Group ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "From Vertex Group",
        enum_gui_description="Create float vertex attribute from vertex group values",
        attribute_auto_name="{vertex_group} Vertex Weight",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    "VERT_IS_IN_VERTEX_GROUP": ObjectDataSource(
        enum_gui_friendly_name="Is In Vertex Group ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "Is In Vertex Group",
        enum_gui_description="Create boolean vertex attribute from vertex group assignment",
        attribute_auto_name="Vertex in {vertex_group}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    "VERT_SHAPE_KEY_POSITION": ObjectDataSource(
        enum_gui_friendly_name="Position from Shape Key ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "Position from Shape Key",
        enum_gui_description="Create float vector attribute from shape key vertex position",
        attribute_auto_name="Position from {shape_key}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    "VERT_SHAPE_KEY_POSITION_OFFSET": ObjectDataSource(
        enum_gui_friendly_name="Position Offset from Shape Key ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "Position Offset from Shape Key",
        enum_gui_description="Create float vector attribute from shape key vertex position offset from other shape key",
        attribute_auto_name="Position Offset from {shape_key_offset_from} to {shape_key}",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    # EDGE ONLY
    "INSERT_NEWLINE_EDGE": None,

    "EDGE_SEAM": ObjectDataSource(
        enum_gui_friendly_name="Edge Seam ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Edge Seam",
        enum_gui_description="Create boolean edge attribute from seams",
        attribute_auto_name="Edge Seam",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "EDGE_BEVEL_WEIGHT": ObjectDataSource(
        enum_gui_friendly_name="Edge Bevel Weight ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Edge Bevel Weight",
        enum_gui_description="Create float edge attribute from Bevel Weight",
        attribute_auto_name="Edge Bevel Weight",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "EDGE_CREASE": ObjectDataSource(
        enum_gui_friendly_name="Edge Crease ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Edge Crease",
        enum_gui_description="Create float edge attribute from Crease",
        attribute_auto_name="Edge Crease",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "EDGE_SHARP": ObjectDataSource(
        enum_gui_friendly_name="Edge Sharp ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Edge Sharp",
        enum_gui_description="Create boolean edge attribute from Edge Sharp",
        attribute_auto_name="Edge Sharp",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "EDGE_FREESTYLE_MARK": ObjectDataSource(
        enum_gui_friendly_name="Edge Freestyle Mark ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Edge Freestyle Mark",
        enum_gui_description="Create boolean edge attribute from Freestyle Mark",
        attribute_auto_name="Edge Freestyle Mark",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "EDGE_IS_LOOSE": ObjectDataSource(
        enum_gui_friendly_name="Loose Edges ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Loose Edges",
        enum_gui_description="Create boolean edge attribute on loose edges",
        attribute_auto_name="Loose Edges",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "EDGE_VERTICES": ObjectDataSource(
        enum_gui_friendly_name="Edge Vertices ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "Edge Vertices",
        enum_gui_description="Create 2D vector edge attribute with indexes of edge vertices",
        attribute_auto_name="Edge Vertex Indexes",
        attribute_domain_on_default='EDGE',
        domains_supported=['EDGE'],
        data_type='FLOAT2',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    # FACE ONLY
    "INSERT_NEWLINE_FACE": None,  

    "SCULPT_MODE_FACE_SETS": ObjectDataSource(
        enum_gui_friendly_name="Sculpt Mode Face Set Index ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Sculpt Mode Face Set Index",
        enum_gui_description="Create float face attribute from face sets in sculpt mode",
        attribute_auto_name="Sculpt Mode Face Set Index",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_USE_SMOOTH": ObjectDataSource(
        enum_gui_friendly_name="Face Use Smooth ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Face Use Smooth",
        enum_gui_description="Create boolean face attribute from smooth shading of a face",
        attribute_auto_name="Is Face Smooth Shaded",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_AREA": ObjectDataSource(
        enum_gui_friendly_name="Face Area ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Face Area",
        enum_gui_description="Create float face attribute from area of each face",
        attribute_auto_name="Face Area",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_MATERIAL_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Material Index ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Material Index",
        enum_gui_description="Create integer face attribute from material index",
        attribute_auto_name="Face Material Index",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    # "FACE_MATERIAL_SLOT_INDEX": ObjectDataSource(
    #     enum_gui_friendly_name="Material Slot Index ⁻ ᶠᵃᶜᵉ",
    #     enum_gui_description="Create integer face attribute from material slot index",
    #     attribute_auto_name="Face Material Slot Index",
    #     attribute_domain_on_default='FACE',
    #     domains_supported=['FACE'],
    #     data_type='INT',
    #     min_blender_ver=None,
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['MESH']
    # ),



    "FACE_VERTS": ObjectDataSource(
        enum_gui_friendly_name="All Vertex Indexes in a Face ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Vertices Indexes in a Face",
        enum_gui_description="Create color (4D Vector) face attribute from indexes of vertices of a face",
        attribute_auto_name="Face Vertex Indexes",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='FLOAT_COLOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_CORNER_INDEXES": ObjectDataSource(
        enum_gui_friendly_name="All Corner Indexes of a Face ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Corner Indexes of a Face",
        enum_gui_description="Create color (4D Vector) face attribute from indexes of face corners of a face",
        attribute_auto_name="Corner Indexes of a Face",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='FLOAT_COLOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_CORNER_TOTAL": ObjectDataSource(
        enum_gui_friendly_name="Corner Count in a Face ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Corner Count in a Face",
        enum_gui_description="Create integer face attribute from count of face corners in a face",
        attribute_auto_name="Corners Count in a Face",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_CORNER_START_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Corner Start Index in a Face ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Corner Start Index in a Face",
        enum_gui_description="Create integer face attribute from lowest index from face corners in a face",
        attribute_auto_name="Corner Start Index in a Face",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_FROM_FACE_MAP": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Face Map ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Boolean From Face Map",
        enum_gui_description="Create boolean face attribute from face map assignment",
        attribute_auto_name="Is face in {face_map}",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=(4,0),
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    "FACE_MAP_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Map Index ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Face Map Index",
        enum_gui_description="Create boolean face attribute from face map assignment",
        attribute_auto_name="Assigned Face Map Index",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=(4,0),
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "FACE_IS_MATERIAL_ASSIGNED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Material Assignment ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Boolean From Material Assignment",
        enum_gui_description="Create boolean face attribute from material assignment",
        attribute_auto_name="Is {material} assigned",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    "FACE_IS_MATERIAL_SLOT_ASSIGNED": ObjectDataSource(
        enum_gui_friendly_name="Boolean From Material Slot Assignment ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Boolean From Material Slot Assignment",
        enum_gui_description="Create boolean face attribute from material slot assignment",
        attribute_auto_name="Is {material_slot} slot assigned",
        attribute_domain_on_default='FACE',
        domains_supported=['FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=True,
        valid_data_sources = ['MESH']
    ),

    # FACE CORNER ONLY
    "INSERT_NEWLINE_FACE_CORNER": None,
    
    "SPLIT_NORMALS": ObjectDataSource(
        enum_gui_friendly_name="Split Normals ⁻ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "Split Normals",
        enum_gui_description="Create vector face corner attribute from split normals",
        attribute_auto_name="Split Normals",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "CORNER_TANGENT": ObjectDataSource(
        enum_gui_friendly_name="Tangent ⁻ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "Tangent",
        enum_gui_description="Create vector face corner attribute from tangent",
        attribute_auto_name="Tangent",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "CORNER_BITANGENT": ObjectDataSource(
        enum_gui_friendly_name="Bitangent ⁻ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "Bitangent",
        enum_gui_description="Create vector face corner attribute from bitangent",
        attribute_auto_name="Bitangent",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "CORNER_BITANGENT_SIGN": ObjectDataSource(
        enum_gui_friendly_name="Bitangent Sign ⁻ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "Bitangent Sign",
        enum_gui_description="Create float face corner attribute from corner bitangent sign",
        attribute_auto_name="Bitangent Sign",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='FLOAT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "CORNER_EDGE_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Corner Edge Index ⁻ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "Face Corner Edge Index",
        enum_gui_description="Create integer face corner attribute from assigned edge index",
        attribute_auto_name="Face Corner Edge Index",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    "CORNER_VERTEX_INDEX": ObjectDataSource(
        enum_gui_friendly_name="Face Corner Vertex Index ⁻ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "Face Corner Vertex Index",
        enum_gui_description="Create integer face corner attribute from assigned vertex index",
        attribute_auto_name="Face Corner Vertex Index",
        attribute_domain_on_default='CORNER',
        domains_supported=['CORNER'],
        data_type='INT',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH']
    ),

    # "INSERT_SEPARATOR_SPECIAL": None,

    # # SPECIAL
    
    # data len = = loops for both, idk how to proceed with this 

    # "SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataSource(
    #     enum_gui_friendly_name="Selected UV Vertices ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if enhanced_enum_titles else "Selected UV Vertices (UV Editor)",
    #     enum_gui_description="Create boolean vertex attribute from selected vertices in UV Editor",
    #     attribute_auto_name="Selected {uvmap} UV Vertices",
    #     attribute_domain_on_default='POINT',
    #     domains_supported=['POINT'],
    #     data_type='BOOLEAN',
    #     min_blender_ver=None,
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['MESH']
    # ),

    # "SELECTED_EDGES_IN_UV_EDITOR": ObjectDataSource(
    #     enum_gui_friendly_name="Selected UV Edges ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if enhanced_enum_titles else "Selected UV Edges (UV Editor)",
    #     enum_gui_description="Create boolean edge attribute from selected edges in UV Editor",
    #     attribute_auto_name="Selected {uvmap} UV Edges",
    #     attribute_domain_on_default='EDGE',
    #     domains_supported=['EDGE'],
    #     data_type='BOOLEAN',
    #     min_blender_ver=None,
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['MESH']
    # ),

}

# Defines an object data target, like position, seams or other
ObjectDataTarget = namedtuple("MeshDataSource", [
    "enum_gui_friendly_name",
    "enum_gui_description",
    "domains_supported",
    "data_type",
    "min_blender_ver",
    "unsupported_from_blender_ver",
])

# Contains object data sources
#
# "INSERT_SEPARATOR_": None,         will add a separator in enum menu
# "INSERT_NEWLINE_": None,           will add a new column in enum menu
#
# Formattable string values:
# NONE, FORMAT DOES NOT PLAY NICE WITH ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ STRINGS
object_data_targets = {

    #POINT EDGE FACE
    "TO_VISIBLE": ObjectDataTarget(
        enum_gui_friendly_name="To Visible In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Visible In Edit Mode",
        enum_gui_description="Convert this attribute to visible in edit mode",
        
        domains_supported=['POINT', 'EDGE', 'FACE'],
        data_type='BOOLEAN',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),

    "TO_HIDDEN": ObjectDataTarget(
            enum_gui_friendly_name="To Hidden In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Hidden In Edit Mode",
            enum_gui_description="Convert this attribute to hidden in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_SELECTED": ObjectDataTarget(
            enum_gui_friendly_name="To Selected In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Selected In Edit Mode",
            enum_gui_description="Convert this attribute to selected in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_NOT_SELECTED": ObjectDataTarget(
            enum_gui_friendly_name="To Not Selected In Edit Mode ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Not Selected In Edit Mode",
            enum_gui_description="Convert this attribute to selected in edit mode",
            
            domains_supported=['POINT', 'EDGE', 'FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    # # VERTEX EDGE
    "INSERT_SEPARATOR_VE": None,  

    
    "TO_MEAN_BEVEL_WEIGHT": ObjectDataTarget(
            enum_gui_friendly_name="To Bevel Weight ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ" if enhanced_enum_titles else "To Not Selected In Edit Mode",
            enum_gui_description="Convert this attribute to bevel weight",
            
            domains_supported=['POINT', 'EDGE'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_MEAN_CREASE": ObjectDataTarget(
            enum_gui_friendly_name="To Mean Crease ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ" if enhanced_enum_titles else "To Mean Crease",
            enum_gui_description="Convert this attribute to mean crease",
            
            domains_supported=['POINT', 'EDGE'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    # VERTEX CORNER
    "INSERT_SEPARATOR_VC": None,  

    'TO_SPLIT_NORMALS': ObjectDataTarget(
            enum_gui_friendly_name="To Split Normals ⁻ ᵛᵉʳᵗᵉˣ ᶜᵒʳⁿᵉʳ" if enhanced_enum_titles else "To Split Normals",
            enum_gui_description="Convert this attribute to split normals",
            
            domains_supported=['POINT', 'CORNER'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    # VERTEX
    "INSERT_NEWLINE_V": None, 

    "TO_POSITION": ObjectDataTarget(
            enum_gui_friendly_name="To Position ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "To Position",
            enum_gui_description="Convert this attribute to mesh positon",
            
            domains_supported=['POINT'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_SCULPT_MODE_MASK": ObjectDataTarget(
            enum_gui_friendly_name="To Sculpt Mode Mask ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "To Sculpt Mode Mask",
            enum_gui_description="Convert this attribute to sculpt mode mask",
            
            domains_supported=['POINT'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_VERTEX_GROUP": ObjectDataTarget(
            enum_gui_friendly_name="To Vertex Group  ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "To Vertex Group",
            enum_gui_description="Convert this attribute to vertex group",
            
            domains_supported=['POINT'],
            data_type='FLOAT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),
        
    "TO_SHAPE_KEY": ObjectDataTarget(
            enum_gui_friendly_name="To Shape Key ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "To Shape Key",
            enum_gui_description="Convert this attribute to mesh shape key",
            
            domains_supported=['POINT'],
            data_type='FLOAT_VECTOR',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_VERTEX_GROUP_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="To Vertex Group Index ⁻ ᵛᵉʳᵗᵉˣ" if enhanced_enum_titles else "To Vertex Group Index",
            enum_gui_description="Convert this attribute to vertex group index for use with armatures",
            domains_supported=['POINT'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    # EDGE
    "INSERT_SEPARATOR_E": None, 

    "TO_SEAM": ObjectDataTarget(
            enum_gui_friendly_name="To Seams ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "To Seams",
            enum_gui_description="Convert this attribute to edge seams",
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_SHARP": ObjectDataTarget(
            enum_gui_friendly_name="To Sharp ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "To Sharp",
            enum_gui_description="Convert this attribute to edge sharps",         
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_FREESTYLE_MARK": ObjectDataTarget(
            enum_gui_friendly_name="To Freestyle Mark ⁻ ᵉᵈᵍᵉ" if enhanced_enum_titles else "To Freestyle Mark",
            enum_gui_description="Convert this attribute to edge freestyle mark",
            
            domains_supported=['EDGE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    # FACE
    "INSERT_NEWLINE_F": None, 

    "TO_FACE_SHADE_SMOOTH": ObjectDataTarget(
            enum_gui_friendly_name="To Face Shade Smooth ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Face Shade Smooth",
            enum_gui_description="Convert this attribute to face shade smooth",
            
            domains_supported=['FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_FACE_MAP": ObjectDataTarget(
            enum_gui_friendly_name="To Face Map ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Face Map",
            enum_gui_description="Convert this attribute to face map",
            
            domains_supported=['FACE'],
            data_type='BOOLEAN',
            min_blender_ver=None,
            unsupported_from_blender_ver=(4,0),
        ),

    "TO_SCULPT_MODE_FACE_SETS": ObjectDataTarget(
            enum_gui_friendly_name="To Sculpt Mode Face Sets ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Sculpt Mode Face Sets",
            enum_gui_description="Convert this attribute to Sculpt Mode Face Sets",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_MATERIAL_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="To Material Index ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "To Material Index",
            enum_gui_description="Convert this attribute to Material Index",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=None,
        ),

    "TO_FACE_MAP_INDEX": ObjectDataTarget(
            enum_gui_friendly_name="Set Face Map Index ⁻ ᶠᵃᶜᵉ" if enhanced_enum_titles else "Set Face Map Index",
            enum_gui_description="Convert this attribute to set face map index",
            
            domains_supported=['FACE'],
            data_type='INT',
            min_blender_ver=None,
            unsupported_from_blender_ver=(4,0),
        ),    

    # # SPECIAL
    # "INSERT_SEPARATOR_SPECIAL": None, 

    # "TO_SELECTED_VERTICES_IN_UV_EDITOR": ObjectDataTarget(
    #         enum_gui_friendly_name="Selected UV Vertices ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if enhanced_enum_titles else "Selected UV Vertices (UV Editor)",
    #         enum_gui_description="Convert this attribute to selected vertices in UV Editor Panel",
    #         domains_supported=['POINT'],
    #         data_type='BOOLEAN',
    #         min_blender_ver=None,
    #         unsupported_from_blender_ver=None,
    #     ),    
    
    # "TO_SELECTED_EDGES_IN_UV_EDITOR": ObjectDataTarget(
    #         enum_gui_friendly_name="Selected UV Edges ⁻ ᵘᵛ ᵉᵈᶦᵗᵒʳ" if enhanced_enum_titles else "Selected UV Edges (UV Editor)",
    #         enum_gui_description="Convert this attribute to selected edges in UV Editor Panel",
    #         domains_supported=['EDGE'],
    #         data_type='BOOLEAN',
    #         min_blender_ver=None,
    #         unsupported_from_blender_ver=None,
    #     ),    


}

AttributeDataType = namedtuple("AttributeDataType", [
    "friendly_name",
    "min_blender_ver",
    "unsupported_from_blender_ver",
])

attribute_data_types = {
    "FLOAT": AttributeDataType(
        friendly_name="Float",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "INT": AttributeDataType(
        friendly_name="Integer",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "INT8": AttributeDataType(
        friendly_name="8-bit Integer",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "FLOAT_VECTOR": AttributeDataType(
        friendly_name="Vector",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "FLOAT_COLOR": AttributeDataType(
        friendly_name="Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "BYTE_COLOR": AttributeDataType(
        friendly_name="Byte Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "STRING": AttributeDataType(
        friendly_name="String",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "BOOLEAN": AttributeDataType(
        friendly_name="Boolean",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "FLOAT2": AttributeDataType(
        friendly_name="Vector 2D",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
    ),
    "INT32_2D": AttributeDataType(
        friendly_name='2D Integer Vector',
        min_blender_ver=(3,6,0),
        unsupported_from_blender_ver=None,
    ),
    "QUATERNION": AttributeDataType(
        friendly_name='Quaternion',
        min_blender_ver=(4,0,0),
        unsupported_from_blender_ver=None,
    ),
}

AttributeDomain = namedtuple("AttributeDomain", [
    "friendly_name",
    "min_blender_ver",
    "unsupported_from_blender_ver",
])

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

class MAME_PropValues(bpy.types.PropertyGroup):
    """
    All editable props in GUI
    """
    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_bool: bpy.props.BoolProperty(name="Boolean Value", default=True)
    val_vector2d: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if get_blender_support(attribute_data_types['INT32_2D'].min_blender_ver, attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))
    if get_blender_support(attribute_data_types['QUATERNION'].min_blender_ver, attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
        val_quaternion: bpy.props.FloatVectorProperty(name="Quaternion Value", size=4, default=(1.0,0.0,0.0,0.0))

    face_corner_spill: bpy.props.BoolProperty(name="Face Corner Spill", default = False, description="Allow setting value to nearby corners of selected vertices or limit it only to selected face")

    val_random_toggle: bpy.props.BoolProperty(name="Randomize", default=False)
    val_random_min_float:bpy.props.FloatProperty(name="Float Random Min", default=0.0)
    val_random_max_float:bpy.props.FloatProperty(name="Float Random Max", default=1.0)
    val_random_min_int:bpy.props.IntProperty(name="Integer Random Min", default=0)
    val_random_max_int:bpy.props.IntProperty(name="Integer Random Max", default=100)
    val_random_min_int8:bpy.props.IntProperty(name="8-Bit Integer Random Min", default=0, min=0, max=127)
    val_random_max_int8:bpy.props.IntProperty(name="8-Bit Integer Random Max", default=127, min=0, max=127)
    val_random_min_vec2d:bpy.props.FloatVectorProperty(name="Vector 2D Random Min", size=2, default=(0.0,0.0))
    val_random_max_vec2d:bpy.props.FloatVectorProperty(name="Vector 2D Random Max", size=2, default=(1.0,1.0))
    val_random_min_vec3d:bpy.props.FloatVectorProperty(name="Vector Random Min", size=3, default=(0.0,0.0,0.0))
    val_random_max_vec3d:bpy.props.FloatVectorProperty(name="Vector Random Max", size=3, default=(0.0,0.0,0.0))
    
    color_rand_type: bpy.props.EnumProperty(
        name="Color Randomize Type",
        description="Select an option",
        items=[
            
            ("HSV", "Randomize HSV Values", "Randomize HSV Values"),
            ("RGB", "Randomize RGB Values", "Randomize RGB Values"),
        ],
        default="HSV"
    )
    
    val_random_hue_toggle: bpy.props.BoolProperty(name="Randomize Hue", default=True)
    val_random_saturation_toggle: bpy.props.BoolProperty(name="Randomize Saturation", default=True)
    val_random_colorvalue_toggle: bpy.props.BoolProperty(name="Randomize Value", default=True)

    val_random_r_toggle: bpy.props.BoolProperty(name="Randomize Red", default=True)
    val_random_g_toggle: bpy.props.BoolProperty(name="Randomize Green", default=True)
    val_random_b_toggle: bpy.props.BoolProperty(name="Randomize Blue", default=True)

    val_random_min_color:bpy.props.FloatVectorProperty(name="Color Random Max", size=3, default=(0.0,0.0,0.0))
    val_random_max_color:bpy.props.FloatVectorProperty(name="Color Random Max", size=3, default=(1.0,1.0,1.0))

    val_random_colorvalue_toggle: bpy.props.BoolProperty(name="Randomize Alpha", default=True)
    val_random_min_alpha:bpy.props.FloatProperty(name="Float Random Min", default=0.0)
    val_random_max_alpha:bpy.props.FloatProperty(name="Float Random Min", default=1.0)