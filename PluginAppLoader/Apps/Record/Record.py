# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Start/stop the screen recording (3D view) and prompt the user to save the video file.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, robodialogs, roboapps

import Settings

robolink.import_install("cv2", "opencv-python")
robolink.import_install("numpy")
import cv2
import numpy as np
import datetime
import tempfile
import os


def Record(RDK=None, S=None):
    """
    Start/stop the screen recording (3D view) and prompt the user to save the video file.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load()

    # Get the video extension (.mp4, .avi, etc)
    VIDEO_EXTENSION = S.VIDEO_EXTENSION[1][S.VIDEO_EXTENSION[0]]

    # Select the according codec
    if 'mp4' in VIDEO_EXTENSION:
        FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        FOURCC = cv2.VideoWriter_fourcc(*'DIVX')  # AVI

    PREFER_SOCKET = True  # If available, prefer socket (usually faster) over temporary file to retrieve the image

    #-------------------------------------------------------------------
    # Use a temporary folder
    with tempfile.TemporaryDirectory(prefix='Record_') as td:

        file_video_temp = os.path.join(td, 'RoboDK_Video' + VIDEO_EXTENSION)

        video = None
        frame = None
        use_socket = PREFER_SOCKET
        render_time_last = 0
        time_per_frame = 1 / S.FRAMES_PER_SECOND

        APP = roboapps.RunApplication()
        while APP.Run():
            robomath.tic()

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
                    if RDK.Command("Snapshot", tf) == 'OK':
                        return not fallback, cv2.imread(tf)

                    return False, None

                # Get the station snapshot
                success, frame = getSnapshot(use_socket, td)
                if not success:
                    if use_socket:
                        use_socket = False
                        continue
                    else:
                        RDK.ShowMessage("Problems retrieving the RoboDK image buffer", False)
                        break

            # Write the frame to the video file
            if video is None:
                # Requires at least one frame to extract the frame size.
                height, width = frame.shape[:2]
                video = cv2.VideoWriter(file_video_temp, FOURCC, S.FRAMES_PER_SECOND, (width, height))
            video.write(frame)

            # Wait some time, if necessary, to have accurate frame rate
            elapsed = robomath.toc()
            if elapsed < time_per_frame:
                t_sleep = time_per_frame - elapsed
                print("Waiting for next frame: " + str(t_sleep))
                robomath.pause(t_sleep)

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
        file_path = robodialogs.getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension=VIDEO_EXTENSION, filetypes=[("Video file", "*" + VIDEO_EXTENSION)])
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
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        roboapps.SkipKill()  # Let this app run after it is unchecked, so that we can save the video file on disk
        Record()


if __name__ == '__main__':
    runmain()