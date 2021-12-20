# This script is part of the app "Record" and allows saving a RoboDK simulation as an AVI video file

# This action is "checkable" as defined in the INI settings.
# Therefore, we can use the Record station parameter to detect if the button is checked or unchecked.
# This script will be triggered when the button is clicked (checked or unchecked)

from robolink import *  # API to communicate with RoboDK
from robodk import *  # import the robodk library (robotics toolbox)

import_install("cv2", "opencv-python")
import_install("numpy")
import cv2  #if is not installed in your system run in terminal " pip install opencv-python "
import numpy as np  #if is not installed in your system run in terminal " pip install numpy "
import os
import datetime
import tempfile
import sys


def RecordProgram():

    # Define the frames per second:
    FRAMES_PER_SECOND = 24

    # Define the video extension (you may need to change the codec)
    #VIDEO_EXTENSION = ".avi"
    VIDEO_EXTENSION = ".mp4"

    # Choose the codec (mp4v, XVID or DIVX)
    #FOURCC = cv2.VideoWriter_fourcc(*'DIVX') # good quality (avi)
    #FOURCC = cv2.VideoWriter_fourcc(*'XVID') # low quality (avi)
    FOURCC = cv2.VideoWriter_fourcc(*'mp4v')  # good quality (mp4)

    # Default screenshot style:
    SNAPSHOT_STYLE = "Snapshot"

    # Other snapshot styles are not recommended, otherwise it will create a delay and a lot of flickering
    # Instead, change the appearance of RoboDK in the menu Tools-Options-Display
    #SNAPSHOT_STYLE = "SnapshotWhite"
    #SNAPSHOT_STYLE = "SnapshotWhiteNoText"
    #SNAPSHOT_STYLE = "SnapshotNoTextNoFrames"

    PREFER_SOCKET = True # If available, prefer socket (usually faster) over temporary file to retrieve the image

    #-------------------------------------------------------------------
    # Use a temporary folder
    with tempfile.TemporaryDirectory(prefix='Record_') as td:

        RDK = Robolink()

        file_video_temp = os.path.join(td, 'RoboDK_Video' + VIDEO_EXTENSION)

        video = None
        frame = None
        use_socket = PREFER_SOCKET  
        render_time_last = 0
        time_per_frame = 1 / FRAMES_PER_SECOND

        app = RunApplication()
        while app.Run():
            tic()

            # There's no need to get a new image if no render as occurred.
            render_time = int(RDK.Command("LastRender"))
            if (render_time_last != render_time):
                render_time_last = render_time

                def getSnapshot(use_socket, tempdir):
                    fallback = False
                    if use_socket:
                        # Socket method. Added in version 5.3.2
                        try:
                            bytes_img = RDK.Cam2D_Snapshot('', None)  # None means station and will throw before version 5.3.2
                            if isinstance(bytes_img, bytes) and bytes_img != b'':
                                return True, cv2.imdecode(np.frombuffer(bytes_img, np.uint8), cv2.IMREAD_UNCHANGED)
                        except Exception:
                            fallback = True
                            pass

                    # Fallback to tempfile method
                    tf = tempdir + '/temp.png'
                    if RDK.Command(SNAPSHOT_STYLE, tf) == 'OK':
                        return not fallback, cv2.imread(tf)

                    return False, None

                # Get the station snapshot
                success, frame = getSnapshot(use_socket, td)
                if not success:
                    if use_socket:
                        use_socket = False
                    else:
                        RDK.ShowMessage("Problems retrieving the RoboDK image buffer", False)
                        break

            # Write the frame to the video file
            if video is None:
                # Requires at least one frame to extract the frame size.
                height, width = frame.shape[:2] 
                video = cv2.VideoWriter(file_video_temp, FOURCC, FRAMES_PER_SECOND, (width, height))
            video.write(frame)

            # Wait some time, if necessary, to have accurate frame rate
            elapsed = toc()
            if elapsed < time_per_frame:
                t_sleep = time_per_frame - elapsed
                print("Waiting for next frame: " + str(t_sleep))
                pause(t_sleep)

        print("Done recording")

        # Check if nothing was saved
        if video is None:
            quit()
        video.release()

        # Save the file
        msg_str = "Saving video recording... "
        print(msg_str)
        RDK.ShowMessage(msg_str, False)

        # Create a suggested file name
        print("Saving video...")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        path_rdk = RDK.getParam('PATH_DESKTOP')  # or path_rdk = RDK.getParam('PATH_OPENSTATION')
        file_name = "RoboDK-Video-" + date_str + VIDEO_EXTENSION

        # Ask the user to provide a file to save
        file_path = getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension=VIDEO_EXTENSION, filetypes=[("Video file", "*" + VIDEO_EXTENSION)])
        if not file_path:
            quit()

        # Save the file
        print("Saving video to: " + file_path)
        if os.path.exists(file_path):
            print("Deleting existing file: " + file_path)
            os.remove(file_path)

        # Move the file
        os.rename(file_video_temp, file_path)

    # Done
    msg_str = "Video recording saved: " + file_path
    print(msg_str)
    RDK.ShowMessage(msg_str, False)


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


def SkipKill():
    """For Checkable actions, this setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called.
    This is needed if we want the user input to save the file. For example: The Record action from the Record App."""
    print("App Setting: Skip kill")
    sys.stdout.flush()


def runmain():
    # Verify if this is an action that was just unchecked
    if Unchecked():
        quit(0)
    else:
        # Checked (or checkable status not applicable)
        SkipKill()
        RecordProgram()


if __name__ == "__main__":
    # Important: leave the main function as runmain if you want to compile this app
    runmain()
