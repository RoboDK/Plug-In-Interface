# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Spawns a box using the preset settings.
# It can be called as an App action or within an App module.
#
# You can call it programmatically from a RoboDK program call.
# To use the spawner ID #2, call SpawnBox(2).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps
import random
import os

try:
    from BoxSpawner import Settings  # Import as an App module. This is needed when the action is used externally, in a RoboDK script for instance.
except:
    import Settings


def SpawnBox(RDK=None, S=None):
    """
    Spawns a box using the preset settings.
    It can be called as an App action or within an App module.

    You can call it programmatically from a RoboDK program call.
    To use the spawner ID #2, call SpawnBox(2).
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Check if the parent exists
    PARENT_NAME = S.SPAWN_FRAME[1][S.SPAWN_FRAME[0]]
    PARENT = RDK.Item(PARENT_NAME)
    if not PARENT.Valid() or PARENT.Name() != PARENT_NAME or PARENT.Type() not in [robolink.ITEM_TYPE_STATION, robolink.ITEM_TYPE_FRAME]:
        RDK.ShowMessage(f"Unable to find the parent frame ({PARENT_NAME})! Did you set the settings?")
        return None

    # Check that the required files exists
    USE_METRIC = S.UNITS_TYPE[0] == 0

    # Attempt to recover the file location when used as a module
    if not os.path.exists(S.REF_BOX_MM_PATH):
        S.REF_BOX_MM_PATH = os.path.normpath(os.path.dirname(os.path.abspath(Settings.__file__)) + '/' + os.path.basename(S.REF_BOX_MM_PATH))
    if not os.path.exists(S.REF_BOX_IN_PATH):
        S.REF_BOX_IN_PATH = os.path.normpath(os.path.dirname(os.path.abspath(Settings.__file__)) + '/' + os.path.basename(S.REF_BOX_IN_PATH))

    if not USE_METRIC and not os.path.exists(S.REF_BOX_IN_PATH):
        RDK.ShowMessage(f"Unable to find the resource file ({S.REF_BOX_IN_PATH})!")
        return None
    elif USE_METRIC and not os.path.exists(S.REF_BOX_MM_PATH):
        RDK.ShowMessage(f"Unable to find the resource file ({S.REF_BOX_MM_PATH})!")
        return None

    RDK.Render(False)

    # Add the object
    if USE_METRIC:
        new_box = RDK.AddFile(S.REF_BOX_MM_PATH, PARENT)
    else:
        new_box = RDK.AddFile(S.REF_BOX_IN_PATH, PARENT)
    new_box.setVisible(False)

    # Set the initial size
    new_box.Scale(S.BOX_SIZE_XYZ)
    RDK.Update()

    # Randomize
    new_box.setPose(robomath.eye(4))
    pose = new_box.Pose()

    scale = 1.0
    if S.ENABLE_RANDOM_SIZE:
        scale = random.uniform(S.RANDOM_SIZE[0], S.RANDOM_SIZE[1])
        new_box.Scale(scale)
        RDK.Update()

    if S.ENABLE_RANDOM_POSITION:
        x = random.uniform(-S.RANDOM_POSITION[0], S.RANDOM_POSITION[0]) if S.RANDOM_POSITION[0] != 0. else 0.
        y = random.uniform(-S.RANDOM_POSITION[1], S.RANDOM_POSITION[1]) if S.RANDOM_POSITION[1] != 0. else 0.
        z = random.uniform(-S.RANDOM_POSITION[2], S.RANDOM_POSITION[2]) if S.RANDOM_POSITION[2] != 0. else 0.
        pose = robomath.RelTool(pose, x, y, z)

    if S.ENABLE_RANDOM_ORIENTATION:
        rx = random.uniform(-S.RANDOM_ORIENTATION[0], S.RANDOM_ORIENTATION[0]) if S.RANDOM_ORIENTATION[0] != 0. else 0.
        ry = random.uniform(-S.RANDOM_ORIENTATION[1], S.RANDOM_ORIENTATION[1]) if S.RANDOM_ORIENTATION[1] != 0. else 0.
        rz = random.uniform(-S.RANDOM_ORIENTATION[2], S.RANDOM_ORIENTATION[2]) if S.RANDOM_ORIENTATION[2] != 0. else 0.
        pose = robomath.RelTool(pose, 0, 0, 0, rx, ry, rz)

    new_box.setPose(pose)
    RDK.Update()

    # Set name according to new size
    sx, sy, sz = robomath.mult3(S.BOX_SIZE_XYZ, scale)
    new_box.setName((S.BOX_ITEM_NAME_MM if USE_METRIC else S.BOX_ITEM_NAME_IN) % (sx, sy, sz))

    # Attach to the closest conveyor
    if S.RELOCATE_TYPE[0] != 0:

        if S.RELOCATE_TYPE[0] == 1:
            # Closest conveyor
            parent_pos = PARENT.PoseAbs().Pos()
            conveyors = [x for x in RDK.ItemList(robolink.ITEM_TYPE_ROBOT_AXES) if len(x.Joints().tolist()) == 1]
            conveyors = sorted(conveyors, key=lambda x: robomath.distance(parent_pos, x.PoseAbs().Pos()))
            if not conveyors:
                RDK.ShowMessage("Unable to find any conveyor to attach too!")
                new_box.Delete()
                return None

            conveyor = conveyors[0]
            if robomath.distance(parent_pos, conveyor.PoseAbs().Pos()) > S.MAX_CONV_DISTANCE:
                RDK.ShowMessage(f"Unable to find any conveyor close enough to attach to (closest is at {robomath.distance(parent_pos, conveyor.PoseAbs().Pos()):.1f} mm)!")
                new_box.Delete()
                return None

            frames = [x for x in conveyor.Childs() if x.Type() == robolink.ITEM_TYPE_FRAME]
            if not frames:
                frames = [RDK.AddFrame(conveyor.Name() + ' Frame', conveyor)]
            new_box.setParentStatic(frames[0])

        elif S.RELOCATE_TYPE[0] == 2:
            # Specific frame
            NEW_PARENT_NAME = S.RELOCATE_FRAME[1][S.RELOCATE_FRAME[0]]
            NEW_PARENT = RDK.Item(NEW_PARENT_NAME)
            if not NEW_PARENT.Valid() or NEW_PARENT.Name() != NEW_PARENT_NAME or NEW_PARENT.Type() not in [robolink.ITEM_TYPE_STATION, robolink.ITEM_TYPE_FRAME]:
                RDK.ShowMessage(f"Unable to find the parent frame ({NEW_PARENT_NAME})! Did you set the settings?")
                return None
            new_box.setParentStatic(NEW_PARENT)

    new_box.setVisible(True)
    RDK.Render(True)

    return new_box


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        # When calling this script from a RoboDK Program, add the ID in the program call: SpawnBox(2)
        import sys
        id = 0
        if len(sys.argv) > 1:
            try:
                id = int(sys.argv[1])
            except:
                pass

        RDK = robolink.Robolink()

        S = Settings.Settings('Box-Spawner-Settings-' + str(id))
        S.Load(RDK)

        SpawnBox(RDK=RDK, S=S)


if __name__ == '__main__':
    runmain()
