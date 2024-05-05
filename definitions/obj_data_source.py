"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Object Data Source Class Definition

"""

# TODO CONVERT TO CLASS&OBJECTS

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
    CURVES = 12
    POINT_DATA = 13

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
    #"using_attribute_data_since"                                # If the object data has been moved to special attribute in some blender version, this has to specify since when
])

# Contains object data sources
object_data_sources = {
    # Formattable string values:
    #   face_map shape_key domain vertex_group material material_slot shape_key_to shape_key_from attribute
    
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

    "ATTRIBUTE": ObjectDataSource(
        enum_gui_friendly_name="Attribute",
        enum_gui_description="Duplicate attribute or create attribute from evaulated attribute",
        attribute_auto_name="{attribute} Attribute",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE'], # Special
        data_type=None, # Special
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['MESH', 'CURVES', 'POINTCLOUD'],
        icon= "OUTLINER_DATA_MESH",
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
        domains_supported=['POINT', 'EDGE', 'FACE','CURVE'],
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

    

    # # CURVES POINT + POINT CLOUD ONLY
    # --------------------------------------

    "RADIUS": ObjectDataSource(
        enum_gui_friendly_name="Radius",
        enum_gui_description="Create radius attribute from curve ppoints",
        attribute_auto_name="Curve Radius",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES', 'POINTCLOUD'],
        icon= "FIXED_SIZE",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "BEZIER_HANDLE_LEFT": ObjectDataSource(
        enum_gui_friendly_name="Bézier Curve Left Handle Position",
        enum_gui_description="Create Bézier Curve Left Handle Position attribute",
        attribute_auto_name="Bézier Curve Left Handle Position",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "TRIA_LEFT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "BEZIER_HANDLE_RIGHT": ObjectDataSource(
        enum_gui_friendly_name="Bézier Curve Right Handle Position",
        enum_gui_description="Create Bézier Curve Right Handle Position attribute",
        attribute_auto_name="Curve Radius",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "TRIA_RIGHT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "BEZIER_HANDLE_TYPE_LEFT": ObjectDataSource(
        enum_gui_friendly_name="Bézier Curve Left Handle Type",
        enum_gui_description="Create Bézier Curve Right Handle Type attribute (8-Bit Integer)",
        attribute_auto_name="Bézier Curve Left Handle Type",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='INT8',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "TRIA_LEFT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "BEZIER_HANDLE_TYPE_RIGHT": ObjectDataSource(
        enum_gui_friendly_name="Bézier Curve Right Handle Type",
        enum_gui_description="Create Bézier Curve Right Handle Type attribute (8-Bit Integer)",
        attribute_auto_name="Bézier Curve Right Handle Type",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='INT8',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "TRIA_RIGHT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "NURBS_WEIGHT": ObjectDataSource(
        enum_gui_friendly_name="NURBS Point Weight",
        enum_gui_description="Create NURBS Point Weight attribute from curve ppoints",
        attribute_auto_name="NURBS Point Weight",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "IPO_EASE_IN_OUT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "TILT": ObjectDataSource(
        enum_gui_friendly_name="Tilt",
        enum_gui_description="Create tilt attribute from curve points",
        attribute_auto_name="Curve Tilt",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "ANIM_DATA",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    "VELOCITY": ObjectDataSource(
        enum_gui_friendly_name="Velocity",
        enum_gui_description="Create velocity attribute from points",
        attribute_auto_name="Velocity",
        attribute_domain_on_default='POINT',
        domains_supported=['POINT'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['POINTCLOUD'],
        icon= "DRIVER_DISTANCE",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.POINT_DATA,
    ),

    # # CURVES CURVE ONLY
    # --------------------------------------

    "POINTS_LENGTH": ObjectDataSource(
        enum_gui_friendly_name="Points Count",
        enum_gui_description="Create points count attribute from points count in a curve",
        attribute_auto_name="Points Count",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "CURVE_SURFACE_UV": ObjectDataSource(
        enum_gui_friendly_name="Surface UV Coordinate",
        enum_gui_description="Create Surface UV Coordinate attribute from selected curves",
        attribute_auto_name="Surface UV Coordinate",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='FLOAT_VECTOR',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "MOD_UVPROJECT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "FIRST_POINT_INDEX": ObjectDataSource(
        enum_gui_friendly_name="First Point Index",
        enum_gui_description="Create first point index attribute from first point index in a curve",
        attribute_auto_name="First Point Index",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "LINENUMBERS_ON",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "SPLINE_RESOLUTION": ObjectDataSource(
        enum_gui_friendly_name="Spline Resolution",
        enum_gui_description="Create Spline Resolution attribute from point count in a curve",
        attribute_auto_name="Spline Resolution",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "IPO_QUINT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "SPLINE_CYCLIC": ObjectDataSource(
        enum_gui_friendly_name="Cyclic",
        enum_gui_description="Create cyclic attribute from cyclic toggle of a curve",
        attribute_auto_name="Cyclic",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='BOOLEAN',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "RECORD_OFF",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    # "SPLINE_SURFACE_NORMAL": ObjectDataSource(
    #     enum_gui_friendly_name="Spline Surface Normal",
    #     enum_gui_description="Create first point index attribute from first point index in a curve",
    #     attribute_auto_name="First Point Index",
    #     attribute_domain_on_default='CURVE',
    #     domains_supported=['CURVE'],
    #     data_type='INT',
    #     min_blender_ver=(3,3),
    #     unsupported_from_blender_ver=None,
    #     batch_convert_support=False,
    #     valid_data_sources = ['CURVES'],
    #     icon= "LINENUMBERS_ON",
    #     quick_ui_exec_type = 'INVOKE_DEFAULT',
    #     ui_category = EObjectDataSourceUICategory.CURVES,
    # ),

    "SPLINE_NORMAL_MODE": ObjectDataSource(
        enum_gui_friendly_name="Curve Normal Mode / Twist Method",
        enum_gui_description="Create Curve Normal Mode attribute",
        attribute_auto_name="Curve Normal Mode",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT8',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "IPO_EASE_IN_OUT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "SPLINE_KNOTS_MODE": ObjectDataSource(
        enum_gui_friendly_name="NURBS Spline Knot Vector Adjustments",
        enum_gui_description="Create NURBS Spline Knot Vector Adjustments attribute NURBS Spline Knot Vector Adjustments in a curve",
        attribute_auto_name="NURBS Spline Knot Vector Adjustments",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT8',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "IPO_EASE_IN_OUT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "SPLINE_NURBS_ORDER": ObjectDataSource(
        enum_gui_friendly_name="NURBS Order in U Direction",
        enum_gui_description="Create NURBS Order in U Direction attribute from NURBS Order in U Direction in a curve",
        attribute_auto_name="NURBS Order in U Direction",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT8',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "IPO_EASE_IN_OUT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

    "SPLINE_TYPE": ObjectDataSource(
        enum_gui_friendly_name="Spline Type",
        enum_gui_description="Create Spline Type attribute from type of spline curve",
        attribute_auto_name="Spline Type",
        attribute_domain_on_default='CURVE',
        domains_supported=['CURVE'],
        data_type='INT8',
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        batch_convert_support=False,
        valid_data_sources = ['CURVES'],
        icon= "IPO_EASE_IN_OUT",
        quick_ui_exec_type = 'INVOKE_DEFAULT',
        ui_category = EObjectDataSourceUICategory.CURVES,
    ),

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