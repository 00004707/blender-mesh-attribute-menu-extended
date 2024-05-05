"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Functions for managing and editing user interface

"""

# UILIsts
# ----------------------------------------------

from func.util_func import get_friendly_data_type_name, get_friendly_domain_name, get_pinned_mesh_object_and_mesh_reference, is_pinned_mesh_used


def refresh_attribute_UIList_elements(context):

        if is_pinned_mesh_used(context):
            obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
        else:
            obj = bpy.context.active_object
        gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues
        list_elements = gui_prop_group.to_mesh_data_attributes_list

        list_elements.clear()

        for attrib in obj.data.attributes:
            el = list_elements.add()
            el.attribute_name = attrib.name
            el.domain = attrib.domain
            el.domain_friendly_name = get_friendly_domain_name(attrib.domain, short=True)
            el.data_type = attrib.data_type
            el.data_type_friendly_name = get_friendly_data_type_name(attrib.data_type)


def set_attribute_uilist_compatible_attribute_type(domain, data_type):
    """Updates elements in UIList to red-highlight attributes that do not have specified domain or data type 

    Args:
        domain (str): domain
        data_type (str): data type
    """
    gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues

    for el in gui_prop_group.to_mesh_data_attributes_list:

                el.b_domain_compatible = el.domain == domain
                el.b_data_type_compatible = el.data_type == data_type


def configutre_attribute_uilist(enable_same_as_target_filter_btn: bool,
                                enable_incompatible_type_highlight: bool):

    gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues
    gui_prop_group.b_attributes_uilist_show_same_as_target_filter = enable_same_as_target_filter_btn
    gui_prop_group.b_attributes_uilist_highlight_different_attrib_types = enable_incompatible_type_highlight