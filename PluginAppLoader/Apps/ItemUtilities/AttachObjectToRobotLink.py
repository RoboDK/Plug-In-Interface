# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Attach object(s) to a robot link permanently.
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


class Settings(roboapps.AppSettings):

    def __init__(self, settings_param='Attach-Object-Robot-Settings'):
        super().__init__(settings_param)

        self._UI_TEXT_SAVE = 'Apply'
        self._UI_TEXT_DISCARD = 'Cancel'
        self._UI_SHOW_DEFAULTS = False

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        self._FIELDS_UI['ROBOT_LINK'] = "Robot joint to attach to (0 is base)"
        self._FIELDS_UI['DELETE_SOURCE_OBJECT'] = "Delete source object"
        self.ROBOT_LINK = [0, ['0', '1', '2', '3', '4', '5', '6']]
        self.DELETE_SOURCE_OBJECT = False


def AttachObjectToRobotLink(RDK=None, S=None, objects=None):
    """
    Attach object(s) to a robot link permanently.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings()
        S.Load()

    # Get object(s)..
    if objects is None:
        # ..from tree selection
        objects = [x for x in RDK.Selection() if x.Type() in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            # ..or user selection
            obj = RDK.ItemUserPick('Select the object to attach', RDK.ItemList(robolink.ITEM_TYPE_OBJECT))
            if not obj.Valid():
                return
            objects = [obj]
    else:
        # ..as provided
        objects = [x for x in objects if x.Type() in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            return

    # Get robot..
    robot = RDK.ItemUserPick('Select the robot to attach to', RDK.ItemList(robolink.ITEM_TYPE_ROBOT))  # Using ItemList to force the prompt
    if not robot.Valid():
        return

    DOF = len(robot.Joints().tolist())
    S.ROBOT_LINK = [0, [str(x) for x in range(DOF + 1)]]
    if S.ShowUI('Attach Object Settings'):
        return

    robot_link = robot.ObjectLink(int(S.ROBOT_LINK[0]))
    if not robot_link.Valid():
        return

    RDK.MergeItems([robot_link] + objects)

    if S.DELETE_SOURCE_OBJECT:
        for obj in objects:
            obj.Delete()


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        AttachObjectToRobotLink()


if __name__ == '__main__':
    runmain()
