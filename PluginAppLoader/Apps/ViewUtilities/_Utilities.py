# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# General utility functions for this App.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink
import re

RE_TARGET = re.compile("\((.+)\)")  # MoveL (Target 1)


def getTargets(RDK):
    """Get all target items"""
    return RDK.ItemList(robolink.ITEM_TYPE_TARGET)


def getJointTargets(RDK):
    """Get all joint targets"""
    return [target for target in getTargets(RDK) if target.isJointTarget()]


def getCartesianTargets(RDK):
    """Get all cartesian tagets"""
    return [target for target in getTargets(RDK) if not target.isJointTarget()]


def getRobotTargets(robot):
    """Get all targets of a robot"""
    targets = []

    RDK = robot.RDK()
    for target in getTargets(RDK):
        if robot == target.getLink(robolink.ITEM_TYPE_ROBOT):
            targets.append(target)
    return targets


def getProgramTargets(program):
    """Get all targets of a program"""

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

    targets = []

    RDK = program.RDK()
    inst_count = program.InstructionCount()
    for i in range(inst_count):
        instruction_dict = program.setParam(i)

        if 'TargetPtr' in instruction_dict:
            target = get_item_from_inst_ptr(instruction_dict['TargetPtr'], RDK)
            if target:
                targets.append(target)
                continue

        if instruction_dict['Type'] in [robolink.INS_TYPE_MOVE]:
            target = get_target_from_inst(instruction_dict['Name'], RDK)
            if target:
                targets.append(target)
                continue

        if instruction_dict['Type'] in [robolink.INS_TYPE_MOVEC]:
            target1, target2 = get_targets_from_inst(instruction_dict['Name'], RDK)
            if target1:
                targets.append(target1)
            if target2:
                targets.append(target2)

        # At this point there is not target in this instruction, or we fail to retrieve it

    return targets


def expand(item, progs=True):
    """Expand a tree item"""
    item.setParam('Tree', 'expand')

    if progs and item.Type() == robolink.ITEM_TYPE_PROGRAM:
        item.ShowInstructions(True)


def collapse(item, progs=True):
    """Collapse a tree item"""
    item.setParam('Tree', 'collapse')

    if progs and item.Type() == robolink.ITEM_TYPE_PROGRAM:
        item.ShowInstructions(False)