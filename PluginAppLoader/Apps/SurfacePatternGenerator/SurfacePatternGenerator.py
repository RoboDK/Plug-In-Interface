# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# The Surface Pattern Generator (SPG) App lets you generate surface patterns on an object surface,
# with its associated Curve Follow Project (CFP).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps
from _spgtools import *

import Settings

# Optionally provide a part name to auto select it without asking the user
PART_NAME = None  # 'Paint Part'


def runmain():

    #---------------------------------------------
    # Initialize the RoboDK API
    RDK = robolink.Robolink()

    #---------------------------------------------
    # First: Retrieve the part item
    if not RDK.ItemList(robolink.ITEM_TYPE_OBJECT, True):
        RDK.ShowMessage("A least one object is required for projection. Please add an Object.")
        quit()

    PART = None
    if PART_NAME is None:
        RDK.setSelection([])
        PART = RDK.ItemUserPick("Select a part", robolink.ITEM_TYPE_OBJECT)
        if not PART.Valid():
            ShowMsg("Operation cancelled by user")
            quit()
    else:
        PART = RDK.Item(PART_NAME, robolink.ITEM_TYPE_OBJECT)
        if not PART.Valid():
            raise Exception("The selected part is not valid or not available")

    #---------------------------------------------
    # List all the reference frames that we want to use to create
    # raster paths (references attached to the object reference
    part_ref = PART.Parent()

    # Get the list of items attached to the part reference
    ref_pattern_candidates = part_ref.Childs()

    # Iterate through these child items and list the reference frames
    # Optionally add ignore in the name
    REF_PATTERN_LIST = []
    for ref_i in ref_pattern_candidates:
        if ref_i.Type() == robolink.ITEM_TYPE_FRAME and (not "ignore" in ref_i.Name()):
            REF_PATTERN_LIST.append(ref_i)

    if len(REF_PATTERN_LIST) <= 0:
        RDK.ShowMessage("No reference frames found. Add one or more frames to " + part_ref.Name())
        quit()

    #---------------------------------------------
    # Load GUI tools
    S = Settings.Settings()
    S.Load(RDK)
    if not S.ShowUI(f"[{PART.Name()}] Surface Pattern Generator Settings"):
        return

    # Update pattern
    prog_name_list = []
    for REF in REF_PATTERN_LIST:
        new_obj = CreatePaths(REF, PART, S.SIZE_X, S.SIZE_Y, S.STEP_X, S.STEP_Y, S.REPEAT_TIMES, S.REPEAT_OFFSET, S.COVER_ALL, S.EVEN_DISTRIBUTION, S.CONTINUOUS, S.ANGLE_TRIANGLE, S.REMOVE_UNPROJECTED_POINTS)

        if S.CREATE_PROGRAM:
            prog = CreateProgram(REF, S.SPEED_OPERATION, S.ANGLE_TCP_X, S.ANGLE_TCP_Y)
            if prog is not None and prog.Valid():
                prog_name_list.append(prog.Name())

    if prog_name_list:
        CreateMainProgram(PART, prog_name_list)


if __name__ == "__main__":
    runmain()