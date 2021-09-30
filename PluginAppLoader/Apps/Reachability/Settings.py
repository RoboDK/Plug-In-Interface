#####################################################
## Copyright (C) RoboDK Inc - All Rights Reserved
## Documentation: https://robodk.com/doc/en/RoboDK-API.html
## Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#####################################################
#
# Purpose: Show the application settings
# Define the Settings in the Settings class (_config file)

from _config import *

def runmain():
    """Main program to run"""
    
    # Verify if this is an action that was just unchecked
    if Unchecked():        
        quit()
    
    # Show embedded in RoboDK window
    SHOW_EMBEDDED = True
    
    S = Settings()   
    S.Load()
    #S.ShowUI()
    S.ShowUI(embed=SHOW_EMBEDDED)
    S.Save()

# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()
    