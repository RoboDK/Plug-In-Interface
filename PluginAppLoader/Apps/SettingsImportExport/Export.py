# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Action to export RoboDK settings as an INI file
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps, robodialogs
import os

ACTION_NAME = os.path.basename(__file__)


def SettingsExport():
    """Export the settings"""
    
    # path_files = RDK.getParam('PATH_OPENSTATION')
    from AppSettings import Settings
    
    path_files = os.path.expanduser("~/Desktop")
    
    S = Settings()
    S.Load()
    file_name = S.SETTINGS_NAME    
    #file_name = "RoboDK-Settings.ini"

    file_path = robodialogs.getSaveFileName(strtitle="Save RoboDK settings", path_preference=path_files, strfile=file_name, defaultextension='.ini', filetypes=[("INI files", "*.ini"), ("All files", "*.*")])
    if not file_path:
        return

    RDK = robolink.Robolink()
    if RDK.Command("Settings", "Save=" + file_path) == "OK" and os.path.exists(file_path):
        RDK.ShowMessage("Successfully saved RoboDK settings to " + file_path, False)
    else:
        RDK.ShowMessage("Failed to export RoboDK settings. Make sure you are using the latest version of RoboDK.")


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SettingsExport()


if __name__ == '__main__':
    runmain()