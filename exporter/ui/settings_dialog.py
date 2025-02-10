import maya.cmds as cmds
from ..config.settings import ConfigManager

class SettingsDialog:
    def __init__(self):
        self.config = ConfigManager()
        self.window_name = "ExportToolSettings"
        
    def show(self):
        # Delete window if it exists
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        # Create window
        window = cmds.window(
            self.window_name,
            title="Export Tool Settings",
            widthHeight=(400, 200),
            sizeable=False
        )
        
        # Main layout
        main_layout = cmds.columnLayout(adjustableColumn=True)
        
        # Add some spacing at the top
        cmds.separator(height=10, style='none')
        
        # Prefix setting
        current_prefix = self.config.get_setting('export_prefix', 'asset_')
        self.prefix_field = cmds.textFieldGrp(
            label="Export Prefix: ",
            text=current_prefix,
            columnWidth=[(1, 100), (2, 250)],
            columnAlign=(1, "left")
        )
        
        # Add space between fields
        cmds.separator(height=20, style='none')
        
        # Save button
        cmds.button(
            label="Save Settings",
            height=40,
            command=self.save_settings
        )
        
        # Add some spacing at the bottom
        cmds.separator(height=10, style='none')
        
        cmds.showWindow(window)
        
    def save_settings(self, *args):
        """Save the current settings and close the dialog."""
        new_prefix = cmds.textFieldGrp(self.prefix_field, query=True, text=True)
        self.config.set_setting('export_prefix', new_prefix)
        cmds.deleteUI(self.window_name)