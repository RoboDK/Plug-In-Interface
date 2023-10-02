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
    """Record App Settings."""

    def __init__(self, settings_param='Record-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        # --------------------------------------------
        self._FIELDS_UI['SECTION_CAMERA'] = "$Camera$"
        self._FIELDS_UI['CAMERA_RELATIVE'] = "Keep relative position when attaching the camera"
        self.CAMERA_RELATIVE = True

        # --------------------------------------------
        self._FIELDS_UI['SECTION_INPUT'] = "$Input$"
        self._FIELDS_UI['DEFAULT_SCREEN_SIZE'] = "Default screen size (width, height) [px]"
        self.DEFAULT_SCREEN_SIZE = (960, 720)

        # --------------------------------------------
        self._FIELDS_UI['SECTION_OUTPUT'] = "$Output$"
        self._FIELDS_UI['FRAMES_PER_SECOND'] = "Frame per seconds"
        self._FIELDS_UI['VIDEO_EXTENSION'] = "Format"
        self.FRAMES_PER_SECOND = 24
        self.VIDEO_EXTENSION = [0, ['.mp4', '.avi']]


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
        S.ShowUI('Record Settings')


if __name__ == '__main__':
    runmain()