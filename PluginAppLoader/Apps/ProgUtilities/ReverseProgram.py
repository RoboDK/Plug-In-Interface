# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Reverse program(s) into new program(s), taking motion type into account.
#
# For instance:
# Set Ref, Set Tool, Set Speed(A), MoveJ(A), MoveL(B), Set Speed(B), MoveJ(C), MoveL(A)
#
# Becomes:
# Set Ref, Set Tool, Set Speed (B), MoveL(A), MoveL(C), MoveJ(B), Set Speed(A), MoveL(A)
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
from collections import OrderedDict

import Settings


def ReversePrograms(RDK=None, S=None, progs=None):
    """
    Reverse program(s) into new program(s), taking motion type into account.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get program(s) to recover..
    if progs is None:
        # ..from tree selection
        progs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            # ..or user selection
            prog = RDK.ItemUserPick('Select the program to recover', robolink.ITEM_TYPE_PROGRAM)
            if not prog.Valid():
                return
            progs = [prog]
    else:
        # ..as provided
        progs = [x for x in progs if x.Type() == robolink.ITEM_TYPE_PROGRAM]
        if not progs:
            return

    # Recover programs
    for prog_from in progs:

        RDK.Render(False)

        # Get the robot parameters of this program
        robot = prog_from.getLink(robolink.ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = RDK.ItemUserPick(f"Select {prog_from.Name()}'s robot", robolink.ITEM_TYPE_ROBOT)
            if not robot.Valid():
                robot = 0

        # Create the recovered program
        prog_to = RDK.AddProgram(f"{prog_from.Name()} {S.REVERSED_PROG_SUFFIX.strip()}", robot)
        prog_to.setParent(prog_from.Parent())
        print('Reversing program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"')

        def get_instructions(prog):
            """Return the instructions of a program, indexed by instruction ID."""
            insts = {}
            for i in range(prog.InstructionCount()):
                insts[i] = prog.setParam(i)
            return insts

        instructions = get_instructions(prog_from)

        # Find instructions that applies to subsequent commands
        # For instance, Set Ref. must be before the MoveLs even the MoveLs are in reverse orders
        blocks = OrderedDict()
        blocks['FRAME'] = sorted(set(i for i in instructions if instructions[i]['Type'] in [
            robolink.INS_TYPE_CHANGEFRAME,
        ]), reverse=True)
        blocks['TOOL'] = sorted(set(i for i in instructions if instructions[i]['Type'] in [
            robolink.INS_TYPE_CHANGETOOL,
        ]), reverse=True)
        blocks['SPEED'] = sorted(set(i for i in instructions if instructions[i]['Type'] in [
            robolink.INS_TYPE_CHANGESPEED,
        ]), reverse=True)
        blocks['ROUNDING'] = sorted(set(i for i in instructions if instructions[i]['Type'] in [
            robolink.INS_TYPE_ROUNDING,
        ]), reverse=True)

        blocks_remaining = sorted([y for x in blocks.values() for y in x], reverse=True)
        blocks_index = set(blocks_remaining)

        move_inst_prev = None

        for i in reversed(range(prog_from.InstructionCount())):

            # Add block instructions
            if blocks_remaining:
                for block_type, ibs in blocks.items():
                    while ibs and i <= ibs[0]:
                        ibs.pop(0)

                    while ibs and ibs[0] in blocks_remaining and ibs[0] < i:
                        prog_to.setParam("Add", instructions[ibs[0]])
                        blocks_remaining.remove(ibs[0])

            # Shift movement commands
            if instructions[i]['Type'] in [robolink.INS_TYPE_MOVE]:
                if move_inst_prev is None:
                    # This is the first movement command. Add as-is.
                    # Preferably, this should be a MoveJ or removed by the user after reversion
                    move_inst_prev = instructions[i].copy()
                    prog_to.setParam("Add", instructions[i])
                    continue

                # Previous move determines the move type, current move determines the target
                move_inst = instructions[i].copy()
                move_inst['Type'] = move_inst_prev['Type']
                move_inst['MoveType'] = move_inst_prev['MoveType']
                move_inst['Name'] = move_inst_prev['Name'].split(' ', 1)[0] + ' ' + move_inst['Name'].split(' ', 1)[1]

                prog_to.setParam("Add", move_inst)
                move_inst_prev = instructions[i].copy()

            else:
                # Add everything else as-is
                if i not in blocks_index:
                    prog_to.setParam("Add", instructions[i])

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ReversePrograms()


if __name__ == '__main__':
    runmain()
