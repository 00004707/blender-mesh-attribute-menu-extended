"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Attribute Data Type Class Definition

"""



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
    FLOAT4X4 = 11







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
    "bpy_props_class",                          # bpy.props class for creating properties
    "bpy_props_vector_subtype",                 # Vector subtype, eg. COLOR (if applicable)
    "prop_value_min",                           # The absolute minimum random value for this datatype in property (if applicable)
    "prop_value_max",                           # The absolute maximum random value for this datatype in property (if applicable)
    "icon",                                     # icon
])

# Defines all supported mesh data types
attribute_data_types = {
    # Do not use ''
    "FLOAT": AttributeDataType(
        friendly_name="Float",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=None,
        gui_prop_subtype=EDataTypeGuiPropType.SCALAR,
        bpy_ops_set_attribute_param_name="value_float",
        default_value=0.0,
        compatible_node_editors=[ENodeEditor.GEOMETRY_NODES, ENodeEditor.SHADER],#, ENodeEditor.ANIMATION_NODES],
        geonodes_attribute_node_datatype="FLOAT",
        animnodes_attribute_node_datatype="FLOAT",
        default_randomize_value_min=0.0,
        default_randomize_value_max=1.0,
        prop_value_max=None,
        prop_value_min=None,
        cast_type=float,
        large_capacity_vector=False,
        large_capacity_vector_size=0,
        large_capacity_vector_size_height=0,
        large_capacity_vector_size_width=0,
        bpy_props_class=bpy.props.FloatProperty,
        bpy_props_vector_subtype=None,
        icon="IPO_EASE_IN_OUT"
    ),
    "INT": AttributeDataType(
        friendly_name="Integer",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
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
        bpy_props_class=bpy.props.IntProperty,
        bpy_props_vector_subtype=None,
        prop_value_max=None,
        prop_value_min=None,
        icon="LONGDISPLAY"
    ),
    "INT8": AttributeDataType(
        friendly_name="8-bit Integer",
        min_blender_ver=(3,2,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
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
        bpy_props_class=bpy.props.IntProperty,
        bpy_props_vector_subtype=None,
        prop_value_max=127,
        prop_value_min=0,
        icon="MODIFIER"
    ),
    "FLOAT_VECTOR": AttributeDataType(
        friendly_name="Vector",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["X","Y","Z"],
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
        bpy_props_class=bpy.props.FloatVectorProperty,
        bpy_props_vector_subtype=None,
        prop_value_max=None,
        prop_value_min=None,
        icon="OUTLINER_DATA_EMPTY"
    ),
    "FLOAT_COLOR": AttributeDataType(
        friendly_name="Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["R","G","B","A"],
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
        bpy_props_class=bpy.props.FloatVectorProperty,
        bpy_props_vector_subtype='COLOR',
        prop_value_min=0.0,
        prop_value_max=1.0,
        icon="NODE_MATERIAL"
    ),
    "BYTE_COLOR": AttributeDataType(
        friendly_name="Byte Color",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["R","G","B","A"],
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
        bpy_props_class=bpy.props.FloatVectorProperty,
        bpy_props_vector_subtype='COLOR',
        prop_value_min=0.0,
        prop_value_max=1.0,
        icon="NODE_MATERIAL"
    ),
    "STRING": AttributeDataType(
        friendly_name="String",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["REVERSE_ORDER"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
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
        bpy_props_class=bpy.props.StringProperty,
        bpy_props_vector_subtype=None,
        prop_value_min=None,
        prop_value_max=None,
        icon="FILE_FONT"
    ),
    "BOOLEAN": AttributeDataType(
        friendly_name="Boolean",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["NOT"],
        supported_comparison_modes=["EQ","NEQ"],
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
        bpy_props_class=bpy.props.BoolProperty,
        bpy_props_vector_subtype=None,
        prop_value_min=None,
        prop_value_max=None,
        icon="CHECKBOX_HLT"
    ),
    "FLOAT2": AttributeDataType(
        friendly_name="Vector 2D",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["X","Y"],
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
        bpy_props_class=bpy.props.FloatVectorProperty,
        bpy_props_vector_subtype=None,
        prop_value_min=None,
        prop_value_max=None,
        icon="SELECT_SET"
    ),
    "INT32_2D": AttributeDataType(
        friendly_name="2D Integer Vector",
        min_blender_ver=(3,6,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["X","Y"],
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
        bpy_props_class=bpy.props.IntVectorProperty,
        bpy_props_vector_subtype=None,
        prop_value_min=None,
        prop_value_max=None,
        icon="SELECT_SET"
    ),
    "QUATERNION": AttributeDataType(
        friendly_name="Quaternion",
        min_blender_ver=(4,0,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["MULTIPLY_MINUS_ONE", "ADD_TO_MINUS_ONE", "SUBTRACT_FROM_ONE"],
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["X","Y","Z","W"],
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
        bpy_props_class=bpy.props.FloatVectorProperty,
        bpy_props_vector_subtype=None,
        prop_value_min=-1.0,
        prop_value_max=1.0,
        icon="DRIVER_ROTATIONAL_DIFFERENCE"
    ),
    "FLOAT4X4": AttributeDataType(
        friendly_name="4x4 Matrix",
        min_blender_ver=(4,2,0),
        unsupported_from_blender_ver=None,
        supported_attribute_invert_modes=["INVERSE_OF_A_MATRIX"], 
        supported_comparison_modes=["EQ","NEQ","EQORGR","EQORLS","GR","LS"],
        vector_subelements_names=["X1","Y1","Z1","W1","X2","Y2","Z2","W2","X3","Y3","Z3","W3","X4","Y4","Z4","W4"],
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
        bpy_props_class=bpy.props.FloatVectorProperty,
        bpy_props_vector_subtype=None,
        prop_value_min=-1.0,
        prop_value_max=1.0,
        icon="LIGHTPROBE_VOLUME"
                                                               
    ),
}
