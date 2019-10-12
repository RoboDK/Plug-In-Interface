# This script is part of the app "Record" and allows saving a RoboDK simulation as an AVI video file

# This action is "checkable" as defined in the INI settings. 
# Therefore, we can use the Record station parameter to detect if the button is checked or unchecked.
# This script will be triggered when the button is clicked (checked or unchecked)

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

# Define the frames per second:
frames_per_second = 25

# Define the video extension (you may need to change the coded)
#video_extension = "avi"
video_extension = "mp4"

# Choose the codec (mp4v, XVID or DIVX)
#fourcc = cv2.VideoWriter_fourcc(*'DIVX') # good quality (avi)
#fourcc = cv2.VideoWriter_fourcc(*'XVID') # low quality (avi)
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # good quality (mp4)

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
frame_path = tempfile.gettempdir() + '/RoboDK_Frame.png'
video_path = tempfile.gettempdir() + '/RoboDK_Video'
file_video_temp = video_path

# Get the file name of this file/script
filename = getFileName(__file__)

# Allow running an infinite loop if this script is run without the parameter AttachCamera
infinite_loop = False
if RDK.getParam(filename) is None:
    infinite_loop = True

# Run until the station parameter AttachCamera is set to 0
video = None
frame = None
render_time_last = 0
time_per_frame = 1/frames_per_second
tic()
while infinite_loop or RDK.getParam(filename) == 1:
    # Get the last time an image was rendered in ms (ms since epoch)
    render_time = int(RDK.Command("LastRender"))
    if (render_time_last != render_time):
        render_time_last = render_time        
        # A render happened in RoboDK. Retrieve the last frame
        #print("Retrieving new frame...")
        #tic()
        status = RDK.Command(snapshot_style, frame_path)        
        #print("getting snapshot:" + str(toc()))
        if status != "OK":
            # Something went wrong. Stop
            RDK.ShowMessage("Problems retrieving the RoboDK image buffer: " + frame_path, False)
            break
            
        # Load the frame image using OpenCV
        #tic()
        frame = cv2.imread(frame_path)
        #print("Reading image:" + str(toc()))
        
    if video is None:
        # Create VideoWriter object        
        file_video_temp = video_path + "." + video_extension
        
        # Retrieve image size
        height, width = frame.shape[:2]        
        video = cv2.VideoWriter(file_video_temp, fourcc, frames_per_second, (width, height))        
    
    #tic()
    video.write(frame) # Write out frame to video
    #print("Adding image:" + str(toc()))
    
    # Wait some time, if necessary, to have accurate frame rate
    elapsed = toc()
    if elapsed < time_per_frame:
        t_sleep = time_per_frame-elapsed
        print("Waiting for next frame: " + str(t_sleep))
        pause(t_sleep)
    
    tic()

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

# Move the file
os.rename(file_video_temp, file_path) 

# Done
msg_str = "Video recording saved: " + file_path
print(msg_str)
RDK.ShowMessage(msg_str, False)




