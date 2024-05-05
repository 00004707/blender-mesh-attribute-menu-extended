"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Enum elements usually used in UI dropdown lists

"""
import bpy
from func.attribute_func import get_active_attribute
from func.obj_func import get_object_in_context
from func.util_func import get_domain_icon, get_domain_supported_object_types, get_friendly_domain_name, get_object_type_class_by_str, get_object_type_from_object_data, get_pinned_mesh_object_and_mesh_reference, is_pinned_mesh_used
from modules import LEGACY_static_data
from func.node_func import get_geometry_node_geometry_output_pins
from . import util_func


# Register
# ------------------------------------------
 
classes = []

def register(init_module):

    for c in classes:
        bpy.utils.register_class(c)
    

def unregister(init_module):
    for c in classes:
        bpy.utils.unregister_class(c)


# Data enums
# --------------------------------------------

# individual mesh data enums

def get_face_maps_enum(self, context):
    """Gets all face maps as an enum entries.

    Can be 'NULL' if there is none.

    List entries will be tuples formatted as (INDEX NAME DESC)

    Args:
        context (Reference): Blender Context Reference

    Returns:
        list: List of tuples to be used as enum values
    """

    items = []
    obj, obj_data = get_object_in_context(context)

    # case: object type invalid
    if (type(obj_data) != get_object_type_class_by_str('MESH') or
        # or no data
        not hasattr(obj, 'face_maps') or not len(obj.face_maps)):
            return [("NULL", "No face maps", "", 'ERROR', 0)]


    for face_map in obj.face_maps:
        items.append((str(face_map.index), face_map.name, f"Use {face_map.name} face map "))

    return items


def get_material_slots_enum(self, context):
    """Gets all material slots in active object as an enum entries.

    Can be 'NULL' if there is none.

    List entries will be tuples formatted as (INDEX NAME DESC)

    Args:
        context (Reference): Blender Context Reference

    Returns:
        list: List of tuples to be used as enum values
    """
    items = []
    if is_pinned_mesh_used(context):
        obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
    else:
        obj = bpy.context.active_object

    # case: no data
    if not len(obj.material_slots):
        return [("NULL", "No material slots", "", 'ERROR', 0)]

    for i, material_slot in enumerate(obj.material_slots):
        if material_slot is not None:
            material_slot_name = f"{str(i)}. {material_slot.name if material_slot.name != '' else 'Empty Slot'}"
            items.append((str(i), material_slot_name, f"Use {material_slot_name} material slot"))

    return items


def get_materials_enum(self, context):
    """Gets all materials stored in blend file as an enum entries.

    Can be 'NULL' if there is none.

    List entries will be tuples formatted as (INDEX NAME DESC)

    Args:
        context (Reference): Blender Context Reference

    Returns:
        list: List of tuples to be used as enum values
    """

    items = []

    obj, obj_data = get_object_in_context(context)

    # case: object type invalid
    if (type(obj_data) != get_object_type_class_by_str('MESH') or
        # or no data
        not len(bpy.data.materials)):
        return [("NULL", "No materials", "", 'ERROR', 0)]


    for i, material in enumerate(bpy.data.materials):
        if material is not None:
            items.append((str(i), material.name, f"Use {material.name} material"))

    return items


def get_vertex_groups_enum(self, context):
    """Gets all vertex groups of active object as an enum entries.

    Can be 'NULL' if there is none.

    List entries will be tuples formatted as (INDEX NAME DESC)

    Args:
        context (Reference): Blender Context Reference

    Returns:
        list: List of tuples to be used as enum values
    """

    items = []
    obj, obj_data = get_object_in_context(context)

    # case: object type invalid
    if (type(obj_data) != get_object_type_class_by_str('MESH') or
        # or no data
        not len(obj.vertex_groups)):
        return [("NULL", "No Vertex Groups", "", 'ERROR', 0)]

    for vg in obj.vertex_groups:
        items.append((str(vg.index), vg.name, f"Use {vg.name} vertex group"))

    return items


def get_shape_keys_enum(self, context):
    """Gets all shape keys of active object as an enum entries.

    Can be 'NULL' if there is none.

    List entries will be tuples formatted as (INDEX NAME DESC)

    Args:
        context (Reference): Blender Context Reference

    Returns:
        list: List of tuples to be used as enum values
    """

    items = []
    obj, obj_data = get_object_in_context(context)

    # case: object type invalid
    if (type(obj_data) != get_object_type_class_by_str('MESH') or
        # or no data
        obj.data.shape_keys is None):
        return [("NULL", "No Shape Keys", "", 'ERROR', 0)]

    for i, sk in enumerate(obj.data.shape_keys.key_blocks):
        items.append((str(i), sk.name, f"Use {sk.name} shape key"))

    return items


def get_uvmaps_enum(self, context):
    """Gets all UVMaps of active object as an enum entries.

    Can be 'NULL' if there is none.

    List entries will be tuples formatted as (INDEX NAME DESC)

    Args:
        context (Reference): Blender Context Reference

    Returns:
        list: List of tuples to be used as enum values
    """

    items = []
    obj, obj_data = get_object_in_context(context)

    # case: object type invalid
    if (type(obj_data) != get_object_type_class_by_str('MESH') or
        # or no data
        not len(obj.data.uv_layers)):
        return [("NULL", "No UVMaps", "", 'ERROR', 0)]

    for i, uvmap in enumerate(obj.data.uv_layers):
        items.append((str(i), uvmap.name, f"Use {uvmap.name} UVMap"))

    return items


# extra gui enums

def get_supported_domains_for_selected_datablock_source_enum_entry(self, context):
    """Gets aa list of compatible domains from enum selection in self.domain_data_type, for reading or writing mesh data from object

    Example being mean bevel that can be stored either in edges or vertices.

    [!] self object has to have domain_data_type enum enum property.

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    items = []

    obj, obj_data = get_object_in_context(context)

    if (self.domain_data_type_enum is None
        or self.domain_data_type_enum == ''
        or type(LEGACY_static_data.object_data_sources[self.domain_data_type_enum]) != LEGACY_static_data.ObjectDataSource
        or obj_data is None):
        return [("NULL", "None", "...")]

    # Handle special case for 'ATTRIBUTE' entry
    if self.domain_data_type_enum == 'ATTRIBUTE':
        try:
            if self.enum_attributes is not None:
                domains_supported = [obj.data.attributes[self.enum_attributes].domain]
        except AttributeError:
            return [("NULL", "None", "...")]
    else:
        # Get domains supported by the entry
        domains_supported = LEGACY_static_data.object_data_sources[self.domain_data_type_enum].domains_supported

        # Get domains supported by object type
        real_domains_supported = []
        if type(obj_data) == get_object_type_class_by_str('MESH'):
            for domain in domains_supported:
                if domain in ['POINT', 'EDGE', 'FACE', 'CORNER']:
                    real_domains_supported.append(domain)
            domains_supported = real_domains_supported

        elif type(obj_data) == get_object_type_class_by_str('CURVES'):
            for domain in domains_supported:
                if domain in ['POINT', 'CURVE']:
                    real_domains_supported.append(domain)
            domains_supported = real_domains_supported

        elif type(obj_data) == get_object_type_class_by_str('POINTCLOUD'):
            if 'POINT' in domains_supported:
                domains_supported = ['POINT']
            else:
                domains_supported = []

    if 'POINT' in domains_supported:
        items.append(("POINT", get_friendly_domain_name("POINT", context=context), f"Use {get_friendly_domain_name('POINT', context=context)} domain for data type", get_domain_icon('POINT', context=context), 0))
    if 'EDGE' in domains_supported:
        items.append(("EDGE", get_friendly_domain_name("EDGE"), "Use edge domain for data type", get_domain_icon('EDGE'), 1))
    if 'FACE' in domains_supported:
        items.append(("FACE", get_friendly_domain_name("FACE"), "Use face domain for data type", get_domain_icon('FACE'), 2))
    if 'CORNER' in domains_supported:
        items.append(("CORNER", get_friendly_domain_name("CORNER"), "Use face corner domain for data type", get_domain_icon('CORNER'), 3))
    if 'CURVE' in domains_supported:
        items.append(("CURVE", get_friendly_domain_name("CURVE"), "Use spline domain for data type", get_domain_icon('CURVE'), 4))

    return items


def get_mesh_data_enum_entry_icon(data_item):
    """Sets the enum dropdown list entry icon (create from datablock data).
    Fallbacks to default icon, defined below by domain, if none is set.

    Args:
        data_item (Reference): Reference to namedtuple from data.object_data_sources or data.object_data_targets

    Returns:
        str: The icon string
    """
    # set the default icon based on supported domains, if none is set
    if data_item.icon == "":
        domains = data_item.domains_supported

        # Default for multiple domains entry
        if len(domains) > 1:
            icon = "MATCUBE"

        # Default for point domain entry
        elif domains[0] == "POINT":
            icon = "VERTEXSEL"

        # Default for edge domain entry
        elif domains[0] == "EDGE":
            icon = "EDGESEL"

        # Default for face domain entry
        elif domains[0] == "FACE":
            icon = "FACESEL"

        # Default for face corner domain entry
        elif domains[0] == "CORNER":
            icon = "SNAP_PERPENDICULAR"

        # Default for curve domain entry
        elif domains[0] == "CURVE":
            icon = "OUTLINER_DATA_CURVES" if util_func.get_blender_support((3,3,0)) else "MOD_CURVE"

    # Use specified icon
    else:
        icon = data_item.icon
    return icon


def get_source_data_enum(self, context):
    """Gets enum entries for source data selection to create an attribute from. Contains separators and newlines.

    Args:
        context (Reference): Blender context reference
        include_separators (bool): Whether to include newlines, categories and separators for enum dropdown menu 

    Returns:
        list: List of tuples to be used as enum entries
    """
    e = []

    obj, obj_data = get_object_in_context(context)

    # TODO Needs some prettier handling in UI, if it ever happens
    if obj_data is None:
        return []

    for i, item in enumerate(LEGACY_static_data.object_data_sources):
        if type(LEGACY_static_data.object_data_sources[item]) is not LEGACY_static_data.ObjectDataSource:
            continue
        else:
            minver = LEGACY_static_data.object_data_sources[item].min_blender_ver
            unsupported_from = LEGACY_static_data.object_data_sources[item].unsupported_from_blender_ver
            name = LEGACY_static_data.object_data_sources[item].enum_gui_friendly_name

            # Is entry supported by current blender version
            if (util_func.get_blender_support(minver, unsupported_from) and
                # is object type supported by this entry
                type(obj_data) in [get_object_type_class_by_str(t) for t in LEGACY_static_data.object_data_sources[item].valid_data_sources]):
                    icon = get_mesh_data_enum_entry_icon(LEGACY_static_data.object_data_sources[item])
                    e.append((item, name, LEGACY_static_data.object_data_sources[item].enum_gui_description, icon, i))
    return e


def get_target_data_enum(self, context, include_separators=True):
    """Gets enum entries for target data to store data from attribute. Contains separators and newlines.

    Args:
        context (Reference): Blender context reference
        include_separators (bool): Whether to include newlines and separators for enum dropdown menu 

    Returns:
        list: List of tuples to be used as enum entries
    """
    items = []
    if is_pinned_mesh_used(context):
        obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
    else:
        obj = context.active_object
    active_attrib = obj.data.attributes.active
    inv_data_entry = ("NULL", "[!] No Convertable Data", "")


    for i, entry in enumerate(LEGACY_static_data.object_data_targets):
        if "INSERT_SEPARATOR" in entry and include_separators:
            items.append((None))
        elif "INSERT_NEWLINE" in entry and include_separators:
            items.append(("","","","",i))
        else:
            minver = LEGACY_static_data.object_data_targets[entry].min_blender_ver
            unsupported_from = LEGACY_static_data.object_data_targets[entry].unsupported_from_blender_ver

            if util_func.get_blender_support(minver, unsupported_from):
                icon = get_mesh_data_enum_entry_icon(LEGACY_static_data.object_data_targets[entry])
                #if etc.get_enhanced_enum_titles_enabled():
                name = LEGACY_static_data.object_data_targets[entry].enum_gui_friendly_name
                #else:
                #    name = static_data.object_data_targets[entry].enum_gui_friendly_name_no_special_characters
                item = (entry,
                        name,
                        LEGACY_static_data.object_data_targets[entry].enum_gui_description,
                        icon,
                        i
                        )
                items.append(item)

    # this should not happen but since it is already coded here...
    if not len(items):
        return [inv_data_entry]

    return items


def get_target_data_enum_with_separators(self, context):
    return get_target_data_enum(self, context, include_separators=True)


def get_target_data_enum_without_separators(self, context):
    return get_target_data_enum(self, context, include_separators=False)


def get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context):
    """Gets all compatible domains for selected data type as enum entries. 

    Example being mean bevel that can be stored either in edges or vertices.

    [!] self object has to have data_target_enum enum property.

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """

    domains_supported = LEGACY_static_data.object_data_targets[self.data_target_enum].domains_supported
    items = []

    if 'POINT' in domains_supported:
        items.append(("POINT", "Vertex", "Store this data in vertices"))
    if 'EDGE' in domains_supported:
        items.append(("EDGE", "Edge", "Store this data in edges"))
    if 'FACE' in domains_supported:
        items.append(("FACE", "Face", "Store this data in faces"))
    if 'CORNER' in domains_supported:
        items.append(("CORNER", "Face Corner", "Store this data in face corners"))

    return items


def get_attribute_data_types_enum(self,context):
    """Gets all attribute data types that are supported by current blender version as enum entries

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    l = []
    for item in LEGACY_static_data.attribute_data_types:
        if util_func.get_blender_support(LEGACY_static_data.attribute_data_types[item].min_blender_ver, LEGACY_static_data.attribute_data_types[item].unsupported_from_blender_ver):
            l.append((item, LEGACY_static_data.attribute_data_types[item].friendly_name, ""))
    return l


def get_attribute_data_types():
    """Gets all attribute data types that are supported by current blender version

    Returns:
        list: List of strings
    """
    l = []
    for item in LEGACY_static_data.attribute_data_types:
        if util_func.get_blender_support(LEGACY_static_data.attribute_data_types[item].min_blender_ver, LEGACY_static_data.attribute_data_types[item].unsupported_from_blender_ver):
            l.append(item)
    return l


def get_attribute_domains_enum(self, context):
    """Gets all attribute domains that are supported by current blender version as enum entries

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    l = []
    for item in LEGACY_static_data.attribute_domains:
        if util_func.get_blender_support(LEGACY_static_data.attribute_domains[item].min_blender_ver, LEGACY_static_data.attribute_domains[item].unsupported_from_blender_ver):
            l.append((item, LEGACY_static_data.attribute_domains[item].friendly_name, ""))
    return l


def get_attribute_domains():
    """Gets all attribute domains that are supported by current blender version

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of str
    """

    l = []
    for item in LEGACY_static_data.attribute_domains:
        if util_func.get_blender_support(LEGACY_static_data.attribute_domains[item].min_blender_ver, LEGACY_static_data.attribute_domains[item].unsupported_from_blender_ver):
            l.append(item)
    return l


def get_attribute_invert_modes(self, context):
    """Returns a list of available modes to invert the active attribute, as enum entries.

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """

    dt = context.active_object.data.attributes.active.data_type

    # Check if this data is supported by the addon
    if not dt in LEGACY_static_data.attribute_data_types.keys():
        return[('NULL', "Data Type Unsupported", "")]

    # Get each supported mode to invert this attribute
    l = []
    for item in LEGACY_static_data.attribute_data_types[dt].supported_attribute_invert_modes:
        l.append((item, LEGACY_static_data.attribute_invert_modes[item].friendly_name, LEGACY_static_data.attribute_invert_modes[item].description))

    return l


def get_convert_attribute_modes_enum(self, context):
    """Gets all attribute convert modes

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    return LEGACY_static_data.attribute_convert_modes


def get_attributes_of_type_enum(self, context, data_types = [], domains = ['POINT'], exclude_names = [], case_sensitive_name_filter = True):
    """Gets all attributes by data type to use in enum dropdown.

    Args:
        context (Reference): Blender context reference
        data_types (list of str): All data type names to filter attributes like ['INT', 'FLOAT'], can be empty/None for all
        domians (list of str): All domains of specified domain, can be empty/None for all
    Returns:
        list: List of tuples to be used in enum
    """
    if is_pinned_mesh_used(context):
        obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
    else:
        obj = context.active_object

    enum_entries = []
    inv_data_entry = ("NULL", "[!] No valid attribues", "This list should contain all compatible attributes")

    # Get all if empty or none
    if not data_types or not len(data_types):
        data_types = [dt for dt in LEGACY_static_data.attribute_data_types]

    if not domains or not len(domains):
        domains = [dt for dt in LEGACY_static_data.attribute_domains]

    for attrib in obj.data.attributes:
        if attrib.domain in domains and attrib.data_type in data_types:
            if (attrib.name not in exclude_names and not case_sensitive_name_filter) or (attrib.name.upper() not in [en.upper() for en in exclude_names] and case_sensitive_name_filter):
                enum_entries.append((attrib.name, attrib.name, f"Use {attrib.name} as a source attribute"))

    if not len(enum_entries):
        return [inv_data_entry]

    return enum_entries


def get_vertex_weight_attributes_enum(self, context):
    """Gets all attributes to syue as weight attribute when setting to vertex group index

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    if hasattr(self, 'b_vgindex_weights_only_floats'):
        if not self.b_vgindex_weights_only_floats:
            return get_attributes_of_type_enum(self, context, [], [])
    return get_attributes_of_type_enum(self, context, ['FLOAT'], ['POINT'])


def get_sculpt_mode_attributes_enum(self, context):
    """Gets all attributes to use as sculpt mode mask or face set

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    gui_prop_group = context.window_manager.MAME_GUIPropValues


    if gui_prop_group.qops_sculpt_mode_attribute_show_unsupported:
            return get_attributes_of_type_enum(self, context, [], [])
    else:
        if gui_prop_group.enum_sculpt_mode_attribute_mode_toggle == 'MASK':
            return get_attributes_of_type_enum(self, context, ['FLOAT'], ['POINT'])
        else:# data.enum_sculpt_mode_attribute_mode_toggle == 'FACE_SETS':
            attrs = get_attributes_of_type_enum(self, context, ['INT'], ['FACE'])
            # Remove '.sculpt_face_set' aka current face set
            for e in attrs:
                if e[0] == '.sculpt_face_set':
                    attrs.remove(e)
                    break
            return attrs


def get_texture_coordinate_attributes_enum(self, context):
    return get_attributes_of_type_enum(self, context, ['FLOAT2', 'INT32_2D', 'FLOAT_VECTOR'], exclude_names=['position'])


def get_attributes_enum(self, context):
    return get_attributes_of_type_enum(self, context, domains = [])


def get_attribute_comparison_conditions_enum(data_type):
    l= []
    for mode in LEGACY_static_data.attribute_data_types[data_type].supported_comparison_modes:
        l.append(LEGACY_static_data.attribute_comparison_modes[mode])
    return l


def get_attribute_comparison_conditions_enum_for_property(self,context):
    """All available conditions for attributes that store numeric values

    Args:
        context (Reference): Blender context reference

    Returns:
        list: List of tuples to be used in enum
    """
    if is_pinned_mesh_used(context):
        obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
    else:
        obj = context.active_object
    a = get_active_attribute(obj)

    return get_attribute_comparison_conditions_enum(a.data_type)


def get_attribute_comparison_conditions_enum_strings(self, context):
    return get_attribute_comparison_conditions_enum('STRING')


def get_image_channel_datasource_enum(self, context, index):
    if is_pinned_mesh_used(context):
        obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
    else:
        obj = context.active_object

    sourcetype = getattr(self, f'source_attribute_{index}_datasource_enum')

    l = []

    # enum dirty fix
    if sourcetype == "":
        setattr(self, f'source_attribute_{index}_datasource_enum', 0)
        return []

    l.append(("NULL", "None (Leave as is)", "Leave initial value in this channel intact"))

    if sourcetype == 'ATTRIBUTE':
        for a in obj.data.attributes:
            l.append((a.name, a.name, f"Use value from {a.name}"))
    else:
        for img in bpy.data.images:
            l.append((img.name, img.name, f"Use image channel value from {img.name}"))
    return l


def get_image_channel_datasource_type_enum(self, context):
    l = []
    l.append(("ATTRIBUTE", "Attribute", "Leave initial value in this channel intact"))
    l.append(("IMAGE", "Image", "Leave initial value in this channel intact"))
    return l


def get_image_channel_datasource_vector_subelement_enum(attr_or_tex, texture= False, individual_channels_only = False, alpha_allowed = False):

    # 0 = R X
    # 1 = G Y
    # 2 = B Z
    # 3 = A W
    # 4 = XY
    # 5 = RGB XYZ
    # 6 = RGBA XYZW

    l = []

    if texture:
        if attr_or_tex.alpha_mode != 'NONE' and alpha_allowed and not individual_channels_only:
            l.append(("6", 'RGBA', f"Use RGBA subelements"))

        if not individual_channels_only:
            l.append(("5", 'RGB', f"Use RGB subelements"))

        l.append(("0", 'R', f"Use R subelement"))
        l.append(("1", 'G', f"Use G subelement"))
        l.append(("2", 'B', f"Use B subelement"))
        if attr_or_tex.alpha_mode != 'NONE':
            l.append(("3", 'A', f"Use A subelement"))
        return l
    else:
        gui_proptype = LEGACY_static_data.attribute_data_types[attr_or_tex.data_type].gui_prop_subtype
        if gui_proptype not in [LEGACY_static_data.EDataTypeGuiPropType.COLOR, LEGACY_static_data.EDataTypeGuiPropType.VECTOR]:
            return []

        vec_el = LEGACY_static_data.attribute_data_types[attr_or_tex.data_type].vector_subelements_names

        # get xyzw
        if len(vec_el) == 4 and not individual_channels_only and alpha_allowed:
            x = str(vec_el[0]+vec_el[1]+vec_el[2]+vec_el[3])
            l.append(("6", x, f"Use {x} subelements"))

        # get xyz
        if len(vec_el) >= 3 and not individual_channels_only:
            x = str(vec_el[0]+vec_el[1]+vec_el[2])
            l.append(("5", x, f"Use {x} subelements"))

        # xy for uvmaps
        if len(vec_el) == 2 and not individual_channels_only:
            x = str(vec_el[0]+vec_el[1])
            l.append(("4", x, f"Use {x} subelements"))

        # get x,y,z,w
        for i, el in enumerate(vec_el):
            l.append((str(i), el, f"Use {el} subelement"))

        return l


def get_image_channel_datasource_vector_element_enum(self, context, index, alpha_allowed):
    """The function that detects which of the the XYZW XYZ X Y Z  channel of the attribute 
    to bake to texture should be shown in GUI.

    Can't put it in the operator

    Returns:
        enum list
    """
    src_attribute_enum = getattr(self, f'source_attribute_{index}_enum')

    # enum dirty fix
    if src_attribute_enum == "":
        setattr(self, f'source_attribute_{index}_enum', 0)
        return []
    elif src_attribute_enum == 'NULL':
        return []



    is_texture = getattr(self, f'source_attribute_{index}_datasource_enum') == 'IMAGE'
    only_subelements = self.image_channels_type_enum == 'ALL'
    if is_texture:
        attr_or_img = bpy.data.images[src_attribute_enum]
    else:
        attr_or_img = context.active_object.data.attributes[src_attribute_enum]

    return get_image_channel_datasource_vector_subelement_enum(attr_or_img, is_texture, only_subelements, alpha_allowed)


def get_built_in_attributes_enum(self, context):
    """Gets an enum list of built-in attributes for use with selection menu

    Shows persistent attributes (eg. position) if self has b_show_persistent and is true
    Show real attribute names (eg .sculpt_mask) if self has b_show_persistent and is true

    Returns:
        enum list
    """

    l = []

    b_show_persistent = hasattr(self, 'b_show_persistent') and self.b_show_persistent
    b_show_attribute_names = hasattr(self, 'b_show_attribute_names') and self.b_show_attribute_names

    obj, obj_data = get_object_in_context(context)
    obj_type = get_object_type_from_object_data(obj_data)

    for i, item in enumerate(LEGACY_static_data.built_in_attributes):

        # Determine supported object types for attribute, based on it's supported domains
        supported_obj_types = []
        for dom in LEGACY_static_data.built_in_attributes[item].domains:
            supported_obj_types += get_domain_supported_object_types(dom)

        if (# Check if blender version is supported
            util_func.get_blender_support(LEGACY_static_data.built_in_attributes[item].min_blender_ver,
                                   LEGACY_static_data.built_in_attributes[item].unsupported_from_blender_ver)

            # Check if object type is supported 
            and obj_type in supported_obj_types

            # Hide attributes that cannot be created or persistent
            and (not LEGACY_static_data.built_in_attributes[item].cannot_create or b_show_persistent)):
                name = item if b_show_attribute_names else LEGACY_static_data.built_in_attributes[item].friendly_name
                l.append((item, name, LEGACY_static_data.built_in_attributes[item].description, LEGACY_static_data.built_in_attributes[item].icon, i))
    return l


def get_objects_with_same_datablock_enum(self, context):
    """Returns enum of object names that have same datablock as object in context

    Args:
        context (ref): context

    Returns:
        list: enum list
    """

    x = []
    obj, obj_data = get_object_in_context(context)

    # Active object always on top
    if bpy.context.active_object and bpy.context.active_object.data == obj_data:
        x.append((obj.name, f"{obj.name} (Active Object)", f"Use {obj.name} and it's modifiers to grab data from", 'OBJECT_DATAMODE', 0))

    # Other objects lower
    for i, sceneobj in enumerate([o for o in bpy.context.scene.objects if o.data == obj_data]):
        if sceneobj == bpy.context.active_object:
            continue
        else:
            x.append((sceneobj.name, sceneobj.name, f"Use {sceneobj.name} and it's modifiers to grab data from"))
    return x


def get_objects_in_scene_enum(self, context):
    """Returns enum of object names are in the same scene as active

    Args:
        context (ref): context

    Returns:
        list: enum list
    """
    x = []
    obj, obj_data = get_object_in_context(context)

    # Active object always on top
    if bpy.context.active_object and bpy.context.active_object.data == obj_data:
        x.append((obj.name, f"{obj.name} (Active Object)", f"Use {obj.name}", 'OBJECT_DATAMODE', 0))

    # Other objects lower
    for i, sceneobj in enumerate(bpy.context.scene.objects):
        if sceneobj == bpy.context.active_object:
            continue
        else:
            x.append((sceneobj.name, sceneobj.name, f"Use {sceneobj.name}"))
    return x


def get_meshes_in_scene_enum(self, context):
    """Returns enum of object names are in the same scene as active (meshes only)

    Args:
        context (ref): context

    Returns:
        list: enum list
    """
    x = []
    obj, obj_data = get_object_in_context(context)

    # Active object always on top
    if bpy.context.active_object and bpy.context.active_object.type == 'MESH' and bpy.context.active_object.data == obj_data:
        x.append((obj.name, f"{obj.name} (Active Object)", f"Use {obj.name}", 'OBJECT_DATAMODE', 0))

    # Other objects lower
    for i, sceneobj in enumerate(bpy.context.scene.objects):
        if sceneobj == bpy.context.active_object:
            continue
        elif sceneobj.type == 'MESH':
            x.append((sceneobj.name, sceneobj.name, f"Use {sceneobj.name}"))
    return x


def get_operator_context_enum(self, context):
    """Returns enum for selecting context for opearators to work on

    Args:
        context (ref): context

    Returns:
        list: enum tuple list
    """

    obj, obj_data = get_object_in_context(context)

    try:
        name = obj_data.name
    except Exception:
        name = 'Datablock'

    return [
            ("DATABLOCK", name, "Edit datablock data", "MESH_DATA", 0),
            ("NODEGROUP", "Geometry Nodes", "Edit Geometry Nodes nodegroup", "NODE", 1),
        ]


def get_geometry_nodegroup_node_geometry_outputs_enum(self, context):
    """Returns enum for selecting geometry outputs of a node in geometry nodes node graph
    Only to be used in node editor.

    Args:
        context (ref): context

    Returns:
        list: enum tuple list
    """

    ng = context.space_data.node_tree
    outputs = get_geometry_node_geometry_output_pins(ng.nodes.active)
    x = []
    for i, o in enumerate(outputs):
        x.append((str(i), f"{str(i+1)}.{o.name}", f"Use \"{o.name}\" output"))

    return x

# extra gui enums

