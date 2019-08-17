# This action is "checkable" as defined in the INI settings. 
# Therefore, we can use the Record station parameter to detect if the button is checked or unchecked.
# This script will be triggered when the button is clicked (checked or unchecked)


snapshot_style = "Snapshot"

# Other snapshot styles are not recommended, otherwise it will create a lot of flickering.
# Instead, change the appearance of RoboDK in the menu Tools-Options-Display
#snapshot_style = "SnapshotWhite"
#snapshot_style = "SnapshotWhiteNoText"
#snapshot_style = "SnapshotNoTextNoFrames"

frames_per_second = 30

video_extension = "avi"

import robodk   # import the robodk library (robotics toolbox)
from robolink import *    # API to communicate with RoboDK

import_install("cv2", "opencv-python")
import cv2 #if is not installed in your system run in terminal " pip install opencv-python "

import os
import datetime
import tempfile
import shutil
import tkinter
from tkinter import filedialog

RDK = Robolink()

item2station_pose = eye(4)
last_item = None


frame_path = tempfile.gettempdir() + '/RoboDK_Frame.png'
video_path = tempfile.gettempdir() + '/RoboDK_Video'
file_video_temp = video_path


# Get the file name of this file/script
filename = getFileName(__file__)

# Allow running an infinite loop if this script is run without the parameter AttachCamera
infinite_loop = False
if RDK.getParam(filename) is None:
    infinite_loop = True

video = None
render_time_last = 0
# Run until the station parameter AttachCamera is set to 0
while infinite_loop or RDK.getParam(filename) == 1:
    # Get the last time an image was rendered in ms (ms since epoch)
    render_time = int(RDK.Command("LastRender"))
    if (render_time_last != render_time):
        render_time_last = render_time        
        # A render happened in RoboDK. Retrieve the last frame
        #print("Retrieving new frame...")
        status = RDK.Command(snapshot_style, frame_path)        
        if status != "OK":
            # Something went wrong. Stop
            RDK.ShowMessage("Problems retrieving the RoboDK image buffer: " + frame_path, False)
            break
            

    frame = cv2.imread(frame_path)
    if video is None:
        # Define the codec and create VideoWriter object 
        
        # Choose the codec (mp4v, XVID or DIVX)
        #fourcc = cv2.VideoWriter_fourcc(*'XVID') # low quality
        fourcc = cv2.VideoWriter_fourcc(*'DIVX') # good quality
        
        # ".mp4" for mp4v.... ".avi" for XVID and DIVX
        file_video_temp = video_path + "." + video_extension
        
        height, width = frame.shape[:2]
        video = cv2.VideoWriter(file_video_temp, fourcc, frames_per_second, (width, height))
    
    video.write(frame) # Write out frame to video

if video is None:
    # Nothing was saved
    quit()

    
msg_str = "Saving video recording... "
print(msg_str)
RDK.ShowMessage(msg_str, False)

# Finish/release the file
video.release()

print("Saving video...")

# Create a suggested file name
date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
path_rdk = RDK.getParam('PATH_OPENSTATION')
file_name = "RoboDK-Video-" + date_str + "." + video_extension

# Ask the user to provide 
root = tkinter.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
types = (("Video file","*"+video_extension),("All files","*.*"))
file_path = filedialog.asksaveasfilename(title = "Save the video recording", defaultextension = types, filetypes = types, initialdir=path_rdk, initialfile=file_name)
if not file_path:
    quit()

# Save the file
print("Saving video to: " + file_path)
if os.path.exists(file_path):
    print("Deleting existing file: " + file_path)
    os.remove(file_path)

# move the file
os.rename(file_video_temp, file_path) 

msg_str = "Video recording saved: " + file_path
print(msg_str)
RDK.ShowMessage(msg_str, False)




