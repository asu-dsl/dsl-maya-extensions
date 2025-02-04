import maya.cmds as cmds

def get_scene_rigs():
    """
    Detect potential character rigs in the scene by looking for characteristic rig structures.
    Returns a list of top-level rig group nodes.
    """
    potential_rigs = []
    
    # Look for typical rig indicators
    all_joints = cmds.ls(type='joint', long=True)
    all_sets = cmds.ls(type='objectSet', long=True)
    
    if all_joints:
        # Get root joints (joints with no joint parents)
        root_joints = []
        for joint in all_joints:
            parent = cmds.listRelatives(joint, parent=True, type='joint')
            if not parent:
                # Found a root joint, get its top-level transform
                top_node = joint
                while True:
                    parent = cmds.listRelatives(top_node, parent=True)
                    if not parent:
                        break
                    top_node = parent[0]
                if top_node not in potential_rigs:
                    potential_rigs.append(top_node)
    
    # Look for control sets (common in character rigs)
    for set_node in all_sets:
        if any(pattern in set_node.lower() for pattern in ['controls', 'anim', 'rig']):
            # Get the top transform for this set
            members = cmds.sets(set_node, q=True)
            if members:
                # Get the top-level transform for the first member
                top_node = members[0]
                while True:
                    parent = cmds.listRelatives(top_node, parent=True)
                    if not parent:
                        break
                    top_node = parent[0]
                if top_node not in potential_rigs:
                    potential_rigs.append(top_node)
    
    return potential_rigs

def try_auto_select_rig():
    """
    Attempts to automatically select a rig if nothing is currently selected.
    
    Returns:
        bool: True if selection was successful (either already selected or auto-selected),
              False if no rig could be found/selected
    """
    # Check if anything is already selected
    if cmds.ls(sl=True):
        return True
        
    # Try to find rigs in the scene
    rigs = get_scene_rigs()
    
    if rigs:
        # Select the first available rig
        cmds.select(rigs[0])
        print(f"Auto-selected rig: {rigs[0]}")
        return True
    
    return False