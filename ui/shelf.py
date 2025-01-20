import maya.cmds as cmds
import os

def create_shelf():
    """Creates a custom shelf button to open the tool's GUI."""
    shelf_name = "ASU_DSL_Shelf"
    
    # Delete the shelf if it already exists to avoid conflicts
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name)
    
    # Get all shelves layouts
    all_shelves = cmds.layout('ShelfLayout', query=True, childArray=True)
    if not all_shelves:
        cmds.warning("Could not find main shelf layout")
        return
        
    # Create new shelf
    shelf = cmds.shelfLayout(shelf_name, parent='ShelfLayout')
    
    # Get the icon path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, 'buttons', 'sparky.png')
    
    # Ensure the icon exists, otherwise use a default Maya icon
    if not os.path.exists(icon_path):
        icon_path = "commandButton.png"
    
    try:
        # Add Export Tool Button
        cmds.shelfButton(
            parent=shelf,
            label="Export",
            annotation="ASU DSL Export Tool",
            image=icon_path,
            command="import ui.gui as gui; gui.show_gui()",
            sourceType="python",
            style='iconAndTextCentered',
            imageOverlayLabel='',
            overlayLabelColor=[1, 1, 1],
            overlayLabelBackColor=[0, 0, 0, 0],
            width=32,
            height=32
        )
        print(f"Created ASU DSL shelf button successfully")
    except Exception as e:
        cmds.warning(f"Failed to create shelf button: {str(e)}")
        return

def remove_shelf():
    """Removes the custom shelf."""
    shelf_name = "ASU_DSL_Shelf"
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name)
        print(f"Removed {shelf_name} shelf")