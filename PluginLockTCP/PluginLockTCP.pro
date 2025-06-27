#----------------- HELP --------------
# Help about RoboDK plugins here:
# https://robodk.com/CreatePlugin

# Clear some space in the General Messages window
message(".")
message(".")
message(".")
message(".")
message(".")
message("Useful tip that helps development: Enter RoboDK as executable and pass the argument /PLUGINSLOAD to start with all available plugins")
# Example to reload all plugins:
# C:/RoboDK/bin/RoboDK.exe "/PLUGINSLOAD"
# Example to load the plugin on the fly:
# C:/RoboDK/bin/RoboDK.exe "/PLUGINLOAD=C:/RoboDK/bin/plugins/pluginexample.dll"
#------------------------------------


#----------------- TEMPLATE --------- (Qt Plugin App template)
# Important: Do not change these values (unless you know what you are doing)
TEMPLATE        = lib
CONFIG         += plugin
#------------------------------------

*-clang* {
    QMAKE_CXXFLAGS_WARN_ON += -Wno-deprecated-declarations
    QMAKE_CXXFLAGS_WARN_ON += -Wno-deprecated-copy-with-user-provided-copy
}

*-g++* {
    QMAKE_CXXFLAGS_WARN_ON += -Wno-comment
    QMAKE_CXXFLAGS_WARN_ON += -Wno-deprecated-copy
}

# Add any Qt libraries you would like to use:
#QT += core gui
QT += widgets
QT += network   # Allows using QTcpSocket

# Define your plugin name (name of the DLL file generated)
TARGET          = PluginLockTCP



#-----------------------------------------------------
# Define the location to place the plugin library (release and/or debug binaries)
exists( "$$PWD/../../destdir_rdk_plugins.pri" ) {
include("$$PWD/../../destdir_rdk_plugins.pri")
DESTDIR = $$DESTDIR_RDK_PLUGINS
} else {
#-----------------------------------------------------
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
    PluginLockTCP.h

SOURCES += \
    PluginLockTCP.cpp 




#--------------------------
# Header and source files required by any RoboDK plugin
# Do not change this section, make sure to have the robodk_interface folder up one folder
HEADERS += \
    ../robodk_interface/iitem.h \
    ../robodk_interface/irobodk.h\
    ../robodk_interface/iapprobodk.h \
    ../robodk_interface/robodktypes.h \
    ../robodk_interface/robodktools.h \
    ../robodk_interface/matrix4x4.h \
    ../robodk_interface/vector3.h \
    ../robodk_interface/deprecated.h \
    ../robodk_interface/constants.h \
    ../robodk_interface/joints.h \

SOURCES += \
    ../robodk_interface/robodktools.cpp \
    ../robodk_interface/robodktypes.cpp \
    ../robodk_interface/matrix4x4.cpp \
    ../robodk_interface/vector3.cpp \
    ../robodk_interface/joints.cpp

INCLUDEPATH += ../robodk_interface
#--------------------------
