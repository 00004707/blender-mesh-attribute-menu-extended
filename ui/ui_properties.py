"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

UI Interface Definition in properties panel

"""


# Properties Panel
# -----------------------------------------

def attributes_panel_extension(self, context):
    """
    Elements underneath the attributes list in Attributes Menu located in Properties Panel
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
        etc.log(attributes_panel_extension, "Unexpected use case, please report an issue!", etc.ELogLevel.ERROR)
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
    pin_ref, ob_data = func.util_func.update_last_object_reference_for_pinned_datablock(context, ob_data)
    
    # Show custom attribute context menu if needed
    if ob_type in ['CURVES', 'POINTCLOUD']:
        row = layout.row()
        row.menu("OBJECT_MT_mame_custom_attribute_context_menu")

    row = layout.row()

    if ((context.object and context.object.type in supported_object_types) 
        or (mesh_data_pinned and ob_data)):

        # Edit mode menu
        if ( active_obj_in_viewport and active_obj_in_viewport.mode == 'EDIT'):
            if ((etc.preferences.get_preferences_attrib('attribute_assign_menu') and ob_type == 'MESH')
                or (etc.preferences.get_preferences_attrib('attribute_assign_menu_curves') and ob_type == 'CURVES')
                or (etc.preferences.get_preferences_attrib('attribute_assign_menu_pointcloud') and ob_type == 'POINTCLOUD')):
                
                # Any attribute needs to be active
                if not ob_data.attributes.active:
                    box = row.box()
                    box.label(text="No active attribute", icon='ERROR')

                # Do not edit hidden attributes
                elif not func.attribute_func.get_is_attribute_valid_for_manual_val_assignment(ob_data.attributes.active):
                    box = row.box()
                    box.label(text="Editing of non-editable and hidden attributes is disabled.")
                
                else:
                    dt = ob_data.attributes.active.data_type

                    # Check for supported types
                    if not func.util_func.get_attribute_compatibility_check(ob_data.attributes.active):
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
                        get_attribute_value_input_ui(col2, prop_group, f"val_{dt.lower()}", dt)
                        
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
                        if etc.preferences.get_preferences_attrib("show_docs_button"):
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

        # Pin exception info                
        uiel_pin_exception_info(self, context, layout, pin_ref, mesh_data_pinned)
        
        # Notes about some of the attributes               
        uiel_attribute_extra_notes(self, context, layout, ob_data)
        
        # Extra tools
        uiel_debug_menu(self, context, layout, pin_ref)

        # Value palette
        uiel_attribute_value_palette(self, context)

        # Quick Attribute Node Menu
        uiel_quick_attribute(self, context, layout, ob_data, active_obj_in_viewport)

        # Pinned attributes
        uiel_bookmarked_attributes(self, context)

# -----------------------------------------

def uiel_pin_exception_info(self, context, layout, pin_ref, mesh_data_pinned):
    # ATTRIBUTE ASSIGN PANEL PIN EXCEPTIONS
    if pin_ref is None and mesh_data_pinned:
        box = layout.box()
        box.alert = True
        col2 = box.column(align=True)
        r= col2.row()
        r.label(icon='INFO', text="Note")
        col2.label(text="Please select any object with this datablock again ")
        col2.label(text="Reference to it has to be recreated")
        
        try:
            col2.label(text=f"{context.space_data.pin_id.name}", icon='OUTLINER_DATA_MESH')
        except AttributeError:
            pass

def uiel_attribute_extra_notes(self, context, layout, ob_data):
    # ATTRIBUTE ASSIGN PANEL EXTRA ATTRIBUTE NOTES
    if (ob_data.attributes.active and ob_data.attributes.active.name in LEGACY_static_data.built_in_attributes
        and LEGACY_static_data.built_in_attributes[ob_data.attributes.active.name].warning_message != ""):
        box = layout.box()
        col2 = box.column(align=True)
        r= col2.row()
        r.label(icon='ERROR', text=f"Note: {ob_data.attributes.active.name} attribute")
        col2.label(text=LEGACY_static_data.built_in_attributes[ob_data.attributes.active.name].warning_message)

def uiel_quick_attribute(self, context, layout, ob_data, active_obj_in_viewport):
    # ATTRIBUTE ASSIGN PANEL QUICK ATTRIBUTE MENU
    if etc.preferences.get_preferences_attrib("quick_attribute_node_enable"):
        box = layout.box()
        row = box.row()
        row.label(text="Quick Attribute Node")
        
        if active_obj_in_viewport and ob_data.attributes.active:

            areas = func.node_func.get_supported_areas_for_attribute(ob_data.attributes.active, ids=True)

            if len(areas):
                col = box.grid_flow(columns=2, align=False, even_columns=True, even_rows=True)
                for i, area in enumerate(areas):
                    node_editor_icon = LEGACY_static_data.node_editors[func.node_func.get_node_editor_type(area, use_id=True)].icon
                    nt = func.node_func.get_area_node_tree(area, useid=True)
                    parent = func.node_func.get_node_tree_parent(nt)
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
            elif not func.node_func.get_node_editor_areas():
                box.label(text="No node editors are open", icon='ERROR') 
            else:
                box.label(text="None of Node Editors support this attribute", icon='ERROR') 

        else:
            box.label(text="No active attribute", icon='ERROR')

        # List of node editors open (debug)
        if etc.preferences.get_preferences_attrib('debug_operators'):
            areas = func.node_func.get_node_editor_areas()
            col = box.column(align=True)
            col.label(text="DEBUG")
            for i, area in enumerate(areas):
                col.label(text=f"{i+1}: {func.node_func.get_node_editor_type(area)}")

    # todo support for bookmarked and hidden attributes here 

def uiel_attribute_value_palette(self, context):
    if not etc.preferences.get_preferences_attrib("attribute_palette_enable"):
        return
    
    layout = self.layout

    obj, obj_data = func.obj_func.get_object_in_context(context)

    # Show color palette if active attribute is color attribute
    if obj_data.attributes.active: # and obj_data.attributes.active.data_type in ['FLOAT_COLOR', 'BYTE_COLOR']:

        gui_prop_group = context.window_manager.MAME_GUIPropValues
        col = layout.column()
        #col.template_ID(gui_prop_group, "palette_selector", 
        #                new="window_manager.mame_attributes_panel_palette_new")
        col.prop_search(gui_prop_group,  "palette_selector", gui_prop_group, 'saved_palettes', text = '') 
        
        if gui_prop_group.palette_selector:
            pass
            #x = col.template_palette(gui_prop_group, "color_palette", color=True)

    else:
        layout.label(text="No active attribute", icon='ERROR')
    #template_palette(data, property, color=True) # try false for others

class DATA_PT_mesh_attributes_palette(bpy.types.Panel):
    bl_idname = "DATA_PT_mesh_attributes_palette"
    bl_label = "Value Palette"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'DATA_PT_mesh_attributes'
    bl_order = 10

    draw = uiel_attribute_value_palette

def uiel_bookmarked_attributes(self, context):
    layout = self.layout
    box = layout.box()
    row = box.row()
    row.label(text="Bookmarked Attributes")

def uiel_debug_menu(self, context, layout, pin_ref):
    # ATTRIBUTE ASSIGN PANEL DEBUG MENU
    if etc.preferences.get_preferences_attrib('debug_operators'):
        gui_prop_group = context.window_manager.MAME_GUIPropValues
        # sub = row.row(align=True)
        dbgbox = layout.box()
        dbgrow = dbgbox.row()
        dbgrow.label(text="DEBUG MENU")

        dbgrow = dbgbox.row()
        dbgrow.operator("mame.tester", text="run tests")
        dbgrow.operator("mame.create_all_attribs", text="attrib test")
        dbgrow = dbgbox.row()
        dbgrow.operator("mame.create_point_cloud")
        dbgrow.operator("mame.debug_nuke_pinned_object_reference_list")
        
        dbgrow = dbgbox.row()
        dbgrow.label(text=f"Pinned: {context.space_data.use_pin_id}")
        dbgrow.label(text=f"RefsCount: {len(gui_prop_group.last_object_refs)}/{etc.preferences.get_preferences_attrib('pinned_mesh_refcount_max')}")

        dbgrow = dbgbox.row()
        dbgrow.label(text=f"Reference: {pin_ref is not None}")
        dbgrow.label(text=f"LastObjRef: {pin_ref.obj_ref_name if pin_ref is not None else 'None'}")
