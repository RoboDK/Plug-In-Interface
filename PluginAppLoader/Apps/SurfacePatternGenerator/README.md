# Surface Pattern Generator

The Surface Pattern Generator (SPG) App for RoboDK let's you generate simple surface patterns on an object surface.

- For more information about RoboDK Apps, visit the
[documentation](https://robodk.com/doc/en/PythonAPI/app.html).
- Submit bug reports and feature suggestions on our
[GitHub](https://github.com/RoboDK/Plug-In-Interface/issues).


## Features

- Define a region of interest (size, step size)
- Create connected or discontinued lines on surfaces
- Distribute points along the lines
- Create multi-passes with vertical offsets
- Automatically create a Curve Follow Project on creation


## Usage

### Setup
- Place a Frame in the station at the same level in the tree as the object and with the desired name of the CFP
- Orient the frame so that the Z axis points towards the object surface, and the X and Y axis in the desired orientation


### Generating the pattern
- Open the SPG App and select the desired object
- Enter the pattern settings, such as the dimensions and resolution of the pattern, the tool settings, etc.
- Update the pattern to see the generate lines, CFP, and program
- Save the settings


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
