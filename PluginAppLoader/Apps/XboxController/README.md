Xbox Controller App for RoboDK
===========================

The Xbox Controller App let's you control your robot with an Xbox One Controller as a RoboDK checkable App.

More information about the RoboDK API for Python here:
* https://robodk.com/doc/en/RoboDK-API.html
* https://robodk.com/doc/en/PythonAPI/index.html

More information on RoboDK Apps here:
* https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader

To use this app, ensure the AppLoader is enabled (Shift+I) and this app is enabled (Shift+A).
Press the Controller icon on the toolbar to start the app, and click again to stop it.
To move the real robot, ensure it is connected before starting the app: RoboDK->Connect->Connect robot->Connect.

Controller mapping
==================
* Press and hold X (X axis), Y (Z axis) or B (Z axis) to select an axis.
* Use the D-pad up or down to move the robot along the selected axis.
* Use the D-pad left or right to increase/decrease the steps.
* Press the left joystick to toggle between translation (default) and rotation.
* Press the right joystick to toggle between MoveJ (default) and MoveL.
* Press both bumpers to Home.
* Use the right trigger to engage the safeguard.

Settings
========
You can edit the XboxController.py script to suit your needs, such as robot speeds, step size, step range, initial settings, etc.
