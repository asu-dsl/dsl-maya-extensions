import maya.cmds as cmds
import os
import subprocess

def create_four_cameras():
    """Creates four cameras for front, side, top, and back views."""
    print("📸 [INFO] Creating virtual cameras...")

    cams = [
        ("playblast_front", (0, 10, 20),  (0,   0,   0)),
        ("playblast_side",  (20, 10, 0),   (0, -90,   0)),
        ("playblast_top",   (0, 30, 0),   (-90, 0,   0)),
        ("playblast_back",  (0, 10,-20),  (0,  180,  0)),
    ]
    
    created = []
    for cname, pos, rot in cams:
        if cmds.objExists(cname):
            cmds.delete(cname)
        cam_transform, cam_shape = cmds.camera()
        new_transform = cmds.rename(cam_transform, cname)
        cmds.setAttr(f"{new_transform}.translate", *pos)
        cmds.setAttr(f"{new_transform}.rotate",   *rot)
        created.append(new_transform)
        print(f"✅ [SUCCESS] Created camera: {cname} at {pos} with rotation {rot}")
    return created

def combine_videos_ffmpeg(sub_files, final_output, width, height):
    """
    Combine four videos into a quad view using ffmpeg.
    This example command scales each video to half the final resolution,
    then stacks them into a 2x2 grid.
    """
    half_width = int(width / 2)
    half_height = int(height / 2)
    filter_complex = (
        f"[0:v] setpts=PTS-STARTPTS, scale={half_width}x{half_height} [tl];"
        f"[1:v] setpts=PTS-STARTPTS, scale={half_width}x{half_height} [tr];"
        f"[2:v] setpts=PTS-STARTPTS, scale={half_width}x{half_height} [bl];"
        f"[3:v] setpts=PTS-STARTPTS, scale={half_width}x{half_height} [br];"
        f"[tl][tr] hstack=inputs=2 [top];"
        f"[bl][br] hstack=inputs=2 [bottom];"
        f"[top][bottom] vstack=inputs=2 [out]"
    )
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i", sub_files[0],
        "-i", sub_files[1],
        "-i", sub_files[2],
        "-i", sub_files[3],
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:v", "libx264",
        "-crf", "18",
        final_output
    ]
    print("🚀 [INFO] Combining videos using ffmpeg...")
    try:
        subprocess.check_call(ffmpeg_cmd)
        print("✅ [SUCCESS] Videos combined successfully.")
    except Exception as e:
        print(f"❌ [ERROR] ffmpeg failed: {e}")

def one_click_quad_ffmpeg(output_path, filename, width, height, quality, show_ornaments, show_grid, cameras):
    """
    Executes the full multi-view playblast process:
      - Opens a quad view window with four viewports using the selected cameras.
      - Playblasts each viewport.
      - Combines the four videos into one final video.
    """
    print("🚀 [INFO] Starting full playblast process...")
    
    win_name = "QuadViewPlayblast"
    if cmds.window(win_name, exists=True):
        cmds.deleteUI(win_name)
    window = cmds.window(win_name, title="Quad View Playblast", widthHeight=(960, 540))
    layout = cmds.paneLayout(configuration="quad")
    
    panels = []
    # Loop through the four camera selections (one per panel)
    for i, cam_sel in enumerate(cameras):
        mp = cmds.modelPanel(label=f"View_{i+1}", parent=layout)
        panels.append(mp)
        # If "Active View" is selected, default to the main perspective camera "persp"
        cam = "persp" if cam_sel == "Active View" else cam_sel
        if cmds.objExists(cam):
            cmds.modelEditor(mp, e=True, camera=cam)
        else:
            cmds.warning(f"Camera {cam} does not exist. Using default camera 'persp'.")
            cmds.modelEditor(mp, e=True, camera="persp")
        print(f"✅ [SUCCESS] Camera {cam} assigned to viewport {i+1}")
    
    cmds.showWindow(window)
    print("🖥 [INFO] Quad View window opened.")
    
    # Playblast each panel separately
    sub_files = []
    for i, p in enumerate(panels):
        base = os.path.join(output_path, f"{filename}_panel_{i}.avi")
        result = cmds.playblast(
            filename=base,
            format="avi",
            forceOverwrite=True,
            compression="none",
            quality=quality,
            percent=100,
            showOrnaments=show_ornaments,
            viewer=False,
            widthHeight=[width, height]
        )
        if result:
            sub_files.append(base)
            print(f"✅ [SUCCESS] Playblast saved: {base}")
        else:
            print(f"❌ [ERROR] Playblast failed for panel {i+1}")
    
    # If all four playblasts succeeded, merge them into one final video
    if len(sub_files) == 4:
        final_output = os.path.join(output_path, f"{filename}_quad_view.mp4")
        combine_videos_ffmpeg(sub_files, final_output, width, height)
        print(f"✅ [SUCCESS] Final merged playblast saved: {final_output}")
    else:
        print("❌ [ERROR] Some playblasts failed. Skipping merge.")
