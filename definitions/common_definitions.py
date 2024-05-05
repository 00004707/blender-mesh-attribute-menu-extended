"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Commonnly used definions, enums and classes

"""
 
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
            icon="GEOMETRY_NODES" if util_func.get_blender_support(minver=(3,3,0)) else "NODE"
        ),
    "an_AnimationNodeTree": NodeEditor(
            gui_friendly_name="Animation Nodes Editor",
            gui_description="Animation Nodes Editor",
            enum=ENodeEditor.ANIMATION_NODES,
            icon="ONIONSKIN_ON"
        ), #OUTLINER_DATA_POINTCLOUD
}

# Defines the type of GUI input to show 
class EDataTypeGuiPropType(Enum):
    SCALAR = 0          #int float int8
    VECTOR = 1          #float vector, vector 2d, quaternion
    COLOR  = 3          # float color byte color
    STRING = 4          # string
    BOOLEAN = 5         # boolean

# Defines all types of external assets to load
class EExternalAssetType(Enum):
    NODEGROUP = 0

# All supported modes for converting attributes to different type
attribute_convert_modes = [("GENERIC", "Generic", ""),
               ("VERTEX_GROUP", "Vertex Group", ""),]


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

