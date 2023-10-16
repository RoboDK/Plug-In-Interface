# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Recalculate the normals of the curves of an object.
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


def RecalculateCurveNormals(RDK=None, S=None, objects=None):
    """
    Recalculate the normals of the curves of an object.
    The XYZ of the points are not changed, only the normals (IJK).
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
            objects = RDK.ItemUserPick('Select the object with curve normals to recalculate', robolink.ITEM_TYPE_OBJECT)
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

        if not S.SIMPLIFY_INPLACE:
            object_item.Copy()
            sorted_object_item = object_item.Parent().Paste()
            sorted_object_item.setName(sorted_object_item.Name() + ' Recalculated')
        else:
            sorted_object_item = object_item
        sorted_object_item.setParam("Reset", "Curves")  # We will lose curve colors!

        # Curves are relative to the object origin, while AddCurve is relative to the object pose
        # This is a "easy" way to work around it
        pose = sorted_object_item.Pose()
        sorted_object_item.setPose(robomath.eye(4))

        for curve in curves:
            curve = cutools.project_points(curve, object_item, False, S.SIMPLIFY_PROJECT_ALONG_NORMAL, True)
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
        RecalculateCurveNormals()


if __name__ == '__main__':
    runmain()