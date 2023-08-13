""" 

All functions

"""

import bpy 
import bmesh
import math
from . import etc
from . import data

# ------------------------------------------
# Attribute related

def get_is_attribute_valid(attrib_name):
    """
    Ignore non-editable, hidden or other invalid attributes.
    """
    forbidden_attribs = ['position', 'sharp_face', '.sculpt_face_set', 'edge_creases', 'material_index']
    forbidden_attrib_prefixes = ['.' #technically the dot will negate all of below, but still
                                  '.vs.',   # vertex selection in UVMap editor
                                  '.es.',   # edge selection in UVMap editor
                                  '.pn.'    # I don't know, something with polygons I guess, returns boolean
    ]

    return not attrib_name.startswith(".") and attrib_name not in forbidden_attribs

def get_valid_attributes(object):
    """
    Gets all valid editable attributes
    """
    return [a for a in object.data.attributes if get_is_attribute_valid(a.name)]

def get_attrib_value_propname(attribute):
    # Different data type has different attribute name when using foreach_get/set
    if attribute.data_type in ["FLOAT_VECTOR", "FLOAT2"]:
        return "vector"
    elif attribute.data_type in ["FLOAT_COLOR", "BYTE_COLOR"]:
        return "color"
    else:
        return "value"

def get_attrib_values(attribute, obj):
    """
    Simply gets attribute values, for every index
    # Returns a list of same type variables as attribute data type

    :param attribute: reference to attribute 
    :param obj: reference to object

    """
    value_attrib_propname = get_attrib_value_propname(attribute)
    dt = attribute.data_type

    if is_verbose_mode_enabled():
        print(f"Getting {attribute.name} values: data type = {dt} ({attribute.data_type}), prop = {value_attrib_propname}, len = {len(attribute.data)}" )

    
    if dt == "FLOAT":
        a_vals = [0.0] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return a_vals
    elif dt == "INT":
        a_vals = [0] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return a_vals
    elif dt == "FLOAT_VECTOR":
        a_vals = [0.0] * (len(attribute.data) * 3) # why not Vector()? 
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return [(a_vals[i], a_vals[i+1], a_vals[i+2]) for i in range(0, len(a_vals), 3)]
    elif dt == "FLOAT_COLOR":
        a_vals = [0.0] * (len(attribute.data) * 4)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return [(a_vals[i], a_vals[i+1], a_vals[i+2], a_vals[i+3]) for i in range(0, len(a_vals), 4)]
    elif dt == "BYTE_COLOR":
        a_vals = [0.0] * (len(attribute.data) * 4)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return [(a_vals[i], a_vals[i+1], a_vals[i+2], a_vals[i+3]) for i in range(0, len(a_vals), 4)]
    elif dt == "BOOLEAN":
        a_vals = [False] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return a_vals
    elif dt == "FLOAT2":
        a_vals = [0.0] * (len(attribute.data) * 2)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return [(a_vals[i], a_vals[i+1]) for i in range(0, len(a_vals), 2)]
    elif dt == "INT32_2D":
        a_vals = [0] * (len(attribute.data) * 2)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return [(a_vals[i], a_vals[i+1]) for i in range(0, len(a_vals), 2)]
    elif dt == "QUATERNION":
        a_vals = [0.0] * (len(attribute.data) * 4)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return [(a_vals[i], a_vals[i+1], a_vals[i+2], a_vals[i+3]) for i in range(0, len(a_vals), 4)]
    elif dt == "INT8":
        a_vals = [0] * len(attribute.data)
        attribute.data.foreach_get(value_attrib_propname, a_vals)
        return a_vals
    elif dt == "STRING":
        # Foreach set get does not support strings.
        a_vals = []
        for entry in attribute.data:
            a_vals.append(entry.value)
        return a_vals
    else:
        return None

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
    elif dt == "INT32_2D":
        return (0, 0)
    elif dt == "QUATERNION":
        return (1.0, 0.0, 0.0, 0.0)
    elif dt == "INT8":
        return 0 

def get_safe_attrib_name(obj, attribute_name, suffix = "Attribute"):
    """Naming the attribute the same name as vertex group will crash blender. Possibly there are other scenarios"""
    while(attribute_name in obj.vertex_groups.keys()):
            attribute_name += " " + suffix

    return attribute_name
   
def set_attribute_values(attribute, value, on_indexes = [], flat_list = False):
    """
    Sets values to attribute. Accepts both list and single value
    If the count of values is lesser than target indexes count, it will repeat
    
    REQUIRED OBJECT MODE
    """
    # for each mode
    if len(on_indexes) == 0:
        prop_name = get_attrib_value_propname(attribute)
        if is_verbose_mode_enabled():
            print(f"Setting {attribute.name} attribute values for each domain. Expected data length {len(attribute.data)}, input data length {len(value)}")

        # create storage
        if flat_list:
            storage = value
        elif type(value) is list:
            if len(value) != len(attribute.data):
                print(f"INPUT DATA INVALID LEN {len(value)} EXPECTED {len(attribute.data)} VALUES:\n{value}")
                raise etc.MeshDataWriteException("set_attribute_values", "Invalid input value data length.")
            storage = value
        else:
            storage = [value] * len(attribute.data)

        # convert to single dimension list if of vector type
        if attribute.data_type in ['FLOAT_VECTOR', 'FLOAT2', 'FLOAT_COLOR', 'BYTE_COLOR', 'INT32_2D', 'QUATERNION'] and not flat_list:
            storage = [val for vec in storage for val in vec]
        
        storage = list(storage)

        # Strings have to be set manually
        if attribute.data_type == 'STRING':
            for i, entry in enumerate(attribute.data):
                entry.value = storage[i]
        else:
            attribute.data.foreach_set(prop_name, storage)

    # on selected indexes mode
    else:
        prop = get_attrib_value_propname(attribute)
        for i in on_indexes:
            if type(value) is list:
                setattr(attribute.data[i], prop, value[i%len(value)]) 
            else:
                setattr(attribute.data[i], prop, value) 

    return True

def set_attribute_value_on_selection(self, context, obj, attribute, value, face_corner_spill = False):
    """
    Sets a single value to attribute, limited to selection in edit mode
    
    REQUIRED OBJECT MODE
    """

    active_attrib_name = attribute.name # !important to get the name not the reference
    active_attrib = obj.data.attributes[active_attrib_name]
    
    if is_verbose_mode_enabled():
        print( f"Working on {active_attrib_name} attribute" )

    # Get selection in edit mode, on attribute domain
    selected_el = get_mesh_selected_by_domain(obj, active_attrib.domain, face_corner_spill)
    
    if not selected_el:
        self.report({'ERROR'}, "Invalid selection or no selection")
        return False
    
    active_attrib = obj.data.attributes[active_attrib_name] # !important get_mesh_selected_by_domain function might toggle modes, and change reference, setting again

    if is_verbose_mode_enabled():
        print(f"Attribute data length: {len(active_attrib.data)}")
        print(f"Selected domains: [{len(selected_el)} total] - {selected_el}")
        print(f"Setting value: {value}")

    if is_verbose_mode_enabled():
        a_vals = get_attrib_values(attribute, obj)
        print(f"Pre-set values: {str(a_vals)}")


    # Write the new values
    selected_el = [el.index for el in selected_el]
    set_attribute_values(active_attrib, value, selected_el)

    
    if is_verbose_mode_enabled():
        a_vals = get_attrib_values(attribute, obj)
        print(f"Post-set values: {str(a_vals)}")

    return True

def convert_attribute(self, obj, attrib_name, mode, domain, data_type):
        if is_verbose_mode_enabled():
            print(f"Converting attribute {attrib_name}")
        # Auto convert to different data type, if enabled in gui
        attrib = obj.data.attributes[attrib_name]
        if attrib is not None:
            # There is some issue with this below
            #obj.data.attributes.active = attrib
            # Will have to use active_index instead. There are hidden attributes, and when setting .active if fails! 
            atrr_index = obj.data.attributes.keys().index(attrib_name)
            obj.data.attributes.active_index = atrr_index

            if is_verbose_mode_enabled():
                print(f"Converting {obj.data.attributes.active.name} with settings {mode}, {domain}, {data_type}")
            bpy.ops.geometry.attribute_convert(mode=mode, domain=domain, data_type=data_type)
        else:
            raise etc.MeshDataWriteException('convert_attribute', f"{attrib_name} attribute is None?")

# ------------------------------------------
# Mesh related

def set_domain_attribute_values(obj, attribute_name:str, domain:str, values: list):
    """
    Sets values of attribute stored in domain like: edges[0].use_sharp 
    """

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

def set_selection_or_visibility_of_mesh_domain(obj, domain, indexes, state = True, selection = True):
    """
    Selection and visibility works a bit differently than other attributes
    Those require setting the state of faces, edges and vertices separately too
    """
    if is_verbose_mode_enabled():
        print(f"Setting sel/vis {selection} to state  {state} on {domain}, \ndataset {indexes}")

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    if domain != 'CORNER':
        try:
            if domain == 'POINT':
                for vertindex in indexes:
                    if selection:
                        bm.verts[vertindex].select = state
                    else:
                        bm.verts[vertindex].hide = state

                    for edge in bm.verts[vertindex].link_edges:
                        if state == selection:
                            if all(vert.index in indexes for vert in edge.verts):
                                if selection:
                                    edge.select = state
                                else:
                                    edge.hide = state
                        else:
                            if any(vert.index in indexes for vert in edge.verts):
                                if selection:
                                    edge.select = state
                                else:
                                    edge.hide = state

                    for face in bm.verts[vertindex].link_faces:
                        if state == selection:
                            if all(vert.index in indexes for vert in face.verts):
                                if selection:
                                    face.select = state
                                else:
                                    face.hide = state
                        else:
                            if any(vert.index in indexes for vert in face.verts):
                                if selection:
                                    face.select = state
                                else:
                                    face.hide = state

            elif domain == 'EDGE':
                for edgeindex in indexes:
                    if selection:
                        bm.edges[edgeindex].select = state
                    else:
                        bm.edges[edgeindex].hide = state

                    for vert in bm.edges[edgeindex].verts:
                        if selection:
                            vert.select = state
                        else:
                            vert.hide = state
                
                    for face in bm.edges[edgeindex].link_faces:
                        if state == selection:
                            if all(edge.index in indexes for edge in face.edges):
                                if selection:
                                    face.select = state
                                else:
                                    face.hide = state
                        else:
                            if any(edge.index in indexes for edge in face.edges):
                                if selection:
                                    face.select = state
                                else:
                                    face.hide = state
                    
            elif domain == 'FACE':
                for faceindex in indexes:
                    if selection:
                        bm.faces[faceindex].select = state
                    else:
                        bm.faces[faceindex].hide = state

                    for vert in bm.faces[faceindex].verts:
                        if selection:
                            vert.select = state
                        else:
                            vert.hide = state
                    
                    for edge in bm.faces[faceindex].edges:
                        if selection:
                            edge.select = state
                        else:
                            edge.hide = state
            
            bm.to_mesh(obj.data)
            bm.free()
        except Exception as e:
            # clear bmesh on exception to avoid extra problems
            bm.to_mesh(obj.data)
            bm.free()
            raise Exception(e)

    else:
        edge_indexes_to_select = []

        for cornerindex in indexes:
            loop = obj.data.loops[cornerindex]

            # get the face index that has this corner
            faceindex = -1
            for face in bm.faces:
                if cornerindex in [loop.index for loop in face.loops]:
                    faceindex = face.index
            
            # get edges that are connected to vertex assinged to this corner
            edges = bm.verts[loop.vertex_index].link_edges
            if is_verbose_mode_enabled():
                print(f"loop {cornerindex} has edges {[edge.index for edge in edges]}")
                print(f"loop {cornerindex} has a face {faceindex}, with edges {[edge.index for edge in bm.faces[faceindex].edges]}")
            
            # get edges that are in face index of this corner
            for edge in edges:
                if edge in bm.faces[faceindex].edges:
                    edge_indexes_to_select.append(edge.index)
        
        bm.free()
        if is_verbose_mode_enabled():
            print(f"Filtered edges of the corner are {edge_indexes_to_select}")
        set_selection_or_visibility_of_mesh_domain(obj, 'EDGE', edge_indexes_to_select, state, selection)

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
    
    return False

def get_filtered_indexes_by_condition(source_data: list, condition:str, compare_value, case_sensitive_string = False):
        # Returns a list of indexes of source data entries that meet the input condition compared to compare_value
        
        # input is 1 dimensional list with values, do not pass vectors, pass individual values
        
        indexes = []
        if is_verbose_mode_enabled():
            print(f"Get filtered indexes with settings:\n{condition} to {compare_value}, case sensitive {case_sensitive_string} \non dataset {source_data}")

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

        if is_verbose_mode_enabled():
            print(f"Filtered indexes: {indexes}")
        return indexes

def get_mesh_data(obj, data_type, source_domain, **kwargs):
    """
    Gets all mesh data of given type
    Returns raw data (vector, bool float integer) read from each domain in a list
    kwargs: (if applicable)
    * vg_index              index of vertex group [id]
    * sk_index              index of shape key [id]
    * vg_offset_index       index of vertex group and the vertex group to offset from [id1, id2]
    * fm_index              face map index
    * sel_mat               selected material
    * mat_index             material index
    * uvmap_index           uvmap index
    """
    if is_verbose_mode_enabled():
        print(f"get_mesh_data_kwargs: {kwargs}")

    def get_simple_domain_attrib_val(domain, attribute_name):
        """
        Gets values from obj.data.vertices[i].attribute_name and similar
        """
        try:
            if domain== "POINT":
                print(f"getting {attribute_name} 0: {getattr(obj.data.vertices[0], attribute_name)}")
                return [getattr(v, attribute_name) for v in obj.data.vertices]
            elif domain == "EDGE":
                return  [getattr(v, attribute_name) for v in obj.data.edges]
            elif domain == "FACE":
                return [getattr(v, attribute_name) for v in obj.data.polygons]
            elif domain == "CORNER":
                return [getattr(v, attribute_name) for v in obj.data.loops]
        except Exception as e:
            raise etc.MeshDataReadException("get_simple_domain_attrib_val", f"Failed to get {attribute_name} from {domain} \n {e}")
    
    if is_verbose_mode_enabled():
        print(f"Reading {data_type} mesh data on {source_domain}...")

    # DOMAIN INDEX
    if data_type == "INDEX":

        if source_domain == "POINT":
            return [i for i, vert in enumerate(obj.data.vertices)]

        elif source_domain == "EDGE":
            return [i for i, vert in enumerate(obj.data.edges)]

        elif source_domain == "FACE":
            return [i for i, vert in enumerate(obj.data.polygons)]

        elif source_domain == "CORNER":
            return [i for i, vert in enumerate(obj.data.loops)]
        
    # VISIBILITY IN EDIT MODE
    elif data_type == "VISIBLE":
        return [not val for val in get_simple_domain_attrib_val(source_domain, "hide")]

    # SELECTED
    elif data_type == "SELECTED":
        return get_simple_domain_attrib_val(source_domain, "select")

    # NOT SELECTED
    elif data_type == "NOT_SELECTED":
        return [not val for val in get_simple_domain_attrib_val(source_domain, "select")]
 
    # POSITION
    elif data_type == "POSITION":
        if source_domain == 'POINT':
            return get_simple_domain_attrib_val(source_domain, "co")
        
        elif source_domain == 'EDGE':
            pairs = get_simple_domain_attrib_val(source_domain, "vertices")
            storage = []
            for i, vert_pair in enumerate(pairs):
                pos_0 = obj.data.vertices[vert_pair[0]].co
                pos_1 = obj.data.vertices[vert_pair[1]].co
                edge_pos = (pos_0 + pos_1)/2
                storage.append(edge_pos)
            return storage

        elif source_domain == 'FACE':
            return [val for val in get_simple_domain_attrib_val(source_domain, "center")]

    # NORMALS
    elif data_type == "NORMAL":
        if source_domain == "POINT":
            return [vec.vector for vec in obj.data.vertex_normals]
            
        elif source_domain == "FACE":
            return [vec.vector for vec in obj.data.polygon_normals]
    
    # Custom split normals, or normals on face corners
    elif data_type == "SPLIT_NORMALS":
            return get_simple_domain_attrib_val(source_domain, "normal")

    # VERTEX MESH ATTRIBUTES START
    # -----------------------------

    # VERTEX MEAN BEVEL
    elif data_type == "VERT_MEAN_BEVEL":
        return get_simple_domain_attrib_val(source_domain, "bevel_weight")

    # VERTEX MEAN CREASE
    elif data_type == "VERT_MEAN_CREASE":
        if bpy.app.version < (4,0):
            if not len(obj.data.vertex_creases):
                return [0.0] * len(obj.data.vertices)
            else:
                return [crease.value for crease in obj.data.vertex_creases[0].data]
        else:
            if not "vertex_creases" in obj.data.attributes:
                return [0.0] * len(obj.data.vertices)
            else:
                return [crease.value for crease in obj.data.attributes["vertex_creases"].data.values()]
    
    # SCULPT MODE MASK ON VERTEX
    elif data_type == "SCULPT_MODE_MASK":
        if not len(obj.data.vertex_paint_masks):
            return [0.0] * len(obj.data.vertices)
        else:
            return [mask.value for mask in obj.data.vertex_paint_masks[0].data]
        
    # VERT_IS_IN_VERTEX_GROUP
    elif data_type == "VERT_IS_IN_VERTEX_GROUP":        
        vg = obj.vertex_groups[int(kwargs['vg_index'])]
        data = []

        for vert in obj.data.vertices:
            b_is_in_group = False
            for group in vert.groups:
                if group.group == int(kwargs['vg_index']):
                    b_is_in_group = True
                    break
            data.append(b_is_in_group)
        return data
    
    # VERTEX GROUP VALUE
    elif data_type == "VERT_FROM_VERTEX_GROUP" :        
        vg = obj.vertex_groups[int(kwargs['vg_index'])]
        data = []

        for vert in obj.data.vertices:
            weight = 0.0
            
            for group in vert.groups:
                if group.group == int(kwargs['vg_index']):
                    weight = group.weight
                    break
            data.append(weight)

        return data

    # VERT_SHAPE_KEY_POSITION
    elif data_type == "VERT_SHAPE_KEY_POSITION":
        sk = obj.data.shape_keys.key_blocks[int(kwargs['sk_index'])]
        return [vert.co for vert in sk.data]

    # VERT SHAPE KEY OFFSET
    elif data_type == "VERT_SHAPE_KEY_POSITION_OFFSET":
        sk = obj.data.shape_keys.key_blocks[int(kwargs['sk_index'])]
        offset_from = [vert_shape.co for vert_shape in sk.data]

        offset_sk = obj.data.shape_keys.key_blocks[int(kwargs['sk_offset_index'])]
        offset_to = [vert_shape.co for vert_shape in offset_sk.data]
        
        for vert in obj.data.vertices:
            offset_from[vert.index] = offset_from[vert.index] - offset_to[vert.index]
        return offset_from


    # EDGE MESH ATTRIBUTES START
    # -----------------------------

    # EDGE SEAM
    elif data_type == "EDGE_SEAM":
        return get_simple_domain_attrib_val(source_domain, "use_seam") 
        
    # EDGE BEVEL WEIGHT
    elif data_type == "EDGE_BEVEL_WEIGHT":
        return get_simple_domain_attrib_val(source_domain, "bevel_weight") 
    
    # EDGE CREASE
    elif data_type == "EDGE_CREASE":
        if bpy.app.version < (4,0):
            return get_simple_domain_attrib_val(source_domain, "crease") 
        else:
            if not "edge_creases" in obj.data.attributes:
                return [0.0] * len(obj.data.edges)
            else:
                return [crease.value for crease in obj.data.attributes["edge_creases"].data.values()]
        
    # EDGE SHARP
    elif data_type == "EDGE_SHARP":
        if hasattr(obj.data.edges, "use_sharp"):
            return get_simple_domain_attrib_val(source_domain, "use_sharp")
        elif hasattr(obj.data.edges, "use_edge_sharp"):
            return get_simple_domain_attrib_val(source_domain, "use_edge_sharp")
        else:
            if not "sharp_edge" in obj.data.attributes:
                return [False] * len(obj.data.edges)
            else:
                return [sharp.value for sharp in obj.data.attributes["sharp_edge"].data]
        
        
    # EDGE FREESTYLE MARK
    elif data_type == "EDGE_FREESTYLE_MARK":
        return get_simple_domain_attrib_val(source_domain, "use_freestyle_mark") 
        
    # EDGE IS LOOSE
    elif data_type == "EDGE_IS_LOOSE":
        return get_simple_domain_attrib_val(source_domain, "is_loose") 
        
    # EDGE_VERTICES
    elif data_type == "EDGE_VERTICES":
        return get_simple_domain_attrib_val(source_domain, "vertices") 
        
    # FACE MESH ATTRIBUTES START
    # -----------------------------

    # SCULPT MODE FACE SETS IDS
    elif data_type == "SCULPT_MODE_FACE_SETS":
        if bpy.app.version < (4,0):
            # case: no face sets
            if ".sculpt_face_set" not in obj.data.polygon_layers_int:
                return [0] * len(obj.data.polygons)
            else:
                return [face.value for face in obj.data.polygon_layers_int['.sculpt_face_set'].data]
        else:
            if not ".sculpt_face_set" in obj.data.attributes:
                return [0] * len(obj.data.polygons)
            else:
                return [faceset.value for faceset in obj.data.attributes[".sculpt_face_set"].data]
        
    # FACE_AREA
    elif data_type == "FACE_AREA":
        return get_simple_domain_attrib_val(source_domain, "area") 
    
    # FACE IS SMOOTH SHADED
    elif data_type == "FACE_USE_SMOOTH":
        if not hasattr(obj.data.polygons[0], "use_smooth"):
            return get_simple_domain_attrib_val(source_domain, "use_smooth") 
        else: # futureproofing
            if not "sharp_face" in obj.data.attributes:
                return [False] * len(obj.data.polygons)
            else:
                return [faceset.value for faceset in obj.data.attributes["sharp_face"].data]

    # FACE MATERIAL INDEX
    elif data_type == "FACE_MATERIAL_INDEX":
        if not hasattr(obj.data.polygons[0], "material_index"):
            return get_simple_domain_attrib_val(source_domain, "material_index") 
        else: # futureproofing
            if not "material_index" in obj.data.attributes:
                return [0] * len(obj.data.polygons)
            else:
                return [faceset.value for faceset in obj.data.attributes["material_index"].data]
        
    # FACE VERTS
    elif data_type == "FACE_VERTS":
        return [f.vertices for f in obj.data.polygons]
        
    # FACE_CORNER_INDEXES
    elif data_type == "FACE_CORNER_INDEXES":
        return [f.loop_indices for f in obj.data.polygons]
    
    # FACE CORNER COUNT
    elif data_type == "FACE_CORNER_TOTAL":
        return get_simple_domain_attrib_val(source_domain, "loop_total") 

    # FACE CORNER START INDEX
    elif data_type == "FACE_CORNER_START_INDEX":
        return get_simple_domain_attrib_val(source_domain, "loop_start") 

    # FACE_FROM_FACE_MAP
    elif data_type == "FACE_FROM_FACE_MAP":
        # WARN: IF NO FACE MAP WAS SET THEN obj.data.face_maps len = 0, even if it was created in the properties panel...
        if len(obj.data.face_maps):
            # print(kwargs['fm_index'])
            # print([obj.data.face_maps[0].data[i].value for i, f in enumerate(obj.data.polygons)])
            return [obj.data.face_maps[0].data[i].value == int(kwargs['fm_index']) for i, f in enumerate(obj.data.polygons)]
        else:
            return [False] * len(obj.data.polygons)

    # FACE MAP INDEX
    elif data_type == "FACE_MAP_INDEX":
        if len(obj.data.face_maps):
            return [obj.data.face_maps[0].data[i].value for i, f in enumerate(obj.data.polygons)]
        else:
            return [-1] * len(obj.data.polygons)

    # FACE MATERIAL INDEX
    elif data_type == "FACE_IS_MATERIAL_ASSIGNED":
        # print(bpy.data.materials[int(kwargs['sel_mat'])])
        # print([obj.material_slots[f.material_index].material for f in obj.data.polygons])
        if len(obj.material_slots):
            return [obj.material_slots[f.material_index].material == bpy.data.materials[int(kwargs['sel_mat'])] for f in obj.data.polygons]
        else:
            return [False] * len(obj.data.polygons)

    #"FACE_IS_MATERIAL_SLOT_ASSIGNED",
    elif data_type == "FACE_IS_MATERIAL_SLOT_ASSIGNED":
        if len(obj.material_slots):
            return [f.material_index == int(kwargs['mat_index']) for f in obj.data.polygons]
        else:
            return [False] * len(obj.data.polygons)

    # FACE CORNER MESH ATTRIBUTES START
    # -----------------------------

    # TANGENT
    elif data_type == "CORNER_TANGENT":
        return get_simple_domain_attrib_val(source_domain, "tangent") 
        
    # BITANGENT
    elif data_type == "CORNER_BITANGENT":
        return get_simple_domain_attrib_val(source_domain, "bitangent") 
    
    # BITANGENT SIGN
    elif data_type == "CORNER_BITANGENT_SIGN":
        return get_simple_domain_attrib_val(source_domain, "bitangent_sign") 
        
    # EDGE INDEX
    elif data_type == "CORNER_EDGE_INDEX":
        return get_simple_domain_attrib_val(source_domain, "edge_index") 
        
    # VERTEX INDEX
    elif data_type == "CORNER_VERTEX_INDEX":
        return get_simple_domain_attrib_val(source_domain, "vertex_index") 
    
    # UVMAP
    elif data_type == "UVMAP":
        return [map.uv for map in obj.data.uv_layers[int(kwargs['uvmap_index'])].data]
    

    # -----------------------------
    # SPECIAL ATTRIBS START

    # SELECTED VERTS IN UV EDITOR
    elif data_type == "SELECTED_VERTICES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        return [vs.value for vs in obj.data.attributes[f".vs.{uvmap_name}"].data]
    
    # SELECTED EDGES IN UV EDITOR
    elif data_type == "SELECTED_EDGES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        return [es.value for es in obj.data.attributes[f".es.{uvmap_name}"].data]
    
    else:
        raise etc.MeshDataReadException("get_mesh_data", f"Invalid domain data type ({data_type}) or this data is not available on this domain ({source_domain})")

def set_mesh_data(obj, data_target:str , src_attrib, **kwargs):
    """
    :param data_target: string name from data.py
    :param src_attrib: reference to the attribute

    :return: status boolean

    :param \**kwargs: 
     (If applicable)
    
    :Keyword Arguments:
        * face_map_name             Name of the face map to create
        * vertex_group_name         Name of the vertex group to create
        * enable_auto_smooth        bool
        * apply_to_first_shape_key  bool
        * to_vgindex_weight         float
        * to_vgindex_weight_mode    enum - STATIC, ATTRIBUTE
        * to_vgindex_src_attrib     attribute reference
        * uvmap_index               integer
    
    """
    a_vals = get_attrib_values(src_attrib, obj)
    if is_verbose_mode_enabled():
        print(f"Setting mesh data {data_target} from {src_attrib}, values: {a_vals}, kwargs: {kwargs}")
    
    src_attrib_name = src_attrib.name

        # BOOLEANS
    if data_target == "TO_VISIBLE":
        vis_indexes = [index for index, value in enumerate(a_vals) if value]
        set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, vis_indexes, False, selection=False)

    elif data_target == "TO_HIDDEN":
        hid_indexes = [index for index, value in enumerate(a_vals) if value]
        set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, hid_indexes, True, selection=False)

    elif data_target == "TO_SELECTED":
        sel_indexes = [index for index, value in enumerate(a_vals) if value]
        set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, sel_indexes, True)

    elif data_target == "TO_NOT_SELECTED":
         nsel_indexes = [index for index, value in enumerate(a_vals) if value]
         set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, nsel_indexes, False)

    # -- EDGE ONLY

    elif data_target == "TO_SEAM":
        set_domain_attribute_values(obj, 'use_seam', src_attrib.domain, a_vals) 

    elif data_target == "TO_SHARP":
        if len(obj.data.edges):
            if hasattr(obj.data.edges[0], "use_sharp"):
                set_domain_attribute_values(obj, "use_sharp", src_attrib.domain, a_vals) 
            elif hasattr(obj.data.edges[0], "use_edge_sharp"):
                set_domain_attribute_values(obj, 'use_edge_sharp', src_attrib.domain, a_vals) 

    elif data_target == "TO_FREESTYLE_MARK":
        set_domain_attribute_values(obj, 'use_freestyle_mark', src_attrib.domain, a_vals) 

    # -- FACE ONLY

    elif data_target == "TO_FACE_MAP":
        fm_name = "Face Map" if kwargs["face_map_name"] == '' else kwargs["face_map_name"]
        fm = obj.face_maps.new(name=fm_name)
        
        # create layer
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.layers.face_map.verify()
        bm.to_mesh(obj.data)
        bm.free()

        # Set face map index to selected polygons in attribute (True)
        for i, val in enumerate(a_vals):
            if val:
                obj.data.face_maps[0].data[i].value = fm.index

    elif data_target == "TO_FACE_SHADE_SMOOTH":
        set_domain_attribute_values(obj, 'use_smooth', src_attrib.domain, a_vals) 
        
    
    # INTEGER

    # -- VERTEX

    elif data_target == "TO_VERTEX_GROUP_INDEX":
    
        # clamp to max index
        max_index_input = max(a_vals)
        max_index_target = len(obj.vertex_groups) - 1
        max_index = min([max_index_input, max_index_target])
        
        if kwargs["to_vgindex_weight_mode"] == 'STATIC':
            #lazy set the weight to static value
            for i, val in enumerate(a_vals):
                obj.vertex_groups[min([max_index, val])].add([i], kwargs['to_vgindex_weight'], 'REPLACE')
        
        # or use attrib
        elif kwargs["to_vgindex_weight_mode"] == 'ATTRIBUTE':
            for i, val in enumerate(a_vals):
                obj.vertex_groups[min([max_index, val])].add([i], kwargs['to_vgindex_src_attrib'].data[i].value, 'REPLACE')

    # -- FACE ONLY
    elif data_target == "TO_SCULPT_MODE_FACE_SETS":
        # case: no face sets
        if ".sculpt_face_set" not in obj.data.polygon_layers_int:
            obj.data.polygon_layers_int.new(name=".sculpt_face_set" )

        for i, val in enumerate(a_vals):
            obj.data.polygon_layers_int['.sculpt_face_set'].data[i].value = val
        
    elif data_target == "TO_MATERIAL_INDEX":
        # todo %
        set_domain_attribute_values(obj, 'material_index', src_attrib.domain, a_vals) 
    
    elif data_target == "TO_FACE_MAP_INDEX":
        for i, val in enumerate(a_vals):
            # limit the value
            val = max(0, min(val, len(obj.face_maps)-1))
            obj.data.face_maps[0].data[i].value = val

        

    # 8-BIT INTEGER


    # FLOAT

    # -- VERTEX + EDGE
    elif data_target == "TO_MEAN_BEVEL_WEIGHT":
        set_domain_attribute_values(obj, 'bevel_weight', src_attrib.domain, a_vals) 

    
    elif data_target == "TO_MEAN_CREASE":
        if src_attrib.domain == 'POINT':
            if bpy.app.version < (4,0):
                
                # Create layer if it does not exist:
                if not len(obj.data.vertex_creases):
                    bm = bmesh.new()
                    bm.from_mesh(obj.data)
                    bm.verts.layers.crease.verify()
                    bm.to_mesh(obj.data)
                    bm.free()
                for i, val in enumerate(a_vals):
                    obj.data.vertex_creases[0].data[i].value = val
            else:
                if not "vertex_creases" in obj.data.attributes:
                    obj.data.attributes.new("vertex_creases", 'FLOAT', 'POINT')
                
                set_attribute_values(obj.data.attributes["vertex_creases"], a_vals)
                
        elif src_attrib.domain == 'EDGE':
            set_domain_attribute_values(obj, 'crease', src_attrib.domain, a_vals) 

    # -- VERTEX
    elif data_target == "TO_SCULPT_MODE_MASK":

        # case: no mask layer, user never used mask on this mesh
        if not len(obj.data.vertex_paint_masks):
            src_attrib_name = src_attrib.name
            # I have not found a way to create a mask layer without using bmesh, so here it goes
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.verts.layers.paint_mask.verify()
            bm.to_mesh(obj.data)
            bm.free()
            src_attrib = obj.data.attributes[src_attrib_name] # !important
        
        for i, val in enumerate(a_vals):
            obj.data.vertex_paint_masks[0].data[i].value = val
        
        
    elif data_target == "TO_VERTEX_GROUP":
        name = get_safe_attrib_name(obj, src_attrib_name + " Group", 'Group')
        vg = obj.vertex_groups.new(name=name if kwargs["vertex_group_name"] == '' else kwargs["vertex_group_name"])
        for vert in obj.data.vertices:
            weight = a_vals[vert.index]
            vg.add([vert.index], weight, 'REPLACE')


    # VECTOR
    elif data_target == "TO_POSITION":
        set_domain_attribute_values(obj, 'co', src_attrib.domain, a_vals) 

        # Apply to first shape key too, if enabled
        if hasattr(obj.data.shape_keys, 'key_blocks') and kwargs["apply_to_first_shape_key"]:
            sk = obj.data.shape_keys.key_blocks[obj.data.shape_keys.key_blocks.keys()[0]].data
            for i, val in enumerate(a_vals):
                sk[i].co = val

    
    elif data_target == "TO_SHAPE_KEY":
        sk = obj.shape_key_add(name=src_attrib_name)
        l = [[vec[0],vec[1],vec[2]] for vec in a_vals]
        for vert in obj.data.vertices:
            sk.data[vert.index].co = l[vert.index]

    elif data_target == 'TO_SPLIT_NORMALS':
        obj.data.use_auto_smooth = kwargs['enable_auto_smooth']
        if src_attrib.domain == 'POINT':
            obj.data.normals_split_custom_set_from_vertices([[vec[0],vec[1],vec[2]] for vec in a_vals])
        elif src_attrib.domain == 'CORNER':
            obj.data.normals_split_custom_set([[vec[0],vec[1],vec[2]] for vec in a_vals])
    
    # VECTOR2D (FLOAT2)

    elif data_target == "TO_UVMAP":
        obj.data.uv_layers.new(name=src_attrib_name)
        for i, val in enumerate(a_vals):
            obj.data.uv_layers[int(kwargs['uvmap_index'])].data[i].uv = (val[0], val[1])

    # special

    elif data_target == "TO_SELECTED_VERTICES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name

        for i, val in enumerate(a_vals):
            obj.data.attributes[f'.vs.{uvmap_name}'].data[i].value = val

    elif data_target == "TO_SELECTED_EDGES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name

        for i, val in enumerate(a_vals):
            obj.data.attributes[f'.es.{uvmap_name}'].data[i].value = val

    else:
        raise etc.MeshDataWriteException("set_mesh_data", f"Can't find {data_target} to set")
    return True
        
def get_all_mesh_data_ids_of_type(obj,data_type):
    """
    Gets each unique indentifiers (index) for data type to iterate on to, and to then evaluate every case
    Does not check for invalid input or invalid data
    """

    if data_type in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"]:   
        return [vg.index for vg in obj.vertex_groups]     

    elif data_type in ["VERT_SHAPE_KEY_POSITION" , "VERT_SHAPE_KEY_POSITION_OFFSET"]:
        return [i for i, sk in enumerate(obj.data.shape_keys.key_blocks)]

    elif data_type == "FACE_FROM_FACE_MAP":
        return list(set([obj.data.face_maps[0].data[i].value  for i, f in enumerate(obj.data.polygons)]))

    elif data_type in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"]:
        return [i for i, mat_slot in obj.material_slots]

    elif data_type in ["FACE_IS_MATERIAL_ASSIGNED"]:
            return [f.material_index for f in obj.data.polygons]


# ------------------------------------------
# Utility

# is this really needed?
def fill_foreachset_val_with_vector(iterable_domain, storage, dimension:int=2, values:list = []):
        for i in iterable_domain:
            for d in range(0, dimension):
                storage[i.index*dimension+d] = values[d]
        return storage

def get_friendly_domain_name(domain_name_raw, plural=False):
    "Convert internal name for domain into friendly user name found in other GUI elements inside of blender"
    if domain_name_raw == 'POINT':
        return "Vertex" if not plural else "Vertices"
    elif domain_name_raw == 'CORNER':
        return "Face Corner" if not plural else "Face Corners"
    else:
        return domain_name_raw.lower().capitalize() if not plural else domain_name_raw.lower().capitalize() + "s"

def get_friendly_data_type_name(data_type_raw):
    if data_type_raw in data.attribute_data_types:
        return data.attribute_data_types[data_type_raw].friendly_name
    else:
        return data_type_raw

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
    if not hasattr(obj, 'face_maps') or not len(obj.face_maps):
        return [("NULL", "[!] No face maps", "")]


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
        return [("NULL", "[!] No material slots", "")]

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
        return [("NULL", "[!] No materials", "")]


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
        return [("NULL", "[!] No Vertex Groups", "")]

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
        return [("NULL", "[!] No Shape Keys", "")]

    for i, sk in enumerate(obj.data.shape_keys.key_blocks):
        items.append((str(i), sk.name, f"Use {sk.name} shape key"))

    #items.append(("CURRENT", "Current Vertex Positions", f"Vertex Positions as you see them now"))
    return items

def get_natively_supported_domains_enum(self, context):
        """
        Returns a list of compatible domains from enum selection in self.domain_data_type, for reading or writing mesh data from object
        SELF HAS TO HAVE self.domain_data_type enum
        """
        items = []
        domains_supported = data.object_data_sources[self.domain_data_type].domains_supported

        # if is_verbose_mode_enabled():
        #     print(f"{self.domain_data_type} supports {domains_supported} domains")
        
        #items.append(("DEFAULT", "Default", "Use default domain for data type"))
        
        if 'POINT' in domains_supported:
            items.append(("POINT", "Vertex", "Use vertex domain for data type"))
        if 'EDGE' in domains_supported:
            items.append(("EDGE", "Edge", "Use edge domain for data type"))
        if 'FACE' in domains_supported:
            items.append(("FACE", "Face", "Use face domain for data type"))
        if 'CORNER' in domains_supported:
            items.append(("CORNER", "Face Corner", "Use face corner domain for data type"))

        return items

def get_mesh_data_enum_default_icon(data_item):
    # set the default icon based on supported domains, if none is set
    if data_item.icon == "":
        domains = data_item.domains_supported
        if len(domains) > 1:
            icon = "MATCUBE"
        elif domains[0] == "POINT":
            icon = "VERTEXSEL"
        elif domains[0] == "EDGE":
            icon = "EDGESEL"
        elif domains[0] == "FACE":
            icon = "FACESEL"
        elif domains[0] == "CORNER":
            icon = "SNAP_PERPENDICULAR"
    else:
        icon = data_item.icon
    return icon


def get_enhanced_enum_title_name(item):
    name = item.enum_gui_friendly_name
    # if etc.get_enhanced_enum_titles_enabled():
    #     name += ' ⁻' 
    #     if 'POINT' in item.domains_supported:
    #         name.append(' ᵛᵉʳᵗᵉˣ')
    #     if 'EDGE' in item.domains_supported:
    #         name += ' ᵉᵈᵍᵉ'
    #     if 'FACE' in item.domains_supported:
    #         name += ' ᶠᵃᶜᵉ'
    #     if 'CORNER' in item.domains_supported:
    #         name += ' ᶜᵒʳⁿᵉʳ'
    return name

def get_source_data_enum(self, context):
    """
    Gets source data enum entries 
    """
    e = []
    for i, item in enumerate(data.object_data_sources):
        if "INSERT_SEPARATOR" in item:
            e.append((None))
        elif "INSERT_NEWLINE" in item:
             e.append(("","","","",i))
        else:
            minver = data.object_data_sources[item].min_blender_ver
            unsupported_from = data.object_data_sources[item].unsupported_from_blender_ver

            name = get_enhanced_enum_title_name(data.object_data_sources[item])
            
            if etc.get_blender_support(minver, unsupported_from): 
                icon = get_mesh_data_enum_default_icon(data.object_data_sources[item])
                e.append((item, name, data.object_data_sources[item].enum_gui_description, icon, i))
    return e

def get_source_data_enum_without_separators(self, context):
    """
    Gets source data enum entries without separators and newlines
    """
    e = []
    for i, item in enumerate(data.object_data_sources):
        if "INSERT_SEPARATOR" in item or "INSERT_NEWLINE" in item:
            continue
        else:
            minver = data.object_data_sources[item].min_blender_ver
            unsupported_from = data.object_data_sources[item].unsupported_from_blender_ver
            
            name = get_enhanced_enum_title_name(data.object_data_sources[item])

            if etc.get_blender_support(minver, unsupported_from): 
                icon = get_mesh_data_enum_default_icon(data.object_data_sources[item])
                e.append((item, name, data.object_data_sources[item].enum_gui_description, icon, i))
    return e

def get_target_data_enum(self, context):
    """
    Gets data targets to show in gui
    """
    items = []
    obj = context.active_object
    active_attrib = obj.data.attributes.active
    inv_data_entry = ("NULL", "[!] No Convertable Data", "")


    for i, entry in enumerate(data.object_data_targets):
        if "INSERT_SEPARATOR" in entry:
            items.append((None))
        elif "INSERT_NEWLINE" in entry:
            items.append(("","","","",i))
        else:
            minver = data.object_data_targets[entry].min_blender_ver
            unsupported_from = data.object_data_targets[entry].unsupported_from_blender_ver

            if etc.get_blender_support(minver, unsupported_from): 
                icon = get_mesh_data_enum_default_icon(data.object_data_targets[entry])
                item = (entry,
                        data.object_data_targets[entry].enum_gui_friendly_name, 
                        data.object_data_targets[entry].enum_gui_description,
                        icon,
                        i
                        )
                items.append(item)

    # this should not happen but since it is here...
    if not len(items):
        return [inv_data_entry]
    
    return items

def get_target_compatible_domains(self, context):
    """
    Gets compatible domains for selected data target, to store it in it
    eg. vertex and edge mean bevel, which one?
    """
    # req: self.data_target

    domains_supported = data.object_data_targets[self.data_target].domains_supported
    items = []

    if 'POINT' in domains_supported:
        items.append(("POINT", "Vertex", "Store this data in vertices"))
    if 'EDGE' in domains_supported:
        items.append(("EDGE", "Edge", "Store this data in edges"))
    if 'FACE' in domains_supported:
        items.append(("FACE", "Face", "Store this data in faces"))
    if 'CORNER' in domains_supported:
        items.append(("CORNER", "Face Corner", "Store this data in face corners"))
    
    return items

def get_attribute_data_types_enum(self,context):
    """
    Gets attribute data types for this blender version
    """
    l = []  
    for item in data.attribute_data_types:
        if etc.get_blender_support(data.attribute_data_types[item].min_blender_ver, data.attribute_data_types[item].unsupported_from_blender_ver):
            l.append((item, data.attribute_data_types[item].friendly_name, ""))
    return l

def get_attribute_domains_enum(self, context):
    """
    Gets attribute domains for this blender version
    """
    l = []
    for item in data.attribute_domains:
        if etc.get_blender_support(data.attribute_domains[item].min_blender_ver, data.attribute_domains[item].unsupported_from_blender_ver):
            l.append((item, data.attribute_domains[item].friendly_name, ""))
    return l

def conditional_selection_poll(self, context):
    """
    poll function of any operator that calls conditional selection
    """
    return (context.active_object
                and context.active_object.mode == 'EDIT' 
                and context.active_object.type == 'MESH' 
                and context.active_object.data.attributes.active 
                and get_is_attribute_valid(context.active_object.data.attributes.active.name))

def get_attribute_invert_modes(self, context):
    return [
                ("MULTIPLY_MINUS_ONE", "Multiply by -1", ""),
                ("ADD_TO_MINUS_ONE", "Add to -1", ""),
                ("SUBTRACT_FROM_ONE", "Subtract from 1", ""),
            ]

def get_float_int_attributes(self, context):
    obj = context.active_object

    enum_entries = []
    inv_data_entry = ("NULL", "[!] No valid attribues", "This list should contain all Integer and Float Attributes store in Vertices")

    for attrib in obj.data.attributes:
        if attrib.domain == 'POINT' and attrib.data_type in ['INT', 'FLOAT']:
            enum_entries.append((attrib.name, attrib.name, f"Use {attrib.name} as a source attribute"))
    
    if not len(enum_entries):
        return [inv_data_entry]
    
    return enum_entries

def get_uvmaps_enum(self, context):
    """
    Gets all UVMaps of an active object

    Index can be 'NULL' if invalid
    (INDEX NAME DESC)
    """

    items = []
    obj = context.active_object

    # case: no data
    if not len(obj.data.uv_layers):
        return [("NULL", "NO UVMAPS", "")]


    for i, uvmap in enumerate(obj.data.uv_layers):
        items.append((str(i), uvmap.name, f"Use {uvmap.name} UVMap"))

    return items

def is_verbose_mode_enabled():
    return etc.get_preferences_attrib('verbose_mode')