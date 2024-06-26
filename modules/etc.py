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

# Constants
# ------------------------------------------

# Package name, eg. to disable the addon
__addon_package_name__ = __package__.replace('.modules','')

# Amount of vertices or points to warn user about slow operation
LARGE_MESH_VERTICES_COUNT = 500000

# Logger object
# LOGGER = None

# Addon log, elements format: {'level': level.name, 'message': message, 'timestamp': time.time(), 'who': obj reference})
LOG = []

# Snapshot of a log at given moment, used by crash hander UI to not overwrite log with new values
LOG_SNAPSHOT = []

# Copy of BL_INFO from __init__
BL_INFO = {}

# Exceptions
# ------------------------------------------

class MeshDataReadException(Exception):
    """
    Exception thrown when reading data from mesh has failed
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[READ] " + self.function_name + ": " + self.message)

class MeshDataWriteException(Exception):
    """
    Exception thrown when writing data to mesh has failed
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[WRITE] " + self.function_name + ": " + self.message)

class GenericFunctionParameterError(Exception):
    """
    Exception thrown when input parameter of a function is invalid
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[PARAM] " + self.function_name + ": " + self.message)


# Extra Functions
# ------------------------------

def get_preferences_attrib(name:str):
    """Reads addon preferences variable

    Args:
        name (str): The name of the variable

    Returns:
        None: None
    """
    prefs = bpy.context.preferences.addons[__addon_package_name__].preferences
    return getattr(prefs, name) if hasattr(prefs, name) else None

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

def get_enhanced_enum_titles_enabled():
    """Returns true if blender and user settings support enhanced enum titles that use non-standard character set

    Returns:
        boolean: True if supported
    """
    if get_blender_support((3,3,0)):
        return get_preferences_attrib('enhanced_enum_titles')
    else:
        return False

def set_global_bl_info(bl_info: set):
    """Sets the bl_info from __init__ to use in other functions

    Args:
        bl_info (set): bl_info
    """
    global BL_INFO
    BL_INFO = bl_info

def get_bl_info_key_value(key:str):
    """Returns bl_info key value or none if invalid

    Returns:
        str: bl_info set value at key
    """

    if key in BL_INFO:
        return BL_INFO[key]
    return None

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

def make_log_snapshot():
    """Copies current log into a new container so it does not get overwritten

    Returns:
        None
    """

    global LOG, LOG_SNAPSHOT
    LOG_SNAPSHOT = LOG.copy()

# Fake operators
# ------------------------------

class FakeFaceCornerSpillDisabledOperator(bpy.types.Operator):
    """
    Fake operator to occupy GUI place
    It looks better than using .enabled = False for UI elemtent
    """

    bl_idname = "mesh.always_disabled_face_corner_spill_operator"
    bl_label = "Fake operator to occupy GUI place"
    bl_description = "Enable Face Corner Spill"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Active attribute is not on Face Corner domain")
        return False


# Utility operators
# -----------------------------

class MAMEDisable(bpy.types.Operator):
    """
    Addon disabler
    """

    bl_idname = "mame.disable"
    bl_label = "Disable Addon"
    bl_description = ""
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        bpy.ops.preferences.addon_disable(module=__addon_package_name__)
        return {'FINISHED'}
    
    @classmethod
    def poll(self, context):
        return True

class MAMEBlenderUpdate(bpy.types.Operator):
    """
    Addon Opens url to update blender
    """

    bl_idname = "mame.update_blender"
    bl_label = "Update blender"
    bl_description = ""
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        bpy.ops.wm.url_open(url="https://www.blender.org/download/")
        return {'FINISHED'}
    
    @classmethod
    def poll(self, context):
        return True

class WINDOW_MANAGER_OT_mame_report_issue(bpy.types.Operator):
    """
    Reports issue with the addon
    """

    bl_idname = "window_manager.mame_report_issue"
    bl_label = "Report Issue"
    bl_description = "Open github page to report the issue"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        bpy.ops.wm.url_open(url="https://github.com/00004707/blender-mesh-attribute-menu-extended/issues")
        return {'FINISHED'}
    
    @classmethod
    def poll(self, context):
        return True

# ------------------------------------------
# Preferences

class AddonPreferencesUnsupportedBlenderVer(bpy.types.AddonPreferences):
    """
    Addon preferences for unsupported blender version
    """

    bl_idname = __addon_package_name__

    def draw(self, context):
        layout = self.layout

        if bpy.app.version < (3,1,0):
                
            row = layout.row()
            row.alert = True
            row.label(text="This addon requires blender version 3.1.0 or higher, and has not been loaded.", icon='ERROR')
            row = layout.row()
            row.operator("mame.update_blender", icon="BLENDER")
            srow = row.row()
            srow.alert = True
            srow.operator("mame.disable", icon="CANCEL")

class AddonPreferences(bpy.types.AddonPreferences):
    """
    Addon preferences definition
    """

    bl_idname = __addon_package_name__
    
    # User settings (variables)
    # ------------------------------------------
    
    # General
    enhanced_enum_titles: bpy.props.BoolProperty(name="Enhanced dropdown menu titles", description="If the following text -> ᶠᵃᶜᵉ, does not display correctly you can toggle it off", default=True)
    attribute_assign_menu: bpy.props.BoolProperty(name="Attribute Assign Menu (Mesh)", description="Assign and clear buttons", default=True)
    attribute_assign_menu_curves: bpy.props.BoolProperty(name="Attribute Assign Menu (Curves)", description="Assign and clear buttons", default=True)
    attribute_assign_menu_pointcloud: bpy.props.BoolProperty(name="Attribute Assign Menu (Point Cloud)", description="Assign and clear buttons", default=True)
    set_attribute_raw_quaterion: bpy.props.BoolProperty(name="Set Raw Quaternions Value", description="If you want to use quaternion attributes as 4D vectors instead of quaternions, enable this", default=True)
    select_attribute_precise_facecorners: bpy.props.BoolProperty(name="Precise Face Corner Select (Slow)", description="If you want to select individual edges that identify a face corner, this has to be enabled. Not requried for face painting", default=False)
    show_docs_button: bpy.props.BoolProperty(name="Show \"Open Documentation\" Button", description="Shows \"Open Documentation\" button in operator menus", default=True)

    # Specials
    add_set_attribute: bpy.props.BoolProperty(name="Add \"Set Attribute\" operator", description="Set Attribute operator in dropdown menu", default=True)
    extra_context_menu_vg: bpy.props.BoolProperty(name="Vertex Groups Menu", description="Adds extra operators to Vertex Group Menu", default=True)
    extra_context_menu_sk: bpy.props.BoolProperty(name="Shape Keys Menu", description="Adds extra operators to Shape Keys Menu", default=True)
    extra_context_menu_uvmaps: bpy.props.BoolProperty(name="UVMap Menu", description="Adds extra operators to UVMap Menu", default=True)
    extra_context_menu_fm: bpy.props.BoolProperty(name="Face Maps Menu", description="Adds extra operators to Face Maps Menu", default=True)
    extra_context_menu_materials: bpy.props.BoolProperty(name="Materials Menu", description="Adds extra operators to Materials Menu", default=True)
    extra_context_menu_color_attributes: bpy.props.BoolProperty(name="Color Attributes Menu", description="Adds extra operators to Color Attributes Menu", default=True)
    # Context
    
    extra_context_menu_edge_menu: bpy.props.BoolProperty(name="Edge Context Menu", description="Adds extra operators to Edge Context Menu in Edit Mode", default=True)
    extra_context_menu_vertex_menu: bpy.props.BoolProperty(name="Vertex Context Menu", description="Adds extra operators to Vertex Context Menu in Edit Mode", default=True)
    extra_context_menu_face_menu: bpy.props.BoolProperty(name="Face Context Menu", description="Adds extra operators to Face Context Menu in Edit Mode", default=True)
    #extra_context_menu_object: bpy.props.BoolProperty(name="Object Context Menu", description="Adds extra operators to Object Context Menu in Object Mode", default=True)

    # 3D View
    extra_header_sculpt: bpy.props.BoolProperty(name="Masks Manager", description="Adds menu to Tool N-panel tab", default=True)
    extra_context_menu_sculpt: bpy.props.BoolProperty(name="Mask & Face Sets Menus", description="Adds extra operators to sculpting 3D View menus", default=True)

    # Quick
    extra_context_menu_geometry_data: bpy.props.BoolProperty(name="Geometry Data Menu", description="Adds extra operators to Geometry Data Menu", default=False)
    quick_shelf_enable: bpy.props.BoolProperty(name="Enable Quick Shelf", description="Buttons for quicker actions", default=False)
    quick_shelf_randomize: bpy.props.BoolProperty(name="Randomize Value", description="Adds a button to randomize value", default=False)
    quick_shelf_convert_to_mesh_data_repeat: bpy.props.BoolProperty(name="To Mesh Data Repeat", description="Adds a button to redo last \"To mesh Data\"", default=False)
    quick_attribute_node_enable: bpy.props.BoolProperty(name="Enable Quick Node", description="Buttons for to create attribute nodes in node editors", default=True)
    
    # Debug
    debug_zone_en: bpy.props.BoolProperty(name="Show", description="Scary", default=False)
    verbose_mode: bpy.props.BoolProperty(name="Verbose Logging - disable only", description="Scary", default=False)
    debug_operators: bpy.props.BoolProperty(name="Enable Debug Extras", description="Scary", default=False)
    pseudo_profiler: bpy.props.BoolProperty(name="Pseudo-profiler - disable only", description="Scary", default=False)
    disable_version_checks: bpy.props.BoolProperty(name="Disable Blender Version Checks", description="Scary", default=False)
    set_algo_tweak: bpy.props.FloatProperty(name="Tweak Optimal Set Attribute Alghoritm Detection", description="set_attribute_values()", default=0.15)
    disable_bpy_set_attribute: bpy.props.BoolProperty(name="Force Disable bpy.ops.mesh.attribute_set", description="Uses add-on alghortitm only to set the values in edit mode", default=False)
    bakematerial_donotdelete: bpy.props.BoolProperty(name="Do not delete temporary bake material", description="Scary", default=False)
    pinned_mesh_refcount_max: bpy.props.IntProperty(name="Max Pinned Mesh References", description="Scary", default=8, min=2)
    pinned_mesh_refcount_critical: bpy.props.IntProperty(name="Absolute Max Pinned Mesh References", description="Scary", default=64, min=4)
    console_loglevel: bpy.props.IntProperty(name="Console Log Level", default=3, min=0, max=4, description="0=SUPER_VERBOSE\n1=VERBOSE\n2=INFO\n3=WARNING\n4=ERROR")
    en_slow_logging_ops: bpy.props.BoolProperty(name="Full Data Logging (Slow)", description="Collects more information about processed object", default=False)
    show_hidden_blown_fuses: bpy.props.BoolProperty(name="Show hidden UI elements with blown fuses", description="Scary", default=False)
    max_log_lines: bpy.props.IntProperty(name="Max Log Lines", description="Scary", min = 8, default=64, max = 128)
    force_assign_on_selected_by_value: bpy.props.BoolProperty(name="Force Assign On Selected By Value", description="Scary", default=False)
    force_assign_on_selected_by_foreach_get_foreach_set: bpy.props.BoolProperty(name="Force Assign On Selected By foreach", description="Scary", default=False)
    register_debug_ops_on_start: bpy.props.BoolProperty(name="Register Debug Operators On Startup", description="Scary", default=False)

    addonproperties_tabs: bpy.props.EnumProperty(items=[
        ("GENERAL", "General", "General Settings"),
        ("SPECIALS", "Specials Menus", "Specials Menus Settings"),
        ("3DVIEW", "3D View", "3D View Extensions Settings"),
        ("QUICK", "Quick Buttons", "Quick Extensions Settings"),
        ("DEBUG", "Troubleshooting", "Troubleshooting and Debug menus"),
    ])

    def draw(self, context):
        layout = self.layout
        
        def draw_general(layout):
            # General
            
            titlebox = layout.box()
            titlebox.label(text="General Settings")
            
            col = layout.column()
            row = col.row()
            row.prop(self, 'attribute_assign_menu', toggle=True)
            row.label(text='Assign and clear buttons', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Attribute-Assign-Menu-Mesh'

            row = col.row()
            ver_support = get_blender_support((3,5,0))
            row.enabled = ver_support
            row.prop(self, 'attribute_assign_menu_curves', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Assign and clear buttons' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Attribute-Assign-Menu-Curves'
            

            # row = col.row()
            # ver_support = False #get_blender_support((3,5,0))
            # row.enabled = ver_support
            # row.prop(self, 'attribute_assign_menu_pointcloud', toggle=True)
            # subrow = row.row()
            # subrow.alert = not ver_support
            # subrow.label(text='Assign and clear buttons' if ver_support else "Not supported in current blender version", icon='INFO')
            # op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            # op.wiki_url = 'Preferences-Page#Attribute-Assign-Menu-Point-Cloud'
            

            row = col.row()
            ver_support = get_blender_support((3,3,0))
            row.enabled = ver_support
            row.prop(self, 'enhanced_enum_titles', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Add ᵛᵉʳᵗᵉˣ to dropdown list entries' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Enhanced-Enum-Titles'

            row = col.row()
            ver_support = get_blender_support((4,0,0))
            row.enabled = ver_support
            row.prop(self, 'set_attribute_raw_quaterion', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Treat Quaternions as 4D Vectors' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Treat-Quaternions-as-4D-Vectors'
            
            row = col.row()
            row.prop(self, 'select_attribute_precise_facecorners', toggle=True)
            row.label(text='Select face corner edges', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Select-Face-Corner-Edges'

            row = col.row()
            row.prop(self, 'show_docs_button', toggle=True)
            row.label(text='In operator menus', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Show-Open-Documentation-Button'

        def draw_specials(layout):
            titlebox = layout.box()
            titlebox.label(text="Specials menus - extensions to the chevron menus next to selection lists")
            
            col = layout.column()

            row = col.row()
            row.prop(self, 'extra_context_menu_vg', toggle=True)
            subrow = row.row()
            subrow.label(text='Properties > Data > Vertex Groups', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Vertex-Groups-Context-Menu'

            row = col.row()
            row.prop(self, 'extra_context_menu_sk', toggle=True)
            subrow = row.row()
            subrow.label(text='Properties > Data > Shape Keys', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Shape-Keys-Context-Menu'

            row = col.row()
            row.prop(self, 'extra_context_menu_materials', toggle=True)
            subrow = row.row()
            subrow.label(text='Properties > Material', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Material-Context-Menu'

            row = col.row()
            ver_support = get_blender_support(minver_unsupported=(3,5,0))
            row.enabled = ver_support
            row.prop(self, 'extra_context_menu_uvmaps', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > UVMaps' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#UVMap-Context-Menu'

            row = col.row()
            ver_support = get_blender_support(minver_unsupported=(3,5,0))
            row.enabled = ver_support
            row.prop(self, 'extra_context_menu_fm', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > Face Maps' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Face-Maps-Context-menu'

            row = col.row()
            ver_support = get_blender_support((3,5,0))
            row.enabled = ver_support
            row.prop(self, 'add_set_attribute', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > Attributes' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Add-Set-Attribute-Operator'
            
            row = col.row()
            ver_support = get_blender_support((3,3,0))
            row.enabled = ver_support
            row.prop(self, 'extra_context_menu_color_attributes', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > Color Attributes' if ver_support else "Not supported in current blender version", icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Color-Attributes-Context-Menu'

            # row = col.row()
            # row.prop(self, 'mame_documentation_op', toggle=True)
            # row.label(text='In Attributes context menu', icon='INFO')

        def draw_3dview(layout):
            titlebox = layout.box()
            titlebox.label(text="3D View Extensions - extensions that are placed in the 3D viewport")
            col = layout.column()
            
            row = col.row()
            row.prop(self, 'extra_header_sculpt', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Menu-Bar'

            row = col.row()
            row.prop(self, 'extra_context_menu_sculpt', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Mask / Face Sets', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Sculpt-Mode-Context-Menu'

            # row = col.row()
            # row.prop(self, 'extra_context_menu_npanel_item', toggle=True)
            # subrow = row.row()
            # subrow.label(text='3D View > N-Panel > Edit', icon='INFO')

            # row = col.row()
            # row.prop(self, 'extra_context_menu_object', toggle=True)
            # subrow = row.row()
            # subrow.label(text='3D View Menu Bar > Object', icon='INFO')

            row = col.row()
            row.prop(self, 'extra_context_menu_vertex_menu', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Vertex', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Vertex-Context-Menu'

            row = col.row()
            row.prop(self, 'extra_context_menu_edge_menu', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Edge', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Edge-Context-Menu'

            row = col.row()
            row.prop(self, 'extra_context_menu_face_menu', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Face', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Face-Context-Menu'

        def draw_quick(layout):
            titlebox = layout.box()
            titlebox.label(text="Quick Buttons - Extra buttons that repeat last actions or other")
            col = layout.column()

            # row = col.row()
            # row.prop(self, 'extra_context_menu_geometry_data', toggle=True)
            # subrow = row.row()
            # subrow.label(text='Properties > Data > Geometry Data', icon='INFO')

            # row = col.row()
            # row.prop(self, 'quick_shelf_enable', toggle=True)
            # subrow = row.row()
            # subrow.label(text='Properties > Data > Attributes', icon='INFO')

            # subbox = col.box()
            # subbox.enabled = self.quick_shelf_enable
            # subbox_col = subbox.column()
            # row = subbox_col.row()
            # row.prop(self, 'quick_shelf_randomize', toggle=True)
            # subrow = row.row()
            # subrow.label(text='Randomize with same values', icon='INFO')

            # row = subbox_col.row()
            # row.prop(self, 'quick_shelf_convert_to_mesh_data_repeat', toggle=True)
            # subrow = row.row()
            # subrow.label(text='Re-convert to mesh data', icon='INFO')
            
            row = col.row()
            row.prop(self, 'quick_attribute_node_enable', toggle=True)
            subrow = row.row()
            subrow.label(text='Create Attribute Nodes Quickly', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Quick-Attribute-Node'

        def draw_debug(layout):
            # Debug Zone
            titlebox = layout.box()
            titlebox.label(text="Troubleshooting")
            col = layout.column(align=False)

            row = col.row()
            row.operator('window_manager.mame_open_wiki', text="Open wiki")
            row.label(text='See Documentation')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")

            row = col.row()
            row.operator('window_manager.mame_report_issue', text="Report Issue")
            row.label(text='Report issue or request feature')
            op = row.operator('window_manager.mame_report_issue', icon='QUESTION', text="")

            row = col.row()
            row.operator('window_manager.mame_save_log_file', text="Save Log File")
            row.label(text='Save log file to a text file')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Save-Log'
            
            row = col.row()
            row.prop(self, 'en_slow_logging_ops', toggle=True, text="Enable Full Logging")
            row.label(text='Slower. Enable only if required')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Enable-Full-Logging'

            row = col.row()
            row.operator('window_manager.mame_show_log', text="Show Log")
            row.label(text='Preview log')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Show-Log'
            
            row = col.row()
            row.prop(self, 'debug_zone_en', toggle=True, text="Debug Zone")
            row.label(text='Scary Spooky Skeletons', icon='ERROR')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Debug-Zone'

            if self.debug_zone_en:
                box = layout.box()
                if self.verbose_mode or self.show_hidden_blown_fuses:
                    box.prop(self, 'verbose_mode')
                box.prop(self, 'console_loglevel')
                box.prop(self, 'debug_operators')
                r = box.row()
                r.prop(self, 'register_debug_ops_on_start')
                r.operator('script.reload')
                if self.pseudo_profiler or self.show_hidden_blown_fuses:
                    box.prop(self, 'pseudo_profiler')
                box.prop(self, 'bakematerial_donotdelete')
                box.prop(self, 'disable_bpy_set_attribute')
                box.prop(self, 'disable_version_checks')
                box.prop(self, 'set_algo_tweak')
                box.prop(self, 'pinned_mesh_refcount_max', slider=False)
        
                # nothing critical will happen if this is invalid, but still it should be above the max
                if self.pinned_mesh_refcount_critical < self.pinned_mesh_refcount_max:
                    self.pinned_mesh_refcount_critical = self.pinned_mesh_refcount_max
                box.prop(self, 'pinned_mesh_refcount_critical', slider=False)

                box.prop(self, 'show_hidden_blown_fuses')
                box.prop(self, 'max_log_lines')
                box.prop(self, 'force_assign_on_selected_by_value')
                box.prop(self, 'force_assign_on_selected_by_foreach_get_foreach_set')
                box.prop(self, 'pinned_mesh_block_ref_creation')
                

        

        # Toggle this to enable tabs layout
        tabs_enabled = True

        if tabs_enabled:
            tabsrow = layout.row()
            tabsrow.prop_tabs_enum(self, 'addonproperties_tabs')
            if self.addonproperties_tabs == 'GENERAL':
                draw_general(layout)
            elif self.addonproperties_tabs == 'SPECIALS':
                draw_specials(layout)
            elif self.addonproperties_tabs == '3DVIEW':
                draw_3dview(layout)
            elif self.addonproperties_tabs == 'QUICK':
                draw_quick(layout)
            elif self.addonproperties_tabs == 'DEBUG':
                draw_debug(layout)
        else:
            draw_general(layout)
            layout.separator()
            draw_specials(layout)
            layout.separator()
            draw_3dview(layout)
            layout.separator()
            draw_quick(layout)
            layout.separator()
            draw_debug(layout)            

            
# Generic UI elements
# ------------------------------------------ 

class AttributeListItem(bpy.types.PropertyGroup):
    """
    Group of properties representing an item in mesh attribute list
    """

    b_select: bpy.props.BoolProperty(name="Selected", default=False)

    attribute_name: bpy.props.StringProperty(
           name="Attribute Name",
           description="Attribute Name",
           default= "Untitled")
    
    data_type: bpy.props.StringProperty(
           name="Data Type",
           description="Data Type",
           default= "")
    
    data_type_friendly_name: bpy.props.StringProperty(
           name="Data Type",
           description="Data Type",
           default= "")
    
    domain: bpy.props.StringProperty(
           name="Domain",
           description="Domain",
           default= "")
    
    domain_friendly_name: bpy.props.StringProperty(
           name="Domain",
           description="Domain",
           default= "")
    
    b_domain_compatible: bpy.props.BoolProperty(
            name="Boolean", 
            default=True)

    b_data_type_compatible: bpy.props.BoolProperty(
            name="Boolean", 
            default=True)

 # Generic datatypes

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


# Logging
# -----------------------------
# Might be useful for debugging
    
class ELogLevel(Enum):
    SUPER_VERBOSE = 0
    VERBOSE = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

def init_logging():
    global LOGGER
    #LOGGER = logging.getLogger(__addon_package_name__)
    #LOGGER.setLevel(logging.DEBUG)

def get_logger():
    global LOGGER
    if not LOGGER:
        init_logging()
    return LOGGER

def is_full_logging_enabled():
    """
    Some logging operations can slow down things drastically, can be enabled if needed
    """
    return get_preferences_attrib('en_slow_logging_ops') or get_preferences_attrib('console_loglevel') == 0

def log(who, message:str, level:ELogLevel):
    """
    Logs to internal set and optionally to system console
    """

    if hasattr(who, '__name__'):
        who = who.__name__
    else:
        who = "Unknown"
    
    console_message = f"[{str(time.time()).ljust(20)[-16:]}][{str(level.name)[:4]}][{who.ljust(16)[:16]}]: {message}"
    
    # if level == ELogLevel.VERBOSE or level == ELogLevel.SUPER_VERBOSE:
    #     get_logger().debug("[MAME]" + message)
    # elif level == ELogLevel.INFO:
    #     get_logger().info("[MAME]" + message)
    # elif level == ELogLevel.WARNING:
    #     get_logger().warning("[MAME]" + message)
    # elif level == ELogLevel.ERROR:
    #     get_logger().error("[MAME]" + message)
    if level.value >= get_preferences_attrib("console_loglevel"):
        print("[MAME]" + console_message)

    global LOG

    LOG.append({'level': level.name, 'message': message, 'timestamp': time.time(), 'who': who})
    while len(LOG) > get_preferences_attrib("max_log_lines"):
        LOG.pop()

class WINDOW_MANAGER_OT_mame_save_log_file(bpy.types.Operator, ExportHelper):
    """
    Saves log to a text file
    """

    bl_idname = "window_manager.mame_save_log_file"
    bl_label = "Save log file"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # Filename
    filename_ext = ".txt"

    # File filter, i guess just to show less stuff in filepath selector
    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  
    )
    
    # File path
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
        default= "mame_log"
    )

    # Overwrite protection
    check_existing: bpy.props.BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )

    # Included info list
    included_info = [
        "Blender Version",
        "Addon version",
        "Time and date",
        "Last addon operations",
        "Last addon handled exceptions",
        "This addon preferences",
        "May contain user name"
    ]

    #Uses last captured log snapshot instead of live capture
    b_use_log_snapshot: bpy.props.BoolProperty(
        name="Use Log Snapshot",
        description="Uses last captured log snapshot instead of live capture",
        default=False,
    )

    # Generic error message
    err_msg_troubleshoot = "Check:\n"\
        "* if your user account has permissions to write to this file in specified location\n"\
        "* or if other program is using the specified file"

    @classmethod
    def poll(self, context):
        
        return True
    
    def execute(self, context):
        global LOG
        global BL_INFO
        
        # Try to open file for writing
        file = None
        try:
            file = open(self.filepath, "w")
        except Exception as exc:
            if file is not None:
                try:
                    file.close()
                except Exception:
                    pass
            bpy.ops.window_manager.mame_message_box(message="Failed to create log file.\n" + self.err_msg_troubleshoot
                                                    + f"\n More info:\n{str(exc)}", width=500)
            return {'CANCELLED'}
            
        # Prepare text file
        try:
            log_text = ""

            log_text += "Mesh Attributes Extended Addon Log File\n"
            log_text += f"Version { bl_version_tuple_to_friendly_string(get_bl_info_key_value('version')) }\n"
            log_text += f"Blender version: {bpy.app.version_string}\n"
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            log_text += f"Creation Time: {date_time}\n"

            log_text += f"-----------------------\n"
            log_text += f"Log Entries\n"
            log_text += f"-----------------------\n"
            
            for i, log_el in enumerate(LOG):
                try:
                    
                    logline_temp = f"[{str(i).ljust(3)[:3]}]"\
                        f"[{str(log_el['timestamp']).ljust(16)[:16]}]"\
                        f"[{str(log_el['level'])[:4]}]"\
                        f"[{log_el['who'].ljust(16)[:16]}]:"\
                            f" {str(log_el['message'])}\n"
                    
                    # Anonymize paths
                    try:
                        username = os.getenv('username')
                        if username is not None:
                            logline_temp = logline_temp.replace(f"\\{username}\\", "\\ANONYMOUS_MAME_USER\\")
                    except Exception:
                        pass
                    log_text += logline_temp
                except Exception as exc:
                    log_text += f"Failed to write {str(i)} log element - {str(exc)}\n"
                
            log_text += f"-----------------------\n"
            log_text += f"Preferences\n"
            log_text += f"-----------------------\n"
            try:
                # Get preferences panel values
                prefs = bpy.context.preferences.addons[__addon_package_name__].preferences
                excluded_pref_attrs = ['bl_rna', 'bl_idname', 'rna_type']
                pref_attr = [attr for attr in dir(prefs) if (attr not in excluded_pref_attrs
                                                            and not callable(getattr(prefs, attr)) 
                                                            and not attr.startswith("__"))]
                
                for i, a in enumerate(pref_attr):
                    try:
                        log_text += f"[{str(i)}] {a}: {get_preferences_attrib(a)}\n"
                    except Exception as exc:
                        log_text += f"Failed to write {str(i)} log element - {str(exc)}\n"
                    
            except Exception as exc:
                log_text += f"Failed to get preferences - {str(exc)}\n"
        
        except Exception as exc:
            if file is not None:
                file.close()
            call_catastrophic_crash_handler(WINDOW_MANAGER_OT_mame_save_log_file, exc)

        try:
            file.write(log_text)
        except Exception as exc:
            try:
                file.close()
            except Exception:
                pass
            bpy.ops.window_manager.mame_message_box(message="Failed to write log to log file.\n" 
                                                    + self.err_msg_troubleshoot + f"\n More info:\n{str(exc)}", width=500)
            return {'CANCELLED'}
        
        # Close file
        try:
            file.close()
        except Exception:
            pass

        return {'FINISHED'}
    
    def invoke(self, context, _event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        header_box = col.box()
        header_box.label(text="Included information in a log file", icon='INFO')

        for el in self.included_info:
            row = col.row(align=True)
            row.label(text='', icon='DOT')
            row.label(text=el)

class CrashMessageBox(bpy.types.Operator):
    """
    Shows a crash message box + save log to file
    """
    bl_idname = "window_manager.mame_crash_handler"
    bl_label = "Mesh Attributes Menu Extended - Crash!"
    bl_options = {'REGISTER', 'INTERNAL'}

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    b_show_details: bpy.props.BoolProperty(name="Show details", description="Shows details of an exception", default = False)

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=800)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        # Grab info
        suspect_name = MAME_CRASH_HANDLER_WHO.__name__ if hasattr(MAME_CRASH_HANDLER_WHO, '__name__') else "Can't determine"
        try:
            cause = str(MAME_CRASH_HANDLER_WHAT_HAPPENED)
        except Exception:
            cause = "Unknown"
        try:
            details = str(MAME_CRASH_HANDLER_WHAT_HAPPENED)
        except Exception:
            details = "None"
        if  issubclass(type(MAME_CRASH_HANDLER_EXCEPTION), Exception):
            exc = MAME_CRASH_HANDLER_EXCEPTION
        else:
            exc = None
        
        # Show info
            
        box = layout.box()
        r = box.column()
        r.alert = True
        r.label(text="Oops! Addon has crashed", icon="ERROR")

        r = layout.row()
        r.operator_context = "INVOKE_DEFAULT"
        r.operator("window_manager.mame_save_log_file", text="Save Log File")
        r.operator("window_manager.mame_report_issue", text="Report Issue")

        r = layout.row()
        r.enabled = get_preferences_attrib("console_loglevel") > 1
        r.prop(self, 'b_show_details', toggle=True)
        if self.b_show_details or get_preferences_attrib("console_loglevel") < 2:
            box = layout.box()
            r = box.column()
            r.label(text=f"Caused by", icon="CANCEL")
            r.label(text=f"{suspect_name}")
            box = layout.box()

            r = box.column()
            r.label(text=f"Exception Type", icon="QUESTION")
            try:
                r.label(text=f"{repr(exc) if exc else 'Not available'}")
            except Exception:
                r.label(text=f"{'Unknown'}")
            box = layout.box()
            r = box.column()
            r.label(text=f"Traceback", icon="FILE_TEXT")
            for line in MAME_CRASH_HANDLER_EXCEPTION_STR.splitlines():
                r.label(text=line)
        
class ShowLog(bpy.types.Operator):
    """
    Shows MAME log
    """
    bl_idname = "window_manager.mame_show_log"
    bl_label = "Mesh Attributes Menu Extended - Log"
    bl_options = {'REGISTER', 'INTERNAL'}

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=800)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        global LOG
        r = layout.row()
        r.label(text=f"Log elements: {str(len(LOG))}, max count {str(get_preferences_attrib('max_log_lines'))}")

        for i, el in enumerate(LOG):
            alert = False
            if el['level'] == 'VERBOSE':
                icon = 'ALIGN_JUSTIFY'
            elif el['level'] == 'SUPER_VERBOSE':
                icon = 'ALIGN_FLUSH'
            elif el['level'] == 'WARNING':
                icon = 'ERROR'
                alert = True
            elif el['level'] == 'ERROR':
                icon = 'CANCEL'
                alert = True
            else:
                icon = 'INFO'
            layout.alert = alert
            r = layout.row()
            r.label(text=f"{el['message']}", icon=icon)
            

        layout.alert = False
        r = layout.row()
        r.operator("window_manager.mame_clear_log")
        
class ClearLog(bpy.types.Operator):
    """
    Clears MAME log
    """
    bl_idname = "window_manager.mame_clear_log"
    bl_label = "Clear Log"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global LOG
        LOG.clear()
        log(ClearLog, "Log cleared", ELogLevel.INFO)
        return {'FINISHED'}

# Catastrophic Error Handling
# -----------------------------
# Crash gracefully and tell the user what went wrong instead of cryptic python stuff
        
def call_catastrophic_crash_handler(who, exception:Exception):
    """
    If something went wrong
    In front of your screen
    Who you gonna call?
    CRASH HANDLER
    """
    
    # there is probably more sophiscated way to do this, but guess what, it's the simplest one and working
    global MAME_CRASH_HANDLER_WHO
    MAME_CRASH_HANDLER_WHO = who
    global MAME_CRASH_HANDLER_EXCEPTION
    MAME_CRASH_HANDLER_EXCEPTION = exception
    global MAME_CRASH_HANDLER_EXCEPTION_STR
    MAME_CRASH_HANDLER_EXCEPTION_STR = format_exc()

    
    log(str(who), MAME_CRASH_HANDLER_EXCEPTION_STR, ELogLevel.ERROR)
    
    # Create log snapshot so it won't get overwritten by new entries
    make_log_snapshot()

    # Show stuff to console
    print(MAME_CRASH_HANDLER_EXCEPTION_STR)

    # Show UI
    bpy.ops.window_manager.mame_crash_handler()

MAME_CRASH_HANDLER_WHO = None
MAME_CRASH_HANDLER_EXCEPTION:Exception = None
MAME_CRASH_HANDLER_EXCEPTION_STR:str = ''


class CrashMessageBox(bpy.types.Operator):
    """
    Shows a crash message box + save log to file
    """
    bl_idname = "window_manager.mame_crash_handler"
    bl_label = "Mesh Attributes Menu Extended - Crash!"
    bl_options = {'REGISTER', 'INTERNAL'}

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    b_show_details: bpy.props.BoolProperty(name="Show details", description="Shows details of an exception", default = False)

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=800)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        # Grab info
        suspect_name = MAME_CRASH_HANDLER_WHO.__name__ if hasattr(MAME_CRASH_HANDLER_WHO, '__name__') else "Can't determine"
        if  issubclass(type(MAME_CRASH_HANDLER_EXCEPTION), Exception):
            exc = MAME_CRASH_HANDLER_EXCEPTION
        else:
            exc = None
        
        # Show info
            
        box = layout.box()
        r = box.column()
        r.alert = True
        r.label(text="Oops! Addon has crashed", icon="ERROR")
        
        r = layout.row()
        r.alert = True
        op = r.operator("window_manager.mame_save_log_file", text="Save Log")
        op.b_use_log_snapshot = True
        r.operator("window_manager.mame_report_issue", text="Report Issue")

        r = layout.row()
        r.enabled = get_preferences_attrib("console_loglevel") > 1
        r.prop(self, 'b_show_details', toggle=True)
        if self.b_show_details or get_preferences_attrib("console_loglevel") < 2:
            box = layout.box()
            r = box.column()
            r.label(text=f"Caused by", icon="CANCEL")
            r.label(text=f"{suspect_name}")
            box = layout.box()
            r = box.column()
            r.label(text=f"Exception Type", icon="QUESTION")
            try:
                r.label(text=f"{repr(exc) if exc else 'Not available'}")
            except Exception:
                r.label(text=f"{'Unknown'}")
            box = layout.box()
            r = box.column()
            r.label(text=f"Traceback", icon="FILE_TEXT")
            for line in MAME_CRASH_HANDLER_EXCEPTION_STR.splitlines():
                r.label(text=line)


# Wiki Link
# ------------------------------------------

class OpenWiki(bpy.types.Operator):
    """Opens wiki page in default browser"""

    bl_idname = "window_manager.mame_open_wiki"
    bl_label = "Open Documentation"
    bl_options = {'REGISTER', 'INTERNAL'}

    wiki_url: bpy.props.StringProperty(name="Wiki Page", default='')

    def execute(self, context):
        url = "https://github.com/00004707/blender-mesh-attribute-menu-extended/wiki" + '/' + str(self.wiki_url)
        bpy.ops.wm.url_open(url=url)
        return {'FINISHED'}
    

def append_wiki_operator(self, context):
    """
    Adds wiki button to draw function of an operator. Operator needs to have wiki_url variable
    """
    if get_preferences_attrib("show_docs_button"):
        r = self.layout.column()
        r.separator()
        op = r.operator('window_manager.mame_open_wiki', icon='HELP')
        op.wiki_url = self.wiki_url

# Generic data types
# ------------------------------------------

class GenericBoolPropertyGroup(bpy.types.PropertyGroup):
    "list of boolean props"
    b_value: bpy.props.BoolProperty(name="Boolean", default=True)
    name: bpy.props.StringProperty(name="Name", default="")
    id: bpy.props.StringProperty(name="Identification String", default="")

class PropPanelPinMeshLastObject(bpy.types.PropertyGroup):
    "Stores a (named) reference to last object by mesh datablock"
    datablock_ref_name: bpy.props.StringProperty(name="Mesh Datablock Name")
    obj_ref_name: bpy.props.StringProperty(name="Object Datablock Name")
    workspace_name: bpy.props.StringProperty(name="Workspace in which the properties panel was seen")


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
    WINDOW_MANAGER_OT_mame_log_save_report_issue]

def register():
    "Register classes. Exception handing in init"
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    "Unregister classes. Exception handing in init"
    for c in classes:
        bpy.utils.unregister_class(c)
