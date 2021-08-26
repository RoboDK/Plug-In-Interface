Xbox Controller App for RoboDK
===========================

The Xbox Controller App allows you to control your robot arm using an Xbox One Controller.

To use this app, you can load the XboxController.apploader.rdkp file in this folder or manually copy the contents of this folder in your RoboDK Apps folder:

``` bash
C:/RoboDK/Apps/XboxController
```

Then, make sure the AppLoader is enabled (Shift+I) and this app is enabled (Shift+A).
Press the Controller icon in the toolbar to start the app, and click again to stop it.

By default, this app moves the simulated robot. You can also move the real robot if you are connected using the RoboDK driver for your robot controller:
* Select Connect-Connect robot
* Enter the IP of the robot
* Select Connect

Some robot controllers will require you to follow additional steps on the robot side. More information about RoboDK drivers here:
* https://robodk.com/doc/en/Robot-Drivers.html#UseDriver

More information about the RoboDK API for Python here:
* https://robodk.com/doc/en/RoboDK-API.html
* https://robodk.com/doc/en/PythonAPI/index.html

More information on RoboDK Apps here:
* https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader


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
