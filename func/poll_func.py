# Multi-use operator poll functions
# --------------------------------

from func.attribute_func import get_attribute_types
from modules import LEGACY_static_data
from func.util_func import get_attribute_compatibility_check


def pinned_mesh_poll(self, context, supported=True):
    """Used to check for vailidity of pinned mesh data, or block operator from using on pinned mesh

    Args:
        self (Ref): self from poll()
        context (Reference): Blender context reference

    Returns:
        boolean
    """
    if hasattr(context, "space_data") and hasattr(context.space_data, "use_pin_id"):
        if context.space_data.use_pin_id:
            if not supported:
                self.poll_message_set("Unsuppported in pinned mesh mode")
                return False
            self.poll_message_set("Please toggle pin, data needs to be refreshed")
            return bool(get_pinned_mesh_ref_from_context(context))
    return True


def conditional_selection_poll(self, context, pinned_mesh_support = False):
    """Used in multiple ops that are used for selecting attributes by condition on their values

    Args:
        context (Reference): Blender context reference

    Returns:
        boolean
    """
    if not context.active_object:
        self.poll_message_set("No active object")
        return False

    elif not context.active_object.mode == 'EDIT':
        self.poll_message_set("Object not in edit mode")
        return False

    elif not context.active_object.type == 'MESH':
        self.poll_message_set("Object is not a mesh")
        return False

    elif context.active_object.data.attributes.active is None:
        self.poll_message_set("No active attribute")
        return False

    elif not LEGACY_static_data.EAttributeType.NOTPROCEDURAL not in get_attribute_types(context.active_object.data.attributes.active):
        self.poll_message_set("Attribute cannot be selected (Non-procedural)")
        return False

    elif not get_attribute_compatibility_check(context.active_object.data.attributes.active):
        self.poll_message_set("Attribute is unsupported in this addon version")
        return False
    elif not pinned_mesh_poll(self, context, pinned_mesh_support):
        return False

    return True


def get_pinned_mesh_ref_from_context(context):
    for ref in context.window_manager.MAME_GUIPropValues.last_object_refs:
            if ref.datablock_ref_name == context.space_data.pin_id.name and ref.workspace_name == context.window.workspace.name:
                return ref
    return None