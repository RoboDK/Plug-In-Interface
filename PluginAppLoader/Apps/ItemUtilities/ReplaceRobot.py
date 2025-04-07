# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Replace robot(s) with another robot from the disk (prompts user).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, robodialogs, roboapps
import os

CORRECT_BASE_FRAME = True
UPDATE_PROGRAMS = True  # Will make the UI render


def ReplaceRobots(robots=None):
    """
    Replace robot(s) with another robot from the disk (prompts user).
    """

    # Get the robots: from specified list, user selection (context-menu) or prompt (action)
    RDK = robolink.Robolink()
    if robots is None:
        robots = [x for x in RDK.Selection() if x.Type() in [robolink.ITEM_TYPE_ROBOT]]
        if not robots:
            robots = RDK.ItemUserPick('Select the robot to replace', robolink.ITEM_TYPE_ROBOT)
            if not robots.Valid():
                return
            robots = [robots]
    else:
        robots = [x for x in robots if x.Type() in [robolink.ITEM_TYPE_ROBOT]]
        if not robots:
            return

    # Get the replacement robot
    replacement_path = robodialogs.getOpenFileName(strtitle='Replacing robot. Select new robot...', defaultextension='.robot', filetypes=[('Robot', '.robot')])
    if not replacement_path or not os.path.exists(replacement_path):
        return

    # Turn off render to hide operations and speed-up the process
    RDK.Render(False)

    # Import the replacement once and copy
    # NOTE: Importing a robot adds a frame+robot
    replacement_robot = RDK.AddFile(replacement_path, 0)
    if not replacement_robot.Valid():
        return
    replacement_robot_frame = replacement_robot.Parent()
    replacement_robot_frame.setParam('Tree', 'Hide')
    replacement_robot_frame.setVisible(False)
    replacement_robot.setVisible(False)
    replacement_robot.Copy()

    # Replace robots
    for old_robot in robots:

        old_robot_frame = old_robot.Parent()
        old_robot_tools = old_robot.Childs()
        old_robot_links = old_robot.getLinks(None)
        old_robot_links = sorted(old_robot_links, key=lambda x: x.Type())  # Targets first, then Programs, then Machining

        # Get the current active tool
        robot_tool = old_robot.getLink(robolink.ITEM_TYPE_TOOL)
        if not robot_tool.Valid():
            if old_robot_tools:
                robot_tool = old_robot_tools[0]
            else:
                robot_tool = robomath.eye(4)

        # Save the current robot state, ensure it is in a replicable state
        old_robot.setPoseFrame(old_robot.Parent())
        old_robot.setPoseTool(robot_tool)
        RDK.Update()
        old_robot_pose = old_robot.Pose()
        old_robot.setJoints(old_robot.JointsHome())
        RDK.Update()
        old_robot_home_pose = old_robot.Pose()

        # Update targets (pose of joint targets) in targets, programs, etc.
        for robot_link in old_robot_links:
            link_type = robot_link.Type()
            if link_type == robolink.ITEM_TYPE_TARGET:
                status = robot_link.setParam('Recalculate')
            elif link_type in [robolink.ITEM_TYPE_PROGRAM]:
                status = robot_link.setParam('RecalculateTargets')
            elif UPDATE_PROGRAMS and link_type in [robolink.ITEM_TYPE_MACHINING, robolink.ITEM_TYPE_PROGRAM]:
                valid_instructions, program_time, program_distance, valid_ratio, readable_msg = robot_link.Update()  # Update will trigger a render
                RDK.Render(False)

        # Create the new robot
        new_robot = old_robot_frame.Paste()
        new_robot.setVisible(True)
        new_robot_frame = old_robot_frame
        old_robot_frame.setName(replacement_robot_frame.Name())  # Keeps the Set Ref. links in robot programs valid
        new_robot.setParam("ReorderBefore", str(old_robot.item))
        RDK.setSelection([])

        # Account for robots where the robot base frame is on J2
        robot_pose = old_robot_pose.copy()
        different_robot = False
        if CORRECT_BASE_FRAME:
            old_robot.setJoints(old_robot.JointsHome())  # assume the lower point will be the base
            new_robot.setJoints(new_robot.JointsHome())
            old_robot_bbox = old_robot.setParam('BoundingBox')
            new_robot_bbox = new_robot.setParam('BoundingBox')
            z_offset = old_robot_bbox['min'][2] - new_robot_bbox['min'][2]
            if abs(z_offset) > 1:
                new_robot_frame.setPose(new_robot_frame.Pose().Offset(0, 0, z_offset))
                robot_pose = robot_pose.Offset(0, 0, -z_offset)
                different_robot = True
                RDK.Update()

        # Migrate tools
        for tool in old_robot_tools:
            tool.setParent(new_robot)

        # Restore the robot state
        new_robot.setPoseFrame(new_robot_frame)
        new_robot.setPoseTool(robot_tool)
        new_robot.setJoints(new_robot.JointsHome())
        new_robot_dof = len(new_robot.Joints().tolist())
        RDK.Update()

        # Determine wether its the same robot kinematics (same robot), or a completely different robot
        different_robot = different_robot or (new_robot.Pose() != old_robot_home_pose)

        # Restore original pose, if reachable
        if different_robot:
            robot_joints = new_robot.SolveIK(robot_pose, new_robot.JointsHome(), new_robot.PoseTool(), new_robot.PoseFrame())
            if len(robot_joints.tolist()) == new_robot_dof:
                new_robot.setJoints(robot_joints)
            new_robot.setPose(robot_pose)

        else:
            new_robot.setPose(robot_pose)
        RDK.Update()

        # Restore links, fix joint targets
        for robot_link in old_robot_links:
            try:
                robot_link.setLink(new_robot)
            except:
                continue

        # Update targets (pose of joint targets) in targets, programs, etc.
        for robot_link in old_robot_links:
            link_type = robot_link.Type()
            if link_type == robolink.ITEM_TYPE_TARGET:
                if different_robot:
                    # Update the stored joint configuration for cartesian targets, without changing the pose
                    # NOTE: This uses the active tool, which might not result in the right config if another tool is expected.
                    robot_joints = new_robot.SolveIK(robot_link.PoseWrt(new_robot.Parent()), new_robot.JointsHome(), new_robot.PoseTool(), new_robot.PoseFrame())
                    if len(robot_joints.tolist()) == new_robot_dof:
                        robot_link.setJoints(robot_joints)
                        if not robot_link.isJointTarget():
                            robot_link.setPose(robot_link.Pose())
                    else:
                        print(f'Target {robot_link.Name()} is not reachable')

                if (robot_link.setParam('Recalculate') != '0'):
                    print(f'Error recalculating target {robot_link.Name()}')

            elif link_type in [robolink.ITEM_TYPE_PROGRAM]:
                if (robot_link.setParam('RecalculateTargets') != 'OK'):
                    print(f'Error recalculating program {robot_link.Name()}')

            if UPDATE_PROGRAMS and link_type in [robolink.ITEM_TYPE_MACHINING, robolink.ITEM_TYPE_PROGRAM]:
                valid_instructions, program_time, program_distance, valid_ratio, readable_msg = robot_link.Update()  # Update will trigger a render
                RDK.Render(False)
                if valid_ratio < 1.0:
                    print(f'Error updating program {robot_link.Name()}: {readable_msg}')

        # Remove the old robot
        old_robot.Delete()

    # Delete initial copy
    replacement_robot_frame.Delete()

    # Turn render back on
    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ReplaceRobots()


if __name__ == '__main__':
    runmain()
