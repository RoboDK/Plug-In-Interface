# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file let's you control your robot with an Xbox One Controller as a RoboDK checkable App.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robolink import *  # API to communicate with RoboDK
from robodk import *
from _tools import *  # "Apps" tools for RoboDK. Can be reused with other apps.

import_install('inputs')
from inputs import get_gamepad
from inputs import devices


def MainAction():

    print('Press and hold X (X axis), Y (Z axis) or B (Z axis) to select an axis.')
    print('Use the D-pad up or down to move the robot along the selected axis.')
    print('Use the D-pad left or right to increase/decrease the steps.')
    print('Press the left joystick to toggle between translation (default) and rotation.')
    print('Press the right joystick to toggle between MoveJ (default) and MoveL.')
    print('Press both bumpers to Home.')
    print('Use the right trigger to engage the safeguard.')
    print('To run on the real robot: RoboDK->Connect->Connect robot->Connect.')
    print('Ensure the robot speed is adequate: RoboDK->Right-click your robot->Options->Parameters.')

    # Global flag for debugging. Setting this to false will never run on robot.
    RUN_ON_ROBOT = True

    # You might want to change this parameters based on your needs.

    # Robot speeds
    MAX_LINEAR_SPEED = 25.0  # mm/s
    MAX_JOINT_SPEED = 20.0  # deg/s

    # Linear move
    LINEAR_STEPS_MAX = 50  # mm/step
    LINEAR_STEPS_MIN = 0.5  # mm/step
    LINEAR_STEPS_INIT = 10  # mm/step

    # Angular move
    ANGULAR_STEPS_MAX = 30  # deg/step
    ANGULAR_STEPS_MIN = 1  # deg/step
    ANGULAR_STEPS_INIT = 5  # deg/step
    DEG_TO_RAD = pi / 180.0

    # Steps
    STEPS_INC_FACTOR = 0.25  # % of step increase/decrease

    # Simulation parameters
    move_steps = {
        "Translate": LINEAR_STEPS_INIT,
        "Rotate": ANGULAR_STEPS_INIT,
    }

    move_type = {
        "Translate": True,
        "Rotate": False,
    }

    robot_move_type = {
        "MoveJ": False,
        "MoveL": True,
    }

    # Controller buttons, as defined here: https://support.xbox.com/en-CA/help/hardware-network/controller/xbox-one-wireless-controller
    keys = {
        "A": False,
        "B": False,
        "X": False,
        "Y": False,
        "Left_Bumper": False,
        "Right_Bumper": False,
        "Left_Trigger": False,
        "Right_Trigger": False,
        "Left_Thumb": False,
        "Right_Thumb": False,
        "View": False,
        "Menu": False,
    }
    keys_prev = keys.copy()

    triggers = {
        "Left_Trigger_A": 0,
        "Right_Trigger_A": 0,
    }
    triggers_prev = triggers.copy()

    dpad = {
        "Left": False,
        "Right": False,
        "Up": False,
        "Down": False,
    }
    dpad_prev = dpad.copy()

    stick = {
        "Left_A": 0,
        "Right_A": 0,
        "Up_A": 0,
        "Down_A": 0,
        "Pushed": False,
    }
    left_stick = stick.copy()
    right_stick = stick.copy()
    left_stick_prev = left_stick.copy()
    right_stick_prev = right_stick.copy()

    RDK = Robolink()

    # Get the controller
    gamepads = devices.gamepads
    if len(gamepads) < 1:
        RDK.ShowMessage("No controller found. Connect a controller and try again.")
        quit(0)
    gamepad = gamepads[0]
    print('Using controller: %s' % gamepad.name)

    # Get a robot. Will not ask the user if there's only one.
    robot = RDK.ItemUserPick("Select a robot", ITEM_TYPE_ROBOT)
    if not robot.Valid():
        RDK.ShowMessage("No robot in the station. Load a robot first, then run this program.")
        quit(0)
    print('Using robot: %s' % robot.Name())
    robot.setPoseFrame(robot.PoseFrame())
    robot.setPoseTool(robot.PoseTool())
    robot.setSpeed(MAX_LINEAR_SPEED, MAX_JOINT_SPEED)

    # Ensure we are in a simulated environnement
    if RDK.RunMode() != RUNMODE_SIMULATE:
        RUN_ON_ROBOT = False

    if RUN_ON_ROBOT:
        # Check if the robot is already connected
        status, status_msg = robot.ConnectedState()
        if (status == ROBOTCOM_READY) and not ShowMessageYesNo("You are about to control the connected robot using the controller.\n\nWould you like to run in simulation mode instead?", ""):
            RDK.setRunMode(RUNMODE_RUN_ROBOT)

    # Retrieve the degrees of freedom or axes (num_dofs = 6 for a 6 axis robot)
    num_dofs = len(robot.JointsHome().list())

    run = RunApplication()
    while run.Run():
        # At the begining in case of "continue"
        keys_prev = keys.copy()
        triggers_prev = triggers.copy()
        dpad_prev = dpad.copy()
        left_stick_prev = left_stick.copy()
        right_stick_prev = right_stick.copy()

        # Check if the gamepad is still present
        gamepads = devices.gamepads
        if len(gamepads) < 1:
            RDK.ShowMessage("Controller lost. Connect a controller and try again.")
            quit(0)

        # Ensure robot is still connected
        if RDK.RunMode() == RUNMODE_RUN_ROBOT:
            status, status_msg = robot.ConnectedState()
            if status < ROBOTCOM_READY:
                # Stop if the connection was lost
                RDK.ShowMessage("Robot connection lost. Connect a robot and try again.")
                quit(0)

        # Read controller inputs
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":

                # X/Y/A/B Buttons, {0, 1}
                if event.code == "BTN_WEST":
                    keys["X"] = bool(event.state)
                elif event.code == "BTN_NORTH":
                    keys["Y"] = bool(event.state)
                elif event.code == "BTN_SOUTH":
                    keys["A"] = bool(event.state)
                elif event.code == "BTN_EAST":
                    keys["B"] = bool(event.state)

                # Bumpers, {0, 1}
                elif event.code == "BTN_TR":
                    keys["Right_Bumper"] = bool(event.state)
                elif event.code == "BTN_TL":
                    keys["Left_Bumper"] = bool(event.state)

                # Joystick down, {0, 1}
                elif event.code == "BTN_THUMBL":
                    left_stick["Pushed"] = bool(event.state)
                elif event.code == "BTN_THUMBR":
                    right_stick["Pushed"] = bool(event.state)

                # Others, {0, 1}
                elif event.code == "BTN_SELECT":
                    keys["View"] = bool(event.state)
                elif event.code == "BTN_START":
                    keys["Menu"] = bool(event.state)

                else:
                    print(event.ev_type, event.code, event.state)

            elif event.ev_type == "Absolute":

                # D-Pad, {-1, 0, 1}
                if event.code == "ABS_HAT0X":
                    dpad["Left"] = bool(-min(0, event.state))  # -1, 0
                    dpad["Right"] = bool(max(0, event.state))  # 0, 1
                elif event.code == "ABS_HAT0Y":
                    dpad["Up"] = bool(-min(0, event.state))  # -1, 0
                    dpad["Down"] = bool(max(0, event.state))  # 0, 1

                # Sticks, {-32768, 0, 32767}
                # Left stick
                elif event.code == "ABS_X":  # Left Joystick L/R
                    left_stick["Left_A"] = max(0, event.state)
                    left_stick["Right_A"] = min(event.state, 0)
                elif event.code == "ABS_Y":  # Left Joystick U/D
                    left_stick["Up_A"] = max(0, event.state)
                    left_stick["Down_A"] = min(event.state, 0)

                # Right stick
                elif event.code == "ABS_RX":  # Right Joystick L/R
                    right_stick["Left_A"] = max(0, event.state)
                    right_stick["Right_A"] = min(event.state, 0)
                elif event.code == "ABS_RY":  # Right Joystick U/D
                    right_stick["Up_A"] = max(0, event.state)
                    right_stick["Down_A"] = min(event.state, 0)

                # Triggers {0, 255}
                elif event.code == "ABS_Z":  # Left trigger
                    triggers["Left_Trigger_A"] = max(0, event.state)
                elif event.code == "ABS_RZ":  # Right trigger
                    triggers["Right_Trigger_A"] = max(0, event.state)

                else:
                    print(event.ev_type, event.code, event.state)

            elif event.ev_type != "Sync":
                print(event.ev_type, event.code, event.state)

        # Process the inputs

        # Home
        if keys["Left_Bumper"] and keys["Right_Bumper"] and triggers["Right_Trigger_A"] >= 235:
            RDK.ShowMessage('Homing..', False)
            home_jts = robot.JointsHome()
            robot.MoveJ(home_jts)
            continue

        # Move type
        if move_type["Translate"] == move_type["Rotate"]:  # In case someone breaks the initial settings
            move_type["Translate"] = not move_type["Rotate"]

        if not left_stick_prev["Pushed"] and left_stick["Pushed"]:  # Only change on "rising edge"
            move_type["Translate"] = not move_type["Translate"]
            move_type["Rotate"] = not move_type["Rotate"]
            if move_type["Translate"]:
                RDK.ShowMessage('Switched to translation mode', False)
            else:
                RDK.ShowMessage('Switched to rotation mode', False)
        print(move_type)

        # Robot move type
        if robot_move_type["MoveJ"] == robot_move_type["MoveL"]:  # In case someone breaks the initial settings
            robot_move_type["MoveJ"] = not robot_move_type["MoveL"]

        if not right_stick_prev["Pushed"] and right_stick["Pushed"]:  # Only change on "rising edge"
            robot_move_type["MoveJ"] = not robot_move_type["MoveJ"]
            robot_move_type["MoveL"] = not robot_move_type["MoveL"]
            if robot_move_type["MoveJ"]:
                RDK.ShowMessage('Switched to MoveJ mode', False)
            else:
                RDK.ShowMessage('Switched to MoveL mode', False)
        print(robot_move_type)

        # Move steps
        dpad_sign = 0
        if not dpad_prev["Right"] and dpad["Right"]:  # Only change on "rising edge"
            dpad_sign = 1.0 + STEPS_INC_FACTOR
        if not dpad_prev["Left"] and dpad["Left"]:  # Only change on "rising edge"
            dpad_sign = 1.0 / (1.0 + STEPS_INC_FACTOR)

        if dpad_sign != 0:
            if move_type["Rotate"]:
                move_steps["Rotate"] = min(ANGULAR_STEPS_MAX, max(ANGULAR_STEPS_MIN, move_steps["Rotate"] * dpad_sign))
                RDK.ShowMessage('Rotation steps (deg): %.2f' % move_steps["Rotate"], False)
            else:
                move_steps["Translate"] = min(LINEAR_STEPS_MAX, max(LINEAR_STEPS_MIN, move_steps["Translate"] * dpad_sign))
                RDK.ShowMessage('Translation steps (mm): %.2f' % move_steps["Translate"], False)
        print(move_steps)

        # Translation / Rotation
        dpad_move = 0
        if not dpad_prev["Up"] and dpad["Up"]:  # Only change on "rising edge"
            dpad_move = 1
        if not dpad_prev["Down"] and dpad["Down"]:  # Only change on "rising edge"
            dpad_move = -1

        move_mtx = [0, 0, 0]
        if keys["X"]:  # X axis
            move_mtx[0] = dpad_move
        if keys["Y"]:  # Y axis
            move_mtx[1] = dpad_move
        if keys["B"]:  # Z axis
            move_mtx[2] = dpad_move

        # Make sure that a movement command is specified
        if norm(move_mtx) <= 0:
            continue
        print(move_mtx)

        # Calculate the new robot position
        x, y, z, rx, ry, rz = 0, 0, 0, 0, 0, 0
        if move_type["Translate"]:
            x, y, z = mult3(move_mtx, move_steps["Translate"])
        elif move_type["Rotate"]:
            rx, ry, rz = mult3(move_mtx, move_steps["Rotate"] * DEG_TO_RAD)
        new_pose = robot.Pose() * transl(x, y, z) * rotx(rx) * roty(ry) * rotz(rz)

        # Calculate the new robot joints
        new_robot_joints = robot.SolveIK(new_pose)
        if len(new_robot_joints.tolist()) < num_dofs:
            RDK.ShowMessage('No robot solution! The new position is too far, out of reach or close to a singularity.', False)
            continue

        # Get the robot joints
        robot_joints = robot.Joints()

        # Get the robot configuration (robot joint state)
        robot_config = robot.JointsConfig(robot_joints).list()

        # Calculate the robot configuration for the new joints
        new_robot_config = robot.JointsConfig(new_robot_joints).list()

        if robot_config != new_robot_config:
            RDK.ShowMessage("Warning!\n\nRobot configuration changed. This can lead to unexpected movements! Please move the robot through RoboDK or try another command.")
            print(robot_config)
            print(new_robot_config)
            continue

        # Safe guard
        if triggers["Right_Trigger_A"] < 235:
            RDK.ShowMessage('Please press the safety trigger!', False)
            continue

        # Move the robot joints to the new position
        try:
            if robot_move_type["MoveJ"]:
                robot.MoveJ(new_pose)
            elif robot_move_type["MoveL"]:
                robot.MoveL(new_pose)
        except TargetReachError as e:
            RDK.ShowMessage('Warning!\n\nTarget unreachable. Try using MoveJ or another command.', True)
            print(e)
            continue


def runmain():
    # Verify if this is an action that was just unchecked
    if Unchecked():
        quit(0)
    else:
        # Checked (or checkable status not applicable)
        MainAction()


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()
