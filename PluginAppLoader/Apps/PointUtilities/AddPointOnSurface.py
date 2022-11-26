# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Click an object's surface to add a point at that location.
# Points can be added as long as this action is running.
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


def ActionChecked():
    """
    Click an object's surface to add a point at that location.
    Points can be added as long as this action is running.
    """

    RDK = robolink.Robolink()

    S = Settings.Settings()
    S.Load(RDK)

    # Clear the selection so that we get a 'rising edge'
    RDK.setSelection([])

    APP = roboapps.RunApplication()
    while APP.Run():

        # Get the point under the mouse
        selected_object, feature_type, _, _, _ = RDK.GetPoints(robolink.FEATURE_HOVER_OBJECT)
        if feature_type != robolink.FEATURE_SURFACE or not selected_object.Valid() or selected_object.Type() not in [robolink.ITEM_TYPE_OBJECT]:
            continue

        # Capture user-click
        if selected_object in RDK.Selection():

            # Get the mouse point on surface
            point_mouse, _ = selected_object.GetPoints(robolink.FEATURE_SURFACE)
            if not point_mouse:
                continue

            # Clear the selection so that we get a 'rising edge'
            RDK.setSelection([])

            # Get the mouse position and normal
            xyzijk = point_mouse[0][0:6]
            xyz = xyzijk[0:3]
            ijk = xyzijk[3:6]

            # Get the mouse position on the surface of the object
            pose_offset = selected_object.Pose()  #selected_object.Parent().PoseAbs().inv() * selected_object.PoseAbs()
            xyz_offset = pose_offset * xyz
            ijk_offset = pose_offset[0:3, 0:3] * ijk
            xyzijk = xyz_offset + ijk_offset

            # Add the point to the clicked object, or create a new object
            point_object = selected_object.AddPoints([xyzijk], S.ADD_TO_OBJECT, robolink.PROJECTION_NONE)
            if not S.ADD_TO_OBJECT:
                x, y, z, i, j, k = xyzijk
                point_object.setName(f"{selected_object.Name()} P[{x:.2f},{y:.2f},{z:.2f},{i:.2f},{j:.2f},{k:.2f}]")


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ActionChecked()


if __name__ == '__main__':
    runmain()