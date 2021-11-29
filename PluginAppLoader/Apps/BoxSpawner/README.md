Box Spawner
============

Editor
-----------
Use the Editor to set the spawner settings.
- Units: mm or in
- Box L/W/H in the above units
- Spawn location: RoboDK item (frame or station) where the box will be spawn
- Conveyor relocation [optional]: Reassign the box from the spawn location to this location to attach it to a conveyor. Leave Unset or Clear to disable this option
- Defaults: Set all parameters to default
- OK: Save the current settings and close the editor
- Cancel or X: Discard changes and close the editor

Spawner
--------------

Use the spawner button to create a new box in you station using the Editor parameters.

Add Python Script
----------------------

Add a python script in your station that will spawn a box when called. Useful for spawning boxes in a Program.