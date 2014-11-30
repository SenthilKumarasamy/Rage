import sys
import os
import numpy
from numpy.distutils import numpy_distribution
basepath = os.path.dirname('__file__')
filepath = os.path.abspath(os.path.join(basepath, "..", ".."))
if filepath not in sys.path:
    sys.path.append(filepath)
    
from distutils.core import setup
import py2exe

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version="0.1.0",
    description="Reconciliation",
    name="NPL Flow sheet",

    # targets to build
    # windows = ["test_wx.py"],
    console=["NPL_FLOW.py"]
    , options={ 
             "py2exe":  { 
                          r'includes': [r'scipy.sparse.csgraph._validation',
                                        r'scipy.special._ufuncs_cxx'],
                          "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe"],
                         } 
            }
    )
