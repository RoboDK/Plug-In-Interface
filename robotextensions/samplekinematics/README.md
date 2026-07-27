# RoboDK Robot Kinematics Interface

This folder shows how to build a **custom kinematics library** for RoboDK. Unlike the plugins in the rest of this repository (which extend RoboDK's UI and behavior via `IAppRoboDK`), a kinematics library replaces the forward/inverse kinematics solver RoboDK uses for a specific robot. This makes it possible to integrate robots with non-generic kinematics (for example, non-spherical wrists) or to plug in a proprietary/vendor solver instead of RoboDK's default iterative solution.

Robot kinematics libraries are supported since **RoboDK 6.0**.

## What it is

`samplekinematics` compiles to a small, dependency-free shared library (DLL/SO/DYLIB) that exports four C functions:

- **`SolveFK`** — forward kinematics: joints → flange pose.
- **`SolveFK_CAD`** — forward kinematics including the pose of every intermediate joint, used to drive the 3D robot model.
- **`SolveIK`** — inverse kinematics: pose → one or more joint solutions (with an optional list of alternate configurations).
- **`Joints2Config`** — computes the robot configuration flags (front/rear, upper/lower arm, flip) for a given joint set.

Each function can return `-1` to fall back to RoboDK's own generic/default calculation, so you only need to implement the functions your robot actually requires.

`samplekinematics.cpp` includes a fully working reference implementation of a generic serial robot (DHM-based forward kinematics, matrix multiplication/inversion helpers, and accessors for the robot's base/tool adaptors, joint limits, joint senses and DHM parameters passed in via `ptr_robot`). It is meant to be read and adapted, not used as-is — the `SolveIK` sample in particular just returns two dummy joint solutions.

## Building

This is a plain qmake project — it does not depend on Qt at all (`CONFIG -= qt`, `TEMPLATE = lib`):

```bash
qmake samplekinematics.pro
make            # or nmake/jom on Windows
```

The `.pro` file places the compiled library directly into RoboDK's `robotextensions` folder:

- **Windows release:** `C:/RoboDK/bin/robotextensions`
- **Windows debug:** `C:/RoboDK/bind/robotextensions`
- **macOS:** `~/RoboDK/RoboDK.app/Contents/MacOS/robotextensions`
- **Linux:** `~/RoboDK/bin/robotextensions`

## Using it in RoboDK

1. Double-click the robot in the station tree.
2. Select **Parameters**.
3. Under **Robot Kinematics**, click **Options**.
4. Click **Select Library** and choose your compiled library.

More information: [RoboDK Plug-In documentation — Link Custom Kinematics](https://robodk.com/doc/en/PlugIns/index.html#LinkKinematics).

## Real-world example: FANUC CRX kinematics

For a production-grade example of this interface in use, see [frfournier/robodk_crx_kinematics](https://github.com/frfournier/robodk_crx_kinematics), a community project that implements custom kinematics for the FANUC CRX collaborative robot family (CRX-5iA, CRX-10iA, CRX-10iA-L, CRX-30iA). 

The FANUC CRX has a non-spherical wrist, which RoboDK's default generic/iterative solver cannot handle reliably — the project instead implements a closed-form geometric solver (based on published research by M. Abbes and G. Poisson) that reduces the 6-axis inverse kinematics problem to 1D root finding, enumerates valid postures, and verifies candidates via forward kinematics. It implements all four callbacks described above (`SolveFK`, `SolveFK_CAD`, `SolveIK`, `Joints2Config`), builds on the Eigen linear algebra library, and includes a Python-based regression test suite alongside pre-configured robot/station assets.
