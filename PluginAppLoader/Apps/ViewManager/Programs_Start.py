# Start all programs. If multiple programs are found for the same robot, only the first one is executed
# Start the RoboDK API
from robodk.robolink import *  # RoboDK API

RDK = Robolink()

RDK.Render(False)

RDK.Command("SingularityTolerance", 0.5)
#RDK.Command("TolerancePickCurve", -1)
#RDK.Command("TolerancePickPoiny", -1)

# List all programs and robots to stop
programs = RDK.ItemList(ITEM_TYPE_PROGRAM)
robots = RDK.ItemList(ITEM_TYPE_ROBOT_ARM)

# Iterate through all programs
for prog in programs:
    # Retrieve the link to the robot
    robot_pri = prog.getLink(ITEM_TYPE_ROBOT)

    # Start if it is a free robot
    if robot_pri in robots:
        # Remove the robot from the list of robots to run
        robots.remove(robot_pri)
        print("Running program: " + str(prog))

        # Run the program
        # Important! Update will recalculate the program.
        # This is needed before runprogram otherwise, subsequent calls may fail if the program is very long
        prog.Update()
        prog.RunProgram()

        # Set program to loop
        prog.setParam("Loop", "1")
