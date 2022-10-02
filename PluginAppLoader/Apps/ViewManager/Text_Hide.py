from robodk.robolink import *
#RDK = Robolink(args=["-SKIPINI", "-TREE_STATE=0"])
RDK = Robolink()

RDK.Command("ShowText", 0)  # Hide text
