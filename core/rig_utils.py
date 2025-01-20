import maya.cmds as cmds

def get_scene_rigs():
    """
    Find character rigs in the scene based on common rig characteristics.
    Returns a list of top-level rig nodes.
    """
    potential_rigs = []
    
    # Look for skeletal structures
    all_joints = cmds.ls(type='joint', long=True)
    if all_joints:
        # Find root joints (no joint parents)
        for joint in all_joints:
            parent = cmds.listRelatives(joint, parent=True, type='joint')
            if not parent:
                # Get the top transform node
                top_node = joint
                while True:
                    parent = cmds.listRelatives(top_node, parent=True)
                    if not parent:
                        break
                    top_node = parent[0]
                if top_node not in potential_rigs:
                    potential_rigs.append(top_node)
    
    # Look for rig control sets
    for set_node in cmds.ls(type='objectSet', long=True):
        if any(pattern in set_node.lower() for pattern in ['controls', 'anim', 'rig']):
            members = cmds.sets(set_node, q=True)
            if members:
                # Get the top transform for the first member
                top_node = members[0]
                while True:
                    parent = cmds.listRelatives(top_node, parent=True)
                    if not parent:
                        break
                    top_node = parent[0]
                if top_node not in potential_rigs:
                    potential_rigs.append(top_node)
    
    return potential_rigs

def ensure_rig_selected():
    """
    Ensures a rig is selected. If nothing is selected, attempts to find and select
    the first available rig in the scene.
    
    Returns:
        bool: True if a rig is selected (either previously or newly), False if no rig could be found
    """
    # Check current selection
    if cmds.ls(sl=True):
        return True
    
    # Try to find rigs
    rigs = get_scene_rigs()
    if rigs:
        # Select the first available rig
        cmds.select(rigs[0])
        print(f"Auto-selected rig: {rigs[0]}")
        return True
    
    return False

def get_rig_joints(rig_node):
    """
    Get all joints belonging to a rig.
    
    Args:
        rig_node (str): The top node of the rig
        
    Returns:
        list: All joints in the rig hierarchy
    """
    return cmds.listRelatives(rig_node, ad=True, type='joint') or []

def get_rig_controls(rig_node):
    """
    Get all control curves of a rig.
    
    Args:
        rig_node (str): The top node of the rig
        
    Returns:
        list: All nurbs curves that appear to be rig controls
    """
    curves = cmds.listRelatives(rig_node, ad=True, type='nurbsCurve') or []
    control_curves = []
    
    for curve in curves:
        # Get the transform node of the curve
        parent = cmds.listRelatives(curve, parent=True)[0]
        if any(pattern in parent.lower() for pattern in ['ctrl', 'control', 'con']):
            control_curves.append(parent)
    
    return control_curves