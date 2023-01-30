# Game Controller

The Game Controller App for RoboDK allows you to control your robot arm using a game controller.

- For more information about RoboDK Apps, visit the
[documentation](https://robodk.com/doc/en/PythonAPI/app.html).
- Submit bug reports and feature suggestions on our
[GitHub](https://github.com/RoboDK/Plug-In-Interface/issues).


## Features

- Supports multiple controllers
- Jog your robot using [RoboDK Drivers](https://robodk.com/doc/en/Robot-Drivers.html#RobotDrivers)


## Usage

Press the Controller icon in the toolbar to start the app, and click again to stop it. Status updates will be available on the status bar of RoboDK (bottom of the screen).

By default, this app moves the simulated robot. You can also move the real robot if you are connected using the RoboDK driver for your robot controller:
- Select Connect-Connect robot
- Enter the IP of the robot
- Select Connect

Some robot controllers will require you to follow additional steps on the robot side. More information about RoboDK drivers here:
- https://robodk.com/doc/en/Robot-Drivers.html#UseDriver


### Controller mapping

The default mapping was created for an Xbox One controller.
- Press and hold X (X axis), Y (Z axis) or B (Z axis) to select an axis.
- Use the D-pad up or down to move the robot along the selected axis.
- Use the D-pad left or right to increase/decrease the steps.
- Press the left joystick to toggle between translation (default) and rotation.
- Press the right joystick to toggle between MoveJ (default) and MoveL.
- Press both bumpers to Home.
- **Use the right trigger to engage the safeguard and enable movements.**


### Settings

You can edit the settings to suit your needs, such as robot speeds, step size, step range, initial settings, etc.


## Prerequisites
- [RoboDK](https://robodk.com/download)
- [RoboDK API](https://pypi.org/project/robodk/) (bundled with RoboDK)
- Content of requirements.txt, if any (automatically installed by RoboDK)
- A game controller


## Installation

Apps are usually packaged as RoboDK Packages (.rdkp), which are automatically installed when opened with RoboDK.
To manually install this App, copy this folder to your RoboDK Apps folder (typically `C:/RoboDK/Apps`).


## Configuration

1. Enable the Add-in Loader (Tools->Add-ins or Shift+I)
2. Enable the App (Tools->AppLoader or Shift+A)


## About RoboDK Apps

RoboDK allows you to easily load scripts and executable files as if they were plug-ins in RoboDK software.

You can integrate scripts as part of the RoboDK user interface and easily customize RoboDK for offline programming and simulation purposes. Adding scripts to an App will add buttons in the menu and the toolbar automatically. A settings file allows you to easily customize the appearance of a specific set of buttons/actions.

Once you complete developing your App you can easily distribute your App as a self-contained package file (.rdkp).

Apps are handled by RoboDK with the AppLoader Add-in, and [roboapps](https://robodk.com/doc/en/PythonAPI/robodk.html#roboapps-py) provides the necessary Python tools to build your App.

You can find more information about the AppLoader and sample Apps in the [AppLoader GitHub](https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader) and the [documentation](https://robodk.com/doc/en/PythonAPI/app.html).

For more information about the RoboDK API for Python, visit our [RoboDK documentation](https://robodk.com/doc/en/RoboDK-API.html) and the [RoboDK Python API documentation](https://robodk.com/doc/en/PythonAPI/index.html).
