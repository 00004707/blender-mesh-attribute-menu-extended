# Object related
# ------------------------------------------

import func.util_func
from func.attribute_func import get_attribute_values, get_safe_attrib_name, set_attribute_values
from func.util_func import is_pinned_mesh_used, linear_to_srgb
from modules import LEGACY_etc
from func.util_func import get_pinned_mesh_object_and_mesh_reference


def get_object_in_context(context = None, b_force_active_object = False):

    """Gets object reference and object data refenence for object in context. eg. Active object or pinned object

    Args:
        context (Optional): Blender Context  
        b_force_active_object (bool): Always get active object in the viewport

    Returns:
        obj: Object reference
        obj_data: Object data reference
    """

    if context is None:
        context = bpy.context

    # If it's pinned mesh, we need to get data and reference from somewhere else.
    b_pinned_mesh_in_use = is_pinned_mesh_used(context)

    if b_pinned_mesh_in_use and not b_force_active_object:
        obj, obj_data = get_pinned_mesh_object_and_mesh_reference(context)
        if obj is not None:
            LEGACY_etc.log(get_object_in_context, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
        else:
            LEGACY_etc.log(get_object_in_context, f"Cannot find reference for object in context", LEGACY_etc.ELogLevel.WARNING)
    else:
        obj_data = context.active_object.data
        obj = context.active_object

    return obj, obj_data


def set_object_in_context_as_active(self, context):
    """Sets the object in context, active or pinned, as active (usually to change object mode and act like it's selected and active)

    Args:
        context (ref): Context
    """

    obj, obj_data = get_object_in_context(context)
    self._current_active_object = bpy.context.active_object
    self._current_selection_state_of_obj = bpy.context.active_object.select_get()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def set_object_by_user_as_active_back(self, context):
    """Restores the selected and active state of object before set_object_in_context_as_active

    Args:
        context (ref): Context
    """

    bpy.context.view_layer.objects.active = self._current_active_object
    bpy.context.view_layer.objects.active.select_set(self._current_selection_state_of_obj)


# Mesh related
# ------------------------------------------

# get

def get_mesh_selected_domain_indexes(obj, domain, spill=False):
    """Gets the indexes of selected domain entries in edit mode. (Vertices, edges, faces or Face Corners)

    Args:
        obj (Reference): 3D Object Reference
        domain (str): Mesh Domain
        spill (bool, optional): Enables selection spilling to nearby face corners from selected verts/faces/edges. Defaults to False.

    Raises:
        etc.MeshDataReadException: If domain is unsupported

    Returns:
        list: List of indexes
    """

    if domain == 'POINT':
        if obj.type == 'MESH':
            storage = np.zeros(len(obj.data.vertices), dtype=bool)
            obj.data.vertices.foreach_get('select', storage)
            return np.arange(0, len(obj.data.vertices))[storage]

        elif obj.type == 'CURVES':
            if '.selection' in obj.data.attributes:

                # Selection attribute can be in point domain or curve domain, depending on edit mode interaction mode
                # Point to point
                if obj.data.attributes['.selection'].domain == 'POINT':
                    storage = np.zeros(len(obj.data.points), dtype=bool)
                    obj.data.attributes['.selection'].data.foreach_get('value', storage)
                    if LEGACY_etc.is_full_logging_enabled():
                        LEGACY_etc.log(get_mesh_selected_domain_indexes, f"Selected curve point IDs: {np.arange(0, len(obj.data.points))[storage]}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)
                    return np.arange(0, len(obj.data.points))[storage]

                # Curve to point
                else:
                    selected_splines = get_mesh_selected_domain_indexes(obj, 'CURVE')
                    point_ids = []
                    for s_id in selected_splines:
                        for point in obj.data.curves[s_id].points:
                            point_ids.append(point.index)

                    return np.arange(0, len(obj.data.points))[point_ids]

            else:
                return []


        else:
            raise LEGACY_etc.exceptions.MeshDataReadException('get_mesh_selected_domain_indexes', f'The {obj.type} object type is not supported')

    elif domain == 'EDGE':
        storage = np.zeros(len(obj.data.edges), dtype=bool)
        obj.data.edges.foreach_get('select', storage)
        return np.arange(0, len(obj.data.edges))[storage]

    elif domain == 'FACE':
        storage = np.zeros(len(obj.data.polygons), dtype=bool)
        obj.data.polygons.foreach_get('select', storage)
        return np.arange(0, len(obj.data.polygons))[storage]

    elif domain == 'CURVE':

        # As of 4.2 alpha selection of curves is invisble, but possible
        if '.selection' in obj.data.attributes:

            # If selection is on points, convert it to curves
            if obj.data.attributes['.selection'].domain == 'POINT':
                selected_points = get_mesh_selected_domain_indexes(obj, 'POINT')
                selected_curve_ids = []
                for curve in obj.data.curves:
                    for point in curve.points:
                        if point.index in selected_points:
                            selected_curve_ids.append(curve.index)
                            break
                if LEGACY_etc.is_full_logging_enabled():
                    LEGACY_etc.log(get_mesh_selected_domain_indexes, f"Selected curve IDs: {selected_curve_ids}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)
                return selected_curve_ids

            # If seletion is on curves, just return it
            else:
                storage = np.zeros(len(obj.data.curves), dtype=bool)
                obj.data.attributes['.selection'].data.foreach_get('value', storage)
                return np.arange(0, len(obj.data.curves))[storage]

        else:
            return []


    elif domain == 'CORNER':
        # boneless chicken 
        if spill:
            # Get selected verts ids
            storage = np.zeros(len(obj.data.vertices), dtype=bool)
            obj.data.vertices.foreach_get('select', storage)
            sel_verts = np.arange(0, len(obj.data.vertices))[storage]

            # Get loop assigned verts
            storage = np.zeros(len(obj.data.loops), dtype=int)
            obj.data.loops.foreach_get('vertex_index', storage)

            # Get the loops with the selected verts
            return np.arange(0, len(obj.data.loops))[np.isin(storage, sel_verts)]

        else:
            mesh_selected_modes = bpy.context.scene.tool_settings.mesh_select_mode
            result = [] # ???

            # Case: User wants to assign faces
            if mesh_selected_modes[2]: # faces

                # Get selected faces
                face_select = np.zeros(len(obj.data.polygons), dtype=bool)
                obj.data.polygons.foreach_get('select', face_select)

                # Get face loop indexes
                #face_loop_start_ids = np.zeros(len(obj.data.polygons), dtype=int)
                #obj.data.polygons.foreach_get('loop_start', face_loop_indices) # why not?

                face_loop_indices = []
                for i in np.arange(0, len(obj.data.polygons))[face_select]:
                    face_loop_indices += obj.data.polygons[i].loop_indices
                return np.unique(face_loop_indices)#[face_select])

            # Case User wants to select individual face corners by edge selection (detect same for vert selection)
            else:

                # get selected edges
                b_sel_edges = np.zeros(len(obj.data.edges), dtype=bool)
                obj.data.edges.foreach_get('select', b_sel_edges)
                sel_edges = np.arange(0, len(obj.data.edges))[b_sel_edges]

                # go away if none selected
                if not len(sel_edges):
                    return []

                # get edge indexes for all loops
                loops_edge_index = np.zeros(len(obj.data.loops), dtype=int)
                obj.data.loops.foreach_get('edge_index', loops_edge_index)

                # get loops that are connected to selected edges
                loop_ids_of_selected_edges = np.arange(0, len(obj.data.loops))[np.isin(loops_edge_index, sel_edges)]

                if LEGACY_etc.is_full_logging_enabled():
                    LEGACY_etc.log(get_mesh_selected_domain_indexes, f"The selection might be one of {loop_ids_of_selected_edges} fcs", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                for fc in [obj.data.loops[li] for li in loop_ids_of_selected_edges]:

                    # Get face that has this loop
                    for f in obj.data.polygons:
                        if fc.index in f.loop_indices:
                            face = f
                            break

                    if LEGACY_etc.is_full_logging_enabled():
                        LEGACY_etc.log(get_mesh_selected_domain_indexes, f"Face {face.index} has fc {fc.index}"\
                       f"Face {face.index} has vts {[v for v in face.vertices]}"\
                       f"Looking for vert {fc.vertex_index}"\
                       f"Looking in face {face.index}: {list(obj.data.polygons[face.index].loop_indices)}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                    valid_edges = []
                    for i in obj.data.polygons[face.index].loop_indices:
                        if b_sel_edges[obj.data.loops[i].edge_index]:
                            edge = obj.data.edges[obj.data.loops[i].edge_index]
                            #print(f"{face.index}: has edge with verts {edge.vertices}")
                            edge_verts = [v for v in edge.vertices]

                            if fc.vertex_index in edge_verts:
                                valid_edges.append(edge.index)
                                #print(f"{edge.index} contains the vert of fc")

                    # check if at least two of those edges are selected

                    if len(valid_edges) > 1:
                        result.append(fc.index)

                return result

    else:
        raise LEGACY_etc.exceptions.MeshDataReadException('get_mesh_selected_domain_indexes', f'The {domain} domain is not supported')


def get_filtered_indexes_by_condition(source_data: list, condition:str, compare_value, case_sensitive_string = False, vector_convert_to_srgb= False):
    """Gets indexes of the list that store values that meet selected condition

    Currently only one dimensional lists are supported.

    Args:
        source_data (list): The list with data
        condition (str): The condition to check
        compare_value (variable): The value to check the condition with
        case_sensitive_string (bool, optional): Whether the strings should be compared with case sensitivity or not. Defaults to False.
        convert_to_srgb (bool, optional): When working with BYTE_COLOR, setting the value might be converted to SRGB colorspace
    Returns:
        list: _Indexes of the list that meet the criteria
    """
        # todo flatten the list or handle vectors somehow
        # there has to be an easier way, what the hell is this

    if vector_convert_to_srgb:
        compare_value = linear_to_srgb(compare_value, False)

    indexes = []
    LEGACY_etc.log(get_filtered_indexes_by_condition, f"""Get filtered indexes with settings:
{condition} to {compare_value}, 
case sensitive {case_sensitive_string}
convert compare value to srgb {vector_convert_to_srgb}""", LEGACY_etc.ELogLevel.VERBOSE)
    if LEGACY_etc.preferences.get_preferences_attrib("en_slow_logging_ops"):
        if vector_convert_to_srgb:
            srgbs = [linear_to_srgb(i, return_float=False) for i in source_data]
            LEGACY_etc.log(get_filtered_indexes_by_condition, "on dataset (int) (len {len(source_data)}) {srgbs}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)
        else:
            LEGACY_etc.log(get_filtered_indexes_by_condition, f"on dataset (float) (len {len(source_data)}) {source_data}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)
    else:
        LEGACY_etc.log(get_filtered_indexes_by_condition, f"dataset *skipped*", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

    #booleans
    if type(source_data[0]) is bool:
        for i, data in enumerate(source_data):
            if condition == "EQ" and data == compare_value:
                indexes.append(i)

            elif condition == "NEQ" and data != compare_value:
                indexes.append(i)

    # numeric values & floats invididual vals
    elif type(source_data[0]) in [int, float, np.int32, np.float32, np.float64]:
        for i, data in enumerate(source_data):
            if vector_convert_to_srgb:
                data = linear_to_srgb(data, False)
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
                cmp = compare_value

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
    else:
        raise LEGACY_etc.exceptions.GenericFunctionParameterError("get_filtered_indexes_by_condition", f"Unsupported input data type: {type(source_data[0])}")

    LEGACY_etc.log(get_filtered_indexes_by_condition, f"Filtered indexes: {indexes}", LEGACY_etc.ELogLevel.VERBOSE)
    return indexes


def get_domain_attribute_values(obj, domain, attribute_name):
    """Gets values of attribute stored in domain like: edges[0].use_sharp 

    Args:
        obj (Reference): 3D Object Reference
        domain (str): Name of the domain: POINT EDGE FACE CORNER
        attribute_name (str): Name of the attribute to set eg. use_sharp

    Returns:
        list: A list of values in that attribute. The type of values in list is variable.
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
        raise LEGACY_etc.exceptions.MeshDataReadException("get_domain_attribute_values", f"Failed to get {attribute_name} from {domain} \n {e}")


def get_mesh_data(obj, data_type, source_domain, **kwargs):
    """Gets all selected data from mesh.

    Args:
        obj (Reference): Object Reference
        data_type (str): The data type to fetch. See data.object_data_sources
        source_domain (str): The domain to take this data from

        kwargs: (if applicable)
        * vg_index              index of vertex group [id]
        * sk_index              index of shape key [id]
        * vg_offset_index       index of vertex group and the vertex group to offset from [id1, id2]
        * fm_index              face map index
        * sel_mat               selected material
        * mat_index             material index
        * uvmap_index           uvmap index

    Raises:
        etc.MeshDataReadException: on failure if selected data type does not exist

    Returns:
        list: _All values. Might conatain tuples or multi level lists.
    """


    LEGACY_etc.log(get_mesh_data, f"get_mesh_data_kwargs: {kwargs}", LEGACY_etc.ELogLevel.VERBOSE)
    LEGACY_etc.log(get_mesh_data, f"Reading {data_type} mesh data on {source_domain}...", LEGACY_etc.ELogLevel.VERBOSE)

    # DOMAIN INDEX
    if data_type == "INDEX":

        if source_domain == "POINT":
            return [i for i, vert in enumerate(obj.data.vertices)]

        elif source_domain == "EDGE":
            return [i for i, edge in enumerate(obj.data.edges)]

        elif source_domain == "FACE":
            return [i for i, face in enumerate(obj.data.polygons)]

        elif source_domain == "CORNER":
            return [i for i, corner in enumerate(obj.data.loops)]

    # VISIBILITY IN EDIT MODE
    elif data_type == "VISIBLE":
        return [not val for val in get_domain_attribute_values(obj, source_domain, "hide")]

    elif data_type == "HIDDEN":
        return [val for val in get_domain_attribute_values(obj, source_domain, "hide")]

    # SELECTED
    elif data_type == "SELECTED":
        return get_domain_attribute_values(obj, source_domain, "select")

    # NOT SELECTED
    elif data_type == "NOT_SELECTED":
        return [not val for val in get_domain_attribute_values(obj, source_domain, "select")]

    # POSITION
    elif data_type == "POSITION":
        if source_domain == 'POINT':
            return get_domain_attribute_values(obj, source_domain, "co")

        elif source_domain == 'EDGE':
            pairs = get_domain_attribute_values(obj, source_domain, "vertices")
            storage = []
            for i, vert_pair in enumerate(pairs):
                pos_0 = obj.data.vertices[vert_pair[0]].co
                pos_1 = obj.data.vertices[vert_pair[1]].co
                edge_pos = (pos_0 + pos_1)/2
                storage.append(edge_pos)
            return storage

        elif source_domain == 'FACE':
            return [val for val in get_domain_attribute_values(obj, source_domain, "center")]

    # NORMALS
    elif data_type == "NORMAL":
        if source_domain == "POINT":
            return [vec.vector for vec in obj.data.vertex_normals]

        elif source_domain == "FACE":
            return [vec.vector for vec in obj.data.polygon_normals]

    # CUSTOM SPLIT NORMALS
    elif data_type == "SPLIT_NORMALS":
            return get_domain_attribute_values(obj, source_domain, "normal")

    # VERTEX MESH ATTRIBUTES START
    # -----------------------------

    # VERTEX MEAN BEVEL
    elif data_type == "VERT_MEAN_BEVEL":

        if hasattr(obj.data.vertices, "bevel_weight"):
            return get_domain_attribute_values(obj, source_domain, "bevel_weight")
        else:
            if not "bevel_weight_vert" in obj.data.attributes:
                return [0.0] * len(obj.data.vertices)
            else:
                return [bevel.value for bevel in obj.data.attributes["bevel_weight_vert"].data]


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
        if bpy.app.version < (4,1):
            if not len(obj.data.vertex_paint_masks):
                return [0.0] * len(obj.data.vertices)
            else:
                return [mask.value for mask in obj.data.vertex_paint_masks[0].data]
        else:
            if not ".sculpt_mask" in obj.data.attributes:
                return [0.0] * len(obj.data.vertices)
            else:
                return [sm.value for sm in obj.data.attributes[".sculpt_mask"].data]

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
            offset_from[vert.index] = offset_to[vert.index] - offset_from[vert.index]
        return offset_from


    # EDGE MESH ATTRIBUTES START
    # -----------------------------

    # EDGE SEAM
    elif data_type == "EDGE_SEAM":
        return get_domain_attribute_values(obj, source_domain, "use_seam")

    # EDGE BEVEL WEIGHT
    elif data_type == "EDGE_BEVEL_WEIGHT":

        if hasattr(obj.data.vertices, "bevel_weight"):
            return get_domain_attribute_values(obj, source_domain, "bevel_weight")
        else:
            if not "bevel_weight_edge" in obj.data.attributes:
                return [0.0] * len(obj.data.edges)
            else:
                return [bevel.value for bevel in obj.data.attributes["bevel_weight_edge"].data]

    # EDGE CREASE
    elif data_type == "EDGE_CREASE":
        if bpy.app.version < (4,0):
            return get_domain_attribute_values(obj, source_domain, "crease")
        else:
            if not "edge_creases" in obj.data.attributes:
                return [0.0] * len(obj.data.edges)
            else:
                return [crease.value for crease in obj.data.attributes["edge_creases"].data.values()]

    # EDGE SHARP
    elif data_type == "EDGE_SHARP":
        if hasattr(obj.data.edges, "use_sharp"):
            return get_domain_attribute_values(obj, source_domain, "use_sharp")
        elif hasattr(obj.data.edges, "use_edge_sharp"):
            return get_domain_attribute_values(obj, source_domain, "use_edge_sharp")
        else:
            if not "sharp_edge" in obj.data.attributes:
                return [False] * len(obj.data.edges)
            else:
                return [sharp.value for sharp in obj.data.attributes["sharp_edge"].data]


    # EDGE FREESTYLE MARK
    elif data_type == "EDGE_FREESTYLE_MARK":
        return get_domain_attribute_values(obj, source_domain, "use_freestyle_mark")

    # EDGE IS LOOSE
    elif data_type == "EDGE_IS_LOOSE":
        return get_domain_attribute_values(obj, source_domain, "is_loose")

    # EDGE_VERTICES
    elif data_type == "EDGE_VERTICES":
        return get_domain_attribute_values(obj, source_domain, "vertices")

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
        return get_domain_attribute_values(obj, source_domain, "area")

    # FACE IS SMOOTH SHADED
    elif data_type == "FACE_USE_SMOOTH":
        if not hasattr(obj.data.polygons[0], "use_smooth"):
            return get_domain_attribute_values(obj, source_domain, "use_smooth")
        else: # futureproofing
            if not "sharp_face" in obj.data.attributes:
                return [False] * len(obj.data.polygons)
            else:
                return [faceset.value for faceset in obj.data.attributes["sharp_face"].data]

    # FACE MATERIAL INDEX
    elif data_type == "FACE_MATERIAL_INDEX":
        if not hasattr(obj.data.polygons[0], "material_index"):
            return get_domain_attribute_values(obj, source_domain, "material_index")
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
        return get_domain_attribute_values(obj, source_domain, "loop_total")

    # FACE CORNER START INDEX
    elif data_type == "FACE_CORNER_START_INDEX":
        return get_domain_attribute_values(obj, source_domain, "loop_start")

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
        return get_domain_attribute_values(obj, source_domain, "tangent")

    # BITANGENT
    elif data_type == "CORNER_BITANGENT":
        return get_domain_attribute_values(obj, source_domain, "bitangent")

    # BITANGENT SIGN
    elif data_type == "CORNER_BITANGENT_SIGN":
        return get_domain_attribute_values(obj, source_domain, "bitangent_sign")

    # EDGE INDEX
    elif data_type == "CORNER_EDGE_INDEX":
        return get_domain_attribute_values(obj, source_domain, "edge_index")

    # VERTEX INDEX
    elif data_type == "CORNER_VERTEX_INDEX":
        return get_domain_attribute_values(obj, source_domain, "vertex_index")

    # UVMAP
    elif data_type == "UVMAP":
        return [map.uv for map in obj.data.uv_layers[int(kwargs['uvmap_index'])].data]


    # -----------------------------
    # SPECIAL ATTRIBS START

    # SELECTED VERTS IN UV EDITOR
    elif data_type == "SELECTED_VERTICES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        attribute_name = f".vs.{uvmap_name}"
        if attribute_name in obj.data.attributes:
            return [es.value for es in obj.data.attributes[attribute_name].data]
        else:
            return [False] * len(obj.data.loops)

    # SELECTED EDGES IN UV EDITOR
    elif data_type == "SELECTED_EDGES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        attribute_name = f".es.{uvmap_name}"
        if attribute_name in obj.data.attributes:
            return [es.value for es in obj.data.attributes[attribute_name].data]
        else:
            return [False] * len(obj.data.loops)

    # SELECTED EDGES IN UV EDITOR
    elif data_type == "PINNED_VERTICES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        attribute_name = f".pn.{uvmap_name}"
        if attribute_name in obj.data.attributes:
            return [es.value for es in obj.data.attributes[attribute_name].data]
        else:
            return [False] * len(obj.data.loops)

    else:
        raise LEGACY_etc.exceptions.MeshDataReadException("get_mesh_data", f"Invalid domain data type ({data_type}) or this data is not available on this domain ({source_domain})")


# set

def set_domain_attribute_values(obj, attribute_name:str, domain:str, values: list):
    """Sets values of attribute stored in domain like: edges[0].use_sharp 

    Args:
        obj (Reference): 3D Object Reference
        attribute_name (str): Name of the attribute
        domain (str): Attribute Domain
        values (list): Values to set 
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
    """Sets the selection or visibility in edit mode.
    Those require setting the state of faces, edges and vertices separately, hence the separate function.

    Args:
        obj (Reference ): 3D Object Reference
        domain (str): Domain - POINT EDGE FACE CORNER
        indexes (list): Domain indexes to set the state
        state (bool, optional): The state of visibility or selection. Defaults to True.
        selection (bool, optional): Whether toggle selection or visibility. Defaults to True.

    Raises:
        Exception: On failure, re-raises the exception and clears bmesh
    """
    LEGACY_etc.log(get_mesh_data, f"Setting sel/vis {selection} to state  {state} on {domain}, \ndataset {indexes}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

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
        if LEGACY_etc.preferences.get_preferences_attrib("select_attribute_precise_facecorners"):
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
                if LEGACY_etc.preferences.get_preferences_attrib("en_slow_logging_ops"):
                    LEGACY_etc.log(set_selection_or_visibility_of_mesh_domain, f"loop {cornerindex} has edges {[edge.index for edge in edges]}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)
                    LEGACY_etc.log(set_selection_or_visibility_of_mesh_domain, f"loop {cornerindex} has a face {faceindex}, with edges {[edge.index for edge in bm.faces[faceindex].edges]}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                # get edges that are in face index of this corner
                for edge in edges:
                    if edge in bm.faces[faceindex].edges:
                        edge_indexes_to_select.append(edge.index)

            bm.free()
            if LEGACY_etc.preferences.get_preferences_attrib("en_slow_logging_ops"):
                LEGACY_etc.log(set_selection_or_visibility_of_mesh_domain, f"Filtered edges of the corner are {edge_indexes_to_select}", LEGACY_etc.ELogLevel.SUPER_VERBOSE)
            set_selection_or_visibility_of_mesh_domain(obj, 'EDGE', edge_indexes_to_select, state, selection)

        # The fast method
        elif len(indexes):
            mesh_selected_modes = bpy.context.scene.tool_settings.mesh_select_mode

            storage = np.zeros(len(obj.data.loops), dtype=int)

            # User is in edit mode with edge or face selection mode
            if mesh_selected_modes[1] or mesh_selected_modes[2]:
                obj.data.loops.foreach_get('edge_index', storage)
                storage = np.take(storage, indexes)
                set_selection_or_visibility_of_mesh_domain(obj, 'EDGE', storage, state, selection)

            # Any other mode 
            else:
                obj.data.loops.foreach_get('vertex_index', storage)
                storage = np.take(storage, indexes)
                set_selection_or_visibility_of_mesh_domain(obj, 'POINT', storage, state, selection)


def set_mesh_data(obj, data_target:str , src_attrib, new_data_name = "", overwrite = False, **kwargs):
    """Sets mesh data from selected attribute

    Args:
        obj (Reference): 3D Object Reference
        data_target (str): See data.object_data_targets
        src_attrib (Reference): Attribute reference
        new_data_name (str): The name of new shape key, vertex group etc.
        overwrite (boolean): if name of the shape key/vertex group exists, replace the data

        kwargs: (If applicable)
        * enable_auto_smooth        bool
        * apply_to_first_shape_key  bool
        * to_vgindex_weight         float
        * to_vgindex_weight_mode    enum - STATIC, ATTRIBUTE
        * to_vgindex_src_attrib     attribute reference
        * uvmap_index               integer
        * invert_sculpt_mask        boolean, 1-clamped sculpt mask val
        * expand_sculpt_mask_mode   enum REPLACE EXPAND SUBTRACT
        * normalize_mask            boolean
        * raw_data                  list, if attribute is none this can set the values directly


    Raises:
        etc.MeshDataWriteException: On failure if selected data target is not supported

    Returns:
        Nothing
    """

    def foreach_get_mesh_data_value(data, prop):
        sample = getattr(data[0], prop)
        if type(sample) in [tuple, list]:
            storage_multi = len(sample)
        else:
            storage_multi = 1
        storage = [None] * len(data) * storage_multi
        data.foreach_get(prop, storage)
        return storage

    def foreach_set_mesh_data_value(data, prop, values):
        data.foreach_set(prop, values)
        return True

    if 'raw_data' in kwargs:
        a_vals = kwargs['raw_data']
    else:
        a_vals = get_attribute_values(src_attrib, obj)

    LEGACY_etc.log(set_mesh_data, f"Setting mesh data {data_target} from {src_attrib}, \nvalues: {a_vals}, \nkwargs: {kwargs}, \ncustom name: {new_data_name}", LEGACY_etc.ELogLevel.VERBOSE)

    if 'raw_data' not in kwargs:
        src_attrib_name = src_attrib.name # for setting active attribute ONLY

    # QUICK BOOLEANS
    # -----------------------------

    # TO VISIBLE
    if data_target == "TO_VISIBLE":
        vis_indexes = [index for index, value in enumerate(a_vals) if value]
        set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, vis_indexes, False, selection=False)

    # TO HIDDEN
    elif data_target == "TO_HIDDEN":
        hid_indexes = [index for index, value in enumerate(a_vals) if value]
        set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, hid_indexes, True, selection=False)

    # TO SELECTED
    elif data_target == "TO_SELECTED":
        sel_indexes = [index for index, value in enumerate(a_vals) if value]
        set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, sel_indexes, True)

    # TO NOT SELECTED
    elif data_target == "TO_NOT_SELECTED":
         nsel_indexes = [index for index, value in enumerate(a_vals) if value]
         set_selection_or_visibility_of_mesh_domain(obj, src_attrib.domain, nsel_indexes, False)


    # VERTEX MESH DATA
    # -----------------------------

    # TO VERTEX GROUP INDEX
    elif data_target == "TO_VERTEX_GROUP_INDEX":

        # clamp to max index
        max_index_input = max(a_vals)
        max_index_target = len(obj.vertex_groups) - 1
        max_index = max(min([max_index_input, max_index_target]), 0)

        if kwargs["to_vgindex_weight_mode"] == 'STATIC':
            #lazy set the weight to static value
            for i, val in enumerate(a_vals):
                obj.vertex_groups[min([max_index, max(val,0)])].add([i], kwargs['to_vgindex_weight'], 'REPLACE')

        # or use attrib
        elif kwargs["to_vgindex_weight_mode"] == 'ATTRIBUTE':
            for i, val in enumerate(a_vals):

                obj.vertex_groups[min([max_index, max(val,0)])].add([i], kwargs['to_vgindex_src_attrib'].data[i].value, 'REPLACE')

    # TO SCULPT MODE MASK
    elif data_target == "TO_SCULPT_MODE_MASK":

        # case: no mask layer, user never used mask on this mesh

        if func.util_func.get_blender_support((4,1,0)):
            if not obj.data.vertex_paint_mask:
                obj.data.vertex_paint_mask_ensure()
        else:
            if not len(obj.data.vertex_paint_masks):
                # I have not found a way to create a mask layer without using bmesh, so here it goes
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                bm.verts.layers.paint_mask.verify()
                bm.to_mesh(obj.data)
                bm.free()

                if 'raw_data' not in kwargs:
                    src_attrib = obj.data.attributes[src_attrib_name] # !important

        if kwargs['invert_sculpt_mask']:
            for i in range(0, len(a_vals)):
                a_vals[i] = 1 - a_vals[i]

        if kwargs['expand_sculpt_mask_mode'] != 'REPLACE':
            if func.util_func.get_blender_support((4,1,0)):
                storage = get_attribute_values(obj.data.attributes[".sculpt_mask"], obj)
            else:
                storage = foreach_get_mesh_data_value(obj.data.vertex_paint_masks[0].data, 'value')

            if kwargs['expand_sculpt_mask_mode'] == 'EXPAND':
                for i in range(0, len(storage)):
                    a_vals[i] = storage[i] + a_vals[i]
            elif kwargs['expand_sculpt_mask_mode'] == 'SUBTRACT':
                for i in range(0, len(storage)):
                    a_vals[i] = storage[i] - a_vals[i]

        if kwargs['normalize_mask']:
            for i, val in enumerate(a_vals):
                a_vals[i] = min(max(val, 0.0), 1.0)

        if func.util_func.get_blender_support((4,1,0)):
            set_attribute_values(obj.data.attributes[".sculpt_mask"], a_vals)
        else:
            foreach_set_mesh_data_value(obj.data.vertex_paint_masks[0].data, 'value', a_vals)


    # TO VERTEX GROUP
    elif data_target == "TO_VERTEX_GROUP":
        name = get_safe_attrib_name(obj, new_data_name, 'Group', check_attributes=True)
        if name in obj.vertex_groups and overwrite:
            vg = obj.vertex_groups[name]
        else:
            vg = obj.vertex_groups.new(name=name)

        for vert in obj.data.vertices:
            weight = a_vals[vert.index]
            vg.add([vert.index], weight, 'REPLACE')

    # TO POSITION
    elif data_target == "TO_POSITION":
        set_domain_attribute_values(obj, 'co', src_attrib.domain, a_vals)

        # Apply to first shape key too, if enabled
        if hasattr(obj.data.shape_keys, 'key_blocks') and kwargs["apply_to_first_shape_key"]:
            sk = obj.data.shape_keys.key_blocks[obj.data.shape_keys.key_blocks.keys()[0]].data
            for i, val in enumerate(a_vals):
                sk[i].co = val

    # TO SHAPE KEY
    elif data_target == "TO_SHAPE_KEY":
        if new_data_name in obj.data.shape_keys.key_blocks and overwrite:
            sk = obj.data.shape_keys.key_blocks[new_data_name]
        else:
            sk = obj.shape_key_add(name=new_data_name)

        l = [[vec[0],vec[1],vec[2]] for vec in a_vals]
        for vert in obj.data.vertices:
            sk.data[vert.index].co = l[vert.index]

    # VERTEX & EDGE MESH DATA
    # -----------------------------

    # TO MEAN BEVEL WEIGHT
    elif data_target == "TO_MEAN_BEVEL_WEIGHT":
        if hasattr(obj.data.vertices, 'bevel_weight'): # Works for edges too, as the api change happened for both at once.
            set_domain_attribute_values(obj, 'bevel_weight', src_attrib.domain, a_vals)
        else:
            if src_attrib.domain == 'POINT':
                if not "bevel_weight_vert" in obj.data.attributes:
                    obj.data.attributes.new("bevel_weight_vert", 'FLOAT', 'POINT')
                set_attribute_values(obj.data.attributes["bevel_weight_vert"], a_vals)

            elif src_attrib.domain == 'EDGE':
                if not "bevel_weight_edge" in obj.data.attributes:
                    obj.data.attributes.new("bevel_weight_edge", 'FLOAT', 'EDGE')
                set_attribute_values(obj.data.attributes["bevel_weight_edge"], a_vals)

    # TO MEAN CREASE
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
            if bpy.app.version < (4,0):
                set_domain_attribute_values(obj, 'crease', src_attrib.domain, a_vals)
            else:
                if not "edge_creases" in obj.data.attributes:
                    obj.data.attributes.new("edge_creases", 'FLOAT', 'EDGE')
                set_attribute_values(obj.data.attributes["edge_creases"], a_vals)

    # EDGE MESH DATA
    # -----------------------------

    # TO EDGE SEAM
    elif data_target == "TO_SEAM":
        set_domain_attribute_values(obj, 'use_seam', src_attrib.domain, a_vals)

    # TO EDGE SHARP
    elif data_target == "TO_SHARP":
        if len(obj.data.edges):
            if hasattr(obj.data.edges[0], "use_sharp"):
                set_domain_attribute_values(obj, "use_sharp", src_attrib.domain, a_vals)
            elif hasattr(obj.data.edges[0], "use_edge_sharp"):
                set_domain_attribute_values(obj, 'use_edge_sharp', src_attrib.domain, a_vals)

    # TO FREESTYLE MARK
    elif data_target == "TO_FREESTYLE_MARK":
        set_domain_attribute_values(obj, 'use_freestyle_mark', src_attrib.domain, a_vals)

    # FACE MESH DATA
    # -----------------------------

    # TO FACE MAP
    elif data_target == "TO_FACE_MAP":
        fm_name = "Face Map" if new_data_name == '' else new_data_name

        if fm_name in obj.face_maps and overwrite:
            fm = obj.face_maps[fm_name].index
        else:
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

    # TO SHADE SMOOTH
    elif data_target == "TO_FACE_SHADE_SMOOTH":
        set_domain_attribute_values(obj, 'use_smooth', src_attrib.domain, a_vals)

    # TO SCULPT MODE FACE SETS
    elif data_target == "TO_SCULPT_MODE_FACE_SETS":

        if func.util_func.get_blender_support(minver_unsupported=(4,0,0)):
            # case: no face sets
            if ".sculpt_face_set" not in obj.data.polygon_layers_int:
                obj.data.polygon_layers_int.new(name=".sculpt_face_set" )

            for i, val in enumerate(a_vals):
                obj.data.polygon_layers_int['.sculpt_face_set'].data[i].value = val
        else:
            if not '.sculpt_face_set' in obj.data.attributes:
                obj.data.attributes.new('.sculpt_face_set', 'INT', 'FACE')

            set_attribute_values(obj.data.attributes['.sculpt_face_set'], a_vals)


    # TO MATERIAL INDEX
    elif data_target == "TO_MATERIAL_SLOT_INDEX":
        if len(obj.data.polygons):
            max_index = max((len(obj.material_slots)-1), 0)

            if hasattr(obj.data.polygons[0], 'material_index'):
                if max_index > 0:
                    set_domain_attribute_values(obj, 'material_index', src_attrib.domain, a_vals)

            else: # futureproofing
                if not 'material_index' in obj.data.attributes:
                    obj.data.attributes.new('material_index', 'INT', 'FACE')
                set_attribute_values(obj.data.attributes['material_index'], a_vals)

    # TO FACE MAP INDEX
    elif data_target == "TO_FACE_MAP_INDEX":
        for i, val in enumerate(a_vals):
            # limit the value
            val = max(0, min(val, len(obj.face_maps)-1))
            obj.data.face_maps[0].data[i].value = val

    # FACE CORNER MESH DATA
    # -----------------------------

    # TO SPLIT NORMALS
    elif data_target == 'TO_SPLIT_NORMALS':
        if not func.util_func.get_blender_support((4,1,0)):
            obj.data.use_auto_smooth = kwargs['enable_auto_smooth']
        if src_attrib.domain == 'POINT':
            obj.data.normals_split_custom_set_from_vertices([[vec[0],vec[1],vec[2]] for vec in a_vals])
        elif src_attrib.domain == 'CORNER':
            obj.data.normals_split_custom_set([[vec[0],vec[1],vec[2]] for vec in a_vals])

    # TO UV MAP
    elif data_target == "TO_UVMAP":
        if not (new_data_name in obj.data.uv_layers and overwrite):
            obj.data.uv_layers.new(name=new_data_name)

        for i, val in enumerate(a_vals):
            obj.data.uv_layers[int(kwargs['uvmap_index'])].data[i].uv = (val[0], val[1])

    # UV EDITOR SPECIALS
    # -----------------------------

    # TO SELECTED VERTICES IN UV EDITOR
    elif data_target == "TO_SELECTED_VERTICES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        attribute_name = f'.vs.{uvmap_name}'

        if not attribute_name in obj.data.attributes:
            obj.data.attributes.new(attribute_name, 'BOOLEAN', 'CORNER')

        for i, val in enumerate(a_vals):
            obj.data.attributes[attribute_name].data[i].value = val

    # TO SELECTED EDGES IN UV EDITOR
    elif data_target == "TO_SELECTED_EDGES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        attribute_name = f'.es.{uvmap_name}'

        if not attribute_name in obj.data.attributes:
            obj.data.attributes.new(attribute_name, 'BOOLEAN', 'CORNER')

        for i, val in enumerate(a_vals):
            obj.data.attributes[attribute_name].data[i].value = val

    # TO PINNED VERTICES IN UV EDITOR
    elif data_target == "TO_PINNED_VERTICES_IN_UV_EDITOR":
        uvmap_name = obj.data.uv_layers[int(kwargs['uvmap_index'])].name
        attribute_name = f'.pn.{uvmap_name}'

        if not attribute_name in obj.data.attributes:
            obj.data.attributes.new(attribute_name, 'BOOLEAN', 'CORNER')

        for i, val in enumerate(a_vals):
            obj.data.attributes[attribute_name].data[i].value = val

    # NONE OF ABOVE
    # -----------------------------
    else:
        raise LEGACY_etc.exceptions.MeshDataWriteException("set_mesh_data", f"Can't find {data_target} to set")


def get_all_mesh_data_indexes_of_type(obj,data_type):
    """Gets all indexes of iterable mesh data. Used in batch converting of attributes.

    * Vertex Groups
    * Shape Keys
    * Face Maps
    * Material Slots

    Args:
        obj (Reference): 3D Object Reference
        data_type (str): Namedtuple entry names, see data.object_data_sources

    Returns:
        list: of all indexes
    """

    if data_type in ["VERT_IS_IN_VERTEX_GROUP", "VERT_FROM_VERTEX_GROUP"]:
        return [vg.index for vg in obj.vertex_groups]

    elif data_type in ["VERT_SHAPE_KEY_POSITION" , "VERT_SHAPE_KEY_POSITION_OFFSET"]:
        return [i for i, sk in enumerate(obj.data.shape_keys.key_blocks)]

    elif data_type == "FACE_FROM_FACE_MAP":
        return list(set([obj.data.face_maps[0].data[i].value  for i, f in enumerate(obj.data.polygons)]))

    elif data_type in ["FACE_IS_MATERIAL_SLOT_ASSIGNED"]:
        return [i for i, mat_slot in enumerate(obj.material_slots)]

    elif data_type in ["FACE_IS_MATERIAL_ASSIGNED"]:
        mats = list(set([mat_slot.material for mat_slot in obj.material_slots if mat_slot.material is not None]))
        return [list(bpy.data.materials).index(mat) for mat in mats]

    elif data_type in ["SELECTED_VERTICES_IN_UV_EDITOR", "SELECTED_EDGES_IN_UV_EDITOR", "PINNED_VERTICES_IN_UV_EDITOR", 'UVMAP']:
        return [i for i, uv in enumerate(obj.data.uv_layers)]

    else:
        raise LEGACY_etc.exceptions.GenericFunctionParameterError("get_all_mesh_data_indexes_of_type", f"Data type unsupported?: {data_type}")