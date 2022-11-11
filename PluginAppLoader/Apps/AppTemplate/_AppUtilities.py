# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Sharable module, ignored by the AppLoader when prefixed with '_'.
# Sharable modules are not considered as actions and not required in the AppConfig.ini.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink


def ShowMessage(RDK, action_name, message, popup):
    """Prefix a message with the action name and forwards it to robodk.robolink.Robolink.ShowMessage."""
    s = '\n\n' if popup else ' '
    RDK.ShowMessage(f"{action_name}:{s}{message}", popup)


if __name__ == '__main__':
    """
    There is no need for an entrypoint for sharable modules, as they are not expected to be run standalone.
    """
    pass