# Box Spawner

The Box Spawner App for RoboDK lets you programmatically add box objects in your RoboDK Station.
You can customize the spawner location, box parameters, and request a new box from a RoboDK Program.
Multiple spawner location are supported by providing a spawner ID in your program call.

- For more information about RoboDK Apps, visit the
[documentation](https://robodk.com/doc/en/PythonAPI/app.html).
- Submit bug reports and feature suggestions on our
[GitHub](https://github.com/RoboDK/Plug-In-Interface/issues).


## Features

### Editor

Use the Editor to set the spawner settings.
- Units: mm or in
- Box size L/W/H in the above units (or X/Y/Z)
- Spawn location: RoboDK item (frame or station) where the box will be spawn
- Conveyor relocation: automatically transfer the box to the closest conveyor
- Randomization: randomize the position, orientation and scale of the box


### Spawner

Use the spawner button to create a new box in you station using the Editor parameters.
The spawner button defaults to the spawner ID #0.


### Add Python Script

Add a python script in your station that will spawn a box when called. Useful for spawning boxes in a Program.
For example, the Program call `Call SpawnBox(2)` will use the spawner ID #2.


## Prerequisites
- [RoboDK](https://robodk.com/download)
- [RoboDK API](https://pypi.org/project/robodk/) (bundled with RoboDK)
- Content of requirements.txt, if any (automatically installed by RoboDK)


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
