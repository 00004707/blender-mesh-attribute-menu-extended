"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
etc

Everything else. 
The file must not create a circular import with anything

"""

import bpy, time, _bpy, os#, logging
from datetime import datetime
from bpy_extras.io_utils import ExportHelper
from enum import Enum
from traceback import format_exc
import addon_utils
from etc.preferences import get_preferences_attrib
from etc.preferences import AddonPreferences
from etc.property_groups import AttributeListItem
from etc.property_groups import GenericBoolPropertyGroup
from etc.property_groups import PropPanelPinMeshLastObject
from etc.property_groups import AttributePropertyGroup
from etc.property_groups import ObjectPropertyGroup
from func.util_func import get_bl_info_key_value
from func.util_func import set_global_bl_info
from func.util_func import bl_version_tuple_to_friendly_string
from func.util_func import set_addon_self_module
from func.util_func import get_addon_directory
from ops.util.util_ops_ui import FakeFaceCornerSpillDisabledOperator
from ops.util.util_ops_ui import WINDOW_MANAGER_OT_mame_report_issue
from ops.util.util_ops_ui import OpenWiki

# Constants
# ------------------------------------------

# Package name, eg. to disable the addon
__addon_package_name__ = __package__.replace('.modules','')
__addon_self_module__ = None

# Amount of vertices or points to warn user about slow operation
LARGE_MESH_VERTICES_COUNT = 500000


# Copy of BL_INFO from __init__
BL_INFO = {}


# Wiki Link
# ------------------------------------------



# Register
# ------------------------------------------
    
classes = [
    CrashMessageBox, 
    WINDOW_MANAGER_OT_mame_save_log_file,
    AddonPreferences,
    AttributeListItem,
    GenericBoolPropertyGroup,
    PropPanelPinMeshLastObject,
    FakeFaceCornerSpillDisabledOperator,
    WINDOW_MANAGER_OT_mame_report_issue,
    ShowLog,
    ClearLog,
    WM_OT_mame_queue_macro_report,
    WM_OT_mame_queue_macro_set_finished,
    OpenWiki,
    AttributePropertyGroup,
    ObjectPropertyGroup
    ]


# Used to determine if an unregister was called on register for GC
REGISTER_RETRY_FLAG = False

register_weight = 1000

def register(init_module):
    "Register classes"
    global REGISTER_RETRY_FLAG
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except ValueError as exc:
            # Garbage collect
            if not REGISTER_RETRY_FLAG:
                REGISTER_RETRY_FLAG = True
                log(register, "Retrying register", ELogLevel.WARNING)
                unregister(init_module)
                register(init_module)
                return
            else:
                raise exc
            
    # Initialize logging
    init_logging()

    # Global bl_info
    set_global_bl_info(init_module.bl_info)

    # Module reference
    set_addon_self_module(init_module)

    log(None, f"Working directory: {get_addon_directory()}", 
                              ELogLevel.VERBOSE)
    
    # on success, allow retry again
    REGISTER_RETRY_FLAG = False

    

def unregister(init_module):
    "Unregister classes. Exception handing in init"
    global REGISTER_RETRY_FLAG
    for c in classes:
        try:
            bpy.utils.unregister_class(c)
        except Exception as exc:
            # Some classes might not be registered.
            if REGISTER_RETRY_FLAG:
                continue
            else:
                raise exc
    # Unregister dynamically created classes if any
    for c in get_dynamically_created_classes():
        try:
            bpy.utils.unregister_class(c)
        except Exception:
            continue
