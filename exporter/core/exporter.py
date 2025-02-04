import maya.cmds as cmds
import os
import maya.mel as mel
from . import rig_utils

def suppress_warnings():
    cmds.scriptEditorInfo(suppressWarnings=True, suppressInfo=True, suppressResults=True)

def enable_warnings():
    cmds.scriptEditorInfo(suppressWarnings=False, suppressInfo=False, suppressResults=False)

def export_fbx(filepath, export_name="single_export", selected=True):
    # Ensure the export directory exists
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    # Define the export file path
    export_file = os.path.join(filepath, f"{export_name}.fbx")
    
    # Load the FBX plugin
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya', quiet=True)

    # Get selected joints and meshes or entire scene if no selection
    if selected:
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.error("No object selected.")
        joints, meshes = find_joints_and_meshes(selection)
    else:
        joints = cmds.ls(type="joint")
        meshes = cmds.ls(type="mesh", long=True)
    
    mesh_transforms = cmds.listRelatives(meshes, parent=True, fullPath=True) or []
    export_objects = joints + mesh_transforms if mesh_transforms else joints

    if not export_objects:
        cmds.error("No joints or mesh objects found for export.")
    
    # Bind poses for skinned meshes
    ensure_bind_pose()

    # Root alignment
    root = export_objects[0] if export_objects else None
    root_check(root)

    # Bake keyframes and remove constraints
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)
    bake_keyframes(export_objects, start_frame, end_frame)
    
    # Select only relevant objects for export
    cmds.select(export_objects, replace=True)
    
    # Export to FBX
    cmds.file(rename=export_file)
    cmds.file(force=True, options="v=0;", type="FBX export", exportSelected=True)
    
    print(f"Exported skeleton, mesh, and animation to {export_file}")

def root_check(root):
    if cmds.objExists(root):
        cmds.rotate(0, 0, 0, root, os=True)
        cmds.move(0, 0, 0, root, os=True)

def ensure_bind_pose():
    skin_clusters = cmds.ls(type='skinCluster')
    for skin in skin_clusters:
        joints = cmds.skinCluster(skin, q=True, inf=True)
        for joint in joints:
            bind_pose = cmds.dagPose(joint, q=True, bindPose=True)
            if not bind_pose:
                cmds.dagPose(joint, save=True, bindPose=True)
    print("Bind poses ensured for all skinned joints.")

def find_joints_and_meshes(selection):
    joints = []
    meshes = []
    for obj in selection:
        obj_joints = cmds.listRelatives(obj, ad=True, type="joint", fullPath=True) or []
        obj_meshes = cmds.listRelatives(obj, ad=True, type="mesh", fullPath=True) or []
        joints.extend(obj_joints)
        meshes.extend(obj_meshes)
    return list(set(joints)), list(set(meshes))

def bake_keyframes(export_objects, start_frame, end_frame):
    cmds.bakeResults(
        export_objects, 
        t=(start_frame, end_frame), 
        simulation=True, 
        preserveOutsideKeys=True, 
        minimizeRotation=True, 
        removeBakedAttributeFromLayer=False, 
        bakeOnOverrideLayer=False, 
        controlPoints=False, 
        shape=True
    )
    constraints = cmds.ls(type='constraint')
    if constraints:
        for constraint in constraints:
            try:
                cmds.delete(constraint)
            except:
                print(f"Could not delete constraint {constraint}. It may be locked or read-only.")
    print(f"Baked keyframes and removed constraints from {export_objects} for frames {start_frame} to {end_frame}.")

# Wrapper function to suppress warnings around the export
def export_fbx_silent(filepath, export_name="single_export", selected=True):
    suppress_warnings()
    try:
        export_fbx(filepath, export_name, selected)
    finally:
        enable_warnings()


def export_ascii(filepath, export_name="single_export"):
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    ascii_file = os.path.join(filepath, f"{export_name}.ma")
    cmds.file(rename=ascii_file)
    cmds.file(save=True, type='mayaAscii')

    print(f"Exported Maya ASCII to {ascii_file}")
