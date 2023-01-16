# Robot Pilot

The Robot Pilot Plug-in for RoboDK allows you to move the robot by incremental steps from the GUI.
These increments can be done with respect to the active coordinate system, the tool or by joint increments.

This Plug-in complements the default robot panel in RoboDK by allowing you to move the robot the same way you can do with the teach pendant of a controller.


## Features
- Move the simulated or connected robot from the GUI
- Move relative to the active reference frame, tool or joint values
- Change the step size (mm or deg)


## Usage

Follow these steps to use the robot pilot menu.
1. Select **Tools-Robot pilot** in RoboDK to open the robot pilot window (docked on the left by default). If you don't see this option in the menu, make sure the robot pilot plug-in is loaded (Tools->Add-Ins).
2. Press **Select robot** if your robot was not automatically selected. This is required if you have more than one robot in your project.
3. Choose the type of incremental movement you would like to do: with respect to the active reference, the tool or joint movements.
4. Choose the step (in mm or deg)
5. Press the corresponding buttons to move the robot.

**Important**: Checking the **Run on robot option** will move the real robot if it the real robot is connected. Make sure the connection is properly established and you are operating in a safe environment.


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
