# Automatically create a package from the apps listed in this folder
import os
import zipfile

def zipdir(path, ziph):
    # ziph is a zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if len(root) < 3:
                continue
            fname = os.path.join(root, file)
            print(fname)
            ziph.write(fname)

if __name__ == '__main__':
    package_name = 'Package.apploader.rdkp'
    if os.path.exists(package_name):
        os.remove(package_name)
    zipf = zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir('.', zipf)
    zipf.close()