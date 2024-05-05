"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

General purpose helper functions

"""

import bpy
from etc.preferences import get_preferences_attrib
from func.ui_enum_func import get_attribute_data_types
from func.obj_func import get_object_in_context
from modules import LEGACY_etc, LEGACY_static_data
from func.node_func import get_all_open_properties_panel_pinned_mesh_names
from modules.LEGACY_etc import BL_INFO, __addon_self_module__
from . import obj_func

# Property Groups


def get_wm_propgroup():
    """Returns Property Group stored in blender UI
    """

    return bpy.context.window_manager.MAME_GUIPropValues

def get_datablock_propgroup(obj_data = None, context=None):
    """Returns Property Group stored in object datablock

    Args:
        obj_data (ref, optional): object data to get the prop group from
        context (ref, optional): context to find the object and get it
    """
    if not obj_data:
        obj, obj_data = obj_func.get_object_in_context(context)

    return obj_data.MAME_PropValues



# Register
# ------------------------------------------
 
classes = []

def register(init_module):

    for c in classes:
        bpy.utils.register_class(c)
    

def unregister(init_module):
    for c in classes:
        bpy.utils.unregister_class(c)


def get_object_type_class_by_str(name:str):
    """Converts strings like 'MESH' to object class from bpy.types

    Args:
        name (str): The name of the object type

    Returns:
        class: bpy.types
    """

    if name == 'MESH':
        return bpy.types.Mesh
    elif name == 'CURVES':
        return bpy.types.Curves
    elif name == 'POINTCLOUD':
        return bpy.types.PointCloud
    else:
        return None # idc about other types


# String Getters
# ------------------------------------------

def get_friendly_domain_name(domain_name_raw, plural=False, short=False, context=None):
    """Converts internal domain name to friendly name to be used in UI
    eg. CORNER to Face Corners

    Args:
        domain_name_raw (str): Domain name
        plural (bool, optional): Return plural string. Defaults to False.
        context (ref): Optional, for changing vertices to points if applicable

    Returns:
        str: Friendly string
    """

    # For python api points are vertices and points, oops
    if context is not None and domain_name_raw == 'POINT':
        obj, obj_data = get_object_in_context(context)
        if obj_data is not None and type(obj_data) in [get_object_type_class_by_str(a) for a in ['CURVES', 'POINTCLOUD']]:
            if short:
                return 'P'
            elif plural:
                return 'Points'
            else:
                return 'Point'

    try:
        obj = LEGACY_static_data.attribute_domains[domain_name_raw]
    except KeyError:
        LEGACY_etc.log(get_friendly_domain_name, f'Cannot find {domain_name_raw}', LEGACY_etc.ELogLevel.ERROR)
        return "..."
    if short:
        return obj.friendly_name_short

    return obj.friendly_name if not plural else obj.friendly_name_plural


def get_domain_icon(domain_name_raw, context=None):
    """Returns icon string for domain

    Args:
        domain_name_raw (str): eg. POINT
        context (ref): optional for setting the icon to point instead of vertex

    Returns:
        str: icon string
    """

    # For python api points are vertices and points, oops
    if context is not None and domain_name_raw == 'POINT':
        obj, obj_data = get_object_in_context(context)
        if obj_data is not None and type(obj_data) in [get_object_type_class_by_str(a) for a in ['CURVES', 'POINTCLOUD']]:
            return 'DOT'

    try:
        return LEGACY_static_data.attribute_domains[domain_name_raw].icon
    except KeyError:
        return 'ERROR'


def get_domain_supported_object_types(domain:str):
    """Returns list of object types supported by this domain

    Args:
        domain (str): domain name
    """

    try:
        return LEGACY_static_data.attribute_domains[domain].object_types
    except KeyError:
        LEGACY_etc.log(get_domain_supported_object_types, f'Cannot find {domain}', LEGACY_etc.ELogLevel.ERROR)
        return []


def get_friendly_data_type_name(data_type_raw):
    """Gets friendly name for attribute data types, to use it in GUI
    eg. INT8 -> 8-bit Integer. See data.attribute_data_types
    Args:
        data_type_raw (str): Data type

    Returns:
        str: Friendly string
    """
    if data_type_raw in LEGACY_static_data.attribute_data_types:
        return LEGACY_static_data.attribute_data_types[data_type_raw].friendly_name
    else:
        return data_type_raw


def get_data_type_icon(data_type_name_raw:str):
    try:
        return LEGACY_static_data.attribute_data_types[data_type_name_raw].icon
    except KeyError:
        return 'ERROR'


def get_friendly_name_from_enum_function(context, enum_function, element:str):
    """Gets the Title from enum tuple

    Args:
        context (ref): Context Reference
        enum_function (function): The function that will return enum entries list
        element (str): The element id, aka first element in enum element tuple

    Returns:
        str: Title string, aka second element in enum element tuple
    """
    en = enum_function(context)
    for e in en:
        if e[0] == element:
            return e[1]
    else:
        return None


def get_friendly_name_and_icon_for_EObjectDataSourceUICategory(enum:LEGACY_static_data.EObjectDataSourceUICategory):

    cats = {LEGACY_static_data.EObjectDataSourceUICategory.OTHER: {'name': "Other", 'icon':'SNAP_VOLUME'},
            LEGACY_static_data.EObjectDataSourceUICategory.VISIBILITY: {'name': 'Edit Mode Visibility', 'icon':'HIDE_OFF'},
            LEGACY_static_data.EObjectDataSourceUICategory.SCULPTING: {'name': "Sculpting Mode Data", 'icon':'SCULPTMODE_HLT'},
            LEGACY_static_data.EObjectDataSourceUICategory.COMMON: {'name': "Common Data", 'icon':'MESH_ICOSPHERE'},
            LEGACY_static_data.EObjectDataSourceUICategory.SHADING: {'name': "Shading and Normals Data", 'icon':'NODE_MATERIAL'},
            LEGACY_static_data.EObjectDataSourceUICategory.SUBDIV_MODIFIER: {'name': "Subdivision / Bevel Adjustment Data", 'icon':'MESH_UVSPHERE'},
            LEGACY_static_data.EObjectDataSourceUICategory.VERTEX_GROUPS: {'name': "Vertex Groups Data", 'icon':'GROUP_VERTEX'},
            LEGACY_static_data.EObjectDataSourceUICategory.SHAPE_KEYS: {'name': "Shape Keys Data", 'icon':'SHAPEKEY_DATA'},
            LEGACY_static_data.EObjectDataSourceUICategory.UV: {'name': 'UV and UV Editor Data', 'icon':'UV'},
            LEGACY_static_data.EObjectDataSourceUICategory.EFFECTS: {'name': 'Special Effects Data', 'icon':'SHADERFX'},
            LEGACY_static_data.EObjectDataSourceUICategory.MISC_DATA: {'name': 'Miscellaneous Data', 'icon':'FREEZE'},
            LEGACY_static_data.EObjectDataSourceUICategory.SELECTION: {'name': 'Edit Mode Selection', 'icon':'EDITMODE_HLT'},
            LEGACY_static_data.EObjectDataSourceUICategory.CURVES: {'name': 'Curves', 'icon':get_domain_icon('CURVE')},
            LEGACY_static_data.EObjectDataSourceUICategory.POINT_DATA: {'name': 'Points', 'icon':'DOT'},}
    try:
        return cats[enum]
    except KeyError:
        return {'name': enum.name, 'icon':'QUESTION'}


# Color
# --------------------------------

def color_vector_to_hsv(color):
    """Converts a 4 dimensional tuple contatining color values in RGB to HSV values. 

    Args:
        color (tuple): 4 dimensional color tuple in RGB

    Returns:
        tuple: 4 dimensional color tuple in HSV
    """
    return tuple(colorsys.rgb_to_hsv(color[0], color[1], color[2])) + (color[3],)


def color_vector_to_rgb(color):
    """Converts a 4 dimensional tuple contatining color values in HSV to RGB values. 

    Args:
        color (tuple): 4 dimensional color tuple in HSV

    Returns:
        tuple: 4 dimensional color tuple in RGB
    """
    return tuple(colorsys.hsv_to_rgb(color[0], color[1], color[2])) + (color[3],)


def linear_to_srgb(color_value: float, return_float=True):
    # https://b3d.interplanety.org/en/color-conversion-from-linear-to-srgb-color-space-and-back-in-blender/
    if color_value <= 0.0031308:
        v = int(12.92 * color_value * 255.99)
        return max(min(1.0, v/255),0.0) if return_float else v
    else:
        v = int((1.055 * color_value ** (1 / 2.4) - 0.055) * 255.99)
        return max(min(1.0, v/255),0.0) if return_float else v


# Other
# --------------------------------

def get_attribute_compatibility_check(attribute):
    """Returns true if the attribute is compatible with this addon.

    Args:
        attribute (ref): Reference to attribute

    Returns:
        bool: True if the support for this attribute type was implemented
    """
    if attribute.data_type not in LEGACY_static_data.attribute_data_types:
        return False
    elif attribute.domain not in LEGACY_static_data.attribute_domains:
        return False
    return True


def get_object_type_from_object_data(obj_data):
    """Returns object type string from object data (if supported)

    Args:
        obj_data (ref): object data

    Returns:
        str: object type
    """

    t = type(obj_data)

    if t == bpy.types.Mesh:
        return 'MESH'
    elif t == bpy.types.Curves:
        return 'CURVES'
    elif t == bpy.types.PointCloud:
        return  'POINTCLOUD'
    return None


# Properties Panel Pinned Mesh
# --------------------------------

def is_pinned_mesh_used(context):
    """Simply checks if properties panel has pinned mesh enabled.

    Args:
        context (ref): context reference

    Returns:
        bool: pinned or not
    """

    if hasattr(context, "space_data") and hasattr(context.space_data, "use_pin_id"):
        return context.space_data.use_pin_id
    return False


def get_pinned_mesh_datablock_from_context(context):
    """Gets Mesh Datablock if pin is enabled in properties panel and context contains the reference to it.

    Args:
        context (ref): context reference

    Returns:
        object: Mesh Datablock reference
    """
    if hasattr(context, "space_data") and hasattr(context.space_data, "use_pin_id"):
        return context.space_data.pin_id
    return None


def get_pinned_mesh_datablocks():
    """Gets all Mesh Datablocks if pin is enabled in properties panel in current viewport and context contains the reference to it.

    Args:
        context (ref): context reference

    Returns:
        list: of mesh datablocks
    """
    pinned_meshes_in_current_viewport = []
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            for space in area.spaces:
                if hasattr(space, "use_pin_id") and space.use_pin_id:
                    pinned_meshes_in_current_viewport.append(space.pin_id)
                    break
    return pinned_meshes_in_current_viewport


def update_last_object_reference_for_pinned_datablock(context, ob_data):
    """ Updates reference to last active object with specified data

    Since it's impossible to get "Object" datablock by Mesh datablock, this will update and store last selected object.

    Args:
        context (ref): context reference

    Returns:
        pin_ref (ref): PropPanelPinMeshLastObject object
        ob_data (ref): object.data, may be updated

    SUPPPORTED OBJECT TYPES: MESH CURVES POINTCLOUD 
    """

    pin_ref = None
    gui_prop_group = context.window_manager.MAME_GUIPropValues

    # Find reference
    valid_other_mesh_ids_in_current_vp = get_all_open_properties_panel_pinned_mesh_names()

    i = 0
    while len(gui_prop_group.last_object_refs) > LEGACY_etc.preferences.get_preferences_attrib("pinned_mesh_refcount_max"):
        if i >= len(gui_prop_group.last_object_refs):
            #print(f"Can't remove, user has too many properties tabs open.")
            break

        # If it's in the workspace that reference was created and there is no pin for that, remove it
        if (
            (gui_prop_group.last_object_refs[i].datablock_ref_name not in valid_other_mesh_ids_in_current_vp and
            gui_prop_group.last_object_refs[i].workspace_name == context.window.workspace.name)
            or
            # If the Mesh datablock does not exist anymore, remove it
            (ob_data.type == 'MESH' and gui_prop_group.last_object_refs[i].datablock_ref_name not in bpy.data.meshes)
            or
            (ob_data.type == 'CURVES' and gui_prop_group.last_object_refs[i].datablock_ref_name not in bpy.data.hair_curves)
            or
            (ob_data.type == 'POINTCLOUD' and gui_prop_group.last_object_refs[i].datablock_ref_name not in bpy.data.pointclouds)
            or
            # If the Object datablock does not exist anymore, remove it
            (gui_prop_group.last_object_refs[i].obj_ref_name not in bpy.data.objects)
            ):

            # print(f"Removed {i} {gui_prop_group.last_object_refs[i].datablock_ref_name}")
            gui_prop_group.last_object_refs.remove(i)

        else:
            i += 1
    # Hold a list of ids to garbage collect
    gc_refs_ids = []

    # Find the reference, if exists
    for i, el in enumerate(gui_prop_group.last_object_refs):

        # It could be pinned in another workspace as well yknow
        if el.datablock_ref_name == ob_data.name and el.workspace_name == context.window.workspace.name:
            pin_ref = el
            #etc.log(update_last_object_reference_for_pinned_datablock, f"Object Reference Present for {ob_data.name if ob_data else None}", etc.ELogLevel.SUPER_VERBOSE)

        #If workspace does not exist, or duplicate is present GC
        elif ((el.workspace_name not in [w.name for w in bpy.data.workspaces])
            or (pin_ref and el.datablock_ref_name == pin_ref.datablock_ref_name and el.workspace_name == pin_ref.workspace_name)):
            gc_refs_ids.append(i)

    # Garbage collect references to dead workspaces
    for i in gc_refs_ids:
        gui_prop_group.last_object_refs.remove(i)

    # Make or refresh reference if pin is not yet enabled
    if context.object:

        # Create new pin reference
        if not pin_ref:
            pin_ref = gui_prop_group.last_object_refs.add()

        # Fill in the data
        pin_ref.datablock_ref_name = ob_data.name
        pin_ref.obj_ref_name = context.object.name
        pin_ref.workspace_name = context.window.workspace.name

    # DEBUG: Block pin reference creation
    if LEGACY_etc.preferences.get_preferences_attrib('pinned_mesh_block_ref_creation') and LEGACY_etc.preferences.get_preferences_attrib('debug_operators'):
        pass

    # If pin is enabled 
    else:
        # Update data if 
        if (# pin exists, and active object has same data as pin
            (pin_ref and bpy.context.active_object and bpy.context.active_object.data.name == pin_ref.datablock_ref_name)

            # Or pin does not exist but input ob_data is same as active object
            or (ob_data and bpy.context.active_object and bpy.context.active_object.data
                and ob_data.name == bpy.context.active_object.data.name)):

            # Create new pin reference
            if not pin_ref:
                pin_ref = gui_prop_group.last_object_refs.add()

            # Fill in the data
            ob_data = bpy.context.active_object.data
            pin_ref.datablock_ref_name = bpy.context.active_object.data.name
            pin_ref.obj_ref_name = bpy.context.active_object.name
            pin_ref.workspace_name = context.window.workspace.name

        # Try finding first object with that mesh data in scene
        elif (# If pin does not exist or object is not in current scene
            (not pin_ref or pin_ref.obj_ref_name not in bpy.context.scene.objects)
            # and scene is small
            and len(bpy.context.scene.objects) < 256):

            for sceneobj in bpy.context.scene.objects:
                try:
                    if sceneobj.data.name == ob_data.name:

                        # Create new pin reference
                        pin_ref = gui_prop_group.last_object_refs.add()

                        # Fill in the data
                        ob_data = sceneobj.data
                        pin_ref.datablock_ref_name = sceneobj.data.name
                        pin_ref.obj_ref_name = sceneobj.name
                        pin_ref.workspace_name = context.window.workspace.name

                        break
                except AttributeError:
                    continue

        elif not pin_ref:
            LEGACY_etc.log(update_last_object_reference_for_pinned_datablock, f"No reference yet for {ob_data.name if ob_data else None}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

    # Memory leak protection (better be safe than sorry)
    if len(gui_prop_group.last_object_refs) > LEGACY_etc.preferences.get_preferences_attrib("pinned_mesh_refcount_critical"):
        gui_prop_group.last_object_refs.clear()

    return pin_ref, ob_data


def get_pinned_mesh_object_and_mesh_reference(context):
    """ Gets the pinned mesh datablock and last object reference that used it.

    Args:
        context (ref): context reference

    Returns:
        ref: Object reference
        ref: Mesh Datablock Reference
    """
    gui_prop_group = context.window_manager.MAME_GUIPropValues

    for el in gui_prop_group.last_object_refs:
        if el.workspace_name == context.window.workspace.name and el.datablock_ref_name == context.space_data.pin_id.name:
            mesh_datablock = context.space_data.pin_id
            try:
                object_datablock = bpy.data.objects[el.obj_ref_name] # TODO MIGHT FAIL IF INVALID
            except KeyError:
                return None, None
            return object_datablock, mesh_datablock
    return None, None


def get_addon_directory():
    mod = get_addon_self_module()
    path = os.path.split(mod.__file__)[0]


    # script_file = os.path.realpath(__file__)
    # path = os.path.dirname(script_file)
    return path


def load_external_assets(asset_category:str,
                        asset_type:LEGACY_static_data.EExternalAssetType,
                        asset_file:str = '',
                        asset_names:list = [],
                        b_do_not_preserve_library:bool = True):

    if asset_type == LEGACY_static_data.EExternalAssetType.NODEGROUP:
        asset_file = asset_type.name.lower() + '.blend'# Nodegroup assets are always 'nodegroup.blend'

    path = os.path.join(get_addon_directory(), "assets", asset_category, f"{asset_file}")

    if not os.path.exists(path):
        raise LEGACY_etc.exceptions.ExternalAssetException(load_external_assets.__name__, f"Cannot find {path}")

    if asset_type.name.upper() == 'NODEGROUP':

        # Check whatever nodes exist now
        current_ngs = [ng.name for ng in bpy.data.node_groups]

        # Load new node
        with bpy.data.libraries.load(path) as (lib_data, loaded_data):
            loaded_data.node_groups = asset_names

        if not len(loaded_data.node_groups) or loaded_data.node_groups[0] is None:
            raise LEGACY_etc.exceptions.ExternalAssetException(load_external_assets.__name__, f"Cannot find nodegroup {asset_names}")

        # Remove library
        if b_do_not_preserve_library:
            for lib in bpy.data.libraries:
                if lib.filepath == path:
                    bpy.data.libraries.remove(lib)
                    break

        return loaded_data.node_groups
    return None


# Static data
# ----------------------------------------------

def get_built_in_attributes():
    """Gets a list of built in attributes

    Returns:
        list: of static_data.BuiltInAttribute objects
    """
    l = []
    for a in LEGACY_static_data.built_in_attributes:
        l.append(LEGACY_static_data.built_in_attributes[a])

    return l


def get_built_in_attribute(key:str):
    """Returns static_data.BuiltInAttribute object that defines built in attribute stuff

    Args:
        key (str): built_in_attributes key

    Raises:
        KeyError: Invalid key

    Returns:
        static_data.BuiltInAttribute: Built in attribute definition
    """

    return LEGACY_static_data.built_in_attributes[key]


def get_built_in_attribute_compatible_domains_enum(self, context):
    """Returns compatbble domains for built_in_attribute. 
    [IMPORTANT] Self needs to have built_in_attribute_enum!

    Returns:
        list: enum tuples
    """
    if not hasattr(self, 'built_in_attribute_enum'):
        return [('NULL', 'Invalid', '', 'ERROR', 0)]

    domains = []
    for i, d in enumerate(LEGACY_static_data.built_in_attributes[self.built_in_attribute_enum].domains):
        domains.append((d, get_friendly_domain_name(d),
                        f"Use {get_friendly_domain_name(d)} domain for this attribute",
                        get_domain_icon(d), i))
    return domains


def get_built_in_attribute_compatible_data_types_enum(self, context):
    """Returns compatbble data_types for built_in_attribute. 
    [IMPORTANT] Self needs to have built_in_attribute_enum!

    Returns:
        list: enum tuples
    """
    if not hasattr(self, 'built_in_attribute_enum'):
        return [('NULL', 'Invalid', '', 'ERROR', 0)]

    data_types = []
    for i, d in enumerate(LEGACY_static_data.built_in_attributes[self.built_in_attribute_enum].data_types):
        data_types.append((d,
                           get_friendly_data_type_name(d),
                           f"Use {get_friendly_data_type_name(d)} data type for this attribute",
                           get_data_type_icon(d),
                           i))
    return data_types


# Properties

def get_bpy_prop_for_attribute_data_type(data_type:str):
    """Returns a bpy.props class for input data type

    Args:
        data_type (str): Data type

    Returns:
        class: bpy.props
    """
    try:
        return LEGACY_static_data.attribute_data_types[data_type].bpy_props_class
    except KeyError:
        return None


# Python script related
# ----------------------------------------------

def check_python_script_syntax(script:str):
    """Checks syntax of input python script.

    Args:
        script (str): python script

    Returns:
        boolean: Is script valid
        Exception: Exception if any
    """

    try:
        ast.parse(script)
        return True, None
    except SyntaxError as exc:
        return False, exc


# Rendering & Images
# ----------------------------------------------

def get_cycles_available():
    """Checks if the Cycles Render Engine is enabled and available

    Returns:
        bool: status
    """
    return 'cycles' in bpy.context.preferences.addons


def get_color_data_types():
    """Returns data types that contain color
    """

    dts = get_attribute_data_types()
    color_dts = []
    for dt in dts:
        if LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype == 'COLOR':
            color_dts.append(dt)
    return color_dts


def get_datablock_prop_group_ui_attribute_value(prop_group, data_type:str):
    """Gets attribute value set in properties panel,

    Args:
        prop_group (ref): Property group in object data block (MAME_PropValues)
        data_type (str): Data type

    Returns:
        _type_: _description_
    """
    attr_name = 'val_' + data_type.lower()
    return getattr(prop_group, attr_name)


def get_alpha_channel_enabled_texture_bake_op(self):
    # Used in AttributesToImage operqtor, can't put it in the operator.
    # Checks if alpha channel is enabled to bake it
    img_ref = bpy.context.window_manager.mame_image_ref
    return((self.image_source_enum == 'NEW' and self.b_new_image_alpha) or (self.image_source_enum == 'EXISTING' and img_ref is not None and img_ref.alpha_mode != 'NONE'))


def get_blender_support(minver = None, minver_unsupported = None):
    """Used to check if blender version is supported for any feature. Use this instead of creating an if

    Args:
        minver (tuple): Version tuple eg. (3,0,0)
        minver_unsupported (tuple): Version tuple eg. (3,0,0)

    Returns:
        Boolean: True if supported
    """
    if get_preferences_attrib('disable_version_checks'):
        return True

    return (minver is None or bpy.app.version >= minver) and (minver_unsupported is None or bpy.app.version < minver_unsupported)


def get_bl_info_key_value(key:str):
    """Returns bl_info key value or none if invalid

    Returns:
        str: bl_info set value at key
    """

    if key in BL_INFO:
        return BL_INFO[key]
    return None


def set_global_bl_info(bl_info: set):
    """Sets the bl_info from __init__ to use in other functions

    Args:
        bl_info (set): bl_info
    """
    global BL_INFO
    BL_INFO = bl_info


def bl_version_tuple_to_friendly_string(ver_tuple:tuple):
    """Returns nicely formatted blender style version tuple as a string

    Args:
        ver_tuple (tuple): eg. (1,0,0)

    Returns:
        str: friendly string
    """
    if type(ver_tuple) != tuple:
        return "Unknown"
    return str(f"{ver_tuple[0]}.{ver_tuple[1]}.{ver_tuple[2]}")


def set_addon_self_module(module):
    """
    Sets the python module of the addon to a global variable
    """
    global __addon_self_module__

    __addon_self_module__ = module


def get_addon_self_module():
    """Returns python module reference

    Returns:
        ref: module
    """
    return __addon_self_module__

    # else:
    #     return domain_name_raw.lower().capitalize() if not plural else domain_name_raw.lower().capitalize() + "s"


# Generic data types
# ------------------------------------------

# Macro utilities
# ---------------------------------
# This API is designed to fire multiple modal operators like texture bake at once, that do not inform about it's completion
# As of commit 74e4f9c used only to fire a single operator, so it's an overkill
#
# To create a macro, use create_macro_queue(), add operators using macro_queue_add_element() and activate with 
# macro_queue_execute(). Wait for True result of macro_queue_finished() in modal function of an operator 
#

# Defines whether the queue macro has finished executing all actions
QUEUE_FINISH_STATUS = True

# Defines macro queue operations count (without UI report operatiors)
QUEUE_SIZE = 0


def set_queue_macro_finish_status(value:bool):
    """Sets the finished state of queue macro

    Args:
        value (bool): Set it to true to notify parent modal operator to stop it's execution, if macro has finished executing
    """
    global QUEUE_FINISH_STATUS
    QUEUE_FINISH_STATUS = value
    return

def get_queue_macro_finish_status():
    """Gets the finished state of queue macro

    Returns:
        bool: If macro has finished executing all actions, it's set to True, parent modal operator can stop executing
    """
    global QUEUE_FINISH_STATUS
    return QUEUE_FINISH_STATUS

def create_macro_queue():
    """Creates macro queue class to execute blender modal operators that do not notify about execution completion

    Returns:
        bpy.types.Macro object: The macro
    """

    # Define macro class
    class OBJECT_OT_mame_queue_macro(bpy.types.Macro):
            bl_idname = "object.mame_queue_macro"
            bl_label = "Bake Macro"
            bl_options = {'INTERNAL'}

    # unregister any previous macro
    if hasattr(bpy.types, "OBJECT_OT_mame_queue_macro"):
        bpy.utils.unregister_class(bpy.types.OBJECT_OT_mame_queue_macro)


    # Reset queue size
    global QUEUE_SIZE
    QUEUE_SIZE = 0

    bpy.utils.register_class(OBJECT_OT_mame_queue_macro)
    return OBJECT_OT_mame_queue_macro

def macro_queue_add_element(macro, operator_class:str, operation_name:str = "Processing"):
    """Adds operator to exisitng macro queue, and automatically adds progress operator as well

    Args:
        macro (bpy.types.Macro): Macro to add operator to
        operator_class (str): Operator class, eg. OBJECT_OT_bake
        operation_name (str, optional): Description of what is happening, eg. Baking. Defaults to "Processing".

    Returns:
        ref: Reference to opeator to modify it's properties
    """
    # Add a progress report operator
    global QUEUE_SIZE
    report = _bpy.ops.macro_define(macro, 'WM_OT_mame_queue_macro_report')
    report.properties.queue_position = QUEUE_SIZE
    report.properties.operation_name = operation_name
    QUEUE_SIZE +=1

    # Add requested operator
    return _bpy.ops.macro_define(macro, operator_class)

def macro_queue_execute(macro):
    """Starts executing macro queue, adds operator that sets the finished flag as well

    Args:
        macro (bpy.types.Macro): Macro to trigger
    """
    # Reset to default
    set_queue_macro_finish_status(False)

    # Add opeator to notify about finished execution
    _bpy.ops.macro_define(macro, 'WM_OT_mame_queue_macro_set_finished')
    
    # Go!
    bpy.ops.object.mame_queue_macro('INVOKE_DEFAULT')
    return

def macro_queue_finished():
    """Returns True if macro queue has finished processing all operations

    Returns:
        bool: True if macro queue has finished executing all operators
    """
    if get_queue_macro_finish_status():
        set_queue_macro_finish_status(False)
        return True
    return False


# ---------------------------------

class WM_OT_mame_queue_macro_report(bpy.types.Operator):
    """
    Shows progress status of queue macro in progress bar
    """
    
    bl_idname = "wm.mame_queue_macro_report"
    bl_label = "Macro Queue Report"
    bl_options = {'INTERNAL'}

    # Currently executed opeartion index
    queue_position: bpy.props.IntProperty()

    # Operation name to show in UI
    operation_name: bpy.props.StringProperty(default = "Processing")

    def execute(self, context):
        global QUEUE_SIZE
        self.report({'INFO'}, f"[{self.queue_position+1}/{QUEUE_SIZE}] {self.operation_name}")
        return {'FINISHED'}

class WM_OT_mame_queue_macro_set_finished(bpy.types.Operator):
    """
    Notifies the operator that called to execute the macro queue, that all of the requested operators have been executed 
    Auto added and executed as last opeator in macro
    """

    bl_idname = "wm.mame_queue_macro_set_finished"
    bl_label = "Bake Set Finished"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        set_queue_macro_finish_status(True)
        return {'FINISHED'}


# Dynamic classess to clean up
# ------------------------------------------
# Classes created by exec or in functions. Save them to clean up on unregister.

dynamically_created_classes = []

def save_dynamically_created_class(c):
    global dynamically_created_classes
    dynamically_created_classes.append(c)

def get_dynamically_created_classes():
    return dynamically_created_classes