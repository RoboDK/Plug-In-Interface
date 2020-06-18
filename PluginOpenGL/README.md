Example to draw OpenGL in the 3D view of RoboDK
===========================

This example shows how to call plain OpenGL commands (2). 

There are 2 ways of drawing OpenGL with RoboDK: 

1. If you are using shaders you should use the default binary: C:/RoboDK/bin/**RoboDK**.exe. Using RoboDK with this binary allows you to use RoboDK shaders. To draw primitives such as Triangles, Lines or points you should call RDK->DrawGeometry.

2. If you are using Desktop OpenGL (no shaders), you should use the GL2 compatible binary: C:/RoboDK/bin/**RoboDK-GL2**.exe. This binary allows you to use PushMatrix(), MulMatrix(), PopMatrix(), GLBegin(), GLEnd(), etc.


Qt Project settings
=======     

*.pro file
----------
     
The following configuration is required in the PRO file to build with support for OpenGL:
* QT += opengl
* LIBS += opengl32.lib


Run settings
-----------

You should enter the following information in the **Projects-Run settings** window:
* Executable: **C:/RoboDK/bin/RoboDK-GL2.exe**
* Arguments: **-PLUGINSUNLOAD -PLUGINLOAD=%{CurrentProject:FileBaseName}**