# Attach Object

The Attach Object Plug-in for RoboDK can dynamically attach multiple objects to a robot link.

## Features

- Attached objects will be updated to track the robot movements
- An object can be attached once, and a robot can have multiple objects attached to multiple links
- The user can attach and detach objects by right-clicking an object, multiple objects, or a robot

| Dress Pack (multiple objects)           | Robot                                   | Robot + Dress Pack                            |
| --------------------------------------- | --------------------------------------- | --------------------------------------------- |
| ![Parts](./doc/parts-view-portrait.png) | ![Robot](./doc/robot-view-portrait.png) | ![Assembly](./doc/assembly-view-portrait.png) |


## Usage

### Attaching and detaching objects from RoboDK

Attach or detach an object or multiple objects to the same robot link by right-clicking them (either in the tree or in the cell). Attach and detach menus will be present according to the state of the selected objects.
If more than one robot is present in the station, a selection prompt will appear.

Attached objects will conserve their relative position to the robot when the object is attached. Place them correctly before attaching them.

![Objects menu](./doc/object-menus.png)

Attach or detach an object or multiple objects to the same robot link by right-clicking a robot (either in the tree or in the cell). Attach and detach menus will be present according to the state of the selected robot.
If more than one object is present in the station, a selection prompt will appear.

![Attaching objects](./doc/robot-menus.png)


Once the objects an the robot are selected, a prompt will appear to select the link ID to attach. For instance, to attach an object on the last link of a six axis robot, enter 6.

![Attaching objects](./doc/joint-entry.png)

### Attaching and detaching objects from the API

Here's a sample code to use this plugin through the API.

```
from robodk.robolink import *
from robodk.robodialogs import *

RDK = Robolink()

robot = RDK.ItemUserPick("Select robot", ITEM_TYPE_ROBOT)
objects = RDK.ItemList(ITEM_TYPE_OBJECT, list_names=True)

# Expected format: "Attach", "Joint|Robot|Object|". Attaches Object to Robot at Joint
#                  "Detach", "Object". Detach Object from any Robot
#                  "Detach", "Robot". Detach all Objects from Robot

dof = len(robot.Joints().list())
for obj in objects:

    entry = mbox("Robot link to attach %s?" % obj, entry=str(dof))
    if entry == False:
        continue
    link = int(entry)

    value = "%i|%s|%s" % (link, robot.Name(), obj)
    result = RDK.PluginCommand("Plugin Attach Object", "Attach", value)
    RDK.ShowMessage(value + " -> " + result, False)
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
