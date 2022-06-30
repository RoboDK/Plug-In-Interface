# Collapse the selected items and their childrens in the tree.
# This also collapse (Hide instructions) for Programs.
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink
import _progutils as putils


def runmain():
    RDK = robolink.Robolink()

    RDK.Render(False)

    def recurse(item):
        for child in item.Childs():
            putils.collapse(child)
            recurse(child)

    for item in RDK.Selection():
        putils.collapse(item)
        recurse(item)

    RDK.Render(True)


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()