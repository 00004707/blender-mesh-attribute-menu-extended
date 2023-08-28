"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

bl_info = {
    "name": "Mesh Attributes Menu eXtended",
    "author": "00004707",
    "version": (0, 5, 0),
    "blender": (3, 1, 0),
    "location": "Properties Panel > Data Properties > Attributes",
    "description": "Extra tools to modify mesh attributes",
    "warning": "",
    "doc_url": "https://github.com/00004707/blender-mesh-attribute-menu-extended",
    "category": "Interface",
    "support": "COMMUNITY",
    "tracker_url": "https://github.com/00004707/blender-mesh-attribute-menu-extended/issues",
}

# Fix for reloading all addon files in blender
import importlib

if "etc" in locals():
    import importlib

    for mod in [etc, func, data, gui, ops]:
        importlib.reload(mod)
else:
    import bpy
    from .modules import etc
    from .modules import func
    from .modules import data
    from .modules import gui
    from .modules import ops
    from .modules import debug
"""
[!] Important notes

Attribute access is prone to unexpected behaviour.
Using operators, changing context, object mode and possibly other actions DESTROY the variables holding the attribute
ie. using a = obj.data.attributes.active, and then using some operator might change the attribute that you're working on!
Please use funciton in func file to set active attribute, as setting the obj.data.attributes.active can be broken in some scenarios

"""

# Class Registration
# ------------------------------------------

# Main
classes = [
    etc.AddonPreferences,
    data.MAME_PropValues,
    ops.CreateAttribFromData,
    ops.AssignActiveAttribValueToSelection,
    ops.ConditionalSelection,
    ops.DuplicateAttribute,
    ops.InvertAttribute,
    ops.RemoveAllAttribute,
    ops.ConvertToMeshData,
    ops.CopyAttributeToSelected,
    ops.DeSelectDomainWithAttributeZeroValue,
    ops.SelectDomainWithAttributeZeroValue,
    ops.AttributeResolveNameCollisions,
    ops.ReadValueFromSelectedDomains,
]

# Debug
classes += [debug.MAMETestAll, debug.MAMECreateAllAttributes]

# Blender stuff
# ------------------------------------------

def register():
    for c in classes:
        bpy.utils.register_class(c)

    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.append(gui.attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.append(
        gui.attribute_context_menu_extension
    )

    # Per-object Property Values
    bpy.types.Object.MAME_PropValues = bpy.props.PointerProperty(
        type=data.MAME_PropValues
    )


def unregister():
    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.remove(gui.attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.remove(
        gui.attribute_context_menu_extension
    )

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
