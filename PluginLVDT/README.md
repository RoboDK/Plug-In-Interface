Linear gage Plug-in for RoboDK
===================================================

This example shows how to dynamically move a linear gage sensor, such as an LVDT, according to TCP(s) making contact.

* The linear gage must be a 1 axis mechanism, with the base frame Z axis pointing outwards.
* The linear gage limits are expected to be from 0 mm (fully extended) to >0 mm (fully engaged).
* It is assume that the gage is spring loaded, and when no TCP are within reach, will fully extend.
* The user can activate a linear gage simulation by right-clicking the Item.
  * A prompt will appear to enter the surface radius
* All TCPs will affect the gage travel, unless they are not visible.

<p align="center"><img src="./doc/linear-gage.png" width="50%"/></p>
