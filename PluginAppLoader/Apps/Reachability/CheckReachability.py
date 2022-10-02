#####################################################
## Copyright (C) RoboDK Inc - All Rights Reserved
## Documentation: https://robodk.com/doc/en/RoboDK-API.html
## Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#####################################################
#
# Purpose: Show a preview of reachability around the current TCP point
#

from _config import *
from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox


# Define the ranges to test
def MainAction():
    # Start the RoboDK API
    RDK = Robolink()

    # Load this app settings
    S = Settings()
    S.Load(RDK)

    # Calculate ranges based on input
    Range_TX = eval(S.Range_TX)
    Range_TY = eval(S.Range_TY)
    Range_TZ = eval(S.Range_TZ)
    Range_RX = eval(S.Range_RX)
    Range_RY = eval(S.Range_RY)
    Range_RZ = eval(S.Range_RZ)

    # Reachable display timeouts in milliseconds
    timeout_reachable = 60 * 60 * 1000

    # Non reachable display timeout in milliseconds
    timeout_unreachable = S.Unreachable_Timeout * 1000

    # Get the robot
    robot = RDK.ItemUserPick('Select a robot to test the reachability', ITEM_TYPE_ROBOT)
    if not robot.Valid():
        RDK.ShowMessage("Select a robot to see reachability")
        quit()

    # Get the current pose of the robot:
    robot_pose_ref = robot.Pose()
    robot_tool = robot.PoseTool()
    robot_base = robot.PoseFrame()
    robot_joints = robot.Joints()

    # Iterate through all pose combinations and collect all valid poses
    reachable_poses = []
    unreachable_poses = []
    for tx in Range_TX:
        for ty in Range_TY:
            for tz in Range_TZ:
                for rx in Range_RX:
                    for ry in Range_RY:
                        for rz in Range_RZ:
                            print("Testing translation/rotation: " + str([tx, ty, tz, rx, ry, rz]))
                            pose_add = transl(tx, ty, tz) * rotx(rx * pi / 180) * roty(ry * pi / 180) * rotz(rz * pi / 180)
                            pose_test = robot_pose_ref * pose_add
                            jnts_sol = robot.SolveIK(pose_test, None, robot_tool, robot_base)
                            #print(jnts_sol.list())
                            if len(jnts_sol.list()) <= 1:
                                print("Not reachable")
                                unreachable_poses.append(pose_test)
                                #reachable_poses.append(pose_test)
                            else:
                                print("Reachable")
                                reachable_poses.append(pose_test)

    # Display settings
    Display_Default = 1  # Display "ghost" tools in RoboDK
    Display_Normal = 2
    Display_Green = 3
    Display_Red = 4

    Display_Invisible = 64
    Display_NotActive = 128
    Display_RobotPoses = 256
    Display_RobotPosesRotZ = 512
    Display_Reset = 1048

    Display_Options = 0
    #Display_Options += Display_Invisible # Show invisible tools
    #Display_Options += Display_NotActive # Show non active tools
    if S.ShowRobotPoses:
        Display_Options += Display_RobotPoses  # Show robot joints if reachable
    #Display_Options += Display_RobotPosesRotZ # Show robot joints if reachable (tests rotating around the Z axis)
    #Display_Options += Display_Reset # Reset flag (clears the trace)

    # Force reset
    robot.ShowSequence([])

    # Show reachable poses:
    robot.ShowSequence(reachable_poses, Display_Options + Display_Default, timeout_reachable)

    # Show unreachable poses:
    robot.ShowSequence(unreachable_poses, Display_Options + Display_Red, timeout_unreachable)

    # Example that shows how to wait for the Terminate signal (SIGINT sent by RoboDK uncheck or Ctrl+C)
    run = RunApplication()
    while run.Run():
        import time
        time.sleep(0.2)

    robot.ShowSequence([])  # Force reset


def MainActionOff():
    """Turn off the display of all sequence previews"""
    # Get the list of all robots:
    RDK = Robolink()
    robot_list = RDK.ItemList(ITEM_TYPE_ROBOT)
    for robot in robot_list:
        # Force reset preview
        robot.ShowSequence([])


def runmain():
    # For checkable actions: this will tell RoboDK to never force stop (kill) this app
    #SkipKill()

    # Verify if this is an action that was just unchecked
    if Unchecked():
        MainActionOff()

    else:
        # Checked (or checkable status not applicable)
        MainAction()


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()
