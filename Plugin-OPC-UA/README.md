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
