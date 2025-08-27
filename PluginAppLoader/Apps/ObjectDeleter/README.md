# Object Deleter

The Object Deleter App for RoboDK adds customizable zones to delete objects.

- For more information about RoboDK Apps, visit the
[documentation](https://robodk.com/doc/en/PythonAPI/app.html).
- Submit bug reports and feature suggestions on our
[GitHub](https://github.com/RoboDK/Plug-In-Interface/issues).

## Feature

- Use the Editor to set the Object Deleter settings.
  - Radius: radius of the delete zone, in mm.
  - Delete location: RoboDK item (frame or station) of the zone's origin
- Use the Delete button to remove all objects in the zone using the Editor parameters.
- Add a python script in your station that will delete objects in the zone. Useful for when running a Program.
- Add a python script in your station that will delete objects in the zone indefinitely. Useful for when running a Program.
