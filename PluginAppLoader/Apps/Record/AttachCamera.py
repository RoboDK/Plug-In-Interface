# This action is "checkable" as defined in the INI settings.
# Therefore, we can use the AttachCamera station parameter to detect if the button is checked or unchecked.
# This script will be triggered when the button is clicked (checked or unchecked)

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox


class RunApplication:
    """Class to detect when the terminate signal is emited.
    Example:
        run = RunApplication()
        while run.run:
            # your loop

    """
    run = True

    def __init__(self):
        import signal
        signal.signal(signal.SIGTERM, self.clean_exit)
        signal.signal(signal.SIGINT, self.clean_exit)  # ctrl + c

    def clean_exit(self, signum, frame):
        self.run = False


run = RunApplication()


def AttachCamera():
    RDK = Robolink()

    item2station_pose = eye(4)
    view_pose_last = eye(4)
    last_item = None

    # Get the file name of this file/script
    filename = getFileName(__file__)

    # Allow running an infinite loop if this script is run without the parameter AttachCamera
    infinite_loop = False
    if RDK.getParam(filename) is None:
        infinite_loop = True

    RDK.Render()

    #run = RunApplication()

    # Run until the station parameter AttachCamera is set to 0
    while infinite_loop or RDK.getParam(filename) == 1:
        #while run.run:
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


def runmain():
    # Make sure we don't run this file if we are unchecking it
    if len(sys.argv) >= 2:
        if sys.argv[1] == "Unchecked":
            print("This action is triggered by the uncheck action")
            quit()

    # Important: This setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called
    # This is needed if we want the user input to save the file
    #print("App Setting: Skip kill")
    #sys.stdout.flush()

    AttachCamera()


# Function to run when this module is executed on its own or by selecting the action button in RoboDK
if __name__ == "__main__":
    runmain()
