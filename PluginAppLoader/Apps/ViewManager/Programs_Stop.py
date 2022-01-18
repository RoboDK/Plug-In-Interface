# Stop all programs and moving robots
from robodk.robolink import *    # RoboDK API
RDK = Robolink()

RDK.Render(False)

programs = RDK.ItemList(ITEM_TYPE_PROGRAM)
robots = RDK.ItemList(ITEM_TYPE_ROBOT_ARM)

for itm in robots + programs:
    itm.Stop()
    

