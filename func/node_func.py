# Node Editors 
# ----------------------------------------------

from func import util_func, static_data


def get_node_editor_type(area = None, use_id = False, return_enum=False, space_data = None):
    """Returns an enum of ENodeEditor for given area or a string

    Args:
        area (ref, optional): Reference to area from window_manager.windows.screen.area
        use_id (bool, optional): Whether to use (window_id, area_id) tuple instead of reference. Defaults to False.
        return_enum (bool, optional): Whether to return static_data.ENodeEditor instead of tree_type string. Defaults to False.
        use_space_data (ref, optional): Use context.space_data to get node editor type. WARNING: Won't check for area type, make sure to use in node editors.
    Returns:
        ENodeEditor or str: type of the node tree in node editor
    """

    if space_data is None:
        if use_id:
            area = bpy.context.window_manager.windows[area[0]].screen.areas[area[1]]

        space_data = area.spaces[0]
        if area.type != 'NODE_EDITOR':
            return None


    if return_enum:
        if space_data.tree_type in static_data.node_editors:
            return static_data.node_editors[space_data.tree_type].enum
        else:
            return None
    else:
        return space_data.tree_type


def get_node_editor_areas(ids=False):
    """Returns all areas that are node editors

    Args:
        ids (bool, optional): Return a tuple with index for windoww, and index for area in (x, y) format. Defaults to False.

    Returns:
        list of ref or list of tuple: References to areas, or 2 dimensional tuples to window id and area ids
    """
    areas = []
    for w, window in enumerate(bpy.context.window_manager.windows):
        for a, area in enumerate(window.screen.areas):
            if area.type == 'NODE_EDITOR':
                areas.append((w, a)) if ids else areas.append(area)

    return areas


def get_area_node_tree(area, useid = False):
    if useid:
        area = bpy.context.window_manager.windows[area[0]].screen.areas[area[1]]

    return area.spaces[0].node_tree


def get_supported_areas_for_attribute(attribute, ids = False):
    """Gets supported node editors for specified attribute to create attribute node in.

    Args:
        attribute (ref): Reference to the attribute
        ids (bool, optional): Return a tuple with index for windoww, and index for area in (x, y) format. Defaults to False.

    Returns:
        ref or tuple: Reference to area, or 2 dimensional tuple to window id and area id
    """

    areas = get_node_editor_areas(True) # returns tuple window id area id

    try:
        attribute_suppported_area_types = static_data.attribute_data_types[attribute.data_type].compatible_node_editors
    except KeyError:
        return []
    supported_areas = []
    for area in areas:
        arearef = bpy.context.window_manager.windows[area[0]].screen.areas[area[1]]

        node_editor_type = get_node_editor_type(arearef, return_enum=True)
        if node_editor_type in attribute_suppported_area_types:
            if node_editor_type == static_data.ENodeEditor.GEOMETRY_NODES and not util_func.get_blender_support(minver=(3,2,0)):
                continue
            else:
                supported_areas.append(area if ids else arearef)

    return supported_areas


def get_all_open_properties_panel_pinned_mesh_names():
    """Gets names of all Mesh datablock names in all open properties panels

    Returns:
        list: List of strings to mesh datablock names
    """

    meshes = []
    for w, window in enumerate(bpy.context.window_manager.windows):
        for a, area in enumerate(window.screen.areas):
            if area.type == 'PROPERTIES':
                for space in area.spaces:
                    # Honestly, IDK, somehow properties panel can become a 3D view out of nowhere
                    # so, hasattr has to stay
                    if hasattr(space, 'use_pin_id') and space.use_pin_id:
                        meshes.append(space.pin_id.name)

    return meshes


def get_node_tree_parent(node_tree, tree_type = None):
    """
    Gets the parent (likely material reference) of the node tree

    Args:
        node_tree (Reference): Reference to node tree
        tree_type (static_data.ENodeEdtior) (Optional): To limit the search to specific tree type it can be specified

    Returns:
        Reference to the parent, likely the material reference
    """
    if tree_type in [None, static_data.ENodeEditor.SHADER]:
        for mat in bpy.data.materials:
            if mat.node_tree == node_tree:
                return mat
    elif tree_type in [None, static_data.ENodeEditor.GEOMETRY_NODES]:
        for gn in bpy.data.node_groups:
            if gn.node_tree == node_tree:
                return gn
    else:
        return None


# Nodes
# ----------------------------------------------

def get_geometry_node_geometry_output_pins(node):
    """Gets Geometry output pins for input node

    Args:
        node (ref): node reference

    Returns:
        list: list of node.output elements
    """
    if node is None:
        return []

    outputs = []
    for output in node.outputs:
        if output.type == 'GEOMETRY':
            outputs.append(output)
    return outputs


def get_geometry_node_boolean_inputs(node):
    """Gets boolean input pins for input node

    Args:
        node (ref): node reference

    Returns:
        list: list of node.inputs elements
    """
    if node is None:
        return []

    inputs = []
    for output in node.inputs:
        if output.type == 'BOOLEAN':
            inputs.append(output)
    return inputs


def get_geometry_node_group_outputs(nodegroup):
    """Returns all node group output nodes in a nodegroup

    Args:
        nodegroup (ref): node group reference 

    Returns:
        list: node references
    """

    if nodegroup is None:
        return []

    nodes = []
    for node in nodegroup.nodes:
        if node.type == 'GROUP_OUTPUT':
            nodes.append(node)

    return nodes


def get_geometry_node_group_inputs(nodegroup):
    """Returns all node group input nodes in a nodegroup

    Args:
        nodegroup (ref): node group reference 

    Returns:
        list: node references
    """

    if nodegroup is None:
        return []

    nodes = []
    for node in nodegroup.nodes:
        if node.type == 'GROUP_INPUT':
            nodes.append(node)

    return nodes


def get_geometry_node_group_valid_output(nodegroup):
    """Checks if geometry type output is first on group output node AND input node (both required for modifier to apply)

    Args:
        nodegroup (ref): node group

    Returns:
        bool: True if valid
    """

    output_nodes = get_geometry_node_group_outputs(nodegroup)
    input_nodes = get_geometry_node_group_inputs(nodegroup)

    # No output nodes
    if not len(output_nodes): #or not len(input_nodes): # Not required.
        return False

    # TODO: Previous blender version support.

    # Blender 4.2
    interface_inputs = []
    interface_outputs = []
    for i in range(0, len(nodegroup.interface.items_tree)):
        item = nodegroup.interface.items_tree[i]
        if item.in_out == 'OUTPUT':
            interface_outputs.append(item)

        # String type suggests that it may be something else as well, better be safe and use if
        elif item.in_out == 'INPUT':
            interface_inputs.append(item)


    # Validity check
    if len(interface_outputs) and interface_outputs[0].socket_type == 'NodeSocketGeometry':
        return True

    return False


def get_geometry_nodegroup_use_types(nodegroup):
    """Returns geometry nodes nodegroup use types, eg. as a modifer and a tool 

    Args:
        nodegroup (ref): nodegroup to evaluate

    Returns:
        list: list of strings in ['MODIFIER', 'TOOL']
    """

    # Tool type was introduced in blender 4.0
    if util_func.get_blender_support(None, (4,0,0)):
        return True

    t = []

    if nodegroup.is_modifier:
        t.append('MODIFIER')
    if nodegroup.is_tool:
        t.append('TOOL')

    return t