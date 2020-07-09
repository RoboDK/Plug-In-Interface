# Manage recorded 3D views using a list of named views

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------

from robolink import *
from robodk import *
import ast



if sys.version_info[0] < 3: # Python 2.X only:
    #import Tkinter as tk
    import tkMessageBox as messagebox
else: # Python 3.x only
    #import tkinter as tk
    from tkinter import messagebox

def ShowMessageYesNoCancel(msg, title=None):
    print(msg)
    if title is None:
        title = msg
        
    root = tkinter.Tk()
    root.overrideredirect(1)
    root.withdraw()
    root.attributes("-topmost", True)        
    result = messagebox.askyesnocancel(title, msg)#, icon='warning')#, parent=texto)
    root.destroy()
    return result

# Start the RoboDK API
RDK = Robolink()

def LoadView(view_name, vr_view=False):
    import ast
    vp_str = RDK.getParam(view_name)
    if vp_str is None:
        RDK.ShowMessage("Preferred view not recorded. Save a view point first", False)
        quit()
        
    # Lazy way to convert a list as a string to a list of floats
    #exec('vp_xyzabc = ' + vp_str, locals())
    vp_xyzabc = ast.literal_eval(vp_str)
    
    vp = KUKA_2_Pose(vp_xyzabc)
    
    if vr_view:
        # Set headset VR view
        RDK.Command("ViewPose", str(pose_2_xyzrxyz(vp)))
        
    else:
        # Set normal VR view
        RDK.setViewPose(vp)

    print("Done")

if __name__ == "__main__":
    # Define the station parameter name
    #VIEW_NAME = "SavedView"
    #LoadView(VIEW_NAME)
    
    # Name of the view we can use with the first button of the toolbar
    MAIN_VIEW_NAME = "Main View"
    
    ListNames = []
    ListPoses = []
        
    def SaveViews():        
        # The first view is always the main view
        strall = ""
        for i in range(0,len(ListNames)):
            if i == 0 and ListNames[i] == MAIN_VIEW_NAME:
                continue
            
            x,y,z,a,b,c = Pose_2_KUKA(ListPoses[i])
            stri = "%s|[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f]" % (ListNames[i],x,y,z,a,b,c)
            strall += "%s||" % stri
            print(stri)
                
        RDK.setParam("ViewNames", strall)
        
    

    vp_str = RDK.getParam("ViewPose")
    if vp_str is not None:
        vp_xyzabc = ast.literal_eval(vp_str)    
        vp = KUKA_2_Pose(vp_xyzabc)
        ListNames.append(MAIN_VIEW_NAME)                
        ListPoses.append(vp)
        
    strvp_all = RDK.getParam("ViewNames")
    if strvp_all is not None:
        for strvp in strvp_all.split("||"):
            strvp_slt = strvp.split("|")
            if len(strvp) > 1:
                vp_xyzabc = ast.literal_eval(strvp_slt[1])
                if len(vp_xyzabc) >= 6:
                    vp = KUKA_2_Pose(vp_xyzabc)
                    view_name = strvp_slt[0]
                    print("Loaded view: " + strvp);
                    ListNames.append(view_name)                
                    ListPoses.append(vp)  
        
    w = tkinter.Tk()      
    
    w.attributes("-topmost", True) 
    w.title("Manage views")
    iconpath = getPathIcon()
    if os.path.exists(iconpath):
        w.iconbitmap(iconpath)  

    w.geometry("200x300")

    listbox = tkinter.Listbox(w)  

    for i in range(len(ListNames)):
        listbox.insert(i+1, ListNames[i])
        
    #listbox.select_set(0) #(0, tkinter.END)
    
    # Select all
    #listbox.select_set(0, tkinter.END)

    def on_ListDelete():
        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return
            
        for index in sel[::-1]: # move backwards!!
            print(index)
            nm = ListNames[index]
            if ShowMessageYesNoCancel("Delete view: " + nm):                
                del ListNames[index]
                del ListPoses[index]
                listbox.delete(index) # delete from UI
                    
                SaveViews()

                msg = "Deleted view: " + nm
                RDK.ShowMessage(msg, False)

    def on_ListRename():
        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return
        
        for index in sel:
            print(index)
            lbli = ListNames[index]
            new_name = mbox("Enter the view name for %s" % listbox.get(index), entry=lbli)
            if not new_name:
                continue
            
            ListNames[index] = new_name
            listbox.delete(index)
            listbox.insert(index, new_name)

            msg = "Renamed selected view to " + ListNames[index]
            RDK.ShowMessage(msg, False)
            
        SaveViews()
        
    def on_ListUpdate():
        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return
        
        for index in sel:
            print(index)
            ListPoses[index] = RDK.ViewPose()
            break
            
        SaveViews()
        
        msg = "Updated view: " + ListNames[index]
        RDK.ShowMessage(msg, False)

    def on_ListAdd():  
        sel = listbox.curselection()    
        new_name = mbox("Enter the view name", entry="New View %i" % (len(ListNames)+1))
        if not new_name:
            return
            
        index_after = len(ListNames)
        for index in sel:
            index_after = index+1
            break
            
        vp = RDK.ViewPose()
        
        listbox.insert(index_after, new_name)
        
        ListNames.append(new_name)                
        ListPoses.append(vp)
        
        SaveViews()
        
        msg = "Recorded view: " + new_name
        RDK.ShowMessage(msg, False)
    
    def on_ListShow(evtdblclick=None):
        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return
        
        index = 0
        for index in sel:
            print(index)
            vp = ListPoses[index]
            
            strpose = str(Pose_2_TxyzRxyz(transl(0,0,+2000)*vp))[1:-1]
            result = RDK.Command("ViewPoseVR", strpose)

            RDK.setViewPose(vp)
            
            msg = "Selected view: " + ListNames[index]
            RDK.ShowMessage(msg, False)

            break

    def on_ListUp():
        sel = listbox.curselection()
        for index in sel:
            print(index)
            if index >= 2:
                oldindex = index
                newindex = index - 1 
                ListNames.insert(newindex, ListNames.pop(oldindex))
                ListPoses.insert(newindex, ListPoses.pop(oldindex))       
     
                listbox.delete(oldindex)
                listbox.insert(newindex, ListNames[newindex])        

                listbox.select_set(newindex)
            break

        SaveViews()
            
    def on_ListDown():
        sel = listbox.curselection()
        for index in sel:
            print(index)
            if index >= 1 and index < (len(ListNames)-1):
                oldindex = index
                newindex = index + 1 
                ListNames.insert(newindex, ListNames.pop(oldindex))
                ListPoses.insert(newindex, ListPoses.pop(oldindex))            
                
                listbox.delete(oldindex)
                listbox.insert(newindex, ListNames[newindex])         

                listbox.select_set(newindex)
            break

        SaveViews()
            
            
    btnDel = tkinter.Button(w, text = "Delete", command=on_ListDelete)          
    btnDel.pack(fill=tkinter.X, side=tkinter.BOTTOM)
      
    btnShow = tkinter.Button(w, text = "Down", command=on_ListDown)          
    btnShow.pack(fill=tkinter.X, side=tkinter.BOTTOM)    
    
    btnShow = tkinter.Button(w, text = "Up", command=on_ListUp)          
    btnShow.pack(fill=tkinter.X, side=tkinter.BOTTOM)    
    
    btnRename = tkinter.Button(w, text = "Rename", command=on_ListRename)          
    btnRename.pack(fill=tkinter.X, side=tkinter.BOTTOM) 
    
    btnRec = tkinter.Button(w, text = "Record View", command=on_ListUpdate)          
    btnRec.pack(fill=tkinter.X, side=tkinter.BOTTOM)   
    
    btnRec = tkinter.Button(w, text = "Add View", command=on_ListAdd)          
    btnRec.pack(fill=tkinter.X, side=tkinter.BOTTOM)  
    
    btnGo = tkinter.Button(w, text = "Move to view", command=on_ListShow)          
    btnGo.pack(fill=tkinter.X, side=tkinter.BOTTOM)  
    
    listbox.pack(fill=tkinter.X, side=tkinter.TOP)
    listbox.bind('<Double-Button>', on_ListShow)

    w.mainloop()

    print("Finished")
    
    
    
    