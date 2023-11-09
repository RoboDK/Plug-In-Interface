# Program Utilities

The Program utilities App for RoboDK adds tools to edit programs and program instructions.

- For more information about RoboDK Apps, visit the
[documentation](https://robodk.com/doc/en/PythonAPI/app.html).
- Submit bug reports and feature suggestions on our
[GitHub](https://github.com/RoboDK/Plug-In-Interface/issues).


## Features

### Convert MoveC to MoveL

Right-click one or more programs to convert any MoveC command in a series of linear movements (MoveL).
The default step size is 1 mm, or 1 degree. You can edit this settings in the ConvertMoveC.py.
A new program will be created after the conversion.


### Expand sub-program calls

Right-click one or more programs to expand (inline) any sub-program calls.
By default, this process is recursive (sub-programs in sub-programs are also inline). You can edit this settings in the ExpandSubPrograms.py.
A new program will be created.


### Merge programs

Right-click two or more programs to merge them.
A new program will be created.


### Visibility utilities

- Right-click one or more programs in the tree to show the targets in the program(s) and hide all others.
- Right-click one or more robots in the tree to show the targets linked to the robot(s) and hide all others.
- Right-click one or more targets in the tree to set the visibility of joint, cartesian or all targets.

### Others
- Toggle "Run on Robot" for a program and all its subprograms
- Recover a program with missing item links (deleted robots, copied from another station, etc.)
- Reverse a program, taking motion type into account (auto backward exit)
- Start/stop all programs in the station

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
