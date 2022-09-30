# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robodk.robolink import Robolink  # RoboDK API
from BoxSpawner import SpawnBoxTools as spt

RDK = Robolink()
spt.loadParameters(RDK)
spt.createBox(RDK)