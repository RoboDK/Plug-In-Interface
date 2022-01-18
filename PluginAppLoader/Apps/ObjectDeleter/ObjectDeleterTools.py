# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robodk.robolink import ITEM_TYPE_OBJECT, Robolink, Item  # RoboDK API
from robodk.robomath import distance
import os
import copy

#------ PARAMETERS ------#

# Paths
LOCAL_PATH: str = os.path.dirname(os.path.abspath(__file__))

# Parameters UID
PARAM_UID: str = 'OBJDELETE_%s'
PARAM_RADIUS: str = PARAM_UID % 'RADIUS'
PARAM_PARENT_NAME: str = PARAM_UID % 'PARENT'

# Defaults
DEFAULT_RADIUS: float = 250  # mm
DEFAULT_PARENT: Item = None

# Global parameters
global RADIUS
global PARENT
RADIUS = copy.copy(DEFAULT_RADIUS)
PARENT = copy.copy(DEFAULT_PARENT)


def loadDefaults():
    global RADIUS
    global PARENT

    RADIUS = copy.copy(DEFAULT_RADIUS)
    PARENT = copy.copy(DEFAULT_PARENT)


def loadParameters(RDK=None):
    if RDK is None:
        RDK = Robolink()

    global RADIUS
    global PARENT

    radius = RDK.getParam(PARAM_RADIUS, True)
    if radius is not None and radius != '':
        RADIUS = float(radius)

    parent_name = RDK.getParam(PARAM_PARENT_NAME, True)
    if parent_name is not None and parent_name != '':
        item = RDK.Item(parent_name)
        if item.Valid() and item.Name() == parent_name:
            PARENT = item
    if PARENT is None:
        PARENT = RDK.ActiveStation()


def setParameters(RDK=None):
    if RDK is None:
        RDK = Robolink()

    global RADIUS
    global PARENT

    RDK.setParam(PARAM_RADIUS, RADIUS)

    if PARENT is not None:
        RDK.setParam(PARAM_PARENT_NAME, PARENT.Name())
    else:
        RDK.setParam(PARAM_PARENT_NAME, '')


def removeParameters(RDK=None):
    if RDK is None:
        RDK = Robolink()

    RDK.setParam(PARAM_RADIUS, b'')
    RDK.setParam(PARAM_PARENT_NAME, b'')


def objectsInZone(RDK=None):
    if RDK is None:
        RDK = Robolink()

    global RADIUS
    global PARENT

    objects_in_zone = []

    if PARENT is None or not PARENT.Valid():
        return objects_in_zone

    objects = RDK.ItemList(ITEM_TYPE_OBJECT)
    if objects is None or len(objects) < 1:
        return objects_in_zone

    p_abs = PARENT.PoseAbs().Pos()
    for obj in objects:
        if distance(p_abs, obj.PoseAbs().Pos()) < RADIUS:
            objects_in_zone.append(obj)

    return objects_in_zone


if __name__ == "__main__":
    pass