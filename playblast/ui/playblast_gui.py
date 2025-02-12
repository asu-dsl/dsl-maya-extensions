import maya.cmds as cmds
import os
from core.playblast_core import one_click_quad_ffmpeg

class PlayblastGUI:
    def __init__(self):
        self.window_name = "PlayblastTool"
        
    def show(self):
        """Create and show the playblast tool window."""
        print("🖥 [INFO] Initializing GUI...")
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        window = cmds.window(
            self.window_name,
            title="Multi-View Playblast Tool",
            widthHeight=(400, 600),
            sizeable=True
        )
        
        main_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.text(label="Multi-View Playblast", height=40, backgroundColor=[0.2, 0.2, 0.2], 
                  align="center", font="boldLabelFont")
        cmds.separator(height=10)
        
        # Output Settings
        cmds.frameLayout(label="Output Settings", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        
        self.output_path = cmds.textFieldButtonGrp(
            label="Output Path: ",
            text="C:/temp",
            buttonLabel="Browse",
            buttonCommand=self.browse_path
        )
        
        self.filename = cmds.textFieldGrp(
            label="Filename: ",
            text="quad_view_playblast"
        )
        
        cmds.separator(height=10)
        
        # Resolution Settings
        cmds.frameLayout(label="Resolution", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        
        self.width = cmds.intFieldGrp(label="Width: ", value1=1920)
        self.height = cmds.intFieldGrp(label="Height: ", value1=1080)
        self.quality = cmds.intSliderGrp(label="Quality: ", field=True, minValue=1, maxValue=100, value=100)
        
        cmds.separator(height=10)
        
        # View Settings (HUD, Grid, Cameras)
        cmds.frameLayout(label="View Settings", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        
        self.show_ornaments = cmds.checkBoxGrp(label="Show HUD: ", value1=True)
        self.show_grid = cmds.checkBoxGrp(label="Show Grid: ", value1=False)
        
        # Retrieve cameras in the scene (or empty list if none)
        cameras = cmds.listCameras() or []
        
        # Create four drop-down menus for selecting cameras
        self.camera1 = cmds.optionMenuGrp(label="Camera 1: ")
        cmds.menuItem(label="Active View")
        for cam in cameras:
            cmds.menuItem(label=cam)
        
        self.camera2 = cmds.optionMenuGrp(label="Camera 2: ")
        cmds.menuItem(label="Active View")
        for cam in cameras:
            cmds.menuItem(label=cam)
        
        self.camera3 = cmds.optionMenuGrp(label="Camera 3: ")
        cmds.menuItem(label="Active View")
        for cam in cameras:
            cmds.menuItem(label=cam)
        
        self.camera4 = cmds.optionMenuGrp(label="Camera 4: ")
        cmds.menuItem(label="Active View")
        for cam in cameras:
            cmds.menuItem(label=cam)
        
        cmds.separator(height=20)
        
        cmds.button(
            label="Create Multi-View Playblast",
            height=50,
            command=self.create_playblast,
            backgroundColor=[0.2, 0.4, 0.2]
        )
        
        cmds.showWindow(window)
        print("🖥 [INFO] GUI displayed successfully.")

    def browse_path(self, *args):
        """Open a file browser to select the output path."""
        path = cmds.fileDialog2(fileMode=3, caption="Select Output Directory")
        if path:
            cmds.textFieldButtonGrp(self.output_path, edit=True, text=path[0])
            print(f"📂 [INFO] Output path selected: {path[0]}")
    
    def create_playblast(self, *args):
        """Gather settings and start multi-view playblast process."""
        print("🎬 [INFO] Starting playblast process from GUI...")

        output_path = cmds.textFieldButtonGrp(self.output_path, query=True, text=True)
        filename = cmds.textFieldGrp(self.filename, query=True, text=True)
        width = cmds.intFieldGrp(self.width, query=True, value1=True)
        height = cmds.intFieldGrp(self.height, query=True, value1=True)
        quality = cmds.intSliderGrp(self.quality, query=True, value=True)
        show_ornaments = cmds.checkBoxGrp(self.show_ornaments, query=True, value1=True)
        show_grid = cmds.checkBoxGrp(self.show_grid, query=True, value1=True)
        
        # Gather camera selections from the four dropdowns
        cam1 = cmds.optionMenuGrp(self.camera1, query=True, value=True)
        cam2 = cmds.optionMenuGrp(self.camera2, query=True, value=True)
        cam3 = cmds.optionMenuGrp(self.camera3, query=True, value=True)
        cam4 = cmds.optionMenuGrp(self.camera4, query=True, value=True)
        selected_cameras = [cam1, cam2, cam3, cam4]

        print(f"🎥 [INFO] Playblast settings:\n"
              f"  📂 Output Path: {output_path}\n"
              f"  📄 Filename: {filename}\n"
              f"  📏 Resolution: {width}x{height}\n"
              f"  🎞 Quality: {quality}\n"
              f"  📷 Cameras: {selected_cameras}")

        one_click_quad_ffmpeg(output_path, filename, width, height, quality, show_ornaments, show_grid, selected_cameras)

def show_gui():
    """Display the Playblast GUI."""
    gui = PlayblastGUI()
    gui.show()

if __name__ == '__main__':
    show_gui()
