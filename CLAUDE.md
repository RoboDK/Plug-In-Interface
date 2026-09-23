# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **RoboDK Plug-In Interface** — a C++/Qt framework for building native plugins that extend RoboDK (industrial robot simulation software). Plugins compile to DLL/SO/DYLIB files and are loaded directly into RoboDK's core, making them much faster than the standard RoboDK API. The repo also ships Python-based **Add-ins** (under `PluginAppLoader/Apps/`) that need no compilation.

Two different kinds of work live here, and they have different toolchains:
- **C++ plugins** (`Plugin*/`, `robodk_interface/`) — qmake + Qt, must match RoboDK's exact Qt version.
- **Python add-ins** (`PluginAppLoader/Apps/*/`) — plain `.py` scripts using the `robodk` PyPI package; no build step.

## Build Commands (C++ plugins)

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

The top-level `Plug-In-Interface.pro` builds all plugins as `SUBDIRS`. `Plugin-OPC-UA`, `PluginOpenGL`, `PluginOpenGL-Shaders`, and `PluginRoboUI` are gated behind `win32 { }` and only build on Windows.

Generated build files (`Makefile*`, `release/`, `debug/`, `moc_*`, `ui_*.h`, `*.pro.user`) are gitignored; do not commit them.

### Output location

Each `.pro` sets `DESTDIR` directly to RoboDK's plugin folder, so a successful build installs the plugin:
- **Windows release:** `C:/RoboDK/bin/plugins/`
- **Windows debug:** `C:/RoboDK/bind/plugins/` (requires debug RoboDK binaries from RoboDK)
- **macOS:** `~/RoboDK-Dev/Deploy/RoboDK.app/Contents/MacOS/plugins/`
- **Linux:** `~/RoboDK/bin/plugins/`

A `destdir_rdk_plugins.pri` file two directories above the plugin (i.e. next to the repo's parent) overrides this via `DESTDIR_RDK_PLUGINS`, if it exists.

### Testing

There are no automated tests. Plugins are tested manually by loading them in RoboDK via **Tools → Plug-Ins**, or by launching RoboDK with a command-line flag:
```bash
RoboDK.exe -PLUGINSLOAD                                          # start with all available plugins loaded
RoboDK.exe -PLUGINLOAD=C:/RoboDK/bin/plugins/pluginexample.dll   # load one plugin on the fly
```
In Qt Creator, set Projects → Run → Executable to `RoboDK.exe` with `-PLUGINSLOAD` so the plugin loads on run. If a plugin fails to load or builds strangely, delete the build folder / old library and rebuild.

### CI

`.github/workflows/plug-in-interface.yml` builds the whole tree on pull requests to `master` (Windows Qt 5.15.2, Ubuntu Qt 5.12.0, macOS Qt 5.15.2). Changes limited to `*.md`, `PluginAppLoader/Apps/`, or `robodk_interface/` do not trigger it.

## Qt Version Requirements

| Platform | Qt Version | Compiler |
|----------|-----------|----------|
| Windows  | 5.15      | MSVC2019 |
| macOS    | 6.10 (≥RoboDK 6.0), 5.15 (older) | clang 64-bit |
| Linux    | 6.10 (≥RoboDK 6.0), 5.12 (older) | GCC |

**The Qt version must match exactly what RoboDK was compiled with**, or the plugin will fail to load. The interface headers can also change between major RoboDK versions (`robodk_interface/Version.txt` records the supported range).

## Architecture

### Core Interface (`robodk_interface/`)

All plugins include this shared interface via:
```qmake
include($$PWD/../robodk_interface/robodk_interface.pri)
```

Key headers:
- **`iapprobodk.h`** — Base class `IAppRoboDK` every plugin implements. Also holds the Doxygen main page for the whole interface and the `TypeEvent`/`TypeApiEvent`/`TypeClick` enums.
- **`irobodk.h`** — Main RoboDK API (`IRoboDK`, aliased `RoboDK`): station tree access, simulation, file I/O, `Render()`.
- **`iitem.h`** — `IItem` (aliased `Item`): any object in the station tree (robot, frame, tool, program, etc.). Delete items with `IItem::Delete`, never the destructor.
- **`robodktypes.h`** — `Mat` (poses), `tJoints`, `tMatrix2D`, and shared enums.
- **`robodktools.h`** — Helpers: `ItemValid()`, `AddDockWidget()`, string/double conversions.
- **`stationtreeeventmonitor.h`** — `robodk::StationTreeEventMonitor`, a QObject that watches the station tree widget and emits `itemAdded/itemRemoved/itemNameChanged/itemIconChanged` signals with filter flags.
- **`matrix4x4.h`**, **`vector3.h`**, **`joints.h`**, **`legacymatrix2d.h`** — Math utilities.

### Plugin Lifecycle (`IAppRoboDK`)

RoboDK calls these hooks; only `PluginName()` is pure virtual:
- `PluginLoad(mw, menubar, statusbar, rdk, settings)` — receives the `QMainWindow`, menu bar, and the `IRoboDK*`; add menus/dock widgets here.
- `PluginLoadToolbar(mw, iconsize)` — add toolbar buttons.
- `PluginItemClick(item, menu, click_type)` / `PluginItemClickMulti(...)` — extend context menus or react to clicks on tree items.
- `PluginCommand(command, value)` — receive string commands (from the API or other plugins).
- `PluginEvent(event_type)` — `EventRender`, `EventChanged`, `EventMoved`, and the `EVENT_*` API events (selection changed, item moved, robot moved, key press, etc.).
- `PluginUnload()`.

Behavioral notes:
- **Items are pointers**, not value objects — check `ItemValid()` / `nullptr` before use.
- **Screen updates are manual** — call `IRoboDK::Render()` after changing robot positions or poses.
- Qt signals/slots are used for all UI callbacks and are thread-safe.
- Wrap user-visible strings in `tr()` for Qt Linguist translation.

### Plugin Structure Pattern

Each plugin follows this structure:
```
PluginXxx/
├── PluginXxx.pro       # qmake project (TEMPLATE = lib, CONFIG += plugin, includes robodk_interface.pri)
├── pluginxxx.h/.cpp    # IAppRoboDK implementation
├── manifest.xml        # Add-in Manager package metadata (title, version, assets)
├── README.md
└── [widget files]      # Optional docked Qt widgets (.ui + .h/.cpp)
```

`PluginExample/` is the minimal template to copy for a new plugin. `PluginAppLoader/` is the most complete real-world example (dialogs, `.rdkp` unpacking via bundled miniz in `zip/`, launching Python/executable scripts).

### Add-in Apps (`PluginAppLoader/Apps/`)

Python-based add-ins loaded by the `PluginAppLoader` C++ plugin (bundled with RoboDK, disabled by default) or by RoboDK's built-in Add-in Manager. `Apps/README.md` is the canonical format reference; `Apps/AppTemplate/` is the documented starting point for a new add-in.

Format essentials:
- Each add-in is one subfolder. Every `.py` (or executable) inside becomes a menu item and toolbar button. Files starting with `_` are ignored as actions and serve as shared modules (e.g. `_AppUtilities.py`, `_cutools.py`).
- An image with the same base name as a script (SVG preferred) becomes its icon; a `...Checked.svg` variant is used for the checked state.
- `AppConfig.ini` is auto-generated on first load and controls menu name/parent/priority, toolbar area, and per-action settings (`Checkable`, `CheckableGroup`, `Shortcut`, `TypeOnContextMenu`, `TypeOnDoubleClick`, `DeveloperOnly`, etc.).
- Scripts use `from robodk import robolink, robomath, roboapps`. Entry point is `runmain()`; checkable actions branch on `roboapps.Unchecked()` and loop on `roboapps.RunApplication().Run()`. Persistent per-station settings with auto-generated UI subclass `roboapps.AppSettings`.
- Optional files: `requirements.txt` (pip deps RoboDK pre-installs), `manifest.xml` (Add-in Manager metadata), `__init__.py` (makes the folder importable from other scripts; RoboDK adds each add-in folder to `PYTHONPATH`), `AppLink.ini` (points to an add-in stored elsewhere).

Helper scripts in `Apps/`:
- `PackageCreate.py` — pack every add-in in `Apps/` into `Package.apploader.rdkp`.
- `PackageCreateOne.py` — pack a single add-in folder.
- `PackageExtract.py` — unpack an `.rdkp`.
- `CompileApp.py` — compile an add-in's `.py` files to `.pyc` and package the result as an `.rdkp`.

### Robot Extensions (`robotextensions/samplekinematics/`)

Custom kinematics libraries that RoboDK loads separately from the plugin interface (no Qt needed). Must export `SolveFK()`, `SolveFK_CAD()`, and `SolveIK()`; installed into `C:/RoboDK/bin/robotextensions` and selected per robot under Parameters → Robot Kinematics → Options → Select Library.

## Deployment

Plugins and add-ins are packaged as `.rdkp` Add-in files using the RoboDK Add-in Manager. See the [Add-ins documentation](https://robodk.com/doc/en/Add-ins.html#AddinManager). Each plugin and add-in includes a `manifest.xml` (title, version, description, asset list) consumed by the Add-in Manager when packaging. Built `.rdkp` files are not tracked in git.

## Useful Links

- Plug-In interface docs: https://robodk.com/doc/en/PlugIns/index.html
- Python API reference (used by add-ins): https://robodk.com/doc/en/PythonAPI/index.html
- Standard RoboDK API (separate project): https://github.com/RoboDK/RoboDK-API
