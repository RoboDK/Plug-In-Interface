import os
import sys
import shutil
import glob
import fnmatch
from robodk import *

# Prevent compiling the following files (Important: name in filename will be used as a check)
SKIP_COMPILE = ['_config']

# Delete PNG files from the main app directory
DELETE_ROOT_FILES = ['*.png']

# Delete SVG and INI files from the compiled folders
DELETE_BRANCH_FILES = ['*.svg', '*.ini']


# Path where compilation takes place (important for error raising!)
path_compilation = "C:/RoboDK/Apps" 

ROOT_PATH = os.path.dirname(__file__)

# Define the python versions the app should be compatible with
PYTHON_VERSION = {}
#PYTHON_VERSION['343'] = 'C:/Python34/python.exe'
#PYTHON_VERSION['353'] = 'C:/Python353/python.exe'
PYTHON_VERSION['373'] = 'C:/RoboDK/Python37/python.exe'

# Module loader template
LIBRARY_LOADER = """# Load library and run dedicated action

import sys
import os

print("Using Python version: " + str(sys.version_info))
path_app = os.path.dirname(__file__).replace("\\\\","/")
print("RoboDK App Path: " + path_app)

path_library = path_app + '/v' + str(sys.version_info[0]) + str(sys.version_info[1]) + str(sys.version_info[2])
if not os.path.isdir(path_library):
    raise Exception("Folder not found (make sure you are using the default Python version): " + path_library)

sys.path.insert(0, path_library)

import %s as thismodule

if __name__== "__main__":
    thismodule.runmain()

"""



def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)

# Current Python version
python_version = sys.version_info
print("Using Python version: " + str(python_version))

CompileVersion = None
path_compile_from = None
path_compile_to = None

#CompileVersion = "373"
#path_compile_from = "C:\RoboDK\Apps\CalibGage"
#path_compile_to = "C:/Users/Albert/Desktop/RoboDK/Deploy/RoboDK_MSVC2017_Qt5.11.2x64/Apps/CalibGage-Comp"

if len(sys.argv) > 1:
    CompileVersion = sys.argv[1]
    path_compile_from = sys.argv[2]
    path_compile_to = sys.argv[3]
    print("Compiling Plug-In version: " + CompileVersion)
    print("CompileVersion = \"" + CompileVersion + "\"")
    print("path_compile_from = \"" + path_compile_from + "\"")
    print("path_compile_to = \"" + path_compile_to + "\"")
    

    
#input("Paused")
if CompileVersion is None:    

    folder = getOpenFolder(ROOT_PATH, 'Select a RoboDK App to compile (directory)')
    if not folder:
        print("Operation cancelled")
        quit()

    # Get the app name
    app_name = os.path.basename(os.path.normpath(folder))

    path_app = os.path.normpath(folder)
    path_compile_from = os.path.normpath(path_compilation + '/' + app_name)  # ROOT_PATH + "/SetStyle/" 
    path_compile_to = folder + "-Comp"

    if path_app != path_compile_from:
        print("Copying folder to compile location")
        copy_and_overwrite(path_app, path_compile_from)

    #Remove all PYC files
    for root, dirnames, filenames in os.walk(path_compile_from):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            #matches.append()
            fdelete = os.path.join(root, filename)
            print("Deleting file: " + fdelete)
            os.remove(fdelete)        

    # Reset final compile to folder
    if os.path.exists(path_compile_to):
        shutil.rmtree(path_compile_to)

    copy_and_overwrite(path_compile_from, path_compile_to)

    # Delete pycache on final directory
    delete_pycache = path_compile_to + '/__pycache__'
    if os.path.exists(delete_pycache):
        shutil.rmtree(delete_pycache)
    
    # Convert each Python module as a library loader
    for filename in os.listdir(path_compile_to):
        if filename.endswith(".py"): 
            module_name = getFileName(filename)
            filename_path = path_compile_to + '/' + filename
            with open(filename_path, 'w') as fid:
                fid.write(LIBRARY_LOADER % module_name)

    print("Triggering compilations on separate instances")
    
    for pyver in PYTHON_VERSION:
        pypath = PYTHON_VERSION[pyver]
        print("-------- Triggering compilation for v%s ------------" % pyver)
        print("Python path: " + pypath)
        print("")
        if os.path.isfile(pypath):
            # Run a new instance
            os.system(pypath + ' "' + __file__ + '" "' + pyver + '" "' + path_compile_from + '" "' + path_compile_to + '"')
        else:
            raise Exception("Python version not found!")

    for del_pattern in DELETE_ROOT_FILES:
        for f in glob.glob(path_compile_to + "/" + del_pattern):
            os.remove(f)
    
    print("--------------- COMPILATION DONE -------------------")     

    print("Creating package...")
    os.system(pypath + ' "%s/PackageCreate.py" "%s"' % (ROOT_PATH, path_compile_to))
    print("DONE!!")
    quit(0)
  
  

if python_version[0] != int(CompileVersion[0]) or python_version[1] != int(CompileVersion[1]) or python_version[2] != int(CompileVersion[2]):
    raise Exception("Targeting Python v%s but Python version is %s" % (CompileVersion, str(python_version)))
    

# Compiled files
path_compile_to_version = path_compile_to + '/v' + CompileVersion + "/"

# Duplicate folder
copy_and_overwrite(path_compile_from, path_compile_to_version)

        
import compileall  
#compiles all .py files in the project (creates PYC files)
compileall.compile_dir(path_compile_to_version)

# Remove PY files from compiled directory
for root, dirnames, filenames in os.walk(path_compile_to_version):
    for filename in fnmatch.filter(filenames, '*.py'):
        if any(s in filename for s in SKIP_COMPILE):
            print("Skipping compilation of: " + filename)
            continue

        fdelete = os.path.join(root, filename)
        print("Deleting file: " + fdelete)
        os.remove(fdelete)

# Move all PYC files from pycache and rename them as modules (except RoboDK.py)
for root, dirnames, filenames in os.walk(path_compile_to_version):
    for filename in fnmatch.filter(filenames, '*.pyc'):
        fmove_from = os.path.join(root, filename)
        #if any(s in filename for s in SKIP_COMPILE):
        #    print("Skipping compilation of: " + filename)
        #    continue

        fmove_to = os.path.dirname(fmove_from) + '/../' + os.path.basename(fmove_from).replace('cpython-34.','').replace('cpython-35.','').replace('cpython-36.','').replace('cpython-37.','')
        
        # Autodesk needs the main file as a PY file
        #if root.lower().replace("/","").replace("\\","").endswith("robodk__pycache__") and os.path.basename(fmove_to.lower()) == "robodk.pyc":
        #    print("Deleting file: " + fmove_from)
        #    os.remove(fmove_from)
        #    continue
        
        print("Moving file: " + fmove_from)
        print("         to: " + fmove_to)
        os.rename(fmove_from, fmove_to)
        
    if root.endswith("__pycache__"):
        shutil.rmtree(root)
        #os.rmdir(root) # raises exception if the folder is not empty

for del_pattern in DELETE_BRANCH_FILES:
    for f in glob.glob(path_compile_to_version + "/" + del_pattern):
        os.remove(f)

