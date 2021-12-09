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


def RecordProgram():

    # Define the frames per second:
    frames_per_second = 25

    # Define the video extension (you may need to change the codec)
    #video_extension = "avi"
    video_extension = "mp4"

    # Choose the codec (mp4v, XVID or DIVX)
    #fourcc = cv2.VideoWriter_fourcc(*'DIVX') # good quality (avi)
    #fourcc = cv2.VideoWriter_fourcc(*'XVID') # low quality (avi)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # good quality (mp4)

    # Default screenshot style:
    snapshot_style = "Snapshot"

    # Other snapshot styles are not recommended, otherwise it will create a delay and a lot of flickering
    # Instead, change the appearance of RoboDK in the menu Tools-Options-Display
    #snapshot_style = "SnapshotWhite"
    #snapshot_style = "SnapshotWhiteNoText"
    #snapshot_style = "SnapshotNoTextNoFrames"

    #-------------------------------------------------------------------
    RDK = Robolink()

    # Define a temporary frame image and video files
    tempdir = tempfile.TemporaryDirectory(prefix='Record_')  # will cleanup itself
    file_video_temp = tempdir.name.replace('\\', '/') + '/RoboDK_Video.' + video_extension

    # Get the file name of this file/script and check the station parameter to detect stop (old method)
    filename = getFileName(__file__)

    # Allow running an infinite loop if this script is run without the parameter AttachCamera
    infinite_loop = False
    if RDK.getParam(filename) is None:
        infinite_loop = True

    # Class to stop the process if we receive the terminate signal
    #run = RunApplication()

    # Run until the station parameter AttachCamera is set to 0
    video = None
    frame = None
    render_time_last = 0
    time_per_frame = 1 / frames_per_second
    tic()
    while infinite_loop or RDK.getParam(filename) == 1:  # old method

        # Get the last time an image was rendered in ms (ms since epoch)
        render_time = int(RDK.Command("LastRender"))
        if (abs(render_time_last - render_time) > 1e-10):

            # A render happened in RoboDK. Retrieve the last frame
            render_time_last = render_time

            bytes_img = RDK.Command(snapshot_style, '')
            if bytes_img is None or bytes_img == b'':
                RDK.ShowMessage("Problems retrieving the RoboDK image buffer", False)
                break

            # Load the frame image using OpenCV
            frame = cv2.imdecode(np.frombuffer(bytes_img, np.uint8), cv2.IMREAD_UNCHANGED)

        if video is None:
            # Create VideoWriter object
            video = cv2.VideoWriter(file_video_temp, fourcc, frames_per_second, frame.shape[:2])

        video.write(frame)  # Write out frame to video

        # Wait some time, if necessary, to have accurate frame rate
        elapsed = toc()
        if elapsed < time_per_frame:
            t_sleep = time_per_frame - elapsed
            print("Waiting for next frame: " + str(t_sleep))
            pause(t_sleep)

        tic()

    print("Done recording")
    # Check if nothing was saved
    if video is None:
        quit()

    # Save the file
    msg_str = "Saving video recording... "
    print(msg_str)
    RDK.ShowMessage(msg_str, False)

    # Finish/release the file
    video.release()

    # Create a suggested file name
    print("Saving video...")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    #path_rdk = RDK.getParam('PATH_OPENSTATION')
    path_rdk = RDK.getParam('PATH_DESKTOP')
    file_name = "RoboDK-Video-" + date_str + "." + video_extension

    # Ask the user to provide a file to save
    file_path = getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension='.' + video_extension, filetypes=[("Video file", "*." + video_extension), ("All files", "*.*")])
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


def runmain():
    # Make sure we don't run this file if we are unchecking it
    if len(sys.argv) >= 2:
        if sys.argv[1] == "Unchecked":
            print("This action is triggered by the uncheck action")
            quit()

    # Important: This setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called
    # This is needed if we want the user input to save the file
    print("App Setting: Skip kill")
    sys.stdout.flush()

    RecordProgram()


# Function to run when this module is executed on its own or by selecting the action button in RoboDK
if __name__ == "__main__":
    runmain()
