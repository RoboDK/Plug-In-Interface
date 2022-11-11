# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Convert MoveC to linear movements (MoveL) in the selected program(s).
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


def ConvertMoveC(RDK=None, S=None, progs=None):
    """
    Convert circular (MoveC) to linear (MoveL) instructions in program(s).
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get program(s) to convert..
    if progs is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            # ..or user selection
            prog = RDK.ItemUserPick('Select the program to convert', robolink.ITEM_TYPE_PROGRAM)
            if not prog.Valid():
                return
            progs = [prog]
    else:
        # ..as provided
        progs = [x for x in progs if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            return

    # Convert programs
    for prog_from in progs:

        RDK.Render(False)

        # Get the robot parameters of this program
        robot = prog_from.getLink(robolink.ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = RDK.ItemUserPick("Select the program's robot", robolink.ITEM_TYPE_ROBOT)
            if not robot.Valid():
                RDK.ShowMessage(prog_from.Name() + ': a robot is required to convert MoveC to MoveL(s)')
                continue
            prog_from.setRobot(robot)

        last_pose = robot.Pose()  # A MoveC has a 'current' start point and 2 targets.
        dof = len(robot.Joints().tolist())

        # Create the converted program
        prog_to = RDK.AddProgram(f"{prog_from.Name()} {S.CONVERT_MOVEC_PROG_SUFFIX.strip()}", robot)
        prog_to.setParent(prog_from.Parent())
        prog_to.ShowInstructions(False)
        print('Converting program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"')

        # Parse instructions
        inst_count = prog_from.InstructionCount()
        for i in range(inst_count):
            instruction_dict = prog_from.setParam(i)

            # Store movements
            if instruction_dict['Type'] == robolink.INS_TYPE_MOVE:
                name, instype, movetype, isjointtarget, pose, joints = prog_from.Instruction(i)
                last_pose = pose

            # Convert MoveC
            elif instruction_dict['Type'] == robolink.INS_TYPE_MOVEC:
                prog_to.RunInstruction(instruction_dict['Name'], robolink.INSTRUCTION_COMMENT)

                # InstructionListJoints converts all movements in the whole program.
                # Create a temporary program with the last pose and the MoveC, get the linear moves.
                prog_temp = RDK.AddProgram(f"{prog_from.Name()} {S.CONVERT_MOVEC_PROG_SUFFIX.strip()} [TEMP]", robot)
                prog_temp.MoveJ(last_pose)
                prog_temp.setParam("Add", instruction_dict)
                status_joint_list = prog_temp.InstructionListJoints(S.CONVERT_MOVEC_STEP_MM, S.CONVERT_MOVEC_STEP_DEG)
                prog_temp.Delete()

                # Check the conversion
                if status_joint_list[0] != 'Success':
                    RDK.ShowMessage('Unable to convert MoveC: %s' % status_joint_list[0])
                    break

                joint_list = status_joint_list[1]
                njoints = joint_list.size(1)
                if njoints < 2:
                    raise Exception('Invalid program!')
                joints_list = joint_list[:dof, :]

                # Add the MoveL to new program
                # This can take a while if we render, inform the user.
                RDK.ShowMessage('Processing %i points, please wait...' % njoints, False)
                for i in range(njoints):
                    prog_to.MoveL(joints_list[:, i])
                    last_pose = joints_list[:, i]
                continue

            prog_to.setParam("Add", instruction_dict)

        prog_to.setParam("RecalculateTargets")

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ConvertMoveC()


if __name__ == '__main__':
    runmain()
