import os
import sys
import shutil
import glob
import fnmatch
from robodk import *

ROOT_PATH = os.path.dirname(__file__)

folder = getOpenFolder(ROOT_PATH, 'Select a RoboDK App to package')
if not folder:
    print("Operation cancelled")
    quit()

# Get the app name
app_name = os.path.basename(os.path.normpath(folder))


print("Creating package " + app_name)
print(folder)
os.system(sys.executable + ' "%s/PackageCreate.py" "%s"' % (ROOT_PATH, folder))
print("DONE!")
quit(0)
  
  

