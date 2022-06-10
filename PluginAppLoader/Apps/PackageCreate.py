# Automatically create a RoboDK package from the apps listed in the Apps folder (this folder)
# Tip: rename a folder starting it with underscore (_) to ignore creating a package for it
import os
import sys
import zipfile
import configparser

SKIP_DISABLED_APPS = False

def zipdir(path, ziph):
    # ziph is a zipfile handle
    
    # list of app folders
    apps = []
    
    if path == ".":
        #apps = [x[0] for x in os.walk(".")] # recursive
        apps = [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]
    else:
        apps.append(path)
    
    for app_folder in apps:
        if app_folder.startswith("_"):
            continue
        if "__pycache__" in app_folder:
            continue
        if ".git" in app_folder.lower():
            continue
            
             
        path_settings = app_folder + '/AppConfig.ini'
        if not os.path.isfile(path_settings):
            path_settings = app_folder + '/Settings.ini'   
            if not os.path.isfile(path_settings):
                print("Settings.ini file not found for: " + app_folder)
                continue
        
        config = configparser.ConfigParser()
        config.read(path_settings)
        if SKIP_DISABLED_APPS and path == "." and config["General"]["Enabled"] != """true""":
            print("App disabled (skipped): " + app_folder)
            continue
            
        print("App found and packed: " + config["General"]["MenuName"])
            
        for root, dirs, files in os.walk(app_folder):            
            if "__pycache__" in root:
                continue
            if ".git" in root.lower():
                continue
                
            for file in files:
                if len(root) < 3:
                    continue
                fname = os.path.join(root, file)
                #print(fname)
                ziph.write(fname)

if __name__ == '__main__':
    # Default package name for all apps
    package_name = 'RoboDK-App-Package.rdkp'
    app_folder = "."
    
    # Command line option: Specify the full path of the app (usually inside the Apps folder) 
    # to create a package for this specific app
    if len(sys.argv) > 1:
        full_path = sys.argv[1]
        app_folder = os.path.basename(full_path)
        os.chdir(full_path + '/../')
        print("Creating package for: " + app_folder)
        package_name = app_folder + '.rdkp'        
    
    # Delete existing package
    print("Creating package: " + package_name)
    if os.path.exists(package_name):
        try:
            os.remove(package_name)
        except:
            input("Unable to write file " + package_name)
            quit()
    
    # Create the package
    zipf = zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED)
    
    zipdir(app_folder, zipf)
    zipf.close()