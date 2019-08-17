# Extract a package by providing a *.apploader.rdkp file
import os
import zipfile
import sys

# Import tkinter
if sys.version_info[0] < 3: # Python 2.X only:
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
else: # Python 3.x only
    import tkinter
    from tkinter import filedialog
    from tkinter import messagebox

# Ask the user to select a file
def getFileOpen():            
    root = tkinter.Tk()
    root.withdraw()
    options = {}
    options['initialdir'] = '.'
    options['title'] = 'Open RoboDK Package file'
    options['defaultextension'] = '.rdkp'
    options['filetypes'] = [('RoboDK package', '.rdkp'), ('Zipped package', '.zip'), ('All files', '.*')]
    file_path = filedialog.askopenfilename(**options)
    return file_path
        
# Check if the package exists
def ExistingPackage(path_zip, path_extract):
    msg = ''
    with zipfile.ZipFile(path_zip, 'r') as zip_ref:
        zip_folders = []
        for name in zip_ref.namelist():
            dir = name.split('/')[0]
            if dir in zip_folders:
                continue            
            zip_folders.append(dir)
            if os.path.isdir(path_extract + '/' + dir):
                msg += "    " + u"\u2022" + " " + dir + '\n'
    if len(msg) > 0:
        msg = "The following package(s) already exist:\n\n" + msg + "\nOverride?"
        return True, msg   
    return False, msg
    
# Unzip a zip file
def UnZipDir(path_zip, path_extract):
    with zipfile.ZipFile(path_zip, 'r') as zip_ref:
        zip_ref.extractall(path_extract)
        
# Ask the user if we should override
def DoOverride(display_message):
    result = messagebox.askquestion("Override?", display_message, icon='warning')
    if result == 'yes':
        return True
    else:
        return False

if __name__ == '__main__':
    #package_file = 'Package.apploader.rdkp'    
    file_path = getFileOpen()
            
    if not file_path:
        quit(0)
    
    exists, msg = ExistingPackage(file_path, '.')
    if exists:
        if not DoOverride(msg):
            print("Override cancelled")
            quit(0)
    
    UnZipDir(file_path, '.')
    print("Done")
    
    
    