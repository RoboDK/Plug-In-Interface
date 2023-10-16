# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Set the first point of a continuous curve.
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


def SortCurveSegments(RDK=None, S=None, objects=None):
    """
    Set the first point of a continuous curve.
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
            objects = RDK.ItemUserPick('Select object with curves to sort', robolink.ITEM_TYPE_OBJECT)
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

        start_point = cutools.get_start_point(object_item, 'Click on the starting point of the "%s" curve (approx.)\nOnly the selected segment will be affected.' % object_item.Name())

        RDK.Render(False)

        if not S.SIMPLIFY_INPLACE:
            object_item.Copy()
            sorted_object_item = object_item.Parent().Paste()
            sorted_object_item.setName(sorted_object_item.Name() + ' Sorted')
        else:
            sorted_object_item = object_item
        sorted_object_item.setParam("Reset", "Curves")  # We will lose curve colors!

        # Find the segment with this point
        indexes = []
        for i, curve in enumerate(curves):
            if start_point in curve:
                indexes=[(i, start_point)] # indexes.append((i, start_point))
                break  # continue
            indexes.append((i, cutools.closest_point(curve, start_point)))
        curve_id, new_start_point = min(indexes, key=lambda x: robomath.distance(x[1][:3], start_point[:3]))

        # Change the start point
        sorted_curves_list = curves.copy()
        point_index = cutools.closest_point_index(sorted_curves_list[curve_id], new_start_point)
        if point_index != 0:
            sorted_curves_list[curve_id] = sorted_curves_list[curve_id][point_index:] + sorted_curves_list[curve_id][:point_index]

        # Curves are relative to the object origin, while AddCurve is relative to the object pose
        # This is a "easy" way to work around it
        pose = sorted_object_item.Pose()
        sorted_object_item.setPose(robomath.eye(4))

        for curve in sorted_curves_list:
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
        SortCurveSegments()


if __name__ == '__main__':
    runmain()