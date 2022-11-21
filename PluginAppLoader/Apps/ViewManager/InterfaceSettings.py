# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Interface settings class.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps


class InterfaceSettings(roboapps.AppSettings):
    """Interface Settings"""

    def __init__(self, settings_param='Interface-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        # IMPORTANT! The default settings below should be the same as RoboDK's default

        # --------------------------------------------
        self._FIELDS_UI['SECTION_WINDOW'] = "$Window$"

        self._FIELDS_UI['WINDOW_STATE'] = 'Window state'
        self.WINDOW_STATE = [3, ['Show', 'Minimized', 'Normal', 'Maximized', 'Fullscreen', 'Cinema', 'Fullscreen + Cinema', 'Video']]

        # --------------------------------------------
        self._FIELDS_UI['SECTION_FLAGS'] = "$Tree$"

        self._FIELDS_UI['FLAG_ROBODK_TREE_ACTIVE'] = "Enable tree"
        self._FIELDS_UI['FLAG_ROBODK_TREE_VISIBLE'] = "Show tree"
        self.FLAG_ROBODK_TREE_ACTIVE = True
        self.FLAG_ROBODK_TREE_VISIBLE = True

        # --------------------------------------------
        self._FIELDS_UI['SECTION_3DVIEW'] = "$3D View$"

        self._FIELDS_UI['FLAG_ROBODK_3DVIEW_ACTIVE'] = "Show 3D view"
        self._FIELDS_UI['VIEW_SIZE_TYPE'] = 'Set 3D view size'
        self._FIELDS_UI['VIEW_SIZE'] = '3D view size (width,height) [px,px]'
        self._FIELDS_UI['FLAG_ROBODK_REFERENCES_VISIBLE'] = "Show reference frames"
        self._FIELDS_UI['SHOW_CURVES'] = "Show curves"
        self._FIELDS_UI['SHOW_POINTS'] = "Show points"
        self._FIELDS_UI['SHOW_TEXT'] = "Show text"
        self._FIELDS_UI['SHOW_TEXT_OBJECT'] = "Show text of objects"
        self._FIELDS_UI['DISPLAY_THRESHOLD'] = "Minimum object size [% of screen]"
        self.FLAG_ROBODK_3DVIEW_ACTIVE = True
        self.VIEW_SIZE_TYPE = [0, ['Keep Current', 'Manual']]
        self.VIEW_SIZE = (1920, 1080)
        self.FLAG_ROBODK_REFERENCES_VISIBLE = True
        self.SHOW_CURVES = True
        self.SHOW_POINTS = True
        self.SHOW_TEXT = True
        self.SHOW_TEXT_OBJECT = True
        self.DISPLAY_THRESHOLD = 0.5

        # --------------------------------------------
        self._FIELDS_UI['SECTION_TOOLBAR'] = "$Toolbars$"

        self._FIELDS_UI['TOOLBAR_LAYOUT'] = 'Toolbar Layout'
        self._FIELDS_UI['FLAG_ROBODK_STATUSBAR_VISIBLE'] = "Show status bar"
        self.TOOLBAR_LAYOUT = [0, ['Default', 'None', 'Viewer', 'Basic', 'Simple', 'Complete', 'Palletizing']]  # 'Basic', 'Complete', 'Viewer'
        self.FLAG_ROBODK_STATUSBAR_VISIBLE = True

        # --------------------------------------------
        self._FIELDS_UI['SECTION_MOUSE'] = "$Mouse & Keyboard$"

        self._FIELDS_UI['ENABLE_MOUSE_FEEDBACK'] = "Enable mouse feedback"
        self._FIELDS_UI['FLAG_ROBODK_LEFT_CLICK'] = "Enable mouse left-click"
        self._FIELDS_UI['FLAG_ROBODK_RIGHT_CLICK'] = "Enable mouse right-click"
        self._FIELDS_UI['FLAG_ROBODK_DOUBLE_CLICK'] = "Enable mouse double-click"
        self._FIELDS_UI['FLAG_ROBODK_WINDOWKEYS_ACTIVE'] = "Enable enable keystrokes"
        self.ENABLE_MOUSE_FEEDBACK = True
        self.FLAG_ROBODK_LEFT_CLICK = True
        self.FLAG_ROBODK_RIGHT_CLICK = True
        self.FLAG_ROBODK_DOUBLE_CLICK = True
        self.FLAG_ROBODK_WINDOWKEYS_ACTIVE = True

        # --------------------------------------------
        self._FIELDS_UI['SECTION_MENU'] = "$Menus$"

        self._FIELDS_UI['FLAG_ROBODK_MENU_ACTIVE'] = "Enable main menu toolbar"
        self._FIELDS_UI['FLAG_ROBODK_MENUFILE_ACTIVE'] = "Enable File menu"
        self._FIELDS_UI['FLAG_ROBODK_MENUEDIT_ACTIVE'] = "Enable Edit menu"
        self._FIELDS_UI['FLAG_ROBODK_MENUPROGRAM_ACTIVE'] = "Enable Program menu"
        self._FIELDS_UI['FLAG_ROBODK_MENUTOOLS_ACTIVE'] = "Enable Tools menu"
        self._FIELDS_UI['FLAG_ROBODK_MENUUTILITIES_ACTIVE'] = "Enable Utilities menu"
        self._FIELDS_UI['FLAG_ROBODK_MENUCONNECT_ACTIVE'] = "Enable Connect menu"
        self.FLAG_ROBODK_MENU_ACTIVE = True
        self.FLAG_ROBODK_MENUFILE_ACTIVE = True
        self.FLAG_ROBODK_MENUEDIT_ACTIVE = True
        self.FLAG_ROBODK_MENUPROGRAM_ACTIVE = True
        self.FLAG_ROBODK_MENUTOOLS_ACTIVE = True
        self.FLAG_ROBODK_MENUUTILITIES_ACTIVE = True
        self.FLAG_ROBODK_MENUCONNECT_ACTIVE = True

    def Apply(self):
        return ApplyInterfaceSettings(S=self)


def ApplyInterfaceSettings(RDK=None, S=None):
    """Apply the interface settings to RoboDK"""
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = InterfaceSettings.Settings()
        S.Load(RDK)

    RDK.Render(False)

    # --------------------------------------------
    window_state = S.WINDOW_STATE[0]
    RDK.setWindowState(robolink.WINDOWSTATE_NORMAL)  # Reset everything, including toolbar layout
    RDK.setWindowState(window_state)

    RDK.Render(False)

    # --------------------------------------------
    flags_robodk = robolink.FLAG_ROBODK_NONE

    if S.FLAG_ROBODK_TREE_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_TREE_ACTIVE
    if S.FLAG_ROBODK_3DVIEW_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_3DVIEW_ACTIVE
    if S.FLAG_ROBODK_LEFT_CLICK:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_LEFT_CLICK
    if S.FLAG_ROBODK_RIGHT_CLICK:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_RIGHT_CLICK
    if S.FLAG_ROBODK_DOUBLE_CLICK:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_DOUBLE_CLICK
    if S.FLAG_ROBODK_MENU_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENU_ACTIVE
    if S.FLAG_ROBODK_MENUFILE_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENUFILE_ACTIVE
    if S.FLAG_ROBODK_MENUEDIT_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENUEDIT_ACTIVE
    if S.FLAG_ROBODK_MENUPROGRAM_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENUPROGRAM_ACTIVE
    if S.FLAG_ROBODK_MENUTOOLS_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENUTOOLS_ACTIVE
    if S.FLAG_ROBODK_MENUUTILITIES_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENUUTILITIES_ACTIVE
    if S.FLAG_ROBODK_MENUCONNECT_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_MENUCONNECT_ACTIVE
    if S.FLAG_ROBODK_WINDOWKEYS_ACTIVE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_WINDOWKEYS_ACTIVE
    if S.FLAG_ROBODK_TREE_VISIBLE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_TREE_VISIBLE
    if S.FLAG_ROBODK_REFERENCES_VISIBLE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_REFERENCES_VISIBLE
    if S.FLAG_ROBODK_STATUSBAR_VISIBLE:
        flags_robodk = flags_robodk | robolink.FLAG_ROBODK_STATUSBAR_VISIBLE

    RDK.setFlagsRoboDK(flags_robodk)

    # --------------------------------------------
    RDK.Render(False)

    if S.TOOLBAR_LAYOUT[0] > 0:  # default is set by WINDOWSTATE_NORMAL
        RDK.Command("ToolbarLayout", S.TOOLBAR_LAYOUT[1][S.TOOLBAR_LAYOUT[0]])

    RDK.Command("MouseFeedback", 1 if S.ENABLE_MOUSE_FEEDBACK else 0)

    RDK.Command("DisplayCurves", 1 if S.SHOW_CURVES else 0)
    RDK.Command("DisplayPoints", 1 if S.SHOW_POINTS else 0)

    RDK.Command("ShowText", 1 if S.SHOW_TEXT else 0)
    RDK.Command("ShowTextObject", 1 if S.SHOW_TEXT_OBJECT else 0)

    RDK.Command("DisplayThreshold", S.DISPLAY_THRESHOLD if S.DISPLAY_THRESHOLD > 0 else -1)

    if S.VIEW_SIZE_TYPE[0] != 0:
        RDK.Command('SetSize3D', f"{S.VIEW_SIZE[0]}x{S.VIEW_SIZE[1]}")

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        S = InterfaceSettings('Interface-Settings-Custom')
        S.Load()
        if not S.ShowUI('Interface Settings (Custom)'):
            return
        ApplyInterfaceSettings(S=S)


if __name__ == '__main__':
    runmain()