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

import bpy
import time

# Constants
# ------------------------------------------
__addon_package_name__ = __package__.replace('.modules','')

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
    if bpy.app.version >= (3,3,0):
        return get_preferences_attrib('enhanced_enum_titles')
    else:
        return False

# Fake operators
# ------------------------------

class FakeFaceCornerSpillDisabledOperator(bpy.types.Operator):
    """
    Fake operator to occupy GUI place
    .disabled is not available for properties in gui, so this is the hack
    """

    bl_idname = "mesh.always_disabled_face_corner_spill_operator"
    bl_label = "Fake operator to occupy GUI place"
    bl_description = "Enable Face Corner Spill"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Active attribute is not on Face Corner domain")
        return False

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

class MAMEReportIssue(bpy.types.Operator):
    """
    Reports issue with the addon
    """

    bl_idname = "mame.report_issue"
    bl_label = "Report Issue"
    bl_description = "Open github page to report the issue"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        bpy.ops.wm.url_open(url="https://github.com/00004707/blender-mesh-attribute-menu-extended/issues")
        return {'FINISHED'}
    
    @classmethod
    def poll(self, context):
        return True


# Profiler
# ------------------------------

profiler_timestamp_start = 0

def pseudo_profiler_init():
    global profiler_timestamp_start
    profiler_timestamp_start = time.time()

def pseudo_profiler(info_string:str):
    if get_preferences_attrib("pseudo_profiler"):
        print(f"[PROFILER][{time.time()-profiler_timestamp_start}] {info_string}")

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

    enhanced_enum_titles: bpy.props.BoolProperty(name="Enhanced dropdown menu titles", description="If the following text -> ᶠᵃᶜᵉ, does not display correctly you can toggle it off", default=True)
    
    disable_bpy_set_attribute: bpy.props.BoolProperty(name="Force Disable bpy.ops.mesh.attribute_set", description="Uses add-on alghortitm only to set the values in edit mode", default=False)
    debug_zone_en: bpy.props.BoolProperty(name="Show", description="Scary", default=False)
    verbose_mode: bpy.props.BoolProperty(name="Verbose Logging", description="Scary", default=False)
    debug_operators: bpy.props.BoolProperty(name="Enable Debug Operators", description="Scary", default=False)
    pseudo_profiler: bpy.props.BoolProperty(name="Enable pseudo-profiler", description="Scary", default=False)
    disable_version_checks: bpy.props.BoolProperty(name="Disable Blender Version Checks", description="Scary", default=False)
    set_algo_tweak: bpy.props.FloatProperty(name="set_algo_tweak", description="set_attribute_values()", default=0.15)

    extra_context_menus: bpy.props.BoolProperty(name="Enable Extra Context Menu Entries", description="Adds extra operators to Shape Keys Menu, Vertex Group Menu and other menus", default=True)

    attribute_assign_menu: bpy.props.BoolProperty(name="Attribute Assign Menu", description="Assign and clear buttons", default=True)
    add_set_attribute: bpy.props.BoolProperty(name="Add \"Set Attribute\" to Specials Menu", description="Set Attribute operator in dropdown menu", default=True)

    extra_context_menu_vg: bpy.props.BoolProperty(name="Vertex Groups Menu", description="Adds extra operators to Vertex Group Menu", default=True)
    extra_context_menu_sk: bpy.props.BoolProperty(name="Shape Keys Menu", description="Adds extra operators to Shape Keys Menu", default=True)
    extra_context_menu_uvmaps: bpy.props.BoolProperty(name="UVMap Menu", description="Adds extra operators to UVMap Menu", default=True)
    extra_context_menu_fm: bpy.props.BoolProperty(name="Face Maps Menu", description="Adds extra operators to Face Maps Menu", default=True)
    extra_context_menu_sculpt: bpy.props.BoolProperty(name="Sculpt Mode Menus", description="Adds extra operators to sculpting 3D View", default=True)
    extra_context_menu_npanel_item: bpy.props.BoolProperty(name="N-Panel Item Tab", description="Adds extra operators to N-Panel Item Tab in Edit Mode", default=True)
    extra_context_menu_materials: bpy.props.BoolProperty(name="Materials Menu", description="Adds extra operators to Materials Menu", default=True)
    extra_context_menu_edge_menu: bpy.props.BoolProperty(name="Edge Context Menu", description="Adds extra operators to Edge Context Menu in Edit Mode", default=True)
    extra_context_menu_vertex_menu: bpy.props.BoolProperty(name="Vertex Context Menu", description="Adds extra operators to Vertex Context Menu in Edit Mode", default=True)
    extra_context_menu_face_menu: bpy.props.BoolProperty(name="Face Context Menu", description="Adds extra operators to Face Context Menu in Edit Mode", default=True)
    extra_context_menu_object: bpy.props.BoolProperty(name="Object Context Menu", description="Adds extra operators to Object Context Menu in Object Mode", default=True)
    extra_context_menu_geometry_data: bpy.props.BoolProperty(name="Geometry Data Menu", description="Adds extra operators to Geometry Data Menu", default=True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Features')
        row = box.row()
        row.prop(self, 'attribute_assign_menu')
        row.label(text='Assign and clear buttons', icon='INFO')

        if bpy.app.version >= (3,5,0):
            row = box.row()
            row.prop(self, 'add_set_attribute')
            row.label(text='Set Attribute operator in dropdown menu', icon='INFO')

        if bpy.app.version >= (3,3,0):
            row = box.row()
            row.prop(self, 'enhanced_enum_titles')
            row.label(text='Add ᵛᵉʳᵗᵉˣ to dropdown list entries', icon='INFO')


        # box = layout.box()
        # box.label(text='Extra Context Menu Operators')
        # row = box.row()
        # row.prop(self, 'extra_context_menus')
        # row.label(text='Extra entries for convenience', icon='INFO')
        
        # if self.extra_context_menus:
        #     box2 = box.box()
        #     col = box2.column()
        #     col.label(text='All individual context menu extensions')
            
        #     row = col.row()
        #     row.prop(self, 'extra_context_menu_vg', toggle=True)
        #     row.prop(self, 'extra_context_menu_sk', toggle=True)
        #     row.prop(self, 'extra_context_menu_uvmaps', toggle=True)

        #     row = col.row()
        #     row.prop(self, 'extra_context_menu_fm', toggle=True)
        #     row.prop(self, 'extra_context_menu_sculpt', toggle=True)
        #     row.prop(self, 'extra_context_menu_npanel_item', toggle=True)

        #     row = col.row()
        #     row.prop(self, 'extra_context_menu_materials', toggle=True)
        #     row.prop(self, 'extra_context_menu_object', toggle=True)
        #     row.prop(self, 'extra_context_menu_geometry_data', toggle=True)

        #     row = col.row()
        #     row.prop(self, 'extra_context_menu_vertex_menu', toggle=True)
        #     row.prop(self, 'extra_context_menu_edge_menu', toggle=True)
        #     row.prop(self, 'extra_context_menu_face_menu', toggle=True)



        # box = layout.box()
        # box.label(text='Extras')
        # row = box.row()

        # row.prop(self, 'enhanced_enum_titles')
        # row.label(text='Enables effects like ᶠᵃᶜᵉ', icon='INFO')

        # Debug Zone
        box = layout.box()
        row = box.row()
        row.prop(self, 'debug_zone_en', toggle=True, text="Debug Zone")
        row.label(text='Scary Spooky Skeletons', icon='ERROR')

        if self.debug_zone_en:
            box = box.box()
            box.prop(self, 'verbose_mode')
            box.prop(self, 'debug_operators')
            box.prop(self, 'pseudo_profiler')
            box.prop(self, 'disable_bpy_set_attribute')
            box.prop(self, 'disable_version_checks')
            box.prop(self, 'set_algo_tweak')
            