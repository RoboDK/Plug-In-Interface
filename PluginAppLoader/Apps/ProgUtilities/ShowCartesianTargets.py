# Show all cartesian targets and hides all others (sets visibility).
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink
import _progutils as putils


def runmain():
    RDK = robolink.Robolink()

    show_targets = putils.getCartesianTargets(RDK)

    RDK.Render(False)
    for target in putils.getTargets(RDK):
        if target in show_targets:
            target.setVisible(True)
        else:
            target.setVisible(False)
    RDK.Render(True)


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()