RoboDK Plug-In example to draw OpenGL in the RoboDK 3D view
===========================

This example shows how to call plain OpenGL commands (2). There are 2 ways of drawing OpenGL with RoboDK: 

1. If you are using shaders you should use the default binary:
C:/RoboDK/bin/RoboDK.exe

Important: Using RoboDK allows you to use RoboDK shaders. To draw primitives (Triangles, Lines or points you should call RDK->DrawGeometry)

2. If you are using Desktop OpenGL (no shaders), you should use the GL2 compatible binary:
C:/RoboDK/bin/RoboDK-GL2.exe
 
Important: Using RoboDK-GL2 allows you to use PushMatrix(), MulMatrix(), PopMatrix(), GLBegin(), GLEnd(), etc.




Qt Project settings
=======     

*.pro file
----------
     
The following code is required in the PRO file to build with support for OpenGL:
* QT += opengl
* LIBS += opengl32.lib


Run settings
-----------

You should enter the following information in the Projects-Run settings:
* Executable: C:/RoboDK/bin/RoboDK-GL2.exe
* Arguments: -PLUGINSUNLOAD -PLUGINLOAD=%{CurrentProject:FileBaseName}