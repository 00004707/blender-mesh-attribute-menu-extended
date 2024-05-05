import func.util_func
from modules import LEGACY_etc, LEGACY_static_data


class AttributesToImage(bpy.types.Operator):
    """
    Writes attributes to image texture
    """

    # BLENDER CLASS PROPERTIES
    # ---------------------------------

    bl_idname = "mesh.attribute_to_image"
    bl_label = "Bake to Data Texture"
    bl_description = "Exports attribute data to data texture"
    bl_options = {'REGISTER'}

    # COMMON
    # ---------------------------------

    b_pinned_mesh_support = False
    b_active_object_required = True
    supported_object_types = ['MESH']


    # IMAGE GENERAL
    # ---------------------------------

    # Toggle for selecting a new file or existing file
    image_source_enum: bpy.props.EnumProperty(
        name="Store in",
        description="Select an option",
        items=[
            ("NEW", "New image", "Stores data in new image"),
            ("EXISTING", "Existing image", "Stores data in existing image"),
        ],
        default="NEW"
    )


    # New image settings
    # ---------------------------------

    # New image width
    img_width: bpy.props.IntProperty(name="Width", default=1024, min=2, max=32768, step=2)

    # New image height
    img_height: bpy.props.IntProperty(name="Height", default=1024, min=2, max=32768, step=2)

    # forces image to use width x width values
    b_force_img_square: bpy.props.BoolProperty(name="Squared", default=True)

    # Name of the new image texture
    new_image_name: bpy.props.StringProperty(name="Name", default="Data Texture")

    # The color fill of the new image texture
    new_image_fill: bpy.props.FloatVectorProperty(name="Base Color", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0,0.0,0.0,1.0))

    # Whether to add alpha channel or not to the new texture
    b_new_image_alpha: bpy.props.BoolProperty(name="Alpha Channel", default=False)

    # New image dimensions presets
    image_dimensions_presets_enum: bpy.props.EnumProperty(
        name="Image Dimensions",
        description="Select an option",
        items=[
            ("CUSTOM", "Custom", "Specify a resolution"),
            ("8", "8x8", "8px x 8px"),
            ("16", "16x16", "16px x 16px"),
            ("32", "32x32", "32px x 32px"),
            ("64", "64x64", "64px x 64px"),
            ("128", "128x128", "128px x 128px"),
            ("256", "256x256", "256px x 256px"),
            ("512", "512x512", "512px x 512px"),
            ("1024", "1024x1024 (1K)", "1024px x 1024px"),
            ("2048", "2048x2048 (2K)", "2048px x 2048px"),
            ("4096", "4096x4096 (4K)", "4096px x 4096px"),
            ("8192", "8192x8192 (8K)", "8192px x 8192px"),
            ("16384", "16384x16384 (16K)", "16384px x 16384px"),
        ],
        default="2048"
    )


    # Existing image settings
    # ---------------------------------

    # Whether to create a copy of existing image and work on it instead.
    b_create_image_copy: bpy.props.BoolProperty(name="Create a copy", default=False)


    # Data menu
    # ---------------------------------

    # Data write mode selector
    image_write_mode_enum: bpy.props.EnumProperty(
        name="Data Write Mode",
        description="Select an option",
        items=[
            ("SEQUENTAL", "Sequental", "Simply writes data one by one pixel starting from (0,0)"),
            ("ATTRIBUTE", "Specify Position", "Use Vector2D attribute to write data at given position"),
            ("UV", "Use UVMap", "Use UV Map to write data like baking textures in blender"),
        ],
        default="UV"
    )


    # UVMap write mode settings
    # ---------------------------------

    # UVMap to sample to write the data
    uvmap_selector_enum: bpy.props.EnumProperty(
        name="UVMap",
        description="Select an option",
        items=func.enum_func.get_uvmaps_enum
    )

    # BAKING
    # ---------------------------------

    # The margin type to use
    image_bake_margin_type_enum: bpy.props.EnumProperty(
        name="Margin type",
        description="Select an option",
        items=[
            ("ADJACENT_FACES", "Adjacent Faces", "Use pixels from adjacent UV seams"),
            ("EXTEND", "Extend", "Extend border pixels outwards"),
        ],
        default="EXTEND"
    )

    # The margin in pixels to bake
    image_bake_margin: bpy.props.IntProperty(name="Margin size (px)", default=0, min=0)

    # Attribute coordinate write mode settings (UVMAP/ATTR)
    texture_coordinate_attribute_selector_enum: bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.enum_func.get_texture_coordinate_attributes_enum
    )

    # Channel selector
    image_channels_type_enum: bpy.props.EnumProperty(
        name="Image channels",
        description="Select an option",
        items=[
            ("GRAYSCALE", "All Channels", "Allows writing a single value to all channels"),
            ("ALL", "Separate Channels", "Allows writing three/four values (24/32-bit)"),
        ],
        default="GRAYSCALE"
    )

    # MISC UI
    # ---------------------------------

    # THE ATTRIBUTE/IMAGE selector enum for each image channel
    def get_image_channel_datasource_0_enum(self, context):
        return func.enum_func.get_image_channel_datasource_enum(self, context, 0)

    def get_image_channel_datasource_1_enum(self, context):
        return func.enum_func.get_image_channel_datasource_enum(self, context, 1)

    def get_image_channel_datasource_2_enum(self, context):
        return func.enum_func.get_image_channel_datasource_enum(self, context, 2)

    def get_image_channel_datasource_3_enum(self, context):
        return func.enum_func.get_image_channel_datasource_enum(self, context, 3)

    # THE XYZ XYZW X Y Z  or RGBA RGB R G B selectors for each image channel
    def get_image_channel_datasource_0_vector_element_enum(self, context):
        return func.enum_func.get_image_channel_datasource_vector_element_enum(self, context, 0, func.util_func.get_alpha_channel_enabled_texture_bake_op(self))

    def get_image_channel_datasource_1_vector_element_enum(self, context):
        return func.enum_func.get_image_channel_datasource_vector_element_enum(self, context, 1, func.util_func.get_alpha_channel_enabled_texture_bake_op(self))

    def get_image_channel_datasource_2_vector_element_enum(self, context):
        return func.enum_func.get_image_channel_datasource_vector_element_enum(self, context, 2, func.util_func.get_alpha_channel_enabled_texture_bake_op(self))

    def get_image_channel_datasource_3_vector_element_enum(self, context):
        return func.enum_func.get_image_channel_datasource_vector_element_enum(self, context, 3, func.util_func.get_alpha_channel_enabled_texture_bake_op(self))

    # The attribute to write in Red channel or all channels if GRAYSCALE was selected in image_channels_type_enum
    source_attribute_0_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_0_enum
    )

    # Toggle between attribute and image to select the input value in Red channel
    source_attribute_0_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.enum_func.get_image_channel_datasource_type_enum
    )

    # Selector for vector/image channel eg xyz rgb to bake to given image channel RED
    source_attribute_0_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_0_vector_element_enum
    )

    # The attribute to write in Green channel
    source_attribute_1_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_1_enum
        )

    # Toggle between attribute and image to select the input value in Green channel
    source_attribute_1_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.enum_func.get_image_channel_datasource_type_enum
    )

    source_attribute_1_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_1_vector_element_enum
    )

    # The attribute to write in Blue channel
    source_attribute_2_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_2_enum
    )

    # Toggle between attribute and image to select the input value in Blue channel
    source_attribute_2_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.enum_func.get_image_channel_datasource_type_enum
    )

    source_attribute_2_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_2_vector_element_enum
    )

    # The attribute to write in Alpha channel if supported
    source_attribute_3_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_3_enum
    )

    # Toggle between attribute and image to select the input value in Alpha channel
    source_attribute_3_datasource_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=func.enum_func.get_image_channel_datasource_type_enum
    )

    source_attribute_3_vector_element_enum:  bpy.props.EnumProperty(
        name="Attribute",
        description="Select an option",
        items=get_image_channel_datasource_3_vector_element_enum
    )

    # UTILITY
    # ---------------------------------

    def is_selected_enum_entry_a_vector_value(self, context, enum, source_attribute_datasource_enum):
        "Checks if given enum entry is a vector or image to show XYZW selectors"
        if source_attribute_datasource_enum == 'IMAGE':
            return True
        if enum == 'NULL':
            return False
        elif enum in context.active_object.data.attributes:
            return LEGACY_static_data.attribute_data_types[context.active_object.data.attributes[enum].data_type].gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.VECTOR, LEGACY_static_data.EDataTypeGuiPropType.COLOR]
        return False

    @classmethod
    def poll(self, context):
        if not func.util_func.get_blender_support(minver=(3,3,0)):
            self.poll_message_set("Blender version unsupported, please use 3.3 or later")
            return False
        elif self.b_active_object_required and not context.active_object:
            self.poll_message_set("No active object")
            return False
        elif not context.active_object.type in self.supported_object_types:
            self.poll_message_set("Selected object is not supported")
            return False
        elif not func.util_func.get_cycles_available():
            self.poll_message_set("Cycles render engine is disabled - required for this function to work")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, self.b_pinned_mesh_support):
            return False
        return True

    def invoke(self, context, event):

        # Refresh and populate UI selector lists to select attributes
        func.ui_func.refresh_attribute_UIList_elements(context)
        func.ui_func.configutre_attribute_uilist(False, False)
        return context.window_manager.invoke_props_dialog(self, width=400)

    def get_user_set_new_image_size(self):

        # Get the values from input fields if custom is set
        if self.image_dimensions_presets_enum == 'CUSTOM':

            # Return width if it is supposed to be squared
            if self.b_force_img_square:
                return (self.img_width, self.img_width)

            # Return fully custom resoltuion
            else:
                return (self.img_width, self.img_height)
        else:
            # Return whatever is set in enum, squared.
            return (int(self.image_dimensions_presets_enum), int(self.image_dimensions_presets_enum))

    def bake_to_texture(self, context, obj, image):
        # Object has to be selected, (happens to be active but not selected)
        if not obj.select_get():
            obj.select_set(True)

        # Check if cycles is available
        elif not func.util_func.get_cycles_available():
            self.report({'ERROR'}, "Cycles Render Engine is disabled. It is required to bake the texture.")
            return {'CANCELLED'}

        # Get requried references
        scene = bpy.context.scene
        uvmap  = obj.data.uv_layers[int(self.uvmap_selector_enum)].name

        if uvmap == 'NULL':
            self.report({'ERROR'}, "No UVMap selected.")
            return {'CANCELLED'}

        # Create a new material
        mat = bpy.data.materials.new('MAME_ATTRIBUTE_BAKER')
        LEGACY_etc.log(AttributesToImage, f"Created new material {mat.name}", LEGACY_etc.ELogLevel.VERBOSE)

        mat.use_nodes = True
        mat_nt = mat.node_tree
        mat_nt.nodes.remove(mat_nt.nodes['Principled BSDF'])

        # Set-up the Image Texture node to bake RGB values, 
        sn_texture = mat_nt.nodes.new('ShaderNodeTexImage')
        sn_texture.location = (-300, 120)
        sn_texture.image = image
        sn_texture.select = True
        sn_texture.interpolation = "Linear"
        sn_texture.extension = "REPEAT"
        sn_texture.projection = "FLAT"

        LEGACY_etc.log(AttributesToImage, f"Baking to {image.name}", LEGACY_etc.ELogLevel.VERBOSE)

        # Set up UVMap input 
        sn_texture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
        sn_texture_uv.location = (-540, -320)
        sn_texture_uv.attribute_name = uvmap
        sn_texture_uv.attribute_type = 'GEOMETRY'
        mat_nt.links.new(sn_texture_uv.outputs['Vector'], sn_texture.inputs['Vector'])

        # Set up separate of the image texture node to select channels
        sn_texture_separate = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
        sn_texture_separate.location = (-80, -320)
        mat_nt.links.new(sn_texture.outputs['Color'], sn_texture_separate.inputs['Vector'])

        # Set up material output node
        sn_out = mat_nt.nodes['Material Output']
        sn_out.location = (660, 140)

        # Set-up emission node
        sn_emit = mat_nt.nodes.new('ShaderNodeEmission')
        sn_emit.location = (340,120)
        mat_nt.links.new(sn_emit.outputs['Emission'], sn_out.inputs['Surface'])

        # Set up RGB mix node 
        sn_colormix = mat_nt.nodes.new('ShaderNodeCombineColor')
        sn_colormix.location = (-140, 120)
        mat_nt.links.new(sn_colormix.outputs['Color'], sn_emit.inputs['Color'])

        LEGACY_etc.log(AttributesToImage, f"Bake mode {self.image_channels_type_enum}", LEGACY_etc.ELogLevel.VERBOSE)
        LEGACY_etc.log(AttributesToImage, f"Alpha {func.util_func.get_alpha_channel_enabled_texture_bake_op(self)}", LEGACY_etc.ELogLevel.VERBOSE)


        #mat_nt.links.new(sn_alphacolormix.outputs['Color'], sn_emit.inputs['Color'])
        # before baking alpha mat_nt.links.new(sn_alphaemit.outputs['Emission'], sn_out.inputs['Surface'])

        # Set-up for RGB baking.
        # ----------------------------

        # Create attribute or texture nodes for input
        def create_attrib_to_combine_color_nodes(src_item_name,
                                                 tgt_tex_channel_id,
                                                 src_attrib_vector_id,
                                                 sn_colormix,
                                                 uvmap_ref,
                                                 input_type = 'ATTRIBUTE'):


            #vector_id = -1 # This means the attribute is not a vector nor image

            # Bypass
            if src_item_name == 'NULL':
                mat_nt.links.new(sn_texture_separate.outputs[tgt_tex_channel_id], sn_colormix.inputs[tgt_tex_channel_id])

            # Use attribute
            elif input_type == 'ATTRIBUTE':
                sn_attrib = mat_nt.nodes.new('ShaderNodeAttribute')
                sn_attrib.attribute_name = src_item_name
                sn_attrib.attribute_type = 'GEOMETRY'

                # scalar value
                if src_attrib_vector_id == -1:
                    mat_nt.links.new(sn_attrib.outputs['Fac'], sn_colormix.inputs[tgt_tex_channel_id])

                # vector value, use separate xyz
                else:
                    sn_attrib_split = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                    mat_nt.links.new(sn_attrib.outputs['Vector'], sn_attrib_split.inputs['Vector'])
                    mat_nt.links.new(sn_attrib_split.outputs[src_attrib_vector_id], sn_colormix.inputs[tgt_tex_channel_id])

            # Use texture
            else:
                # Set up the texture image node with uv and split xyz
                sn_inputtexture = mat_nt.nodes.new('ShaderNodeTexImage')
                sn_inputtexture.image = bpy.data.images[src_item_name]
                sn_inputtexture.select = False
                sn_inputtexture.interpolation = "Linear"
                sn_inputtexture.extension = "REPEAT"
                sn_inputtexture.projection = "FLAT"

                # Set up UVMap input node 
                sn_inputtexture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
                sn_inputtexture_uv.attribute_name = uvmap_ref
                sn_inputtexture_uv.attribute_type = 'GEOMETRY'
                mat_nt.links.new(sn_inputtexture_uv.outputs['Vector'], sn_inputtexture.inputs['Vector'])

                # Split RGB
                sn_inputtexture_separate = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                mat_nt.links.new(sn_inputtexture.outputs['Color'], sn_inputtexture_separate.inputs['Vector'])

                mat_nt.links.new(sn_inputtexture_separate.outputs[src_attrib_vector_id], sn_colormix.inputs[tgt_tex_channel_id])

        # Bake single attribute or color texture 
        if self.image_channels_type_enum == 'GRAYSCALE':
            source_attribute_name = getattr(self, f'source_attribute_0_enum')

            LEGACY_etc.log(AttributesToImage, f"Baking RGB from {source_attribute_name}", LEGACY_etc.ELogLevel.VERBOSE)

            # Case: Not a vector attribute nor an image
            if not len(self.get_image_channel_datasource_0_vector_element_enum(context)):
                # For each RGB channel
                for texture_ch in range(0, 3):
                    create_attrib_to_combine_color_nodes(source_attribute_name,
                                                         texture_ch,
                                                         -1, # force not a vector
                                                         sn_colormix,
                                                         uvmap,
                                                         'ATTRIBUTE') # force attribute
            else:

                userinput = self.source_attribute_0_vector_element_enum

                # User selected RGBA or RGB / XYZW or XYZ
                if userinput in ["6", '5']:
                    for texture_ch_and_vecid in range(0, 3):
                        create_attrib_to_combine_color_nodes(source_attribute_name,
                                                             texture_ch_and_vecid,
                                                             texture_ch_and_vecid,
                                                             sn_colormix,
                                                             uvmap,
                                                             getattr(self, f'source_attribute_0_datasource_enum'))

                # User selected XY (no RG preset)
                elif userinput == '4':
                    for texture_ch_and_vecid in range(0, 2):
                        create_attrib_to_combine_color_nodes(source_attribute_name,
                                                             texture_ch_and_vecid,
                                                             texture_ch_and_vecid,
                                                             sn_colormix,
                                                             uvmap,
                                                             'ATTRIBUTE') # no RG preset for images
                    # bypass B channel
                    create_attrib_to_combine_color_nodes('NULL',
                                                         2, # connect to B
                                                         2, # sample B
                                                         sn_colormix,
                                                         uvmap,
                                                         'ATTRIBUTE')

                # User selected R G B or A
                else:
                    for texture_ch in range(0, 3):
                        create_attrib_to_combine_color_nodes(source_attribute_name,
                                                             texture_ch,
                                                             int(userinput), # use selected source channel
                                                             sn_colormix,
                                                             uvmap,
                                                             getattr(self, f'source_attribute_0_datasource_enum'))

        # Separate channels to separate inputs
        else:
            for texture_ch in range(0, 3):
                source_attribute_name = getattr(self, f'source_attribute_{texture_ch}_enum')

                LEGACY_etc.log(AttributesToImage, f"Baking channel {texture_ch} from {source_attribute_name}", LEGACY_etc.ELogLevel.VERBOSE)

                if len(self.get_image_channel_datasource_0_vector_element_enum(context)):

                    attrib_vector_id = getattr(self, f'source_attribute_{texture_ch}_vector_element_enum')
                    if attrib_vector_id == '':
                        attrib_vector_id = -1
                else:
                    attrib_vector_id = -1
                create_attrib_to_combine_color_nodes(source_attribute_name,
                                                     texture_ch,
                                                     int(attrib_vector_id),
                                                     sn_colormix,
                                                     uvmap,
                                                     getattr(self, f'source_attribute_{texture_ch}_datasource_enum'))

        # Setup alpha channel if applicable

        if self.image_channels_type_enum == 'GRAYSCALE':
            bake_alpha = (func.util_func.get_alpha_channel_enabled_texture_bake_op(self) and                              # check if the image supports alpha
                                len(self.get_image_channel_datasource_0_vector_element_enum(context))    # if the source attribute is even a vector/image
                                and self.source_attribute_0_vector_element_enum == '6')                        # and if the RGBA/XYZW was selected

        else:
            bake_alpha = func.util_func.get_alpha_channel_enabled_texture_bake_op(self) and self.source_attribute_3_enum != 'NULL'

        if bake_alpha:
            # The only way to trigger this is either XYZW value or RGBA value input.
            if self.image_channels_type_enum == 'GRAYSCALE':
                if self.source_attribute_0_datasource_enum == 'IMAGE':
                    sn_alphatexture = mat_nt.nodes.new('ShaderNodeTexImage')
                    sn_alphatexture.location = (-360, 600)

                    sn_alphatexture.image = bpy.data.images[self.source_attribute_0_enum]
                    sn_alphatexture.interpolation = "Linear"
                    sn_alphatexture.extension = "REPEAT"
                    sn_alphatexture.projection = "FLAT"

                    # And it's UV input
                    sn_alphatexture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphatexture_uv.location = (-540, -600)
                    sn_alphatexture_uv.attribute_name = uvmap
                    sn_alphatexture_uv.attribute_type = 'GEOMETRY'
                    mat_nt.links.new(sn_alphatexture_uv.outputs['Vector'], sn_alphatexture.inputs['Vector'])

                    alpha_source_node = [sn_alphatexture, 'Alpha']

                else:
                    sn_alphaattrib = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphaattrib.attribute_name = self.source_attribute_0_enum
                    sn_alphaattrib.attribute_type = 'GEOMETRY'

                    alpha_source_node = [sn_alphaattrib, 'Alpha']

            else:
                # if baking separate attributes 
                if self.source_attribute_3_datasource_enum == 'IMAGE':
                    # Set-up the SOURCE Alpha Image Texture node to bake to
                    sn_alphatexture = mat_nt.nodes.new('ShaderNodeTexImage')
                    sn_alphatexture.location = (-360, 600)

                    sn_alphatexture.image = bpy.data.images[self.source_attribute_3_enum]
                    sn_alphatexture.interpolation = "Linear"
                    sn_alphatexture.extension = "REPEAT"
                    sn_alphatexture.projection = "FLAT"

                    # And it's UV input
                    sn_alphatexture_uv = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphatexture_uv.location = (-540, -600)
                    sn_alphatexture_uv.attribute_name = uvmap
                    sn_alphatexture_uv.attribute_type = 'GEOMETRY'
                    mat_nt.links.new(sn_alphatexture_uv.outputs['Vector'], sn_alphatexture.inputs['Vector'])

                    if self.source_attribute_3_vector_element_enum == 3:
                        alpha_source_node = [sn_alphatexture, 'Alpha']
                    else:
                        # Split RGB
                        sn_alphatexture_separate = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                        mat_nt.links.new(sn_alphatexture.outputs['Color'], sn_alphatexture_separate.inputs['Vector'])

                        alpha_source_node = [sn_alphatexture_separate, int(self.source_attribute_3_vector_element_enum)]

                else:
                    sn_alphaattrib = mat_nt.nodes.new('ShaderNodeAttribute')
                    sn_alphaattrib.attribute_name = self.source_attribute_3_enum
                    sn_alphaattrib.attribute_type = 'GEOMETRY'

                    # scalar
                    if not len(self.get_image_channel_datasource_3_vector_element_enum(context)):
                        alpha_source_node = [sn_alphaattrib, 'Fac']
                    # vector
                    else:

                        sn_alphaattrib_split = mat_nt.nodes.new('ShaderNodeSeparateXYZ')
                        mat_nt.links.new(sn_alphaattrib.outputs['Vector'], sn_alphaattrib_split.inputs['Vector'])
                        alpha_source_node = [sn_alphaattrib, int(self.source_attribute_3_vector_element_enum)]





        # Replace all material slots or create a material slot.
        remove_slot = False
        if not len(obj.material_slots):
            remove_slot = True
            bpy.ops.object.material_slot_add()

        current_mats = [slot.material for slot in obj.material_slots]
        for slot in obj.material_slots:
            slot.material = mat

        # Set the render settings
        sn_texture.select = True

        # All settings to be changed
        change_settings = [
            [scene.render, "engine"],
            [scene.cycles, "feature_set"],
            [scene.cycles, "device"],
            [scene.cycles, "adaptive_threshold"],
            [scene.cycles, "samples"],
            [scene.cycles, "adaptive_min_samples"],
            [scene.cycles, "time_limit"],
            [scene.cycles, "use_denoising"],
            [scene.cycles, "bake_type"],
            [scene.render.bake, "target"],
            [scene.render.bake, "use_selected_to_active"],
            [scene.render.bake, "use_clear"]]

        if hasattr(bpy.context.scene.render.bake, 'margin_type'):
            change_settings += [
                [scene.render.bake, "margin_type"]]

        if hasattr(bpy.context.scene.cycles, "use_guiding"):
            change_settings += [
                [scene.cycles, "use_guiding"]]

        if hasattr(bpy.context.scene.render.bake, "view_from"):
            change_settings += [
                [scene.render.bake, "view_from"]]

        change_settings += [
            [scene.render.bake, "margin"]
        ]

        # Settings for render
        mame_settings = [
            'CYCLES',
            'SUPPORTED',
            'CPU',
            0.01,
            1,
            0,
            0,
            False,
            'EMIT',
            'IMAGE_TEXTURES',
            False,
            False,
            ]

        if hasattr(bpy.context.scene.render.bake, 'margin_type'):
            mame_settings += [
                self.image_bake_margin_type_enum]

        if hasattr(bpy.context.scene.cycles, "use_guiding"):
            mame_settings += [False]

        if hasattr(bpy.context.scene.render.bake, "view_from"):
            mame_settings += ['ABOVE_SURFACE']

        mame_settings +=[
            self.image_bake_margin
        ]


        # Store current settings to revert to after baking
        current_settings = []
        for a in change_settings:
            current_settings.append(getattr(a[0], a[1]))

        # Change to settings optimized for baking attributes
        for i, a in enumerate(change_settings):
            setattr(a[0], a[1], mame_settings[i])

        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.active_object.data.update()

        # Bake RGB
        sn_texture.image = image
        sn_texture.select = True
        mat.node_tree.nodes.active = sn_texture
        bpy.ops.object.bake(type='EMIT')

        # Write alpha to RGB
        if bake_alpha:
            # Create a new image to store the alpha in
                new_img_size = self.get_user_set_new_image_size()
                alpha_image = bpy.data.images.new("Temporary baked alpha texture (safe to remove)", new_img_size[0], new_img_size[1], float_buffer=True, is_data=True)
                alpha_image.alpha_mode = 'NONE'
                alpha_image.generated_color = self.new_image_fill

                # Set the image node to new image
                sn_texture.image = alpha_image
                sn_texture.select = True
                mat.node_tree.nodes.active = sn_texture

                # Connect the node to emit shader input

                mat_nt.links.new(alpha_source_node[0].outputs[alpha_source_node[1]], sn_emit.inputs['Color'])

                # Bake again
                bpy.ops.object.bake(type='EMIT')

                # Copy red channel to alpha channel to first image
                pixelbuffer_RGB = np.zeros(len(image.pixels), dtype=np.float32)
                image.update()
                image.pixels.foreach_get(pixelbuffer_RGB)
                np.delete(pixelbuffer_RGB, [a for a in range(3,len(pixelbuffer_RGB), 4)]) # remove exising alpha

                alpha_image.update()
                pixelbuffer_A = np.zeros(len(alpha_image.pixels), dtype=np.float32)
                alpha_image.pixels.foreach_get(pixelbuffer_A)
                pixelbuffer_A = np.take(pixelbuffer_A, [a for a in range(0,len(pixelbuffer_A), 4)]) # get r channel

                np.put(pixelbuffer_RGB, [i for i in range(3, len(pixelbuffer_RGB), 4)], pixelbuffer_A) # insert new alpha

                image.pixels.foreach_set(pixelbuffer_RGB)
                image.update()
                # cleanup
                if not LEGACY_etc.preferences.get_preferences_attrib('bakematerial_donotdelete'):
                    bpy.data.images.remove(alpha_image)

        # Clean up
        for i, a in enumerate(change_settings):
            setattr(a[0], a[1], current_settings[i])

        if not remove_slot:
            for i, slot in enumerate(obj.material_slots):
                slot.material = current_mats[i]

        if not LEGACY_etc.preferences.get_preferences_attrib('bakematerial_donotdelete'):
            bpy.data.materials.remove(mat)

        if remove_slot:
            bpy.ops.object.material_slot_remove()

        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, f'Data written to \"{image.name}\" image texture')
        return {'FINISHED'}

    def execute(self, context):
        try:
            obj = context.active_object
            image = None

            # Store references to images
            LEGACY_etc.log(AttributesToImage, "Storing references to images", LEGACY_etc.ELogLevel.VERBOSE)
            enums = []
            for i in range(0, 4):
                enums.append(getattr(self, f'source_attribute_{i}_enum'))


            # Create a new image with specified dimensions and color fill
            if self.image_source_enum == 'NEW':
                LEGACY_etc.log(AttributesToImage, "Creating new image", LEGACY_etc.ELogLevel.VERBOSE)
                new_img_size = self.get_user_set_new_image_size()
                image = bpy.data.images.new(self.new_image_name, new_img_size[0], new_img_size[1], float_buffer=False, is_data=True)
                image.alpha_mode = 'CHANNEL_PACKED' if self.b_new_image_alpha else 'NONE'
                image.generated_color = self.new_image_fill

            # Get existing image
            else:
                image = context.window_manager.mame_image_ref
                if image is None:
                    self.report({'ERROR'}, 'No image selected')
                    return {'CANCELLED'}

                LEGACY_etc.log(AttributesToImage, f"Loading image {image.name if hasattr(image, 'name') else 'Unknown'}", LEGACY_etc.ELogLevel.VERBOSE)
                # Copy the image if selected
                if self.b_create_image_copy:
                    image = image.copy()
                    LEGACY_etc.log(AttributesToImage, f"Copy of {image.name if hasattr(image, 'name') else 'Unknown'} image created", LEGACY_etc.ELogLevel.VERBOSE)

            for i in range(0, 4):
                enums.append(setattr(self, f'source_attribute_{i}_enum', enums[i]))

            return self.bake_to_texture(context, obj, image)
        except Exception as exc:
            LEGACY_etc.call_catastrophic_crash_handler(AttributesToImage, exc)
            return {"CANCELLED"}


    def enum_watchdog(self, context):
        "Bugfix for blender handling of dynamic enums"
        for i in range(0, 4):
            try:
                if getattr(self, f'source_attribute_{i}_enum') == '':
                    setattr(self, f'source_attribute_{i}_enum', exec(f'self.get_image_channel_datasource_{i}_enum(context)[0][0]'))
            except TypeError:
                pass

        for i in range(0, 4):
            try:
                if getattr(self, f'source_attribute_{i}_datasource_enum') == '':
                    setattr(self, f'source_attribute_{i}_datasource_enum', func.enum_func.get_image_channel_datasource_type_enum(self, context)[0][0])
            except TypeError:
                pass

        for i in range(0, 4):
            try:
                if self.is_selected_enum_entry_a_vector_value(context, getattr(self, f'source_attribute_{i}_enum')):
                    ve = getattr(self, f'source_attribute_{i}_vector_element_enum')
                    if  ve == '' and len(exec(f'self.get_image_channel_datasource_{i}_vector_element_enum(context)')):
                        setattr(self, f'source_attribute_{i}_vector_element_enum', exec(f'self.get_image_channel_datasource_{i}_vector_element_enum(context)[0][0]'))
            except TypeError:
                pass

    def draw(self, context):
        obj = context.active_object
        active_attribute = func.attribute_func.get_active_attribute(obj)
        domain = active_attribute.domain
        dt = active_attribute.data_type

        # add enum checks
        self.enum_watchdog(context)

        layout = self.layout
        col = layout.column()

        rootcol = col.column()


        # Image File Settings
        rootcol.label(text='Image Texture File')
        box = rootcol.box()
        col = box.column()
        col.ui_units_y = 9
        sourceselect_row = col.row(align = True)
        sourceselect_row.prop_enum(self, 'image_source_enum', 'NEW')
        sourceselect_row.prop_enum(self, 'image_source_enum', 'EXISTING')

        # New image menu
        if self.image_source_enum == 'NEW':
            sr = col.row()
            sr.label(text="Texture Name")
            sr.prop(self, 'new_image_name', text="")
            sr = col.row()
            sr.label(text="Base Color Fill")
            sr.prop(self, 'new_image_fill', text="")

            sr = col.row()
            sr.label(text="Add Alpha Channel")
            sr.prop(self, 'b_new_image_alpha', text="Alpha Channel" if self.b_new_image_alpha else "No Alpha Channel", toggle=True)

            sr = col.row()
            sr.label(text='Dimensions')
            sr.prop(self, 'image_dimensions_presets_enum', text= '')

            if self.image_dimensions_presets_enum == 'CUSTOM':

                row = col.row()
                row.prop(self, "img_width", text="Width" if not self.b_force_img_square else "Width x Height")
                if not self.b_force_img_square:
                    row.prop(self, "img_height")

                col.prop(self, "b_force_img_square", toggle = True)

        # Existing image menu
        else:
            sr = col.row()
            sr.label(text="Texture Image")
            sr.template_ID(context.window_manager, 'mame_image_ref', open='image.open', text="")
            sr = col.row()
            sr.label(text="Copy image")
            sr.prop(self, 'b_create_image_copy', toggle = True)

            sr = col.row()
            sr.label(text="Alpha channel")
            img = context.window_manager.mame_image_ref
            if img is not None:
                alpha_en = img.alpha_mode != 'NONE'
            else:
                alpha_en = False
            sr.label(text="Supported" if alpha_en else 'Unsupported', icon="CHECKMARK" if alpha_en else "X")

            if context.window_manager.mame_image_ref is not None and not context.window_manager.mame_image_ref.is_float:
                sr = col.column()
                sr.label(icon="ERROR", text="This image stores bytes (0-255), not floats (0.0-1.0)")
                sr.label(icon="INFO", text="Some values might be rounded")



        # Data write mode menu
        # rootcol.label(text="Data write mode")
        rootcol.label(text="Settings")
        box = rootcol.box()
        subcol = box.column()
        # subcol.ui_units_y = 11
        subcol.ui_units_y = 6
        row = subcol.row()
        #row.prop_tabs_enum(self, 'image_write_mode_enum')

        # Sequental write menu
        if self.image_write_mode_enum == 'SEQUENTAL':
            subcol = subcol.column(align=False)
            infobox = subcol.box()
            infobox_col = infobox.column()
            infobox_col.label(icon="INFO", text="Write values from left lower corner, line by line")

            subcol.prop(self, 'pixel_index_offset')

            row = subcol.row(align=True)
            row.prop(self, 'x_pixel_offset')
            row.prop(self, 'y_pixel_offset')

            row = subcol.row(align=True)
            row.prop(self, 'x_max_height')
            row.prop(self, 'y_max_width')
            subcol.label(text="")

        # Specify position write menu
        elif self.image_write_mode_enum == 'ATTRIBUTE':
            subcol = subcol.column(align=True)
            infobox = subcol.box()
            infobox_col = infobox.column()
            infobox_col.label(icon="INFO", text="Write values at XY pixel coordinates from attribute")

            subcol.prop(self, 'texture_coordinate_attribute_selector_enum')


        # UVMap bake menu
        elif self.image_write_mode_enum == 'UV':
            subcol = subcol.column(align=False)

            if not func.util_func.get_cycles_available():
                subcol.label(text="")
                subcol.label(icon='ERROR', text="This mode requires Cycles Render Engine to be enabled")
            else:

                # infobox = subcol.box()
                # infobox_col = infobox.column()
                # infobox_col.label(icon="INFO", text="Bake interpolated values at UV coordinates")

                mr = subcol.row()
                mr.label(text="UVMap")
                mr.prop(self, 'uvmap_selector_enum', text = "")
                mr = subcol.row()
                mr.label(text="Margin Size (px)")
                mr.prop(self, 'image_bake_margin', text='')
                if hasattr(bpy.context.scene.render.bake, 'margin_type'):
                    mr = subcol.row()
                    mr.label(text="Margin Type")
                    mr.prop(self, 'image_bake_margin_type_enum', text = "")

                subcol.label(text="")
                subcol.label(icon='ERROR', text="Make sure modifiers and geometry nodes do not override materials")


        # Attribute and data selector menu
        rootcol.label(text="Data")
        box = rootcol.box()
        subcol = box.column()
        subcol.ui_units_y = 7
        row = subcol.row()
        row.prop_tabs_enum(self, 'image_channels_type_enum')

        channel_selector_text_x_units = 0.7
        channel_selector_datatype_x_units = 6
        vector_subelements_x_units = 3.5

        subcol = subcol.column(align=False)
        if self.image_channels_type_enum == 'GRAYSCALE':
            right_el_x_size = 16
            sr = subcol.row()
            sr_text = sr.row()
            sr_text.label(text="Source Type")
            ssr = sr_text.row()
            ssr.ui_units_x = right_el_x_size
            ssr.prop_tabs_enum(self, 'source_attribute_0_datasource_enum')

            sr_text = subcol.row()
            sr_text.label(text="Source")
            ssr = sr_text.row()
            ssr.ui_units_x = right_el_x_size
            ssr.prop(self, 'source_attribute_0_enum', text='')

            sr = subcol.row()
            if self.is_selected_enum_entry_a_vector_value(context, self.source_attribute_0_enum, self.source_attribute_0_datasource_enum) and len(self.get_image_channel_datasource_0_vector_element_enum(context)):
                sr.label(text="Source Channels")
                ssr = sr.row()
                ssr.ui_units_x = right_el_x_size
                ssr.prop_tabs_enum(self, 'source_attribute_0_vector_element_enum')

        else:
            sr = subcol.row()
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="R")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_0_datasource_enum')
            sr.prop(self, 'source_attribute_0_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_0_vector_element_enum')

            sr = subcol.row()
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="G")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_1_datasource_enum')
            sr.prop(self, 'source_attribute_1_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_1_vector_element_enum')


            sr = subcol.row()
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="B")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_2_datasource_enum')
            sr.prop(self, 'source_attribute_2_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_2_vector_element_enum')


            sr = subcol.row()

            sr.enabled = func.util_func.get_alpha_channel_enabled_texture_bake_op(self)
            sr_text = sr.row()
            sr_text.ui_units_x = channel_selector_text_x_units
            sr_text.label(text="A")
            sr_datatype = sr.row()
            sr_datatype.ui_units_x = channel_selector_datatype_x_units
            sr_datatype.prop_tabs_enum(self, 'source_attribute_3_datasource_enum')
            sr.prop(self, 'source_attribute_3_enum', text='')
            ssr = sr.row(align=True)
            ssr.ui_units_x = vector_subelements_x_units
            ssr.prop_tabs_enum(self, 'source_attribute_3_vector_element_enum')