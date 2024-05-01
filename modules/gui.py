
"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
gui

Everything related to user interface.

"""
 
import bpy 
from . import func
from . import static_data
from . import etc
from . import debug

# Properties Panel
# -----------------------------------------

def attribute_assign_panel(self, context):
    """
    Buttons underneath the attributes list in Attributes Menu located in Properties Panel
    """

    layout = self.layout

    # Supported object types for assingment panel
    supported_object_types = ['MESH', 'CURVES', 'POINTCLOUD']

    # Show options available if pin is enabled
    mesh_data_pinned = context.space_data.use_pin_id

    # Get object data of object in context
    if context.object:
       ob_data = context.object.data
       ob_type = context.object.type

    elif mesh_data_pinned: 
        # if hasattr(context.curves, 'points'):
        ob_type = context.space_data.pin_id.id_type
        if  ob_type == 'CURVES':
            ob_data = context.curves
            
        elif ob_type  == 'MESH':
            ob_data = context.mesh
            
        elif ob_type == 'POINTCLOUD':
            ob_data = context.pointcloud
            
    else:
        etc.log(attribute_assign_panel, "Unexpected use case, please report an issue!", etc.ELogLevel.ERROR)
        return
    
    # Source to check if object can slow down blender
    if ob_type == 'CURVES':
        obj_size_source = ob_data.points

    elif ob_type  == 'MESH':
        obj_size_source = ob_data.vertices

    elif ob_type == 'POINTCLOUD':
        obj_size_source = ob_data.points
        
    active_obj_in_viewport = bpy.context.active_object
    prop_group = ob_data.MAME_PropValues
    gui_prop_group = context.window_manager.MAME_GUIPropValues
    
    # Store reference to last active object before pin
    pin_ref, ob_data = func.update_last_object_reference_for_pinned_datablock(context, ob_data)
    
    # Show custom attribute context menu if needed
    if ob_type in ['CURVES', 'POINTCLOUD']:
        row = layout.row()
        row.menu("OBJECT_MT_mame_custom_attribute_context_menu")

    row = layout.row()

    if ((context.object and context.object.type in supported_object_types) 
        or (mesh_data_pinned and ob_data)):

        # Edit mode menu
        if ( active_obj_in_viewport and active_obj_in_viewport.mode == 'EDIT'):
            if ((etc.get_preferences_attrib('attribute_assign_menu') and ob_type == 'MESH')
                or (etc.get_preferences_attrib('attribute_assign_menu_curves') and ob_type == 'CURVES')
                or (etc.get_preferences_attrib('attribute_assign_menu_pointcloud') and ob_type == 'POINTCLOUD')):
                
                # Any attribute needs to be active
                if not ob_data.attributes.active:
                    box = row.box()
                    box.label(text="No active attribute", icon='ERROR')

                # Do not edit hidden attributes
                elif not func.get_is_attribute_valid_for_manual_val_assignment(ob_data.attributes.active):
                    box = row.box()
                    box.label(text="Editing of non-editable and hidden attributes is disabled.")
                
                else:
                    dt = ob_data.attributes.active.data_type

                    # Check for supported types
                    if not func.get_attribute_compatibility_check(ob_data.attributes.active):
                        sublayout = layout.column()
                        sublayout.alert = True
                        sublayout.label(text="This attribute type is not supported by MAME addon.", icon='ERROR')
                        sublayout.operator('window_manager.mame_report_issue')
                    else:
                        # Create new UI Container
                        assign_buttons = layout.column()
                        
                        # 1ST Row
                        col = assign_buttons.row()
                        
                        # Value Field
                        col2 = col.row(align=True)
                        if dt == 'BOOLEAN':
                            title_str = "True" if prop_group.val_boolean else "False"
                        else:
                            title_str = ""

                        if static_data.attribute_data_types[dt].large_capacity_vector:
                            matrixcol = col2.column(align=True)
                            matrix_w = static_data.attribute_data_types[dt].large_capacity_vector_size_width
                            matrix_h = static_data.attribute_data_types[dt].large_capacity_vector_size_height
                            for i in range(0, matrix_w):
                                matrix_vals_col = matrixcol.column(align=True)
                                matrix_vals_row = matrix_vals_col.row(align=True)
                                for j in range(0, matrix_h):
                                    matrix_vals_row.prop(prop_group, f"val_{dt.lower()}", text=title_str, toggle=True, index=i*matrix_w+j)
                        else:
                            col2.prop(prop_group, f"val_{dt.lower()}", text=title_str, toggle=True)
                        
                        # Randomize Button
                        if dt == 'STRING':
                            col2.prop(prop_group, f"val_select_casesensitive", text="", toggle=True, icon='SYNTAX_OFF')
                        col2.operator('mesh.attribute_gui_value_randomize', text="", icon='FILE_REFRESH')
                        col2.ui_units_x = 40

                        # Face Corner Spill Feature
                        col2 = col.row(align=True)
                        if ob_data.attributes.active.domain == "CORNER":
                            col2.prop(prop_group, "face_corner_spill", text=f"Spill", toggle=True)
                        else:
                            col2.operator("mesh.always_disabled_face_corner_spill_operator", text=f"Spill")
                        sub = col2.row(align=True)
                        sub.enabled = not (len(obj_size_source) > etc.LARGE_MESH_VERTICES_COUNT 
                                           and not prop_group.face_corner_spill 
                                           and ob_data.attributes.active.domain == "CORNER") or prop_group.val_enable_slow_ops
                        # Read Button
                        sub.operator("mesh.attribute_read_value_from_selected_domains", text="Read")
                        
                        # Open Docs Button
                        if etc.get_preferences_attrib("show_docs_button"):
                            sub.separator()
                            sub = col2.row(align=False)
                            op = sub.operator('window_manager.mame_open_wiki', icon='QUESTION', text="")
                            op.wiki_url = 'Main-User-Interface'

                        # 2ND Row
                        col = assign_buttons.row()

                        # Assignment buttons
                        sub = col.row(align=True)
                        btn_assign = sub.operator('object.set_active_attribute_to_selected', text=f"Assign")
                        btn_assign.b_clear = False
                        btn_assign.b_face_corner_spill_enable = prop_group.face_corner_spill
                        btn_clear = sub.operator('object.set_active_attribute_to_selected', text=f"Clear")
                        btn_clear.b_clear = True
                        btn_clear.b_face_corner_spill_enable = prop_group.face_corner_spill

                        #Selection buttons
                        sub = col.row(align=True)
                        sub.enabled = len(obj_size_source) < etc.LARGE_MESH_VERTICES_COUNT or prop_group.val_enable_slow_ops
                        sub.operator_context = 'EXEC_DEFAULT'
                        sub.operator("mesh.attribute_select_button", text=f"Select")
                        sub.operator("mesh.attribute_deselect_button", text=f"Deselect")
                        
                        
                        sub = sub.row(align=True)
                        sub.ui_units_x = 1
                        sub.prop(prop_group, "val_select_non_zero_toggle", text=f"NZ" if prop_group.val_select_non_zero_toggle else 'V', toggle=True)

                        # Slow operation warning with a toggle
                        if len(obj_size_source) > etc.LARGE_MESH_VERTICES_COUNT:
                            box = layout.box()
                            col2 = box.column(align=True)
                            r= col2.row()
                            r.label(icon='ERROR', text="Warning")
                            r.alert=True
                            col2.label(text="Large amount of vertices/points - blender may freeze!")
                            r2 = col2.row()
                            r2.label(text='Allow slow operators')
                            r2.prop(prop_group, 'val_enable_slow_ops', toggle=True, text="Enable")

                        # Reminder about a not selected pinned mesh
                        try:
                            if mesh_data_pinned and pin_ref is not None and not bpy.data.objects[pin_ref.obj_ref_name].select_get():
                                box = layout.box()
                                col2 = box.column(align=True)
                                r= col2.row()
                                r.label(icon='INFO', text="The pinned object is not selected")
                                r2 = col2.row()
                                r2.label(text="You can edit but won't see selected elements")
                        except Exception:
                            pass
        
        # Reminder about mesh datablock not in scene
        if mesh_data_pinned and pin_ref is not None and pin_ref.obj_ref_name not in bpy.context.scene.objects:
            try:
                box = layout.box()
                box.alert = True
                col2 = box.column(align=True)
                r= col2.row()
                r.label(icon='INFO', text="The pinned object is not in active scene")
                r2 = col2.row()
                try:
                    r2.label(text="Select object with")
                    r2.label(text=f"{context.space_data.pin_id.name}", icon='OUTLINER_DATA_MESH')
                    r2.label(text=" datablock again in this scene")
                except AttributeError:
                    r2.label(text="Select object with this datablock again in this scene")
            except Exception:
                pass
        
        # Opeartor Context
        uiel_operator_context(self, context)

        # Pin exception info                
        uiel_pin_exception_info(self, context, layout, pin_ref, mesh_data_pinned)
        
        # Notes about some of the attributes               
        uiel_attribute_extra_notes(self, context, layout, ob_data)
        
        # Extra tools
        uiel_debug_menu(self, context, layout, gui_prop_group, pin_ref)
            
        # Quick Attribute Node Menu
        uiel_quick_attribute(self, context, layout, ob_data, active_obj_in_viewport)

# -----------------------------------------

def uiel_pin_exception_info(self, context, layout, pin_ref, mesh_data_pinned):
    # ATTRIBUTE ASSIGN PANEL PIN EXCEPTIONS
    if pin_ref is None and mesh_data_pinned:
        box = layout.box()
        box.alert = True
        col2 = box.column(align=True)
        r= col2.row()
        r.label(icon='INFO', text="Note")
        col2.label(text="Please select object with the mesh data again, data needs to be refreshed")

def uiel_attribute_extra_notes(self, context, layout, ob_data):
    # ATTRIBUTE ASSIGN PANEL EXTRA ATTRIBUTE NOTES
    if (ob_data.attributes.active and ob_data.attributes.active.name in static_data.defined_attributes
        and static_data.defined_attributes[ob_data.attributes.active.name].warning_message != ""):
        box = layout.box()
        col2 = box.column(align=True)
        r= col2.row()
        r.label(icon='ERROR', text=f"Note: {ob_data.attributes.active.name} attribute")
        col2.label(text=static_data.defined_attributes[ob_data.attributes.active.name].warning_message)

def uiel_quick_attribute(self, context, layout, ob_data, active_obj_in_viewport):
    # ATTRIBUTE ASSIGN PANEL QUICK ATTRIBUTE MENU
    if etc.get_preferences_attrib("quick_attribute_node_enable"):
        box = layout.box()
        row = box.row()
        row.label(text="Quick Attribute Node")
        
        if active_obj_in_viewport and ob_data.attributes.active:

            areas = func.get_supported_areas_for_attribute(ob_data.attributes.active, ids=True)

            if len(areas):
                col = box.grid_flow(columns=2, align=False, even_columns=True, even_rows=True)
                for i, area in enumerate(areas):
                    node_editor_icon = static_data.node_editors[func.get_node_editor_type(area, use_id=True)].icon
                    nt = func.get_area_node_tree(area, useid=True)
                    parent = func.get_node_tree_parent(nt)
                    if nt is None:
                        parentname = "No node tree"
                    elif parent is None:
                        parentname = nt.name
                    else:
                        parentname = parent.name
                    subrow = col.row(align=False)
                    subrow.enabled = nt is not None
                    op = subrow.operator("mesh.attribute_create_attribute_node", text=f"W{i+1}: {parentname}", icon=node_editor_icon)
                    op.windowid = area[0]
                    op.areaid = area[1]
            elif not func.get_node_editor_areas():
                box.label(text="No node editors are open", icon='ERROR') 
            else:
                box.label(text="None of Node Editors support this attribute", icon='ERROR') 

        else:
            box.label(text="No active attribute", icon='ERROR')

        # List of node editors open (debug)
        if etc.get_preferences_attrib('debug_operators'):
            areas = func.get_node_editor_areas()
            col = box.column(align=True)
            col.label(text="DEBUG")
            for i, area in enumerate(areas):
                col.label(text=f"{i+1}: {func.get_node_editor_type(area)}")

def uiel_debug_menu(self, context, layout, gui_prop_group, pin_ref):
    # ATTRIBUTE ASSIGN PANEL DEBUG MENU
    if etc.get_preferences_attrib('debug_operators'):
        # sub = row.row(align=True)
        dbgbox = layout.box()
        dbgrow = dbgbox.row()
        dbgrow.label(text="DEBUG MENU")

        dbgrow = dbgbox.row()
        dbgrow.operator("mame.tester", text="run tests")
        dbgrow.operator("mame.create_all_attribs", text="attrib test")
        dbgrow.operator("mame.create_point_cloud")
        
        dbgrow = dbgbox.row()
        dbgrow.label(text=f"Pinned: {context.space_data.use_pin_id}")
        dbgrow.label(text=f"RefsCount: {len(gui_prop_group.last_object_refs)}/{etc.get_preferences_attrib('pinned_mesh_refcount_max')}")

        dbgrow = dbgbox.row()
        dbgrow.label(text=f"Reference: {pin_ref is not None}")
        dbgrow.label(text=f"LastObjRef: {pin_ref.obj_ref_name if pin_ref is not None else 'None'}")

# Context Menus
# -----------------------------------------

def attribute_context_menu_extension(self, context):
    """
    Extra entries in ^ menu
    """

    self.layout.operator_context = "INVOKE_DEFAULT"
    if etc.get_preferences_attrib('add_set_attribute') and bpy.app.version >= (3,5,0):
        self.layout.operator('mesh.attribute_set')
    self.layout.operator('mesh.attribute_create_from_data', icon='MESH_DATA')
    self.layout.operator('mesh.attribute_convert_to_mesh_data', icon='MESH_ICOSPHERE')
    self.layout.operator('mesh.attribute_duplicate', icon='DUPLICATE')
    self.layout.operator('mesh.attribute_invert', icon='UV_ISLANDSEL')
    self.layout.operator('mesh.attribute_copy', icon='COPYDOWN')
    self.layout.operator('mesh.attribute_resolve_name_collisions', icon='SYNTAX_OFF')
    self.layout.operator('mesh.attribute_conditioned_select', icon='CHECKBOX_HLT')
    self.layout.operator('mesh.attribute_built_in_create', icon='ADD')
    self.layout.operator('mesh.attribute_randomize_value', icon='SHADERFX')
    self.layout.operator('mesh.attribute_remove_all', icon='REMOVE')
    if etc.get_blender_support(minver=(3,3,0)): 
        self.layout.operator('mesh.attribute_to_image', icon="TEXTURE")
    self.layout.operator('mesh.attribute_to_csv', icon='FILE_NEW')
    self.layout.operator('mesh.attribute_from_file', icon='FILEBROWSER')

class MameCustomAttributeContextMenu(bpy.types.Menu):
    """
    Context menu for panels that do not allow extending built-in context menus
    """

    bl_idname = "OBJECT_MT_mame_custom_attribute_context_menu"
    bl_label = "Attribute Context Menu"

    draw = attribute_context_menu_extension

def vertex_groups_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > Vertex Groups
    """
    if etc.get_preferences_attrib('extra_context_menu_vg'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_vertex_group', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_all_vertex_groups', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_vertex_group_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_vertex_group_assignment', icon='MESH_DATA')

def shape_keys_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > Shape Keys
    """
    if etc.get_preferences_attrib('extra_context_menu_sk'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_shape_key', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_offset_from_shape_key', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_all_shape_keys', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_offset_from_all_shape_keys', icon='MESH_DATA')

def material_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Material > Material
    """
    if etc.get_preferences_attrib('extra_context_menu_materials'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_material_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_material_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_material_slot_assignment', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_all_from_material_slot_assignment', icon='MESH_DATA')

def uvmaps_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > UVMaps
    """
    if etc.get_preferences_attrib('extra_context_menu_uvmaps') and etc.get_blender_support(minver_unsupported=(3,5,0)):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator('mesh.attribute_quick_from_uvmap', icon='MESH_DATA')

def facemaps_context_menu_extension(self,context):
    """
    Entries in ^ menu located in Properties > Data > Face Maps
    """
    if etc.get_preferences_attrib('extra_context_menu_fm') and etc.get_blender_support(minver_unsupported=(4,0,0)):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator('mesh.attribute_quick_from_face_map', icon='MESH_DATA')
        self.layout.operator('mesh.attribute_quick_from_face_map_index', icon='MESH_DATA')

def color_attributes_menu_extension(self, context):
    if etc.get_preferences_attrib('extra_context_menu_color_attributes'):
        self.layout.separator()
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator('mesh.color_attribute_quick_bake', icon='OUTPUT')

# Edit Mode
# -----------------------------------------

class VIEW3D_MT_edit_mesh_vertices_attribute_from_data(bpy.types.Menu):
    bl_label = "New Attribute from..."

    def draw(self, _context):
        layout = self.layout
        for edt in [edt for edt in func.get_source_data_enum_without_separators(self, bpy.context) if 'POINT' in static_data.object_data_sources[edt[0]].domains_supported]:
            row = layout.row()
            row.operator_context = static_data.object_data_sources[edt[0]].quick_ui_exec_type
            op = self.layout.operator('mesh.attribute_create_from_data',
                                      icon = func.get_mesh_data_enum_entry_icon(static_data.object_data_sources[edt[0]]),
                                      text=edt[1])
            op.attrib_name = ''
            op.domain_data_type_enum = edt[0]
            op.target_attrib_domain_enum = 'POINT'
            op.b_batch_convert_enabled
            op.b_offset_from_offset_to_toggle
            op.b_overwrite
            op.b_enable_name_formatting
            op.b_auto_convert = False

def vertex_context_menu_extension(self,context):
    """
    Entries in Vertex context menu in edit mode
    """
    if etc.get_preferences_attrib('extra_context_menu_vertex_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.menu("VIEW3D_MT_edit_mesh_vertices_attribute_from_data")

class VIEW3D_MT_edit_mesh_edges_attribute_from_data(bpy.types.Menu):
    bl_label = "New Attribute from..."

    def draw(self, _context):
        layout = self.layout
        for edt in [edt for edt in func.get_source_data_enum_without_separators(self, bpy.context) if 'EDGE' in static_data.object_data_sources[edt[0]].domains_supported]:
            row = layout.row()
            row.operator_context = static_data.object_data_sources[edt[0]].quick_ui_exec_type
            op = self.layout.operator('mesh.attribute_create_from_data',
                                      icon = func.get_mesh_data_enum_entry_icon(static_data.object_data_sources[edt[0]]),
                                      text=edt[1])
            op.attrib_name = ''
            op.domain_data_type_enum = edt[0]
            op.target_attrib_domain_enum = 'EDGE'
            op.b_batch_convert_enabled
            op.b_offset_from_offset_to_toggle
            op.b_overwrite
            op.b_enable_name_formatting
            op.b_auto_convert = False

def edge_context_menu_extension(self,context):
    """
    Entries in Edge context menu in edit mode
    """
    if etc.get_preferences_attrib('extra_context_menu_edge_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.menu("VIEW3D_MT_edit_mesh_edges_attribute_from_data")

class VIEW3D_MT_edit_mesh_faces_attribute_from_data(bpy.types.Menu):
    bl_label = "New Attribute from..."

    def draw(self, _context):
        layout = self.layout
        
        for edt in [edt for edt in func.get_source_data_enum_without_separators(self, bpy.context) if 'FACE' in static_data.object_data_sources[edt[0]].domains_supported]:
            row = layout.row()
            row.operator_context = static_data.object_data_sources[edt[0]].quick_ui_exec_type
            op = row.operator('mesh.attribute_create_from_data',
                                      icon = func.get_mesh_data_enum_entry_icon(static_data.object_data_sources[edt[0]]),
                                      text=edt[1])
            op.attrib_name = ''
            op.domain_data_type_enum = edt[0]
            op.target_attrib_domain_enum = 'FACE'
            op.b_batch_convert_enabled
            op.b_offset_from_offset_to_toggle
            op.b_overwrite
            op.b_enable_name_formatting
            op.b_auto_convert = False

def face_context_menu_extension(self,context):
    """
    Entries in Face context menu in edit mode
    """
    if etc.get_preferences_attrib('extra_context_menu_face_menu'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.menu("VIEW3D_MT_edit_mesh_faces_attribute_from_data")

# Object Mode
# -----------------------------------------

def object_context_menu_extension(self,context):
    """
    Entries in Object context menu in object mode
    UNUSED
    """
    if etc.get_preferences_attrib('extra_context_menu_object'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        # self.layout.separator()

# Sculpt Mode
# -----------------------------------------

def sculpt_mode_mask_menu_extension(self, context):
    """
    Extra entries in sculpt mode mask menu on the menu bar
    """
    
    if etc.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_current_sculpt_mask', icon='MESH_DATA') 
        self.layout.operator('mesh.attribute_quick_sculpt_mask_from_active_attribute', icon='MOD_MASK')
        self.layout.operator('mesh.selected_in_edit_mode_to_sculpt_mode_mask')

def sculpt_mode_face_sets_menu_extension(self, context):
    """
    Extra entries in sculpt mode face sets menu on the menu bar
    """
    if etc.get_preferences_attrib('extra_context_menu_sculpt'):
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.separator()
        self.layout.operator('mesh.attribute_quick_from_face_sets', icon='MESH_DATA') 
        self.layout.operator('mesh.attribute_quick_face_sets_from_attribute', icon='FACE_MAPS')

class SculptMode3DViewHeaderSettings(bpy.types.Menu):
    """
    Menu shown in sculpt mode tool n-panel menu, Mask Manager submenu
    
    Contains extra toggles that are not required to be visible by default
    """
    bl_idname = "VIEW3D_MT_select_test"
    bl_label = "Settings"

    def draw(self, context):
        layout = self.layout
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        layout.prop(gui_prop_group, "qops_sculpt_mode_attribute_show_unsupported")
        layout.prop(gui_prop_group, "qops_sculpt_mode_mask_normalize")

class MasksManagerPanel(bpy.types.Panel):
    """
    The panel menu in N-Panel Tool tab and properties panel Tool tab.

    Allows managing masks and face sets from attributes in a quicker way
    """
    bl_label = "Mask Manager"
    bl_idname = "TOOL_PT_MAME_Masks_Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'


    # Show only in sculpt mode and if enabled in preferences
    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and etc.get_preferences_attrib('extra_header_sculpt')

    def draw(self, context):

        obj_prop_group = context.active_object.data.MAME_PropValues
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        
        col = self.layout.column(align=True)

        # box2.ui_units_x = 1.0

        # Toggle between masks and face sets
        row2 = col.row(align=True)
        row2.label(text="Mode")
        row2 = col.row(align=True)
        
        row2.prop_enum(gui_prop_group, "enum_sculpt_mode_attribute_mode_toggle", "MASK")
        row2.prop_enum(gui_prop_group, "enum_sculpt_mode_attribute_mode_toggle", "FACE_SETS")

        # Attribute selector dropdown menu
        row2 = col.row(align=True)
        row2.label(text="Attribute")
        box2 = col.row(align=True)
        box2.ui_units_x = 5
        gui_prop_group.validify_enums() # make sure the selection in dropdown exists
        box2.prop(gui_prop_group, "enum_sculpt_mode_attribute_selector", text="")

        # Modify sub-menu
        row2 = col.row(align=True)
        row2.label(text=f"Modify {func.get_friendly_name_from_enum_function(context, gui_prop_group.get_enum_sculpt_mode_attribute_mode_toggle_enum, gui_prop_group.enum_sculpt_mode_attribute_mode_toggle)}")
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_apply", icon='ZOOM_PREVIOUS')
        row.operator("mesh.mame_attribute_sculpt_mode_apply_inverted",text="Inverted", icon='SELECT_SUBTRACT')
    
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_extend", text="Add", icon='ZOOM_IN')
        row.operator("mesh.mame_attribute_sculpt_mode_subtract", text="Subtract", icon='ZOOM_OUT')
        col.operator('mesh.selected_in_edit_mode_to_sculpt_mode_mask', text="From Edit Mode Selection", icon='RESTRICT_SELECT_OFF')
        
        # Manage sub-menu
        row2 = col.row(align=True)
        row2.label(text="Manage")
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_new",text="Store", icon='FILE_NEW')
        row.operator("mesh.mame_attribute_sculpt_mode_remove",text="Remove", icon='PANEL_CLOSE')
        row = col.row(align=True)
        row.operator("mesh.mame_attribute_sculpt_mode_overwrite",text="Overwrite Attribute", icon='COPYDOWN')
        
        col.menu('VIEW3D_MT_select_test', text='Settings', text_ctxt='', translate=True, icon='SETTINGS')

        
        # Show warning for multiresolution
        for mod in context.active_object.modifiers:
            if mod.type == 'MULTIRES':
                box = col.box()
                col2 = box.column(align=True)
                r= col2.row()
                r.label(icon='ERROR', text="Warning")
                r.alert=True
                col2.label(text="Multiresolution is not-compatible")
                break

        if len(context.active_object.data.vertices) > etc.LARGE_MESH_VERTICES_COUNT:
            box = col.box()
            col2 = box.column(align=True)
            r= col2.row()
            r.label(icon='ERROR', text="Warning")
            r.alert=True
            col2.label(text="HiPoly mesh - slow operatons")

# Value assignment UIs
# -----------------------------------------

def get_attribute_value_input_ui(layout,
                    source,
                    prop_name:str,
                    data_type:str):
    """Shows UI for inputting attribute values

    Args:
        layout (ref): Layout reference
        source (ref): Source to get property from
        prop_name (str): name of the property
        data_type (str): Data type
    """
    
    # Show true false for booleans
    attr_val = getattr(source, prop_name)
    if type(attr_val) == bool:
        title_str = "True" if attr_val else "False"
    else:
        title_str = ""
    
    matrix_type = static_data.attribute_data_types[data_type].large_capacity_vector
    matrix_w = static_data.attribute_data_types[data_type].large_capacity_vector_size_width
    matrix_h = static_data.attribute_data_types[data_type].large_capacity_vector_size_height

    # Matrix input UI
    if matrix_type:
        matrixcol = layout.column(align=True)
        for i in range(0, matrix_w):
            matrix_vals_col = matrixcol.column(align=True)
            matrix_vals_row = matrix_vals_col.row(align=True)
            for j in range(0, matrix_h):
                matrix_vals_row.prop(source, prop_name, text=title_str, toggle=True, index=i*matrix_w+j)
    
    # Blender built-in method for other
    else:
        layout.prop(source, prop_name, text=title_str, toggle=True)



# Multiselect List
# -----------------------------------------

class ATTRIBUTE_UL_attribute_multiselect_list(bpy.types.UIList):
    """
    Multi-selection list of attributes, with tickboxes, data types and domains on the list entries.
    Supports filtering and reordering
    """

    name_filter: bpy.props.StringProperty(name="Name", default="")

    datatype_filter_compatible: bpy.props.BoolProperty(name="Same as target", default=False)
    datatype_filter: bpy.props.CollectionProperty(type = etc.GenericBoolPropertyGroup)

    domain_filter_compatible: bpy.props.BoolProperty(name="Same as target", default=False)
    domain_filter: bpy.props.CollectionProperty(type = etc.GenericBoolPropertyGroup)
    
    def _gen_order_update(name1, name2):
        def _u(self, ctxt):
            if (getattr(self, name1)):
                setattr(self, name2, False)
        return _u

    use_order_name: bpy.props.BoolProperty(
        name="Name", default=False, options=set(),
        description="Sort groups by their name (case-insensitive)",
        update=_gen_order_update("use_order_name", "use_order_importance"),
    )

    sort_reverse: bpy.props.BoolProperty(
        name="Reverse",
        default=False,
        options=set(),
        description="Reverse sorting",
    )


    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues

        # layout.label(text=item.attribute_name)
        
        row = layout.row()
        row.prop(item, "b_select", text=item.attribute_name)
        # subrow = row.row()
        # subrow.scale_x = 1.0
        # subrow.label(text=item.attribute_name)

        subrow = row.row()
        subrow.scale_x = 0.5
        subrow.alert = not item.b_domain_compatible and gui_prop_group.b_attributes_uilist_highlight_different_attrib_types
        subrow.label(text = item.domain_friendly_name)

        subrow = row.row()
        subrow.scale_x = .75
        subrow.alert = not item.b_data_type_compatible and gui_prop_group.b_attributes_uilist_highlight_different_attrib_types
        subrow.label(text = item.data_type_friendly_name)

    
    def draw_filter(self, context, layout):
        gui_prop_group = bpy.context.window_manager.MAME_GUIPropValues
        col = layout.column()

    
        row = col.row(align=True)
        row.prop(self, "name_filter", text="")
        row.prop(self, "use_order_name", text="", icon="SORTALPHA")
        icon = 'SORT_ASC' if self.sort_reverse else 'SORT_DESC'
        row.prop(self, "sort_reverse", text="", icon=icon)
    
        col.label(text="Filter Domains")

        if gui_prop_group.b_attributes_uilist_show_same_as_target_filter:
            filter_row = col.row(align=True)
            filter_row.prop(self, 'domain_filter_compatible', toggle=True)
        else:
            self.domain_filter_compatible = False

        filter_row = col.row(align=True)
        filter_row.enabled = not self.domain_filter_compatible
        for boolprop in self.domain_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)
        
        col.label(text="Filter Data Types")

        if gui_prop_group.b_attributes_uilist_show_same_as_target_filter:
            filter_row = col.row(align=True)
            filter_row.prop(self, 'datatype_filter_compatible', toggle=True)
        else:
            self.datatype_filter_compatible = False

        filter_row = col.grid_flow(columns=3, even_columns=False, align=True)
        filter_row.enabled = not self.datatype_filter_compatible
        for boolprop in self.datatype_filter:
            filter_row.prop(boolprop, f"b_value", toggle=True, text=boolprop.name)

    def initialize(self, context):
        self.datatype_filter.clear()

        for data_type in static_data.attribute_data_types:
            b = self.datatype_filter.add()
            b.b_value = True
            b.name = func.get_friendly_data_type_name(data_type)
            b.id = data_type

        for domain in static_data.attribute_domains:
            b = self.domain_filter.add()
            b.b_value = True
            b.name = func.get_friendly_domain_name(domain)
            b.id = domain

        self.prop_group = bpy.context.window_manager.MAME_GUIPropValues

    def filter_items(self, context, data, propname):
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        attributes = getattr(gui_prop_group, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        if not len(self.datatype_filter):
            self.initialize(context)

        filter_list = []
        sort_ids_list = []

        # Filtering

        # Filtering by name
        if self.name_filter:
            filter_list = helper_funcs.filter_items_by_name(self.name_filter, self.bitflag_filter_item, attributes, "attribute_name",
                                                          reverse=False)

        # make sure something is returned 
        if not filter_list:
            filter_list = [self.bitflag_filter_item] * len(attributes)

        # Filter by domain
        if self.domain_filter_compatible:
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.b_domain_compatible else 0
        else:
            d_filters = [d.id for d in self.domain_filter if d.b_value]
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.domain in d_filters else 0

        # Filter by datatype
        if self.datatype_filter_compatible:
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.b_data_type_compatible else 0
        else:
            dt_filters = [dt.id for dt in self.datatype_filter if dt.b_value]
            for i, item in enumerate(attributes):
                filter_list[i] = filter_list[i] if item.data_type in dt_filters else 0


        # Sorting

        # Sorting by name
        if self.use_order_name:
            sort_ids_list = helper_funcs.sort_items_by_name(attributes, "attribute_name")
        
        # Reverse sorting
        if self.sort_reverse:
            if not len(sort_ids_list):
                sort_ids_list = [*range(0, len(attributes))]
                
            sort_ids_list.reverse()

        return filter_list, sort_ids_list

# Message Box
# -----------------------------------------

class GenericMessageBox(bpy.types.Operator):
    """Shows an OK message box.

    """
    bl_idname = "window_manager.mame_message_box"
    bl_label = "Mesh Attributes Menu Extended Message"
    bl_options = {'REGISTER', 'INTERNAL'}

    # Width of the message box
    width: bpy.props.IntProperty(default=400)

    # Message to show
    message: bpy.props.StringProperty(default='')

    # Whether to use custom draw functions stored in MESSAGE_BOX_DRAW_FUNCTION global variable
    custom_draw: bpy.props.BoolProperty(default=False)

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=self.width)
        return {'FINISHED'}
    
    def draw(self, context):
        if self.custom_draw:
            global MESSAGE_BOX_DRAW_FUNCTION
            MESSAGE_BOX_DRAW_FUNCTION(self, context, message=self.message)
        else:
            layout = self.layout
            messages = self.message.splitlines()
            for msg in messages:
                layout.label(text=msg)


def draw_error_list(self, context, message=''):
    col = self.layout.column()
    col.label(icon='ERROR', text=message)

    max_errors = 10
    global MESSAGE_BOX_EXTRA_DATA
    errors = MESSAGE_BOX_EXTRA_DATA
    print(f"data{errors}")
    for error in range(0, min(max_errors+1, len(errors))):
        col.label(icon='DOT', text=errors[error])
    if len(errors) > max_errors:
        col.label(text=f"{len(errors)-max_errors} more...")

def set_message_box_function(function):
    """Assigns a custom draw function when using GenericMessageBox

    Args:
        function (func): function to call. Will be called with paramters: self, context, message
    """
    global MESSAGE_BOX_DRAW_FUNCTION
    MESSAGE_BOX_DRAW_FUNCTION = function

def set_message_box_extra_data(extra_data):
    """Stores custom data to use in custom draw function of GenericMessageBox

    Args:
        extra_data (any): any type of data 
    """
    global MESSAGE_BOX_EXTRA_DATA
    MESSAGE_BOX_EXTRA_DATA = extra_data

# Used in GenericMessageBox to use as a draw function 
MESSAGE_BOX_DRAW_FUNCTION = None

# Used in GenericMessageBox to use as extra data in draw function
MESSAGE_BOX_EXTRA_DATA = None

# Register
# ------------------------------------------
    
classes = [
    GenericMessageBox,
    ATTRIBUTE_UL_attribute_multiselect_list,
    MasksManagerPanel,
    SculptMode3DViewHeaderSettings,
    VIEW3D_MT_edit_mesh_vertices_attribute_from_data,
    VIEW3D_MT_edit_mesh_edges_attribute_from_data,
    VIEW3D_MT_edit_mesh_faces_attribute_from_data,
    MameCustomAttributeContextMenu
]

def ui_register():
    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.append(attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.append(attribute_context_menu_extension)
    bpy.types.VIEW3D_MT_mask.append(sculpt_mode_mask_menu_extension)
    bpy.types.VIEW3D_MT_face_sets.append(sculpt_mode_face_sets_menu_extension)
    bpy.types.MESH_MT_vertex_group_context_menu.append(vertex_groups_context_menu_extension)
    bpy.types.MESH_MT_shape_key_context_menu.append(shape_keys_context_menu_extension)
    bpy.types.MATERIAL_MT_context_menu.append(material_context_menu_extension)
    bpy.types.VIEW3D_MT_object.append(object_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(face_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(edge_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(vertex_context_menu_extension)
    bpy.types.DATA_PT_uv_texture.append(uvmaps_context_menu_extension)
    bpy.types.DATA_PT_pointcloud_attributes.append(attribute_assign_panel)

    if bpy.app.version >= (3,5,0):
        bpy.types.DATA_PT_CURVES_attributes.append(attribute_assign_panel)
    
    if bpy.app.version < (4,0,0):
        bpy.types.DATA_PT_face_maps.append(facemaps_context_menu_extension)
    
    if bpy.app.version >= (3,3,0):
        bpy.types.MESH_MT_color_attribute_context_menu.append(color_attributes_menu_extension)

def ui_unregister():
    # GUI Extensions
    bpy.types.DATA_PT_mesh_attributes.remove(attribute_assign_panel)
    bpy.types.MESH_MT_attribute_context_menu.remove(attribute_context_menu_extension)
    bpy.types.VIEW3D_MT_mask.remove(sculpt_mode_mask_menu_extension)
    bpy.types.VIEW3D_MT_face_sets.remove(sculpt_mode_face_sets_menu_extension)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(vertex_groups_context_menu_extension)
    bpy.types.MESH_MT_shape_key_context_menu.remove(shape_keys_context_menu_extension)
    bpy.types.MATERIAL_MT_context_menu.remove(material_context_menu_extension)
    bpy.types.VIEW3D_MT_object.remove(object_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(face_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(edge_context_menu_extension)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(vertex_context_menu_extension)
    bpy.types.MESH_MT_attribute_context_menu.remove(attribute_context_menu_extension)
    bpy.types.DATA_PT_uv_texture.remove(uvmaps_context_menu_extension)
    bpy.types.DATA_PT_pointcloud_attributes.remove(attribute_assign_panel)
    
    if bpy.app.version >= (3,5,0):
        bpy.types.DATA_PT_CURVES_attributes.remove(attribute_assign_panel)
    
    if bpy.app.version < (4,0,0):
        bpy.types.DATA_PT_face_maps.remove(facemaps_context_menu_extension)
    
    if bpy.app.version >= (3,3,0):
        bpy.types.MESH_MT_color_attribute_context_menu.remove(color_attributes_menu_extension)


def register():
    "Register classes. Exception handing in init"
    for c in classes:
        bpy.utils.register_class(c)
    
    ui_register()

def unregister():
    "Unregister classes. Exception handing in init"

    ui_unregister()

    for c in classes:
        bpy.utils.unregister_class(c)
