# playblast/core/playblast.py
import maya.cmds as cmds
import maya.mel as mel
import os

def create_playblast(
    output_path,
    filename,
    width=1920,
    height=1080,
    quality=100,
    compression="H.264",
    show_ornaments=True,
    show_grid=False,
    camera=None
):
    """
    Create a playblast with the specified settings.
    
    Args:
        output_path (str): Directory to save the playblast
        filename (str): Name of the output file (without extension)
        width (int): Width of the playblast in pixels
        height (int): Height of the playblast in pixels
        quality (int): Quality setting (1-100)
        compression (str): Compression format
        show_ornaments (bool): Whether to show HUD elements
        show_grid (bool): Whether to show the grid
        camera (str): Specific camera to use (None for active view)
    """
    # Ensure output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    # Full output path
    output_file = os.path.join(output_path, f"{filename}.mov")
    
    # Store current camera if none specified
    if not camera:
        panel = cmds.playblast(activeEditor=True)
        camera = cmds.modelPanel(panel, query=True, camera=True)
    
    # Store current settings
    current_grid = cmds.grid(query=True, toggle=True)
    
    try:
        # Configure view settings
        cmds.grid(toggle=show_grid)
        
        # Configure display settings
        if not show_ornaments:
            mel.eval("setJS_HUDsVisible(0);")
            
        # Create the playblast
        cmds.playblast(
            filename=output_file,
            format="qt",
            compression=compression,
            quality=quality,
            width=width,
            height=height,
            percent=100,
            showOrnaments=show_ornaments,
            clearCache=True,
            viewer=True,
            offScreen=False,
            framePadding=4,
            forceOverwrite=True,
            camera=camera
        )
        
        print(f"Playblast created successfully: {output_file}")
        return True
        
    except Exception as e:
        cmds.warning(f"Failed to create playblast: {str(e)}")
        return False
        
    finally:
        # Restore settings
        cmds.grid(toggle=current_grid)
        if not show_ornaments:
            mel.eval("setJS_HUDsVisible(1);")