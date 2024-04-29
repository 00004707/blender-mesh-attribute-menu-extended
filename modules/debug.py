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
    
        def test_from_mesh_data(self, context):
            obj = context.active_object
            req_attrs = ['domains_supported', 
                        'batch_convert_support']
            
            excs = []
            for source_data in static_data.object_data_sources:
                
                # ignore separators
                if 'SEPARATOR' in source_data or 'NEWLINE' in source_data:
                    continue

                # something went very wrong then
                if source_data is None:
                    print(F"[TESTS] NONETYPE: {source_data}")
                    raise Exception()
                
                # check attrs 
                for attr in req_attrs:
                    if not hasattr(static_data.object_data_sources[source_data], attr):
                        print(F"[TESTS] NO REQ ATTR: {source_data} - {attr}")
                        raise Exception()
                    
                # check support for current blender version
                if not etc.get_blender_support(static_data.object_data_sources[source_data].min_blender_ver, static_data.object_data_sources[source_data].unsupported_from_blender_ver):
                    print(f"[TESTS] Handled non-compatible version xception: {source_data}")
                    continue
                
                # test all cases
                for domain in static_data.object_data_sources[source_data].domains_supported:
                    for batch_mode_en in [True, False] if static_data.object_data_sources[source_data].batch_convert_support else [False]:
                        for overwrite in [True, False]:
                            for name_format_en in [True, False]:
                                for auto_convert in [True, False]:
                                    print(f"[TESTS] Creating new attribute from {source_data}, on domain {domain}, batch: {batch_mode_en}, name format enable: {name_format_en}, auto_convert: {auto_convert}")
                                    try:
                                        bpy.ops.mesh.attribute_create_from_data('EXEC_DEFAULT',
                                                                    attrib_name='',
                                                                    domain_data_type_enum=source_data,
                                                                    target_attrib_domain_enum=domain,
                                                                    b_batch_convert_enabled=batch_mode_en,
                                                                    b_overwrite=overwrite,
                                                                    b_enable_name_formatting=name_format_en,
                                                                    b_auto_convert=auto_convert)
                                    except RuntimeError as exc:
                                        print(f"[TESTS] Handled exception: {exc}")
                                    else:
                                        print("[TESTS] SUCCESS")
        
        obj = context.active_object

        print("[TESTS] FULL TEST START")
        print("[TESTS] --------------------------------------------------")
        print(f"[TESTS] Testing create from mesh data on object {obj}, type: empty object data test")
        test_from_mesh_data(self, context)  

        print("[TESTS] --------------------------------------------------")
        print(f"[TESTS] Testing create from mesh data on object {obj}, type: filled object data test")

        bpy.ops.object.material_slot_add()
        bpy.ops.material.new()
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.shape_key_add(from_mix=False)
        bpy.ops.object.shape_key_add(from_mix=False)
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.object.face_map_add()
        bpy.ops.object.face_map_add()
        bpy.ops.geometry.color_attribute_add(name="Color", domain='POINT', data_type='FLOAT_COLOR', color=(0, 0, 0, 1))
        bpy.ops.geometry.color_attribute_add(name="Color", domain='CORNER', data_type='BYTE_COLOR', color=(0, 0, 0, 1))
        bpy.ops.mesh.customdata_custom_splitnormals_add()
        bpy.ops.mesh.customdata_bevel_weight_edge_add()
        bpy.ops.mesh.customdata_bevel_weight_vertex_add()
        bpy.ops.mesh.customdata_crease_edge_add()
        bpy.ops.mesh.customdata_crease_vertex_add()
        test_from_mesh_data(self, context)

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
             
        for domain in static_data.attribute_domains:
            for data_type in dts:
                try:
                    bpy.context.active_object.data.attributes.new(f"{domain} {data_type}", data_type, domain)
                except Exception:
                    continue
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True

class MAMECreatePointCloudObject(bpy.types.Operator):
    """
    Creates point cloud object
    """
    bl_idname = "mame.create_point_cloud"
    bl_label = "Create pointcloud"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        pcdata = bpy.data.pointclouds.new("ptcloud")
        obj = bpy.data.objects.new('PointCloud', pcdata)
        bpy.context.scene.collection.objects.link(obj)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True

class MAMENukePinnedObjectReferenceList(bpy.types.Operator):
    """
    Clears pinned mesh object reference list
    """
    bl_idname = "mame.debug_nuke_pinned_object_reference_list"
    bl_label = "Nuke Pinned Refs"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        gui_prop_group.last_object_refs.clear()
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True

# Utility
# ----------------------------

classes = [MAMECreateAllAttributes,
           MAMECreatePointCloudObject,
           MAMETestAll]
           MAMENukePinnedObjectReferenceList]

def force_register():
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except Exception:
            etc.log(force_register, f"Cannot register debug operator", etc.ELogLevel.ERROR)
            continue


def register():
    if etc.get_preferences_attrib('register_debug_ops_on_start'):
        force_register()


def unregister():
    for c in classes:
        try:
            bpy.utils.unregister_class(c)
        except Exception:
            continue