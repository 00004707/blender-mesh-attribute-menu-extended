"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Debug

"""

import bpy
from . import ops
from . import func
from . import static_data
from . import etc

# Operators
# ----------------------------

class MAMETestAll(bpy.types.Operator):
    """
    Tests operator (hidden)
    """
    bl_idname = "mame.tester"
    bl_label = "mame test"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # bpy.ops.mesh.primitive_monkey_add()
        # obj = context.active_object
        excs = []
        for source_data in [el[0] for el in func.get_source_data_enum_without_separators(self, context)]:
            for target_domain in ['POINT','EDGE','FACE','CORNER']:
                # for convert_domain in func.get_attribute_domains_enum(self, context):
                #     for convert_dt in func.get_attribute_data_types_enum(self, context):
                    
                    
                        bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT',
                                                                attrib_name='',
                                                                domain_data_type=source_data)
                                                                #target_attrib_domain=target_domain)#,
                    
        if excs:
            raise Exception(excs)   
        
                                # batch_convert_enabled= True,
                                # auto_convert = True,
                                # enum_attrib_converter_mode='GENERIC')
                                # enum_attrib_converter_domain=convert_domain,
                                # enum_attrib_converter_datatype=convert_dt)
    
    # enum_face_maps=''
    # enum_material_slots: bpy.props.EnumProperty(
    # enum_materials: bpy.props.EnumProperty(
    # enum_vertex_groups: bpy.props.EnumProperty(
    # enum_shape_keys: bpy.props.EnumProperty(
    # enum_shape_keys_offset_source: bpy.props.EnumProperty(

 
                            

        return {'FINISHED'}
        for domain in func.get_supported_domains_for_selected_mesh_data_target_enum_entry(self, context):
            for data_target in func.get_target_data_enum(self, context):
                bpy.ops.mesh.attribute_convert_to_mesh_data('EXEC_DEFAULT',
                                                            append_to_current=False,
                                                            apply_to_first_shape_key=True,
                                                            delete_if_converted=False,
                                                            data_target=data_target,
                                                            attrib_name="",
                                                            convert_to_domain=domain,
                                                            enable_auto_smooth=True)
                                                

        return {'FINISHED'}


    @classmethod
    def poll(self, context):
        return True

class MAMECreateAllAttributes(bpy.types.Operator):
    """
    Operator to create and test all attributes.
    """
    bl_idname = "mame.create_all_attribs"
    bl_label = "attrib test"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        dts = []
        for dt in static_data.attribute_data_types:
             if etc.get_blender_support(static_data.attribute_data_types[dt].min_blender_ver, static_data.attribute_data_types[dt].unsupported_from_blender_ver):
                  print(dt)
                  dts.append(dt)
             
        for domain in ['POINT', 'EDGE','FACE','CORNER']:
            for data_type in dts:
                bpy.context.active_object.data.attributes.new(f"{domain} {data_type}", data_type, domain)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True
    
# Utility
# ----------------------------

