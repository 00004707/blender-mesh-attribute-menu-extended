
import bpy
from . import func
from . import etc
from . import static_data 



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
    if etc.get_blender_support(static_data.attribute_data_types['INT8'].min_blender_ver, static_data.attribute_data_types['INT8'].unsupported_from_blender_ver):
        val_int8: bpy.props.IntProperty(name="8-bit Integer Value", min=-128, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    if etc.get_blender_support(static_data.attribute_data_types['INT32_2D'].min_blender_ver, static_data.attribute_data_types['INT32_2D'].unsupported_from_blender_ver):
        val_int32_2d: bpy.props.IntVectorProperty(name="2D Integer Vector Value", size=2, default=(0,0))
    if etc.get_blender_support(static_data.attribute_data_types['QUATERNION'].min_blender_ver, static_data.attribute_data_types['QUATERNION'].unsupported_from_blender_ver):
        val_quaternion: bpy.props.FloatVectorProperty(name="Quaternion Value", size=4, default=(1.0,0.0,0.0,0.0))

    # Assign/select options
    # -------------------------------------------------

    face_corner_spill: bpy.props.BoolProperty(name="Face Corner Spill", default = False, description="Allow setting value to nearby corners of selected vertices or limit it only to selected face")
    val_select_non_zero_toggle: bpy.props.BoolProperty(name="Select Non-Zero", default=True, description='Select buttons will select/deselect "non-zero" values instead')
    
    # Sculpt mode bar
    # -------------------------------------------------

    enum_sculpt_mode_attribute_selector: bpy.props.EnumProperty(
        name="Source Attribute",
        description="Select an option",
        items=func.get_sculpt_mode_attributes_enum
    )

    enum_sculpt_mode_attribute_mode_toggle: bpy.props.EnumProperty(
        name="Mode Toggle",
        description="Select an option",
        items=[("MASK", "Mask", "Use attribute to modify mask", 'MOD_MASK', 0),
                ("FACE_SETS", "Face Set", "Use attribute to modify Face Maps", "FACE_MAPS", 1),],
        default="MASK",
    )

qops_sculpt_mode_attribute_show_unsupported: bpy.props.BoolProperty(name="Show all attributes", default=False)