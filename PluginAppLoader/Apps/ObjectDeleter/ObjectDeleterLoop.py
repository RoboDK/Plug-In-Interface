# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import Robolink  # RoboDK API
from robodk import pause
import ObjectDeleterTools as odt

RDK = Robolink()

while True:
    odt.loadParameters(RDK)
    objects = odt.objectsInZone(RDK)
    for obj in objects:
        obj.Delete()
    pause(0.1)