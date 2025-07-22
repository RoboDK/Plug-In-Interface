# Game Controller

The Game Controller Add-In allows you to control your robot arm using a game controller. You can control your robot using game controllers like the Microsof Xbox, PlayStation or the Nintendo Wii.

## Features

- Supports multiple controllers
- Jog your robot using [RoboDK Drivers](https://robodk.com/doc/en/Robot-Drivers.html#RobotDrivers)


## Usage

Press the Controller icon in the toolbar to start the Add-In, and click again to stop it. Status updates will be available on the status bar of RoboDK (bottom of the screen).

By default, this Add-In moves the simulated robot. You can also move the real robot if you are connected using the robot driver via RoboDK:
- Select Connect-Connect robot
- Enter the IP of the robot
- Select Connect

Some robot controllers will require you to follow additional steps on the robot side to configure your robot to work with drivers. You can find more information about RoboDK drivers here:
- https://robodk.com/doc/en/Robot-Drivers.html#UseDriver


### Controller mapping

The default mapping was created for an Xbox One controller.
- Press and hold X (X axis), Y (Z axis) or B (Z axis) to select an axis.
- Use the D-pad up or down to move the robot along the selected axis.
- Use the D-pad left or right to increase/decrease the steps.
- Press the left joystick to toggle between translation (default) and rotation.
- Press the right joystick to toggle between MoveJ (default) and MoveL.
- Press both bumpers to Home.
- **Use the right trigger to engage the safeguard and enable movements.**


### Settings

You can change the built-in settings to match your needs, such as robot speeds, step size, step range, initial settings, etc.

## Supported hardware

- Xbox 360 Controller via USB cable
- Xbox One Controller via USB cable
- All USB Keyboards
- All USB Mice
- Laptop built in keyboard and touchpads
- PS4 Controller via USB cable (supported on Linux only)
- PS3 Controller via USB cable (supported on Linux only)
- Pi-Hut SNES Style USB Gamepad (supported on Linux only)
- Wii controller (supported on Linux only)



## Prerequisites
- A game controller supported by this Add-In