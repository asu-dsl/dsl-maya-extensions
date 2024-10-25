import maya.cmds as cmds
import os
from core.exporter import export_fbx, export_ascii
from core.cleanup import cleanup_scene

def show_gui():
    """Creates the tool's main GUI window with enhanced layout and styling."""
    window_name = "MyExportTool"
    
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    # Create main window with resizable option
    window = cmds.window(window_name, title="My Export Tool", widthHeight=(400, 300), sizeable=True)
    main_layout = cmds.columnLayout(adjustableColumn=True)

    # Title Section
    cmds.text(label="DreamTools Exporter", align="center", height=40, 
              backgroundColor=[0.2, 0.6, 0.8], font="boldLabelFont")

    # Export Path Section
    cmds.frameLayout(label="Export Settings", collapsable=True, marginHeight=15)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Select Export Path:", align="left")
    export_path = cmds.textFieldButtonGrp(label="Path: ", buttonLabel="Browse", 
                                          buttonCommand=lambda: browse_path(export_path), columnAlign=(1, "left"))

    cmds.setParent(main_layout)  # Ensure we're back in the main layout

    # Export Buttons Section with large buttons
    cmds.frameLayout(label="Export Options", collapsable=True, marginHeight=15)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="Export FBX", height=50, command=lambda _: export_fbx(cmds.textFieldButtonGrp(export_path, query=True, text=True)))
    cmds.button(label="Export ASCII", height=50, command=lambda _: export_ascii(cmds.textFieldButtonGrp(export_path, query=True, text=True)))
    cmds.button(label="Cleanup Scene", height=50, command=lambda _: cleanup_scene())

    # Show the window
    cmds.showWindow(window)

def browse_path(export_path):
    """Opens a file browser dialog to select export path."""
    path = cmds.fileDialog2(fileMode=3, caption="Select Folder")
    if path:
        cmds.textFieldButtonGrp(export_path, edit=True, text=path[0])
