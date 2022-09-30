# Show the status bar of RoboDK
from robodk import robolink

RDK = robolink.Robolink()

# FLAG_ROBODK_REFERENCES_VISIBLE = 16384      # Make the reference frames visible
FLAG_ROBODK_STATUSBAR_VISIBLE = 2 * robolink.FLAG_ROBODK_REFERENCES_VISIBLE
flagsrdk = robolink.FLAG_ROBODK_ALL & ~FLAG_ROBODK_STATUSBAR_VISIBLE

RDK.setFlagsRoboDK(flagsrdk)  # Detached and hidden
