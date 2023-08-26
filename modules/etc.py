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

def get_blender_support(minver, minver_unsupported):
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



# ------------------------------------------
# Preferences

class AddonPreferences(bpy.types.AddonPreferences):
    """
    Addon preferences definition
    """

    bl_idname = __addon_package_name__
    
    # User settings (variables)
    # ------------------------------------------

    enhanced_enum_titles: bpy.props.BoolProperty(name="Enhanced dropdown menu titles", description="If the following text -> ᶠᵃᶜᵉ, does not display correctly you can toggle it off", default=True)
    verbose_mode: bpy.props.BoolProperty(name="Verbose Logging", description="Scary", default=False)
    debug_operators: bpy.props.BoolProperty(name="Enable Debug Operators", description="Scary", default=False)
    disable_version_checks: bpy.props.BoolProperty(name="Disable Blender Version Checks", description="Scary", default=False)
    extra_context_menus: bpy.props.BoolProperty(name="Enable Extra Context Menu Entries", description="Adds extra operators to Shape Keys Menu, Vertex Group Menu and other menus", default=True)

    attribute_assign_menu: bpy.props.BoolProperty(name="Attribute Assign Menu", description="Assign and clear buttons", default=True)
    add_set_attribute: bpy.props.BoolProperty(name="Add Set Attribute to Menu", description="Set Attribute operator in dropdown menu", default=True)

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

        box = layout.box()
        box.label(text='Danger zone')
        box.prop(self, 'verbose_mode')
        box.prop(self, 'debug_operators')
        box.prop(self, 'disable_version_checks')