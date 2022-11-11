# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file deletes objects in a zone indefinitely using the preset settings.
# It can be called as an App action or within an App module.
#
# You can call it programmatically from a RoboDK program call.
# To use the zone ID #2, call DeleteObjectsLoop(2).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps

try:
    from ObjectDeleter import DeleteObjects  # Import as an App module. This is needed when the action is used externally, in a RoboDK script for instance.
    from ObjectDeleter import Settings
except:
    import DeleteObjects
    import Settings


def DeleteObjectsLoop(RDK=None, S=None):
    """
    This file deletes objects in a zone indefinitely using the preset settings.
    It can be called as an App action or within an App module.
    
    You can call it programmatically from a RoboDK program call.
    To use the zone ID #2, call DeleteObjectsLoop(2).
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    APP = roboapps.RunApplication(RDK)
    while APP.Run():
        if not DeleteObjects.DeleteObjects(RDK=RDK, S=S):
            break
        robomath.pause(0.1)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        # When calling this script from a RoboDK Program, add the ID in the program call: DeleteObjectsLoop(2)
        import sys
        id = 0
        if len(sys.argv) > 1:
            try:
                id = int(sys.argv[1])  # RoboDK will add 'Checked' when called from the toolbar
            except:
                pass

        RDK = robolink.Robolink()

        S = Settings.Settings('Object-Deleter-Settings-' + str(id))
        S.Load(RDK)

        DeleteObjectsLoop(RDK=RDK, S=S)


if __name__ == '__main__':
    runmain()
