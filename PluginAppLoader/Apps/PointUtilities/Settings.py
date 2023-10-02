# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file lets you edit the settings of this RoboDK App.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import roboapps


class Settings(roboapps.AppSettings):
    """
    Point Utilities Settings
    """

    def __init__(self, settings_param='Point-Utilities-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        self._FIELDS_UI['SECTION_ADD_POINT'] = "$Add point on surface$"

        self._FIELDS_UI['ADD_TO_OBJECT'] = "Add new points to the object"
        self.ADD_TO_OBJECT = False

        self._FIELDS_UI['SECTION_POINT_TO_TARGET'] = "$Point to target$"

        self._FIELDS_UI['TARGET_INVERSE_NORMAL'] = "Inverse point normal"
        self.TARGET_INVERSE_NORMAL = True

        self._FIELDS_UI['SECTION_SORT'] = "$Sort points$"

        self._FIELDS_UI['PROMPT_FIRST_POINT'] = "Prompt to enter the first point when sorting"
        self.PROMPT_FIRST_POINT = False


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        S = Settings()
        S.Load()
        S.ShowUI('Point Utilities Settings')


if __name__ == '__main__':
    runmain()