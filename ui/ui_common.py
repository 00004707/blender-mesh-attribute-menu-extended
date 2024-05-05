"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Common UI Interface Elements

"""


import bpy
from etc.preferences import get_preferences_attrib
from etc import property_groups, static_data

# Confirm Box
# -----------------------------------------
# To use confirm box execute get_confirm_box() in execute, then listen in modal timer
# for get_confirm_box_status() for OK or CANCEL string.

# The reference to the confirm box, for checking if it exists (user cancelled)
MAME_CONFIRM_BOX_REFERENCE = None


def set_confirm_box_reference(ref):
    global MAME_CONFIRM_BOX_REFERENCE
    MAME_CONFIRM_BOX_REFERENCE = ref


class WM_OT_mame_confirm_box(bpy.types.Operator):
        bl_idname = 'window_manager.mame_confirm_box'
        bl_label = 'Confirm'
        bl_options = {'REGISTER', 'INTERNAL'}

        title: bpy.props.StringProperty(name='Title', default='Warning')
        icon: bpy.props.StringProperty(name='icon', default='WARNING')
        confirm_text: bpy.props.StringProperty(name='Confirm Text', default='Continue')

        def invoke(self, context, event):
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            gui_prop_group.popup_window_status = ''
            set_confirm_box_reference(self)
            return context.window_manager.invoke_confirm(self, event, title=self.title,  icon=self.icon, confirm_text=self.confirm_text)

        def execute(self, context):
            gui_prop_group = context.window_manager.MAME_GUIPropValues
            gui_prop_group.popup_window_status = 'OK'
            return {'FINISHED'}


def get_confirm_box(title:str = "Are you sure?", confirm_text:str = "Continue", icon:str='WARNING'):
    """
    A hacky way to show a confirm box with custom message
    """

    global MAME_CONFIRM_BOX_REFERENCE
    MAME_CONFIRM_BOX_REFERENCE = None

    return bpy.ops.window_manager.mame_confirm_box('INVOKE_DEFAULT', title=title, confirm_text=confirm_text, icon=icon)


def get_confirm_box_reference():
    return MAME_CONFIRM_BOX_REFERENCE


def get_confirm_box_status():
    """Returns status of a confirm box. Clears status on use.
    '' - No box or still waiting for input
    'OK' - Accepted
    'CANCEL' - Cancelled"""

    # how long before i have to fix issues with this type of programming?

    gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues
    if gui_prop_group.popup_window_status == 'OK':
        gui_prop_group.popup_window_status = ''
        return 'OK'
    try:
        get_confirm_box_reference().name
    except ReferenceError:
        gui_prop_group.popup_window_status = ''
        return 'CANCEL'
    return ''


# Message Box
# -----------------------------------------

# Used in GenericMessageBox to use as a draw function 
MESSAGE_BOX_DRAW_FUNCTION = None

# Used in GenericMessageBox to use as extra data in draw function
MESSAGE_BOX_EXTRA_DATA = None

class GenericMessageBox(bpy.types.Operator):
    """Shows an OK message box.

    """
    bl_idname = "window_manager.mame_message_box"
    bl_label = "Mesh Attributes Menu Extended Message"
    bl_options = {'REGISTER', 'INTERNAL'}

    # Width of the message box
    width: bpy.props.IntProperty(default=400)

    # Message to show
    message: bpy.props.StringProperty(default='')

    # Whether to use custom draw functions stored in MESSAGE_BOX_DRAW_FUNCTION global variable
    custom_draw: bpy.props.BoolProperty(default=False)

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=self.width)
        return {'FINISHED'}

    def draw(self, context):
        if self.custom_draw:
            global MESSAGE_BOX_DRAW_FUNCTION
            MESSAGE_BOX_DRAW_FUNCTION(self, context, message=self.message)
        else:
            layout = self.layout
            messages = self.message.splitlines()
            for msg in messages:
                layout.label(text=msg)


def draw_error_list(self, context, message=''):
    col = self.layout.column()
    col.label(icon='ERROR', text=message)

    max_errors = 10
    global MESSAGE_BOX_EXTRA_DATA
    errors = MESSAGE_BOX_EXTRA_DATA
    print(f"data{errors}")
    for error in range(0, min(max_errors+1, len(errors))):
        col.label(icon='DOT', text=errors[error])
    if len(errors) > max_errors:
        col.label(text=f"{len(errors)-max_errors} more...")


def set_message_box_function(function):
    """Assigns a custom draw function when using GenericMessageBox

    Args:
        function (func): function to call. Will be called with paramters: self, context, message
    """
    global MESSAGE_BOX_DRAW_FUNCTION
    MESSAGE_BOX_DRAW_FUNCTION = function


def set_message_box_extra_data(extra_data):
    """Stores custom data to use in custom draw function of GenericMessageBox

    Args:
        extra_data (any): any type of data 
    """
    global MESSAGE_BOX_EXTRA_DATA
    MESSAGE_BOX_EXTRA_DATA = extra_data


def get_attribute_value_input_ui(layout,
                    source,
                    prop_name:str,
                    data_type:str):
    """Shows UI for inputting attribute values

    Args:
        layout (ref): Layout reference
        source (ref): Source to get property from
        prop_name (str): name of the property
        data_type (str): Data type
    """

    # Show true false for booleans
    attr_val = getattr(source, prop_name)
    if type(attr_val) == bool:
        title_str = "True" if attr_val else "False"
    else:
        title_str = ""

    matrix_type = static_data.attribute_data_types[data_type].large_capacity_vector
    matrix_w = static_data.attribute_data_types[data_type].large_capacity_vector_size_width
    matrix_h = static_data.attribute_data_types[data_type].large_capacity_vector_size_height

    # Matrix input UI
    if matrix_type:
        matrixcol = layout.column(align=True)
        for i in range(0, matrix_w):
            matrix_vals_col = matrixcol.column(align=True)
            matrix_vals_row = matrix_vals_col.row(align=True)
            for j in range(0, matrix_h):
                matrix_vals_row.prop(source, prop_name, text=title_str, toggle=True, index=i*matrix_w+j)

    # Blender built-in method for other
    else:
        layout.prop(source, prop_name, text=title_str, toggle=True)


class ATTRIBUTE_UL_attribute_multiselect_list(bpy.types.UIList):
    """
    Multi-selection list of attributes, with tickboxes, data types and domains on the list entries.
    Supports filtering and reordering
    """

    name_filter: bpy.props.StringProperty(name="Name", default="")

    datatype_filter_compatible: bpy.props.BoolProperty(name="Same as target", default=False)
    datatype_filter: bpy.props.CollectionProperty(type = property_groups.GenericBoolPropertyGroup)

    domain_filter_compatible: bpy.props.BoolProperty(name="Same as target", default=False)
    domain_filter: bpy.props.CollectionProperty(type = property_groups.GenericBoolPropertyGroup)

    def _gen_order_update(name1, name2):
        def _u(self, ctxt):
            if (getattr(self, name1)):
                setattr(self, name2, False)
        return _u

    use_order_name: bpy.props.BoolProperty(
        name="Name", default=False, options=set(),
        description="Sort groups by their name (case-insensitive)",
        update=_gen_order_update("use_order_name", "use_order_importance"),
    )

    sort_reverse: bpy.props.BoolProperty(
        name="Reverse",
        default=False,
        options=set(),
        description="Reverse sorting",
    )


    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues

        # layout.label(text=item.attribute_name)

        row = layout.row()
        row.prop(item, "b_select", text=item.attribute_name)
        # subrow = row.row()
        # subrow.scale_x = 1.0
        # subrow.label(text=item.attribute_name)

        subrow = row.row()
        subrow.scale_x = 0.5
        subrow.alert = not item.b_domain_compatible and gui_prop_group.b_attributes_uilist_highlight_different_attrib_types
        subrow.label(text = item.domain_friendly_name)

        subrow = row.row()
        subrow.scale_x = .75
        subrow.alert = not item.b_data_type_compatible and gui_prop_group.b_attributes_uilist_highlight_different_attrib_types
        subrow.label(text = item.data_type_friendly_name)


    def draw_filter(self, context, layout):
        gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues
        col = layout.column()


        row = col.row(align=True)
        row.prop(self, "name_filter", text="")
        row.prop(self, "use_order_name", text="", icon="SORTALPHA")
        icon = 'SORT_ASC' if self.sort_reverse else 'SORT_DESC'
        row.prop(self, "sort_reverse", text="", icon=icon)

        col.label(text="Filter Domains")

        if gui_prop_group.b_attributes_uilist_show_same_as_target_filter:
            filter_row = col.row(align=True)
            filter_row.prop(self, 'domain_filter_compatible', toggle=True)
        else:
            self.domain_filter_compatible = False

        filter_row = col.row(align=True)
        filter_row.enabled = not self.domain_filter_compatible
        for boolprop in self.domain_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)

        col.label(text="Filter Data Types")

        if gui_prop_group.b_attributes_uilist_show_same_as_target_filter:
            filter_row = col.row(align=True)
            filter_row.prop(self, 'datatype_filter_compatible', toggle=True)
        else:
            self.datatype_filter_compatible = False

        filter_row = col.grid_flow(columns=3, even_columns=False, align=True)
        filter_row.enabled = not self.datatype_filter_compatible
        for boolprop in self.datatype_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)

    def initialize(self, context):
        self.datatype_filter.clear()

        for data_type in static_data.attribute_data_types:
            b = self.datatype_filter.add()
            b.b_value = True
            b.name = func.util_func.get_friendly_data_type_name(data_type)
            b.id = data_type

        for domain in static_data.attribute_domains:
            b = self.domain_filter.add()
            b.b_value = True
            b.name = func.util_func.get_friendly_domain_name(domain)
            b.id = domain

        self.prop_group = bpy.context.window_manager.MAME_GUIPropValues

    def filter_items(self, context, data, propname):
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        attributes = getattr(gui_prop_group, propname)
        helper_funcs = bpy.types.UI_UL_list

        if not len(self.datatype_filter):
            self.initialize(context)

        filter_list = []
        sort_ids_list = []

        # Filtering

        # Filtering by name
        if self.name_filter:
            filter_list = helper_funcs.filter_items_by_name(self.name_filter, self.bitflag_filter_item, attributes, "attribute_name",
                                                          reverse=False)

        # make sure something is returned 
        if not filter_list:
            filter_list = [self.bitflag_filter_item] * len(attributes)

        # Filter by domain
        if self.domain_filter_compatible:
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.b_domain_compatible else 0
        else:
            d_filters = [d.id for d in self.domain_filter if d.b_value]
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.domain in d_filters else 0

        # Filter by datatype
        if self.datatype_filter_compatible:
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.b_data_type_compatible else 0
        else:
            dt_filters = [dt.id for dt in self.datatype_filter if dt.b_value]
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.data_type in dt_filters else 0


        # Sorting

        # Sorting by name
        if self.use_order_name:
            sort_ids_list = helper_funcs.sort_items_by_name(attributes, "attribute_name")

        # Reverse sorting
        if self.sort_reverse:
            if not len(sort_ids_list):
                sort_ids_list = [*range(0, len(attributes))]

            sort_ids_list.reverse()

        return filter_list, sort_ids_list


def draw_multi_attribute_select_uilist(layout):
    col = layout.column(align=True)
    label_row = col.row()
    sr = label_row.row()
    sr.label(text="Name")
    sr = label_row.row()
    sr.scale_x = 0.5
    sr.label(text="Domain")
    sr = label_row.row()
    sr.scale_x = .85
    sr.label(text="Data Type")
    gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues
    col.template_list("ATTRIBUTE_UL_attribute_multiselect_list", "Mesh Attributes", gui_prop_group,
                    "to_mesh_data_attributes_list", gui_prop_group, "to_mesh_data_attributes_list_active_id", rows=10)


def append_wiki_operator(self, context):
    """
    Adds wiki button to draw function of an operator. Operator needs to have wiki_url variable
    """
    if get_preferences_attrib("show_docs_button"):
        r = self.layout.column()
        r.separator()
        op = r.operator('window_manager.mame_open_wiki', icon='HELP')
        op.wiki_url = self.wiki_url


def create_submenu(submenu_idname_suffix, submenu_friendly_name):
    """
    Creates a menu object to use in dynamically populated menus as submenu
    """

    idname = f"WM_MT_{submenu_idname_suffix.replace(' ', '_')}"

    # Unregister if already registered
    if hasattr(bpy.types, idname):
        bpy.utils.unregister_class(getattr(bpy.types, idname))

    # Create new submenu class and return reference to it
    exec_locals = {}
    code = f"""class SubMenu(bpy.types.Menu):
        bl_idname = '{idname}'
        bl_label = '{submenu_friendly_name}'

        def draw(self, context):
            return

    \nbpy.utils.register_class(SubMenu)
    \nsm = SubMenu"""
    exec(code, None, exec_locals)
    return exec_locals['sm']

