import maya.cmds as cmds
import os
from ..core.exporter import export_fbx, export_ascii, export_fbx_silent
from ..core.cleanup import cleanup_scene
from ..config.settings import ConfigManager
from .settings_dialog import SettingsDialog
from .utils import try_auto_select_rig

# No changes needed for cleanup.py, exporter.py, or utils.py as they don't have tool-specific imports

class ExportToolGUI:
    def __init__(self):
        self.config = ConfigManager()
        self.window_name = "MyExportTool"
        self.settings_dialog = SettingsDialog()
        
    def show(self):
        """Creates the tool's main GUI window with enhanced layout and styling."""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        
        # Create main window with resizable option
        window = cmds.window(self.window_name, title="My Export Tool", widthHeight=(400, 300), sizeable=True)
        main_layout = cmds.columnLayout(adjustableColumn=True)

        # Title Section with Settings Button
        title_row = cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(320, 80))
        cmds.text(label="DreamTools Exporter", align="center", height=40, 
                backgroundColor=[0.2, 0.6, 0.8], font="boldLabelFont")
        cmds.button(label="Settings", width=80, height=40, 
                   command=lambda x: self.settings_dialog.show())
        cmds.setParent(main_layout)

        # Export Path Section
        cmds.frameLayout(label="Export Settings", collapsable=True, marginHeight=15)
        cmds.columnLayout(adjustableColumn=True)
        
        # Export name field with default from config
        default_name = self.config.get_default_export_name()
        self.export_name = cmds.textFieldGrp(
            label="Export Name: ",
            text=default_name,
            columnAlign=(1, "left"),
            columnWidth=[(1, 80), (2, 280)]
        )
        
        # Export path field
        cmds.text(label="Select Export Path:", align="left")
        last_path = self.config.get_setting('last_export_path', '')
        self.export_path = cmds.textFieldButtonGrp(
            label="Path: ", 
            text=last_path,
            buttonLabel="Browse", 
            buttonCommand=self.browse_path,
            columnAlign=(1, "left")
        )

        cmds.setParent(main_layout)

        # Export Buttons Section
        cmds.frameLayout(label="Export Options", collapsable=True, marginHeight=15)
        cmds.columnLayout(adjustableColumn=True)
        
        # Export buttons
        cmds.button(
            label="Export FBX", 
            height=50, 
            command=self.export_fbx
        )
        cmds.button(
            label="Export ASCII", 
            height=50, 
            command=self.export_ascii
        )
        cmds.button(label="Cleanup Scene", height=50, command=lambda x: cleanup_scene())

        # Show the window
        cmds.showWindow(window)

    def browse_path(self, *args):
        """Opens a file browser dialog to select export path."""
        path = cmds.fileDialog2(fileMode=3, caption="Select Folder")
        if path:
            path = path[0]
            cmds.textFieldButtonGrp(self.export_path, edit=True, text=path)
            self.config.set_setting('last_export_path', path)

    def export_fbx(self, *args):
        """Handle FBX export with current settings."""
        from ..core.rig_utils import ensure_rig_selected
        
        # Check if we have a rig selected or can select one
        if not ensure_rig_selected():
            cmds.warning("No rig found in scene. Please select a rig to export.")
            return
            
        path = cmds.textFieldButtonGrp(self.export_path, query=True, text=True)
        name = cmds.textFieldGrp(self.export_name, query=True, text=True)
        export_fbx_silent(path, name)

    def export_ascii(self, *args):
        """Handle ASCII export with current settings."""
        from core.rig_utils import ensure_rig_selected
        
        # Check if we have a rig selected or can select one
        if not ensure_rig_selected():
            cmds.warning("No rig found in scene. Please select a rig to export.")
            return
            
        path = cmds.textFieldButtonGrp(self.export_path, query=True, text=True)
        name = cmds.textFieldGrp(self.export_name, query=True, text=True)
        export_ascii(path, name)

# Function to create instance and show window
def show_gui():
    tool = ExportToolGUI()
    tool.show()