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
    "version": (1, 0, 0),
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
reg_modules = [etc, variable_data, gui, ops, quick_ops]

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
        except Exception as exc:
            unregister()
            raise exc
        
        # Per-object Property Values
        bpy.types.Mesh.MAME_PropValues = bpy.props.PointerProperty(type=variable_data.MAME_PropValues)
        bpy.types.WindowManager.MAME_GUIPropValues = bpy.props.PointerProperty(type=variable_data.MAME_GUIPropValues)
        bpy.types.WindowManager.mame_image_ref = bpy.props.PointerProperty(name='Image', type=bpy.types.Image)

        # GUI Extensions
        bpy.types.DATA_PT_mesh_attributes.append(gui.attribute_assign_panel)
        bpy.types.MESH_MT_attribute_context_menu.append(gui.attribute_context_menu_extension)
        bpy.types.VIEW3D_MT_mask.append(gui.sculpt_mode_mask_menu_extension)
        bpy.types.VIEW3D_MT_face_sets.append(gui.sculpt_mode_face_sets_menu_extension)
        bpy.types.MESH_MT_vertex_group_context_menu.append(gui.vertex_groups_context_menu_extension)
        bpy.types.MESH_MT_shape_key_context_menu.append(gui.shape_keys_context_menu_extension)
        bpy.types.MATERIAL_MT_context_menu.append(gui.material_context_menu_extension)
        bpy.types.VIEW3D_MT_object.append(gui.object_context_menu_extension)
        bpy.types.VIEW3D_MT_edit_mesh_faces.append(gui.face_context_menu_extension)
        bpy.types.VIEW3D_MT_edit_mesh_edges.append(gui.edge_context_menu_extension)
        bpy.types.VIEW3D_MT_edit_mesh_vertices.append(gui.vertex_context_menu_extension)
        bpy.types.DATA_PT_uv_texture.append(gui.uvmaps_context_menu_extension)
        if bpy.app.version < (4,0,0):
            bpy.types.DATA_PT_face_maps.append(gui.facemaps_context_menu_extension)
        
        if bpy.app.version >= (3,3,0):
            bpy.types.MESH_MT_color_attribute_context_menu.append(gui.color_attributes_menu_extension)

def unregister():
    print(f"[MAME] Shutting down")
    if bpy.app.version < req_bl_ver:
        for c in unsupported_ver_classes:
            bpy.utils.unregister_class(c)
    else:
        try:
            # GUI Extensions
            bpy.types.DATA_PT_mesh_attributes.remove(gui.attribute_assign_panel)
            bpy.types.MESH_MT_attribute_context_menu.remove(gui.attribute_context_menu_extension)
            bpy.types.VIEW3D_MT_mask.remove(gui.sculpt_mode_mask_menu_extension)
            bpy.types.VIEW3D_MT_face_sets.remove(gui.sculpt_mode_face_sets_menu_extension)
            bpy.types.MESH_MT_vertex_group_context_menu.remove(gui.vertex_groups_context_menu_extension)
            bpy.types.MESH_MT_shape_key_context_menu.remove(gui.shape_keys_context_menu_extension)
            bpy.types.MATERIAL_MT_context_menu.remove(gui.material_context_menu_extension)
            bpy.types.VIEW3D_MT_object.remove(gui.object_context_menu_extension)
            bpy.types.VIEW3D_MT_edit_mesh_faces.remove(gui.face_context_menu_extension)
            bpy.types.VIEW3D_MT_edit_mesh_edges.remove(gui.edge_context_menu_extension)
            bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(gui.vertex_context_menu_extension)
            bpy.types.MESH_MT_attribute_context_menu.remove(gui.attribute_context_menu_extension)
            bpy.types.DATA_PT_uv_texture.remove(gui.uvmaps_context_menu_extension)
            
            if bpy.app.version < (4,0,0):
                bpy.types.DATA_PT_face_maps.remove(gui.facemaps_context_menu_extension)
            
            if bpy.app.version >= (3,3,0):
                bpy.types.MESH_MT_color_attribute_context_menu.remove(gui.color_attributes_menu_extension)

            for el in reg_modules:
                name = el.__name__ if hasattr(el, '__name__') else str(el)
                try:
                    print(f"[MAME] Unregistering {name}")
                    el.unregister()
                except Exception:
                    print(f"[MAME] Failed to unregister {name}")
                    continue

            del bpy.types.Mesh.MAME_PropValues
            del bpy.types.WindowManager.MAME_GUIPropValues
            del bpy.types.WindowManager.mame_image_ref
        except Exception:
            pass
            
        print(f"[MAME] bye")

if __name__ == "__main__":
    register()
