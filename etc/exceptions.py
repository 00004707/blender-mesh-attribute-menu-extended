"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Addon Exceptions 
"""

import bpy, os, sys, traceback

# Local utility functions
# ------------------------------------------

def get_traceback():
    """Returns last traceback

    Returns:
        traceback: last traceback
    """

    # Get last exception
    return sys.exc_info()[-1]

    
def get_exception_raiser_name(tb):
    """Get object/element name that raised an exception

    Args:
        tb (traceback): traceback to extract

    Returns:
        str: Who let the dogs out
    """
    frame_summary = traceback.extract_tb(tb)
    return frame_summary[0][2]

# Exceptions
# ------------------------------------------


# Register
# ------------------------------------------
 
classes = []

def register(init_module):

    for c in classes:
        bpy.utils.register_class(c)
    

def unregister(init_module):
    for c in classes:
        bpy.utils.unregister_class(c)


# Exceptions
# ------------------------------------------

class MeshDataReadException(Exception):
    """
    Exception thrown when reading data from mesh has failed
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[READ] " + self.function_name + ": " + self.message)


class MeshDataWriteException(Exception):
    """
    Exception thrown when writing data to mesh has failed
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[WRITE] " + self.function_name + ": " + self.message)


class GenericFunctionParameterError(Exception):
    """
    Exception thrown when input parameter of a function is invalid
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[PARAM] " + self.function_name + ": " + self.message)


class ExternalAssetException(Exception):
    """
    Exception thrown when external asset cannot be loaded
    """
    def __init__(self, function_name, message=""):
        self.function_name = function_name
        self.message = message
        super().__init__("[ASSET] " + self.function_name + ": " + self.message)