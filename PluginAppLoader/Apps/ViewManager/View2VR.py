# Set the current view in the RoboDK main window to the VR headset
from robodk.robolink import *
from robodk.robomath import *
import ast

# Start the RoboDK API
RDK = Robolink()
vp = RDK.ViewPose()

result = RDK.Command("VR")
strpose = str(Pose_2_TxyzRxyz(transl(0, 0, +2000) * vp))[1:-1]
result = RDK.Command("ViewPoseVR", strpose)
print(strpose)

if result == "OK":
    RDK.ShowMessage("Window view sent to VR headset", False)
else:
    RDK.ShowMessage("Problems setting VR view: " + result, False)