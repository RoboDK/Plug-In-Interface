# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Merge selected program(s) into a new common program.
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


def MergePrograms(RDK=None, S=None, progs=None):
    """
    Merge instructions from a list of programs to another program.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get programs to merge..
    if progs is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
    else:
        # ..as provided
        progs = [x for x in progs if x.Type() == robolink.ITEM_TYPE_PROGRAM]

    if len(progs) < 2:
        RDK.ShowMessage('Please select at least two programs to merge.')
        return

    RDK.Render(False)

    # Get the robot parameters of this program
    robot = progs[0].getLink(robolink.ITEM_TYPE_ROBOT)
    if not robot.Valid():
        robot = RDK.ItemUserPick("Select the program's robot", robolink.ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = 0

    # Create a new empty program to merge into
    prog_to = RDK.AddProgram(f"{' '.join([x.Name() for x in progs])} {S.MERGE_PROG_SUFFIX.strip()}", robot)

    # Merge programs into the new program
    for prog_from in progs:
        RDK.ShowMessage('Merging program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"', False)

        inst_count = prog_from.InstructionCount()
        for i in range(inst_count):
            instruction_dict = prog_from.setParam(i)
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
        MergePrograms()


if __name__ == "__main__":
    runmain()