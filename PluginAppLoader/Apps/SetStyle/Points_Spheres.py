# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Paint points as spheres (white by default) for specified objects.
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

import Settings


def PaintPointsAsSpheres(RDK=None, S=None, objects=None):
    """
    Paint points as spheres (white by default) for specified objects.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load()

    # Get object(s) to color..
    if objects is None:
        # ..from tree selection
        objects = [x for x in RDK.Selection() if x.Type() in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
        if not objects:
            # ..or user selection
            curve = RDK.ItemUserPick('Select the curve', RDK.ItemList(robolink.ITEM_TYPE_OBJECT) + RDK.ItemList(robolink.ITEM_TYPE_CURVE))
            if not curve.Valid():
                return
            objects = [curve]
    else:
        # ..as provided
        objects = [x for x in objects if x.Type() in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
        if not objects:
            return

    for obj in objects:
        # Display as a sphere (size,rings):
        r, g, b, a = S.POINTS_SPHERE_COLOR
        obj.setParam('Display', f'PARTICLE=SPHERE({S.POINTS_SPHERE_SIZE},{S.POINTS_SPHERE_RINGS}) COLOR={Settings.rgba2hex(r,g,b,a)}')


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        PaintPointsAsSpheres()


if __name__ == '__main__':
    runmain()
