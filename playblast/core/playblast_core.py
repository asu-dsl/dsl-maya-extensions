import maya.cmds as cmds
import os
import subprocess
import time

# ----------------------------------------------------------------------------------
# Helper: Detect all transforms with animCurves connected
# ----------------------------------------------------------------------------------
def find_animated_geometry():
    """
    Find transforms in the scene that have animation curves connected.
    Returns a list of animated transforms.
    """
    animated = []
    all_transforms = cmds.ls(type="transform")
    if not all_transforms:
        return animated

    for node in all_transforms:
        anim_curves = cmds.listConnections(node, type="animCurve")
        if anim_curves:
            animated.append(node)
    return animated

# ----------------------------------------------------------------------------------
# Helper: Create four cameras (front, side, top, back)
# ----------------------------------------------------------------------------------
def create_four_cameras():
    """
    Creates four cameras for front, side, top, and back views.
    Returns a list of camera transform names in that order.
    """
    print("📸 [INFO] Creating four virtual cameras (front, side, top, back)...")

    cams_data = [
        ("playblast_front", (0, 10, 20),  (0,   0,   0)),
        ("playblast_side",  (20, 10, 0),   (0, -90,   0)),
        ("playblast_top",   (0, 30, 0),   (-90, 0,   0)),
        ("playblast_back",  (0, 10,-20),  (0,  180,  0)),
    ]
    created = []
    for cname, pos, rot in cams_data:
        if cmds.objExists(cname):
            print(f"⚠️ [WARNING] Deleting existing camera: {cname}")
            cmds.delete(cname)

        cam_transform, cam_shape = cmds.camera()
        new_transform = cmds.rename(cam_transform, cname)
        # Set initial position/rotation
        cmds.setAttr(f"{new_transform}.translate", *pos)
        cmds.setAttr(f"{new_transform}.rotate",   *rot)

        created.append(new_transform)
        print(f"✅ [SUCCESS] Created camera '{cname}' at {pos} with rotation {rot}")

    return created

# ----------------------------------------------------------------------------------
# Helper: Get FPS from Maya's current time unit
# ----------------------------------------------------------------------------------
def get_fps():
    """
    Map Maya's time unit to frames-per-second. If unknown, default to 24.
    """
    time_unit = cmds.currentUnit(query=True, time=True)
    fps_map = {
        'film': 24,
        'pal': 25,
        'ntsc': 30,
        'show': 48,
        'palf': 50,
        'ntscf': 60,
        'game': 15
    }
    return fps_map.get(time_unit, 24)

# ----------------------------------------------------------------------------------
# Extended multi-view approach with AIM constraints for each camera
# ----------------------------------------------------------------------------------
def extended_quad_playblast(
    output_path,
    filename,
    width,
    height,
    quality,
    show_ornaments,
    show_grid,
    camera,
    target_asset,
    offsets
):
    """
    1) Create 4 cameras.
    2) Aim each camera at the target asset (if specified) and apply local offsets.
    3) Open quad view and playblast each panel.
    4) Merge with FFmpeg.
    Returns the list of created camera transforms.
    """
    print("🚀 [INFO] Running extended multi-view playblast with AIM constraints & per-camera offsets...")

    # (1) Create four cameras in order: front, side, top, back
    cams = create_four_cameras()  # e.g. [frontCam, sideCam, topCam, backCam]

    # (2) If target asset is valid, do aimConstraint + local offsets
    if target_asset and cmds.objExists(target_asset):
        print(f"🔗 [INFO] Aim constraining cameras to: {target_asset}")
        for i, cam_transform in enumerate(cams):
            # Remove existing constraints if any
            existing_cons = cmds.listRelatives(cam_transform, type="constraint")
            if existing_cons:
                cmds.delete(existing_cons)
            # Aim constraint
            cmds.aimConstraint(
                target_asset,
                cam_transform,
                aimVector=(0, 0, -1),   # cameras look down negative Z
                upVector=(0, 1, 0),
                worldUpType="scene",
                mo=False
            )
            # Apply local offset for the camera
            ox, oy, oz = offsets[i]
            cmds.move(ox, oy, oz, cam_transform + ".scalePivot", cam_transform + ".rotatePivot", r=True, os=True)
            print(f"✅ [SUCCESS] {cam_transform} local offset => ({ox}, {oy}, {oz})")
    else:
        print("⚠️ [WARNING] No valid target asset specified. Cameras remain unconstrained.")
        # Apply offsets even if unconstrained:
        for i, cam_transform in enumerate(cams):
            ox, oy, oz = offsets[i]
            cmds.move(ox, oy, oz, cam_transform + ".scalePivot", cam_transform + ".rotatePivot", r=True, os=True)
            print(f"✅ [SUCCESS] {cam_transform} local offset => ({ox}, {oy}, {oz}), unconstrained")

    # (3) Open a quad layout
    win_name = "QuadViewPlayblast_Extended"
    if cmds.window(win_name, exists=True):
        cmds.deleteUI(win_name)
    window = cmds.window(win_name, title="Quad View (Extended w/ Aim)", widthHeight=(960, 540))
    layout = cmds.paneLayout(configuration="quad")

    panels = []
    for i, cam in enumerate(cams):
        mp = cmds.modelPanel(label=f"View_{i+1}", parent=layout)
        panels.append(mp)
        cmds.modelEditor(mp, e=True, camera=cam)
        cmds.modelEditor(mp, e=True, grid=show_grid)

    cmds.showWindow(window)
    print("🖥 [INFO] Quad window opened. Starting multi-view playblasts...")

    # (4) Playblast each panel
    sub_files = []
    for i, p in enumerate(panels):
        out_file = os.path.join(output_path, f"{filename}_panel_{i}.avi")
        print(f"🎬 [INFO] Playblasting => {out_file}")
        result = cmds.playblast(
            filename=out_file,
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
            print(f"✅ [SUCCESS] Single panel playblast => {out_file}")
            sub_files.append(out_file)
        else:
            print(f"❌ [ERROR] Single panel playblast failed for panel {i+1}")

    # (5) If all 4 playblasts succeeded, combine them into one video
    if len(sub_files) == 4:
        final_mp4 = os.path.join(output_path, f"{filename}_quad_view.mp4")
        combine_videos_ffmpeg(sub_files, final_mp4)
        print(f"✅ [SUCCESS] Final extended quad playblast => {final_mp4}")
    else:
        print("❌ [ERROR] Some panel blasts failed. Skipping final combination.")

    return cams  # Return the list of created camera transforms

# ----------------------------------------------------------------------------------
# Combine 4 .avi files into a 2x2 .mp4 using FFmpeg
# ----------------------------------------------------------------------------------
def combine_videos_ffmpeg(files_in, file_out):
    print("🎞 [INFO] Combining videos with FFmpeg =>", file_out)
    ffmpeg_path = r"C:\Users\mahar\Documents\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
    if not os.path.exists(ffmpeg_path):
        print("❌ [ERROR] FFmpeg not found. Skipping merge.")
        return

    filter_graph = (
        "[0:v][1:v]hstack=inputs=2[top]; "
        "[2:v][3:v]hstack=inputs=2[bottom]; "
        "[top][bottom]vstack=inputs=2[out]"
    )

    cmd = [
        ffmpeg_path, "-y",
        "-i", files_in[0],
        "-i", files_in[1],
        "-i", files_in[2],
        "-i", files_in[3],
        "-filter_complex", filter_graph,
        "-map", "[out]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        file_out
    ]
    print(f"🔹 [INFO] Running FFmpeg command: {' '.join(cmd)}")
    subprocess.run(cmd)

# ----------------------------------------------------------------------------------
# Play the animation in real time
# ----------------------------------------------------------------------------------
def play_animation():
    print("▶️ [INFO] Playing the animation in real time...")
    start = cmds.playbackOptions(q=True, minTime=True)
    end   = cmds.playbackOptions(q=True, maxTime=True)
    fps   = get_fps()
    duration_seconds = (end - start) / fps

    cmds.play(forward=True)
    print(f"🕒 [INFO] Animation playing from frame {start} to {end} at ~{fps} fps...")
    time.sleep(duration_seconds)
    cmds.play(state=False)
    print("⏹ [INFO] Animation playback stopped.")

# ----------------------------------------------------------------------------------
# Remove the created cameras from the scene
# ----------------------------------------------------------------------------------
def remove_virtual_cameras(cameras):
    print("🗑 [INFO] Removing virtual cameras from scene...")
    for cam_transform in cameras:
        if cmds.objExists(cam_transform):
            cmds.delete(cam_transform)
            print(f"✅ [SUCCESS] Removed camera: {cam_transform}")
    print("🗑 [INFO] All cameras removed.")
