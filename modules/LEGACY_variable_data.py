
"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Volatile data, variables and other
"""

import bpy
from etc.property_groups import MAME_PropValues
from etc.property_groups import MAME_GUIPropValues
import func.util_func
from ..etc import property_groups


classes = [
    MAME_PropValues,
    MAME_GUIPropValues,
]

register_weight = -100


