"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Quick Attribute Node Extension

"""


import func.node_func
from modules import LEGACY_static_data


class QuickAttributeNode(bpy.types.Operator):
    bl_idname = "mesh.attribute_create_attribute_node"
    bl_label = "Create Attribute Node"
    bl_description = "Creates Attribute node in selected nodes editor"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # The area to create the node
    areaid: bpy.props.IntProperty(name="AreaID")
    windowid: bpy.props.IntProperty(name="windowid")
    area = None

    @classmethod
    def poll(self, context):
        obj =  bpy.context.active_object
        if not obj:
            self.poll_message_set("No active object")
            return False
        elif obj.type != 'MESH':
            self.poll_message_set("Object is not a mesh")
            return False
        elif obj.data.attributes.active is None:
            self.poll_message_set("No active attribute")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        attribute = obj.data.attributes.active
        self.area = bpy.context.window_manager.windows[self.windowid].screen.areas[self.areaid]
        node_tree_type = func.node_func.get_node_editor_type(self.area, return_enum=True)
        region = self.area.regions[3]
        node_tree = self.area.spaces[0].node_tree

        node_spawn_location = region.view2d.region_to_view(region.width / 2,  region.height / 2)
        # Widen the node if the name is long

        extra_width = max(0,(len(attribute.name) - 10) * 9)


        if node_tree_type == LEGACY_static_data.ENodeEditor.GEOMETRY_NODES:
            node = node_tree.nodes.new("GeometryNodeInputNamedAttribute")
            node.inputs[0].default_value = attribute.name
            node.data_type = LEGACY_static_data.attribute_data_types[attribute.data_type].geonodes_attribute_node_datatype
            node.width = node.width + extra_width
        elif node_tree_type == LEGACY_static_data.ENodeEditor.SHADER:
            node = node_tree.nodes.new("ShaderNodeAttribute")
            node.attribute_type = 'GEOMETRY'
            node.attribute_name = attribute.name
            node.width = node.width + extra_width
        # elif node_tree_type == static_data.ENodeEditor.ANIMATION_NODES:
        #     node = node_tree.nodes.new("an_GetCustomAttributeNode")
        #     node.inputs[1].value = attribute.name
        #     node.dataType = static_data.attribute_data_types[attribute.data_type].animnodes_attribute_node_datatype

        else:
            self.report({'ERROR'}, "Unsupported node group")
            return {'CANCELLED'}

        node.select = False
        node.location = node_spawn_location

        return {'FINISHED'}