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
    "version": (1, 1, 0),
    "blender": (3, 1, 0),
    "location": "Properties Panel > Data Properties > Attributes",
    "description": "Extra tools to modify mesh attributes",
    "doc_url": "https://github.com/00004707/blender-mesh-attribute-menu-extended",
    "category": "Interface",
    "support": "COMMUNITY",
    "tracker_url": "https://github.com/00004707/blender-mesh-attribute-menu-extended/issues",
}

req_bl_ver = bl_info["blender"]

# Fix for reloading all addon files in blender
import importlib

if "etc" in locals():
    import importlib
    for mod in [etc,func,static_data,gui,ops,quick_ops,variable_data]:
        importlib.reload(mod)
else:
    import bpy
    from .modules import etc
    from .modules import func
    from .modules import static_data
    from .modules import variable_data
    from .modules import gui
    from .modules import ops
    from .modules import debug
    from .modules import quick_ops

# This is also the correct order of registering
reg_modules = [etc, variable_data, gui, ops, quick_ops, debug]

"""
[!] Important notes

Attribute access is prone to unexpected behaviour.
Using operators, changing context, object mode and possibly other actions DESTROY the variables holding the attribute
ie. using a = obj.data.attributes.active, and then using some operator might change the attribute that you're working on!
Please use funciton in func file to set and get active attribute, as setting the obj.data.attributes.active can be broken in some scenarios

"""

# Class Registration
# ------------------------------------------

# Classes for unsupported blender versions
unsupported_ver_classes = [
    etc.AddonPreferencesUnsupportedBlenderVer, 
    etc.MAMEBlenderUpdate, 
    etc.MAMEDisable
]

def register():

    if bpy.app.version < req_bl_ver:
        for c in unsupported_ver_classes:
            bpy.utils.register_class(c)
    else:
        try:
            etc.register()
            variable_data.register()
            ops.register()
            gui.register()
            quick_ops.register()
            debug.register()
        except Exception as exc:
            unregister()
            raise exc
        
        # Logging
        etc.init_logging()

        # Global bl_info
        etc.set_global_bl_info(bl_info)

        # Per-object Property Values
        bpy.types.Mesh.MAME_PropValues = bpy.props.PointerProperty(type=variable_data.MAME_PropValues)
        
        # This barely has any features, if it fails, at least rest of the addon will work
        try:
            bpy.types.PointCloud.MAME_PropValues = bpy.props.PointerProperty(type=variable_data.MAME_PropValues)
        except Exception:
            pass
        
        if bpy.app.version >= (3,5,0):
            bpy.types.Curves.MAME_PropValues = bpy.props.PointerProperty(type=variable_data.MAME_PropValues)
        bpy.types.WindowManager.MAME_GUIPropValues = bpy.props.PointerProperty(type=variable_data.MAME_GUIPropValues)
        bpy.types.WindowManager.mame_image_ref = bpy.props.PointerProperty(name='Image', type=bpy.types.Image)

        
def unregister():
    print(f"[MAME] Shutting down")
    if bpy.app.version < req_bl_ver:
        for c in unsupported_ver_classes:
            bpy.utils.unregister_class(c)
    else:
        try:
            
            for el in reg_modules:
                name = el.__name__ if hasattr(el, '__name__') else str(el)
                try:
                    print(f"[MAME] Unregistering {name}")
                    el.unregister()
                except Exception:
                    print(f"[MAME] Failed to unregister {name}")
                    continue

            del bpy.types.Mesh.MAME_PropValues
            
            # This barely has any features, if it fails, at least rest of the addon will work
            try:
                del bpy.types.PointCloud.MAME_PropValues
            except Exception:
                pass

            if bpy.app.version >= (3,5,0):
                del bpy.types.Curves.MAME_PropValues
            del bpy.types.WindowManager.MAME_GUIPropValues
            del bpy.types.WindowManager.mame_image_ref
        except Exception:
            pass
            
        print(f"[MAME] bye")

if __name__ == "__main__":
    register()
