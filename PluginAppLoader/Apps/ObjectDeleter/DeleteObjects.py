# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file deletes objects in a zone using the preset settings.
# It can be called as an App action or within an App module.
#
# You can call it programmatically from a RoboDK program call.
# To use the zone ID #2, call DeleteObjectsLoop(2).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps

try:
    from ObjectDeleter import Settings  # Import as an App module. This is needed when the action is used externally, in a RoboDK script for instance.
except:
    import Settings


def DeleteObjects(RDK=None, S=None):
    """
    This file deletes objects in a zone using the preset settings.
    It can be called as an App action or within an App module.

    You can call it programmatically from a RoboDK program call.
    To use the zone ID #2, call DeleteObjectsLoop(2).
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Check if the parent exists
    PARENT_NAME = S.ZONE_FRAME[1][S.ZONE_FRAME[0]]
    PARENT = RDK.Item(PARENT_NAME)
    if not PARENT.Valid() or PARENT.Name() != PARENT_NAME or PARENT.Type() not in [robolink.ITEM_TYPE_STATION, robolink.ITEM_TYPE_FRAME]:
        RDK.ShowMessage(f"Unable to find the parent frame ({PARENT_NAME})! Did you set the settings?")
        return False

    # Compile the regex, if any
    rgx = None
    if S.INCLUDE_REGEX:
        import re
        rgx = re.compile(S.INCLUDE_REGEX)

    # Get candidate items
    candidates = []
    if S.INCLUDE_OBJECT:
        candidates.extend(RDK.ItemList(robolink.ITEM_TYPE_OBJECT))
    if S.INCLUDE_CURVE:
        candidates.extend(RDK.ItemList(robolink.ITEM_TYPE_CURVE))
    if S.INCLUDE_FRAME:
        candidates.extend(RDK.ItemList(robolink.ITEM_TYPE_FRAME))
    if S.INCLUDE_TARGET:
        candidates.extend(RDK.ItemList(robolink.ITEM_TYPE_TARGET))

    # Find the items in the zone
    p_abs = PARENT.PoseAbs().Pos()
    objects = []
    for obj in candidates:
        if obj == PARENT:
            continue

        if not S.INCLUDE_HIDDEN and not obj.Visible():
            continue

        if rgx and not rgx.fullmatch(obj.Name()):
            continue

        if robomath.distance(p_abs, obj.PoseAbs().Pos()) > S.ZONE_RADIUS:
            continue

        objects.append(obj)

    # Delete the objects
    if objects:
        RDK.Render(False)
        RDK.Delete(objects)
        RDK.Render(True)

    return True


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        # When calling this script from a RoboDK Program, add the ID in the program call: DeleteObjectsLoop(2)
        import sys
        id = 0
        if len(sys.argv) > 1:
            id = int(sys.argv[1])

        S = Settings.Settings('Object-Deleter-Settings-' + str(id))
        S.Load()

        DeleteObjects(S=S)


if __name__ == '__main__':
    runmain()
