# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Start all programs in the station in a loop.
# If multiple programs are found for the same robot, only the first one is executed.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps


def StartPrograms():
    """
    Start all programs in the station in a loop.
    If multiple programs are found for the same robot, only the first one is executed.
    """

    RDK = robolink.Robolink()

    RDK.Render(False)

    # List all programs and robots
    programs = RDK.ItemList(robolink.ITEM_TYPE_PROGRAM)
    robots = RDK.ItemList(robolink.ITEM_TYPE_ROBOT)

    # Prioritize main programs, if any
    programs = sorted(programs, key=lambda x: '0' if x.Name().lower().startswith('main') else x.Name())

    # Iterate through all programs
    for prog in programs:

        # Retrieve the link to the robot
        robot_link = prog.getLink(robolink.ITEM_TYPE_ROBOT)
        if not robot_link.Valid():
            continue

        # Start if it is a free robot
        if robot_link in robots:

            # Remove the robot from the list of robots to run
            robots.remove(robot_link)

            # Set program to loop
            prog.setParam("Loop", "1")

            # Run the program
            # Important! Update will recalculate the program.
            # This is needed before we run the program, otherwise subsequent calls may fail if the program is very long
            print("Running program: " + prog.Name())
            prog.Update()
            prog.RunCode()

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        StartPrograms()


if __name__ == '__main__':
    runmain()