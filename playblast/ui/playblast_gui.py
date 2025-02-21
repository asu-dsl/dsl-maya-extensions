import maya.cmds as cmds
from playblast.core.playblast_core import (
    find_animated_geometry,
    extended_quad_playblast,
    play_animation,
    remove_virtual_cameras
)

class PlayblastGUI:
    def __init__(self):
        self.window_name = "PlayblastTool_Extended"

    def show(self):
        """Create and show the extended playblast tool window (with aim constraints + offsets)."""
        print("🖥 [INFO] Initializing Extended GUI...")
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        window = cmds.window(
            self.window_name,
            title="Extended Multi-View Playblast Tool (Aim Constraints)",
            widthHeight=(400, 900),
            sizeable=True
        )
        main_layout = cmds.columnLayout(adjustableColumn=True)
        
        # Title
        cmds.text(
            label="Multi-View Playblast (Aim Constraints + Offsets)",
            height=40,
            backgroundColor=[0.2, 0.2, 0.2],
            align="center",
            font="boldLabelFont"
        )
        cmds.separator(height=10)
        
        # --- Output Settings ---
        cmds.frameLayout(label="Output Settings", collapsable=True, collapse=False)
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
        
        # --- Resolution / Quality ---
        cmds.frameLayout(label="Resolution", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True)
        self.width = cmds.intFieldGrp(label="Width: ", value1=1920)
        self.height = cmds.intFieldGrp(label="Height: ", value1=1080)
        self.quality = cmds.intSliderGrp(label="Quality: ", field=True, minValue=1, maxValue=100, value=100)
        cmds.separator(height=10)
        
        # --- View Settings ---
        cmds.frameLayout(label="View Settings", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True)
        self.show_ornaments = cmds.checkBoxGrp(label="Show HUD: ", value1=True)
        self.show_grid = cmds.checkBoxGrp(label="Show Grid: ", value1=False)
        
        cameras = cmds.listCameras()
        self.camera = cmds.optionMenuGrp(label="Camera: ")
        cmds.menuItem(label="Active View")
        for cam in cameras:
            cmds.menuItem(label=cam)
        cmds.separator(height=10)
        
        # --- Camera Constraint & Multi-Offset Settings ---
        cmds.frameLayout(label="Camera Constraints & Offsets", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True)
        self.target_asset = cmds.textFieldButtonGrp(
            label="Target Asset: ",
            text="",
            buttonLabel="Pick",
            buttonCommand=self.pick_target_asset
        )
        cmds.separator(height=5)
        cmds.text(label="Per-Camera Offset (Local X, Y, Z):")
        cmds.text(label="Front Camera Offset:")
        self.offset_front = cmds.floatFieldGrp(numberOfFields=3, value1=0.0, value2=0.0, value3=0.0)
        cmds.text(label="Side Camera Offset:")
        self.offset_side = cmds.floatFieldGrp(numberOfFields=3, value1=0.0, value2=0.0, value3=0.0)
        cmds.text(label="Top Camera Offset:")
        self.offset_top = cmds.floatFieldGrp(numberOfFields=3, value1=0.0, value2=0.0, value3=0.0)
        cmds.text(label="Back Camera Offset:")
        self.offset_back = cmds.floatFieldGrp(numberOfFields=3, value1=0.0, value2=0.0, value3=0.0)
        cmds.separator(height=10)
        self.auto_select_animated = cmds.checkBoxGrp(
            label="Auto-Select Animated Geometry:",
            value1=False
        )
        cmds.separator(height=20)
        
        # --- Create playblast button ---
        cmds.button(
            label="Create Extended Multi-View Playblast",
            height=50,
            command=self.create_playblast,
            backgroundColor=[0.2, 0.4, 0.2]
        )
        cmds.separator(height=10)
        cmds.showWindow(window)
        print("✅ [INFO] Extended GUI displayed successfully.")

    def browse_path(self, *args):
        """Open a file browser to select the output path."""
        path = cmds.fileDialog2(fileMode=3, caption="Select Output Directory")
        if path:
            cmds.textFieldButtonGrp(self.output_path, edit=True, text=path[0])
            print(f"📂 [INFO] Output path selected: {path[0]}")

    def pick_target_asset(self, *args):
        """Pick a target asset to aim cameras at."""
        print("🔎 [INFO] Waiting for user to pick a target asset in the viewport...")
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("No object selected. Please select an object in the scene.")
            return
        asset = selection[0]
        cmds.textFieldButtonGrp(self.target_asset, edit=True, text=asset)
        print(f"✅ [INFO] Target asset set to: {asset}")

    def create_playblast(self, *args):
        """
        Gather settings and run the entire sequence:
         1) Optionally auto-select animated geometry.
         2) Add cameras, apply aim constraints & offsets, and record multi-cam playblast.
         3) Play the animation.
         4) Remove the created cameras.
        """
        print("🎬 [INFO] Starting extended multi-view playblast process from GUI...")
        output_path = cmds.textFieldButtonGrp(self.output_path, query=True, text=True)
        filename = cmds.textFieldGrp(self.filename, query=True, text=True)
        width = cmds.intFieldGrp(self.width, query=True, value1=True)
        height = cmds.intFieldGrp(self.height, query=True, value1=True)
        quality = cmds.intSliderGrp(self.quality, query=True, value=True)
        show_ornaments = cmds.checkBoxGrp(self.show_ornaments, query=True, value1=True)
        show_grid = cmds.checkBoxGrp(self.show_grid, query=True, value1=True)
        camera_selection = cmds.optionMenuGrp(self.camera, query=True, value=True)
        camera = None if camera_selection == "Active View" else camera_selection
        
        # Get constraint target and per-camera offsets
        asset = cmds.textFieldButtonGrp(self.target_asset, query=True, text=True)
        front_offset = cmds.floatFieldGrp(self.offset_front, query=True, value=True)
        side_offset  = cmds.floatFieldGrp(self.offset_side,  query=True, value=True)
        top_offset   = cmds.floatFieldGrp(self.offset_top,   query=True, value=True)
        back_offset  = cmds.floatFieldGrp(self.offset_back,  query=True, value=True)
        offsets = [front_offset, side_offset, top_offset, back_offset]
        auto_select_flag = cmds.checkBoxGrp(self.auto_select_animated, query=True, value1=True)

        print(f"🎥 [INFO] Extended Playblast settings:\n"
              f"  📂 Output Path: {output_path}\n"
              f"  📄 Filename: {filename}\n"
              f"  📏 Resolution: {width}x{height}\n"
              f"  🎞 Quality: {quality}\n"
              f"  📷 Camera: {camera_selection}\n"
              f"  🔗 Target Asset: {asset}\n"
              f"  ↕ Offsets => Front:{front_offset}, Side:{side_offset}, Top:{top_offset}, Back:{back_offset}\n"
              f"  🤖 Auto-Select Animated Geometry: {auto_select_flag}")

        # (A) Auto-select animated geometry if enabled.
        if auto_select_flag:
            animated_nodes = find_animated_geometry()
            if animated_nodes:
                cmds.select(animated_nodes, replace=True)
                print(f"✅ [INFO] Auto-selected animated geometry: {animated_nodes}")
            else:
                print("⚠️ [WARNING] No animated geometry found in the scene.")

        # (B) Add cameras with constraints & offsets and record multi-cam playblast.
        cams = extended_quad_playblast(
            output_path=output_path,
            filename=filename,
            width=width,
            height=height,
            quality=quality,
            show_ornaments=show_ornaments,
            show_grid=show_grid,
            camera=camera,
            target_asset=asset,
            offsets=offsets
        )
        # (C) Play the animation.
        if cams:
            play_animation()
        # (D) Remove the created cameras.
        remove_virtual_cameras(cams)
        print("✅ [INFO] Entire multi-view playblast sequence is complete!")

def show_gui():
    tool = PlayblastGUI()
    tool.show()

if __name__ == '__main__':
    show_gui()
