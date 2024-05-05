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
import importlib, os, bpy, sys

if "etc" in locals():
    import importlib
    for mod in [LEGACY_etc,func, util_func, exceptions, property_groups, enum_func,   LEGACY_static_data,LEGACY_gui,LEGACY_ops,LEGACY_quick_ops,   LEGACY_variable_data,  ]:
        importlib.reload(mod)
else:
    import bpy
    from .modules import LEGACY_etc
    from .modules import func
    from .modules import LEGACY_static_data
    from .modules import LEGACY_variable_data
    from .modules import LEGACY_gui
    from .modules import LEGACY_ops
    from .modules import debug
    from .modules import LEGACY_quick_ops
    from .etc import exceptions
    from .etc import property_groups
    from .func import enum_func
    from .func import util_func



# This is also the correct order of registering
reg_modules = [LEGACY_etc,func, util_func, exceptions, property_groups, enum_func,   LEGACY_static_data,LEGACY_gui,LEGACY_ops,LEGACY_quick_ops,   LEGACY_variable_data,  ]

"""
[!] Important notes

Attribute access is prone to unexpected behaviour.
Using operators, changing context, object mode and possibly other actions DESTROY the variables holding the attribute
ie. using a = obj.data.attributes.active, and then using some operator might change the attribute that you're working on!
Please use funciton in func file to set and get active attribute, as setting the obj.data.attributes.active can be broken in some scenarios

"""

# import importlib, os, sys

# Class Registration
# ------------------------------------------

# excluded_files = ['__init__.py']
# excluded_dirs = ['__pycache__', '.git']
# max_depth = 10
# found_modules = []
# addon_root = os.path.dirname(__file__)

# register_exception = None

init_module = sys.modules[__name__]

# Reload trigger

# b_reload = False
# if 'bpy' not in locals():
#     loaded_modules = {}
# else:
#     print('[MAME] Reloading')
#     b_reload = True

# # Load bpy now
# import bpy

# def look_for_modules(directory, depth=0):
#     if depth == max_depth:
#         print(f"[MAME] Directory recursion depth maximum hit for: {directory}")
#     try:
#         for item_name in os.listdir(directory):
#             item_path = os.path.join(directory, item_name)
            
#             # If it's a directory, search deeper
#             if os.path.isdir(item_path) and item_name not in excluded_dirs:
#                 look_for_modules(item_path, depth+1)

#             # If it's py file, mark it to load
#             if os.path.isfile(item_path) and item_name not in excluded_files:
#                 if item_name[-3:] == '.py':
#                     found_modules.append({'name': item_name[:len(item_name)-3], 
#                                             'relative_path': item_path[len(addon_root):-3]})
#     except FileNotFoundError:
#         return

# def register_for_unsupported_blender_version():
#     from .modules import etc
    
#     # Classes for unsupported blender versions
#     unsupported_ver_classes = [
#         etc.AddonPreferencesUnsupportedBlenderVer, 
#         etc.MAMEBlenderUpdate, 
#         etc.MAMEDisable
#     ]

#     # Register unsupported info classes
#     if bpy.app.version < req_bl_ver:
#         for c in unsupported_ver_classes:
#             bpy.utils.register_class(c)

# def unregister_for_unsupported_blender_version():
#     pass

# # Imports, keep out of register
# look_for_modules(addon_root)

# if b_reload:
#     for loaded_module in loaded_modules:
#         try:
#             importlib.reload(loaded_modules[loaded_module]['module'])
#             print(f'[MAME][INFO ] Module {loaded_modules[loaded_module]["name"]} reloaded')
#         except Exception:
#             continue


# Store in separated variable, as blender won't clear locals()
# Looking in loaded_modules might cause module to load&store refernece twice 
# unique_weights = []
# loaded_modules = []

# for fm in found_modules:
#     # Load found module
#     mod_filepath = fm['relative_path'].replace('\\', '.')
#     m = importlib.import_module(name=mod_filepath, package=__name__)
    
#     # Set weight
#     if hasattr(m, 'register_weight'):
#         weight = m.register_weight
#     else:
#         weight = 0

#     # Make sure weight is unique
#     while weight in unique_weights:
#         weight += 1

#     unique_weights.append(weight)

#     # Reload if loaded (blender won't)
#     #if b_reload or weight in loaded_modules:
#     importlib.reload(m)
#     #    #importlib.reload(loaded_modules[weight]['module'])
#     print(f'[MAME][INFO ] Module {fm["name"]} reloaded')

#     # Store module
#     loaded_modules[weight] = {'name': fm['name'], 'module': m}


def register():
    # In directory of init, look for directories with py files and load
    
    # print(sorted(loaded_modules, reverse=True))
    # for loaded_module_weight in sorted(loaded_modules, reverse=True):
    #     # Trigger register
    #     loaded_module = loaded_modules[loaded_module_weight]['module']
    #     if hasattr(loaded_module, 'register'):
    #         try:
    #             print(f"[MAME] Registering {loaded_modules[loaded_module_weight]['name']}")
    #             loaded_module.register(init_module)
    #         except Exception as exc:
    #             unregister()
    #             raise exc

    for mod in reg_modules:
        try:
            print(mod.__name__)
            mod.register(init_module)
        except Exception as exc:
            print(f"Failed to register {str(exc)}")

        # except Exception as exc:
        #     print(f'[MAME][ERROR] Module {fm["name"]} failed to register : {str(exc)}')
            
    print("[MAME] Successfully loaded")
    return
    # # Logging
    # loaded_modules['etc'].init_logging()

    # # Global bl_info
    # loaded_modules['etc'].set_global_bl_info(bl_info)

    # # Module reference
    # loaded_modules['etc'].set_addon_self_module()

    # # Info
    # loaded_modules['etc'].log(None, f"Working directory: {loaded_modules['etc'].get_addon_directory()}", 
    #                           loaded_modules['etc'].ELogLevel.VERBOSE)


    # Per-object Property Values
    bpy.types.Mesh.MAME_PropValues = bpy.props.PointerProperty(type=loaded_modules['variable_data'].MAME_PropValues)
    
    # This barely has any features, if it fails, at least rest of the addon will work
    try:
        bpy.types.PointCloud.MAME_PropValues = bpy.props.PointerProperty(type=loaded_modules['variable_data'].MAME_PropValues)
    except Exception:
        pass
    
    if bpy.app.version >= (3,5,0):
        bpy.types.Curves.MAME_PropValues = bpy.props.PointerProperty(type=loaded_modules['variable_data'].MAME_PropValues)
    bpy.types.WindowManager.MAME_GUIPropValues = bpy.props.PointerProperty(type=loaded_modules['variable_data'].MAME_GUIPropValues)
    bpy.types.WindowManager.mame_image_ref = bpy.props.PointerProperty(name='Image', type=bpy.types.Image)

        
def unregister():
    print(f"[MAME] Shutting down")
    # if bpy.app.version < req_bl_ver:
    #     unregister_for_unsupported_blender_version()
    # #     for c in unsupported_ver_classes:
    # #         bpy.utils.unregister_class(c)
    # # else:
    # try:
        
    #     # for el in reg_modules:
    #     #     name = el.__name__ if hasattr(el, '__name__') else str(el)
    #     #     try:
    #     #         print(f"[MAME] Unregistering {name}")
    #     #         el.unregister()
    #     #     except Exception:
    #     #         print(f"[MAME] Failed to unregister {name}")
    #     #         continue

    #     for module_weight in loaded_modules:
    #         name = loaded_modules[module_weight]['name']
    #         module_ref = loaded_modules[module_weight]['module']
    #         try:
    #             print(f"[MAME] Unregistering {name}")
    #             module_ref.unregister(init_module)
    #         except Exception as exc:
    #             print(f"[MAME] Failed to unregister {name} - {str(exc)}")
    #             continue

    #     # del bpy.types.Mesh.MAME_PropValues
        
    #     # # This barely has any features, if it fails, at least rest of the addon will work
    #     # try:
    #     #     del bpy.types.PointCloud.MAME_PropValues
    #     # except Exception:
    #     #     pass

    #     # if bpy.app.version >= (3,5,0):
    #     #     del bpy.types.Curves.MAME_PropValues
    #     # del bpy.types.WindowManager.MAME_GUIPropValues
    #     # del bpy.types.WindowManager.mame_image_ref
    # except Exception as exc:
    #     print(f"[MAME] Failed to unregister types - {str(exc)}")
    #     pass
    
    for c in reg_modules:
        try:
            c.unregister(init_module)
        except Exception as exc:
            print(f"Failed to unregister: {str(exc)}")
    print(f"[MAME] bye")
    # if register_exception:
    #     raise register_exception

if __name__ == "__main__":
    register()
