"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit Color Attributes

"""

# Quick Color Attributes

class QuickBakeColorAttribute(bpy.types.Operator):
    bl_idname = "mesh.color_attribute_quick_bake"
    bl_label = "Bake to texture with active UVMap"
    bl_description = "Bakes active color attribute to a new image with selected UVMap"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # forces image to use width x width values
    b_force_img_square: bpy.props.BoolProperty(name="Squared", default=True)

    # Name of the texture
    tex_name: bpy.props.StringProperty(name="Image Name", default="Vertex Color")

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

    # The margin in pixels to bake
    image_bake_margin: bpy.props.IntProperty(name="Margin size (px)", default=8, min=0)

    new_texture_res_x: bpy.props.IntProperty(name="X", default=2048, min=0)
    new_texture_res_y: bpy.props.IntProperty(name="Y", default=2048, min=0)

    @classmethod
    def poll(self, context):
        obj = context.active_object

        if not obj:
            self.poll_message_set("No active object")
            return False
        elif obj.type != 'MESH':
            self.poll_message_set("Object is not a mesh")
            return False
        elif not len(obj.data.color_attributes):
            self.poll_message_set("No color attributes")
            return False
        elif obj.data.color_attributes.active_index is None:
            self.poll_message_set("No active color attribute")
            return False
        elif not len(obj.data.uv_layers):
            self.poll_message_set("No UVMaps")
            return False
        elif obj.data.uv_layers.active_index is None:
            self.poll_message_set("No active UVMap")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        args = {}
        args['image_source_enum'] = 'NEW'
        args['img_width'] = self.new_texture_res_x
        args['img_height'] = self.new_texture_res_y
        args['b_force_img_square'] = self.b_force_img_square
        args['new_image_name'] = self.tex_name
        args['new_image_fill'] = (0.0, 0.0, 0.0, 1.0)
        args['b_new_image_alpha'] = False
        args['image_dimensions_presets_enum'] = self.image_dimensions_presets_enum
        args['b_create_image_copy'] = False
        args['image_write_mode_enum'] = 'UV'
        args['uvmap_selector_enum'] = str(obj.data.uv_layers.active_index)
        args['image_bake_margin_type_enum'] = "EXTEND"
        args['image_bake_margin'] = self.image_bake_margin
        args['image_channels_type_enum'] =  'GRAYSCALE'
        args['source_attribute_0_datasource_enum'] = 'ATTRIBUTE'
        args['source_attribute_0_enum'] = obj.data.attributes.active_color.name
        args['source_attribute_0_vector_element_enum'] = '5' # rgb

        return bpy.ops.mesh.attribute_to_image('EXEC_DEFAULT', **args)

    def draw(self, layout):
        c = self.layout.column()

        r = c.row()
        r.prop(self, 'tex_name')
        r = c.row()
        r.prop(self, 'image_dimensions_presets_enum', text='Dimensions')
        if self.image_dimensions_presets_enum == 'CUSTOM':
            r = c.row(align=True)
            r.prop(self, 'new_texture_res_x', text= 'Width x Height' if self.b_force_img_square else 'Width')

            if not self.b_force_img_square:
                r.prop(self, 'new_texture_res_y', text = 'Height')

            r = c.row(align=True)
            r.prop(self, 'b_force_img_square', toggle=True)
        r = c.row()
        r.prop(self, 'image_bake_margin')


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)