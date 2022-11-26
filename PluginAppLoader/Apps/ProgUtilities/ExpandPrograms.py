# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Expand program calls of the selected program(s) into new program(s).
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


def ExpandPrograms(RDK=None, S=None, progs=None):
    """
    Inline all instructions from a program to another program for every program provided.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get program(s) to expand..
    if progs is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            # ..or user selection
            prog = RDK.ItemUserPick('Select the program to expand', robolink.ITEM_TYPE_PROGRAM)
            if not prog.Valid():
                return
            progs = [prog]
    else:
        # ..as provided
        progs = [x for x in progs if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            return

    for prog in progs:
        ExpandProgram(RDK, S, prog)


def ExpandProgram(RDK=None, S=None, prog_from=None, prog_to=None, prog_root=None):
    """
    Inline all instructions from a program to another program.
    For recursive calls only, the initial root program must be provided to avoid loopholes.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get program to expand..
    if prog_from is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs or len(progs) != 1:
            prog_from = RDK.ItemUserPick('Select the program to expand', robolink.ITEM_TYPE_PROGRAM)
        else:
            prog_from = progs[0]

    if not prog_from.Valid():
        return

    RDK.Render(False)

    # Get the robot parameters of this program
    robot = prog_from.getLink(robolink.ITEM_TYPE_ROBOT)
    if not robot.Valid():
        robot = RDK.ItemUserPick("Select the program's robot", robolink.ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = 0

    # Create a new empty program to expand into
    if prog_to is None:
        prog_to = RDK.AddProgram(f"{prog_from.Name()} {S.EXPAND_PROG_SUFFIX.strip()}", robot)
        prog_to.setParent(prog_from.Parent())

    # Ensure we avoid loopholes
    if S.EXPAND_RECURSIVELY and prog_root == prog_from:
        raise Exception("Attempting to expand %s, which recursively calls itself in %s" % (prog_root.Name(), prog_to.Name()))

    # Inline any sub programs into the new program
    RDK.ShowMessage('Expanding program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"', False)
    inst_count = prog_from.InstructionCount()
    for i in range(inst_count):
        instruction_dict = prog_from.setParam(i)

        if instruction_dict['Type'] == robolink.INS_TYPE_CODE and S.EXPAND_RECURSIVELY:
            sub_prog = RDK.Item(instruction_dict['Code'], robolink.ITEM_TYPE_PROGRAM)
            if sub_prog.Valid() and instruction_dict['Name'].startswith('Call'):
                ExpandProgram(RDK, S, sub_prog, prog_to, prog_from if prog_root is None else prog_root)
                continue  # continue, as program calls to non-program are valid

        prog_to.setParam("Add", instruction_dict)

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ExpandPrograms()


if __name__ == '__main__':
    runmain()
