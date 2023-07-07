bl_info = {
    "name": "Mesh Attributes Menu eXtended",
    "author": "00004707",
    "version": (0, 2, 0),
    "blender": (3, 1, 0),
    "location": "Properties Panel > Data Properties > Attributes",
    "description": "Extra tools to modify mesh attributes",
    "warning": "",
    "doc_url": "",
    "category": "Interface",
}

import random
from mathutils import Vector

import sys
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
    #print("loaded")

# Important notes 
# Attribute access is prone to unexpected behaviour
# Setting active attribute with obj.data.attributes.active, might work might not
# it's best to get obj.data.attributes.keys().index("attribute_name") and set attribute with obj.data.attributes.active_index instead
# "attrib = obj.data.attributes.active" makes "attrib" still dynamic - it changes depending on mode, context and even use of bpy.ops
# the best way to handle those is by NAME, most and foremost, and then by index, secondly, if setting by name fails
# idk how to use pointers here, this might have helped, if possible at all


# TODO overwrite on creating attributes from data option
# TODO get val under selected
# TODO invert: INT8 = -128 <-> 127, same for int likely, clamp to fit in limits
# TODO add to current SM
# TODO To vertex group index assignment with static weight value 
# TODO Batch name formatting by user input
# TODO Add shape key if there is none, in from object data.
# TODO boolean from visible
# TODO Attribute 2 UVMap & from UVMap for 3.4,3.3 users.
# TODO ConditionedRemoveAttribute
# TODO Search for attribute
# TODO Convert multiple attributes at once etc.

# ------------------------------------------
# registers

classes = [data.MAME_PropValues, 
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
           etc.AddonPreferences
           ]

if etc.enable_debug_tester:
    classes.append(ops.MAMETestAll)

def register():
    
    for c in classes:
        if etc.verbose_mode:
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

