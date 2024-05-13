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
import os, time

ACTION_NAME = os.path.basename(__file__)


def SettingsExport():
    """Export the settings"""

    # path_files = RDK.getParam('PATH_OPENSTATION')
    from AppSettings import Settings

    path_files = os.path.expanduser("~/Desktop")

    S = Settings()
    S.Load()
    file_name = S.SETTINGS_NAME

    file_path = robodialogs.getSaveFileName(strtitle="Save RoboDK settings", path_preference=path_files, strfile=file_name, defaultextension='.ini', filetypes=[("INI files", "*.ini"), ("All files", "*.*")])
    if not file_path:
        return

    RDK = robolink.Robolink()
    if os.path.exists(file_path):
        os.remove(file_path)

    status = RDK.Command("Settings", "Save=" + file_path)
    exists = False
    for i in range(10):
        # This strange workaround is needed for MacOS, apparently it take some time for the file to be visible by the OS
        if os.path.exists(file_path):
            exists = True
            break

        time.sleep(0.05)

    if status == "OK" and exists:
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
