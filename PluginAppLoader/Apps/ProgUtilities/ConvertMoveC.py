# Convert MoveC to linear movements (MoveL) in the selected program(s).
#
# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

import robolink as rlk
import robodk as rdk

STEP_MM = 1
STEP_DEG = 1
PROG_EXPAND_NAME = "%s Linear"  # ex: MyProg Linear


def getConvertedProg(prog, RDK):
    """Creates a new program from the specified program."""

    # Delete previously generated programs of the same name
    new_prog_name = PROG_EXPAND_NAME % prog.Name()
    new_prog = RDK.Item(new_prog_name, rlk.ITEM_TYPE_PROGRAM)
    if new_prog.Valid() and new_prog.Name() == new_prog_name:
        new_prog.Delete()

    # Create a new program
    new_prog = RDK.AddProgram(new_prog_name)
    if not new_prog.Valid():
        new_prog.Delete()
        raise
    new_prog.setParent(prog.Parent())
    new_prog.ShowInstructions(False)
    return new_prog


def convertProg(prog_from, prog_to, RDK):
    """
    Convert MoveC to linear movements (MoveL) from a program to another program.
    """

    print('Converting program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"')

    # Get the robot parameters of this program
    robot = prog_from.getLink()
    if not robot.Valid():
        RDK.ShowMessage('Link a robot to the program before converting it.')
        return
    last_pose = robot.Pose()  # A MoveC has a 'current' start point and 2 targets.
    dof = len(robot.Joints().tolist())

    inst_count = prog_from.InstructionCount()
    for i in range(inst_count):
        instruction_dict = prog_from.setParam(i)
        print(' - Instruction: ' + str(instruction_dict))

        # Store movements
        if instruction_dict['Type'] == rlk.INS_TYPE_MOVE:
            name, instype, movetype, isjointtarget, pose, joints = prog_from.Instruction(i)
            last_pose = pose

        # Convert MoveC
        elif instruction_dict['Type'] == rlk.INS_TYPE_MOVEC:
            prog_to.RunInstruction(instruction_dict['Name'], rlk.INSTRUCTION_COMMENT)

            # InstructionListJoints converts all movements in the whole program.
            # Create a temporary program with the last pose and the MoveC, get the linear moves.
            prog_temp = getConvertedProg(prog_to, RDK)
            prog_temp.MoveJ(last_pose)
            prog_temp.setParam("Add", instruction_dict)
            status_joint_list = prog_temp.InstructionListJoints(STEP_MM, STEP_DEG)
            prog_temp.Delete()

            # Check the conversion
            if status_joint_list[0] != 'Success':
                raise Exception('Unable to convert MoveC: %s' % status_joint_list[0])
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

            continue

        prog_to.setParam("Add", instruction_dict)

    prog_to.ShowInstructions(True)


def runmain():
    RDK = rlk.Robolink()

    # Get the programs to convert
    programs = list(filter(lambda item: item.Type() == rlk.ITEM_TYPE_PROGRAM, RDK.Selection()))
    if len(programs) < 1:
        RDK.ShowMessage('Please select at least one program.')
        return

    RDK.Render()
    RDK.Render(False)

    for program in programs:
        # Create a new empty program
        exp_prog = getConvertedProg(program, RDK)

        # Convert any sub programs into the new program
        convertProg(program, exp_prog, RDK)

    RDK.Render(True)


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()