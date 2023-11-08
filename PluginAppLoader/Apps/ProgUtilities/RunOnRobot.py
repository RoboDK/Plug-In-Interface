# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Toggle Run on Robot for programs, including their sub-programs.
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


def RunOnRobots(RDK=None, S=None, progs=None):
    """
    Toggle Run on Robot for programs, including their sub-programs.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get program(s) to process..
    if progs is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            # ..or user selection
            prog = RDK.ItemUserPick('Select the program to run on robot', robolink.ITEM_TYPE_PROGRAM)
            if not prog.Valid():
                return
            progs = [prog]
    else:
        # ..as provided
        progs = [x for x in progs if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            return

    RDK.Render(False)

    for prog in progs:
        robot = prog.getLink(robolink.ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = RDK.ItemUserPick("Select the program's robot", robolink.ITEM_TYPE_ROBOT)
            if not robot.Valid():
                continue
            prog.setRobot(robot)

        run_type = robolink.PROGRAM_RUN_ON_SIMULATOR if prog.RunType() == robolink.PROGRAM_RUN_ON_ROBOT else robolink.PROGRAM_RUN_ON_ROBOT
        RunOnRobot(RDK, S, prog, robot_root=robot, run_type=run_type)


def RunOnRobot(RDK=None, S=None, prog_from=None, prog_root=None, robot_root=None, run_type=None, progs: set = None):
    """
    Toggle Run on Robot for programs, including their sub-programs.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get program to procress..
    if prog_from is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs or len(progs) != 1:
            prog_from = RDK.ItemUserPick('Select the program to run on robot', robolink.ITEM_TYPE_PROGRAM)
        else:
            prog_from = progs[0]

    if not prog_from.Valid():
        return

    # Keep track of the programs we already parsed
    if progs is None:
        progs = set()

    if prog_from in progs:
        return

    # Get the robot of this program, as we only want to activate run on robot for this robot
    robot = prog_from.getLink(robolink.ITEM_TYPE_ROBOT)
    if not robot.Valid():
        robot = RDK.ItemUserPick("Select the program's robot", robolink.ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = 0

    # Ensure we avoid loopholes
    if prog_root == prog_from:
        raise Exception("Attempting to process %s, which recursively calls itself in %s" % (prog_root.Name(), prog_from.Name()))

    # Inline any sub programs into the new program
    if robot == robot_root:
        prog_from.setRunType(run_type)

    for i in range(prog_from.InstructionCount()):
        instruction_dict = prog_from.setParam(i)

        if instruction_dict['Type'] == robolink.INS_TYPE_CODE and instruction_dict['Behavior'] == 0:
            sub_prog = RDK.Item(instruction_dict['Code'], robolink.ITEM_TYPE_PROGRAM)
            if sub_prog.Valid():
                RunOnRobot(RDK, S, sub_prog, prog_from if prog_root is None else prog_root, robot_root, run_type, progs)

    progs.add(prog_from)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        RunOnRobots()


if __name__ == '__main__':
    runmain()
