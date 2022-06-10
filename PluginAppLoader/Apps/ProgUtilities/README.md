Program Utilities
===================

This app adds program utilities to RoboDK.

Convert MoveC to MoveL
------------------------
Right-click one or more programs to convert any MoveC command in a series of linear movements (MoveL).

The default step size is 1 mm, or 1 degree. You can edit this settings in the ConvertMoveC.py.

A new program will be created after the conversion.


Expand sub-program calls
--------------------------
Right-click one or more programs to expand (inline) any sub-program calls.

By default, this process is recursive (sub-programs in sub-programs are also inline). You can edit this settings in the ExpandSubPrograms.py.

A new program will be created.


Merge programs
--------------------------
Right-click two or more programs to merge them.

A new program will be created.


Visibility utilities
--------------------------
* Right-click one or more programs in the tree to show the targets in the program(s) and hide all others.
* Right-click one or more robots in the tree to show the targets linked to the robot(s) and hide all others.
* Right-click one or more targets in the tree to set the visibility of joint, cartesian or all targets.