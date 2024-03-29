# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Convert point(s) to target(s) suing the normal of the point as the Z axis.
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

import Settings


def PointToTarget(RDK=None, S=None, objects=None):
    """
    Convert point(s) to target(s) suing the normal of the point as the Z axis.
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    if objects is None:
        objects = [x for x in RDK.Selection() if x.type in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            objects = RDK.ItemUserPick('Select the points to convert', robolink.ITEM_TYPE_OBJECT)
            if not objects.Valid():
                return
            objects = [objects]
    else:
        objects = [x for x in objects if x.type in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            return

    RDK.Render(False)

    for object_item in objects:

        points = object_item.GetPoints(robolink.FEATURE_POINT)[0]
        if not points:
            continue

        for i, point in enumerate(points):
            xyz = point[:3]
            ijk = [0, 0, 1]
            if len(point) > 3:
                ijk = point[3:6]

            if S.TARGET_INVERSE_NORMAL:
                ijk = robomath.mult3(ijk, -1)

            pose = robomath.point_Zaxis_2_pose(xyz, ijk)
            target = RDK.AddTarget(f'{object_item.Name()} {i+1}', object_item.Parent())
            target.setPose(pose)

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        PointToTarget()


if __name__ == '__main__':
    runmain()