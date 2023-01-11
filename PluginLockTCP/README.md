# Lock TCP

The Lock TCP Plug-in for RoboDK adds the ability to lock the TCP position for a 6 axis robot mounted on a synchronized external axis.


## Features

- Lock the the robot's tool position so that the TCP absolute position is kept
- Reject out-of-reach positions
- Change the lock state through the API


## Usage

This example adds a "Lock TCP" checkable menu item when right-clicking a tool.

![Lock TCP menu](./doc/menu.PNG)


### Behaviour

Locking the TCP will allow the external axis to move the robot base while keeping the tool position. New pose in limit cases, such as new joints configuration or robot fully extended, will be rejected.


|  Original lock position              | Moved back position                  |
| ------------------------------------ | ------------------------------------ |
| ![Locked pose 1](./doc/locked_1.PNG) | ![Locked pose 2](./doc/locked_2.PNG) |


### Run from API

Here's a sample code to use this plugin through the API.

```
from robodk.robolink import ITEM_TYPE_TOOL, Robolink

RDK = Robolink()

item = RDK.ItemUserPick("Select TCP to lock", ITEM_TYPE_TOOL)
if not item.Valid():
    quit()

if RDK.PluginCommand("Lock TCP", "LOCK", item.Name()) != "OK":
    RDK.ShowMessage('Failed to lock TCP of %s. Ensure the plugin is enabled (Shift+I)' % item.Name())
    quit()
RDK.ShowMessage('Locked TCP of %s' % item.Name())

# Try it out!

if RDK.PluginCommand("Lock TCP", "UNLOCK", item.Name()) != "OK":
    RDK.ShowMessage('Failed to unlock TCP of %s' % item.Name())
RDK.ShowMessage('Unlocked TCP of %s' % item.Name())
```


## Prerequisites
- [RoboDK](https://robodk.com/download)


## Installation

Plug-ins are usually packaged as RoboDK Packages (.rdkp), which are automatically installed when opened with RoboDK.
To manually install this Plug-in, copy the content of this folder to your RoboDK Plug-ins folder (typically `C:/RoboDK/bin/plugins`).


## Configuration

1. Enable the Plug-in (Tools->Add-ins or Shift+I)


## About RoboDK Plug-ins

The RoboDK Plug-In Interface allows you to extend or customize RoboDK software with Plug-ins linked natively into the core of RoboDK.

You can integrate your Plug-in as part of the RoboDK user interface and easily customize RoboDK for offline programming and simulation purposes.
For instance, by adding buttons in the menu and the toolbar, processing events, synchronizing with render, accept API command calls, and more.

Once you complete developing your Plug-in, you can easily distribute your Plug-in as a self-contained package file (.rdkp).

Plug-ins are handled by RoboDK with the Add-in Manager, and the [Plug-In Interface](https://github.com/RoboDK/Plug-In-Interface) provides the necessary C++ tools to build your Plug-in.

You can find more information about the Plug-In Interface and sample Plug-ins in the [Plug-In Interface GitHub](https://github.com/RoboDK/Plug-In-Interface) and the [documentation](https://robodk.com/doc/en/PlugIns/index.html).
