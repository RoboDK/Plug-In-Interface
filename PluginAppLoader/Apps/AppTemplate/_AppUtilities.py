# Sharable modules, ignored by the AppLoader when prefixed with '_'
from robodk import robolink

APP_OPTION_KEY = 'APP_OPTION'
APP_OPTION_A_KEY = 'APP_OPTION_A'
APP_OPTION_B_KEY = 'APP_OPTION_B'


def ShowMessage(RDK, action_name, message, popup):
    """Prefix a message with the action name and forwards it to robodk.robolink.Robolink.ShowMessage."""
    s = '\n\n' if popup else ' '
    RDK.ShowMessage(f"{action_name}:{s}{message}", popup)


if __name__ == '__main__':
    pass