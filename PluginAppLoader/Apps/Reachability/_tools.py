#-------------------------------------------------------
# This file provides generic tools for your Python app in RoboDK
# This file includes:
#   1. RunApplication: class to cleanly stop checkable actions (checkable actions get the Terminate/SIGINT signal when they are unchecked)
#   2. AppsSettings class: simple way to detect an unchecked action from RoboDK by capturing the Terminate signal
#   3. AppSettings
#-------------------------------------------------------

import sys

if sys.version_info[0] < 3: 
    # Python 2.X only:
    import Tkinter as tk
    import tkMessageBox as messagebox
else: 
    # Python 3.x only
    import tkinter as tk
    from tkinter import messagebox

class RunApplication:
    """Class to detect when the terminate signal is emited to stop an action.
    
    .. code-block:: python
    
        run = RunApplication()
        while run.run:
            # your main loop to run until the terminate signal is detected
            ...

    """
    run = True
    def __init__(self):
        import signal
        signal.signal(signal.SIGINT, self.clean_exit)
        signal.signal(signal.SIGTERM, self.clean_exit)

    def clean_exit(self,signum,frame):
        self.run = False
        
def Unchecked():
    """Verify if the command "Unchecked" is present. In this case it means the action was just unchecked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Unchecked" in sys.argv[1:]:
            return True
    
    return False

def Checked():
    """Verify if the command "Checked" is present. In this case it means the action was just checked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Checked" in sys.argv[1:]:
            return True
    
    return False    
    
def KeepChecked():
    """Keep an action checked even if the execution of the script completed (this is applicable to Checkable actions only)"""
    print("App Setting: Keep checked")
    sys.stdout.flush()
    
def SkipKill():
    """For Checkable actions, this setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called.
    This is needed if we want the user input to save the file. For example: The Record action from the Record App."""
    print("App Setting: Skip kill")
    sys.stdout.flush()
    
def Str2FloatList(str_values, expected_nvalues=3):
    """Convert a string into a list of values. It returns None if the array is smaller than the expected size."""
    import re
    if str_values is None:
        return None
        
    values = re.findall("[-+]?\d+[\.]?\d*", str_values)    
    valuesok = []
    for i in range(len(values)):
        try:
            valuesok.append(float(values[i]))
        except:
            return None
    
    if len(valuesok) < expected_nvalues:
        return None
        
    print('Read values: ' + repr(values))
    return valuesok
  
    
def Registry(varname, setvalue=None): 
    """Read value from the registry or set a value. It will use HKEY_CURRENT_USER so no admin rights required."""
    from sys import platform as _platform
    if _platform == "linux" or _platform == "linux2":
        # Ubuntu, Linux or Debian
        return None
    elif _platform == "darwin":
        # MacOS
        #self.APPLICATION_DIR = "/Applications/RoboDK.app/Contents/MacOS/RoboDK"
        return None
    else:
        # Windows assumed  
        if sys.version_info[0] < 3:
            import _winreg
        else:
            import winreg as _winreg
        
        # Try to get the value from the Windows registry:
        try:
            # Open the key and return the handle object.
            reg_flag = _winreg.KEY_READ if setvalue is None else _winreg.KEY_WRITE
            try:
                hKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "SOFTWARE\\RoboDK", 0, reg_flag | _winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                hKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "SOFTWARE\\RoboDK", 0, reg_flag | _winreg.KEY_WOW64_32KEY)                
            
            # Read the value.
            if setvalue is None:
                result = _winreg.QueryValueEx(hKey, varname)            
                # Close the handle object.
                _winreg.CloseKey(hKey)         
                # Return only the value from the resulting tuple (value, type_as_int).
                return result[0]
                
            else:
                _winreg.SetValueEx(hKey, varname, 0, _winreg.REG_SZ, str(setvalue))
                _winreg.CloseKey(hKey)
                return True
                
        except:# FileNotFoundError:
            return None
            
        return None
    
class AppSettings:
    """Generic settings class to save and load settings from a RoboDK station and show methods in RoboDK"""
    def __init__(self, settings_param='App-Settings'):
        self._ATTRIBS_SAVE = True
        self._FIELDS_UI = True
        self._SETTINGS_PARAM = settings_param

    def CopyFrom(self, other):
        """Copy settings from another instance"""
        attr = self.getAttribs()
        for a in attr:
            if hasattr(other, a):
                setattr(self,a, getattr(self, a))
        
    def getAttribs(self):
        """Get the list of attributes"""
        return [a for a in dir(self) if (not callable(getattr(self, a)) and not a.startswith("_"))]                
        
    def _getAttribsSave(self):
        """Get list of attributes to save (list of strings)"""
        if type(self._ATTRIBS_SAVE) is list:
            return self._ATTRIBS_SAVE
        return self.getAttribs()
        
    def _getFieldsUI(self):
        """Get dictionary fields to be displayed in the UI"""
        from collections import OrderedDict
        if type(self._FIELDS_UI) is dict or type(self._FIELDS_UI) is OrderedDict:
            return self._FIELDS_UI
           
        attribs = None
        if type(self._FIELDS_UI) is list:
            attribs = self._FIELDS_UI
        else:
            attribs = self.getAttribs()
            
        fields = OrderedDict() 
        for a in attribs:
            fields[a] = a.replace('_',' ')
            
        return fields        
        
    def get(self,attrib,default_value=None):
        """Get attribute value by key, otherwise it returns None"""
        if hasattr(self,attrib):
            return getattr(self,attrib)
        return default_value
            
    def Save(self, rdk=None, autorecover=False):
        # Save the class attributes as a string
        # Use a dictionary and the str/eval buit-in conversion
        attribs_list = self._getAttribsSave()
        if len(attribs_list) <= 0:
            print("Saving skipped")
            return

        print("Saving data to RoboDK station...")
        dict_data = {}
        
        # Important! We must save this but not show it in the UI
        dict_data['_FIELDS_UI'] = self._FIELDS_UI        
        for key in attribs_list:
            dict_data[key] = getattr(self, key)
        
        #Protocol tips: https://docs.python.org/3/library/pickle.html
        import pickle
        bytes_data = pickle.dumps(dict_data,protocol=2) # protocol=2: bynary, compatible with python 2.3 and later
        if rdk is None:
            from robolink import Robolink
            rdk = Robolink()
        
        param_val = self._SETTINGS_PARAM
        param_backup = param_val + "-Backup"

        if autorecover:
            rdk.setParam(param_backup, bytes_data)

        else:
            rdk.setParam(param_val, bytes_data)
            rdk.setParam(param_backup, b'')        

    def Load(self, rdk=None):#, stream_data=b''):
        """Save the class attributes as a RoboDK binary parameter"""
        # Use a dictionary and the str/eval buit-in conversion
        attribs_list = self._getAttribsSave()
        #if len(attribs_list) == 0:
        #    print("Load settings: No attributes to load")
        #    return False

        print("Loading data from RoboDK station...")
        if rdk is None:
            from robolink import Robolink
            rdk = Robolink()

        param_backup = self._SETTINGS_PARAM
        param_backup += "-Backup"
            
        bytes_data = rdk.getParam(param_backup, False)
        if len(bytes_data) > 0:
            result = ShowMessageYesNoCancel("Something went wrong with the last test.\nRecover lost data?", "Auto recover")
            if result is None:
                return False

            elif not result:
                bytes_data = b''

            # Clear backup data
            rdk.setParam(param_backup, b'', False)

        if len(bytes_data) <= 0:
            bytes_data = rdk.getParam(self._SETTINGS_PARAM, False)
        
        if len(bytes_data) <= 0:
            print("Load settings: No data for " + self._SETTINGS_PARAM)
            return False

        import pickle
        saved_dict = pickle.loads(bytes_data)
        for key in saved_dict.keys():
            # if we have a list of attributes that we want, load it only if it is in the list
            if len(attribs_list) > 0 and not key in attribs_list:
                print("Obsolete variable saved (will be deleted): " + key)
                
            else:
                value = saved_dict[key]
                setattr(self,key,value)                    
                
        return True
    
    def ShowUI(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None):
        """Open settings window"""                
        fields_list = self._getFieldsUI()
        w = None
        #wparent = None
        if wparent is not None:        
            w = tk.Toplevel(wparent) 
        else:
            #if embed:
            w = tk.Tk()
            #else:
            #    w = tk.Toplevel()    
            
        obj = self
        #global TEMP_ENTRIES 
        TEMP_ENTRIES = {}
        FLOAT_ARRAY_ATTRIBS = {}
        def add_fields():
            """Creates the UI from the field stored in the variable"""
            # Loop through every field in FIELD to retrieve its information
            
            sticky = tk.NSEW# + tk.S + tk.W #+tk.W
            #weight = 1

            
            frame = tk.Frame(w)
            idrow = -1
            for fkey in fields_list:       
                # Iterate for each key and add the variable to the UI
                field = fields_list[fkey]
                if not field is list:
                    field = [field]

                fname = field[0]
                fvalue = getattr(obj, fkey)
                ftype = type(fvalue)                
                #fother = field[2] # combobox options 

                # Convert None to double
                if ftype is None:
                    ftype = float
                    fvalue = -1.0
                
                tkvar = None

                # Create a row for each field 
                #row = tk.Frame(w)
                idrow = idrow + 1
                
                print(fkey + ' = ' + str(fvalue))
                
                # If the field is combo box
                if ftype is float or ftype is int or (ftype is str and len(field) < 2):
                    lab = tk.Label(frame, width=15, text=fname, anchor='w')

                    if ftype is float:
                        tkvar = tk.DoubleVar()
                        ent = tk.Spinbox(frame, textvariable=tkvar)

                    elif ftype is int:
                        tkvar = tk.IntVar()
                        ent = tk.Spinbox(frame, textvariable=tkvar)

                    elif ftype is str:
                        tkvar = tk.StringVar()                
                        ent = tk.Entry(frame, textvariable=tkvar)

                    else:
                        raise Exception("Uknown variable type: " + str(ftype))

                    tkvar.set(fvalue)

                    #row.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
                    #lab.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
                    #ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                    lab.grid(row=idrow, column=0, sticky=sticky)
                    ent.grid(row=idrow, column=1, sticky=sticky)

                elif ftype is bool:
                    tkvar = tk.BooleanVar()

                    lab = tk.Label(frame, width=15, text=fname, anchor='w') # Set the field label (name)
                    lab.grid(row=idrow, column=0,sticky=sticky)

                    ent = tk.Checkbutton(frame, text="Activate", variable=tkvar)
                    tkvar.set(fvalue)

                    #row.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
                    #ent.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
                    #lab.grid(row=idrow, column=0)
                    ent.grid(row=idrow, column=1,sticky=tk.W)
                    
                elif ftype is list and len(fvalue) > 0 and (type(fvalue[0]) == float or type(fvalue[0]) == int):
                    FLOAT_ARRAY_ATTRIBS[fkey] = len(fvalue)
                    
                    lab = tk.Label(frame, width=15, text=fname, anchor='w') # Set the field label (name)
                    tkvar = tk.StringVar()
                    tkvar.set(str(fvalue)[1:-1])
                    ent = tk.Entry(frame, textvariable=tkvar)
                    
                    lab.grid(row=idrow, column=0,sticky=sticky)
                    ent.grid(row=idrow, column=1,sticky=sticky)
                
                elif ftype is str or ftype is list:
                    # it is a combo box
                    fchoices = []
                    current_choice = ''
                    
                    if len(field) > 1:
                        fchoices = field[2] # Retrieve list of options 
                        current_choice = fchoices[0]
                    
                    if len(fvalue) > 1:
                        current_choice = fvalue[0]
                        fchoices = fvalue[1] # Retrieve list of options                         
                        
                    if len(fchoices) == 0:
                        continue
                        
                    lab = tk.Label(frame, width=15, text=fname, anchor='w') # Set the field label (name)
                    # ent = Entry(row)
                    tkvar = tk.StringVar()
                    tkvar.set(current_choice)
                    
                    # Create the combo box    
                    cmb = tk.OptionMenu(frame, tkvar, *fchoices)#, command=read_inputs)
                    
                    #row.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
                    #lab.pack(side=tk.LEFT)
                    #cmb.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                    lab.grid(row=idrow, column=0,sticky=sticky)
                    cmb.grid(row=idrow, column=1,sticky=sticky)
                
                # Apply row weight
                frame.grid_rowconfigure(idrow, weight=1)                
                TEMP_ENTRIES[fkey] = (field, tkvar)
                
                frame.grid_columnconfigure(0, weight=2)
                frame.grid_columnconfigure(1, weight=1)

                
            frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)

        def read_fields(e=None):
            #if skip_events:
            #    return
            print("Values entered:")
            #print(ENTRIES)
            for fkey in TEMP_ENTRIES:
                entry = TEMP_ENTRIES[fkey]
                #field = entry[0]
                value  = entry[1].get()
                
                # The value is a float array
                print(fkey)
                print(FLOAT_ARRAY_ATTRIBS)
                if fkey in FLOAT_ARRAY_ATTRIBS.keys():
                    value_input = value
                    value = Str2FloatList(value_input, FLOAT_ARRAY_ATTRIBS[fkey])
                    if value is None:
                        ShowMessage("Invalid input: " + value_input)
                        return                    
                
                else:
                    if type(value) == str:
                        value = value.strip()
                    
                    last_value = getattr(obj,fkey)
                    if type(last_value) is list:
                        newvalue = last_value
                        newvalue[0] = value
                        value = newvalue

                print(fkey + " = " + str(value))
                setattr(obj,fkey,value)
            
            # we are done, we need to close the window here            
            self.Save()
            w.destroy()
            
              
            
        add_fields()
        #root.bind('<Return>', (lambda event, e=entries: enter_values(e)))   
        #root.bind('<Return>', enter_values())
        
        
        if callback_frame is not None:
            callback_frame(w)

        row = tk.Frame(w)

        #Creating the Cancel button
        b1 = tk.Button(row, text='Cancel', command=w.destroy, width=8)
        b1.pack(side=tk.LEFT, padx=5, pady=5)

        #Creating the OK button
        bhelper = tk.Button(row, text='OK', command=read_fields, width=8)
        bhelper.pack(side=tk.RIGHT, padx=5, pady=5)

        row.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
                
        w.title(windowtitle)        
        
        import os
        from robolink import getPathIcon
        iconpath = getPathIcon()
        if os.path.exists(iconpath):
            w.iconbitmap(iconpath)  
        
        # Embed the window in RoboDK
        if embed:
            from robolink import EmbedWindow
            EmbedWindow(windowtitle)
        else:
            # If not, make sure to make the window stay on top
            w.attributes("-topmost", True)        


        #def _on_mousewheel(event):
        #    w.yview_scroll(-1*(event.delta/120), "units")
        #w.bind_all("<MouseWheel>", _on_mousewheel)
        
        if wparent is None:
            # Important for unchecking the action in RoboDK
            w.protocol("WM_DELETE_WINDOW", w.destroy)
            w.mainloop()
            
        else:
            print("Settings window: using parent loop")

        #self.Save()
        
        


def runmain():
    # Use the Settings example instead of this example
    S = AppSettings('_tools-sample')
    S.Int_Value = 123456
    S.Float_Value = 0.123456789
    S.String_Value = 'String test'
    S.Float_List = [1,2,3] # 3 numbers minimum!
    S.Boolean = True
    S.Dropdown = ['Chosen value', ['First line', 'Second line', 'Third option']]
    
    
    S.Load()
    S.ShowUI()
    S.Save()
        
if __name__ == "__main__":
    runmain()
        