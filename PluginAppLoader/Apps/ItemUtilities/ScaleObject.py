# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Scale an object given a per-axis scale ratio.
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


class ScaleSettings(roboapps.AppSettings):

    def __init__(self, settings_param='Scale-Settings'):
        super().__init__(settings_param)

        self._UI_SHOW_DISCARD = False
        self._UI_TEXT_SAVE = 'Apply'

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        self._FIELDS_UI['SCALE_XYZ'] = "Scale (x,y,z) [%/100]"
        self.SCALE_XYZ = [1., 1., 1.]


def ScaleObject(RDK=None, S=None, objects=None):
    """
    Scale an object given a per-axis scale ratio.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = ScaleSettings()
        S.Load()

    # Get object(s)..
    if objects is None:
        # ..from tree selection
        objects = [x for x in RDK.Selection() if x.Type() in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
        if not objects:
            # ..or user selection
            curve = RDK.ItemUserPick('Select the curve', RDK.ItemList(robolink.ITEM_TYPE_OBJECT) + RDK.ItemList(robolink.ITEM_TYPE_CURVE))
            if not curve.Valid():
                return
            objects = [curve]
    else:
        # ..as provided
        objects = [x for x in objects if x.Type() in [robolink.ITEM_TYPE_OBJECT, robolink.ITEM_TYPE_CURVE]]
        if not objects:
            return

    S.ShowUI('Scale settings')
    if S.SCALE_XYZ == [1., 1., 1.]:
        return

    for obj in objects:
        obj.Scale(S.SCALE_XYZ)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ScaleObject()


if __name__ == '__main__':
    runmain()
