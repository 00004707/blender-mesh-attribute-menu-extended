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
    for mod in [etc,func,data,gui,ops]:
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
    #print("loaded")

# Important notes 
# Attribute access is prone to unexpected behaviour
# Setting active attribute with obj.data.attributes.active, might work might not
# it's best to get obj.data.attributes.keys().index("attribute_name") and set attribute with obj.data.attributes.active_index instead
# "attrib = obj.data.attributes.active" makes "attrib" still dynamic - it changes depending on mode, context and even use of bpy.ops
# the best way to handle those is by NAME, most and foremost, and then by index, secondly, if setting by name fails
# idk how to use pointers here, this might have helped, if possible at all

# TODO Get value under active domain in gui
# TODO invert: INT8 = -128 <-> 127, same for int likely, clamp to fit in limits
# TODO Add to current sculpt mask option
# TODO invert sm value when converting
# TODO Custom names with {format} accessible via gui by user when batch converting attributes
# TODO Selected verts and edges in uvmap -> .vs.uvmap and vice versa
# TODO ConditionedRemoveAttribute
# TODO Convert multiple attributes at once etc.
# TODO quickly create named attribute node from active attribute
# TODO add buttons in vertex group and shape key menus
# TODO toggleable quick menus
# TODO BETTER GUI

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

# dbg
classes += [debug.MAMETestAll, 
            debug.MAMECreateAllAttributes
            ]

def register():
    
    for c in classes:
        if func.is_verbose_mode_enabled():
            print(f"Registering class {c}")
        bpy.utils.register_class(c)

    bpy.types.DATA_PT_mesh_attributes.append(gui.attribute_assign_panel)
    
    # old blender fix
    if not hasattr(bpy.types, "MESH_MT_attribute_context_menu"):
        bpy.types.DATA_PT_mesh_attributes.append(gui.attribute_context_menu_extension)
    else:
        bpy.types.MESH_MT_attribute_context_menu.append(gui.attribute_context_menu_extension)
    
    bpy.types.Object.MAME_PropValues = bpy.props.PointerProperty(type=data.MAME_PropValues)

def unregister():
    bpy.types.DATA_PT_mesh_attributes.remove(gui.attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.remove(gui.attribute_context_menu_extension)
    
    for c in classes:
        bpy.utils.unregister_class(c)
    

if __name__ == "__main__":
    register()

