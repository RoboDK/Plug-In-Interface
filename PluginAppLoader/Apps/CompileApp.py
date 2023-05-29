# This script will compile the PY files in your app to PYC files
# The resulting package will be an rdkp file that will automatically be installed by RoboDK

import os
import sys
import shutil
import glob
import fnmatch
from robodk.robodialogs import *
from robodk.robofileio import *

# List of files from the source app to NEVER copy and ALWAYS ignore. Use glob patterns.
COPY_IGNORE = ['.git', '.gitignore', 'env', '__pycache__', '*.pyc', '*.bat', '*.code-workspace']

# Prevent compiling the following .py files (Important: name in filename will be used as a check)
SKIP_COMPILE = ['_config']

# Delete these files from the main app directory
DELETE_ROOT_FILES = []

# Delete these files from the compiled folders
DELETE_BRANCH_FILES = ['*.ini', '*.svg', '*.png', '*.txt']

# Path where compilation takes place (important for error raising!)
path_compilation = "C:/RoboDK/Apps"

ROOT_PATH = os.path.dirname(__file__)

# Define the python versions the app should be compatible with
PYTHON_VERSION = {}
#PYTHON_VERSION['34'] = 'C:/Python34/python.exe'
#PYTHON_VERSION['35'] = 'C:/Python353/python.exe'
PYTHON_VERSION['37'] = 'C:/RoboDK/Python37/python.exe'
PYTHON_VERSION['310'] = 'C:/RoboDK/Python-Embedded/python.exe'

# Module loader template
LIBRARY_LOADER = """# Load Python library from your App folder and run the custom action

import sys
import os

# Detect Python version and App
print("Using Python version: " + str(sys.version_info))
path_app = os.path.dirname(__file__).replace(os.sep,"/")
print("Running RoboDK App compiled action " + path_app)

# Check if the App is compatible with the Python version
version_str = str(sys.version_info[0]) + str(sys.version_info[1])
path_library = path_app + '/v' + version_str
if not os.path.isdir(path_library):
    raise Exception("RoboDK App not found. Make sure you are using a supported Python version: " + path_library)

# Load the App
exec("from v" + version_str + ".%s import *")

if __name__== "__main__":
    runmain()

"""


def handle_remove_readonly(func, path, exc):
    # https://stackoverflow.com/questions/1213706/what-user-do-python-scripts-run-as-in-windows
    import stat, errno
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def copy_and_overwrite(from_path, to_path, ignore_patterns=[]):
    if os.path.exists(to_path):
        shutil.rmtree(to_path, ignore_errors=False, onerror=handle_remove_readonly)
    shutil.copytree(from_path, to_path, ignore=shutil.ignore_patterns(*ignore_patterns))


# Current Python version
python_version = sys.version_info
print("Using Python version: " + str(python_version))

CompileVersion = None
path_compile_from = None
path_compile_to = None

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
    path_compile_to = os.path.normpath(path_compile_from + "-Comp")
    # Exceptionally, if an app has the name ending with "-Src", we'll compile it to the same name without -Src or Comp
    if path_compile_from.lower().endswith("-src"):
        path_compile_to = path_compile_from[:-4]

    del_path_compile_from = False

    if path_app != path_compile_from:
        print(f"Copying {path_app} to {path_compile_from}")
        if os.path.exists(path_compile_from):
            print(f"{path_compile_from} already present and will be deleted!")
        copy_and_overwrite(path_app, path_compile_from, COPY_IGNORE)
        del_path_compile_from = True

    # Reset final compile to folder
    if os.path.exists(path_compile_to):
        shutil.rmtree(path_compile_to, ignore_errors=False, onerror=handle_remove_readonly)

    copy_and_overwrite(path_compile_from, path_compile_to, COPY_IGNORE)

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

    # Delete temp compile folder in RoboDK/Apps (if we created one)
    if del_path_compile_from and os.path.exists(path_compile_from):
        shutil.rmtree(path_compile_from, ignore_errors=False, onerror=handle_remove_readonly)

    # Delete temp compile folder
    if os.path.exists(path_compile_to):
        shutil.rmtree(path_compile_to, ignore_errors=False, onerror=handle_remove_readonly)

    print("DONE!!")
    quit(0)

if python_version[0] != int(CompileVersion[0]) or python_version[1] != int(CompileVersion[1:]):  # or python_version[2] != int(CompileVersion[2]):
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

        fmove_to = os.path.dirname(fmove_from) + '/../' + os.path.basename(fmove_from).replace('cpython-34.', '').replace('cpython-35.', '').replace('cpython-36.', '').replace('cpython-37.', '').replace('cpython-38.', '').replace('cpython-39.', '').replace('cpython-310.', '').replace('cpython-311.', '')

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
