# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Attach the camera (3D view point) to the currently selected item.
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


def AttachCamera(RDK=None, S=None):
    """
    Attach the camera (3D view point) to the currently selected item.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    item2station_pose = robomath.eye(4)
    view_pose_last = robomath.eye(4)
    last_item = None

    APP = roboapps.RunApplication()
    while APP.Run():

        # Sync rendering with this App
        RDK.Render(False)

        # Retrieve user selection
        selected_items = RDK.Selection()
        if len(selected_items) <= 0:
            last_item = None
            continue

        # Use the first selected item to attach the camera
        item = selected_items[0]

        # Prevent selecting programs or instructions or anything that doesn't move
        if item.type in [robolink.ITEM_TYPE_ROBOT, robolink.ITEM_TYPE_TOOL, robolink.ITEM_TYPE_FRAME, robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_TARGET]:
            item_pose = item.PoseWrt(RDK.ActiveStation())  # Selected item pose with respect to the station reference (this works for robots too!)
            item2station_pose = item_pose.inv()

            if last_item != item:
                # If it is the first time we select this item: update the relationship camera 2 item pose
                view_pose = RDK.ViewPose()  # View Pose (camera pose with respect to the station reference)
                camera2item_pose = (item2station_pose * view_pose.inv()).inv()
                msg = 'Camera attached to %s' % item.Name()
                print(msg)
                RDK.ShowMessage(msg, False)
                last_item = item

            else:
                # Calculate the new view pose and update it
                if S.CAMERA_RELATIVE:
                    view_pose = camera2item_pose * item2station_pose
                else:
                    view_pose = (item_pose * robomath.rotx(-robomath.pi)).inv()

                # Only update if the view pose changed
                if view_pose != view_pose_last:
                    view_pose_last = view_pose
                    RDK.setViewPose(view_pose)

    # Action unchecked, turn rendering back on
    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        AttachCamera()


if __name__ == '__main__':
    runmain()
