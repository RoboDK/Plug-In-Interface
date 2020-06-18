# Stop all programs and moving robots
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

RDK.Render(False)

programs = RDK.ItemList(ITEM_TYPE_PROGRAM)
robots = RDK.ItemList(ITEM_TYPE_ROBOT_ARM)

for itm in robots + programs:
    itm.Stop()
    

