# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# App settings action: when this action is executed it will show the settings we can configure for this App.
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
    Settings class to define configurable settings for the Import-Export Settings App
    """

    def __init__(self, settings_param='Import-Export-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()  # _FIELDS_UI are optional, but provides better descriptions to the user

        self._FIELDS_UI['SETTINGS_NAME'] = "Default settings file name"
        self.SETTINGS_NAME = 'RoboDK-Settings.ini'


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.

    Example for a 'Checkable Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    Example for a 'Momentary Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                roboapps.Exit()  # or sys.exit()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    Example for a 'Checkable Option':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.KeepChecked()  # Important, prevents RoboDK from unchecking the action after it has completed
                ActionChecked()

    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        S = Settings()
        S.Load()
        S.ShowUI('Import/Export settings')


if __name__ == '__main__':
    runmain()