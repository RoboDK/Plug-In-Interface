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
    """Snapshot App Settings."""

    def __init__(self, settings_param='Snapshot-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        # --------------------------------------------
        self._FIELDS_UI['SECTION_SNAPSHOT'] = "$Snapshot (High Resolution)$"
        self._FIELDS_UI['SNAPSHOT_SIZE'] = 'Size (width, height) [px,px]'
        self._FIELDS_UI['SNAPSHOT_AA'] = 'Anti-aliasing'
        self._FIELDS_UI['SNAPSHOT_AA_MAX'] = 'Maximum size with anti-aliasing [px]'
        self._FIELDS_UI['SNAPSHOT_FOV'] = 'Field of view (FOV) [deg]'
        self.SNAPSHOT_SIZE = (1920, 1080)
        self.SNAPSHOT_AA = 4
        self.SNAPSHOT_AA_MAX = 8000
        self.SNAPSHOT_FOV = 30

        self._FIELDS_UI['SNAPSHOT_REMOVE_BG'] = 'Remove background (transparency)'
        self._FIELDS_UI['SNAPSHOT_ZOOM_TO_FIT'] = 'Zoom to fit (if background removed)'
        self.SNAPSHOT_REMOVE_BG = True
        self.SNAPSHOT_ZOOM_TO_FIT = False

        self._FIELDS_UI['SNAPSHOT_COMPRESSION'] = 'File compression level'
        self.SNAPSHOT_COMPRESSION = [4, [str(x) for x in range(0, 10)]]


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
        S.ShowUI('Snapshot Settings')


if __name__ == '__main__':
    runmain()