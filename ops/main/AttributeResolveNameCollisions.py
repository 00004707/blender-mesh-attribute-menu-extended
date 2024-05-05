import func.util_func
from modules import LEGACY_etc, LEGACY_static_data


class AttributeResolveNameCollisions(bpy.types.Operator):
    """
    Adds suffix to attributes with colliding names
    """

    bl_idname = "mesh.attribute_resolve_name_collisions"
    bl_label = "Resolve name collisions"
    bl_description = "Renames attributes to avoid name collisions"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type == 'MESH':
            self.poll_message_set("Selected object is not a mesh")
            return False
        elif not len(context.active_object.data.attributes):
            self.poll_message_set("No attributes")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, True):
            return False

        return True


    def execute(self, context):
        # If it's pinned mesh, we need to get data and reference from somewhere else.
        b_pinned_mesh_in_use = func.util_func.is_pinned_mesh_used(context)
        if b_pinned_mesh_in_use:
            obj, obj_data = func.util_func.get_pinned_mesh_object_and_mesh_reference(context)
            LEGACY_etc.log(AttributeResolveNameCollisions, f"Using pinned mesh {obj_data.name} + {obj.name}", LEGACY_etc.ELogLevel.VERBOSE)
        else:
            obj_data = context.active_object.data
            obj = context.active_object

        current_mode = context.active_object.mode # use active object not pinned mesh

        # Operators below need to work on object level. If pinned switch to referenced object.
        if b_pinned_mesh_in_use:
            current_active_object = bpy.context.active_object
            current_selection_state_of_obj = obj.select_get()
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj


        bpy.ops.object.mode_set(mode='OBJECT')

        restricted_names = []

        # get vertex groups name, if any
        vg_names = [vg.name for vg in obj.vertex_groups]
        restricted_names += vg_names

        # get UVMap names, for blender 3.4 or lower
        if func.util_func.get_blender_support(minver_unsupported=(3,5,0)):
            uvm_names = [uv.name for uv in obj.data.uv_layers]
            restricted_names += uvm_names

        # rename those, get by index, by name is fucky wucky
        renamed = 0
        failed = 0
        enumerate(obj.data.attributes)
        for i, a in enumerate(obj.data.attributes):
            LEGACY_etc.log(AttributeResolveNameCollisions, f"{a} {i}", LEGACY_etc.ELogLevel.VERBOSE)

            if obj.data.attributes[i].name in restricted_names:
                atypes = func.attribute_func.get_attribute_types(obj.data.attributes[i])

                is_removeable = not bool(len([atype for atype in atypes if atype in [LEGACY_static_data.EAttributeType.HIDDEN, LEGACY_static_data.EAttributeType.CANTREMOVE, LEGACY_static_data.EAttributeType.READONLY]]))


                renamed +=1
                j = 0
                while obj.data.attributes[i].name in restricted_names:
                    if (not is_removeable):
                        failed += 1
                        break
                    j += 1
                    obj.data.attributes[i].name = str(obj.data.attributes[i].name) + "." + str(j).zfill(3)

        if failed > 0:
            self.report({'WARNING'}, f"Renamed {str(renamed)}, cannot rename {str(failed)}")
        elif renamed == 0:
            self.report({'INFO'}, f"No name collisions found")
        else:
            self.report({'INFO'}, f"Renamed {str(renamed)} attribute" + ("s" if renamed > 1 else ""))

        # Switch back to the previous object if pinned mesh was used
        if b_pinned_mesh_in_use:
            bpy.context.view_layer.objects.active = current_active_object
            obj.select_set(current_selection_state_of_obj)
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}