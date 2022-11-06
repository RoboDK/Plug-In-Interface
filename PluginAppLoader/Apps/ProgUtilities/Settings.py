# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file let's you edit the settings of this RoboDK App.
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
    """ProgUtilities App Settings."""

    def __init__(self, settings_param='ProgUtilities-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        # --------------------------------------------
        self._FIELDS_UI['SECTION_EXPAND'] = "$Expand program$"
        self._FIELDS_UI['EXPAND_PROG_SUFFIX'] = "Expanded program suffix"
        self._FIELDS_UI['EXPAND_RECURSIVELY'] = "Expand programs recursively"
        self.EXPAND_PROG_SUFFIX = 'Expanded'
        self.EXPAND_RECURSIVELY = True

        # --------------------------------------------
        self._FIELDS_UI['SECTION_MERGE'] = "$Merge program$"
        self._FIELDS_UI['MERGE_PROG_SUFFIX'] = "Merged program suffix"
        self.MERGE_PROG_SUFFIX = 'Merged'

        # --------------------------------------------
        self._FIELDS_UI['SECTION_RECOVER_PROG'] = "$Program Links Recovery$"
        self._FIELDS_UI['RECOVER_PROG_SUFFIX'] = "Recovered program suffix"
        self.RECOVER_PROG_SUFFIX = 'Recovered'

        # --------------------------------------------
        self._FIELDS_UI['SECTION_MOVEC'] = "$Convert MoveC$"
        self._FIELDS_UI['CONVERT_MOVEC_STEP_MM'] = "Step size of linear movements [mm]"
        self._FIELDS_UI['CONVERT_MOVEC_STEP_DEG'] = "Step size of joint movements [deg]"
        self._FIELDS_UI['CONVERT_MOVEC_PROG_SUFFIX'] = "Converted program suffix"
        self.CONVERT_MOVEC_STEP_MM = 1.
        self.CONVERT_MOVEC_STEP_DEG = 1.
        self.CONVERT_MOVEC_PROG_SUFFIX = 'Linear MoveC'


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
        S.ShowUI('Program Utilities Settings')


if __name__ == '__main__':
    runmain()