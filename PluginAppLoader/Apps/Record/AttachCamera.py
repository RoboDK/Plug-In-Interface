# This action is "checkable" as defined in the INI settings.
# Therefore, we can use the AttachCamera station parameter to detect if the button is checked or unchecked.
# This script will be triggered when the button is clicked (checked or unchecked)

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox


def AttachCamera():
    RDK = Robolink()

    item2station_pose = eye(4)
    view_pose_last = eye(4)
    last_item = None

    RDK.Render()

    run = RunApplication()
    while run.Run():
        # Retrieve user selection
        selected_items = RDK.Selection()
        if len(selected_items) <= 0:
            last_item = None
            continue

        # Use the first selected item to attach the camera
        item = selected_items[0]

        # Prevent selecting programs or instructions or anything that doesn't move
        if item.type == ITEM_TYPE_ROBOT or item.type == ITEM_TYPE_TOOL or item.type == ITEM_TYPE_FRAME or item.type == ITEM_TYPE_OBJECT or item.type == ITEM_TYPE_TARGET:
            item_pose = item.PoseAbs()  # Selected item pose with respect to the station reference
            item2station_pose = item_pose.inv()

            if last_item != item:
                # If it is the first time we select this item: update the relationship camera 2 item pose
                view_pose = RDK.ViewPose()  # View Pose (camera pose with respect to the station reference)
                camera2item_pose = (item2station_pose * view_pose.inv()).inv()
                msg = 'Camera attached to %s' % item.Name()
                print(msg)
                RDK.ShowMessage(msg, False)
                last_item = item

            else:
                # calculate the new view pose and udpate it
                view_pose = camera2item_pose * item2station_pose

                # Only update if the view pose changed
                if view_pose != view_pose_last:
                    view_pose_last = view_pose
                    RDK.setViewPose(view_pose)
                    RDK.Render()


class RunApplication:
    """Class to detect when the terminate signal is emited to stop an action.

    .. code-block:: python

        run = RunApplication()
        while run.Run():
            # your main loop to run until the terminate signal is detected
            ...

    """
    time_last = -1
    param_name = None
    RDK = None

    def __init__(self, rdk=None):
        if rdk is None:
            from robolink import Robolink
            self.RDK = Robolink()
        else:
            self.RDK = rdk

        self.time_last = time.time()
        if len(sys.argv) > 0:
            path = sys.argv[0]
            folder = os.path.basename(os.path.dirname(path))
            file = os.path.basename(path)
            if file.endswith(".py"):
                file = file[:-3]
            elif file.endswith(".exe"):
                file = file[:-4]

            self.param_name = file + "_" + folder
            self.RDK.setParam(self.param_name, "1")  # makes sure we can run the file separately in debug mode

    def Run(self):
        time_now = time.time()
        if time_now - self.time_last < 0.25:
            return True
        self.time_last = time_now
        if self.param_name is None:
            # Unknown start
            return True

        keep_running = not (self.RDK.getParam(self.param_name) == 0)
        return keep_running


def Unchecked():
    """Verify if the command "Unchecked" is present. In this case it means the action was just unchecked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Unchecked" in sys.argv[1:]:
            return True

    return False


def Checked():
    """Verify if the command "Checked" is present. In this case it means the action was just checked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Checked" in sys.argv[1:]:
            return True

    return False


def runmain():
    # Verify if this is an action that was just unchecked
    if Unchecked():
        quit(0)
    else:
        # Checked (or checkable status not applicable)
        AttachCamera()


if __name__ == "__main__":
    # Important: leave the main function as runmain if you want to compile this app
    runmain()
