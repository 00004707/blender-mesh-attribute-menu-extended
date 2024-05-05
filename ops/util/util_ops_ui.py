
import bpy
from modules import LEGACY_etc, LEGACY_static_data
from modules.LEGACY_etc import __addon_package_name__
from ...func import util_func
from ...modules import func


class AttributesPanel_PaletteNew(bpy.types.Operator):
    """
    Used to create new palette in attributes panel
    """
    bl_idname = "window_manager.mame_attributes_panel_palette_new"
    bl_label = "New Palette"
    bl_description = "Create new palette"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):

        gui_prop_group = util_func.get_wm_propgroup()
        palette = bpy.data.palettes.new('Palette')

        gui_prop_group.color_palette = palette
        return  {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True

class AttributesPanel_PaletteColorAdd(bpy.types.Operator):
    """
    Used to create new entry in palette in attributes panel
    """
    bl_idname = "window_manager.mame_attributes_panel_palette_color_add"
    bl_label = "Add Color to Palette"
    bl_description = "Add Color to Palette"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):

        gui_prop_group = util_func.get_wm_propgroup()
        obj, obj_data = func.obj_func.get_object_in_context(context)
        obj_prop_group = util_func.get_datablock_propgroup(obj_data)
        attr_data_type = obj_data.attributes.active.data_type
        
        gui_prop_group.color_palette = util_func.get_datablock_prop_group_ui_attribute_value(obj_prop_group, attr_data_type)

        return  {'FINISHED'}

    @classmethod
    def poll(self, context):

        obj, obj_data = func.obj_func.get_object_in_context(context)
        
        if not obj_data.attributes.active:
            self.poll_message_set("No active attribute")
            return False
        if obj_data.attributes.active.data_type not in util_func.get_color_data_types():
            self.poll_message_set("Active attribute is not a color")
            return False

        return True

# Register
# ------------------------------------------
 
classes = [
    AttributesPanel_PaletteNew,
    ]

def register(init_module):

    for c in classes:
        bpy.utils.register_class(c)
    

def unregister(init_module):
    for c in classes:
        bpy.utils.unregister_class(c)


class SelectDomainButton(bpy.types.Operator):
    """
    Used in gui to select domains with non-zero value
    """
    bl_idname = "mesh.attribute_select_button"
    bl_label = "Select"
    bl_description = "Select attribute domains"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    deselect: bpy.props.BoolProperty(name="deselect", default=False)

    def execute(self, context):

        LEGACY_etc.log(SelectDomainButton, f"select? {not self.deselect} attrib: {context.active_object.data.attributes.active}", LEGACY_etc.ELogLevel.VERBOSE)

        prop_group = context.object.data.MAME_PropValues
        select_nonzero = prop_group.val_select_non_zero_toggle

        dt = context.active_object.data.attributes.active.data_type
        params = {}
        params['b_deselect'] = self.deselect
        params['b_single_condition_vector'] = True
        params['b_use_color_picker'] =  False
        params['b_single_value_vector'] = False
        # select true booleans though
        params['attribute_comparison_condition_enum'] = 'NEQ' if (select_nonzero and dt != 'BOOLEAN') else 'EQ'
        params['b_string_case_sensitive'] = prop_group.val_select_casesensitive
        params['color_value_type_enum'] = 'RGBA'


        # Enable comparing for each vector dimension
        if LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype in [LEGACY_static_data.EDataTypeGuiPropType.VECTOR,
                                                                     LEGACY_static_data.EDataTypeGuiPropType.COLOR]:
            for i in range(0,len(LEGACY_static_data.attribute_data_types[dt].vector_subelements_names)):
                params[f'val_vector_{i}_toggle'] = True

        # Do not compare alpha value of colors
        if LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR:
            params[f'val_vector_3_toggle'] = False

        if select_nonzero:
            params[f'val_{dt.lower()}'] = func.attribute_func.get_attribute_default_value(datatype=dt)
            params['vec_0_condition_enum'] = 'NEQ'
            params['vector_value_cmp_type_enum'] = 'OR'
        else:
            params[f'val_{dt.lower()}'] = getattr(prop_group, f'val_{dt.lower()}')
            params['vec_0_condition_enum'] = 'EQ'
            params['vector_value_cmp_type_enum'] = 'AND'

        return  bpy.ops.mesh.attribute_conditioned_select('EXEC_DEFAULT', **params)


    @classmethod
    def poll(self, context):
        return func.poll_func.conditional_selection_poll(self, context)


class DeSelectDomainButton(bpy.types.Operator):
    """
    Used in gui to deselect domains with non-zero value
    """
    bl_idname = "mesh.attribute_deselect_button"
    bl_label = "Deselect"
    bl_description = "Deselect attribute domains"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        LEGACY_etc.log(DeSelectDomainButton, f"deselect {context.active_object.data.attributes.active}", LEGACY_etc.ELogLevel.VERBOSE)

        return  bpy.ops.mesh.attribute_select_button('EXEC_DEFAULT',
                                                     deselect=True)

    @classmethod
    def poll(self, context):
        return func.poll_func.conditional_selection_poll(self, context)


class RandomizeGUIInputFieldValue(bpy.types.Operator):
    """
    Used in gui to randomize the value in set attribute value field
    """
    bl_idname = "mesh.attribute_gui_value_randomize"
    bl_label = "Randomize"
    bl_description = "Randomize value"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        attrib = obj.data.attributes.active
        dt=attrib.data_type
        prop_group = context.object.data.MAME_PropValues
        args = {}
        args['range_min'] = LEGACY_static_data.attribute_data_types[dt].default_randomize_value_min
        args['range_max'] = LEGACY_static_data.attribute_data_types[dt].default_randomize_value_max
        args['bool_probability'] = .50
        args['string_capital'] = True
        args['string_lowercase'] = True
        args['string_numbers'] = True
        args['string_special'] = False
        args['string_custom'] = ""
        args['color_randomize_type'] = 'RGBA'
        for i in range(0, 3):
            args[f'b_vec_{i}'] = True
        if LEGACY_static_data.attribute_data_types[dt].gui_prop_subtype == LEGACY_static_data.EDataTypeGuiPropType.COLOR:
            args[f'b_vec_3'] = False # no alpha
        else:
            args[f'b_vec_3'] = True
        args['original_vector'] =  getattr(prop_group, f'val_{dt.lower()}')
        args['no_numpy'] = True
        setattr(prop_group, f'val_{dt.lower()}', func.attribute_func.get_random_attribute_of_data_type(obj, dt, 1, True, **args))

        return  {'FINISHED'}

    @classmethod
    def poll(self, context):
        obj = context.active_object

        if not obj:
            self.poll_message_set('No active object')
            return False
        elif obj.data.attributes.active is None:
            self.poll_message_set('No active attribute')
            return False
        elif not func.util_func.get_attribute_compatibility_check(context.active_object.data.attributes.active):
            self.poll_message_set("Attribute is unsupported in this addon version")
            return False
        elif not func.poll_func.pinned_mesh_poll(self, context, False):
            return False
        return True


class FakeFaceCornerSpillDisabledOperator(bpy.types.Operator):
    """
    Fake operator to occupy GUI place
    It looks better than using .enabled = False for UI elemtent
    """

    bl_idname = "mesh.always_disabled_face_corner_spill_operator"
    bl_label = "Fake operator to occupy GUI place"
    bl_description = "Enable Face Corner Spill"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(self, context):
        self.poll_message_set("Active attribute is not on Face Corner domain")
        return False


class MAMEDisable(bpy.types.Operator):
    """
    Addon disabler
    """

    bl_idname = "mame.disable"
    bl_label = "Disable Addon"
    bl_description = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        bpy.ops.preferences.addon_disable(module=__addon_package_name__)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True


class MAMEBlenderUpdate(bpy.types.Operator):
    """
    Addon Opens url to update blender
    """

    bl_idname = "mame.update_blender"
    bl_label = "Update blender"
    bl_description = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        bpy.ops.wm.url_open(url="https://www.blender.org/download/")
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True


class WINDOW_MANAGER_OT_mame_report_issue(bpy.types.Operator):
    """
    Reports issue with the addon
    """

    bl_idname = "window_manager.mame_report_issue"
    bl_label = "Report Issue"
    bl_description = "Open github page to report the issue"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        bpy.ops.wm.url_open(url="https://github.com/00004707/blender-mesh-attribute-menu-extended/issues")
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return True


class OpenWiki(bpy.types.Operator):
    """Opens wiki page in default browser"""

    bl_idname = "window_manager.mame_open_wiki"
    bl_label = "Open Documentation"
    bl_options = {'REGISTER', 'INTERNAL'}

    wiki_url: bpy.props.StringProperty(name="Wiki Page", default='')

    def execute(self, context):
        url = "https://github.com/00004707/blender-mesh-attribute-menu-extended/wiki" + '/' + str(self.wiki_url)
        bpy.ops.wm.url_open(url=url)
        return {'FINISHED'}