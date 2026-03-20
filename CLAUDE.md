# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **RoboDK Plug-In Interface** — a C++/Qt framework for building native plugins that extend RoboDK (industrial robot simulation software). Plugins compile to DLL/SO/DYLIB files and are loaded directly into RoboDK's core, making them 10-100x faster than the standard RoboDK API.

## Build Commands

All projects use **qmake** (not CMake). Open a `.pro` file in Qt Creator, or build from the command line:

**Windows (Qt 5.15, MSVC2019):**
```bash
qmake Plug-In-Interface.pro -spec win32-msvc CONFIG+=qtquickcompiler CONFIG+=Release
jom.exe   # or: nmake
```

**Linux/macOS:**
```bash
qmake Plug-In-Interface.pro CONFIG+=qtquickcompiler CONFIG+=Release
make
```

To build a single plugin, run qmake/make inside its subdirectory (e.g., `PluginExample/PluginExample.pro`).

There are no automated tests — plugins are tested manually by loading them in RoboDK via **Tools → Plug-Ins**.

## Qt Version Requirements

| Platform | Qt Version | Compiler |
|----------|-----------|----------|
| Windows  | 5.15      | MSVC2019 |
| macOS    | 6.10 (≥RoboDK 6.0), 5.15 (older) | clang 64-bit |
| Linux    | 6.10 (≥RoboDK 6.0), 5.12 (older) | GCC |

**The Qt version must match exactly what RoboDK was compiled with**, or the plugin will fail to load.

## Plugin Output Locations

Compiled plugins must be placed in RoboDK's plugin directory:
- **Windows release:** `C:/RoboDK/bin/plugins/`
- **Windows debug:** `C:/RoboDK/bind/plugins/`
- **macOS:** `~/RoboDK.app/Contents/MacOS/plugins/`
- **Linux:** `~/RoboDK/bin/plugins/`

## Architecture

### Core Interface (`robodk_interface/`)

All plugins include this shared interface via:
```qmake
include($$PWD/../robodk_interface/robodk_interface.pri)
```

Key headers:
- **`irobodk.h`** — Main RoboDK API (100+ methods: robot control, simulation, file I/O)
- **`iitem.h`** — Represents any object in the station tree (robot, frame, tool, program, etc.)
- **`iapprobodk.h`** — Base class that every plugin must implement
- **`robodktypes.h`** — Shared enums and type definitions
- **`matrix4x4.h`**, **`vector3.h`**, **`joints.h`** — Math utilities

### Plugin Lifecycle

Every plugin implements `IAppRoboDK` and receives pointers to `IRoboDK` and `IItem`. Key behavioral notes:
- **Items are pointers**, not value objects — check for `nullptr` before use
- **Screen updates are manual** — call a render event explicitly after changing robot positions
- Qt signals/slots are used for all UI callbacks and are thread-safe

### Plugin Structure Pattern

Each plugin follows this structure:
```
PluginXxx/
├── PluginXxx.pro       # qmake project (CONFIG += plugin)
├── pluginxxx.h/.cpp    # IAppRoboDK implementation
└── [widget files]      # Optional docked Qt widgets
```

### Add-in Apps (`PluginAppLoader/Apps/`)

Python-based apps loaded via the `PluginAppLoader` C++ plugin. Each app in its own subdirectory follows the same `IAppRoboDK` interface conventions but runs as Python scripts rather than compiled DLLs.

### Robot Extensions (`robotextensions/samplekinematics/`)

Custom kinematics libraries that RoboDK loads separately. Must export `SolveFK()`, `SolveFK_CAD()`, and `SolveIK()` functions.

## Starting a New Plugin

Copy `PluginExample/` as a template. It demonstrates:
- Plugin registration and lifecycle hooks
- Adding menu items and toolbar buttons
- Docked widget creation
- Timing/performance benchmarking of the RoboDK API

## Deployment

Plugins are packaged as `.rdkp` Add-in files using the RoboDK Add-in Manager. See the [Add-ins documentation](https://robodk.com/doc/en/Add-ins.html#AddinManager).
