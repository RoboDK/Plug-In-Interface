# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Recover missing links in program(s), which happens when a program is copied from another station.
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
import re

import Settings

# Regex for finding items in program 'Name' instructions
RE_TARGET = re.compile("\((.+)\)")  # MoveL (Target 1)
RE_FRAME = re.compile("Set Ref.: (.+)")  # Set Ref.: Frame 2
RE_TOOL = re.compile("Set Tool: (.+)")  # Set Tool.: Paint gun


def get_item_from_inst_ptr(inst_ptr, RDK):
    """Get an item from an instruction pointer, typically a TargetPtr, FramePtr, ToolPtr, etc."""
    if inst_ptr == '0' or inst_ptr == 0:
        return None

    item = robolink.Item(RDK, str(inst_ptr))
    if not item.Valid(True) or str(item.item) != str(inst_ptr):
        return None

    return item


def get_target_from_inst(inst_target_name, RDK):
    """Get a target item from an instruction, typically a MoveL or MoveJ"""
    r = RE_TARGET.search(inst_target_name)
    if not r:
        return None

    target_name = r.group(1)
    target = RDK.Item(target_name, robolink.ITEM_TYPE_TARGET)
    if not target.Valid(True) or target.Name() != target_name:
        return None

    return target


def get_targets_from_inst(inst_targets_name, RDK):
    """Get targets items from an instruction, typically a MoveC."""
    r = RE_TARGET.search(inst_targets_name)
    if not r:
        return None, None

    target_names = r.group(1).split(', ')
    target1 = RDK.Item(target_names[0], robolink.ITEM_TYPE_TARGET)
    if not target1.Valid(True) or target1.Name() != target_names[0]:
        target1 = None

    target2 = RDK.Item(target_names[1], robolink.ITEM_TYPE_TARGET)
    if not target2.Valid(True) or target2.Name() != target_names[1]:
        target2 = None

    return target1, target2


def get_frame_from_inst(inst_frame_name, RDK):
    """Get a frame item from an instruction"""
    r = RE_FRAME.search(inst_frame_name)
    if not r:
        return None

    frame_name = r.group(1)
    frame = RDK.Item(frame_name, robolink.ITEM_TYPE_FRAME)
    if not frame.Valid(True) or frame.Name() != frame_name:
        return None

    return frame


def get_tool_from_inst(inst_tool_name, RDK):
    """Get a target item from an instruction"""
    r = RE_TOOL.search(inst_tool_name)
    if not r:
        return None

    tool_name = r.group(1)
    tool = RDK.Item(tool_name, robolink.ITEM_TYPE_TOOL)
    if not tool.Valid(True) or tool.Name() != tool_name:
        return None

    return tool


def RecoverPrograms(RDK=None, S=None, progs=None):
    """
    Recover missing links in program(s), which happens when a program is copied from another station.
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
        prog_to = RDK.AddProgram(f"{prog_from.Name()} {S.RECOVER_PROG_SUFFIX.strip()}", robot)
        prog_to.setParent(prog_from.Parent())
        print('Recovering program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"')

        # Parse instructions
        inst_count = prog_from.InstructionCount()
        for i in range(inst_count):
            instruction_dict = prog_from.setParam(i)

            # MoveJ and MoveL have a linked target
            if instruction_dict['Type'] in [robolink.INS_TYPE_MOVE]:
                target = None
                if 'TargetPtr' in instruction_dict:
                    target = get_item_from_inst_ptr(instruction_dict['TargetPtr'], RDK)
                if target is None:
                    target = get_target_from_inst(instruction_dict['Name'], RDK)
                if target is None:
                    target = RDK.ItemUserPick('Target of ' + instruction_dict['Name'], robolink.ITEM_TYPE_TARGET)

                if target and target.Valid():
                    if instruction_dict['MoveType'] in [robolink.MOVE_TYPE_JOINT]:
                        prog_to.MoveJ(target)
                        continue
                    elif instruction_dict['MoveType'] in [robolink.MOVE_TYPE_LINEAR]:
                        prog_to.MoveL(target)
                        continue
                    elif instruction_dict['MoveType'] in [robolink.MOVE_TYPE_LINEARSEARCH]:
                        prog_to.SearchL(target)
                        continue

            # MoveC has 2 linked targets
            elif instruction_dict['Type'] in [robolink.INS_TYPE_MOVEC]:
                target1, target2 = get_targets_from_inst(instruction_dict['Name'], RDK)
                if target1 is None:
                    target1 = RDK.ItemUserPick('Target 1 of ' + instruction_dict['Name'], robolink.ITEM_TYPE_TARGET)
                if target2 is None:
                    target1 = RDK.ItemUserPick('Target 2 of ' + instruction_dict['Name'], robolink.ITEM_TYPE_TARGET)

                if target1 and target1.Valid() and target2 and target2.Valid():
                    if instruction_dict['MoveType'] in [robolink.MOVE_TYPE_CIRCULAR]:
                        prog_to.MoveC(target1, target2)
                        continue

            # Set Frame has a linked frame
            elif instruction_dict['Type'] in [robolink.INS_TYPE_CHANGEFRAME]:
                frame = None
                if 'FramePtr' in instruction_dict:
                    frame = get_item_from_inst_ptr(instruction_dict['FramePtr'], RDK)
                if frame is None:
                    frame = get_frame_from_inst(instruction_dict['Name'], RDK)
                if frame is None:
                    frame = RDK.ItemUserPick('Frame of ' + instruction_dict['Name'], robolink.ITEM_TYPE_FRAME)

                if frame and frame.Valid():
                    prog_to.setFrame(frame)
                    continue

            # Set Tool has a linked tool
            elif instruction_dict['Type'] in [robolink.INS_TYPE_CHANGETOOL]:
                tool = None
                if 'ToolPtr' in instruction_dict:
                    tool = get_item_from_inst_ptr(instruction_dict['ToolPtr'], RDK)
                if tool is None:
                    tool = get_tool_from_inst(instruction_dict['Name'], RDK)
                if tool is None:
                    tool = RDK.ItemUserPick('Tool of ' + instruction_dict['Name'], robolink.ITEM_TYPE_TOOL)

                if tool and tool.Valid():
                    prog_to.setTool(tool)
                    continue

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
        RecoverPrograms()


if __name__ == '__main__':
    runmain()
