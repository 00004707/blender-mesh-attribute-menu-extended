from func.enum_func import get_attribute_data_types
import func.util_func
from modules import LEGACY_etc, LEGACY_static_data


def get_dynamic_all_attribute_values_property_group_definition(b_ignore_safe_limits:bool = False, class_name:str = "AttributeDataTypePropertyGroup"):
    """Gets definition for a class that contains all possible attribute values, as properties.
    The class has to be registered and executed in exec()

    Args:
        b_ignore_safe_limits (bool, optional): Implement min max on properties. Defaults to False.
        class_name (str, optional): Class name. Defaults to "AttributeDataTypePropertyGroup".

    """
    dts = get_attribute_data_types()

    # Create jank
    code = f"class {class_name}(bpy.types.PropertyGroup):\n"

    for dt in dts:
        prop = LEGACY_static_data.attribute_data_types[dt]

        # Check if supported by current blender version
        if func.util_func.get_blender_support(prop.min_blender_ver, prop.unsupported_from_blender_ver):
            name = str("val_" + dt.lower())

            code += f'  {name}: bpy.props.{prop.bpy_props_class.__name__}('
            code += f'name="{prop.friendly_name} Value"'

            # For string type
            default = str(prop.default_value)

            if default == '':
                code += f', default=""'
            else:
                code += f', default={prop.default_value}'

            # Try adding vector size
            try:
                if default == '':
                    raise TypeError # skip string

                vector_size = len(prop.default_value)
                code += f', size={str(vector_size)}'
            except TypeError:
                pass

            # Try adding vector type
            if prop.bpy_props_vector_subtype is not None:
                code += f', subtype="{str(prop.bpy_props_vector_subtype)}"'

            if not b_ignore_safe_limits:
                # Try adding min
                if prop.prop_value_min is not None:
                    code += f', min={str(prop.prop_value_min)}'
                # Try adding max
                if prop.prop_value_max is not None:
                    code += f', max={str(prop.prop_value_min)}'

            code += ')\n'

    return code


def get_all_attribute_data_types_property_group(b_ignore_safe_limits:bool = False, class_name:str = "AttributeDataTypePropertyGroup"):
    """Returns a PropertyGroup class containing all compatible and available data types of an attribute

    Args:
        b_ignore_safe_limits (bool, optional): Removes min and max from attribute declarations. Defaults to False.

    Returns:
        class: PropertyGroup
    """
    code_locals = {}

    # Create jank
    code = get_dynamic_all_attribute_values_property_group_definition(b_ignore_safe_limits, class_name)

    # Register class
    code += '\nbpy.utils.register_class(AttributeDataTypePropertyGroup)'
    code += '\nc = AttributeDataTypePropertyGroup'

    exec(code, None, code_locals)

    c = code_locals['c']
    LEGACY_etc.save_dynamically_created_class(c)

    return code_locals['c']


def get_all_attribute_datatype_property_group_value(prop_group, data_type:str):
    """Gets value of property of datatype in class created by get_all_attribute_data_types_property_group

    Args:
        prop_group (str): property group
        data_type (str): data type

    Returns:
        value: requested value
    """
    return getattr(prop_group, str("val_" + data_type.lower()))


def set_all_attribute_datatype_property_group_value(prop_group, data_type:str, value):
    """Sets the value of property of datatype in class created by get_all_attribute_data_types_property_group

    Args:
        prop_group (str): property group
        data_type (str): data type
        value: value to set

    """
    setattr(prop_group, str("val_" + data_type.lower()), value)


def get_property_name_by_data_type_in_all_attribute_property_group(data_type):
    return str("val_"+ data_type.lower())