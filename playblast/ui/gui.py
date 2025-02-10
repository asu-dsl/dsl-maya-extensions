# playblast/ui/gui.py
import maya.cmds as cmds
import os
from ..core.playblast import create_playblast
from ..config.settings import ConfigManager

class PlayblastGUI:
    def __init__(self):
        self.window_name = "PlayblastTool"
        self.config = ConfigManager()
        
    def show(self):
        """Create and show the playblast tool window."""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        # Create window
        window = cmds.window(
            self.window_name,
            title="Playblast Tool",
            widthHeight=(400, 500),
            sizeable=True
        )
        
        main_layout = cmds.columnLayout(adjustableColumn=True)
        
        # Title
        cmds.text(label="Quick Playblast", height=40, backgroundColor=[0.2, 0.2, 0.2], 
                 align="center", font="boldLabelFont")
        cmds.separator(height=10)
        
        # Output settings
        cmds.frameLayout(label="Output Settings", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        
        # Get last used path
        last_path = self.config.get_setting('last_playblast_path', '')
        
        self.output_path = cmds.textFieldButtonGrp(
            label="Output Path: ",
            text=last_path,
            buttonLabel="Browse",
            buttonCommand=self.browse_path
        )
        
        self.filename = cmds.textFieldGrp(
            label="Filename: ",
            text="playblast"
        )
        
        cmds.separator(height=10)
        
        # Resolution settings
        cmds.frameLayout(label="Resolution", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        
        self.width = cmds.intFieldGrp(
            label="Width: ",
            value1=1920,
            columnWidth=[(1, 100), (2, 60)]
        )
        
        self.height = cmds.intFieldGrp(
            label="Height: ",
            value1=1080,
            columnWidth=[(1, 100), (2, 60)]
        )
        
        self.quality = cmds.intSliderGrp(
            label="Quality: ",
            field=True,
            minValue=1,
            maxValue=100,
            value=100
        )
        
        cmds.separator(height=10)
        
        # View settings
        cmds.frameLayout(label="View Settings", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        
        self.show_ornaments = cmds.checkBoxGrp(
            label="Show HUD: ",
            value1=True
        )
        
        self.show_grid = cmds.checkBoxGrp(
            label="Show Grid: ",
            value1=False
        )
        
        # Camera selection
        cameras = cmds.listCameras()
        self.camera = cmds.optionMenuGrp(label="Camera: ")
        cmds.menuItem(label="Active View")
        for cam in cameras:
            cmds.menuItem(label=cam)
            
        cmds.separator(height=20)
        
        # Create playblast button
        cmds.button(
            label="Create Playblast",
            height=50,
            command=self.create_playblast,
            backgroundColor=[0.2, 0.4, 0.2]
        )
        
        cmds.showWindow(window)
        
    def browse_path(self, *args):
        """Open a file browser to select the output path."""
        path = cmds.fileDialog2(fileMode=3, caption="Select Output Directory")
        if path:
            path = path[0]
            cmds.textFieldButtonGrp(self.output_path, edit=True, text=path)
            self.config.set_setting('last_playblast_path', path)
            
    def create_playblast(self, *args):
        """Gather settings and create the playblast."""
        # Get settings from UI
        output_path = cmds.textFieldButtonGrp(self.output_path, query=True, text=True)
        filename = cmds.textFieldGrp(self.filename, query=True, text=True)
        width = cmds.intFieldGrp(self.width, query=True, value1=True)
        height = cmds.intFieldGrp(self.height, query=True, value1=True)
        quality = cmds.intSliderGrp(self.quality, query=True, value=True)
        show_ornaments = cmds.checkBoxGrp(self.show_ornaments, query=True, value1=True)
        show_grid = cmds.checkBoxGrp(self.show_grid, query=True, value1=True)
        
        # Get selected camera (None for Active View)
        camera_selection = cmds.optionMenuGrp(self.camera, query=True, value=True)
        camera = None if camera_selection == "Active View" else camera_selection
        
        # Create the playblast
        if not output_path:
            cmds.warning("Please select an output path.")
            return
            
        success = create_playblast(
            output_path=output_path,
            filename=filename,
            width=width,
            height=height,
            quality=quality,
            show_ornaments=show_ornaments,
            show_grid=show_grid,
            camera=camera
        )
        
        if success:
            cmds.confirmDialog(
                title="Success",
                message=f"Playblast created successfully!\nLocation: {output_path}",
                button=["OK"],
                defaultButton="OK"
            )

def show_gui():
    """Show the playblast tool GUI."""
    tool = PlayblastGUI()
    tool.show()