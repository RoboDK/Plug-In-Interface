# Surface Pattern Generator

The Surface Pattern Generator (SPG) App for RoboDK lets you generate simple surface patterns on an object surface.

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
