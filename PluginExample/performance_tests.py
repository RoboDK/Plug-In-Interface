# Run some performance tests of RoboDK using the RoboDK API for Python

# You can also use the new version of the API:
from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
import random
import time

# Start the RoboDK API
RDK = robolink.Robolink()

robot = RDK.Item("", robolink.ITEM_TYPE_ROBOT_ARM)

print(robot.Name())

# Retrieve the joint limits as a list to retrieve random sets of robot joints
j_low, j_high, _ = robot.JointLimits()
j_low = j_low.list()
j_high = j_high.list()
def joints_rand():
    return [random.uniform(l, h) for l, h in zip(j_low, j_high)]

# TODO: Implement tests of the SolveFK function (robot.SolveFK on random joints)
# run robot.SolveFK(randomjoints) multiple times

# TODO: Implement tests of the SolveIK function (robot.SolveIK on random joints)
# run robot.SolveFK(randomjoints) multiple times



# TODO: Implement tests of

# Program example:
t_start = time.time()
t_check = t_start + 4
count = 0

# Turn off automatic rendering (usualy immediately after a call that updates the scene)
RDK.Render(False)
# Turn collisions off on each setJoints, we'll retrieve the collision status using Collisions()
RDK.setCollisionActive(robolink.COLLISION_OFF)
while time.time() < t_check:
    joints = joints_rand()
    robot.setJoints(joints)

    # Provokes an update to refresh the position of every robot, tool, object in the scene without rendering
    RDK.Update()

    # Calculate collisions
    # TODO: Collect number of collisions and show the report of the number of times a collision was found vs not found
    print(RDK.Collisions())

    count = count + 1

t_end = time.time()

# Show metrics
# TODO: Improve presentation of the results to include:
# collision check time (per sample or call to RDK.Collisions())
# Collision rate per second (samples per second)
t_delta = t_end - t_start
print(t_delta)
print(count/t_delta)
