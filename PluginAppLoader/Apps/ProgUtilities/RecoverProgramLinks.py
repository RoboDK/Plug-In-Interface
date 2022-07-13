# Attempts to recover broken Item links in a Program. For instance, when a Program was copied from another station.
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink

import re

RE_TARGET = re.compile("\((.+)\)")  # MoveL (Target 1)
RE_FRAME = re.compile("Set Ref.: (.+)")  # Frame 2 or Set Ref.: Frame 2
RE_TOOL = re.compile("Set Tool: (.+)")  # Paint gun or Set Tool.: Paint gun

PROG_RECOVER_NAME = "%s Recovered"  # ex: MyProg Recovered


def getRecoverProg(prog, RDK):
    """Creates a new program from the specified program."""

    # Delete previously generated programs of the same name
    new_prog_name = PROG_RECOVER_NAME % prog.Name()
    new_prog = RDK.Item(new_prog_name, robolink.ITEM_TYPE_PROGRAM)
    if new_prog.Valid() and new_prog.Name() == new_prog_name:
        new_prog.Delete()

    # Create a new program
    new_prog = RDK.AddProgram(new_prog_name)
    if not new_prog.Valid():
        new_prog.Delete()
        raise
    new_prog.setParent(prog.Parent())
    new_prog.ShowInstructions()
    return new_prog


def recoverProg(prog_from, prog_to, RDK):
    """
    Recover a program that has missing links, which happens when a program is copied from another station.
    """
    robot = prog_from.getLink(robolink.ITEM_TYPE_ROBOT)
    if not robot.Valid():
        robot = RDK.ItemUserPick(f'Select {prog_from.Name()} robot', robolink.ITEM_TYPE_ROBOT)
        prog_to.setRobot(robot)

    inst_count = prog_from.InstructionCount()
    for i in range(inst_count):
        instruction_dict = prog_from.setParam(i)
        print(' - Instruction: ' + str(instruction_dict))

        if instruction_dict['Type'] in [robolink.INS_TYPE_MOVE]:
            target_name = RE_TARGET.search(instruction_dict['Name']).group(1)
            target = RDK.Item(target_name, robolink.ITEM_TYPE_TARGET)
            if target.Valid():
                if instruction_dict['MoveType'] in [robolink.MOVE_TYPE_JOINT]:
                    prog_to.MoveJ(target)
                    continue
                elif instruction_dict['MoveType'] in [robolink.MOVE_TYPE_LINEAR]:
                    prog_to.MoveL(target)
                    continue

        elif instruction_dict['Type'] in [robolink.INS_TYPE_MOVEC]:
            target_names = RE_TARGET.search(instruction_dict['Name']).group(1).split(', ')
            target1 = RDK.Item(target_names[0], robolink.ITEM_TYPE_TARGET)
            target2 = RDK.Item(target_names[1], robolink.ITEM_TYPE_TARGET)
            if target1.Valid() and target2.Valid():
                prog_to.MoveC(target1, target2)
                continue

        elif instruction_dict['Type'] in [robolink.INS_TYPE_CHANGEFRAME]:
            frame_name = instruction_dict['FrameName']
            if frame_name.startswith("Set Ref.:"):
                frame_name = RE_FRAME.search(instruction_dict['FrameName']).group(1)
            frame = RDK.Item(frame_name, robolink.ITEM_TYPE_FRAME)
            if frame.Valid():
                prog_to.setFrame(frame)
                continue

        elif instruction_dict['Type'] in [robolink.INS_TYPE_CHANGETOOL]:
            tool_name = instruction_dict['ToolName']
            if tool_name.startswith("Set Tool:"):
                tool_name = RE_TOOL.search(instruction_dict['ToolName']).group(1)
            tool = RDK.Item(tool_name, robolink.ITEM_TYPE_TOOL)
            if tool.Valid():
                prog_to.setTool(tool)
                continue

        prog_to.setParam("Add", instruction_dict)

    prog_to.setParam("RecalculateTargets")


def runmain():
    RDK = robolink.Robolink()

    # Get the programs to recover
    programs = list(filter(lambda item: item.Type() == robolink.ITEM_TYPE_PROGRAM, RDK.Selection()))
    if not programs:
        RDK.ShowMessage('Please select at least one program.')
        return

    for program in programs:
        # Create a new empty program
        rec_prog = getRecoverProg(program, RDK)

        # Recover program into the new program
        recoverProg(program, rec_prog, RDK)


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()