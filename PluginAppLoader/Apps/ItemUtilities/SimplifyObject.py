# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This script removes small components of an object such as small shapes or small/invalid triangles
# Among other things, this improve the speed and the numerical stability of collision checking
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


class SimplifySettings(roboapps.AppSettings):

    def __init__(self, settings_param='Simplify-Settings'):
        super().__init__(settings_param)

        self._UI_SHOW_DISCARD = False
        self._UI_TEXT_SAVE = 'Apply'

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        self._FIELDS_UI['SHAPE_RADIUS'] = "Minimum object size/radius [mm]"
        self._FIELDS_UI['TRIANGLE_AREA'] = "Minimum triangle surface [mm^2]"
        self._FIELDS_UI['TRIANGLE_ANGLE'] = "Minimum triangle angle [deg]"
        self.SHAPE_RADIUS = 0.1
        self.TRIANGLE_AREA = 0.1
        self.TRIANGLE_ANGLE = 0.02


def SimplifyObject(RDK=None, S=None, objects=None):
    """
    This script removes small components of an object such as small shapes or small/invalid triangles
    Among other things, this improve the speed and the numerical stability of collision checking
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = SimplifySettings()
        S.Load()

    # Get object(s)..
    if objects is None:
        # ..from tree selection
        objects = [x for x in RDK.Selection() if x.Type() in [
            robolink.ITEM_TYPE_OBJECT,
            robolink.ITEM_TYPE_CURVE,
            robolink.ITEM_TYPE_ROBOT,
            robolink.ITEM_TYPE_TOOL,
        ]]
        if not objects:
            # ..or user selection
            obj = RDK.ItemUserPick('Select the object', RDK.ItemList(robolink.ITEM_TYPE_OBJECT))
            if not obj.Valid():
                return
            objects = [obj]
    else:
        # ..as provided
        objects = [x for x in objects if x.Type() in [
            robolink.ITEM_TYPE_OBJECT,
            robolink.ITEM_TYPE_CURVE,
            robolink.ITEM_TYPE_ROBOT,
            robolink.ITEM_TYPE_TOOL,
        ]]
        if not objects:
            return

    # Get the scaling
    S.ShowUI('Simplify settings')

    # Apply the simplification
    for obj in objects:
        status = obj.setParam("FilterMesh", [S.SHAPE_RADIUS, S.TRIANGLE_AREA, S.TRIANGLE_ANGLE])
        RDK.ShowMessage(f"{obj.Name()}: {status}", False)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SimplifyObject()


if __name__ == '__main__':
    runmain()
