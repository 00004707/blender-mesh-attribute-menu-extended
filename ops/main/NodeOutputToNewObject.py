import modules.ui.ui_common
from modules import LEGACY_etc, LEGACY_static_data
from modules.CreateBuiltInAttribute import CreateBuiltInAttribute


class NodeOutputToNewObject(bpy.types.Operator):
    """
    TODO
    """

    # BLENDER CLASS PROPERTIES
    # ---------------------------------

    bl_idname = "mesh.node_output_to_object"
    bl_label = "Node output to new object"
    bl_description = "Converts output of this node to new object"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # COMMON
    # ---------------------------------

    # Operator supports working with pinned mesh in properties panel
    b_pinned_mesh_support = True

    # Operator supports working in nodegroup context instead of datablock context
    b_nodegroup_context_support = True

    # Operator required active object to work
    b_active_object_required = True

    # Operator can edit these types of meshes
    supported_object_types = ['MESH', 'CURVES', 'POINTCLOUD']

    # Wiki URL suffix
    wiki_url = 'TODO' #TODO

    # OPTIONS
    # ---------------------------------

    node_geometry_output: bpy.props.EnumProperty(
        name="Geometry Output",
        description="Select an option",
        items=func.enum_func.get_geometry_nodegroup_node_geometry_outputs_enum
    )

    new_object_type: bpy.props.EnumProperty(
        name="New Object Type",
        description="Select an option",
        items=[('MESH', 'Mesh', "Create new object of mesh type", 'MESH_CUBE', 0),
               #('CURVE', 'Curve', "Create new object of curve type", 'CURVE_DATA', 1),
               ('CURVES', 'Hair Curves', "Create new object of hair curves type", 'CURVES_DATA', 2),
               ('POINTCLOUD', 'Point Cloud', "Create new object of point cloud type", 'OUTLINER_OB_POINTCLOUD', 3),
               #('PARTICLES', 'Particles', "Create new particle system with points as particles", 'PARTICLES', 4),
               ('HAIR_PARTICLES', 'Hair Particles', "Create new particle system with curves as hair particles", 'PARTICLEMODE', 5),]
    )

    particles_on_object: bpy.props.EnumProperty(
        name="New partice system on object",
        description="Select an option",
        items=func.enum_func.get_meshes_in_scene_enum
    )



    @classmethod
    def poll(self, context):
        obj, obj_data = func.obj_func.get_object_in_context(context, b_force_active_object=True)
        if self.b_active_object_required and not obj:
            self.poll_message_set("No active object")
            return False
        elif obj.mode != 'OBJECT':
            self.poll_message_set("Object mode required")
            return False
        elif func.node_func.get_node_editor_type(space_data=context.space_data) != 'GeometryNodeTree':
            self.poll_message_set("Not a geometry nodes graph")
            return False
        elif context.space_data.node_tree is None:
            self.poll_message_set("Valid nodegroup required")
            return False
        elif not func.node_func.get_geometry_node_group_valid_output(context.space_data.node_tree):
            self.poll_message_set("Nodegroup has no valid outputs")
            return False
        elif context.space_data.node_tree.nodes.active is None:
            self.poll_message_set("No active node in node group")
            return False
        elif obj.type not in self.supported_object_types:
            self.poll_message_set("Object type is not supported")
            return False
        return True

# Get nested node groups hierarchy (for group nodes)
# def get_nested_nodegroups_hierarchy(node_tree, hierarchy):
#     an = node_tree.nodes.active
#     if an.type == 'GROUP':
#         nt = an.node_tree
#         hierarchy.append({'node_tree': node_tree, 'active_node': an})
#         return get_nested_nodegroups_hierarchy(nt, hierarchy)
#     else:
#         hierarchy.append({'node_tree': node_tree, 'active_node': an})
#         return hierarchy

# h = []
# h = get_nested_nodegroups_hierarchy(ng, h)

# print("-----")
# for item in h:
#     print(f"{item['active_node'].name} [{item['active_node'].node_tree.name if item['active_node'].type =='GROUP' else '---' }] in {item['node_tree'].name}")



    def execute(self, context):
        try:
            # Debug
            b_no_cleanup = LEGACY_etc.preferences.get_preferences_attrib('convert_node_to_new_object_no_cleanup')

            ng = context.space_data.node_tree

            # Duplicate active object
            obj, obj_data = func.obj_func.get_object_in_context(context, b_force_active_object=True)

            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            original_object_name = obj.name

            bpy.ops.object.duplicate(linked=False)

            obj_clone = bpy.context.view_layer.objects.active
            obj_clone.name = obj_clone.name + f'.clone_SAFE_TO_REMOVE'

            # Find geometry nodes modifier with node group in context

            nodes_mod = None

            for mod_index in range(0, len(obj_clone.modifiers)):
                mod = obj_clone.modifiers[mod_index]

                # Remove all modifiers above it
                if nodes_mod is not None:
                    obj_clone.modifiers.remove(mod)

                elif mod.type == 'NODES' and mod.node_group == ng:
                    nodes_mod = mod


            # Duplicate node group
            top_level_ng_copy = ng.copy()
            nodes_mod.node_group = top_level_ng_copy

            if self.new_object_type in ['CURVES', 'POINTCLOUD', 'MESH']:
                LEGACY_etc.log(NodeOutputToNewObject, f'Converting to object supporting geonodes', LEGACY_etc.ELogLevel.VERBOSE)

                # Override nested group nodes as well, if active
                active_node_in_ng = top_level_ng_copy.nodes.active
                nested_ngs = []
                ng_in_viewer_copy = top_level_ng_copy

                # If it's a group, user is deeper in the hierarchy, connect top level ng to output.
                if active_node_in_ng.type == 'GROUP':
                    # Remove all other outputs in top level node group
                    nodes_to_remove = []

                    for node in top_level_ng_copy.nodes:
                        if node.type == 'GROUP_OUTPUT':
                            nodes_to_remove.append(node)

                    for node in nodes_to_remove:
                        top_level_ng_copy.nodes.remove(node)

                    # Create new output node
                    group_output_node = top_level_ng_copy.nodes.new('NodeGroupOutput')

                    # Connect the group node to group output
                    outputs = func.node_func.get_geometry_node_geometry_output_pins(active_node_in_ng)
                    top_level_ng_copy.links.new(group_output_node.inputs[0], outputs[0])

                # Connect each nested group to output
                while active_node_in_ng.type == 'GROUP':
                    # Get node group in group node, and create new
                    nested_ng = active_node_in_ng.node_tree.copy()
                    nested_ng.name = nested_ng.name + "_SAFE_TO_REMOVE"

                    # Store to clean up later
                    nested_ngs.append(nested_ng)

                    # Assign cloned nested group
                    active_node_in_ng.node_tree = nested_ng

                    # Remove all other group outputs
                    nodes_to_remove = []
                    for node in nested_ng.nodes:
                        if node.type == 'GROUP_OUTPUT':
                            nodes_to_remove.append(node)

                    for node in nodes_to_remove:
                        nested_ng.nodes.remove(node)

                    # Create new output
                    nested_group_output_node = nested_ng.nodes.new('NodeGroupOutput')
                    nested_group_output_node.label = 'MAME'

                    # Connect the active node to output
                    outputs = func.node_func.get_geometry_node_geometry_output_pins(nested_ng.nodes.active)
                    nested_ng.links.new(nested_group_output_node.inputs[0], outputs[0])

                    # Loop while applicable
                    active_node_in_ng = nested_ng.nodes.active
                    ng_in_viewer_copy = nested_ng


                # Set the output node on node in viewer
                nodes_to_remove = []

                for node in ng_in_viewer_copy.nodes:
                    if node.type == 'GROUP_OUTPUT':
                        nodes_to_remove.append(node)

                for node in nodes_to_remove:
                    ng_in_viewer_copy.nodes.remove(node)

                group_output_node = ng_in_viewer_copy.nodes.new('NodeGroupOutput')

                # Connect to group output, which green pin - selected by the user
                outputs = func.node_func.get_geometry_node_geometry_output_pins(active_node_in_ng)
                target_node_output_index = int(self.node_geometry_output[0])
                ng_in_viewer_copy.links.new(group_output_node.inputs[0], outputs[target_node_output_index])

                # Set the node group output as active to use it
                ng_in_viewer_copy.nodes.active = group_output_node

                failure_exception = False

                # if object type matches
                #if obj_clone.type in ['MESH', 'CURVES', 'POINTCLOUD'] and obj_clone.type == self.new_object_type:

                # # If object has shape keys, apply visible
                # if obj_clone.type == 'MESH':
                #     sk = func.get_shape_keys_enum(self, context)

                #     if sk[0][0] != 'NULL':
                #         bpy.ops.object.shape_key_remove(all=True, apply_mix=True)


                    # # Apply all modifiers (assuming active object is clone)
                    # try:
                    #     for i in range(0, len(obj_clone.modifiers)):
                    #         bpy.ops.object.modifier_apply(modifier=obj_clone.modifiers[i].name)
                    # except RuntimeError as exc:
                    #     failure_exception = exc

                    # # On apply failure, clean up
                    # if failure_exception and not b_no_cleanup:
                    #     obj_clone_data = obj_clone.data
                    #     obj_clone_type = obj_clone.type
                    #     bpy.data.objects.remove(obj_clone)

                    #     if obj_clone_type == 'MESH':
                    #         bpy.data.meshes.remove(obj_clone_data)
                    #         obj_clone = None

                # Convert to compatible output type via nodes
                #if not failure_exception and obj_clone.type != self.new_object_type:


                # Rename mesh object as it is going to be removed
                name_suffix = active_node_in_ng.label if active_node_in_ng.label != '' else active_node_in_ng.bl_label
                final_object_name = original_object_name + f'.{name_suffix}'

                obj_clone.name = 'SAFE_TO_REMOVE'

                # create new hair curves object
                if self.new_object_type == 'MESH':
                    converted_obj_data = bpy.data.meshes.new(name=final_object_name)
                elif self.new_object_type == 'CURVES':
                    converted_obj_data = bpy.data.hair_curves.new(name=final_object_name)
                elif self.new_object_type == 'POINTCLOUD':
                    converted_obj_data = bpy.data.pointclouds.new(name=final_object_name)

                converted_obj = bpy.data.objects.new(final_object_name, converted_obj_data)
                bpy.context.collection.objects.link(converted_obj)
                LEGACY_etc.log(NodeOutputToNewObject, f'Created new object: {converted_obj.name}', LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                # Create new modifier on it, with converter node
                conv_mod = converted_obj.modifiers.new('Converter', 'NODES')

                # Select the new object
                bpy.context.view_layer.objects.active = converted_obj
                converted_obj.select_set(True)

                # Convert using nodes
                def convert(method, conv_mod):
                    try_another_method = False
                    conv_mod.node_group = method
                    conv_mod['Socket_2'] = obj_clone

                    # Apply modifier
                    try:
                        bpy.ops.object.modifier_apply(modifier=conv_mod.name)
                    except RuntimeError as exc:
                        # failure_exception = exc
                        try_another_method = True

                    return try_another_method

                # I don't know how to determine the type of output, it can be anything. Brute force it is.
                try_another_method = True

                # MAME_POINTS_TO_xyz is using an instancer, should be used as last resort as it accepts anything with points afaik
                if self.new_object_type == 'POINTCLOUD':
                    methods = ['MAME_SIMPLE_CONVERT', 'MAME_MESH_TO_POINTS', 'MAME_CURVE_TO_POINTS']
                elif self.new_object_type == 'CURVES':
                    methods = ['MAME_SIMPLE_CONVERT', 'MAME_MESH_TO_CURVE', 'MAME_POINTS_TO_CURVE']
                elif self.new_object_type == 'MESH':
                    methods = ['MAME_SIMPLE_CONVERT', 'MAME_CURVE_TO_MESH', 'MAME_POINTS_TO_MESH'] #'MAME_SIMPLE_CONVERT',
                else:
                    raise LEGACY_etc.exceptions.GenericFunctionParameterError(NodeOutputToNewObject.__name__, f"Invalid object type {self.new_object_type}")

                # Load node groups
                method_ng = func.util_func.load_external_assets('geometry_nodes',
                            LEGACY_static_data.EExternalAssetType.NODEGROUP,
                            asset_names=methods)

                # BRUTE FORCE GOGOGOGO
                for i, method in enumerate(method_ng):
                    if try_another_method:
                        LEGACY_etc.log(NodeOutputToNewObject, f'Trying method: {method.name}', LEGACY_etc.ELogLevel.SUPER_VERBOSE)

                        try_another_method = convert(method, conv_mod)

                        # Converting to mesh does not fail though, but mesh can be empty so, 
                        if converted_obj.type == 'MESH' and not len(converted_obj.data.vertices):
                            try_another_method = True

                            # and add modifier again
                            conv_mod = converted_obj.modifiers.new('Converter', 'NODES')

                    else:
                        break

                # Cleanup: remove imported node groups
                if not b_no_cleanup:
                    for m in method_ng:
                        bpy.data.node_groups.remove(m)

                # Cleanup: Remove mesh object
                if not b_no_cleanup:
                    mesh_data = obj_clone.data
                    obj_clone_type = obj_clone.type
                    bpy.data.objects.remove(obj_clone)
                    if obj_clone_type == 'MESH':
                        bpy.data.meshes.remove(mesh_data)
                    elif obj_clone_type == 'CURVES':
                        bpy.data.hair_curves.remove(mesh_data)
                    elif obj_clone_type == 'POINTCLOUD':
                        bpy.data.pointclouds.remove(mesh_data)

                # Be friendly
                if try_another_method:
                    failure_exception = 'Failed to convert'

                # Cleanup on failure
                if failure_exception and not b_no_cleanup:
                    bpy.data.objects.remove(converted_obj)

                    if self.new_object_type == 'MESH':
                        bpy.data.meshes.remove(converted_obj_data)
                    elif self.new_object_type == 'CURVES':
                        bpy.data.hair_curves.remove(converted_obj_data)
                    elif self.new_object_type == 'POINTCLOUD':
                        bpy.data.pointclouds.remove(converted_obj_data)

                    obj_clone = None
                else:
                    # Set new name for whatever is below
                    obj_clone = converted_obj

                # Clean up
                if not b_no_cleanup:
                    for nng in nested_ngs:
                        bpy.data.node_groups.remove(nng)

            # Clean up
            if not b_no_cleanup:
                bpy.data.node_groups.remove(top_level_ng_copy)

            # Set active object back to previous one
            if obj_clone is not None:
                obj_clone.select_set(False)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            # Inform user about failure, if any
            if failure_exception:
                self.report({'ERROR'}, f"Creating object failed: {str(failure_exception)}")
                return {'CANCELLED'}
            return {'FINISHED'}
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(CreateBuiltInAttribute, exc)
            return {"CANCELLED"}


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):

        ng = context.space_data.node_tree
        layout = self.layout

        if len(func.node_func.get_geometry_node_geometry_output_pins(ng.nodes.active)) > 1:
            layout.label(text="Geometry output pin")
            layout.prop(self, 'node_geometry_output', text='')

        layout.label(text="New object type")
        layout.prop(self, 'new_object_type', text='')

        if self.new_object_type in ['PARTICLES', 'HAIR_PARTICLES']:
            layout.label(text="Create particles on")
            layout.prop(self, 'particles_on_object', text='')

        # Wiki
        modules.ui.ui_common.append_wiki_operator(self, context)