
# excs
# ------------------------------------------

import bpy

__addon_package_name__ = __package__.replace('.modules','')

# will enable debug verbose logging to console
verbose_mode = False
enable_debug_tester = False

class MeshDataReadException(Exception):
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[READ] " + self.function_name + ": " + self.message)

class MeshDataWriteException(Exception):
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[WRITE] " + self.function_name + ": " + self.message)

# Extra Functions
# ------------------------------

def get_preferences_attrib(name:str):
    prefs = bpy.context.preferences.addons[__addon_package_name__].preferences
    return getattr(prefs, name) if hasattr(prefs, name) else None

def get_blender_support(minver, minver_unsupported):
    if get_preferences_attrib('disable_version_checks'):
        return True
    
    return (minver is None or bpy.app.version >= minver) and (minver_unsupported is None or bpy.app.version < minver_unsupported)

def get_enhanced_enum_titles_enabled():
    return bool(bpy.app.version >= (3,3,0)) #and get_preferences_attrib('enhanced_enum_titles')


# ------------------------------------------
# Preferences

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __addon_package_name__
    
    enhanced_enum_titles: bpy.props.BoolProperty(name="Enhanced dropdown menu titles", description="If the following text -> ᶠᵃᶜᵉ, does not display correctly you can toggle it off", default=True)
    verbose_mode: bpy.props.BoolProperty(name="Verbose Logging", description="Scary", default=False)
    debug_operators: bpy.props.BoolProperty(name="Enable Debug Operators", description="Scary", default=False)
    disable_version_checks: bpy.props.BoolProperty(name="Disable Blender Version Checks", description="Scary", default=False)
    extra_context_menus: bpy.props.BoolProperty(name="Enable Extra Context Menu Entries", description="Adds extra operators to Shape Keys Menu, Vertex Group Menu and other menus", default=True)

    attribute_assign_menu: bpy.props.BoolProperty(name="Attribute Assign Buttons", description="Assign and clear buttons", default=True)
    add_set_attribute: bpy.props.BoolProperty(name="Add Set Attribute to Context Menu", description="Set Attribute operator in dropdown menu", default=True)


    extra_context_menu_vg: bpy.props.BoolProperty(name="Vertex Groups Menu", description="Adds extra operators to Vertex Group Menu", default=True)
    extra_context_menu_sk: bpy.props.BoolProperty(name="Shape Keys Menu", description="Adds extra operators to Shape Keys Menu", default=True)
    extra_context_menu_uvmaps: bpy.props.BoolProperty(name="UVMap Menu", description="Adds extra operators to UVMap Menu", default=True)
    extra_context_menu_fm: bpy.props.BoolProperty(name="Face Maps Menu", description="Adds extra operators to Face Maps Menu", default=True)
    extra_context_menu_sculpt: bpy.props.BoolProperty(name="Mask & Face Sets Menus", description="Adds extra operators to sculpting 3D View menus", default=True)
    extra_header_sculpt: bpy.props.BoolProperty(name="Sculpt Mode Header", description="Adds extra operators to sculpting 3D View", default=True)
    extra_context_menu_npanel_item: bpy.props.BoolProperty(name="N-Panel Item Tab", description="Adds extra operators to N-Panel Item Tab in Edit Mode", default=True)
    extra_context_menu_materials: bpy.props.BoolProperty(name="Materials Menu", description="Adds extra operators to Materials Menu", default=True)
    extra_context_menu_edge_menu: bpy.props.BoolProperty(name="Edge Context Menu", description="Adds extra operators to Edge Context Menu in Edit Mode", default=True)
    extra_context_menu_vertex_menu: bpy.props.BoolProperty(name="Vertex Context Menu", description="Adds extra operators to Vertex Context Menu in Edit Mode", default=True)
    extra_context_menu_face_menu: bpy.props.BoolProperty(name="Face Context Menu", description="Adds extra operators to Face Context Menu in Edit Mode", default=True)
    extra_context_menu_object: bpy.props.BoolProperty(name="Object Context Menu", description="Adds extra operators to Object Context Menu in Object Mode", default=True)
    extra_context_menu_geometry_data: bpy.props.BoolProperty(name="Geometry Data Menu", description="Adds extra operators to Geometry Data Menu", default=True)

    set_data_use_foreach_domain_count: bpy.props.IntProperty(name="Use alternative mesh setting alghoritm from", description="_foreach_set", default=1000)


    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Toggleable Extensions')
        row = box.row()
        # row.prop(self, 'extra_context_menus')
        # row.label(text='Extra entries for convenience')
        
        if self.extra_context_menus:
            box2 = box.box()
            col = box2.column()
            col.label(text='Properties Panel Extensions')
            
            row = col.row()
            row.prop(self, 'attribute_assign_menu', toggle=True)
            row.label(text='Properites > Data > Attributes')

            row = col.row()
            row.prop(self, 'extra_context_menu_vg', toggle=True)
            row.label(text='Properties > Data > Vertex Groups')

            row = col.row()
            row.prop(self, 'extra_context_menu_sk', toggle=True)
            row.label(text='Properties > Data > Shape Keys')

            row = col.row()
            row.prop(self, 'extra_context_menu_materials', toggle=True)
            row.label(text='Properties > Material')

            row = col.row()
            row.prop(self, 'add_set_attribute', toggle=True)
            row.label(text='Properites > Data > Attributes')
            
            box2 = box.box()
            col = box2.column()
            col.label(text='Menu Bar/3D View Context Menu Extensions')

            row = col.row()
            row.prop(self, 'extra_context_menu_sculpt', toggle=True)
            row.label(text='3D View Menu Bar > Mask / Face Sets')
            
            row = col.row()
            row.prop(self, 'extra_context_menu_object', toggle=True)
            row.label(text='3D View Menu Bar > Object')
            #row.prop(self, 'extra_context_menu_fm', toggle=True)
            #row.prop(self, 'extra_context_menu_uvmaps', toggle=True)
            #row.prop(self, 'extra_context_menu_npanel_item', toggle=True)
            #row.prop(self, 'extra_context_menu_geometry_data', toggle=True)

            row = col.row()
            row.prop(self, 'extra_context_menu_vertex_menu', toggle=True)
            row.label(text='3D View Menu Bar > Vertex')

            row = col.row()
            row.prop(self, 'extra_context_menu_edge_menu', toggle=True)
            row.label(text='3D View Menu Bar > Edge')

            row = col.row()
            row.prop(self, 'extra_context_menu_face_menu', toggle=True)
            row.label(text='3D View Menu Bar > Face')

            box2 = box.box()
            col = box2.column()
            col.label(text='3D View Extensions')
            row = col.row()
            row.prop(self, 'extra_header_sculpt', toggle=True)
            row.label(text='3D View Menu Bar, next to Face Sets')

            




        # box = layout.box()
        # box.label(text='Extras')
        # row = box.row()

        # row.prop(self, 'enhanced_enum_titles')
        # row.label(text='Enables effects like ᶠᵃᶜᵉ')

        box = layout.box()
        box.label(text='Danger zone')
        box.prop(self, 'verbose_mode')
        box.prop(self, 'debug_operators')
        box.prop(self, 'disable_version_checks')