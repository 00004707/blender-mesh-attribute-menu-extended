# Object data
# ----------------------------------------------

from func.util_func import get_object_type_from_object_data


def get_uvmaps(object_data):
    """Returns all UVMaps in object data

    Args:
        object_data (ref): object.data

    Returns:
        list: list of uvmaps
    """
    # case: object type invalid
    if (get_object_type_from_object_data(object_data) != 'MESH' or
        # or no data
        not len(object_data.uv_layers)):
        return []

    return object_data.uv_layers