# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Paint curves with preset #1 (white by default) for specified objects.
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


def PaintCurvesPreset1(RDK=None, S=None, curves=None):
    """
    Paint curves with preset #1 (white by default) for specified objects.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get curve(s) to color..
    if curves is None:
        # ..from tree selection
        curves = [x for x in RDK.Selection() if x.Type() in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
        if not curves:
            # ..or user selection
            curve = RDK.ItemUserPick('Select the curve', RDK.ItemList(robolink.ITEM_TYPE_OBJECT) + RDK.ItemList(robolink.ITEM_TYPE_CURVE))
            if not curve.Valid():
                return
            curves = [curve]
    else:
        # ..as provided
        curves = [x for x in curves if x.Type() in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
        if not curves:
            return

    for curve in curves:
        # Set the curve color
        r, g, b, a = S.CURVE_1_COLOR
        curve.setColorCurve(Settings.rgba2f(r, g, b, a))

        # Change the size of displayed curves:
        curve.setParam('Display', f'LINEW={S.CURVE_1_LINE_WEIGHT}')


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        PaintCurvesPreset1()


if __name__ == '__main__':
    runmain()
