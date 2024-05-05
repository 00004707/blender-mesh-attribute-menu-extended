"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Addon Preferences and helper functions

"""

# Extra Functions
# ------------------------------

from func.util_func import get_blender_support
from modules.LEGACY_etc import __addon_package_name__


def get_preferences_attrib(name:str):
    """Reads addon preferences variable

    Args:
        name (str): The name of the variable

    Returns:
        None: None
    """
    prefs = bpy.context.preferences.addons[__addon_package_name__].preferences
    return getattr(prefs, name) if hasattr(prefs, name) else None


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
    quick_attribute_node_enable: bpy.props.BoolProperty(name="Enable Quick Node", description="", default=True)
    attribute_palette_enable: bpy.props.BoolProperty(name="Enable Attribute Palette", description="", default=True)
    attribute_bookmarks_enable: bpy.props.BoolProperty(name="Enable Attribute Bookmarks", description="", default=True)
    attribute_hidden_list_enable: bpy.props.BoolProperty(name="Enable Hidden Attribute View", description="", default=True)


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
    pinned_mesh_block_ref_creation: bpy.props.BoolProperty(name="Block Pinned Mesh Reference Creation", description="Scary", default=False)
    convert_node_to_new_object_no_cleanup: bpy.props.BoolProperty(name="convert_node_to_new_object_no_cleanup", description="Scary", default=False)

    addonproperties_tabs: bpy.props.EnumProperty(items=[
        ("GENERAL", "General", "General Settings"),
        ("SPECIALS", "Specials Menus", "Specials Menus Settings"),
        ("3DVIEW", "3D View", "3D View Extensions Settings"),
        ("QUICK", "Extensions", "Extensions Settings"),
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


            if not get_preferences_attrib("enhanced_enum_titles"):
                row = col.row()
                row.alert = True
                ver_support = get_blender_support((3,3,0))
                row.enabled = ver_support
                row.prop(self, 'enhanced_enum_titles', toggle=True)
                subrow = row.row()
                subrow.alert = True #not ver_support
                #subrow.label(text='Add ᵛᵉʳᵗᵉˣ to dropdown list entries' if ver_support else "Not supported in current blender version", icon='INFO')
                subrow.label(text="Removed feature, click to hide", icon='INFO')
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
            titlebox.label(text="Extensions - Optional features")
            col = layout.column()


            row = col.row()
            row.prop(self, 'quick_attribute_node_enable', toggle=True)
            subrow = row.row()
            subrow.label(text='Create Attribute Nodes Quickly', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Quick-Attribute-Node'

            row = col.row()
            row.prop(self, 'attribute_palette_enable', toggle=True)
            subrow = row.row()
            subrow.label(text='Save values and colors to palette', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Attribute-Value-Palette'

            row = col.row()
            row.prop(self, 'attribute_bookmarks_enable', toggle=True)
            subrow = row.row()
            subrow.label(text='Bookmark Attributes', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Attribute-Bookmarks'

            row = col.row()
            row.prop(self, 'attribute_hidden_list_enable', toggle=True)
            subrow = row.row()
            subrow.label(text='View Hidden Attributes', icon='INFO')
            op = row.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
            op.wiki_url = 'Preferences-Page#Hidden-Attribute-List'




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
                box.prop(self, 'convert_node_to_new_object_no_cleanup')




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