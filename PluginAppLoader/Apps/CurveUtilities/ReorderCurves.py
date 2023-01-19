# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Import an SVG file as a curve(s) or point(s) object.
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

import os

import Settings


def GetObjectCurves(object_item, feature_id=-1):
    if feature_id != -1:
        return [object_item.GetPoints(robolink.FEATURE_CURVE, feature_id)[0]]

    object_curves = []
    i = 0
    while True:
        curve = object_item.GetPoints(robolink.FEATURE_CURVE, i)[0]
        if not curve:
            break
        object_curves.append(curve)
        i += 1
    return object_curves


def SortCurves(coords, start=None):
    if start is None:
        start = coords[0]
    pass_by = coords.copy()
    path = [start]
    if start in pass_by:
        pass_by.remove(start)
    while pass_by:
        nearest = min(pass_by, key=lambda x: robomath.distance(path[-1][-1][:3], x[0][:3]))
        path.append(nearest)
        pass_by.remove(nearest)
    return path


def ReorderCurves(RDK=None, S=None, objects=None):
    """
    Reorder curves into one continuous path (or closest match)
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    if objects is None:
        objects = [x for x in RDK.Selection() if x.type in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
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

        curves_list = GetObjectCurves(object_item)
        if len(curves_list) <= 2:
            continue

        RDK.Render(False)

        object_item.Copy()
        sorted_object_item = object_item.Parent().Paste()
        sorted_object_item.setName(sorted_object_item.Name() + ' Sorted')
        sorted_object_item.setVisible(True)

        sorted_curves_list = SortCurves(curves_list)
        sorted_object_item.setParam("Reset", "Curves")  # We will lose curve colors!
        for curve in sorted_curves_list:
            sorted_object_item.AddCurve(curve, True, robolink.PROJECTION_NONE)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ReorderCurves()


if __name__ == '__main__':
    runmain()