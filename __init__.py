bl_info = {
    "name": "Mesh Attributes Menu eXtended",
    "author": "00004707",
    "version": (0, 4, 0),
    "blender": (3, 1, 0),
    "location": "Properties Panel > Data Properties > Attributes",
    "description": "Extra tools to modify mesh attributes",
    "warning": "",
    "doc_url": "https://github.com/00004707/blender-mesh-attribute-menu-extended",
    "category": "Interface",
    "support": "COMMUNITY",
    "tracker_url": "https://github.com/00004707/blender-mesh-attribute-menu-extended/issues",
}

import importlib

# reload for developing fix
if "etc" in locals():
    import importlib
    for mod in [etc,func,data,gui,ops,quick_ops]:
        importlib.reload(mod)
        #print(f"reloaded:{mod}")
else:
    import bpy
    from .modules import etc
    from .modules import func
    from .modules import data
    from .modules import gui
    from .modules import ops
    from .modules import debug
    from .modules import quick_ops
    #print("loaded")

# Important notes 
# Attribute access is prone to unexpected behaviour
# Setting active attribute with obj.data.attributes.active, might work might not
# it's best to get obj.data.attributes.keys().index("attribute_name") and set attribute with obj.data.attributes.active_index instead
# "attrib = obj.data.attributes.active" makes "attrib" still dynamic - it changes depending on mode, context and even use of bpy.ops
# the best way to handle those is by NAME, most and foremost, and then by index, secondly, if setting by name fails
# idk how to use pointers here, this might have helped, if possible at all

# TODO Get value under active domain in gui
# TODO Selected verts and edges in uvmap -> .vs.uvmap and vice versa
# TODO ConditionedRemoveAttribute
# TODO Convert multiple attributes at once etc.
# TODO quickly create named attribute node from active attribute
# TODO add buttons in vertex group and shape key menus
# TODO toggleable quick menus

# ------------------------------------------
# registers

classes = [etc.AddonPreferences,
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
           ]

# quick menu extensions
classes += [quick_ops.QuickCurrentSculptMaskToAttribute,
            quick_ops.QuickActiveAttributeToSculptMask,
            quick_ops.QuickFaceSetsToAttribute,
            quick_ops.QuickActiveAttributeToFaceSets,
            gui.SculptMode3DViewHeaderSettings,
            quick_ops.QuickShapeKeyToAttribute,
            quick_ops.QuickShapeKeyOffsetToAttribute,
            quick_ops.QuickAllShapeKeyToAttributes,
            quick_ops.QuickAllShapeKeyOffsetToAttributes,
            quick_ops.QuickVertexGroupToAttribute,
            quick_ops.QuickAllVertexGroupToAttributes,
            quick_ops.QuickVertexGroupAssignmentToAttribute,
            quick_ops.QuickMaterialAssignmentToAttribute,
            quick_ops.QuickMaterialIndexToAttribute,
            quick_ops.QuickMaterialSlotAssignmentToAttribute,
            quick_ops.QuickSculptModeApplyAttribute,
            quick_ops.QuickSculptModeExtendAttribute,
            quick_ops.QuickSculptModeSubtractAttribute,
            quick_ops.QuickSculptModeRemoveAttribute,
            quick_ops.QuickSculptModeNewAttribute,
            quick_ops.QuickSculptModeOverwriteAttribute,
            quick_ops.QuickSculptModeInvertAttribute
            ]

# dbg
classes += [debug.MAMETestAll, 
            debug.MAMECreateAllAttributes
            ]

def register():
    
    for c in classes:
        if func.is_verbose_mode_enabled():
            print(f"Registering class {c}")
        bpy.utils.register_class(c)

    # GUI Variable Storage
    bpy.types.Object.MAME_PropValues = bpy.props.PointerProperty(type=data.MAME_PropValues)

    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.append(gui.attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.append(gui.attribute_context_menu_extension)
    bpy.types.VIEW3D_MT_mask.append(gui.sculpt_mode_mask_menu_extension)
    bpy.types.VIEW3D_MT_face_sets.append(gui.sculpt_mode_face_sets_menu_extension)
    bpy.types.VIEW3D_MT_editor_menus.append(gui.sculpt_mode_3dview_header_extension)
    bpy.types.MESH_MT_vertex_group_context_menu.append(gui.vertex_groups_context_menu_extension)
    bpy.types.MESH_MT_shape_key_context_menu.append(gui.shape_keys_context_menu_extension)
    bpy.types.MATERIAL_MT_context_menu.append(gui.material_context_menu_extension)
    bpy.types.VIEW3D_MT_object.append(gui.object_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(gui.face_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(gui.edge_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(gui.vertex_context_menu_extension)

def unregister():
    bpy.types.DATA_PT_mesh_attributes.remove(gui.attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.remove(gui.attribute_context_menu_extension)
    bpy.types.VIEW3D_MT_mask.remove(gui.sculpt_mode_mask_menu_extension)
    bpy.types.VIEW3D_MT_face_sets.remove(gui.sculpt_mode_face_sets_menu_extension)
    bpy.types.VIEW3D_MT_editor_menus.remove(gui.sculpt_mode_3dview_header_extension)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(gui.vertex_groups_context_menu_extension)
    bpy.types.MESH_MT_shape_key_context_menu.remove(gui.shape_keys_context_menu_extension)
    bpy.types.MATERIAL_MT_context_menu.remove(gui.material_context_menu_extension)
    bpy.types.VIEW3D_MT_object.remove(gui.object_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(gui.face_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(gui.edge_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(gui.vertex_context_menu_extension)
    for c in classes:
        bpy.utils.unregister_class(c)
    

if __name__ == "__main__":
    register()

