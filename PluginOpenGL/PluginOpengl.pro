#----------------- HELP --------------
# Help about RoboDK plugins here:
# https://robodk.com/CreatePlugin

# Note: You can load a plugin while RoboDK is running
message(".")
message(".")
message(".")
message(".")
message(".")
message("Useful tip that helps debugging: Enter RoboDK as executable and pass the DLL of your plugin using -PLUGINLOAD=path-to-dll")
# Example to reload all plugins:
# C:/RoboDK/bin/RoboDK-GL2.exe "-PLUGINSLOAD"
#
# Example to load the plugin on the fly:
#     C:/RoboDK/bin/RoboDK-GL2.exe "-PLUGINLOAD=C:/RoboDK/bin/plugins/pluginexample.dll"
#
# Example to load ONLY this plugin:
#     C:/RoboDK/bin/RoboDK-GL2.exe "-PLUGINSUNLOAD -PLUGINLOAD=%{CurrentProject:FileBaseName}
# You can also select Tools-PlugIns and manually load a plugin
#------------------------------------


#----------------- TEMPLATE --------- (Qt Plugin App template)
# Important: Do not change these values (unless you know what you are doing)
TEMPLATE        = lib
CONFIG         += plugin
#------------------------------------


# Add any Qt libraries you would like to use:
#QT += core gui
QT += widgets
QT += network



#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# **** Important notes for OpenGL using the RoboDK Plug-In interface: ****
# This example shows how to call plain OpenGL commands (2)
# There are 2 ways of drawing OpenGL with RoboDK:
#
# (1) If you are using shaders you should use the default binary  -->  RoboDK.exe
#     Important: Using RoboDK allows you to use RoboDK shaders. To draw primitives (Triangles, Lines or points you should call RDK->DrawGeometry)

# (2) If you are using Desktop OpenGL (no shaders), you should use the GL2 compatible binary --> RoboDK-GL2.exe
#     Important: Using RoboDK-GL2 allows you to use PushMatrix(), MulMatrix, PopMatrix(), GLBegin(), GLEnd(), etc.
#
# The following is required to build with OpenGL libraries
QT += opengl
LIBS += opengl32.lib
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*


# Define your plugin name (new DLL file generated)
TARGET          = PluginOpenGL

*-clang* {
    QMAKE_CXXFLAGS_WARN_ON += -Wno-deprecated-declarations
    QMAKE_CXXFLAGS_WARN_ON += -Wno-deprecated-copy-with-user-provided-copy
}

*-g++* {
    QMAKE_CXXFLAGS_WARN_ON += -Wno-comment
    QMAKE_CXXFLAGS_WARN_ON += -Wno-deprecated-copy
}

#-----------------------------------------------------
# Define the location to place the plugin library (release and/or debug binaries)
exists( "$$PWD/../../destdir_rdk_plugins.pri" ) {
include("$$PWD/../../destdir_rdk_plugins.pri")
DESTDIR = $$DESTDIR_RDK_PLUGINS
} else {
CONFIG(release, debug|release) {

    message("Using release binaries.")
    message("Select Projects-Run-Executable and set to C:/RoboDK/bin/RoboDK.exe ")
    win32{
        #Default path on Windows
        DESTDIR  = C:/RoboDK/bin/plugins
    } else {
    macx {
        # Default path on MacOS
        DESTDIR  = ~/RoboDK-Dev/Deploy/RoboDK.app/Contents/MacOS/plugins
    } else {
        #Default path on Linux
        DESTDIR  = ~/RoboDK/bin/plugins
    }
    }

} else {

    message("Using debug binaries: Make sure you start the debug version of RoboDK ( C:/RoboDK/bind/ ). ")
    message("Select Projects-Run-Executable and set to C:/RoboDK/bind/RoboDK.exe ")
    message("(send us an email at info@robodk.com to obtain debug binaries that should go to the bind directory)")
    win32{
        #Default path on Windows (debug)
        DESTDIR  = C:/RoboDK/bind/plugins
    } else {
    macx {
        # Default path on MacOS (debug)
        DESTDIR  = ~/RoboDK-Dev/Deploy/RoboDK.app/Contents/MacOS/plugins
    } else {
        #Default path on Linux (debug)
        DESTDIR  = ~/RoboDK/bind/plugins
    }
    }

}
}

#--------------------------
# Add header and source files (use File->New File or Project and add your files)
# This can be modified manually or automatically by Qt Creator
HEADERS += \
    pluginopengl.h

SOURCES += \
    pluginopengl.cpp


#--------------------------
# Header and source files required by any RoboDK plugin
# Do not change this section, make sure to have the robodk_interface folder up one folder
HEADERS += \
    ../robodk_interface/iitem.h \
    ../robodk_interface/irobodk.h\
    ../robodk_interface/iapprobodk.h \
    ../robodk_interface/robodktypes.h \
    ../robodk_interface/robodktools.h \

SOURCES += \
    ../robodk_interface/robodktools.cpp \
    ../robodk_interface/robodktypes.cpp

INCLUDEPATH += ../robodk_interface
#--------------------------
