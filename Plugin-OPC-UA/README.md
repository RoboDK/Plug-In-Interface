# OPC UA

The OPC UA Plug-in for RoboDK allows you to add OPC UA compatibility to your RoboDK projects.
This Plug-in can be used as an OPC UA server and/or an OPC UA client.

The OPC UA (Open Platform Communications Unified Architecture) is a cross-platform, open-source, IEC62541 standard for data exchange from sensors to cloud applications developed by the OPC Foundation.

OPC UA provides a platform independent service-oriented architecture that integrates all the functionality of the classic OPC into one extensible framework.


## Features

- Add RoboDK as a OPC UA server and/or an OPC UA client
- Retrieve or set station parameters and robot joints


## Usage

### How to use OPC UA as a server

Select **OPC UA-Start OPC UA server** to start the server. You can also select the corresponding button in the toolbar.

You should see a message in the status bar that shows the port the server is available in. The default port for OPC UA communication is 4840.

With the server running you should see the following OPC UA variables and functions exposed:
- **RoboDK**: this tag means you are connected to RoboDK and provides the RoboDK version in the description as a string. Example: `RoboDK 64 bit v5.5.1.22569`
- **SimulationSpeed** this tag provide the current simulation speed ratio. For example, a value of 5 means that RoboDK is simulating 5 times faster.
- **StationParameter** this tag allows you to specify what station variable you want to get or set. Right click on a station and select **Station Variables** to see or edit station variables.
- **StationValue** this tag allows you to see the value of the station parameter you chose with **StationParameter**. Changing this value will change the station value in RoboDK.
- **getJointsStr** this function allows you to get the robot joint values of a robot as a string.
- **setJointsStr** this function allows you to set the robot joint values of a robot as a string.
- **getJoints** this function is the same as getJointsStr but retrieves the robot joint values as a list of doubles.
- **setJoints** this function is the same as setJointsStr but sets the robot joint values as a list of doubles.

You can select **OPC UA-OPC UA Settings** to see additional communication settings, such as the server port, start or stop the server.

**Tip:** You can use software like UaExpert by Unified Automation to connect to the endpoint and check the status.

**Note:** Station variables can be managed automatically, using the UI or the API when you simulate digital inputs or digital outputs.


### How to use OPC UA as a client

Select **OPC UA-Start OPC UA client** to connect to an endpoint and retrieve all the nodes as station variables. Right click on a station and select **Station Variables** to see or edit station variables.

You can select **OPC UA-OPC UA Settings** to specify the endpoint to connect to (server).


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
