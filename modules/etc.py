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
LARGE_MESH_VERTICES_COUNT = 500000


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
# aka printer with timestamps

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
    
    # General
    enhanced_enum_titles: bpy.props.BoolProperty(name="Enhanced dropdown menu titles", description="If the following text -> ᶠᵃᶜᵉ, does not display correctly you can toggle it off", default=True)
    attribute_assign_menu: bpy.props.BoolProperty(name="Attribute Assign Menu", description="Assign and clear buttons", default=True)
    set_attribute_raw_quaterion: bpy.props.BoolProperty(name="Set Raw Quaternions Value", description="If you want to use quaternion attributes as 4D vectors instead of quaternions, enable this", default=True)
    select_attribute_precise_facecorners: bpy.props.BoolProperty(name="Precise Face Corner Select (Slow)", description="If you want to select individual edges that identify a face corner, this has to be enabled. Not requried for face painting", default=False)

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
    verbose_mode: bpy.props.BoolProperty(name="Verbose Logging", description="Scary", default=False)
    debug_operators: bpy.props.BoolProperty(name="Enable Debug Operators", description="Scary", default=False)
    pseudo_profiler: bpy.props.BoolProperty(name="Enable pseudo-profiler", description="Scary", default=False)
    disable_version_checks: bpy.props.BoolProperty(name="Disable Blender Version Checks", description="Scary", default=False)
    set_algo_tweak: bpy.props.FloatProperty(name="set_algo_tweak", description="set_attribute_values()", default=0.15)
    disable_bpy_set_attribute: bpy.props.BoolProperty(name="Force Disable bpy.ops.mesh.attribute_set", description="Uses add-on alghortitm only to set the values in edit mode", default=False)
    bakematerial_donotdelete: bpy.props.BoolProperty(name="bakematerial_donotdelete", description="", default=False)

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

            row = col.row()
            ver_support = get_blender_support((3,3,0))
            row.enabled = ver_support
            row.prop(self, 'enhanced_enum_titles', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Add ᵛᵉʳᵗᵉˣ to dropdown list entries' if ver_support else "Not supported in current blender version", icon='INFO')
            
            row = col.row()
            ver_support = get_blender_support((4,0,0))
            row.enabled = ver_support
            row.prop(self, 'set_attribute_raw_quaterion', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Treat Quaternions as 4D Vectors' if ver_support else "Not supported in current blender version", icon='INFO')
     
            row = col.row()
            row.prop(self, 'select_attribute_precise_facecorners', toggle=True)
            row.label(text='Select face corner edges', icon='INFO')
       
            

        def draw_specials(layout):
            titlebox = layout.box()
            titlebox.label(text="Specials menus - extensions to the chevron menus next to selection lists")
            
            col = layout.column()

            row = col.row()
            row.prop(self, 'extra_context_menu_vg', toggle=True)
            subrow = row.row()
            subrow.label(text='Properties > Data > Vertex Groups', icon='INFO')

            row = col.row()
            row.prop(self, 'extra_context_menu_sk', toggle=True)
            subrow = row.row()
            subrow.label(text='Properties > Data > Shape Keys', icon='INFO')

            row = col.row()
            row.prop(self, 'extra_context_menu_materials', toggle=True)
            subrow = row.row()
            subrow.label(text='Properties > Material', icon='INFO')

            row = col.row()
            ver_support = get_blender_support(minver_unsupported=(3,5,0))
            row.enabled = ver_support
            row.prop(self, 'extra_context_menu_uvmaps', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > UVMaps' if ver_support else "Not supported in current blender version", icon='INFO')

            row = col.row()
            ver_support = get_blender_support(minver_unsupported=(3,5,0))
            row.enabled = ver_support
            row.prop(self, 'extra_context_menu_fm', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > Face Maps' if ver_support else "Not supported in current blender version", icon='INFO')

            row = col.row()
            ver_support = get_blender_support((3,5,0))
            row.enabled = ver_support
            row.prop(self, 'add_set_attribute', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > Attributes' if ver_support else "Not supported in current blender version", icon='INFO')

            row = col.row()
            ver_support = get_blender_support((3,3,0))
            row.enabled = ver_support
            row.prop(self, 'extra_context_menu_color_attributes', toggle=True)
            subrow = row.row()
            subrow.alert = not ver_support
            subrow.label(text='Properties > Data > Color Attributes' if ver_support else "Not supported in current blender version", icon='INFO')

        def draw_3dview(layout):
            titlebox = layout.box()
            titlebox.label(text="3D View Extensions - extensions that are placed in the 3D viewport")
            col = layout.column()
            
            row = col.row()
            row.prop(self, 'extra_header_sculpt', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar', icon='INFO')

            row = col.row()
            row.prop(self, 'extra_context_menu_sculpt', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Mask / Face Sets', icon='INFO')

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

            row = col.row()
            row.prop(self, 'extra_context_menu_edge_menu', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Edge', icon='INFO')

            row = col.row()
            row.prop(self, 'extra_context_menu_face_menu', toggle=True)
            subrow = row.row()
            subrow.label(text='3D View Menu Bar > Face', icon='INFO')

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

        def draw_debug(layout):
                        # Debug Zone
            titlebox = layout.box()
            titlebox.label(text="Troubleshooting")
            col = layout.column(align=False)

            row = col.row()
            row.operator('mame.report_issue', text="Report Issue")
            row.label(text='Report issue or request feature')
            

            row = col.row()
            row.prop(self, 'debug_zone_en', toggle=True, text="Debug Zone")
            row.label(text='Scary Spooky Skeletons', icon='ERROR')

            if self.debug_zone_en:
                box = layout.box()
                box.prop(self, 'verbose_mode')
                box.prop(self, 'debug_operators')
                box.prop(self, 'pseudo_profiler')
                box.prop(self, 'bakematerial_donotdelete')
                box.prop(self, 'disable_bpy_set_attribute')
                box.prop(self, 'disable_version_checks')
                box.prop(self, 'set_algo_tweak')
        

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


# Generic data types
# ------------------------------------------

class GenericBoolPropertyGroup(bpy.types.PropertyGroup):
    "list of boolean props"
    b_value: bpy.props.BoolProperty(name="Boolean", default=True)
    name: bpy.props.StringProperty(name="Name", default="")
    id: bpy.props.StringProperty(name="Identification String", default="")

