# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Take a screenshot of the 3D view with the current screen resolution and prompt the user to save the image.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, robodialogs, roboapps
import datetime

import Settings


def TakeSnapshot(RDK=None, S=None):
    """
    Take a screenshot of the 3D view with the current screen resolution and prompt the user to save the image.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    date_str = datetime.datetime.now().strftime("%H-%M-%S")
    path_rdk = RDK.getParam('PATH_OPENSTATION')
    file_name = "RoboDK-Screenshot-" + date_str + ".png"

    file_path = robodialogs.getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension='.png', filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
    if not file_path:
        return

    if RDK.Command("Snapshot", file_path) != 'OK':
        RDK.ShowMessage("Snapshot save failed: " + file_path, False)
        return

    RDK.ShowMessage("Snapshot saved: " + file_path, False)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        TakeSnapshot()


if __name__ == '__main__':
    runmain()