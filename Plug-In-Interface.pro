# This file builds all plugins from the public repository RoboDK/Plug-In-Interface

linux{
#QMAKE_CXXFLAGS_WARN_OFF -= -Wunused-parameter
QMAKE_CXXFLAGS+=-Wno-unused-parameter
QMAKE_CXXFLAGS+=-Wno-unused-variable
QMAKE_CXXFLAGS+=-Wno-comment
}

# CONFIG += ordered

TEMPLATE = subdirs

SUBDIRS += PluginAppLoader/AppLoader.pro
SUBDIRS += PluginExample/PluginExample.pro
SUBDIRS += PluginLockTCP/PluginLockTCP.pro
win32 {
SUBDIRS += Plugin-OPC-UA/PluginOPCUA.pro
SUBDIRS += PluginOpenGL/PluginOpengl.pro
SUBDIRS += PluginOpenGL-Shaders/PluginChip8Opengl.pro
}
SUBDIRS += PluginRealTime/PluginRealTime.pro
SUBDIRS += PluginRobotPilot/PluginRobotPilot.pro
