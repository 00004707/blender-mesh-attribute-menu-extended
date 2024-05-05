"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Operators to quickly edit UVMap data

"""

# Quick UV

class QuickUVMapToAttribute(bpy.types.Operator):
    # this is for pre blender 3.5
    bl_idname = "mesh.attribute_quick_from_uvmap"
    bl_label = "Convert UVMap to Vector 2D Attribute"
    bl_description = "Converts active UVMap to Vector 2D Attribute"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        obj = context.active_object

        if not obj:
            self.poll_message_set("No active object")
            return False
        elif obj.type != 'MESH':
            self.poll_message_set("Object is not a mesh")
            return False
        elif not len(obj.data.uv_layers):
            self.poll_message_set("No UVMaps")
            return False
        elif obj.data.uv_layers.active is None:
            self.poll_message_set("No active UVMap")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True

    def execute(self, context):
        obj = context.active_object

        args = {}
        args['attrib_name'] = ""
        args['domain_data_type_enum'] = "UVMAP"
        args['target_attrib_domain_enum'] = 'CORNER'
        args['b_batch_convert_enabled'] = False
        args['b_overwrite'] = True
        args['b_enable_name_formatting'] = True
        args['enum_uvmaps'] = str(obj.data.uv_layers.active_index)
        return bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT', **args)