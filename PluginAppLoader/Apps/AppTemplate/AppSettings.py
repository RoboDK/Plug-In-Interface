# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# App settings example.
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
    App Template's App Settings.
    
    Use robodk.roboapps.AppSettings to create auto-generated user interface for your App's settings.
    Settings are automatically saved in your station and are accessible from anywhere in your App.
    """

    def __init__(self, settings_param='App-Template-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()  # _FIELDS_UI are optional, but provides better descriptions to the user

        self._FIELDS_UI['APP_OPTION_KEY'] = "Checkable Option Key"
        self._FIELDS_UI['APP_OPTION_A_KEY'] = "Checkable Option (Group) A Key"
        self._FIELDS_UI['APP_OPTION_B_KEY'] = "Checkable Option (Group) B Key"
        self.APP_OPTION_KEY = 'APP_OPTION'
        self.APP_OPTION_A_KEY = 'APP_OPTION_A'
        self.APP_OPTION_B_KEY = 'APP_OPTION_B'


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
        S.ShowUI('App Template Settings')


if __name__ == '__main__':
    runmain()