Robot Pilot
===========

The Robot pilot plug-in allows you to move the robot by incremental steps. These increments can be done with respect to the active coordinate system, the tool or by joint increments. 

This plug-in complements the default robot panel in RoboDK by allowing you to move the robot the same way you can do with the teach pendant of a controller.


How to use
----------

Follow these steps to use the robot pilot menu.
1. Select **Tools-Robot pilot** in RoboDK to open the robot pilot window (docked on the left by default). If you don't see this option in the menu, make sure the robot pilot plug-in is loaded (Tools-Add-Ins).
2. Press **Select robot** if your robot was not automatically selected. This is required if you have more than one robot in your project.
3. Choose the type of incremental movement you would like to do: with respect to the active reference, the tool or joint movements.
4. Choose the step (in mm or deg)
5. Press the corresponding buttons to move the robot.

**Important**: Checking the **Run on robot option** will move the real robot if it the real robot is connected. Make sure the connection is properly established and you are operating in a safe environment.


More information
----------------

This plugin is open source and provided as a RoboDK Plug-In example. The source code is available on GitHub:
https://github.com/RoboDK/Plug-In-Interface/tree/master/Plugin-OPC-UA
