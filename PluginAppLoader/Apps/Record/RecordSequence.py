# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Start/stop the screen recording (3D view) and prompt the user to save the image sequence (.png)).
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


def add_cameras(RDK):

    view_size = RDK.Command('SetSize3D')
    width, height = view_size.split('x', maxsplit=1)
    width, height = int(width), int(height)

    anti_aliasing = 4
    while anti_aliasing > 1 and (width * anti_aliasing > 2000 or height * anti_aliasing > 2000):
        anti_aliasing -= 1

    # Add temporary cameras at the view location
    RDK.Render(False)
    ref_cam = RDK.AddFrame('Snapshot Frame')
    ref_cam.setVisible(False)
    ref_cam.setPose(RDK.ViewPose().inv() * robomath.rotx(robomath.pi))
    RDK.Render(True)

    cam_params = f"SNAPSHOT={width*anti_aliasing}x{height*anti_aliasing} SIZE={view_size} FOV=30 FAR_LENGTH=100000 MINIMIZED"

    cam_item_black = RDK.Cam2D_Add(ref_cam, cam_params + " BG_COLOR=black")
    cam_item_black.setName('Snapshot Camera (Black)')
    cam_item_black.setParam("Open", 1)

    cam_item_white = RDK.Cam2D_Add(ref_cam, cam_params + " BG_COLOR=white")
    cam_item_white.setName('Snapshot Camera (White)')
    cam_item_white.setParam("Open", 1)

    return ref_cam, cam_item_black, cam_item_white


def get_snapshot(cam_item):
    # Socket method. Added in version 5.3.2
    try:
        bytes_img = cam_item.RDK().Cam2D_Snapshot(
            '',
            cam_item,
        )
        if isinstance(bytes_img, bytes) and bytes_img != b'':
            return True, cv2.imdecode(np.frombuffer(bytes_img, np.uint8), cv2.IMREAD_UNCHANGED)
    except Exception:
        return False, None


def remove_background(img_black, img_white):
    """
    Takes the same RGB image with contrasting background (white vs. black) and returns a RGBA image with a transparent background.
    """
    img_transp = img_black.copy()

    # Assume two RGB or RGBA images
    if img_transp.shape[2] < 4:
        img_transp = cv2.cvtColor(img_transp, cv2.COLOR_RGB2RGBA)

    img_transp[:, :, 3] = 255 * (img_white[:, :, :3] - img_black[:, :, :3] != 255).any(axis=2)

    return img_transp


def RecordSequence(RDK=None, S=None):
    """
    Start/stop the screen recording (3D view) and prompt the user to save the video file.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load()

    ref_cam, cam_item_black, cam_item_white = add_cameras(RDK)
    sim_speed = RDK.SimulationSpeed()

    #-------------------------------------------------------------------
    # Use a temporary folder
    with tempfile.TemporaryDirectory(prefix='Record_') as td:

        frame = None
        render_time_last = 0
        time_per_frame = 1 / S.FRAMES_PER_SECOND
        counter = 0

        APP = roboapps.RunApplication()
        while APP.Run():
            robomath.tic()

            # There's no need to get a new image if no render as occurred.
            render_time = int(RDK.Command("LastRender"))
            if (render_time_last != render_time):
                render_time_last = render_time

                # Get the station snapshot
                RDK.setSimulationSpeed(0) # Make sure nothing moves between the two images
                success1, black = get_snapshot(cam_item_black)
                success2, white = get_snapshot(cam_item_white)
                RDK.setSimulationSpeed(sim_speed)
                if not success1 or not success2:
                    RDK.ShowMessage("Problems retrieving the RoboDK image buffer", False)
                    break

                frame = remove_background(black, white)

            # Write the frame to the video file
            file_path = os.path.join(td, f'RoboDK_Sequence_{counter}.png')
            if not cv2.imwrite(file_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 4]):
                RDK.ShowMessage("Snapshot save failed: " + file_path, False)
                return
            counter += 1

            # Wait some time, if necessary, to have accurate frame rate
            elapsed = robomath.toc()
            if elapsed < time_per_frame:
                t_sleep = time_per_frame - elapsed
                print("Waiting for next frame: " + str(t_sleep))
                robomath.pause(t_sleep)

        print("Done recording")
        ref_cam.Delete()

        # Check if nothing was saved
        if not counter:
            quit()

        # Save the file
        msg_str = "Saving sequence recording... "
        print(msg_str)
        RDK.ShowMessage(msg_str, False)

        # Ask the user to provide a folder to save
        path_rdk = RDK.getParam('PATH_DESKTOP')  # or path_rdk = RDK.getParam('PATH_OPENSTATION')
        date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        folder_path = robodialogs.getSaveFolder(path_preference=path_rdk)
        if not folder_path:
            quit()
        folder_path = os.path.join(folder_path, 'RoboDK-Sequence-' + date_str)

        # Save the file
        print("Saving sequence to: " + folder_path)
        if os.path.exists(folder_path):
            print("Deleting existing folder: " + folder_path)
            os.remove(folder_path)

        # Move the file
        os.rename(td, folder_path)

    # Done
    msg_str = "Sequence recording saved: " + file_path
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
        RecordSequence()


if __name__ == '__main__':
    runmain()
