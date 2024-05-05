"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""

Attribute Domain Class Definition

"""
import bpy
from ..func import util_func




# Class
# ---------------------------

class AttributeDomain():

    # Name of a domain shown to user
    _friendly_name:str = "Not defined"

    # Name of a domain shown to user, plural
    _friendly_name_plural:str = "Not defined"

    # Name of a domain, shorter
    _friendly_name_short:str = "Undefined"

    # Name of a domain, single letter preferably
    _friendly_name_veryshort:str = "?"

    # Minimum supported blender version
    _min_blender_ver:tuple = None

    # First unsupported blender version
    _unsupported_from_blender_ver:tuple = None

    # Blender Icon
    _icon:str = "ERROR"

    # Supported object types (str)
    _supported_object_types:list = []

    # ---------------------------

    def get_friendly_name(self, plural=False, short=False, very_short=False, object_type:str = None):
        """Returns a name that can be shown in UI

        Args:
            plural (bool, optional): Use plural. Defaults to False.
            short (bool, optional): Use shorter name
            very_short  (bool, optional): Use single letter name
            object_type  (str, optional): Use different naming depending on object type
        Returns:
            str: Friendly name
        """
        if plural:
            return self._friendly_name_plural
        elif short:
            return self._friendly_name_short
        elif very_short:
            return self._friendly_name_veryshort
        else:
            return self._friendly_name
    
    def get_is_supported(self):
        """Checks if domain is supported in currently running blender version

        Returns:
            bool: Supported or not
        """
        return util_func.get_blender_support(self._min_blender_ver, self._unsupported_from_blender_ver)

    def get_icon(self):
        """Returns icon string to use in UI

        Returns:
            str: Blender icon string
        """
        return self._icon

    def get_supported_object_types(self):
        """Returns a list of supported object types (str)
        """

        return self._supported_object_types

# All Domains
# ---------------------------

_DOMAINS = []

def get_domains():
    """Returns all defined domains

    Returns:
        list: List of AttributeDomain objects.
    """
    return _DOMAINS

def new_domain(domain:AttributeDomain):
    global _DOMAINS
    _DOMAINS.append(domain)

# Index definition
# ---------------------------

# Global variable accessible anywhere
POINT = AttributeDomain() 

POINT._friendly_name = 'Vertex'

new_domain(POINT)





# Defines mesh domain entries
AttributeDomain = namedtuple("AttributeDomain", [
    "friendly_name",
    "friendly_name_plural",
    "friendly_name_short",                      # The name presented to the user (shorter)
    "friendly_name_veryshort",                  # The name presented to the user (shorter)
    "min_blender_ver",                          # Minimum blender version to include this domain
    "unsupported_from_blender_ver",             # Minimum blender version to exclude this domain
    "icon",                                     # UI Icon
    "object_types",                             # Object types that support this domain
])

# Defines all mesh domains
attribute_domains = {
    "POINT": AttributeDomain(
        friendly_name="Vertex", # Use get_friendly_domain_name with context to get points for curves instead.
        friendly_name_plural="Vertices",
        friendly_name_short="Vertex",
        friendly_name_veryshort="V",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='VERTEXSEL',
        object_types=['MESH','POINTCLOUD', 'CURVES']
    ),
    "EDGE": AttributeDomain(
        friendly_name="Edge",
        friendly_name_plural="Edges",
        friendly_name_short="Edge",
        friendly_name_veryshort="E",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='EDGESEL',
        object_types=['MESH']
    ),
    "FACE": AttributeDomain(
        friendly_name="Face",
        friendly_name_plural="Faces",
        friendly_name_short="Face",
        friendly_name_veryshort="V",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='FACE_MAPS',
        object_types=['MESH']
    ),
    "CORNER": AttributeDomain(
        friendly_name="Face Corner",
        friendly_name_plural="Face Corners",
        friendly_name_short="Corner",
        friendly_name_veryshort="C",
        min_blender_ver=None,
        unsupported_from_blender_ver=None,
        icon='FACE_CORNER',
        object_types=['MESH']
    ),
    "CURVE": AttributeDomain(
        friendly_name="Spline",
        friendly_name_plural="Splines",
        friendly_name_short="Spline",
        friendly_name_veryshort="S",
        min_blender_ver=(3,3),
        unsupported_from_blender_ver=None,
        icon='CURVE_DATA',
        object_types=['CURVES']
    ),
}


