import maya.cmds as cmds
import os

def export_fbx(filepath, export_name="single_export", selected=True):
    """Exports skeleton (joints), mesh objects, and animation keyframes to a single FBX file."""
    
    # Ensure the export directory exists
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    # Define the export file path
    export_file = os.path.join(filepath, f"{export_name}.fbx")
    
    # Ensure FBX plugin is loaded
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya', quiet=True)

    # Filter the selection to only include joints and geometry (mesh)
    if selected:
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.error("No object selected.")
        
        # Find joints and meshes in the selection
        joints, meshes = find_joints_and_meshes(selection)
    else:
        # Select all joints and meshes in the scene
        joints = cmds.ls(type="joint")
        meshes = cmds.ls(type="mesh", long=True)
    
    # Get the transforms associated with the meshes (parents of the mesh shape nodes)
    mesh_transforms = cmds.listRelatives(meshes, parent=True, fullPath=True) or []
    
    # Combine joints and mesh transforms for export
    export_objects = joints + mesh_transforms if mesh_transforms else joints
    
    # Debugging: Print what's being exported
    print(f"Joints for export: {joints}")
    print(f"Meshes for export: {meshes}")
    print(f"Mesh Transforms for export: {mesh_transforms}")
    
    if not export_objects:
        cmds.error("No joints or mesh objects found for export.")
    
    # Select only the joints and mesh transforms for export
    cmds.select(export_objects, replace=True)
    
    # Bake keyframes to ensure animations are included
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)
    bake_keyframes(export_objects, start_frame, end_frame)
    
    # Perform the export to FBX
    cmds.file(rename=export_file)
    cmds.file(force=True, options="v=0;", type="FBX export", exportSelected=True)
    
    print(f"Exported skeleton, mesh, and animation to {export_file}")


def find_joints_and_meshes(selection):
    """Find all joints and meshes in the given selection hierarchy, including namespaces."""
    joints = []
    meshes = []

    # Traverse through each object in the selection
    for obj in selection:
        # Find all joints and meshes in the hierarchy
        obj_joints = cmds.listRelatives(obj, ad=True, type="joint", fullPath=True) or []
        obj_meshes = cmds.listRelatives(obj, ad=True, type="mesh", fullPath=True) or []
        
        # Add found joints and meshes to the respective lists
        joints.extend(obj_joints)
        meshes.extend(obj_meshes)

    # Return unique joints and meshes
    return list(set(joints)), list(set(meshes))


def bake_keyframes(export_objects, start_frame, end_frame):
    """Bakes keyframes into the joints and mesh objects to ensure animation is included."""
    cmds.bakeResults(export_objects, 
                     t=(start_frame, end_frame), 
                     simulation=True, 
                     preserveOutsideKeys=True, 
                     minimizeRotation=True, 
                     removeBakedAttributeFromLayer=False, 
                     bakeOnOverrideLayer=False, 
                     controlPoints=False, 
                     shape=True)
    print(f"Baked keyframes for export objects from frame {start_frame} to {end_frame}.")



def export_ascii(filepath, export_name="single_export"):
    """Exports only skeleton and mesh objects to Maya ASCII format."""
    
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    ascii_file = os.path.join(filepath, f"{export_name}.ma")
    
    # Perform the export to Maya ASCII format
    cmds.file(rename=ascii_file)
    cmds.file(save=True, type='mayaAscii')

    print(f"Exported Maya ASCII to {ascii_file}")
