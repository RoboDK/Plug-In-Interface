# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Split/group segments into separate curves objects based on continuity.
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


def SplitDiscontinuousCurves(RDK=None, S=None, objects=None):
    """
    Split/group segments into separate curves objects based on continuity.
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    selection = RDK.Selection()

    if objects is None:
        objects = [x for x in selection if x.type in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            objects = RDK.ItemUserPick('Select the curves to sort', robolink.ITEM_TYPE_OBJECT)
            if not objects.Valid():
                return
            objects = [objects]
    else:
        objects = [x for x in objects if x.type in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            return

    for object_item in objects:

        RDK.ShowMessage(f'Processing {object_item.Name()}..', False)

        curves = cutools.get_curves(object_item)
        if len(curves) <= 0:
            continue

        RDK.Render(False)

        grouped_curves = cutools.split_discontinuous_curves(curves, S.SPLIT_TOLERANCE)  # Works better if they are sorted first

        object_item.Copy()
        for i, group in enumerate(grouped_curves):
            sorted_object_item = object_item.Parent().Paste()
            sorted_object_item.setName(sorted_object_item.Name() + f' {i}')
            sorted_object_item.setParam("Reset", "Curves")  # We will lose curve colors!
            sorted_object_item.setVisible(True)
            for curve in group:
                sorted_object_item.AddCurve(curve, True, robolink.PROJECTION_NONE)

    RDK.setSelection(selection)  # Restore selection


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SplitDiscontinuousCurves()


if __name__ == '__main__':
    runmain()