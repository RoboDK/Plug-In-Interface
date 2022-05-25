# Copyright 2015-2021 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This is a RoboDK Apps toolbox for RoboDK API for Python
# This toolbox includes checkable apps, app settings, etc.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
# --------------------------------------------

import os
import sys
import time


class RunApplication:
    """Class to detect when the terminate signal is emited to stop an action.

    .. code-block:: python

        run = RunApplication()
        while run.Run():
            # your main loop to run until the terminate signal is detected
            ...

    """
    time_last = -1
    param_name = None
    RDK = None

    def __init__(self, rdk=None):
        if rdk is None:
            from robodk.robolink import Robolink
            self.RDK = Robolink()
        else:
            self.RDK = rdk

        self.time_last = time.time()
        if len(sys.argv) > 0:
            path = sys.argv[0]
            folder = os.path.basename(os.path.dirname(path))
            file = os.path.basename(path)
            if file.endswith(".py"):
                file = file[:-3]
            elif file.endswith(".exe"):
                file = file[:-4]

            self.param_name = file + "_" + folder
            self.RDK.setParam(self.param_name, "1")  # makes sure we can run the file separately in debug mode

    def Run(self):
        time_now = time.time()
        if time_now - self.time_last < 0.1:
            return True
        self.time_last = time_now
        if self.param_name is None:
            # Unknown start
            return True

        keep_running = not (self.RDK.getParam(self.param_name) == 0)
        return keep_running


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
    """Read value from the registry or set a value. It will do so at HKEY_CURRENT_USER so no admin rights required."""
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

        def KeyExist(key, subkey, access) -> bool:
            try:
                hkey = _winreg.OpenKey(key, subkey, 0, access)
            except OSError as e:
                print(e)
                return None
            return hkey

        # Key settings
        access_flag = _winreg.KEY_READ if setvalue is None else _winreg.KEY_WRITE
        key = _winreg.HKEY_CURRENT_USER
        subkey = "SOFTWARE\\RoboDK"

        # Get the key or create a new one (unless we are reading the value)
        hKey = KeyExist(key, subkey, access_flag | _winreg.KEY_WOW64_64KEY)
        if hKey is None:
            hKey = KeyExist(key, subkey, access_flag | _winreg.KEY_WOW64_32KEY)
            if hKey is None and setvalue is not None:
                try:
                    hKey = _winreg.CreateKeyEx(key, subkey, 0, _winreg.KEY_WRITE | _winreg.KEY_WOW64_64KEY)
                except OSError as e:
                    print(e)
                    return None
            else:
                return None

        if setvalue is None:
            # Read the value.
            try:
                result = _winreg.QueryValueEx(hKey, varname)
                _winreg.CloseKey(hKey)
                return result[0]  # Return only the value from the resulting tuple (value, type_as_int).
            except _winreg.QueryValue as e:
                print(e)
                return None
        else:
            # Write the value
            try:
                _winreg.SetValueEx(hKey, varname, 0, _winreg.REG_SZ, str(setvalue))
                _winreg.CloseKey(hKey)
                return None
            except _winreg.SetValue as e:
                print(e)
                return None


# Default to Qt and revert to tkinter if it fails.
ENABLE_QT = True
if ENABLE_QT:
    try:
        from robodk.robolink import import_install
        import_install("PySide2")
        from PySide2 import QtCore, QtGui, QtWidgets
    except:
        # Can't install Qt, fallback to tkinter
        ENABLE_QT = False

import sys
if sys.version_info[0] < 3:
    # Python 2.X only:
    import Tkinter as tkinter
else:
    # Python 3.x only
    import tkinter


class AppSettings:
    """Generic settings class to save and load settings from a RoboDK station and show methods in RoboDK."""

    def __init__(self, settings_param='App-Settings'):
        self._ATTRIBS_SAVE = True
        self._FIELDS_UI = True
        self._SETTINGS_PARAM = settings_param

        self._UI_READ_FIELDS = None

    def CopyFrom(self, other):
        """Copy settings from another instance"""
        attr = self.getAttribs()
        for a in attr:
            if hasattr(other, a):
                setattr(self, a, getattr(other, a))

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
            fields[a] = a.replace('_', ' ')

        return fields

    def get(self, attrib, default_value=None):
        """Get attribute value by key, otherwise it returns None"""
        if hasattr(self, attrib):
            return getattr(self, attrib)
        return default_value

    def Save(self, rdk=None, autorecover=False):
        """Save the class attributes as a RoboDK binary parameter"""
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

        # Protocol tips: https://docs.python.org/3/library/pickle.html
        import pickle
        bytes_data = pickle.dumps(dict_data, protocol=2)  # protocol=2: bynary, compatible with python 2.3 and later
        if rdk is None:
            from robodk.robolink import Robolink
            rdk = Robolink()

        param_val = self._SETTINGS_PARAM
        param_backup = param_val + "-Backup"

        if autorecover:
            rdk.setParam(param_backup, bytes_data)

        else:
            rdk.setParam(param_val, bytes_data)
            rdk.setParam(param_backup, b'')

    def Load(self, rdk=None):  #, stream_data=b''):
        """Load the class attributes from a RoboDK binary parameter"""
        # Use a dictionary and the str/eval buit-in conversion
        attribs_list = self._getAttribsSave()
        #if len(attribs_list) == 0:
        #    print("Load settings: No attributes to load")
        #    return False

        print("Loading data from RoboDK station...")
        if rdk is None:
            from robodk.robolink import Robolink
            rdk = Robolink()

        param_backup = self._SETTINGS_PARAM
        param_backup += "-Backup"

        bytes_data = rdk.getParam(param_backup, False)
        if len(bytes_data) > 0:
            from robodk.robodialogs import ShowMessageYesNoCancel
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
            if len(attribs_list) == 0 or (key not in attribs_list and key != '_FIELDS_UI'):
                print("Obsolete variable saved (will be deleted): " + key)

            else:
                value = saved_dict[key]
                setattr(self, key, value)

        return True

    def __ShowUIPyQt(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None, dark_mode=True):
        """Open settings window"""

        from PySide2 import QtCore, QtGui, QtWidgets

        fields_list = self._getFieldsUI()
        values_list = {key: getattr(self, key) for key in fields_list}

        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])  # No need to create a new one

        windowQt = QtWidgets.QWidget()

        layoutQtWidgetGrid = QtWidgets.QVBoxLayout()
        layoutQtWidgetGrid.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        layoutQtWidgetGrid.setContentsMargins(10, 10, 10, 10)

        big_form = QtWidgets.QFormLayout()
        big_form.setVerticalSpacing(1)
        big_form.setHorizontalSpacing(15)
        layoutQtWidgetGrid.addLayout(big_form)

        windowQt.setLayout(layoutQtWidgetGrid)

        obj = self
        TEMP_ENTRIES = {}

        def value_to_widget(value):
            widget = None
            func = []
            value_type = type(value)

            if value_type is float:
                widget = QtWidgets.QDoubleSpinBox()
                import decimal
                decimals = abs(decimal.Decimal(str(value)).as_tuple().exponent)
                widget.setDecimals(max(4, decimals))
                widget.setRange(-9999999., 9999999.)
                widget.setValue(value)
                func = [widget.value]

            elif value_type is int:
                widget = QtWidgets.QSpinBox()
                widget.setRange(-9999999, 9999999)
                widget.setValue(value)
                func = [widget.value]

            elif value_type is str:
                widget = QtWidgets.QLineEdit()
                widget.setText(value)
                func = [widget.text]

            elif value_type is bool:
                widget = QtWidgets.QCheckBox("Activate")
                widget.setChecked(value)
                func = [widget.isChecked]

            # List or tuple of PODs
            elif value_type in [list, tuple] and len(value) > 0 and all(isinstance(n, (float, int, str, bool)) for n in value):
                h_layout = QtWidgets.QHBoxLayout()
                h_layout.setSpacing(0)
                h_layout.setContentsMargins(0, 0, 0, 0)
                for v in value:
                    f_widget, f_func = value_to_widget(v)
                    func.append(f_func[0])
                    h_layout.addWidget(f_widget)
                widget = QtWidgets.QWidget()
                widget.setLayout(h_layout)

            # ComboBox with specified index as int [1, ['First line', 'Second line', 'Third line']]
            elif value_type is list and (len(value) == 2) and isinstance(value[0], int) and all(isinstance(n, str) for n in value[1]):
                index = value[0]
                options = value[1]
                widget = QtWidgets.QComboBox()
                widget.addItems(options)
                widget.setCurrentIndex(index)
                func = [widget.currentIndex]

            # ComboBox with specified index as str ['Second line', ['First line', 'Second line', 'Third line']]
            elif value_type is list and (len(value) == 2) and isinstance(value[0], str) and all(isinstance(n, str) for n in value[1]) and value[0] in value[1]:
                index = value[1].index(value[0])
                options = value[1]
                widget = QtWidgets.QComboBox()
                widget.addItems(options)
                widget.setCurrentIndex(index)
                #widget.itemText(widget.currentIndex)
                func = [widget.currentIndex]  # str index will be replaced with int index once saved

            return widget, func

        def add_fields():
            """Creates the UI from the field stored in the variable"""

            for fkey in fields_list:
                # Iterate for each key and add the variable to the UI
                field = fields_list[fkey]
                if not field is list:
                    field = [field]

                fname = field[0]
                fvalue = values_list[fkey]
                ftype = type(fvalue)

                # Convert None to double
                if ftype is None:
                    ftype = float
                    fvalue = -1.0

                print(fkey + ' = ' + str(fvalue))

                widget, func = value_to_widget(fvalue)
                if widget is not None:
                    big_form.addRow(QtWidgets.QLabel(fname), widget)
                    TEMP_ENTRIES[fkey] = (field, func)
                else:
                    big_form.addRow(QtWidgets.QLabel(fname), QtWidgets.QLabel('Unsupported'))

        def read_fields():
            print("Values entered:")
            for fkey in TEMP_ENTRIES:
                entry = TEMP_ENTRIES[fkey]
                funcs = entry[1]
                values = [value() for value in funcs]  # tuple needs to be casted below

                for value in values:
                    if type(value) == str:
                        value = value.strip()

                if len(values) == 1:
                    values = values[0]

                # Comboboxes
                last_value = getattr(obj, fkey)
                if (type(last_value) is list) and (len(last_value) == 2) and isinstance(last_value[0], (int, str)) and all(isinstance(n, str) for n in last_value[1]):
                    newvalue = last_value
                    newvalue[0] = value
                    values = newvalue

                # Tuples
                if type(last_value) is tuple:
                    values = tuple(values)

                if type(last_value) != type(values):
                    print('Warning! Type change detected (old:new): %s:%s' % (str(last_value), str(values)))
                    new_type = type(last_value)
                    values = new_type(values)
                print(fkey + " = " + str(values))
                setattr(obj, fkey, values)

        def command_ok():
            read_fields()
            self.Save()
            command_quit()

        def command_cancel():
            command_quit()

        def command_quit():
            self._UI_READ_FIELDS = None
            windowQt.window().close()

        add_fields()

        self._UI_READ_FIELDS = read_fields

        if callback_frame is not None:
            callback_frame(windowQt)

        # Creating the Cancel button
        buttonCancel = QtWidgets.QPushButton(windowQt)
        buttonCancel.setText("Cancel")
        buttonCancel.clicked.connect(command_cancel)

        # Creating the OK button
        buttonOk = QtWidgets.QPushButton(windowQt)
        buttonOk.setText('Save')
        buttonOk.clicked.connect(command_ok)

        OkCancelLayout = QtWidgets.QHBoxLayout()
        OkCancelLayout.addWidget(buttonOk)
        OkCancelLayout.addWidget(buttonCancel)
        layoutQtWidgetGrid.addLayout(OkCancelLayout)

        # Add a spacer to keep the text packed
        qtSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        layoutQtWidgetGrid.addItem(qtSpacer)

        import os
        from robodk.robolink import getPathIcon
        iconpath = getPathIcon()
        if os.path.exists(iconpath):
            windowQt.setWindowIcon(QtGui.QIcon(iconpath))

        # Set the window style
        keys = QtWidgets.QStyleFactory.keys()
        if 'Fusion' in keys:
            app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
            if dark_mode:
                # https://forum.qt.io/topic/101391/windows-10-dark-theme/4
                darkPalette = QtGui.QPalette()
                darkColor = QtGui.QColor(45, 45, 45)
                disabledColor = QtGui.QColor(127, 127, 127)
                darkPalette.setColor(QtGui.QPalette.ColorRole.Window, darkColor)
                darkPalette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("white"))
                darkPalette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(18, 18, 18))
                darkPalette.setColor(QtGui.QPalette.ColorRole.AlternateBase, darkColor)
                darkPalette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor("white"))
                darkPalette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor("white"))
                darkPalette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("white"))
                darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, disabledColor)
                darkPalette.setColor(QtGui.QPalette.ColorRole.Button, darkColor)
                darkPalette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("white"))
                darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, disabledColor)
                darkPalette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor("red"))
                darkPalette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
                darkPalette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
                darkPalette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("black"))
                darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.HighlightedText, disabledColor)
                app.setPalette(darkPalette)

            windowQt.update()

        if embed:
            # Embed the window in RoboDK
            mainWindow = QtWidgets.QMainWindow()
            mainWindow.setCentralWidget(windowQt)
            mainWindow.setWindowTitle(windowtitle)
            mainWindow.update()
            mainWindow.show()

            from robodk.robolink import EmbedWindow
            EmbedWindow(windowtitle)
        else:
            windowQt.setWindowTitle(windowtitle)
            windowQt.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        if wparent is None:
            # Important for unchecking the action in RoboDK
            app.lastWindowClosed.connect(command_quit)
            windowQt.show()
            app.exec_()

    def __ShowUITkinter(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None):
        """Open settings window using tkinter"""

        import sys
        if sys.version_info[0] < 3:
            # Python 2.X only:
            import Tkinter as tkinter
        else:
            # Python 3.x only
            import tkinter

        fields_list = self._getFieldsUI()
        values_list = {key: getattr(self, key) for key in fields_list}

        windowTk = None
        if wparent is not None:
            windowTk = tkinter.Toplevel(wparent)
        else:
            windowTk = tkinter.Tk()

        obj = self
        TEMP_ENTRIES = {}

        def value_to_widget(value, frame):
            widget = None
            func = []
            value_type = type(value)

            if value_type is float:
                tkvar = tkinter.DoubleVar(value=value)
                func = [tkvar.get]
                widget = tkinter.Spinbox(frame, from_=-9999999, to=9999999, textvariable=tkvar, format="%.2f")

            elif value_type is int:
                tkvar = tkinter.IntVar(value=value)
                func = [tkvar.get]
                widget = tkinter.Spinbox(frame, from_=-9999999, to=9999999, textvariable=tkvar)

            elif value_type is str:
                tkvar = tkinter.StringVar(value=value)
                func = [tkvar.get]
                widget = tkinter.Entry(frame, textvariable=tkvar)

            elif value_type is bool:
                tkvar = tkinter.BooleanVar(value=value)
                func = [tkvar.get]
                widget = tkinter.Checkbutton(frame, text="Activate", variable=tkvar)

            # List or tuple of PODs
            elif value_type in [list, tuple] and len(value) > 0 and all(isinstance(n, (float, int, str, bool)) for n in value):
                widget = tkinter.Frame(frame)  # simple sub-container
                idcol = -1
                for v in value:
                    idcol += 1
                    f_widget, f_func = value_to_widget(v, widget)
                    f_widget.grid(row=0, column=idcol, sticky=tkinter.NSEW)
                    func.append(f_func[0])
                    widget.grid_columnconfigure(idcol, weight=1)

            # ComboBox with specified index as int [1, ['First line', 'Second line', 'Third line']]
            elif value_type is list and (len(value) == 2) and isinstance(value[0], int) and all(isinstance(n, str) for n in value[1]):
                index = value[0]
                options = value[1]
                tkvar = tkinter.StringVar(value=options[index])
                widget = tkinter.OptionMenu(frame, tkvar, *options)
                func = [tkvar.get]

            # ComboBox with specified index as str ['Second line', ['First line', 'Second line', 'Third line']]
            elif value_type is list and (len(value) == 2) and isinstance(value[0], str) and all(isinstance(n, str) for n in value[1]) and value[0] in value[1]:
                index = value[0].index(value[0])
                options = value[1]
                tkvar = tkinter.StringVar(value=options[index])
                widget = tkinter.OptionMenu(frame, tkvar, *options)
                func = [tkvar.get]

            return widget, func

        def add_fields():
            """Creates the UI from the field stored in the variable"""
            sticky = tkinter.NSEW
            frame = tkinter.Frame(windowTk)
            idrow = -1

            for fkey in fields_list:
                idrow += 1

                # Iterate for each key and add the variable to the UI
                field = fields_list[fkey]
                if not field is list:
                    field = [field]

                fname = field[0]
                fvalue = values_list[fkey]
                ftype = type(fvalue)

                # Convert None to double
                if ftype is None:
                    ftype = float
                    fvalue = -1.0

                print(fkey + ' = ' + str(fvalue))

                widget, func = value_to_widget(fvalue, frame)
                label_name = tkinter.Label(frame, text=fname, anchor='w')
                label_name.grid(row=idrow, column=0, sticky=sticky)

                if widget is not None:
                    _sticky = sticky
                    if type(widget) is tkinter.Checkbutton:
                        _sticky = tkinter.W
                    widget.grid(row=idrow, column=1, sticky=_sticky)

                    TEMP_ENTRIES[fkey] = (field, func)
                else:
                    label_unsupported = tkinter.Label(frame, text='Unsupported')
                    label_unsupported.grid(row=idrow, column=1, sticky=sticky)

                frame.grid_rowconfigure(idrow, weight=1)
                frame.grid_columnconfigure(0, weight=1)
                frame.grid_columnconfigure(1, weight=1)

            frame.pack(side=tkinter.TOP, fill=tkinter.X, padx=1, pady=1)

        def read_fields():
            print("Values entered:")
            for fkey in TEMP_ENTRIES:
                entry = TEMP_ENTRIES[fkey]
                funcs = entry[1]
                values = [value() for value in funcs]  # tuple needs to be casted below

                for value in values:
                    if type(value) == str:
                        value = value.strip()

                if len(values) == 1:
                    values = values[0]

                # Comboboxes
                last_value = getattr(obj, fkey)
                if (type(last_value) is list) and (len(last_value) == 2) and isinstance(last_value[0], (int, str)) and all(isinstance(n, str) for n in last_value[1]):
                    newvalue = last_value
                    newvalue[0] = value
                    values = newvalue

                # Tuples
                if type(last_value) is tuple:
                    values = tuple(values)

                if type(last_value) != type(values):
                    print('Warning! Type change detected (old:new): %s:%s' % (str(last_value), str(values)))
                    new_type = type(last_value)
                    values = new_type(values)
                print(fkey + " = " + str(values))
                setattr(obj, fkey, values)

        def command_ok():
            read_fields()
            self.Save()
            command_quit()

        def command_cancel():
            command_quit()

        def command_quit():
            self._UI_READ_FIELDS = None
            windowTk.destroy()

        add_fields()

        self._UI_READ_FIELDS = read_fields

        # Everything after the callframe will be added after whatever is added to the frame
        if callback_frame is not None:
            callback_frame(windowTk)

        row = tkinter.Frame(windowTk)

        #Creating the Cancel button
        b_cancel = tkinter.Button(row, text='Cancel', command=command_cancel, width=8)
        b_cancel.pack(side=tkinter.LEFT, padx=5, pady=5)

        #Creating the OK button
        b_ok = tkinter.Button(row, text='Save', command=command_ok, width=8)
        b_ok.pack(side=tkinter.RIGHT, padx=5, pady=5)

        row.pack(side=tkinter.TOP, fill=tkinter.X, padx=1, pady=1)

        windowTk.title(windowtitle)

        from robodk.robolink import getPathIcon
        iconpath = getPathIcon()
        if os.path.exists(iconpath):
            windowTk.iconbitmap(iconpath)

        # Embed the window in RoboDK
        if embed:
            from robodk.robolink import EmbedWindow
            EmbedWindow(windowtitle)
        else:
            # If not, make sure to make the window stay on top
            windowTk.attributes("-topmost", True)

        #def _on_mousewheel(event):
        #    windowTk.yview_scroll(-1*(event.delta/120), "units")
        #windowTk.bind_all("<MouseWheel>", _on_mousewheel)

        if wparent is None:
            # Important for unchecking the action in RoboDK
            windowTk.protocol("WM_DELETE_WINDOW", command_quit)
            windowTk.mainloop()

        else:
            print("Settings window: using parent loop")

    def ShowUI(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None):
        if ENABLE_QT:
            # Get RoboDK theme
            from robodk.robolink import Robolink
            rdk = Robolink()
            theme = rdk.Command("Theme", "")
            self.__ShowUIPyQt(windowtitle, embed, wparent, callback_frame, dark_mode=theme in ['0', '2'])
        else:
            self.__ShowUITkinter(windowtitle, embed, wparent, callback_frame)


def runmain():
    #------------------------------------------------------------------------
    # Using custom call backs with SettingsExample
    class SettingsExample(AppSettings):
        """Example of AppSettings using custom call backs"""

        # Variable names when displayed on the user interface.
        # Create this dictionary in the same order that you want to display it.
        # If not provided, all variables of this class will be used.
        from collections import OrderedDict
        __FIELDS_UI = OrderedDict()
        __FIELDS_UI['Boolean'] = 'This is a bool'
        __FIELDS_UI['Int_Value'] = 'This is an int'
        __FIELDS_UI['Float_Value'] = 'This is a float'
        __FIELDS_UI['String_Value'] = 'This is a string'
        __FIELDS_UI['Int_List'] = 'This is an int list'
        __FIELDS_UI['Float_List'] = 'This is a float list'
        __FIELDS_UI['String_List'] = 'This is a string list'
        __FIELDS_UI['Mixed_List'] = 'This is a mixed list'
        __FIELDS_UI['Int_Tuple'] = 'This is an int tuple'
        __FIELDS_UI['Dropdown'] = 'This is a dropdown'
        __FIELDS_UI['Dropdown2'] = 'This is a dropdown too'
        __FIELDS_UI['Unsupported'] = 'This is unsupported'

        # List the variable names you would like to save and their default values
        # Important: Try to avoid default None type!!
        # If None is used as default value it will attempt to treat it as a float and None = -1
        # Variables that start with underscore (_) will not be saved
        Boolean = True
        Int_Value = 123456
        Float_Value = 0.123456789
        String_Value = 'String test'
        Int_List = [1, 2, 3]  # 3 numbers minimum!
        Float_List = [1.0, 2.0, 3.0]  # 3 numbers minimum!
        String_List = ['First line', 'Second line', 'Third line']
        Mixed_List = [False, 1, '2']
        Int_Tuple = (1, 2, 3)
        Dropdown = ['Second line', ['First line', 'Second line', 'Third line']]
        Dropdown2 = [1, ['First line', 'Second line', 'Third line']]
        Unsupported = {}
        _HiddenUnsavedBool = True
        HiddenSavedBool = True

        def __init__(self):
            # customize the initialization section if needed
            super(SettingsExample, self).__init__()
            self._FIELDS_UI = self.__FIELDS_UI

        def SetDefaults(self):
            # List untouched variables for default settings
            list_untouched = []

            # save in local variables
            for var in list_untouched:
                exec('%s=self.%s' % (var, var))

            defaults = SettingsExample()
            self.CopyFrom(defaults)

            # restore from local vars
            for var in list_untouched:
                exec('self.%s=%s' % (var, var))

        def ShowUI(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None):
            # Show the UI for these settings including a custom frame to set the default settings. TODO: Compatibility with PyQT
            if not ENABLE_QT:

                def custom_frame(w):

                    def set_defaults():
                        w.destroy()
                        self.SetDefaults()
                        self.ShowUI(windowtitle=windowtitle, embed=embed, wparent=wparent, callback_frame=custom_frame)

                    row = tkinter.Frame(w)
                    b_defaults = tkinter.Button(row, text='Set defaults', command=set_defaults, width=8)
                    b_defaults.pack(side=tkinter.LEFT, padx=5, pady=5)
                    row.pack(side=tkinter.TOP, fill=tkinter.X, padx=1, pady=1)
            else:

                def custom_frame(w: QtWidgets.QWidget):

                    def set_defaults():
                        w.window().close()
                        w.deleteLater()
                        self.SetDefaults()
                        self.ShowUI(windowtitle=windowtitle, embed=embed, wparent=wparent, callback_frame=custom_frame)

                    layout = w.layout()
                    b_default = QtWidgets.QPushButton('Set defaults')
                    b_default.clicked.connect(set_defaults)
                    layout.addWidget(b_default)

            super(SettingsExample, self).ShowUI(windowtitle=windowtitle, embed=embed, wparent=wparent, callback_frame=custom_frame)

    #------------------------------------------------------------------------
    S = SettingsExample()
    #S.Load()
    print('S._HiddenUnsavedBool: ' + str(S._HiddenUnsavedBool))
    print('S.HiddenSavedBool: ' + str(S.HiddenSavedBool))
    S.ShowUI(embed=False)
    S._HiddenUnsavedBool = not S._HiddenUnsavedBool
    S.HiddenSavedBool = not S.HiddenSavedBool
    S.Save()

    #------------------------------------------------------------------------
    # Using the AppSettings as is
    A = AppSettings()
    from collections import OrderedDict
    A._FIELDS_UI = OrderedDict()
    A._FIELDS_UI['Boolean'] = 'This is a bool'
    A._FIELDS_UI['Int_Value'] = 'This is an int'
    A._FIELDS_UI['Float_Value'] = 'This is a float'
    A._FIELDS_UI['String_Value'] = 'This is a string'
    A._FIELDS_UI['Float_List'] = 'This is a float list'
    A._FIELDS_UI['Int_List'] = 'This is an int list'
    A._FIELDS_UI['String_List'] = 'This is a string list'
    A._FIELDS_UI['Mixed_List'] = 'This is a mixed list'
    A._FIELDS_UI['Int_Tuple'] = 'This is an int tuple'
    A._FIELDS_UI['Dropdown'] = 'This is a dropdown'
    A._FIELDS_UI['Dropdown2'] = 'This is a dropdown too'
    A._FIELDS_UI['Unsupported'] = 'This is unsupported'

    A.Boolean = True
    A.Int_Value = 123456
    A.Float_Value = 0.123456789
    A.String_Value = 'String test'
    A.Int_List = [1, 2, 3]  # 3 numbers minimum!
    A.Float_List = [1.0, 2.0, 3.0]  # 3 numbers minimum!
    A.String_List = ['First line', 'Second line', 'Third line']
    A.Mixed_List = [False, 1, '2']
    A.Int_Tuple = (1, 2, 3)
    A.Dropdown = ['Second line', ['First line', 'Second line', 'Third line']]
    A.Dropdown2 = [1, ['First line', 'Second line', 'Third line']]
    A.Unsupported = {}
    A._HiddenUnsavedBool = True
    A.HiddenSavedBool = True

    #A.Load()
    print('A._HiddenUnsavedBool: ' + str(A._HiddenUnsavedBool))
    print('A.HiddenSavedBool: ' + str(A.HiddenSavedBool))
    A.ShowUI(embed=False)
    A._HiddenUnsavedBool = not A._HiddenUnsavedBool
    A.HiddenSavedBool = not A.HiddenSavedBool
    A.Save()


if __name__ == "__main__":
    runmain()
