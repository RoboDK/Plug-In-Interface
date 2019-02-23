#----------------- HELP --------------
# Help about RoboDK plugins here:
# https://robodk.com/CreatePlugin

# Clear some space in the General Messages window
message("")
message("")
message("")
message("")
message("")
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


# Add any Qt libraries you would like to use:
#QT += core gui
QT += widgets
QT += network   # Allows using QTcpSocket

# Define your plugin name (name of the DLL file generated)
TARGET          = PluginExample


# Define the location to place the plugin library
CONFIG(debug, debug|release) {

message("Using debug binaries: Make sure you start the debug version of RoboDK ( C:/RoboDK/bind/ ). ")
message("Select Projects-Run-Executable and set to C:/RoboDK/bind/RoboDK.exe ")
message("(send us an email at info@robodk.com to obtain debug binaries that should go to the bind directory)")
DESTDIR  = C:/RoboDK/bind/plugins   #Default path on Windows
#DESTDIR  = ~/RoboDK/Applications/RoboDK.app/Contents/MacOS/RoboDK # Default path on MacOS
#DESTDIR  = ~/RoboDK/bind/RoboDK     #Default path on Linux

} else {

message("Using release binaries.")
message("Select Projects-Run-Executable and set to C:/RoboDK/bin/RoboDK.exe ")
DESTDIR  = C:/RoboDK/bin/plugins   #Default path on Windows
#DESTDIR  = ~/RoboDK/Applications/RoboDK.app/Contents/MacOS/RoboDK # Default path on MacOS
#DESTDIR  = ~/RoboDK/bin/RoboDK     #Default path on Linux

}


#--------------------------
# Header and source files required by any Qt application as a RoboDK plugin
# Do not change this section
HEADERS += \
    robodk_interface/iitem.h \
    robodk_interface/irobodk.h\
    robodk_interface/iapprobodk.h \
    robodk_interface/robodktypes.h \
    robodk_interface/robodktools.h \

SOURCES += \
    robodk_interface/robodktools.cpp \
    robodk_interface/robodktypes.cpp

INCLUDEPATH += robodk_interface
#--------------------------


#--------------------------
# Add header and source files (use File->New File or Project and add your files)
# This can be modified manually or automatically by Qt Creator


HEADERS += \
    pluginexample.h \
    formrobotpilot.h

SOURCES += \
    pluginexample.cpp \
    formrobotpilot.cpp

FORMS += \
    formrobotpilot.ui

RESOURCES += \
    resources1.qrc

