
"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Volatile data, variables and other
"""

import bpy
from . import func
from . import etc
from . import static_data 


class MAME_PropValues(bpy.types.PropertyGroup):
    """
    The values stored per-object
    """

    # Assign attribute value in edit mode entries
    # -------------------------------------------------
    # val_datatype, datatype is in lower case eg attribute.data_type.lower()
    
    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_float_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_boolean: bpy.props.BoolProperty(name="Boolean Value", default=True)
    val_float2: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    if etc.get_blender_support(static_data.attribute_data_types['INT8'].min_blender_ver, static_data.attribute_data_types['INT8'].unsupported_from_blender_ver):
        val_int8: bpy.props.IntProperty(name="8-bit Integer Value", min=-128, max=127, default=0)
    val_float_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_byte_color: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if etc.get_blender_support(static_data.attribute_data_types['INT32_2D'].min_blender_ver, static_data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))
    if etc.get_blender_support(static_data.attribute_data_types['QUATERNION'].min_blender_ver, static_data.attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
        val_quaternion: bpy.props.FloatVectorProperty(name="Quaternion Value", size=4, default=(1.0,0.0,0.0,0.0))
    # if etc.get_blender_support(static_data.attribute_data_types['FLOAT4X4'].min_blender_ver, static_data.attribute_data_types['FLOAT4X4'].unsupported_from_blender_ver):
    #     val_float4x4: bpy.props.FloatVectorProperty(name="4x4 Matrix Value", size=16, default=(1.0,0.0,0.0,0.0, 0.0,1.0,0.0,0.0, 0.0,0.0,1.0,0.0, 0.0,0.0,0.0,1.0))

    # Assign/select options
    # -------------------------------------------------

    face_corner_spill: bpy.props.BoolProperty(name="Face Corner Spill", default = False, description="Allow setting value to nearby corners of selected vertices or limit it only to selected face")
    val_select_non_zero_toggle: bpy.props.BoolProperty(name="Select Non-Zero", default=True, description='Non-zero Select\n\nON: Select domains with non-zero, non-empty, non-black and True values \nOFF: Select domains containing the value in the input field')
    val_select_casesensitive: bpy.props.BoolProperty(name="Case sensitive", default=False, description='Select only matching case')
    val_enable_slow_ops: bpy.props.BoolProperty(name="Allow Slow Operations", default=False, description='Enable operations that can freeze blender')
class MAME_GUIPropValues(bpy.types.PropertyGroup):
    """
    The values stored in blender UI
    """

    # Sculpt mode Masks Manager hidden setting to show all attributes in Masks Manager
    qops_sculpt_mode_attribute_show_unsupported: bpy.props.BoolProperty(name="Show all attributes", default=False)

    # Sculpt mode Masks Manager hidden setting to disable normalization of masks when applying them
    qops_sculpt_mode_mask_normalize: bpy.props.BoolProperty(name="Normalize Mask Value", description="Keep the mask value in 0.0 to 1.0 range", default=True)

    # Sculpt Mode Masks Manager mask/face sets toggle enums
    def get_enum_sculpt_mode_attribute_mode_toggle_enum(self, context):
        return [("MASK", "Mask", "Use attribute to modify mask", 'MOD_MASK', 0),
                    ("FACE_SETS", "Face Sets", "Use attribute to modify Face Maps", "FACE_MAPS", 1),]

    # Sculpt Mode Masks Manager mask/face sets toggle
    enum_sculpt_mode_attribute_mode_toggle: bpy.props.EnumProperty(
        name="Mode Toggle",
        description="Select an option",
        items=get_enum_sculpt_mode_attribute_mode_toggle_enum,
    )

    # List of all attributes used in "To Mesh Data" to show all attributes in an  UIList
    to_mesh_data_attributes_list: bpy.props.CollectionProperty(type = etc.AttributeListItem)

    # Active attribute selected in UILIst in "To Mesh Data" menu when converting multiple attributes at once
    to_mesh_data_attributes_list_active_id: bpy.props.IntProperty(name="Mesh Attribute", default=0)
    
    # Whether to show "Same as target" button in filter list
    b_attributes_uilist_show_same_as_target_filter: bpy.props.BoolProperty(name="Same As Target Filter", default=True)
    
    # Whether to tint red all data types and domains that do not fit the active attribute type
    b_attributes_uilist_highlight_different_attrib_types: bpy.props.BoolProperty(name="Same As Target Filter", default=True)
        
    # Sculpt mode bar
    # -------------------------------------------------

    # Source attribute dropdown menu to use as a mask or face map
    enum_sculpt_mode_attribute_selector: bpy.props.EnumProperty(
        name="Source Attribute",
        description="Select an option",
        items=func.get_sculpt_mode_attributes_enum
    )

    # Fix to make sure the source attribute dropdown menu always has a correct enum in it 
    def validify_enums(self):
        sm_attribs = [e[0] for e in func.get_sculpt_mode_attributes_enum(self, bpy.context)]

        if self.enum_sculpt_mode_attribute_selector not in sm_attribs:
            self.enum_sculpt_mode_attribute_selector = sm_attribs[len(sm_attribs)-1]

    # UI Pinning support
    # -------------------------------------------------
    last_object_refs: bpy.props.CollectionProperty(name="Collection of references to Object Datablock by Mesh Datatblock", type = etc.PropPanelPinMeshLastObject) 
classes = [
    MAME_PropValues,
    MAME_GUIPropValues,
]

def register():
    "Register classes. Exception handing in init"
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    "Unregister classes. Exception handing in init"
    for c in classes:
        bpy.utils.unregister_class(c)
