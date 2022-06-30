# General utility functions for this App.
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink


def getTargets(RDK):
    return RDK.ItemList(robolink.ITEM_TYPE_TARGET)


def getJointTargets(RDK):
    return [target for target in getTargets(RDK) if target.isJointTarget()]


def getCartesianTargets(RDK):
    return [target for target in getTargets(RDK) if not target.isJointTarget()]


def getRobotTargets(robot):
    targets = []

    RDK = robot.RDK()
    for target in getTargets(RDK):
        if robot == target.getLink(robolink.ITEM_TYPE_ROBOT):
            targets.append(target)
    return targets


def getProgramTargets(program):
    import re
    RE_TARGET = re.compile("\((.+)\)")  # MoveL (Target 1)

    targets = []

    RDK = program.RDK()
    inst_count = program.InstructionCount()
    for i in range(inst_count):
        instruction_dict = program.setParam(i)
        if instruction_dict['Type'] in [robolink.INS_TYPE_MOVE]:
            target_name = RE_TARGET.search(instruction_dict['Name']).group(1)
            target = RDK.Item(target_name, robolink.ITEM_TYPE_TARGET)
            if not target.Valid():
                continue

            targets.append(target)
    return targets


def expand(item, progs=True):
    item.setParam('Tree', 'expand')

    if progs and item.Type() == robolink.ITEM_TYPE_PROGRAM:
        item.ShowInstructions(True)


def collapse(item, progs=True):
    item.setParam('Tree', 'collapse')

    if progs and item.Type() == robolink.ITEM_TYPE_PROGRAM:
        item.ShowInstructions(False)