# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robodk.robolink import Robolink, Item  # RoboDK API
from robodk.robomath import eye
import os
import copy

#------ PARAMETERS ------#

# Paths
LOCAL_PATH: str = os.path.dirname(os.path.abspath(__file__))
REF_BOX_MM_PATH: str = os.path.abspath(LOCAL_PATH + '/Ref_Box_MM.sld')
REF_BOX_IN_PATH: str = os.path.abspath(LOCAL_PATH + '/Ref_Box_IN.sld')
if not os.path.exists(REF_BOX_MM_PATH):
    raise
if not os.path.exists(REF_BOX_IN_PATH):
    raise

# Parameters UID
BOX_ITEM_NAME_MM: str = 'Box (%ix%ix%i mm)'  # Box (5x5x5 mm)
BOX_ITEM_NAME_IN: str = 'Box (%ix%ix%i in)'  # Box (5x5x5 in)
PARAM_UID: str = 'BOXSPAWNER_%s'
PARAM_BOX_X: str = PARAM_UID % 'SIZE_X'
PARAM_BOX_Y: str = PARAM_UID % 'SIZE_Y'
PARAM_BOX_Z: str = PARAM_UID % 'SIZE_Z'
PARAM_UNITS: str = PARAM_UID % 'UNITS'
PARAM_PARENT_NAME: str = PARAM_UID % 'PARENT'
PARAM_CONV_PARENT_NAME: str = PARAM_UID % 'CONV_PARENT'

# Defaults
DEFAULT_BOX_SIZE_XYZ: list = [400, 200, 200]
DEFAULT_USE_METRIC: bool = True
DEFAULT_PARENT: Item = None
DEFAULT_CONV_PARENT: Item = None

# Global parameters
global BOX_SIZE_XYZ
global USE_METRIC
global PARENT
global CONV_PARENT
BOX_SIZE_XYZ = copy.copy(DEFAULT_BOX_SIZE_XYZ)
USE_METRIC = copy.copy(DEFAULT_USE_METRIC)
PARENT = copy.copy(DEFAULT_PARENT)
CONV_PARENT = copy.copy(DEFAULT_CONV_PARENT)


def loadDefaults():
    global BOX_SIZE_XYZ
    global USE_METRIC
    global PARENT
    global CONV_PARENT

    BOX_SIZE_XYZ = copy.copy(DEFAULT_BOX_SIZE_XYZ)
    USE_METRIC = copy.copy(DEFAULT_USE_METRIC)
    PARENT = copy.copy(DEFAULT_PARENT)
    CONV_PARENT = copy.copy(DEFAULT_CONV_PARENT)


def loadParameters(RDK=None):
    if RDK is None:
        RDK = Robolink()

    global BOX_SIZE_XYZ
    global USE_METRIC
    global PARENT
    global CONV_PARENT

    size_x = RDK.getParam(PARAM_BOX_X, True)
    if size_x is not None and size_x != '':
        BOX_SIZE_XYZ[0] = float(size_x)

    size_y = RDK.getParam(PARAM_BOX_Y, True)
    if size_y is not None and size_y != '':
        BOX_SIZE_XYZ[1] = float(size_y)

    size_z = RDK.getParam(PARAM_BOX_Z, True)
    if size_z is not None and size_z != '':
        BOX_SIZE_XYZ[2] = float(size_z)

    metric = RDK.getParam(PARAM_UNITS, True)
    if metric is not None and metric != '':
        USE_METRIC = bool(metric == 'True')

    parent_name = RDK.getParam(PARAM_PARENT_NAME, True)
    if parent_name is not None and parent_name != '':
        item = RDK.Item(parent_name)
        if item.Valid() and item.Name() == parent_name:
            PARENT = item
    if PARENT is None:
        PARENT = RDK.ActiveStation()

    conv_parent_name = RDK.getParam(PARAM_CONV_PARENT_NAME, True)
    if conv_parent_name is not None and conv_parent_name != '':
        item = RDK.Item(conv_parent_name)
        if item.Valid() and item.Name() == conv_parent_name:
            CONV_PARENT = item


def setParameters(RDK=None):
    if RDK is None:
        RDK = Robolink()

    global BOX_SIZE_XYZ
    global USE_METRIC
    global PARENT
    global CONV_PARENT

    RDK.setParam(PARAM_BOX_X, BOX_SIZE_XYZ[0])
    RDK.setParam(PARAM_BOX_Y, BOX_SIZE_XYZ[1])
    RDK.setParam(PARAM_BOX_Z, BOX_SIZE_XYZ[2])
    RDK.setParam(PARAM_UNITS, USE_METRIC)

    if PARENT is not None:
        RDK.setParam(PARAM_PARENT_NAME, PARENT.Name())
    else:
        RDK.setParam(PARAM_PARENT_NAME, '')

    if CONV_PARENT is not None:
        RDK.setParam(PARAM_CONV_PARENT_NAME, CONV_PARENT.Name())
    else:
        RDK.setParam(PARAM_CONV_PARENT_NAME, '')


def removeParameters(RDK=None):
    if RDK is None:
        RDK = Robolink()

    RDK.setParam(PARAM_BOX_X, b'')
    RDK.setParam(PARAM_BOX_Y, b'')
    RDK.setParam(PARAM_BOX_Z, b'')
    RDK.setParam(PARAM_UNITS, b'')
    RDK.setParam(PARAM_PARENT_NAME, b'')
    RDK.setParam(PARAM_CONV_PARENT_NAME, b'')


def createBox(RDK=None):
    if RDK is None:
        RDK = Robolink()

    global BOX_SIZE_XYZ
    global USE_METRIC
    global PARENT
    global CONV_PARENT

    RDK.Render(False)

    x, y, z = BOX_SIZE_XYZ
    if USE_METRIC:
        new_box = RDK.AddFile(REF_BOX_MM_PATH, PARENT)
        new_box.setName(BOX_ITEM_NAME_MM % (x, y, z))
    else:
        new_box = RDK.AddFile(REF_BOX_IN_PATH, PARENT)
        new_box.setName(BOX_ITEM_NAME_IN % (x, y, z))

    new_box.setPose(eye(4))
    new_box.Scale([x, y, z])
    RDK.Update()

    if CONV_PARENT is not None:
        new_box.setParentStatic(CONV_PARENT)

    new_box.setVisible(True)
    RDK.Render(True)


if __name__ == "__main__":
    pass