# RoboDK Import-Export Settings

The Import-Export Settings App for RoboDK allows you to export and import all RoboDK global settings.
This allows sharing settings among different computers and create backups.

These settings are accessible from the menu `Tools->Options`.


## Features

This Add-in adds the following actions in the menu and the toolbar:

- Settings Import-Export
    - Export: Export the settings as an .INI file
    - Import: Import the settings from an .INI file
	
Note: The license settings are also exported and imported.


## Prerequisites
- [RoboDK](https://robodk.com/download) v5.7.2 or later
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
