# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Takes a snapshot image of the current view, optionally applying transparency to the background and keeping the region of interest.
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

robolink.import_install("cv2", "opencv-python")
robolink.import_install("numpy")
import cv2 as cv
import numpy as np
import datetime

import Settings


def remove_background(img_black, img_white):
    """
    Takes the same RGB image with contrasting background (white vs. black) and returns a RGBA image with a transparent background.
    """
    img_transp = img_black.copy()

    # Assume two RGB or RGBA images
    if img_transp.shape[2] < 4:
        img_transp = cv.cvtColor(img_transp, cv.COLOR_RGB2RGBA)

    img_transp[:, :, 3] = 255 * (img_white[:, :, :3] - img_black[:, :, :3] != 255).any(axis=2)

    return img_transp


def move(img, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0):
    """
    Move the image within the image, effectively adding transparent/white padding.
    """
    padding = [0, 0, 0]
    if len(img.shape) >= 3 and img.shape[2] >= 4:
        padding = padding + [0]
    return cv.copyMakeBorder(img, top, bottom, left, right, cv.BORDER_CONSTANT, None, padding)


def bounding_box(img, invert=False, keep_ratio=False):
    """
    Returns an image corresponding to the bounding box of the non-zero (light) regions in the image.
    Set invert to true to use zero (dark) regions.
    If the image is completely empty, it will return the original image.
    """
    img_bw = np.copy(img)

    if len(img_bw.shape) != 2:
        if img_bw.shape[2] == 3:
            img_bw = cv.cvtColor(img_bw, cv.COLOR_RGB2GRAY)
        else:
            img_bw = np.asarray(img_bw)[:, :, 3]  # Use the Alpha channel as a mask

    if invert:
        img_bw = (255 - img_bw)

    contours, _ = cv.findContours(img_bw, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img

    min_y, min_x = img.shape[:2]
    max_y = max_x = 0
    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)
        min_x, max_x = min(x, min_x), max(x + width, max_x)
        min_y, max_y = min(y, min_y), max(y + height, max_y)

    # Keep one pixel around the perimeter of the image (for padding)
    height, width = img.shape[:2]
    min_x, max_x = max(0, min_x - 1), min(width, max_x + 1)
    min_y, max_y = max(0, min_y - 1), min(height, max_y + 1)
    img_bb = img[min_y:max_y, min_x:max_x].copy()

    if not keep_ratio:
        return img_bb

    # Original image ratio
    height, width = img.shape[:2]
    desired_ratio = height / width

    # Current bounding box ratio
    hc, wc = (max_y - min_y), (max_x - min_x)
    current_ratio = hc / wc

    ratio_ratio = desired_ratio / current_ratio

    # Padding required
    top, bottom, left, right = 0, 0, 0, 0
    if ratio_ratio < 1:
        new_w = int(wc / ratio_ratio)
        padding = new_w - wc
        left = int(padding / 2)
        right = padding - left
    else:
        new_h = int(hc * ratio_ratio)
        padding = new_h - hc
        top = int(padding / 2)
        bottom = padding - top

    return move(img_bb, top, bottom, left, right)


def resize(img, height: int = -1, width: int = -1):
    """
    Resize up or down an image to the specified size, in pixels.
    """
    if (height, width) == img.shape[0:2] or height < 0 or width < 0:
        return img
    return cv.resize(img, (width, height), interpolation=cv.INTER_AREA)  # cv.INTER_CUBIC cv.INTER_LANCZOS4 cv.INTER_NEAREST_EXACT are too sharp


def Snapshot(RDK=None, S=None):
    """
    Takes a snapshot image of the current view, optionally applying transparency to the background and keeping the region of interest.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    width, height = S.SNAPSHOT_SIZE

    anti_aliasing = max(1, S.SNAPSHOT_AA)
    while anti_aliasing > 1 and (width * anti_aliasing > S.SNAPSHOT_AA_MAX or height * anti_aliasing > S.SNAPSHOT_AA_MAX):
        anti_aliasing -= 1

    # Add temporary cameras at the view location
    RDK.Render(False)
    ref_cam = RDK.AddFrame('Snapshot Frame')
    ref_cam.setVisible(False)
    ref_cam.setPose(RDK.ViewPose().inv() * robomath.rotx(robomath.pi))
    RDK.Render(True)

    cam_params = f"SNAPSHOT={width*anti_aliasing}x{height*anti_aliasing} SIZE={width}x{height} FOV={S.SNAPSHOT_FOV} FAR_LENGTH=100000 MINIMIZED"

    img = None

    if S.SNAPSHOT_REMOVE_BG:

        # Get a black background image
        cam_item_black = RDK.Cam2D_Add(ref_cam, cam_params + " BG_COLOR=black")
        cam_item_black.setName('Snapshot Camera (Black)')
        bytes_img = RDK.Cam2D_Snapshot('', cam_item_black)
        nparr = np.frombuffer(bytes_img, np.uint8)
        black = cv.imdecode(nparr, cv.IMREAD_UNCHANGED)
        cam_item_black.Delete()

        # Get a white background image
        cam_item_white = RDK.Cam2D_Add(ref_cam, cam_params + " BG_COLOR=white")
        cam_item_white.setName('Snapshot Camera (White)')
        bytes_img = RDK.Cam2D_Snapshot('', cam_item_white)
        nparr = np.frombuffer(bytes_img, np.uint8)
        white = cv.imdecode(nparr, cv.IMREAD_UNCHANGED)
        cam_item_white.Delete()

        # Filter out the background
        img = remove_background(black, white)

        # Only keep the region of interest
        if S.SNAPSHOT_ZOOM_TO_FIT:
            img = bounding_box(img, keep_ratio=True)

    else:
        # Get a default image
        cam_item_default = RDK.Cam2D_Add(ref_cam, cam_params)
        cam_item_default.setName('Snapshot Camera (Default)')
        bytes_img = RDK.Cam2D_Snapshot('', cam_item_default)
        nparr = np.frombuffer(bytes_img, np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_UNCHANGED)
        cam_item_default.Delete()

    # Remove temporary items
    ref_cam.Delete()

    # Resize
    img = resize(img, height, width)

    # Prompt to save
    date_str = datetime.datetime.now().strftime("%H-%M-%S")
    path_rdk = RDK.getParam('PATH_OPENSTATION')
    file_name = "RoboDK-Screenshot-HQ-" + date_str + ".png"

    file_path = robodialogs.getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension='.png', filetypes=[("PNG files", "*.png")])
    if not file_path:
        return

    if not cv.imwrite(file_path, img, [cv.IMWRITE_PNG_COMPRESSION, int(S.SNAPSHOT_COMPRESSION[1][S.SNAPSHOT_COMPRESSION[0]])]):
        RDK.ShowMessage("Snapshot save failed: " + file_path, False)
        return

    RDK.ShowMessage("Snapshot saved: " + file_path, False)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        Snapshot()


if __name__ == '__main__':
    runmain()