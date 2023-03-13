# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Sort the order of points in an object by distance from the previous point.
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
import _putools as cutools


def SortCurveSegments(RDK=None, S=None, objects=None):
    """
    Sort the order of curves in an object by distance from the end of a segment to the start of the next segment.
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

        points = cutools.get_points(object_item)
        if len(points) <= 0:
            continue

        RDK.Render(False)

        object_item.Copy()
        sorted_object_item = object_item.Parent().Paste()
        sorted_object_item.setName(sorted_object_item.Name() + ' Sorted')
        sorted_object_item.setParam("Reset", "Points")
        sorted_object_item.setVisible(True)

        start_point = None
        if S.PROMPT_FIRST_POINT:
            start_point = robodialogs.InputDialog('Enter the desired start point.\nThe default values represent the current first point.\n\nStart point (xyz) [mm]:', [round(x, 4) for x in points[0][:3]])

        sorted_points_list = cutools.sort_points(points, start_point)
        sorted_object_item.AddPoints(sorted_points_list, True, robolink.PROJECTION_NONE)

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