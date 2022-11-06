# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file adds the Box Spawner script to your RoboDK station.
# You can then call it programmatically from a RoboDK program call.
# To use the spawner ID #2, call SpawnBox(2).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk.robolink import Robolink
import os

RDK = Robolink()
script = RDK.AddFile(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/SpawnBox.py'))
script.setName('SpawnBox')