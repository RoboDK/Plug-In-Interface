# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Convert a RooDK program to a curve.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps, robodialogs

import Settings
import _cutools as cutools


def inst_pose(inst: str) -> robomath.Mat:
    from robodk.robomath import transl

    def rotx(deg):
        from robodk.robomath import rotx as rotx_rad
        return rotx_rad(deg * 180 / robomath.pi)

    def roty(deg):
        from robodk.robomath import roty as roty_rad
        return roty_rad(deg * 180 / robomath.pi)

    def rotz(deg):
        from robodk.robomath import rotz as rotz_rad
        return rotz_rad(deg * 180 / robomath.pi)

    try:
        return eval(inst)
    except:
        return None


def ProgToCurve(RDK=None, S=None, progs=None):
    """
    Convert a RooDK program to a curve.
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    selection = RDK.Selection()

    if progs is None:
        progs = [x for x in selection if x.type in [robolink.ITEM_TYPE_PROGRAM]]
        if not progs:
            progs = RDK.ItemUserPick('Select program to convert to a curve', robolink.ITEM_TYPE_PROGRAM)
            if not progs.Valid():
                return
            progs = [progs]
    else:
        progs = [x for x in progs if x.type in [robolink.ITEM_TYPE_PROGRAM]]
        if not progs:
            return

    RDK.Render(False)
    for prog_item in progs:

        RDK.ShowMessage(f'Processing {prog_item.Name()}..', False)

        curve = []
        pose_frame = robomath.eye(4)
        for i in range(prog_item.InstructionCount()):
            name, instype, movetype, isjointtarget, target, joints = prog_item.Instruction(i)
            inst_dict = prog_item.setParam(i)

            if inst_dict['Type'] == robolink.INS_TYPE_CHANGEFRAME:
                pose_frame = inst_pose(inst_dict['Pose'])

            if not movetype:
                continue

            pose = inst_pose(inst_dict['Pose'])
            pose_abs = pose_frame * pose

            xyz = pose_abs.Pos()
            ijk = pose_abs.VZ()

            curve.append(xyz + ijk)

        if not curve:
            continue

        curve_item = RDK.AddCurve(curve)
        curve_item.setName(prog_item.Name())

        # There is a bug in RoboDK where the resulting object does not show the curve icon, this is a workaround
        curve_item.setVisible(False)
        curve_item.setVisible(True)

    RDK.setSelection(selection)  # Restore selection


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ProgToCurve()


if __name__ == '__main__':
    runmain()