"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
ops

All operators

"""

import bpy, bmesh, colorsys

from modules.AttributeEditOnNodes import AttributeEditOnNodes
from modules.AttributeResolveNameCollisions import AttributeResolveNameCollisions
from modules.AttributesFromExternalFile import AttributesFromExternalFile
from modules.AttributesToExternalFile import AttributesToExternalFile
from modules.AttributesToImage import AttributesToImage
from modules.ConditionalSelection import ConditionalSelection
from modules.ConvertToMeshData import ConvertToMeshData
from modules.CopyAttributeToSelected import CopyAttributeToSelected
from modules.CreateAttribFromData import CreateAttribFromData
from modules.CreateBuiltInAttribute import CreateBuiltInAttribute
from modules.DuplicateAttribute import DuplicateAttribute
from modules.InvertAttribute import InvertAttribute
from modules.MarkNodeSelectionInEditMode import MarkNodeSelectionInEditMode
from modules.NodeOutputToNewObject import NodeOutputToNewObject
from modules.RandomizeAttributeValue import RandomizeAttributeValue
from modules.ReadValueFromSelectedDomains import ReadValueFromSelectedDomains
from modules.RemoveAllAttribute import RemoveAllAttribute
from ops.main.AssignActiveAttribValueToSelection import AssignActiveAttribValueToSelection



# Register
# ------------------------------------------
    
classes = [
    CreateAttribFromData,
    AssignActiveAttribValueToSelection,
    ConditionalSelection,
    DuplicateAttribute,
    InvertAttribute,
    RemoveAllAttribute,
    ConvertToMeshData,
    CopyAttributeToSelected,
    AttributeResolveNameCollisions,
    ReadValueFromSelectedDomains,
    RandomizeAttributeValue,
    AttributesFromExternalFile,
    AttributesToExternalFile,
    AttributesToImage,
    CreateBuiltInAttribute,
    AttributeEditOnNodes,
    NodeOutputToNewObject,
    MarkNodeSelectionInEditMode
]

def register(init_module):
    "Register classes. Exception handing in init"
    for c in classes:
        bpy.utils.register_class(c)

def unregister(init_module):
    "Unregister classes. Exception handing in init"
    for c in classes:
        bpy.utils.unregister_class(c)
