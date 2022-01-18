# This script allows you to take screen capture with the size as shown on the screen (based on a 1K screen) and with anti aliasing

# Set the image size in pixels (image will be cropped as seen on the screen)
# Large sizes may not work depending on your graphic card
IMAGE_WIDTH = 1980
IMAGE_HEIGHT = 1080

# Samples for anti aliasing
#AA_SAMPLES = 1  # Screen quality (fast)
AA_SAMPLES = 2  # OK quality (slow)
#AA_SAMPLES = 4  # Good quality (slow)

#---------------------------------------
from robodk.robomath import *
from robodk.robodialogs import *
from robodk.robolink import *
import datetime

import os
import tempfile

import_install("PIL", "Pillow")

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

# Turn auto render back on (otherwise we get a black view)
#RDK.Render(True)

# Create a new 2D camera view with high snapshot resolution, take a snapshot and close
# More information here: https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Robolink.Cam2D_Snapshot
camparams = "SNAPSHOT=%ix%i FOV=30 FAR_LENGTH=100000" % (IMAGE_WIDTH * AA_SAMPLES, IMAGE_HEIGHT * AA_SAMPLES)
#cam_id = RDK.Cam2D_Add(ref_cam, "NEAR_LENGTH=5 FAR_LENGTH=100000 FOV=30 SNAPSHOT=%ix%i NO_TASKBAR BG_COLOR=black" % (IMAGE_WIDTH, IMAGE_HEIGHT))

# Take black snapshot
cam = RDK.Cam2D_Add(ref_cam, camparams + " BG_COLOR=black")
RDK.Render()
pause(0.2)
RDK.Cam2D_Snapshot(temp_black, cam)

# Take white snapshot
RDK.Cam2D_SetParams(camparams + " BG_COLOR=white", cam)
RDK.Render()
pause(0.2)
RDK.Cam2D_Snapshot(temp_white, cam)
RDK.Cam2D_Close(cam)

RDK.Render(False)

# Delete the temporary reference added
cam.Delete()
ref_cam.Delete()

#----------------------
# Do some image processing
from PIL import Image

imgB = Image.open(temp_black)
imgB = imgB.convert("RGBA")
imgW = Image.open(temp_white)
imgW = imgW.convert("RGBA")

datasB = imgB.getdata()
datasW = imgW.getdata()

numpix = IMAGE_WIDTH * IMAGE_HEIGHT * AA_SAMPLES * AA_SAMPLES
update_rate = int(numpix / 100)

newData = []
cnt = 0
for itemB, itemW in zip(datasB, datasW):
    # Remove pixels that are part of the background (we need to check black and white to make sure we don't get false positives)
    if itemB[0] == 0 and itemB[1] == 0 and itemB[2] == 0 and itemW[0] == 255 and itemW[1] == 255 and itemW[2] == 255:
        #if itemB[:3] == (0,0,0) and itemW[:3] == (255,255,255):
        newData.append((0, 0, 0, 0))
    else:
        newData.append(itemB)

    if cnt % update_rate == 0:
        percent = 100 * cnt / numpix
        RDK.ShowMessage("Saving image, please wait ... %.0f" % (percent), False)
        RDK.Command("ProgressBar", percent)

    cnt += 1

imgB.putdata(newData)

# Crop image and resize
#imgB.getbbox()  # (64, 89, 278, 267)
imgB = imgB.crop(imgB.getbbox())
imgB = imgB.resize((int(imgB.size[0] / AA_SAMPLES), int(imgB.size[1] / AA_SAMPLES)), Image.ANTIALIAS)
imgB.save(file_path, "PNG", quality=95, optimize=True)

# Delete temporary files
os.remove(temp_white)
os.remove(temp_black)

# We are done!
print("Done")
RDK.Command("ProgressBar", -1)
RDK.ShowMessage("High resolution snapshot saved: " + file_path, False)
