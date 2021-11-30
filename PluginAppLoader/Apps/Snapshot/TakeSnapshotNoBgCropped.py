# This script allows you to take screen capture with the size as shown on the screen (based on a 1K screen) and with anti aliasing

# Set the image size in pixels (image will be cropped as seen on the screen)
# Large sizes may not work depending on your graphic card
IMAGE_WIDTH = 1980
IMAGE_HEIGHT = 1080

# Samples for anti aliasing
#AA_SAMPLES = 1 # Screen quality (fast)
AA_SAMPLES = 2  # OK quality (slow)
#AA_SAMPLES = 4 # Good quality (slow)

#---------------------------------------
from robodk import *
from robolink import *

import_install("PIL", "Pillow")
import_install("numpy")
from PIL import Image
import numpy as np
import datetime
import tempfile

# Get Temporary file names
#date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
date_str = datetime.datetime.now().strftime("%H-%M-%S")

tempdir = tempfile.gettempdir()
temp_white = tempdir + "/" + date_str + "W.png"
temp_black = tempdir + "/" + date_str + "B.png"

# Start RoboDK API
RDK = Robolink()

path_rdk = RDK.getParam('PATH_OPENSTATION')
#path_rdk = RDK.getParam('PATH_DESKTOP')
file_name = "RoboDK-Screenshot-" + date_str + ".png"

# Ask to provide an image to save
file_path = getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension='.png', filetypes=[("PNG files", "*.png"), ("All files", "*.*")])

if not file_path:
    print("Operation cancelled")
    quit()

# Add a new reference frame at the camera view location
ref_cam = RDK.AddFrame("Camera Position")
ref_cam.setVisible(False)
campose = RDK.ViewPose()

# Make the view homogeneous
campose = KUKA_2_Pose(Pose_2_KUKA(campose))

ref_cam.setPose(campose.inv() * rotx(pi))

# Create a new 2D camera view with high snapshot resolution, take a snapshot and close
# More information here: https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink.Cam2D_Snapshot
camparams = "SNAPSHOT=%ix%i SIZE=%ix%i FOV=30 FAR_LENGTH=100000" % (IMAGE_WIDTH * AA_SAMPLES, IMAGE_HEIGHT * AA_SAMPLES, IMAGE_WIDTH, IMAGE_HEIGHT)
#cam_id = RDK.Cam2D_Add(ref_cam, "NEAR_LENGTH=5 FAR_LENGTH=100000 FOV=30 SNAPSHOT=%ix%i NO_TASKBAR BG_COLOR=black" % (IMAGE_WIDTH, IMAGE_HEIGHT))

# Take black snapshot
cam = RDK.Cam2D_Add(ref_cam, camparams + " BG_COLOR=black")
RDK.Render(True)
pause(0.1)
RDK.Cam2D_Snapshot(temp_black, cam)

# Take white snapshot
RDK.Cam2D_SetParams(camparams + " BG_COLOR=white", cam)
RDK.Render(True)
pause(0.1)
RDK.Cam2D_Snapshot(temp_white, cam)

RDK.Cam2D_Close(cam)

# Delete the temporary reference added
cam.Delete()
ref_cam.Delete()

#----------------------
# Do some image processing
imgB = Image.open(temp_black)
imgB = imgB.convert("RGBA")
imgW = Image.open(temp_white)
imgW = imgW.convert("RGBA")

# Delete temporary files
os.remove(temp_white)
os.remove(temp_black)


# Remove background
def removeBackground(imgB, imgW):
    b = np.asarray(imgB).copy()
    w = np.asarray(imgW).copy()

    b[:, :, 3] = 255 * (w[:, :, :3] - b[:, :, :3] != 255).any(axis=2)

    return Image.fromarray(b)


imgT = removeBackground(imgB, imgW)

# Crop image and resize
imgC = imgT.crop(imgT.getbbox())
imgC = imgC.resize((int(imgC.size[0] / AA_SAMPLES), int(imgC.size[1] / AA_SAMPLES)), Image.ANTIALIAS)
imgC.save(file_path, "PNG", quality=95, optimize=True)

# We are done!
print("Done")
RDK.ShowMessage("High resolution snapshot saved: " + file_path, False)
