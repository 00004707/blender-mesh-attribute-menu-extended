import select
import bpy
import random
from mathutils import Vector
import bmesh
import colorsys

bl_info = {
    "name": "Mesh Attributes Menu eXtended",
    "author": "00004707",
    "version": (0, 1),
    "blender": (3, 5, 0),
    "location": "Properties Panel > Data Properties > Attributes",
    "description": "Extra tools to modify mesh attributes",
    "warning": "",
    "doc_url": "",
    "category": "Interface",
}

verbose_mode = False

# TODO check creating of attribs from data on various blender versions
# TODO Byte color is unsigned ints only!
# TODO attrib offset from all shapekeys and also shapekey pos, perhaps same for vertex groups etc?
# TODO overwrite them too
# TODO get val under selected
# TODO self report more
# TODO check if attrib is get by name if edit mode was switched for each op
# TODO invert: INT8 = -128 <-> 127, same for int likely, clamp to fit in limits
# not quite sure if foreach set is required for setting on selection, by index is faster?
# general cleanup this is a mess

# note: attriubes have to be accessed via name, not by reference. Reference is an index (?), and those change upon deletion, *mesh mode change* etc.

# ------------------------------------------
# storage, props, etc

class MAME_PropValues(bpy.types.PropertyGroup):
    """
    All editable props in GUI
    """
    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_bool: bpy.props.BoolProperty(name="Boolean Value", default=False)
    val_vector2d: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))

    face_corner_spill: bpy.props.BoolProperty(name="Face Corner Spill", default = False, description="Allow setting value to nearby corners of selected vertices or limit it only to selected face")

    val_random_toggle: bpy.props.BoolProperty(name="Randomize", default=False)
    val_random_min_float:bpy.props.FloatProperty(name="Float Random Min", default=0.0)
    val_random_max_float:bpy.props.FloatProperty(name="Float Random Max", default=1.0)
    val_random_min_int:bpy.props.IntProperty(name="Integer Random Min", default=0)
    val_random_max_int:bpy.props.IntProperty(name="Integer Random Max", default=100)
    val_random_min_int8:bpy.props.IntProperty(name="8-Bit Integer Random Min", default=0, min=0, max=127)
    val_random_max_int8:bpy.props.IntProperty(name="8-Bit Integer Random Max", default=127, min=0, max=127)
    val_random_min_vec2d:bpy.props.FloatVectorProperty(name="Vector 2D Random Min", size=2, default=(0.0,0.0))
    val_random_max_vec2d:bpy.props.FloatVectorProperty(name="Vector 2D Random Max", size=2, default=(1.0,1.0))
    val_random_min_vec3d:bpy.props.FloatVectorProperty(name="Vector Random Min", size=3, default=(0.0,0.0,0.0))
    val_random_max_vec3d:bpy.props.FloatVectorProperty(name="Vector Random Max", size=3, default=(0.0,0.0,0.0))
    
    color_rand_type: bpy.props.EnumProperty(
        name="Color Randomize Type",
        description="Select an option",
        items=[
            
            ("HSV", "Randomize HSV Values", "Randomize HSV Values"),
            ("RGB", "Randomize RGB Values", "Randomize RGB Values"),
        ],
        default="HSV"
    )
    
    val_random_hue_toggle: bpy.props.BoolProperty(name="Randomize Hue", default=True)
    val_random_saturation_toggle: bpy.props.BoolProperty(name="Randomize Saturation", default=True)
    val_random_colorvalue_toggle: bpy.props.BoolProperty(name="Randomize Value", default=True)

    val_random_r_toggle: bpy.props.BoolProperty(name="Randomize Red", default=True)
    val_random_g_toggle: bpy.props.BoolProperty(name="Randomize Green", default=True)
    val_random_b_toggle: bpy.props.BoolProperty(name="Randomize Blue", default=True)

    val_random_min_color:bpy.props.FloatVectorProperty(name="Color Random Max", size=3, default=(0.0,0.0,0.0))
    val_random_max_color:bpy.props.FloatVectorProperty(name="Color Random Max", size=3, default=(1.0,1.0,1.0))

    val_random_colorvalue_toggle: bpy.props.BoolProperty(name="Randomize Alpha", default=True)
    val_random_min_alpha:bpy.props.FloatProperty(name="Float Random Min", default=0.0)
    val_random_max_alpha:bpy.props.FloatProperty(name="Float Random Min", default=1.0)

    
# ------------------------------------------
# functions, operators, etc.

def get_is_attribute_valid(attrib_name):
    """
    Ignore non-editable, hidden or other invalid attributes.
    """
    forbidden_attribs = ['position']
    return not attrib_name.startswith(".") and attrib_name not in forbidden_attribs

def get_valid_attributes(object):
    """
    Gets all valid editable attributes
    """
    return [a for a in object.data.attributes if get_is_attribute_valid(a.name)]

def get_mesh_selected_by_domain(obj, domain, spill=False):
    # get the selected vertices/edges/faces/face corner
    if domain == 'POINT': 
        return [v for v in obj.data.vertices if v.select]
    elif domain == 'EDGE': 
        return [e for e in obj.data.edges if e.select]
    elif domain == 'FACE': 
        return [f for f in obj.data.polygons if f.select]
    elif domain == 'CORNER': 
        # boneless chicken 
        if spill: # if spill then idc
            return [fc for fc in obj.data.loops if obj.data.vertices[fc.vertex_index].select]
        else:
            mesh_selected_modes = bpy.context.scene.tool_settings.mesh_select_mode
            
            result = []
            if mesh_selected_modes[2]: # faces
                return [obj.data.loops[fc] for f in obj.data.polygons if f.select for fc in f.loop_indices]
            
            
            #elif mesh_selected_modes[1]: #edges
            else:
                # get selected edges
                sel_edges = [e.index for e in obj.data.edges if e.select]
                
                if not len(sel_edges):
                    return []
                
                for fc in obj.data.loops:
                    # check if fc.vertex_index in selection
                    if not fc.edge_index in sel_edges:
                        continue
                    
                    # Get face that has this loop
                    for f in obj.data.polygons:
                        if fc.index in f.loop_indices:
                            face = f
                            break
                    
                    # Get all edges that are using the vert of the loop
                    edges = [e for e in obj.data.edges if fc.vertex_index in e.vertices]
                    
                    # Get edges of that face that have vertex of the loop
                    # those can be mixed, since this is a 2 index list, just check both cases
                    valid_edges = []
                    for edge in edges:
                        edge_verts = [v for v in edge.vertices]
                        if edge_verts in [[e[0], e[1]] for e in face.edge_keys] or edge_verts[::-1] in [[e[0], e[1]] for e in face.edge_keys]:
                            valid_edges.append(edge.index)
                    
                    # check if at least two of those edges are selected
                    sel_count = 0

                    for valid_edge in valid_edges:
                        if valid_edge in sel_edges:
                            sel_count += 1

                    if sel_count > 1:
                        result.append(fc)
                
                return result


            # else: # idk if use this at all
            #     # get active vertex in edit mode
            #     active_vert = None
            #     bpy.ops.object.mode_set(mode='EDIT')
            #     bm = bmesh.from_edit_mesh(obj.data)
            #     for el in bm.select_history:
            #         if isinstance(el, bmesh.types.BMVert):
            #             active_vert = el.index
            #     bm.free()
            #     bpy.ops.object.mode_set(mode='OBJECT')
                    
            #     result = []
            #     sel_verts = [v.index for v in obj.data.vertices if v.select]
            #     print(f"Selected verts: {sel_verts}")
            #     for face in obj.data.polygons:
            #         # We need at least 3 vertices selected to check which face user wants to use
            #         selected_verts_of_face = 0
            #         for vert in face.vertices:
            #             if vert in sel_verts:
            #                 selected_verts_of_face += 1
                    
            #         if selected_verts_of_face < 3:
            #             continue
            #         print(f"Face: {face.index}")
            #         print(f"Active vert: {active_vert}")
            
            #         if active_vert is None:
            #             return []

            #         for fc in face.loop_indices:
            #              if obj.data.loops[fc].vertex_index == active_vert:
            #                  result.append(obj.data.loops[fc])
            #                  print(f"Loop: {obj.data.loops[fc].index}")
                    
            #     return result

        
    else:
        return False

def get_attrib_value_propname(attribute):
    # Different data type has different attribute name when using foreach_get/set
    if attribute.data_type in ["FLOAT_VECTOR", "FLOAT2"]:
        return "vector"
    elif attribute.data_type in ["FLOAT_COLOR", "BYTE_COLOR"]:
        return "color"
    else:
        return "value"

# use this???
def get_attrib_values(attribute):
    """
    Simply gets attribute values using foreach_get

    Warning! Strings are read and set directly without "foreach_set", so this function might not be needed for those
    #used for debug print for strings though
    """
    value_attrib_name = get_attrib_value_propname(attribute)

    dt = attribute.data_type
    if dt == "FLOAT":
        a_vals = [0.0] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "INT":
        a_vals = [0] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "FLOAT_VECTOR":
        a_vals = [0.0] * (len(attribute.data) * 3) # why not Vector()? 
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "FLOAT_COLOR":
        a_vals = [0.0] * (len(attribute.data) * 4)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "BYTE_COLOR":
        a_vals = [0.0] * (len(attribute.data) * 4)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "BOOLEAN":
        a_vals = [False] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "FLOAT2":
        a_vals = [0.0] * (len(attribute.data) * 2)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "INT8":
        a_vals = [0] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_name, a_vals)
        return a_vals
    elif dt == "STRING":
        return [""] * len(attribute.data)
    else:
        return False

def get_attrib_default_value(attribute):
    "returns zero value for given datatype"
    dt = attribute.data_type
    if dt == "FLOAT":
        return 0.0 
    elif dt == "INT":
        return 0 
    elif dt == "FLOAT_VECTOR":
        return (0.0, 0.0, 0.0) 
    elif dt == "FLOAT_COLOR":
        return (0.0, 0.0, 0.0, 0.0)
    elif dt == "BYTE_COLOR":
        return (0.0, 0.0, 0.0, 0.0)
    elif dt == "STRING":
        return "" 
    elif dt == "BOOLEAN":
        return False
    elif dt == "FLOAT2":
        return (0.0, 0.0)
    elif dt == "INT8":
        return 0 

# is this really needed?
def fill_foreachset_val_with_vector(iterable_domain, storage, dimension:int=2, values:list = []):
        for i in iterable_domain:
            for d in range(0, dimension):
                storage[i.index*dimension+d] = values[d]
        return storage

def get_friendly_domain_name(domain_name_raw, plural=False):
    "ah yes, the POINT, not the vertex"
    if domain_name_raw == 'POINT':
        return "Vertex" if not plural else "Vertices"
    elif domain_name_raw == 'CORNER':
        return "Face Corner" if not plural else "Face Corners"
    else:
        return domain_name_raw.lower().capitalize() if not plural else domain_name_raw.lower().capitalize() + "s"

def set_domain_attr(obj, attribute_name:str, domain:str, values: list):
    if domain == 'POINT':
        for i, vert in enumerate(obj.data.vertices):
            setattr(vert, attribute_name, values[i])
    elif domain == 'EDGE':
        for i, edge in enumerate(obj.data.edges):
            setattr(edge, attribute_name, values[i])
    elif domain == 'FACE':
        for i, face in enumerate(obj.data.polygons):
            setattr(face, attribute_name, values[i])
    elif domain == 'CORNER':
        for i, loop in enumerate(obj.data.loops):
            setattr(loop, attribute_name, values[i])

def list_to_vectors(l, dim=3):
    return [(l[i], l[i+1], l[i+2]) for i in range(0, len(l), 3) ]

def set_selection_of_mesh_domain(obj, domain, index, state = True):
            if domain == "POINT":
                obj.data.vertices[index].select = state
            elif domain == "POINT":
                obj.data.edges[index].select = state
            elif domain == "FACE":
                obj.data.polygons[index].select = state

def get_filtered_indexes_by_condition(source_data: list, condition:str, compare_value, case_sensitive_string = False):
        # input is 1 dimensional list with values
        
        indexes = []
        print(type(source_data[0]))
        print(source_data)
        print(compare_value)
        #booleans
        if type(source_data[0]) is bool:
            for i, data in enumerate(source_data):
                if condition == "EQ" and data == compare_value:
                    indexes.append(i)

                elif condition == "NEQ" and data != compare_value:
                    indexes.append(i)

        # numeric values & floats invididual vals
        elif type(source_data[0]) in [int, float]:
            for i, data in enumerate(source_data):
                if condition == "EQ" and data == compare_value: #equal
                    indexes.append(i)

                elif condition == "NEQ" and data != compare_value: # not equal
                    indexes.append(i)

                elif condition == "EQORGR" and data >= compare_value: # >=
                    indexes.append(i)

                elif condition == "EQORLS" and data <= compare_value: # <=
                    indexes.append(i)

                elif condition == "GR" and data > compare_value: # >
                    indexes.append(i)

                elif condition == "LS" and data < compare_value: # <
                    indexes.append(i)
        
        # strings
        elif type(source_data[0]) == str:
            for i, data in enumerate(source_data):
                    
                # case sensitive toggle
                if not case_sensitive_string:
                    value = data.upper()
                    cmp = compare_value.upper()
                else:
                    value = data
                
                if condition == "EQ" and value == cmp: #equal
                    indexes.append(i)

                elif condition == "NEQ" and value != cmp: #not equal
                    indexes.append(i)
                
                elif condition == "CONTAINS" and cmp in value: # contains
                    indexes.append(i)
                
                elif condition == "STARTS_WITH" and value.startswith(cmp): #equal
                    indexes.append(i)

                elif condition == "ENDS_WITH" and value.endswitch(cmp): #endswith
                    indexes.append(i)


        
        return indexes

# Data enums
# --------------------------------------------

def get_face_maps_enum(self, context):
    """
    Gets all face maps from active object to enum
    Index can be "NULL" if invalid.

    (INDEX NAME DESC)
    """

    items = []
    obj = bpy.context.active_object

    # case: no data
    if not len(obj.face_maps):
        return [("NULL", "NO FACE MAPS", "")]


    for face_map in obj.face_maps:
        items.append((str(face_map.index), face_map.name, f"Use {face_map.name} face map "))

    return items

def get_material_slots_enum(self, context):
    """
    Gets an enum entries for material slots in active object 

    Index can be 'NULL' if invalid
    (INDEX NAME DESC)
    """
    items = []
    obj = bpy.context.active_object

    # case: no data
    if not len(obj.material_slots):
        return [("NULL", "NO MATERIAL SLOTS", "")]

    for i, material_slot in enumerate(obj.material_slots):
        if material_slot is not None:
            material_slot_name = f"{str(i)}. {material_slot.name if material_slot.name != '' else 'Empty Slot'}"
            items.append((str(i), material_slot_name, f"Use {material_slot_name} material slot"))

    return items

def get_materials_enum(self, context):
    """
    Gets all materials in the .blend file to a single enum

    Index can be 'NULL' if invalid
    (INDEX NAME DESC)
    """

    items = []

    # case: no data
    if not len(bpy.data.materials):
        return [("NULL", "NO MATERIALS", "")]


    for i, material in enumerate(bpy.data.materials):
        if material is not None:
            items.append((str(i), material.name, f"Use {material.name} material"))

    return items

def get_vertex_groups_enum(self, context):
    """
    Gets all vertex groups of current object to enum values
    
    Index can be 'NULL' if invalid
    (INDEX NAME DESC)
    """

    items = []
    obj = bpy.context.active_object

    # case: no data
    if not len(obj.vertex_groups):
        return [("NULL", "NO VERTEX GROUPS", "")]

    for vg in obj.vertex_groups:
        items.append((str(vg.index), vg.name, f"Use {vg.name} vertex group"))

    return items

def get_shape_keys_enum(self, context):
    """
    Gets all shape keys of active object to enum entries

    Index can be 'NULL' if invalid
    (INDEX NAME DESC)
    """

    items = []
    obj = bpy.context.active_object

    # case: no data
    if obj.data.shape_keys is None:
        return [("NULL", "NO SHAPE KEYS", "")]

    for i, sk in enumerate(obj.data.shape_keys.key_blocks):
        items.append((str(i), sk.name, f"Use {sk.name} shape key"))

    #items.append(("CURRENT", "Current Vertex Positions", f"Vertex Positions as you see them now"))
    return items

def get_natively_supported_domains_enum(self, context):
        """
        Defines compatible domain for input data
        """
        items = []
        domain_supports_verts = [
            "INDEX",
            "VISIBLE", "POSITION",
            "NORMAL",
            "SELECTED","NOT_SELECTED",
            'SCULPT_MODE_MASK', 'VERT_MEAN_BEVEL', 'VERT_MEAN_CREASE', 'VERT_IS_IN_VERTEX_GROUP', 'VERT_FROM_VERTEX_GROUP', 'VERT_SHAPE_KEY_POSITION', 'VERT_SHAPE_KEY_POSITION_OFFSET'
        ]
        domain_supports_edges = [
            "INDEX",
            "VISIBLE", "POSITION",
            "SELECTED","NOT_SELECTED",
            'EDGE_SEAM', 'EDGE_BEVEL_WEIGHT', 'EDGE_CREASE', 'EDGE_SHARP', 'EDGE_FREESTYLE_MARK', 'EDGE_IS_LOOSE', 'EDGE_VERTICES'
        ]
        domain_supports_faces = [
            "INDEX",
            "VISIBLE", "POSITION",
            "NORMAL",
            "SELECTED","NOT_SELECTED",
            'SCULPT_MODE_FACE_SETS', 'FACE_AREA', 'FACE_MATERIAL_INDEX', 'FACE_VERTS', 'FACE_CORNER_INDEXES', 'FACE_CORNER_TOTAL', 'FACE_CORNER_START_INDEX', 'FACE_FROM_FACE_MAP', 'FACE_MAP_INDEX', 'FACE_IS_MATERIAL_ASSIGNED'
        ]
        domain_supports_face_corners = [
            "INDEX",
            'CORNER_TANGENT', 'CORNER_BITANGENT', 'CORNER_BITANGENT_SIGN', 'CORNER_EDGE_INDEX', 'CORNER_VERTEX_INDEX'
        ]
        
        #items.append(("DEFAULT", "Default", "Use default domain for data type"))
        
        if self.domain_data_type in domain_supports_verts:
            items.append(("VERTEX", "Vertex", "Use vertex domain for data type"))
        if self.domain_data_type in domain_supports_edges:
            items.append(("EDGE", "Edge", "Use edge domain for data type"))
        if self.domain_data_type in domain_supports_faces:
            items.append(("FACE", "Face", "Use face domain for data type"))
        if self.domain_data_type in domain_supports_face_corners:
            items.append(("FACE_CORNER", "Face Corner", "Use face corner domain for data type"))
        
        
        return items



# ops
# --------------------------------------------

class AssignActiveAttribValueToSelection(bpy.types.Operator):
    """
    This operator will set active attribute value to whatever is set in gui, to selection in edit mode
    """


    bl_idname = "object.set_active_attribute_to_selected"
    bl_label = "Assign Active Attribute Value To Selection in Edit Mode"
    bl_description = "Assigns active attribute value to selection in edit mode."
    bl_options = {'REGISTER', 'UNDO'}
    
    clear: bpy.props.BoolProperty(name="clear", default = False)
    random: bpy.props.BoolProperty(name="clear", default = False)
    random_range: bpy.props.BoolProperty(name="clear", default = False)


    @classmethod
    def poll(cls, context):
        return (context.active_object.mode == 'EDIT' 
                and context.active_object.type == 'MESH' 
                and context.active_object.data.attributes.active 
                and get_is_attribute_valid(context.active_object.data.attributes.active.name))
    
    def execute(self, context):
        obj = context.active_object

        
        # MODE SWITCH TO BE DONE OUTSIDE OF THE FUNCTION
        # OTHERWISE IT CAN CORRUPT THE ATTRIUBTE (len(attrib.data) is 0)

        # get this value before switching mode, as it changes selected attribute as well when switching
        active_attrib_name = obj.data.attributes.active.name 

        bpy.ops.object.mode_set(mode='OBJECT')
        print( active_attrib_name )
        
        self.set_attrib_value(context, active_attrib_name, obj, self.clear, verbose_mode)
        bpy.ops.object.mode_set(mode='EDIT')
        
        return {"FINISHED"}
    
    def set_attrib_value(self, context, active_attrib_name, obj, clear, randomize):

        # Get required Info
        # there are some shenanigans with this after switching object modes, better update this when switching occurs (by name not index/reference)
        active_attrib = obj.data.attributes[active_attrib_name]
        
        dt = active_attrib.data_type
        prop_group = context.object.MAME_PropValues

        selected_el = get_mesh_selected_by_domain(obj, active_attrib.domain, prop_group.face_corner_spill)
        
        if not selected_el:
            self.report({'ERROR'}, "Invalid selection or no selection")
            return False
        active_attrib = obj.data.attributes[active_attrib_name]
        # Read current values
        print(active_attrib.name)
        print(len(active_attrib.data))

        a_vals = get_attrib_values(active_attrib)
        if dt != 'STRING' and not a_vals:
            self.report({'ERROR'}, "Unsupported data type")
            return False
        
        # Read value from gui
        if dt == "FLOAT":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_float
        elif dt == "INT":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_int
        elif dt == "FLOAT_VECTOR":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_vector
        elif dt == "FLOAT_COLOR":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_color
        elif dt == "BYTE_COLOR":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_bytecolor
        elif dt == "STRING":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_string
        elif dt == "BOOLEAN":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_bool
        elif dt == "FLOAT2":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_vector2d
        elif dt == "INT8":
            value = get_attrib_default_value(active_attrib) if clear else prop_group.val_int8

        # - - - dbg - - - 
        if verbose_mode:
            print(f"""Setting \"{active_attrib.name}\" attribute value
    Total entries: {str(len(active_attrib.data))}
    Selected count: {len(selected_el)}
    Domain {active_attrib.data_type}
    Value: {value}
    Storage: {len(a_vals)}""")
            print(f"pre-set:{str(a_vals)}")

        

        # Assign custom value to storage variable
        if dt == "STRING": 
            pass
        elif dt in ["FLOAT_VECTOR"]: 
            a_vals = fill_foreachset_val_with_vector(selected_el, a_vals, 3, value)
            # for v in selected_el:
            #     a_vals[v.index*3] = float(value[0])
            #     a_vals[v.index*3+1] = float(value[1])
            #     a_vals[v.index*3+2] = float(value[2])
        elif dt in ["FLOAT_COLOR", "BYTE_COLOR"]: 
            a_vals = fill_foreachset_val_with_vector(selected_el, a_vals, 4, value)
            # for v in selected_el:
            #     a_vals[v.index*4] = float(value[0])
            #     a_vals[v.index*4+1] = float(value[1])
            #     a_vals[v.index*4+2] = float(value[2])
            #     a_vals[v.index*4+3] = float(value[3])
        elif dt in ["FLOAT2"]: 
            a_vals = fill_foreachset_val_with_vector(selected_el, a_vals, 2, value)
            # for v in selected_el:
            #     a_vals[v.index*2] = float(value[0])
            #     a_vals[v.index*2+1] = float(value[1])
        else:
            for v in selected_el:
                a_vals[v.index] = value
    

        # Write new values
        if dt in ["STRING"]:
            for v in selected_el:
                active_attrib.data[v.index].value = str(value)   
        else:
            active_attrib.data.foreach_set(get_attrib_value_propname(active_attrib), list(a_vals))
        
        # - - - dbg - - - 
        if verbose_mode:
            if dt in ["STRING"]:
                for i, string_data in enumerate(active_attrib.data):
                    a_vals[i] = string_data[i]
            else:
                active_attrib.data.foreach_get(get_attrib_value_propname(active_attrib), a_vals)
            print(f"post-set:{str(a_vals)}")

#todo create all for type
class CreateAttribFromData(bpy.types.Operator):
    """
    This operator creates a new attribute from exisitng mesh data 
    """

    bl_label = 'Create From Mesh Data'
    bl_idname = 'mesh.attribute_create_from_data'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates attribute from mesh data, like seams or crease."
    
    attrib_name: bpy.props.StringProperty(name="Attribute Name", default="")

    all_of_type_to_attrib: bpy.props.BoolProperty(name="Convert All To Attributes", description="Convert all vertex groups/shape keys/face maps/... at once", default=False)
    
    all_of_type_to_attrib_shape_key_offset_toggle: bpy.props.BoolProperty(name="Set Offset To instead", description="Set \"Offset to\" instaed of \"Offset From\"", default=False)

    domain_data_type: bpy.props.EnumProperty(
        name="Domain Data",
        description="Select an option",
        items=[
            # multi all
            ("INDEX", "Index ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ ᶜᵒʳⁿᵉʳ", "Create attribute from domain index"),
            
            # multi vertex edge face
            (None),
            ("VISIBLE", "Visible ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ", "Create boolean vertex attribute from domain visiblity"),
            ("POSITION", "Position ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ", "Create vertex attribute from domain position"),
            
            # multi vertex face
            (None),
            ("NORMAL", "Normal ⁻ ᵛᵉʳᵗᵉˣ ᶠᵃᶜᵉ", "Create attribute from domain normals"),
            
            # booleans from
            (None),
            ("SELECTED", "Boolean From Selected ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ", "Create boolean attribute from domain selection"),
            ("NOT_SELECTED", "Boolean From Not Selected ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ", "Create boolean attribute from domain that is not selected"),
            # TODO
            #("FROM_CONDITION", "Boolean Compare Attribute ⁻ ᵛᵉʳᵗᵉˣ ᵉᵈᵍᵉ ᶠᵃᶜᵉ ᶜᵒʳⁿᵉʳ", "Create boolean attribute from condition on other attribute"),
            
            # vert
            #(None),
            ("","","","",0),
            ("SCULPT_MODE_MASK", "Sculpt mode mask ⁻ ᵛᵉʳᵗᵉˣ", "Create float vertex attribute from masked vertices in sculpt mode"),
            ("VERT_MEAN_BEVEL", "Vertex Mean Bevel Weight ⁻ ᵛᵉʳᵗᵉˣ", "Create float vertex attribute from Mean Bevel Weight"),
            ("VERT_MEAN_CREASE", "Mean Vertex Crease ⁻ ᵛᵉʳᵗᵉˣ", "Create float vertex attribute from Mean Vertex Crease"),
            ("VERT_FROM_VERTEX_GROUP", "From Vertex Group ⁻ ᵛᵉʳᵗᵉˣ", "Create float vertex attribute from vertex group values"),
            ("VERT_IS_IN_VERTEX_GROUP", "Is In Vertex Group ⁻ ᵛᵉʳᵗᵉˣ", "Create boolean vertex attribute from vertex group assignment"),
            ("VERT_SHAPE_KEY_POSITION", "Position from Shape Key ⁻ ᵛᵉʳᵗᵉˣ", "Create float vector attribute from shape key vertex position"),
            ("VERT_SHAPE_KEY_POSITION_OFFSET", "Position Offset from Shape Key ⁻ ᵛᵉʳᵗᵉˣ", "Create float vector attribute from shape key vertex position offset from other shape key"),
            
            # edge
            (None),
            #("","","","",0),
            ("EDGE_SEAM", "Edge Seam ⁻ ᵉᵈᵍᵉ", "Create boolean edge attribute from seams"),
            ("EDGE_BEVEL_WEIGHT", "Edge Bevel Weight ⁻ ᵉᵈᵍᵉ", "Create float edge attribute from Bevel Weight"),
            ("EDGE_CREASE", "Edge Crease ⁻ ᵉᵈᵍᵉ", "Create float edge attribute from Crease"),
            ("EDGE_SHARP", "Edge Sharp ⁻ ᵉᵈᵍᵉ", "Create boolean edge attribute from Edge Sharp"),
            ("EDGE_FREESTYLE_MARK", "Edge Freestyle Mark ⁻ ᵉᵈᵍᵉ", "Create boolean edge attribute from Freestyle Mark"),
            ("EDGE_IS_LOOSE", "Loose Edges ⁻ ᵉᵈᵍᵉ", "Create boolean edge attribute on loose edges"),
            ("EDGE_VERTICES", "Edge Vertices ⁻ ᵉᵈᵍᵉ", "Create 2D vector edge attribute with indexes of edge vertices"),

            # face
            #(None),
            ("","","","",0),
            ("SCULPT_MODE_FACE_SETS", "Sculpt Mode Face Set Index ⁻ ᶠᵃᶜᵉ", "Create float face attribute from face sets in sculpt mode"),
            ("FACE_AREA", "Face Area ⁻ ᶠᵃᶜᵉ", "Create float face attribute from area of each face"),
            ("FACE_MATERIAL_INDEX", "Material Index ⁻ ᶠᵃᶜᵉ", "Create integer face attribute from material index"),
            ("FACE_VERTS", "Vertices Indexes in a Face ⁻ ᶠᵃᶜᵉ", "Create color (4D Vector) face attribute from indexes of vertices of a face"),
            ("FACE_CORNER_INDEXES", "Corner Indexes if a Face ⁻ ᶠᵃᶜᵉ", "Create color (4D Vector) face attribute from indexes of face corners of a face"),
            ("FACE_CORNER_TOTAL", "Corner Count in a Face ⁻ ᶠᵃᶜᵉ", "Create integer face attribute from count of face corners in a face"),
            ("FACE_CORNER_START_INDEX", "Corner Start Index in a Face ⁻ ᶠᵃᶜᵉ", "Create integer face attribute from lowest index from face corners in a face"),
            ("FACE_FROM_FACE_MAP", "Boolean From Face Map ⁻ ᶠᵃᶜᵉ", "Create boolean face attribute from face map assignment"),
            ("FACE_MAP_INDEX", "Face Map Index ⁻ ᶠᵃᶜᵉ", "Create boolean face attribute from face map assignment"),
            ("FACE_IS_MATERIAL_ASSIGNED", "Boolean From Material Assignment ⁻ ᶠᵃᶜᵉ", "Create boolean face attribute from material assignment"),
            ("FACE_IS_MATERIAL_SLOT_ASSIGNED", "Boolean From Material Slot Assignment ⁻ ᶠᵃᶜᵉ", "Create boolean face attribute from material slot assignment"),
            

            # face corner
            (None),
            #("","","","",0),
            ("CORNER_TANGENT", "Tangent ⁻ ᶜᵒʳⁿᵉʳ", "Create vector face corner attribute from tangent"),
            ("CORNER_BITANGENT", "Bitangent ⁻ ᶜᵒʳⁿᵉʳ", "Create vector face corner attribute from bitangent"),
            ("CORNER_BITANGENT_SIGN", "Bitangent Sign ⁻ ᶜᵒʳⁿᵉʳ", "Create float face corner attribute from corner bitangent sign"),
            ("CORNER_EDGE_INDEX", "Face Corner Edge Index ⁻ ᶜᵒʳⁿᵉʳ", "Create integer face corner attribute from assigned edge index"),
            ("CORNER_VERTEX_INDEX", "Face Corner Vertex Index ⁻ ᶜᵒʳⁿᵉʳ", "Create integer face corner attribute from assigned vertex index"),

        ],
        default="INDEX",
    )

    target_attrib_domain: bpy.props.EnumProperty(
        name="Attribute Domain",
        description="Select an option",
        items=get_natively_supported_domains_enum
    )

    enum_face_maps: bpy.props.EnumProperty(
        name="Face Map",
        description="Select an option",
        items=get_face_maps_enum
    )

    enum_material_slots: bpy.props.EnumProperty(
        name="Material Slot",
        description="Select an option",
        items=get_material_slots_enum
    )

    enum_materials: bpy.props.EnumProperty(
        name="Material",
        description="Select an option",
        items=get_materials_enum
    )

    enum_vertex_groups: bpy.props.EnumProperty(
        name="Vertex Group",
        description="Select an option",
        items=get_vertex_groups_enum
    )

    enum_shape_keys: bpy.props.EnumProperty(
        name="Shape Key",
        description="Select an option",
        items=get_shape_keys_enum
    )

    enum_shape_keys_offset_source: bpy.props.EnumProperty(
        name="Offset from",
        description="Select an option",
        items=get_shape_keys_enum
    )

    auto_convert: bpy.props.BoolProperty(name="Convert Attribute", description="Auto converts created attribute to another domain or type", default=False)
    
    enum_attrib_converter_mode:bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=[("GENERIC", "Generic", ""),
               ("VERTEX_GROUP", "Vertex Group", ""),],
        default="GENERIC",
    )

    enum_attrib_converter_domain:bpy.props.EnumProperty(
        name="Domain",
        description="Select an option",
        items=[("POINT", "Vertex", ""),
               ("EDGE", "Edge", ""),
               ("FACE", "Face", ""),
               ("CORNER", "Face Corner", ""),],
        default="POINT",
    )

    enum_attrib_converter_datatype: bpy.props.EnumProperty(
        name="Mode",
        description="Select an option",
        items=[("FLOAT", "Float", ""),
                ("INT", "Integer", ""),
                ("FLOAT_VECTOR", "Vector", ""),
                ("FLOAT_COLOR", "Color", ""),
                ("BYTE_COLOR", "Byte Color", ""),
                ("STRING", "String", ""),
                ("BOOLEAN", "Boolean", ""),
                ("FLOAT2", "Vector 2D", ""),
                ("INT8", "8-bit Integer", ""),],
        default="FLOAT",
    )

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None) and context.active_object.type == "MESH"
    
    def execute(self, context):    

        obj = bpy.context.active_object
        attrib = None
        # Switch to object mode to modify data
        mode = obj.mode
        if mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # using ifs as the 3.0 uses py3.9, switch is added in py3.10

        # UNIVERSAL MESH ATTRIBUTES START
        # -----------------------------
        
        # DOMAIN INDEX
        if self.domain_data_type == "INDEX":
            if self.target_attrib_domain =="DEFAULT":
                self.target_attrib_domain = "VERTEX"

            name = f"{str(self.target_attrib_domain).lower().capitalize()} Index" if self.attrib_name == "" else self.attrib_name

            if self.target_attrib_domain == "VERTEX":
                attrib = obj.data.attributes.new(name=name, type='INT', domain='POINT')
                attrib.data.foreach_set('value', [i for i, vert in enumerate(obj.data.vertices)])

            elif self.target_attrib_domain == "EDGE":
                attrib = obj.data.attributes.new(name=name, type='INT', domain='EDGE')
                attrib.data.foreach_set('value', [i for i, vert in enumerate(obj.data.edges)])

            elif self.target_attrib_domain == "FACE":
                attrib = obj.data.attributes.new(name=name, type='INT', domain='FACE')
                attrib.data.foreach_set('value', [i for i, vert in enumerate(obj.data.polygons)])

            elif self.target_attrib_domain == "FACE_CORNER":
                attrib = obj.data.attributes.new(name=name, type='INT', domain='CORNER')
                attrib.data.foreach_set('value', [i for i, vert in enumerate(obj.data.loops)])
            
        # VISIBILITY IN EDIT MODE
        elif self.domain_data_type == "VISIBLE":
            if self.target_attrib_domain =="DEFAULT":
                self.target_attrib_domain = "VERTEX"

            name = f" Visible {str(self.target_attrib_domain).lower().capitalize()}" if self.attrib_name == "" else self.attrib_name

            if self.target_attrib_domain == "VERTEX":
                attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='POINT')
                attrib.data.foreach_set('value', [not v.hide for v in obj.data.vertices])
            
            elif self.target_attrib_domain == "EDGE":
                attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='EDGE')
                attrib.data.foreach_set('value', [not v.hide for v in obj.data.edges])
            
            elif self.target_attrib_domain == "FACE":
                attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='FACE')
                attrib.data.foreach_set('value', [not v.hide for v in obj.data.polygons])

        # SELECTED & NOT SELECTED
        elif self.domain_data_type == "SELECTED" or self.domain_data_type == "NOT_SELECTED":
            # safe
            if self.target_attrib_domain =="DEFAULT":
                self.target_attrib_domain = "VERTEX"

            name = f"{str(self.target_attrib_domain).lower().capitalize()} Selection" if self.attrib_name == "" else self.attrib_name

            use_selected = (self.domain_data_type == "SELECTED")
            if self.target_attrib_domain == "VERTEX":
                attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='POINT')
                attrib.data.foreach_set('value', [v.select if use_selected else not v.select for v in obj.data.vertices])

            elif self.target_attrib_domain == "EDGE":
                attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='EDGE')
                attrib.data.foreach_set('value', [e.select if use_selected else not e.select for e in obj.data.edges])

            elif self.target_attrib_domain == "FACE":
                attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='FACE')
                attrib.data.foreach_set('value', [f.select if use_selected else not f.select for f in obj.data.polygons])
            
        # POSITION
        elif self.domain_data_type == "POSITION":
            if self.target_attrib_domain =="DEFAULT":
                self.target_attrib_domain = "VERTEX"

            name = f"{str(self.target_attrib_domain).lower().capitalize()} Position" if self.attrib_name == "" else self.attrib_name

            if self.target_attrib_domain == "VERTEX":
                storage = [0.0] * 3 * len(obj.data.vertices)
                obj.data.vertices.foreach_get('co', storage)
                attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='POINT')
                attrib.data.foreach_set('vector', storage)

            elif self.target_attrib_domain == "EDGE":
                storage = [0.0] * 3 * len(obj.data.edges)
                vert_pairs = [0] * 2 * len(obj.data.edges)
                obj.data.edges.foreach_get('vertices', vert_pairs)
                vert_pairs = [vert_pairs[i:i+2] for i in range(0, len(vert_pairs), 2)]
                for i, vert_pair in enumerate(vert_pairs):
                    pos_0 = obj.data.vertices[vert_pair[0]].co
                    pos_1 = obj.data.vertices[vert_pair[1]].co
                    edge_pos = (pos_0 + pos_1)/2

                    storage[i*3] = edge_pos[0]
                    storage[i*3+1] = edge_pos[1]
                    storage[i*3+2] = edge_pos[2]

                attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='EDGE')
                attrib.data.foreach_set('vector', storage)

            elif self.target_attrib_domain == "FACE":
                storage = [0.0] * 3 * len(obj.data.polygons)
                obj.data.polygons.foreach_get('center', storage)
                attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='FACE')
                attrib.data.foreach_set('vector', storage)

        # NORMALS
        elif self.domain_data_type == "NORMAL":
            if self.target_attrib_domain =="DEFAULT":
                self.target_attrib_domain = "VERTEX"

            name = f"{str(self.target_attrib_domain).lower().capitalize()} Normal" if self.attrib_name == "" else self.attrib_name

            if self.target_attrib_domain == "VERTEX":
                attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='POINT')
                attrib.data.foreach_set('vector',  [vv for value in obj.data.vertex_normals for vv in value.vector])
                
            elif self.target_attrib_domain == "FACE":
                attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='FACE')
                attrib.data.foreach_set('vector',  [vv for value in obj.data.polygon_normals for vv in value.vector])

        # VERTEX MESH ATTRIBUTES START
        # -----------------------------

        # VERTEX MEAN BEVEL
        elif self.domain_data_type == "VERT_MEAN_BEVEL":
            name = "Mean Bevel Weight" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='POINT')
            attrib.data.foreach_set('value', [e.bevel_weight for e in obj.data.vertices])
            
        # VERTEX MEAN CREASE
        elif self.domain_data_type == "VERT_MEAN_CREASE":
            name = "Vertex Mean Crease" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='POINT')
            if not len(obj.data.vertex_creases):
                storage = [0.0] * len(obj.data.vertices)
                attrib.data.foreach_set('value', storage)
            else:
                attrib.data.foreach_set('value', [vcrease.value for vcrease in obj.data.vertex_creases[0].values()])
           
        # SCULPT MODE MASK ON VERTEX
        elif self.domain_data_type == "SCULPT_MODE_MASK":
            # Supports only vertex, UNSAFE
            name = "Sculpt Mode Mask" if self.attrib_name == "" else self.attrib_name

            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='POINT')
            if not len(context.active_object.data.vertex_paint_masks):
                storage = [0.0] * len(obj.data.vertices)
                attrib.data.foreach_set('value', storage)
            else:
                attrib.data.foreach_set('value', [mask.value for mask in obj.data.vertex_paint_masks[0].values()])
            
        # VERT_IS_IN_VERTEX_GROUP
        elif self.domain_data_type == "VERT_IS_IN_VERTEX_GROUP":
            # case invalid data
            if self.enum_vertex_groups == 'NULL':
                self.report({'ERROR'}, f"No vertex groups")
                return {'CANCELLED'}
            
            vg = obj.vertex_groups[int(self.enum_vertex_groups)]

            name = f"Is In {vg.name}" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='POINT')
            data = []
            for vert in obj.data.vertices:
                b_is_in_group = False
                for group in vert.groups:
                    if group.group == int(self.enum_vertex_groups):
                        b_is_in_group = True
                        break
                data.append(b_is_in_group)

            attrib.data.foreach_set('value', data)
        
        # VERTEX GROUP VALUE
        elif self.domain_data_type == "VERT_FROM_VERTEX_GROUP" :
            # case invalid data
            if self.enum_vertex_groups == 'NULL':
                self.report({'ERROR'}, f"No vertex groups")
                return {'CANCELLED'}
            
            vg = obj.vertex_groups[int(self.enum_vertex_groups)]

            name = f"{vg.name}" if self.attrib_name == "" else self.attrib_name
        
            # Naming the attribute same name as the vertex group will crash blender
            while(name in obj.vertex_groups.keys()):
                name += " Vertex Group"

            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='POINT')

            data = []
            for vert in obj.data.vertices:
                weight = 0.0
                
                for group in vert.groups:
                    if group.group == int(self.enum_vertex_groups):
                        weight = group.weight
                        break
                data.append(weight)

            attrib.data.foreach_set('value', data)

        # VERT_SHAPE_KEY_POSITION
        elif self.domain_data_type == "VERT_SHAPE_KEY_POSITION":
            
            # case invalid data
            if self.enum_shape_keys == 'NULL':
                self.report({'ERROR'}, f"No shape keys")
                return {'CANCELLED'}
            
            sk = obj.data.shape_keys.key_blocks[int(self.enum_shape_keys)]

            name = f"{sk.name} Shape" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='POINT')

            attrib.data.foreach_set('vector', [vv for vert_shape in sk.data for vv in vert_shape.co ])

        # VERT SHAPE KEY OFFSET
        elif self.domain_data_type == "VERT_SHAPE_KEY_POSITION_OFFSET":
            
            # case invalid data
            if self.enum_shape_keys == 'NULL':
                self.report({'ERROR'}, f"No shape keys")
                return {'CANCELLED'}
            
            sk = obj.data.shape_keys.key_blocks[int(self.enum_shape_keys)]
            offset_from = [vert_shape.co for vert_shape in sk.data]

            offset_sk = obj.data.shape_keys.key_blocks[int(self.enum_shape_keys_offset_source)]
            offset_to = [vert_shape.co for vert_shape in offset_sk.data]
            
            name = f"{sk.name} Shape Offset" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='POINT')

            for vert in obj.data.vertices:
                offset_from[vert.index] = offset_from[vert.index] - offset_to[vert.index]

            attrib.data.foreach_set('vector', [vv for vec in offset_from for vv in vec])

        # EDGE MESH ATTRIBUTES START
        # -----------------------------

        # EDGE SEAM
        elif self.domain_data_type == "EDGE_SEAM":
            # supports only edge, safe
            name = "Seam" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='EDGE')
            attrib.data.foreach_set('value', [e.use_seam for e in obj.data.edges])
            
        # EDGE BEVEL WEIGHT
        elif self.domain_data_type == "EDGE_BEVEL_WEIGHT":
            # supports only edge, safe
            name = "Edge Bevel Weight" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='EDGE')
            attrib.data.foreach_set('value', [e.bevel_weight for e in obj.data.edges])
        
        # EDGE CREASE
        elif self.domain_data_type == "EDGE_CREASE":
            # supports only edge, safe
            name = "Edge Crease" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='EDGE')
            attrib.data.foreach_set('value', [e.crease for e in obj.data.edges])
          
        # EDGE SHARP
        elif self.domain_data_type == "EDGE_SHARP":
            # supports only edge, safe
            name = "Edge Sharp" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='EDGE')
            attrib.data.foreach_set('value', [e.use_edge_sharp for e in obj.data.edges])
          
        # EDGE FREESTYLE MARK
        elif self.domain_data_type == "EDGE_FREESTYLE_MARK":
            # supports only edge, safe
            name = "Edge Freestyle Mark" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='EDGE')
            attrib.data.foreach_set('value', [e.use_freestyle_mark for e in obj.data.edges])
            
        # EDGE IS LOOSE
        elif self.domain_data_type == "EDGE_IS_LOOSE":
            # supports only edge, safe
            name = "Loose Edges" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='EDGE')
            attrib.data.foreach_set('value', [e.is_loose for e in obj.data.edges])
           
        # EDGE_VERTICES
        elif self.domain_data_type == "EDGE_VERTICES":
            # supports only edge, safe
            name = "Edge Vertices" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT2', domain='EDGE')
            attrib.data.foreach_set('value', [vert for e in obj.data.edges for vert in e.vertices])
            
        # FACE MESH ATTRIBUTES START
        # -----------------------------

        # SCULPT MODE FACE SETS IDS
        elif self.domain_data_type == "SCULPT_MODE_FACE_SETS":
            # Supports only face, UNSAFE
            name = "Sculpt Mode Face Set ID" if self.attrib_name == "" else self.attrib_name
            
            attrib = obj.data.attributes.new(name=name, type='INT', domain='FACE')

            # case: no face sets
            if ".sculpt_face_set" not in obj.data.polygon_layers_int:
                storage = [0] * len(obj.data.polygons)
                attrib.data.foreach_set('value', storage)
            else:
                attrib.data.foreach_set('value', [fs.value for fs in obj.data.polygon_layers_int['.sculpt_face_set'].values()])
            
        # FACE_AREA
        elif self.domain_data_type == "FACE_AREA":
            # safe
            name = "Face Area" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT', domain='FACE')
            attrib.data.foreach_set('value', [f.area for f in obj.data.polygons])
           
        # FACE MATERIAL INDEX
        elif self.domain_data_type == "FACE_MATERIAL_INDEX":
            # safe
            name = "Material Index" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='INT', domain='FACE')
            attrib.data.foreach_set('value', [f.material_index for f in obj.data.polygons])
          
        # FACE VERTS
        elif self.domain_data_type == "FACE_VERTS":
            # supports only face, safe
            name = "Face Vertices" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BYTE_COLOR', domain='FACE')
            attrib.data.foreach_set('color', [vert for f in obj.data.polygons for vert in f.vertices])
            
        # FACE_CORNER_INDEXES
        elif self.domain_data_type == "FACE_CORNER_INDEXES":
            # supports only face, safe
            name = "Face Corner Indexes" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BYTE_COLOR', domain='FACE')
            attrib.data.foreach_set('color', [vert for f in obj.data.polygons for vert in f.loop_indices])
        
        # FACE CORNER COUNT
        elif self.domain_data_type == "FACE_CORNER_TOTAL":
            # supports only face, safe
            name = "Face Corners Count" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='INT', domain='FACE')
            attrib.data.foreach_set('value', [f.loop_total for f in obj.data.polygons])

        # FACE CORNER START INDEX
        elif self.domain_data_type == "FACE_CORNER_START_INDEX":
            # supports only face, safe
            name = "Face Corner Start Index" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='INT', domain='FACE')
            attrib.data.foreach_set('value', [f.loop_start for f in obj.data.polygons])

        # FACE_FROM_FACE_MAP
        elif self.domain_data_type == "FACE_FROM_FACE_MAP":
            # supports only face, safe
            selected_face_map = obj.face_maps[int(self.enum_face_maps)] 
            name = f"Is Face In {selected_face_map.name} Map" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='FACE')

            # WARN: IF NO FACE MAP WAS SET THEN obj.data.face_maps len = 0, even if it was created in the properties panel...
            if len(obj.data.face_maps):
                attrib.data.foreach_set('value', [obj.data.face_maps[0].data[i].value == selected_face_map.index for i, f in enumerate(obj.data.polygons)])
            else:
                attrib.data.foreach_set('value', [False for p in obj.data.polygons])

        # FACE MAP INDEX
        elif self.domain_data_type == "FACE_MAP_INDEX":
            # supports only face, safe 
            name = "Face Map Index" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='INT', domain='FACE')
            if len(obj.data.face_maps):
                attrib.data.foreach_set('value', [obj.data.face_maps[0].data[i].value for i, f in enumerate(obj.data.polygons)])
            else:
                attrib.data.foreach_set('value', [-1 for p in obj.data.polygons] )

        # FACE MATERIAL INDEX
        elif self.domain_data_type == "FACE_IS_MATERIAL_ASSIGNED":
            # safe
            mat = bpy.data.materials[int(self.enum_materials)]
            name = f"Is {mat.name} Material Assigned" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='FACE')
            if len(obj.material_slots):
                attrib.data.foreach_set('value', [obj.material_slots[f.material_index].material == mat for f in obj.data.polygons])
            # case: no materials
            else:
                attrib.data.foreach_set('value', [False] * len(obj.data.polygons))

        #"FACE_IS_MATERIAL_SLOT_ASSIGNED",
        elif self.domain_data_type == "FACE_IS_MATERIAL_SLOT_ASSIGNED":
            # safe
            name = f"Is #{self.enum_material_slots} Material Slot Assigned" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='BOOLEAN', domain='FACE')
            if len(obj.material_slots):
                attrib.data.foreach_set('value', [f.material_index == int(self.enum_material_slots) for f in obj.data.polygons])
            # case: no materials
            else:
                attrib.data.foreach_set('value', [False] * len(obj.data.polygons))

        # FACE CORNER MESH ATTRIBUTES START
        # -----------------------------

        # TANGENT
        elif self.domain_data_type == "CORNER_TANGENT":
            name = "Tangent" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='CORNER')
            attrib.data.foreach_set('vector', [v_float for c in obj.data.loops for v_float in c.tangent])
           
        # BITANGENT
        elif self.domain_data_type == "CORNER_BITANGENT":
            name = "Bitangent" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='CORNER')
            attrib.data.foreach_set('vector', [v_float for c in obj.data.loops for v_float in c.bitangent])
            
        # EDGE INDEX
        elif self.domain_data_type == "CORNER_EDGE_INDEX":
            name = "Edge Index Of Corner" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='INT', domain='CORNER')
            attrib.data.foreach_set('value', [c.edge_index for c in obj.data.loops])
           
        # VERTEX INDEX
        elif self.domain_data_type == "CORNER_VERTEX_INDEX":
            name = "Vertex Index Of Corner" if self.attrib_name == "" else self.attrib_name
            attrib = obj.data.attributes.new(name=name, type='INT', domain='CORNER')
            attrib.data.foreach_set('value', [c.vertex_index for c in obj.data.loops])

        # this should not happen
        else:
            self.report({'ERROR'}, f"Nothing done")
        obj.data.update()

        # Auto convert 
        if self.auto_convert and attrib is not None:
            obj.data.attributes.active = attrib
            bpy.ops.geometry.attribute_convert(mode=self.enum_attrib_converter_mode, domain=self.enum_attrib_converter_domain, data_type=self.enum_attrib_converter_datatype)

        # Switch back to previous mode.
        if mode:
             bpy.ops.object.mode_set(mode=mode)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        # get if the attrib supports converting all
        all_to_attrib_support = self.domain_data_type in ["VERT_IS_IN_VERTEX_GROUP", 
                                     "VERT_FROM_VERTEX_GROUP", 
                                     "VERT_SHAPE_KEY_POSITION_OFFSET", 
                                     "VERT_SHAPE_KEY_POSITION",
                                     "FACE_IS_MATERIAL_ASSIGNED", 
                                     "FACE_IS_MATERIAL_SLOT_ASSIGNED", 
                                     "FACE_FROM_FACE_MAP"]

        row = self.layout
        if not (all_to_attrib_support and self.all_of_type_to_attrib):
            row.prop(self, "attrib_name", text="Name")

        row.prop(self, "domain_data_type", text="Data")
        

        # read from domain
        if len(get_natively_supported_domains_enum(self, context)) > 1:
            row.prop(self, "target_attrib_domain", text="From")

        row.label(text="")
        
        # face maps
        if self.domain_data_type in ["FACE_FROM_FACE_MAP"]:
            self.fix_dynamic_enum_list(self.enum_face_maps)
            row.prop(self, "enum_face_maps", text="Face Map")
        
        # material slots
        if self.domain_data_type in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"]:
            self.fix_dynamic_enum_list(self.enum_material_slots)
            row.prop(self, "enum_material_slots", text="Material Slot")
        
        # materials
        if self.domain_data_type in ["FACE_IS_MATERIAL_ASSIGNED"]:
            self.fix_dynamic_enum_list(self.enum_materials)
            row.prop(self, "enum_materials", text="Material")
        
        # shape keys
        if self.domain_data_type in ["VERT_SHAPE_KEY_POSITION_OFFSET", "VERT_SHAPE_KEY_POSITION"]:
            
            if self.domain_data_type ==  "VERT_SHAPE_KEY_POSITION_OFFSET":

                if not self.all_of_type_to_attrib or (not self.all_of_type_to_attrib_shape_key_offset_toggle):
                    row.prop(self, "enum_shape_keys_offset_source", text="Offset from")

                if not self.all_of_type_to_attrib or self.all_of_type_to_attrib_shape_key_offset_toggle:
                    row.prop(self, "enum_shape_keys", text="Offset To")
                
                if self.all_of_type_to_attrib:
                    row.prop(self, "all_of_type_to_attrib_shape_key_offset_toggle", text="Set \"Offset to\" instead of \"Offset From\"")

            if self.domain_data_type ==  "VERT_SHAPE_KEY_POSITION":
                row.prop(self, "enum_shape_keys", text="Shape Key")
            
            
            
        # vertex groups
        if self.domain_data_type in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"]:
            self.fix_dynamic_enum_list(self.enum_vertex_groups)
            row.prop(self, "enum_vertex_groups", text="Vertex Group")
            
        # convert all of type to attrib
        if all_to_attrib_support:
            row.prop(self, "all_of_type_to_attrib", text="Convert All To Attributes [PLACEHOLDER]")

        #row.label(text=f"Data will be stored in {self.target_attrib_domain} domain.")

        row.prop(self, "auto_convert", text="Convert Attribute After Creation")
        if self.auto_convert:
            row.label(text="Conversion Options")
            row.prop(self, "enum_attrib_converter_mode", text="Mode")
            if self.enum_attrib_converter_mode == 'GENERIC':
                row.prop(self, "enum_attrib_converter_domain", text="Domain")
                row.prop(self, "enum_attrib_converter_datatype", text="Data Type")

# todo similar stuff is in the invert op
class DuplicateAttribute(bpy.types.Operator):
    """
    Simply duplicates an attribute"""

    bl_idname = "mesh.attribute_duplicate"
    bl_label = "Duplicate Attribute"
    bl_description = "Duplicate Active Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("No active attribute")
        return context.active_object and context.active_object.data.attributes.active

    def execute(self, context):
        obj = context.active_object
        src_attrib = obj.data.attributes.active
        current_mode = context.active_object.mode

        bpy.ops.object.mode_set(mode='OBJECT')
        # make this in obj mode
        na = obj.data.attributes.new(name=src_attrib.name, type=src_attrib.data_type, domain=src_attrib.domain)
        if src_attrib.data_type == 'STRING':
            for i, dom in enumerate(src_attrib.data):
                na.data[i].value = dom.value
        else:
            prop_name = get_attrib_value_propname(src_attrib)
            # create storage
            if src_attrib.domain == 'POINT':
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.vertices)
            elif src_attrib.domain == 'EDGE':
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.edges)
            elif src_attrib.domain == 'FACE':
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.polygons)
            else:
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.loops)
            
            if src_attrib.data_type in ['FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR']:
                storage = [val for vec in storage for val in vec]
            
            storage = list(storage)

            src_attrib.data.foreach_get(prop_name, storage)
            na.data.foreach_set(prop_name, storage)
        
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

class InvertAttribute(bpy.types.Operator):
    """
    Inverts active attribute value, with edit mode selection support
    """

    bl_idname = "mesh.attribute_invert"
    bl_label = "Invert Attribute"
    bl_description = "Invert Active Attribute Value"
    bl_options = {'REGISTER', 'UNDO'}

    def invert_attrib_mode_enum(self, context):
        items=[
                ("MULTIPLY_MINUS_ONE", "Multiply by -1", ""),
                ("ADD_TO_MINUS_ONE", "Add to -1", ""),
                ("SUBTRACT_FROM_ONE", "Subtract from 1", ""),
            ]
        return items

    def invert_attrib_color_mode_enum(self, context):
        # reverse
        return invert_attrib_mode_enum(self, context)[::-1]


    edit_mode_selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Affect only selected in edit mode",
        default=False
    )

    edit_mode_face_corner_spill: bpy.props.BoolProperty(
        name="Face Corner Spill",
        description="Allow inverting value to nearby corners of selected vertices or limit it only to selected face",
        default=False
    )

    invert_mode: bpy.props.EnumProperty(
        name="Invert Mode",
        description="Select an option",
        items=invert_attrib_mode_enum
    )

    color_invert_mode: bpy.props.EnumProperty(
        name="Invert Mode",
        description="Select an option",
        items=invert_attrib_color_mode_enum
    )

    @classmethod
    def poll(self, context):
        self.poll_message_set("No active attribute")
        return context.active_object and context.active_object.data.attributes.active
    
    def execute(self, context):
        obj = context.active_object
        src_attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        bpy.ops.object.mode_set(mode='OBJECT')

        src_attrib = obj.data.attributes[src_attrib_name] # !important
        
        # get selected domain indexes
        selected = [domain.index for domain in get_mesh_selected_by_domain(obj, src_attrib.domain, self.edit_mode_face_corner_spill)]
        print(selected)
        
        # No selection and selection mode is enabled?
        if not len(selected) and self.edit_mode_selected_only:
            self.report({'ERROR'}, f"No selection to perform operations onto")
            bpy.ops.object.mode_set(mode=current_mode)
            return {'CANCELLED'}

        # strings are different
        if src_attrib.data_type == 'STRING':
            for i, dom in enumerate(src_attrib.data):
                if not self.edit_mode_selected_only or i in selected:
                    dom.value = dom.value[::-1]
        
        # numbers:
        else:
            prop_name = get_attrib_value_propname(src_attrib)
            
            # create storage
            if src_attrib.domain == 'POINT':
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.vertices)
            elif src_attrib.domain == 'EDGE':
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.edges)
            elif src_attrib.domain == 'FACE':
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.polygons)
            else:
                storage = [get_attrib_default_value(src_attrib)] * len(obj.data.loops)

            storage = list(storage)
            
            # int just get and multiply by -1
            if src_attrib.data_type in ['INT','INT8']:
                src_attrib.data.foreach_get(prop_name, storage)
                storage = [-v if not self.edit_mode_selected_only or i in selected else v for i, v in enumerate(storage) ]

            # for floats just get it as there is multiple modes
            elif src_attrib.data_type in ['FLOAT']:
                src_attrib.data.foreach_get(prop_name, storage)
            
            # booleans just not them
            elif src_attrib.data_type =='BOOLEAN':
                src_attrib.data.foreach_get(prop_name, storage)
                storage = [not v if not self.edit_mode_selected_only or i in selected else v for i, v in enumerate(storage)]
            
            # vectors get them as a single list
            elif src_attrib.data_type in ['FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR']:
                storage = [val for vec in storage for val in vec]
                src_attrib.data.foreach_get(prop_name, storage)

            # invert modes for vectors and float
            if src_attrib.data_type in ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR']:
                invert_mode = self.color_invert_mode if src_attrib.data_type in ['FLOAT_COLOR', 'BYTE_COLOR'] else self.invert_mode

                #ah vectors, yes
                skip = len(get_attrib_default_value(src_attrib))
                if invert_mode == "MULTIPLY_MINUS_ONE":
                    storage = [v * -1 if not self.edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)]
                elif invert_mode == "SUBTRACT_FROM_ONE":
                    storage = [1-v if not self.edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)] 
                elif invert_mode == "ADD_TO_MINUS_ONE":
                    storage = [-1+v if not self.edit_mode_selected_only or int(i/skip) in selected else v for i, v in enumerate(storage)] 
            
            src_attrib.data.foreach_set(prop_name, storage)
            
        
        obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if context.active_object.data.attributes.active.data_type in ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR'] or context.active_object.mode == 'EDIT':
            # display props
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        row = self.layout
        obj = context.active_object

        # invert mode for float and vectors
        if obj.data.attributes.active.data_type in ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR']:
            prop = "invert_mode" if context.active_object.data.attributes.active.data_type in ['FLOAT', 'FLOAT_VECTOR', 'FLOAT2'] else "color_invert_mode"
            row.prop(self, prop, text="Invert Mode")
        
        # selected only
        if obj.mode =='EDIT':
            row.prop(self, "edit_mode_selected_only", text="Selected only")
            # spill face corners
            if context.active_object.data.attributes.active.domain == 'CORNER':
                row.prop(self, "edit_mode_face_corner_spill", text="Face Corner Spill")

class RemoveAllAttribute(bpy.types.Operator):
    """
    Removes all valid attributes
    """
    bl_idname = "mesh.attribute_remove_all"
    bl_label = "Remove All"
    bl_description = "Removes all attributes"
    bl_options = {'REGISTER', 'UNDO'}

    bool_include_uvs: bpy.props.BoolProperty(
        name="Include UVMaps", 
        description="All Vector2D attributes stored in Face Corners", 
        default=False
        )
    
    bool_include_color_attribs: bpy.props.BoolProperty(
        name="Include Color Attributes", 
        description="All Color attributes stored in Vertices or Face Corners", 
        default=False
        )


    @classmethod
    def poll(self, context):
        return context.active_object and len(get_valid_attributes(context.active_object))

    def is_uvmap(self, a):
        return a.domain == 'CORNER' and a.data_type == 'FLOAT2'

    def is_color_attrib(self, a):
        return (a.domain == 'CORNER' or a.domain == 'POINT') and (a.data_type == 'FLOAT_COLOR' or a.data_type == 'BYTE_COLOR') 
    
    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        num = 0

        attrib_names = [a.name for a in obj.data.attributes]
        
        for name in attrib_names:
            a = obj.data.attributes[name]
            #print(f"{a.name}: {a.domain}, {a.data_type}")
            if (get_is_attribute_valid(name) and
                (self.bool_include_uvs if self.is_uvmap(a) else True) and 
                (self.bool_include_color_attribs if self.is_color_attrib(a) else True)):
                    #print("removed!")
                    obj.data.attributes.remove(a)
                    num += 1
        
        obj.data.update()
        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, (f"Removed {str(num)} attribute" + ("s" if num > 1 else "") if num else "None of attributes removed!"))
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.label(text="WARNING")
        row.separator()
        row.label(text="Attributes include UVMaps and Color Attributes")
        row.label(text="Potentially more data in newer versions of blender")
        row.separator()
        row.label(text="Include:")
        row.prop(self, "bool_include_uvs", text="UVMaps")
        row.prop(self, "bool_include_color_attribs", text="Color Attributes")

# TODO
# TODO ADD TO CURRENT SM MASK 
# TODO CREATE FACE SETS IF INPUT IDS ARE OVER THE CURREENT COUNT
# TODO naming vertex groups safe
class ConvertToMeshData(bpy.types.Operator):
    bl_idname = "mesh.attribute_convert_to_mesh_data"
    bl_label = "Convert To Mesh Data"
    bl_description = "Converts attribute to vertex group, shape key, normals..."
    bl_options = {'REGISTER', 'UNDO'}

    
    def get_compatible_mesh_data_enum(self, context):
        items = []
        obj = context.active_object
        active_attrib = obj.data.attributes.active
        inv_data_entry = ("NULL", "NO CONVERTABLE DATA", "")


        # case: no compatible data 
        valid_attribs = 0
        for a in obj.data.attributes:
            if get_is_attribute_valid(a.name): # you have a func for that tho
                valid_attribs += 1
        if not valid_attribs:
            return [inv_data_entry]
        
        #case: simply no entries below for those
        if active_attrib.domain in ['FLOAT2', 'BYTE_COLOR', 'COLOR', "INT8"]:
            return [inv_data_entry]

        # -- Boolean
        if active_attrib.data_type =='BOOLEAN':
            if active_attrib.domain in ['POINT', 'EDGE', 'FACE']:
                items += [
                    ("TO_VISIBLE",f"To Visible {get_friendly_domain_name(active_attrib.domain, True)} In Edit Mode", f"Convert this attribute to visible domain in edit mode"),
                    ("TO_HIDDEN",f"To Hidden {get_friendly_domain_name(active_attrib.domain, True)} In Edit Mode", f"Convert this attribute to hidden domain in edit mode"),
                    ("TO_SELECTED",f"To Selected {get_friendly_domain_name(active_attrib.domain, True)} In Edit Mode", f"Convert this attribute to selected domain in edit mode"),
                    ("TO_NOT_SELECTED", f"To Not Selected {get_friendly_domain_name(active_attrib.domain, True)} In Edit Mode", f"Convert this attribute to selected domain in edit mode"),
                ]
            if active_attrib.domain in ['EDGE']:
                items += [
                    ("TO_SEAM","To Seams", f"Convert this attribute to edge seams"),
                    ("TO_SHARP","To Sharp", f"Convert this attribute to edge sharps"),
                    ("TO_FREESTYLE_MARK","To Freestyle Mark", f"Convert this attribute to edge freestyle mark")
                ]
            if active_attrib.domain in ['FACE']:
                items += [
                    ("TO_FACE_MAP","To Face Map", f"Convert this attribute to face map")
                ]
        # -- Integer
        elif active_attrib.data_type =='INT':
            if active_attrib.domain in ['FACE']:
                items += [
                    ("TO_SCULPT_MODE_FACE_SETS","To Sculpt Mode Face Sets", f"Convert this attribute to Sculpt Mode Face Sets"),
                    ("TO_MATERIAL_INDEX","To Material Index", f"Convert this attribute to Material Index"),
                    ("TO_FACE_MAP_INDEX","Set Face Map Index", f"Convert this attribute to set face map index"),
                ]

        # -- Integer 8bit
        elif active_attrib.data_type =='INT8':
            pass

        # -- Float
        elif active_attrib.data_type =='FLOAT':
            if active_attrib.domain in ['POINT', 'EDGE']:
                items += [
                    ("TO_MEAN_BEVEL_WEIGHT",f"To {get_friendly_domain_name(active_attrib.domain)} Bevel Weight", f"Convert this attribute to domain bevel weight"),
                    ("TO_MEAN_CREASE",F"To {get_friendly_domain_name(active_attrib.domain)} Mean Crease", f"Convert this attribute to domain mean crease"),
                ]
            if active_attrib.domain in ['POINT']:
                items += [
                    ("TO_SCULPT_MODE_MASK","To Sculpt Mode Mask", f"Convert this attribute to sculpt mode mask"),
                    ("TO_VERTEX_GROUP","To Vertex Group", f"Convert this attribute to vertex group"),
                ]

        # -- Vector
        elif active_attrib.data_type =='FLOAT_VECTOR':
            if active_attrib.domain in ['POINT']:
                items += [
                    ("TO_POSITION","To Position", f"Convert this attribute to mesh posiiton"),
                    ("TO_SHAPE_KEY","To Shape Key", f"Convert this attribute to mesh shape key"),
                ]
            if active_attrib.domain in ['POINT', 'FACE']:
                items += [
                    ("TO_NORMAL",F"To {get_friendly_domain_name(active_attrib.domain)} Normal", f"Convert this attribute to mesh domain normal"),
                ]

        # -- Vector 2D
        elif active_attrib.data_type =='FLOAT2':
            pass

        # -- Color/Vector 4D
        elif active_attrib.data_type =='FLOAT_COLOR':
            pass

        # -- ByteColor/Vector 4D uInt
        elif active_attrib.data_type =='BYTE_COLOR':
            pass

        if not len(items):
            return [inv_data_entry]
        
        return items


    append_to_current: bpy.props.BoolProperty(name="Append", default=False)

    data_target: bpy.props.EnumProperty(
        name="Target",
        description="Select an option",
        items=get_compatible_mesh_data_enum
    )

    attrib_name: bpy.props.StringProperty(name="Name", default="")


    @classmethod
    def poll(self, context):
        self.poll_message_set("Nothing to convert this data to")
        
        # No actions currently that support those
        if (self.get_compatible_mesh_data_enum(self, context))[0][0] == 'NULL':
            self.poll_message_set("Nothing to convert this data to")
            return False
        
        return True



    def execute(self, context):
        obj = context.active_object
        src_attrib_name = obj.data.attributes.active.name
        current_mode = context.active_object.mode

        bpy.ops.object.mode_set(mode='OBJECT')

        src_attrib = obj.data.attributes[src_attrib_name] # !important
        a_vals = get_attrib_values(src_attrib)

        # BOOLEANS
        if self.data_target == "TO_VISIBLE":
            a_vals = [not val for val in a_vals]
            set_domain_attr(obj, 'hide', src_attrib.domain, a_vals)

        elif self.data_target == "TO_HIDDEN":
            set_domain_attr(obj, 'hide', src_attrib.domain, a_vals)

        elif self.data_target == "TO_SELECTED":
            set_domain_attr(obj, 'select', src_attrib.domain, a_vals) 

        elif self.data_target == "TO_NOT_SELECTED":
            a_vals = [not val for val in a_vals]
            set_domain_attr(obj, 'select', src_attrib.domain, a_vals) 
        
        # -- EDGE ONLY

        elif self.data_target == "TO_SEAM":
            set_domain_attr(obj, 'seam', src_attrib.domain, a_vals) 

        elif self.data_target == "TO_SHARP":
            set_domain_attr(obj, 'use_edge_sharp', src_attrib.domain, a_vals) 

        elif self.data_target == "TO_FREESTYLE_MARK":
            set_domain_attr(obj, 'use_freestyle_mark', src_attrib.domain, a_vals) 

        # -- FACE ONLY

        elif self.data_target == "TO_FACE_MAP":
            fm_name = "Face Map" if self.attrib_name == '' else self.attrib_name
            fm = obj.face_maps.new(name=fm_name)
            
            for i, val in enumerate(a_vals):
                fm.data[i].value = val
            
        
        # INTEGER

        # -- FACE ONLY
        elif self.data_target == "TO_SCULPT_MODE_FACE_SETS":
            # case: no face sets
            if ".sculpt_face_set" not in obj.data.polygon_layers_int:
                obj.data.polygon_layers_int.new(".sculpt_face_set" )

            for i, val in enumerate(a_vals):
                obj.data.polygon_layers_int['.sculpt_face_set'].data[i].value = val
            
        elif self.data_target == "TO_MATERIAL_INDEX":
            # TODO SAFETY MECHANISMS
            set_domain_attr(obj, 'material_index', src_attrib.domain, a_vals) 
        
        elif self.data_target == "TO_FACE_MAP_INDEX":
            obj.face_maps.new(name=fm_name)
            max_id = len(obj.face_maps)

            if not max_id:
                self.report({'ERROR'}, "No face sets in this mesh")
            for i, val in enumerate(a_vals):
                obj.face_maps[i].data[i].value = True
            

        # 8-BIT INTEGER


        # FLOAT

        # -- VERTEX + EDGE
        elif self.data_target == "TO_MEAN_BEVEL_WEIGHT":
            set_domain_attr(obj, 'bevel_weight', src_attrib.domain, a_vals) 

        elif self.data_target == "TO_MEAN_CREASE":
            if src_attrib.domain == 'POINT':
                # TODO
                pass
            elif src_attrib.domain == 'EDGE':
                set_domain_attr(obj, 'crease', src_attrib.domain, a_vals) 

        # -- VERTEX
        elif self.data_target == "TO_SCULPT_MODE_MASK":

            # case: no mask layer, user never used mask on this mesh
            if not len(obj.data.vertex_paint_masks):
                # I have not found a way to create a mask layer without using bmesh, so here it goes
                #bpy.ops.object.mode_set(mode='EDIT')
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                bm.verts.layers.paint_mask.verify()
                bm.to_mesh(obj.data)
                bm.free()
                #bpy.ops.object.mode_set(mode='OBJECT')
                src_attrib = obj.data.attributes[src_attrib_name] # !important
            
            for i, val in enumerate(a_vals):
                obj.data.vertex_paint_masks[0].data[i].value = val
            
            
        elif self.data_target == "TO_VERTEX_GROUP":
            #TODO SAFE NAME OF VERTEX GROUPS TO AVOID CRASHING
            vg = obj.vertex_groups.new(name=src_attrib_name + " Group")
            for vert in obj.data.vertices:
                weight = a_vals[vert.index]
                vg.add([vert.index], weight, 'REPLACE')


        # VECTOR
        elif self.data_target == "TO_POSITION":
            set_domain_attr(obj, 'co', src_attrib.domain, list_to_vectors(a_vals)) 
        
        elif self.data_target == "TO_SHAPE_KEY":
            sk = obj.shape_key_add(name=src_attrib_name)
            l = list_to_vectors(a_vals)
            for vert in obj.data.vertices:
                sk.data[vert.index].co = l[vert.index]


        elif self.data_target == "TO_NORMAL":
            # TODO this
            if src_attrib.domain == 'POINT':
                obj.data.normals_split_custom_set_from_vertices(list_to_vectors(a_vals))
            elif src_attrib.domain == 'CORNER':
                obj.data.normals_split_custom_set(list_to_vectors(a_vals))

        obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "data_target", text="Target")

        if self.data_target in ['TO_FACE_MAP']:
            row.prop(self, "attrib_name", text="Name")

class CopyAttributeToSelected(bpy.types.Operator):
    bl_idname = "mesh.attribute_copy"
    bl_label = "Copy Attribute to selected"
    bl_description = "Copies attribute from active mesh to selected meshes, by index"
    bl_options = {'REGISTER', 'UNDO'}

    overwrite: bpy.props.BoolProperty(name="Overwrite", default=False, description="Overwrite on target if exists, and is same data type or domain")
    overwrite_different_type: bpy.props.BoolProperty(name="Overwrite different type", default=False, description="For the attribute in target that has a different domain or data type")

    extend_mode: bpy.props.EnumProperty(
        name="Extend Mode",
        description="If target has more vertices/faces/edges/face corners than source, what data should be stored inside of those?",
        items=[("LAST_VAL", "Repeat value at last index", ""),
        ("ZERO", "Fill with \"zero-value\"", ""),
        ("REPEAT", "Repeat", ""),
        ("PING_PONG", "Ping-Pong", "BlendeRRednelB"),
        ],
        default="ZERO",
        
    )

    def get_attribute_data_length(self, obj, a):
        if a.domain == 'POINT':
            return len(obj.data.vertices)
        elif a.domain == 'EDGE':
            return len(obj.data.edges)
        elif a.domain == 'FACE':
            return len(obj.data.faces)
        else:
            return len(obj.data.loops)

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) > 1 and True not in [obj.type != 'MESH' for obj in bpy.context.selected_objects]

    def execute(self, context):
        obj = context.active_object
        current_mode = obj.mode
        src_attrib_name = obj.data.attributes.active.name
        bpy.ops.object.mode_set(mode='OBJECT')
        src_attrib = obj.data.attributes[src_attrib_name] # !important
        a_vals = get_attrib_values(src_attrib)

        # get size of the source attribute domain
        source_size = self.get_attribute_data_length(obj, src_attrib)



        for sel_obj in [sel_obj for sel_obj in bpy.context.selected_objects if sel_obj.type =='MESH' and sel_obj is not obj]:
            
            sel_obj_attr = None
            

            # check if present in target mesh
            if src_attrib_name in [a.name for a in sel_obj.data.attributes]:
                sel_obj_attr = sel_obj.data.attributes[src_attrib_name]

                # overwrite if present?
                if not self.overwrite:
                    continue
                
                #overwrite different type?
                not_same_type = sel_obj_attr.domain != src_attrib.domain or sel_obj_attr.data_type != src_attrib.domain

                if not_same_type and not self.overwrite_different_type:
                    continue
                elif not_same_type:
                    sel_obj.data.attributes.remove(sel_obj_attr)
                    sel_obj_attr = sel_obj.data.attributes.new(name=src_attrib_name, type=src_attrib.data_type, domain=src_attrib.domain)
            else:
                sel_obj_attr = sel_obj.data.attributes.new(name=src_attrib_name, type=src_attrib.data_type, domain=src_attrib.domain)
            
            # check if the target mesh has different amount of faces/verts/etc.
            target_size = self.get_attribute_data_length(sel_obj, sel_obj_attr)

            if sel_obj_attr.domain == 'POINT':
                target_size = len(sel_obj.data.vertices)
            elif sel_obj_attr.domain == 'EDGE':
                target_size = len(sel_obj.data.edges)
            elif sel_obj_attr.domain == 'FACE':
                target_size = len(sel_obj.data.faces)
            else:
                target_size = len(sel_obj.data.loops)
            
            # trim or extend if needed
            if target_size > source_size:
                
                # different types for that case
                if self.extend_mode not in ["REPEAT", "PING_PONG"]: #placeholder for new ideas with non-repeatable values
                    
                    if self.extend_mode =='LAST_VAL':
                        fill_value = [a_vals[-1]]

                    elif self.extend_mode =='ZERO':
                        fill_value = get_attrib_default_value(src_attrib)
                        if src_attrib.data_type != 'STRING' and len(fill_value) > 1:
                            fill_value = fill_value[0]
                        fill_value = [fill_value]

                    target_a_vals = a_vals + (fill_value * (target_size-source_size))
                else:
                    times = target_size - source_size

                    if self.extend_mode =="REPEAT":
                        target_a_vals = a_vals * times
                    elif self.extend_mode == "PING_PONG":
                        target_a_vals = []
                        for t in times:
                            if t%2:
                                target_a_vals += a_vals[::-1]
                            else:
                                target_a_vals += a_vals

                    target_a_vals = target_a_vals[:target_size]

                
            elif target_size < source_size:
                target_a_vals = a_vals[:target_size]
            else:
                target_a_vals = a_vals

            
            sel_obj_attr.data.foreach_set(get_attrib_value_propname(sel_obj_attr), target_a_vals)

            

        obj.data.update()

        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

    def draw(self, context):
        row = self.layout
        row.prop(self, "overwrite", text="Overwrite if exists")
        row.prop(self, "overwrite_different_type", text="Overwrite different type")
        row.prop(self, "extend_mode", text="Extend Mode")

# TODO

# bytecolor is stored as float
# i'm not quite sure if gui input should be a float or 0-127 int
class ConditionalSelection(bpy.types.Operator):
    bl_idname = "mesh.attribute_conditioned_select"
    bl_label = "Select by condition"
    bl_description = "Select mesh domain by attribute value with specified conditions"
    bl_options = {'REGISTER', 'UNDO'}

    # conditions
    
    def get_numeric_conditions_enum(self,context):
        return [
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
            ("EQORGR", "Equal or greater", ">="),
            ("EQORLS", "Equal or lesser", "<="),
            ("GR", "Greater than", ">"),
            ("LS", "Lesser than", "<"),
        ]

    numeric_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    
    bool_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
        ],
        default="EQ"
    )

    string_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
            ("CONTAINS", "Contains", "in"),
            ("STARTS_WITH", "Starts with", "startswith"),
            ("ENDS_WITH", "Ends with", "endswith"),
        ],
        default="EQ"
    )

    string_case_sensitive_bool: bpy.props.BoolProperty(
        name="Case sensitive", 
        description="Is \"BLENDER\" different than \"blEnDer\"?", 
        default=False
        )
    
    visible_color_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=[
            ("EQ", "Equal", "=="),
            ("NEQ", "Not equal", "!="),
            ("LIGHTER", "Visibly lighter", ""),
            ("DARKER", "Visibly darker", ""),
        ],
        default="EQ"
    )

    # RGB HSV
    color_value_type_enum: bpy.props.EnumProperty(
        name="Color Mode",
        description="Select an option",
        items=[
            ("RGBA", "RGBA", ""),
            ("HSVA", "HSVA", ""),
        ],
        default="RGBA"
    )

    color_gui_mode_enum: bpy.props.EnumProperty(
        name="Color Mode",
        description="Select an option",
        items=[
            ("COLOR", "Color", ""),
            ("VALUE", "Value", ""),
        ],
        default="COLOR"
    )

    # do same for vectors

    val_int: bpy.props.IntProperty(name="Integer Value", default=0)
    val_float: bpy.props.FloatProperty(name="Float Value", default=0.0)
    val_vector: bpy.props.FloatVectorProperty(name="Vector Value", size=3, default=(0.0,0.0,0.0))
    val_string: bpy.props.StringProperty(name="String Value", default="")
    val_bool: bpy.props.BoolProperty(name="Boolean Value", default=False)
    val_vector2d: bpy.props.FloatVectorProperty(name="Vector 2D Value", size=2, default=(0.0,0.0))
    val_int8: bpy.props.IntProperty(name="8-bit unsigned Integer Value", min=0, max=127, default=0)
    val_color: bpy.props.FloatVectorProperty(name="Color Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,0.0))
    val_bytecolor: bpy.props.FloatVectorProperty(name="ByteColor Value", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,0.0))

    val_float_x: bpy.props.FloatProperty(name="X", default=0.0)
    val_float_y: bpy.props.FloatProperty(name="Y", default=0.0)
    val_float_z: bpy.props.FloatProperty(name="Z", default=0.0)
    val_float_w: bpy.props.FloatProperty(name="W", default=0.0)

    val_float_color_x: bpy.props.FloatProperty(name="X", default=0.0, min=0.0, max=1.0)
    val_float_color_y: bpy.props.FloatProperty(name="Y", default=0.0, min=0.0, max=1.0)
    val_float_color_z: bpy.props.FloatProperty(name="Z", default=0.0, min=0.0, max=1.0)
    val_float_color_w: bpy.props.FloatProperty(name="W", default=0.0, min=0.0, max=1.0)

    val_vector_x_toggle: bpy.props.BoolProperty(name="X", default=False)
    val_vector_y_toggle: bpy.props.BoolProperty(name="Y", default=False)
    val_vector_z_toggle: bpy.props.BoolProperty(name="Z", default=False)
    val_vector_w_toggle: bpy.props.BoolProperty(name="W", default=False)

    vec_x_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    vec_y_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    vec_z_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )
    vec_w_condition_enum: bpy.props.EnumProperty(
        name="Condition",
        description="Select an option",
        items=get_numeric_conditions_enum,
    )


    @classmethod
    def poll(cls, context):
        return (context.active_object.mode == 'EDIT' 
                and context.active_object.type == 'MESH' 
                and context.active_object.data.attributes.active 
                and get_is_attribute_valid(context.active_object.data.attributes.active.name))
    
    def execute(self, context):
        
        obj = context.active_object
        current_mode = obj.mode
        
        attribute_name = obj.data.attributes.active.name
        bpy.ops.object.mode_set(mode='OBJECT')
        attrib = obj.data.attributes[attribute_name]

        condition = ""
        comparison_value = None
        attrib_data_type = attrib.data_type
        case_sensitive_comp = False
        filtered_indexes = []

        def debug_print():
            print(f"""ConditionalSelectionTrigger
Cond: {condition}
CompVal: {comparison_value}
DataType: {attrib_data_type}
CaseSensitive: {case_sensitive_comp}
FiltIndex: {filtered_indexes}""")

        def compare_float_vals_and(vals_list):
            # compare to each other "and"
                for i in range(1, len(vals_list)):
                    for num in vals_list[0]:
                        if num not in vals_list[i]:
                            vals_list[0].remove(num)
                return vals_list[0]

        #case 1: single number/value
        if attrib_data_type in ['FLOAT', 'INT', 'INT8', 'STRING', 'BOOLEAN']:
            if attrib_data_type in ['FLOAT', 'INT', 'INT8', 'BOOLEAN']:
                condition = self.numeric_condition_enum
                if attrib_data_type == 'INT':
                    comparison_value = self.val_int
                elif attrib_data_type == 'INT8':
                    comparison_value = self.val_int8
                elif attrib_data_type == 'FLOAT':
                    comparison_value = self.val_float
                elif attrib_data_type == 'BOOLEAN':
                    comparison_value = self.val_bool

            elif attrib_data_type == 'STRING':
                condition = self.string_condition_enum
                case_sensitive_comp = self.string_case_sensitive_bool

            filtered_indexes = get_filtered_indexes_by_condition([entry.value for entry in attrib.data], condition, comparison_value, case_sensitive_comp)
            debug_print()

            
        # case 2: multiple values
        elif attrib_data_type in ['FLOAT_VECTOR', 'VECTOR2'] or (attrib_data_type in ['FLOAT_COLOR', 'BYTE_COLOR']):
            vals_to_cmp = []

            filtered_indexes = []

            if self.val_vector_x_toggle or self.val_vector_y_toggle or self.val_vector_z_toggle:
                #x
                if self.val_vector_x_toggle:
                    condition = self.vec_x_condition_enum
                    comparison_value = self.val_float_x
                    vals_to_cmp.append(get_filtered_indexes_by_condition([entry.vector[0] for entry in attrib.data], condition, comparison_value))

                #y
                if self.val_vector_y_toggle:
                    condition = self.vec_y_condition_enum
                    comparison_value = self.val_float_y
                    vals_to_cmp.append(get_filtered_indexes_by_condition([entry.vector[1] for entry in attrib.data], condition, comparison_value))
                
                if attrib_data_type == 'FLOAT_VECTOR' and self.val_vector_z_toggle:
                    #z
                    condition = self.vec_z_condition_enum
                    comparison_value = self.val_float_z
                    vals_to_cmp.append(get_filtered_indexes_by_condition([entry.vector[2] for entry in attrib.data], condition, comparison_value))

                filtered_indexes = compare_float_vals_and(vals_to_cmp)

            elif attrib_data_type in ['FLOAT_COLOR', 'BYTE_COLOR']:
               
                # value editor for color val
                # todo

                # value editor for RGB/hsv values
                if self.color_gui_mode_enum == 'VALUE' and self.val_vector_x_toggle or self.val_vector_y_toggle or self.val_vector_z_toggle:
                    
                    for entry in attrib.data:
                        color = entry.color

                        if self.color_value_type_enum == 'HSVA':
                            color = list(colorsys.rgb_to_hsv(color[0], color[1], color[2])) + [color[3]]
                        #r
                        if self.val_vector_x_toggle:
                            condition = self.vec_x_condition_enum
                            comparison_value = self.val_float_color_x
                            vals_to_cmp.append(get_filtered_indexes_by_condition(color[0], condition, comparison_value))

                        #g
                        if self.val_vector_y_toggle:
                            condition = self.vec_y_condition_enum
                            comparison_value = self.val_float_color_y
                            vals_to_cmp.append(get_filtered_indexes_by_condition(color[1], condition, comparison_value))
                        
                        #b
                        if self.val_vector_z_toggle:
                            
                            condition = self.vec_z_condition_enum
                            comparison_value = self.val_float_color_z
                            vals_to_cmp.append(get_filtered_indexes_by_condition(color[2], condition, comparison_value))

                        #a
                        if self.val_vector_w_toggle:
                            
                            condition = self.vec_w_condition_enum
                            comparison_value = self.val_float_color_w
                            vals_to_cmp.append(get_filtered_indexes_by_condition(color[3], condition, comparison_value))

                        filtered_indexes = compare_float_vals_and(vals_to_cmp)



        for i in filtered_indexes:
            set_selection_of_mesh_domain(obj, attrib.domain, i, True)

        bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):

        obj = context.active_object
        attribute_name = obj.data.attributes.active.name
        attribute = obj.data.attributes.active

        row = self.layout

        if attribute.data_type == 'BOOLEAN':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "bool_condition_enum", text="")
            grid.prop(self, "val_bool", text="Value")

        elif attribute.data_type == 'STRING':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "string_condition_enum", text="")
            grid.prop(self, "val_bool", text="Value")

            row.prop(self, "string_case_sensitive_bool", text="Case Sensitive")

        elif attribute.data_type == 'INT':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "numeric_condition_enum", text="")
            grid.prop(self, "val_int", text="Value")

        elif attribute.data_type == 'INT8':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "numeric_condition_enum", text="")
            grid.prop(self, "val_int8", text="Value")
        
        elif attribute.data_type == 'FLOAT':
            grid = row.grid_flow(columns=2, even_columns=True)
            grid.prop(self, "numeric_condition_enum", text="")
            grid.prop(self, "val_float", text="Value")

        # VEC FLOAT2
        elif attribute.data_type in ['FLOAT2', 'FLOAT_VECTOR']:


            row.prop(self, "val_vector_x_toggle", text="X")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_x_toggle
            grid.prop(self, "vec_x_condition_enum", text="")
            grid.prop(self, "val_float_x", text="Value")


            row.prop(self, "val_vector_y_toggle", text="Y")

            grid = row.grid_flow(columns=2, even_columns=True)
            grid.enabled = self.val_vector_y_toggle
            grid.prop(self, "vec_y_condition_enum", text="")
            grid.prop(self, "val_float_y", text="Value")  
            

            if attribute.data_type == 'FLOAT_VECTOR':
                row.prop(self, "val_vector_z_toggle", text="Z")

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_z_toggle
                grid.prop(self, "vec_z_condition_enum", text="")
                grid.prop(self, "val_float_z", text="Value") 

        # COLOR
        elif attribute.data_type in ['FLOAT_COLOR', 'BYTE_COLOR']:
            row.prop(self, "color_gui_mode_enum", text="Mode")
            
            
            if self.color_gui_mode_enum == 'COLOR':
                # color pickers & visual comparison

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.prop(self, "visible_color_condition_enum", text="")
                if attribute.data_type == 'FLOAT_COLOR':
                    grid.prop(self, "val_color", text="Value")
                else:
                    grid.prop(self, "val_bytecolor", text="Value")
                
                
            elif self.color_gui_mode_enum == 'VALUE':
                # gui that compares individual values like a vector, with hsv mode too
                row.prop(self, "color_value_type_enum", text="Value Type")

                rgb = self.color_value_mode_enum == 'RGBA'

                row.prop(self, "val_vector_x_toggle", text="R" if rgb else 'H')

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_x_toggle
                grid.prop(self, "vec_x_condition_enum", text="")
                grid.prop(self, "val_float_x", text="Value")

                row.prop(self, "val_vector_y_toggle", text="G" if rgb else 'S')

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_y_toggle
                grid.prop(self, "vec_y_condition_enum", text="")
                grid.prop(self, "val_float_y", text="Value")  
                
                row.prop(self, "val_vector_z_toggle", text="B" if rgb else 'V')

                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_z_toggle
                grid.prop(self, "vec_z_condition_enum", text="")
                grid.prop(self, "val_float_z", text="Value") 

                row.prop(self, "val_vector_w_toggle", text="A")
                
                grid = row.grid_flow(columns=2, even_columns=True)
                grid.enabled = self.val_vector_w_toggle
                grid.prop(self, "vec_w_condition_enum", text="")
                grid.prop(self, "val_float_w", text="Value")  
            
# TODO
# class ConditionedRemoveAttribute(bpy.types.Operator):
#     bl_idname = "mesh.attribute_conditioned_remove"
#     bl_label = "Remove by Condition"
#     bl_description = "Removes attributes by condition"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         return False

#     def execute(self, context):
#         return 

# TODO
# class AttributeFind(bpy.types.Operator):
#     bl_idname = "mesh.attribute_find"
#     bl_label = "Find Attribute"
#     bl_description = "Finds an attribute"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         return False

#     def execute(self, context):
#         return 

# TODO
# add grouping by type
# class AttributesSort(bpy.types.Operator):
#     bl_idname = "mesh.attributes_sort"
#     bl_label = "Sort Attributes"
#     bl_description = "Sorts attributes alphabetically"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(self, context):
#         self.poll_message_set("Not implemented yet...")
#         return False

#     def execute(self, context):
#         return 

# ------------------------------------------
# gui
 
def attribute_assign_panel(self, context):
    """
    Buttons underneath the attributes list
    """

    layout = self.layout
    row = layout.row()
    ob = context.active_object
    if ( ob and ob.type == 'MESH'):
        if ( ob.mode == 'EDIT' and ob.data.attributes.active):
            # Do not edit hidden attributes
            if not get_is_attribute_valid(ob.data.attributes.active.name): 
                row.label(text="Editing of non-editable and hidden attributes is disabled.")
            else:
                # fluff
                friendly_domain_name = "mesh domain"
                if ob.data.attributes.active.domain == 'POINT':
                    friendly_domain_name = "Vertex"
                elif ob.data.attributes.active.domain == 'EDGE':
                    friendly_domain_name = "Edge"
                elif ob.data.attributes.active.domain == 'FACE':
                    friendly_domain_name = "Face"
                elif ob.data.attributes.active.domain == 'CORNER':
                    friendly_domain_name = "Face Corner"
                
                # Assignment buttons
                sub = row.row(align=True)
                btn_assign = sub.operator('object.set_active_attribute_to_selected', text=f"Assign")
                btn_assign.clear = False
                btn_clear = sub.operator('object.set_active_attribute_to_selected', text=f"Clear")
                btn_clear.clear = True

                #Selection buttons
                sub = row.row(align=True)
                sub.operator("mesh.attribute_conditioned_select", text="Select")
                sub.operator("mesh.attribute_conditioned_select", text="Deselect")
                
                
                dt = ob.data.attributes.active.data_type
                prop_group = context.object.MAME_PropValues

                # Input fields for each type
                if dt == "FLOAT":
                    layout.prop(prop_group, "val_float", text=f"{friendly_domain_name} Float Value")

                elif dt == "INT":
                    layout.prop(prop_group, "val_int", text=f"{friendly_domain_name} Integer Value")

                elif dt == "FLOAT_VECTOR":
                    layout.prop(prop_group, "val_vector", text=f"{friendly_domain_name} Vector Value")

                elif dt == "FLOAT_COLOR":
                    layout.prop(prop_group, "val_color", text=f"{friendly_domain_name} Color Value")

                elif dt == "BYTE_COLOR":
                    layout.prop(prop_group, "val_bytecolor", text=f"{friendly_domain_name} Bytecolor Value")

                elif dt == "STRING":
                    layout.prop(prop_group, "val_string", text=f"{friendly_domain_name} String Value")

                elif dt == "BOOLEAN":
                    layout.prop(prop_group, "val_bool", text=f"{friendly_domain_name} Boolean Value")

                elif dt == "FLOAT2":
                    layout.prop(prop_group, "val_vector2d", text=f"{friendly_domain_name} Vector 2D Value")

                elif dt == "INT8":
                    layout.prop(prop_group, "val_int8", text=f"{friendly_domain_name} 8-bit Integer Value")

                else:
                    layout.label(text="This attribute type is not supported.")
                
                # Toggle Face Corner Spill 
                if ob.data.attributes.active.domain == "CORNER":
                    layout.prop(prop_group, "face_corner_spill", text=f"Face Corner Spill")
        else:

            # Extra tools
            sub = row.row(align=True)


def attribute_context_menu_extension(self, context):
    """
    Extra entries in ^ menu
    """
    self.layout.operator_context = "INVOKE_DEFAULT"
    self.layout.operator('mesh.attribute_set')
    self.layout.operator('mesh.attribute_create_from_data', icon='MESH_DATA')
    self.layout.operator('mesh.attribute_convert_to_mesh_data', icon='MESH_ICOSPHERE')
    self.layout.operator('mesh.attribute_duplicate', icon='DUPLICATE')
    self.layout.operator('mesh.attribute_invert', icon='UV_ISLANDSEL')
    self.layout.operator('mesh.attribute_copy', icon='COPYDOWN')
    # self.layout.operator('mesh.attribute_find', icon='VIEWZOOM')
    # self.layout.operator('mesh.attributes_sort', icon='SEQ_HISTOGRAM')
    self.layout.operator('mesh.attribute_conditioned_select', icon='CHECKBOX_HLT')
    #self.layout.operator('mesh.attribute_conditioned_remove', icon='X')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE') 
    

# ------------------------------------------
# registers

classes = [MAME_PropValues, 
           CreateAttribFromData, 
           AssignActiveAttribValueToSelection, 
           ConditionalSelection, 
           DuplicateAttribute, 
           InvertAttribute, 
           RemoveAllAttribute, 
           ConvertToMeshData, 
           #ConditionedRemoveAttribute,
           CopyAttributeToSelected]

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.DATA_PT_mesh_attributes.append(attribute_assign_panel)
    # old blender fix
    if not hasattr(bpy.types, "MESH_MT_attribute_context_menu"):
        bpy.types.DATA_PT_mesh_attributes.append(attribute_context_menu_extension)
    else:
        bpy.types.MESH_MT_attribute_context_menu.append(attribute_context_menu_extension)
    
    bpy.types.Object.MAME_PropValues = bpy.props.PointerProperty(type=MAME_PropValues)

def unregister():
    bpy.types.DATA_PT_mesh_attributes.remove(attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.remove(attribute_context_menu_extension)
    
    for c in classes:
        bpy.utils.unregister_class(c)
    

if __name__ == "__main__":
    register()

