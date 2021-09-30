#####################################################
## Copyright (C) RoboDK Inc - All Rights Reserved
## Documentation: https://robodk.com/doc/en/RoboDK-API.html
## Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#####################################################

from _tools import *
from collections import OrderedDict

FIELDS_UI = OrderedDict()

#------------------------------------------------------------------------
# CONFIGURATION SECTION  
APP_NAME = 'Reachability'

# Variable names when displayed on the user interface
# Create this dictionary in the same order that you want to display it
FIELDS_UI = OrderedDict()
#FIELDS_UI['Speed_Approach'] = 'Approach speed (mm/s)'
#FIELDS_UI['Speed_Normal'] = 'Operation Speed (mm/s)'
FIELDS_UI['ShowRobotPoses']  = 'Show Robot'
FIELDS_UI['Unreachable_Timeout']  = 'Unreachable timeout (s)'
FIELDS_UI['Range_TX'] = 'Translation X (m)'
FIELDS_UI['Range_TY'] = 'Translation Y (m)'
FIELDS_UI['Range_TZ'] = 'Translation Z (m)'
FIELDS_UI['Range_RX'] = 'Rotation X (deg)'
FIELDS_UI['Range_RY'] = 'Rotation Y (deg)'
FIELDS_UI['Range_RZ'] = 'Rotation Z (deg)'


# Station name to store
STATIONVAR_NAME = APP_NAME    

class Settings(AppSettings):
    """Generic settings class to save and load settings from a RoboDK station and show methods in RoboDK"""
    # List the variable names you would like to save and their default values
    # Important: Try to avoid default None type!! 
    # If None is used as default value it will attempt to treat it as a float and None = -1    
    # Variables that start with underscore (_) will not be saved
    #Speed_Approach = 200
    #Speed_Normal = 50    
    ShowRobotPoses = False
    Unreachable_Timeout = 2
    Range_TX = "[0]"
    Range_TY = "[0]"
    Range_TZ = "[0]"
    Range_RX = "range(-120, 180, 60)"
    Range_RY = "range(-120, 180, 60)"
    Range_RZ = "[0]"    
    
    
#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------    
    def __init__(self):
        # customize the initialization section if needed
        super(Settings, self).__init__(STATIONVAR_NAME)
        self._FIELDS_UI = FIELDS_UI

    def CopyFrom(self, other):
        """Copy settings from another instance"""
        attr = self.getAttribs()
        for a in attr:
            if hasattr(other, a):
                setattr(self,a, getattr(other, a))

    def SetDefaults(self):
        # List untouched variables for default settings
        list_untouched = []
        
        # save in local variables
        for var in list_untouched:
            exec('%s=self.%s' % (var,var))

        defaults = Settings()
        self.CopyFrom(defaults)

        # restore from local vars
        for var in list_untouched:
            exec('self.%s=%s' % (var,var))

    def ShowUI(self, windowtitle=APP_NAME, embed=False, wparent=None, callback_frame=None):
        # Show the UI for these settings including a custom frame to set the default settings
        def custom_frame(w):
            def set_defaults():
                w.destroy()
                self.SetDefaults()
                self.ShowUI(windowtitle=windowtitle, embed=embed, wparent=wparent, callback_frame=custom_frame)

            row = tk.Frame(w)
            b1 = tk.Button(row, text='Set defaults', command=set_defaults, width=8)
            b1.pack(side=tk.LEFT, padx=5, pady=5)

            #Creating the OK button
            #bhelper = tk.Button(row, text='OK', command=read_fields, width=8)
            #bhelper.pack(side=tk.RIGHT, padx=5, pady=5)

            row.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)

        super(Settings, self).ShowUI(windowtitle=windowtitle, embed=embed, wparent=wparent, callback_frame=custom_frame)


def runmain():
    # Read this app settings
    S = Settings()

    #if not S.Load():
    #    print("Using default settings (loaded for the first time)")
    
    S.Load()
    S.ShowUI()
    S.Save()        
        
if __name__ == "__main__":
    runmain()
