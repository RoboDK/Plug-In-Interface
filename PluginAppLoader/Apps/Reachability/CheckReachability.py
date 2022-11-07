# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Show a preview of reachability around the current TCP point.
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
import time

import Settings


def MainAction(RDK=None, S=None):
    """
    Show a preview of reachability around the current TCP point.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load()

    # Get the rotation range
    RANGE_RX = range(1)
    RANGE_RY = range(1)
    RANGE_RZ = range(1)
    if S.ROTATION_ENABLE:
        RANGE_RX = range(S.RANGE_RX[0], S.RANGE_RX[1], S.RANGE_RX[2]) if S.RANGE_RX[2] > 0 and S.RANGE_RX[0] - S.RANGE_RX[1] != 0 else RANGE_RX
        RANGE_RY = range(S.RANGE_RY[0], S.RANGE_RY[1], S.RANGE_RY[2]) if S.RANGE_RY[2] > 0 and S.RANGE_RY[0] - S.RANGE_RY[1] != 0 else RANGE_RY
        RANGE_RZ = range(S.RANGE_RZ[0], S.RANGE_RZ[1], S.RANGE_RZ[2]) if S.RANGE_RZ[2] > 0 and S.RANGE_RZ[0] - S.RANGE_RZ[1] != 0 else RANGE_RZ

    # Get the translation range
    RANGE_TX = range(1)
    RANGE_TY = range(1)
    RANGE_TZ = range(1)
    if S.TRANSLATION_ENABLE:
        RANGE_TX = range(S.RANGE_TX[0], S.RANGE_TX[1], S.RANGE_TX[2]) if S.RANGE_TX[2] > 0 and S.RANGE_TX[0] - S.RANGE_TX[1] != 0 else RANGE_RX
        RANGE_TY = range(S.RANGE_TY[0], S.RANGE_TY[1], S.RANGE_TY[2]) if S.RANGE_TY[2] > 0 and S.RANGE_TY[0] - S.RANGE_TY[1] != 0 else RANGE_RY
        RANGE_TZ = range(S.RANGE_TZ[0], S.RANGE_TZ[1], S.RANGE_TZ[2]) if S.RANGE_TZ[2] > 0 and S.RANGE_TZ[0] - S.RANGE_TZ[1] != 0 else RANGE_RZ

    # Get the robot
    robot = RDK.ItemUserPick('Select a robot to test the reachability', robolink.ITEM_TYPE_ROBOT)
    if not robot.Valid():
        # User canceled, or no robot in the station
        return

    # Get the current pose of the robot:
    robot_pose_ref = robot.Pose()
    robot_tool = robot.PoseTool()
    robot_base = robot.PoseFrame()

    # Iterate through all pose combinations and collect all valid poses
    reachable_poses = []
    unreachable_poses = []
    for tx in RANGE_TX:
        for ty in RANGE_TY:
            for tz in RANGE_TZ:
                for rx in RANGE_RX:
                    for ry in RANGE_RY:
                        for rz in RANGE_RZ:
                            msg = "Testing translation/rotation: " + str([tx, ty, tz, rx, ry, rz])

                            pose_add = robomath.transl(tx, ty, tz) * robomath.rotx(rx * robomath.pi / 180) * robomath.roty(ry * robomath.pi / 180) * robomath.rotz(rz * robomath.pi / 180)
                            pose_test = robot_pose_ref * pose_add
                            jnts_sol = robot.SolveIK(pose_test, None, robot_tool, robot_base)

                            if len(jnts_sol.list()) <= 1:
                                print(msg + " -> Not reachable")
                                unreachable_poses.append(pose_test)
                            else:
                                print(msg + " -> Reachable")
                                reachable_poses.append(pose_test)

    # Preview display options
    display_options = robolink.SEQUENCE_DISPLAY_TOOL_POSES
    if S.PREVIEW_ROBOT_JOINTS:
        display_options += robolink.SEQUENCE_DISPLAY_ROBOT_POSES

    # Show poses
    time_out = 0.
    robot.ShowSequence([])

    if S.PREVIEW_REACHABLE:
        robot.ShowSequence(reachable_poses, display_options + robolink.SEQUENCE_DISPLAY_COLOR_GOOD, S.TIMEOUT_REACHABLE * 1000)
        time_out = max(time_out, S.TIMEOUT_REACHABLE)

    if S.PREVIEW_UNREACHABLE:
        robot.ShowSequence(unreachable_poses, display_options + robolink.SEQUENCE_DISPLAY_COLOR_BAD, S.TIMEOUT_UNREACHABLE * 1000)
        time_out = max(time_out, S.TIMEOUT_UNREACHABLE)

    # Show the poses until the user uncheck the action, or the timeout is reached
    if time_out > 0:
        APP = roboapps.RunApplication()
        start = time.time()
        while APP.Run():
            time.sleep(0.2)
            if time.time() - start > time_out:
                break

    robot.ShowSequence([])


def MainActionOff(RDK=None, S=None):
    """
    Turn off the display of all sequence previews (of all robots).
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load()

    if not S.PREVIEW_CLEAR_ALL:
        return

    robot_list = RDK.ItemList(robolink.ITEM_TYPE_ROBOT)
    for robot in robot_list:
        robot.ShowSequence([])


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """
    if roboapps.Unchecked():
        MainActionOff()
    else:
        MainAction()


if __name__ == '__main__':
    runmain()
