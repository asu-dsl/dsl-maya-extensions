import maya.cmds as cmds
from ui.gui import show_gui

def create_shelf():
    """Creates a custom shelf button to open the tool's GUI."""
    shelf_name = "MyToolShelf"
    
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name)
    
    cmds.shelfLayout(shelf_name, parent="ShelfLayout")
    
    # Add Export Tool Button
    cmds.shelfButton(label="Export Tool",
                     image="commandButton.png",  # Icon for the shelf button
                     command="import ui.gui; ui.gui.show_gui()")
