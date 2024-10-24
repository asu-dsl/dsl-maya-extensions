import maya.cmds as cmds
import os
from core.exporter import export_fbx, export_ascii
from core.cleanup import cleanup_scene

def show_gui():
    """Creates the tool's main GUI window."""
    window_name = "MyExportTool"
    
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    window = cmds.window(window_name, title="My Export Tool", widthHeight=(300, 200))
    layout = cmds.columnLayout(adjustableColumn=True)
    
    # Select Asset Section
    cmds.text(label="Select Export Path:")
    export_path = cmds.textFieldButtonGrp(label="Path: ", buttonLabel="Browse", buttonCommand=lambda: browse_path())
    
    # Export and Cleanup Buttons
    cmds.button(label="Export FBX", command=lambda _: export_fbx(cmds.textFieldButtonGrp(export_path, query=True, text=True)))
    cmds.button(label="Export ASCII", command=lambda _: export_ascii(cmds.textFieldButtonGrp(export_path, query=True, text=True)))
    cmds.button(label="Cleanup Scene", command=lambda _: cleanup_scene())
    
    cmds.showWindow(window)

def browse_path():
    """Opens a file browser dialog to select export path."""
    path = cmds.fileDialog2(fileMode=3, caption="Select Folder")
    if path:
        cmds.textFieldButtonGrp(edit=True, text=path[0])
