# Object Deleter

The Object Deleter Add-in for RoboDK adds customizable zones to delete objects.

## Features

- Use the Editor to set the Object Deleter settings.
  - Radius: radius of the delete zone, in mm.
  - Delete location: RoboDK item (frame or station) of the zone's origin
- Use the Delete button to remove all objects in the zone using the Editor parameters.
- Add a Python script in your station that will delete objects currently in the zone once, on demand. Useful for a one-off cleanup step in a Program.
- Add a Python script in your station that will continuously monitor the zone and delete objects as they enter it. Useful for running alongside a Program.
