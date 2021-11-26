# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import Robolink  # RoboDK API
import SpawnBoxTools as spt

RDK = Robolink()
spt.loadParameters(RDK)
spt.createBox(RDK)