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
    """Reachability App Settings."""

    def __init__(self, settings_param='Reachability-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        # --------------------------------------------
        self._FIELDS_UI['SECTION_PREVIEW'] = "$Preview$"
        self._FIELDS_UI['PREVIEW_ROBOT_JOINTS'] = 'Preview robot (not just the tool)'
        self._FIELDS_UI['PREVIEW_REACHABLE'] = 'Preview reachable poses'
        self._FIELDS_UI['PREVIEW_UNREACHABLE'] = 'Preview unreachable poses'
        self.PREVIEW_ROBOT_JOINTS = False
        self.PREVIEW_REACHABLE = True
        self.PREVIEW_UNREACHABLE = True

        self._FIELDS_UI['TIMEOUT_REACHABLE'] = 'Reachable timeout [s]'
        self._FIELDS_UI['TIMEOUT_UNREACHABLE'] = 'Unreachable timeout [s]'
        self.TIMEOUT_REACHABLE = 10.
        self.TIMEOUT_UNREACHABLE = 10.

        self._FIELDS_UI['PREVIEW_CLEAR_ALL'] = 'Clear all robot previews on exit'
        self.PREVIEW_CLEAR_ALL = True

        # --------------------------------------------
        self._FIELDS_UI['SECTION_TRANSLATE'] = "$Translation$"
        self._FIELDS_UI['TRANSLATION_ENABLE'] = 'Check translations'
        self._FIELDS_UI['RANGE_TX'] = 'Translation X (min,max,step) [mm,mm,mm]'
        self._FIELDS_UI['RANGE_TY'] = 'Translation Y (min,max,step) [mm,mm,mm]'
        self._FIELDS_UI['RANGE_TZ'] = 'Translation Z (min,max,step) [mm,mm,mm]'
        self.TRANSLATION_ENABLE = False
        self.RANGE_TX = (-100, 100, 100)
        self.RANGE_TY = (-100, 100, 100)
        self.RANGE_TZ = (-100, 100, 100)

        # --------------------------------------------
        self._FIELDS_UI['SECTION_Range'] = "$Rotation$"
        self._FIELDS_UI['ROTATION_ENABLE'] = 'Check rotations'
        self._FIELDS_UI['RANGE_RX'] = 'Rotation X (min,max,step) [deg,deg,deg]'
        self._FIELDS_UI['RANGE_RY'] = 'Rotation Y (min,max,step) [deg,deg,deg]'
        self._FIELDS_UI['RANGE_RZ'] = 'Rotation Z (min,max,step) [deg,deg,deg]'
        self.ROTATION_ENABLE = True
        self.RANGE_RX = (-120, 180, 60)
        self.RANGE_RY = (-120, 180, 60)
        self.RANGE_RZ = (-90, 90, 0)


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
        S.ShowUI('Reachability Settings')


if __name__ == '__main__':
    runmain()