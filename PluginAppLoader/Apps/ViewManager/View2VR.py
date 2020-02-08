# Set the current view in the RoboDK main window to the VR headset
from robolink import *
from robodk import *
import ast

# Start the RoboDK API
RDK = Robolink()
vp = RDK.ViewPose(vp)

result = RDK.Command("ViewPoseVR", str(Pose_2_TxyzRxyz(vp)))

if result == "OK":
    RDK.ShowMessage("Window view sent to VR headset")
else:
    RDK.ShowMessage("Problems setting VR view: " + result)