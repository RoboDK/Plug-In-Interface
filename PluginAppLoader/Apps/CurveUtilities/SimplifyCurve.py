# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Simplify the curves of an object with preferred settings.
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


def SimplifyCurve(RDK=None, S=None, objects=None):
    """
    Simplify the curves of an object with preferred settings.
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

        start_point = None
        if S.SIMPLIFY_SORT:
            start_point = cutools.get_start_point(object_item, 'Click on the starting point of the "%s" curve (approx.)' % object_item.Name())
            start_point = [start_point]

        RDK.Render(False)

        if not S.SIMPLIFY_INPLACE:
            object_item.Copy()
            sorted_object_item = object_item.Parent().Paste()
            sorted_object_item.setName(sorted_object_item.Name() + ' Simplified')
        else:
            sorted_object_item = object_item
        sorted_object_item.setParam("Reset", "Curves")  # We will lose curve colors!

        simplified_curves = curves

        # The order matters as it will change the results!

        if S.SIMPLIFY_PROJECT_POINT or S.SIMPLIFY_RECALC_NORMAL:
            simplified_curves = [cutools.project_points(curve, object_item, S.SIMPLIFY_PROJECT_POINT, S.SIMPLIFY_PROJECT_ALONG_NORMAL, S.SIMPLIFY_RECALC_NORMAL) for curve in simplified_curves]

        if S.SIMPLIFY_SORT:
            simplified_curves = cutools.sort_curve_segments(simplified_curves, start=start_point, reverse_segments=S.SIMPLIFY_REVERSE)

        if S.SIMPLIFY_MERGE:
            simplified_curves = [cutools.merge_curves(simplified_curves)]

        if S.SIMPLIFY_STRAIGHT_LINES:
            simplified_curves = [cutools.filter_straight_lines(curve, S.SIMPLIFY_TOLERANCE_STRAIGHT_LINE, S.SIMPLIFY_COMPARE_NORMALS, S.SIMPLIFY_TOLERANCE_NORMALS) for curve in simplified_curves]

        if S.SIMPLIFY_DUPLICATES:
            simplified_curves = [cutools.filter_subsequent_duplicated_points(curve, S.SIMPLIFY_TOLERANCE_POINT, S.SIMPLIFY_COMPARE_NORMALS, S.SIMPLIFY_TOLERANCE_NORMALS) for curve in simplified_curves]

        # Curves are relative to the object origin, while AddCurve is relative to the object pose
        # This is a "easy" way to work around it
        pose = sorted_object_item.Pose()
        sorted_object_item.setPose(robomath.eye(4))

        for curve in simplified_curves:
            sorted_object_item.AddCurve(curve, True, robolink.PROJECTION_NONE)

        sorted_object_item.setPose(pose)

        # There is a bug in RoboDK where the resulting object does not show the curve icon, this is a workaround
        sorted_object_item.setVisible(False)
        sorted_object_item.setVisible(True)

    RDK.setSelection(selection)  # Restore selection


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SimplifyCurve()


if __name__ == '__main__':
    runmain()