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
    replacement_robot_frame.Copy()

    # Replace robots
    for old_robot in robots:
        old_robot_frame = old_robot.Parent()
        old_robot_tools = old_robot.Childs()
        old_robot_links = old_robot.getLinks(None)

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
        robot_pose = old_robot.Pose()

        # Create the new robot
        new_robot_frame = old_robot_frame.Parent().Paste()
        new_robot = new_robot_frame.Childs()[0]
        RDK.setSelection([])

        # Restore the original robot base frame
        new_robot_frame.setPose(old_robot_frame.Pose())
        RDK.Update()

        # Account for robots where the robot base frame is on J2
        if CORRECT_BASE_FRAME:
            old_robot.setJoints(old_robot.JointsHome())  # assume the lower point will be the base
            new_robot.setJoints(new_robot.JointsHome())
            old_robot_bbox = old_robot.setParam('BoundingBox')
            new_robot_bbox = new_robot.setParam('BoundingBox')
            z_offset = old_robot_bbox['min'][2] - new_robot_bbox['min'][2]
            if abs(z_offset) > 1:
                new_robot_frame.setPose(new_robot_frame.Pose().Offset(0, 0, z_offset))
                robot_pose = robot_pose.Offset(0, 0, -z_offset)
                RDK.Update()

        # Migrate tools
        for tool in old_robot_tools:
            tool.setParent(new_robot)

        # Migrate items under the base frame
        for child in [x for x in old_robot_frame.Childs() if x != old_robot]:
            child.setParentStatic(new_robot_frame)  # Static is important if we moved the robot base frame

        # Remove the old robot
        old_robot_frame.Delete()

        # Restore the pose
        new_robot.setPoseFrame(new_robot_frame)
        new_robot.setPoseTool(robot_tool)
        #new_robot.setJoints(new_robot.JointsHome())
        RDK.Update()

        robot_joints = new_robot.SolveIK(robot_pose, new_robot.JointsHome(), new_robot.PoseTool(), new_robot.PoseFrame())
        if len(robot_joints.tolist()) == len(new_robot.Joints().tolist()):
            new_robot.setJoints(robot_joints)
        else:
            new_robot.setPose(robot_pose)
        RDK.Update()

        # Restore links
        for robot_link in old_robot_links:
            try:
                robot_link.setLink(new_robot)
            except:
                pass

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