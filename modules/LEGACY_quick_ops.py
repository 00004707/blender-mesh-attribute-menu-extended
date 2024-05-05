"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Convenience buttons and operator callers from ops.py
"""

import bpy
import func.node_func
from ops.extension.masks_menu import QuickSculptModeApplyAttribute
from ops.extension.masks_menu import QuickSculptModeExtendAttribute
from ops.extension.masks_menu import QuickSculptModeSubtractAttribute
from ops.extension.masks_menu import QuickSculptModeRemoveAttribute
from ops.extension.masks_menu import QuickSculptModeNewAttribute
from ops.extension.masks_menu import QuickSculptModeOverwriteAttribute
from ops.extension.masks_menu import QuickSculptModeApplyInvertedAttribute
from ops.extension.quick_attribute_node import QuickAttributeNode
from ops.quick.colorattribute_qops import QuickBakeColorAttribute
from ops.quick.facemap_qops import QuickFaceMapAssignmentToAttribute
from ops.quick.facemap_qops import QuickFaceMapIndexToAttribute
from ops.quick.material_qops import QuickMaterialAssignmentToAttribute
from ops.quick.material_qops import QuickMaterialSlotAssignmentToAttribute
from ops.quick.material_qops import QuickAllMaterialAssignmentToAttribute
from ops.quick.material_qops import QuickAllMaterialSlotAssignmentToAttribute
from ops.quick.sculpt_qops import QuickCurrentSculptMaskToAttribute
from ops.quick.sculpt_qops import QuickActiveAttributeToSculptMask
from ops.quick.sculpt_qops import QuickSelectedInEditModeToSculptMask
from ops.quick.sculpt_qops import QuickFaceSetsToAttribute
from ops.quick.sculpt_qops import QuickActiveAttributeToFaceSets
from ops.quick.shape_key_qops import QuickShapeKeyToAttribute
from ops.quick.shape_key_qops import QuickAllShapeKeyToAttributes
from ops.quick.shape_key_qops import QuickShapeKeyOffsetToAttribute
from ops.quick.shape_key_qops import QuickAllShapeKeyOffsetToAttributes
from ops.quick.uvmap_qops import QuickUVMapToAttribute
from ops.quick.vertex_group_qops import QuickVertexGroupToAttribute
from ops.quick.vertex_group_qops import QuickAllVertexGroupToAttributes
from ops.quick.vertex_group_qops import QuickVertexGroupAssignmentToAttribute
from ops.quick.vertex_group_qops import QuickAllVertexGroupAssignmentToAttributes
from ops.util.util_ops_ui import SelectDomainButton
from ops.util.util_ops_ui import DeSelectDomainButton
from ops.util.util_ops_ui import RandomizeGUIInputFieldValue
from . import LEGACY_ops


# Quick nodes


# Select and deselect buttons


# Register
# ------------------------------------------
    
classes = [
    DeSelectDomainButton,
    SelectDomainButton,
    RandomizeGUIInputFieldValue,
    QuickCurrentSculptMaskToAttribute,
    QuickActiveAttributeToSculptMask,
    QuickFaceSetsToAttribute,
    QuickActiveAttributeToFaceSets,
    QuickShapeKeyToAttribute,
    QuickShapeKeyOffsetToAttribute,
    QuickAllShapeKeyToAttributes,
    QuickAllShapeKeyOffsetToAttributes,
    QuickVertexGroupToAttribute,
    QuickAllVertexGroupToAttributes,
    QuickVertexGroupAssignmentToAttribute,
    QuickAllVertexGroupAssignmentToAttributes,
    QuickMaterialAssignmentToAttribute,
    QuickAllMaterialAssignmentToAttribute,
    QuickAllMaterialSlotAssignmentToAttribute,
    QuickMaterialSlotAssignmentToAttribute,
    QuickSculptModeApplyAttribute,
    QuickSculptModeExtendAttribute,
    QuickSculptModeSubtractAttribute,
    QuickSculptModeRemoveAttribute,
    QuickSculptModeNewAttribute,
    QuickSculptModeOverwriteAttribute,
    QuickSculptModeApplyInvertedAttribute,
    QuickAttributeNode,
    QuickUVMapToAttribute,
    QuickFaceMapAssignmentToAttribute,
    QuickFaceMapIndexToAttribute,
    QuickBakeColorAttribute,
    QuickSelectedInEditModeToSculptMask,
    ]

def register(init_module):
    "Register classes. Exception handing in init"
    for c in classes:
        bpy.utils.register_class(c)

def unregister(init_module):
    "Unregister classes. Exception handing in init"
    for c in classes:
        bpy.utils.unregister_class(c)