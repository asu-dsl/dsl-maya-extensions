import os
import sys
import winreg
from pathlib import Path

def search_directory_for_maya(start_path):
    """Recursively search a directory for Maya installations."""
    maya_versions = {}
    
    try:
        # First check if this is a Maya documents directory
        if os.path.basename(start_path) == "maya":
            # Check immediate subdirectories for year folders
            for item in os.listdir(start_path):
                if item.isdigit():  # Year folders are typically just numbers (2024, 2025, etc.)
                    maya_versions[item] = start_path
                    print(f"Found Maya {item} user directory in: {start_path}")
        
        # Then look for Maya binary installations
        for root, dirs, files in os.walk(start_path):
            if 'maya.exe' in files or 'mayapy.exe' in files:
                path_parts = root.lower().split(os.sep)
                for part in path_parts:
                    if part.startswith('maya20'):  # Match Maya year versions
                        version = part.replace('maya', '')
                        if version.isdigit():
                            maya_versions[version] = root
                            print(f"Found Maya {version} installation in: {root}")
                            break
    except Exception as e:
        print(f"Error scanning {start_path}: {e}")
    
    return maya_versions

def find_maya_installations():
    """Find all Maya installations on the system."""
    maya_versions = {}
    
    # Define search paths
    search_paths = [
        os.path.expanduser("~/Documents/maya"),     # User maya directory
        "C:/Program Files/Autodesk",               # Program Files
        "C:/Autodesk",                            # Alternative installation
        os.path.expanduser("~"),                  # User's home directory
    ]
    
    print("Searching for Maya installations...")
    for path in search_paths:
        if os.path.exists(path):
            print(f"Scanning {path}...")
            found_versions = search_directory_for_maya(path)
            maya_versions.update(found_versions)
    
    return maya_versions

def install_to_maya(maya_path, version):
    """Install the tool for a specific Maya version."""
    scripts_path = os.path.join(os.path.expanduser("~/Documents/maya"), version, "scripts")
    
    # Create scripts directory if it doesn't exist
    os.makedirs(scripts_path, exist_ok=True)
    
    # Get the directory where this script is located
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create scripts directory if it doesn't exist
    os.makedirs(scripts_path, exist_ok=True)
    
    # Also create a modules directory if it doesn't exist
    modules_path = os.path.join(os.path.dirname(scripts_path), "modules")
    os.makedirs(modules_path, exist_ok=True)

    # Create a .mod file for Maya to recognize our tool
    mod_file_path = os.path.join(modules_path, "asu_dsl_tools.mod")
    mod_content = f"""+ ASU_DSL_TOOLS 1.0 {tool_dir}
scripts: {tool_dir}"""
    
    with open(mod_file_path, 'w') as f:
        f.write(mod_content)

    # Create/update userSetup.py
    usersetup_path = os.path.join(scripts_path, "userSetup.py")
    setup_code = '''import maya.cmds as cmds
import maya.mel as mel
import maya.utils
import importlib

def load_asu_dsl_shelf():
    """Load ASU DSL shelf"""
    try:
        import ui.shelf
        importlib.reload(ui.shelf)  # Proper way to reload in Python 3
        ui.shelf.create_shelf()
    except Exception as e:
        cmds.warning(f"Failed to load ASU DSL shelf: {str(e)}")
        import traceback
        traceback.print_exc()

# Use executeDeferred to ensure UI exists before creating shelf
maya.utils.executeDeferred(load_asu_dsl_shelf)
'''
    
    # Write or update userSetup.py
    with open(usersetup_path, 'w') as f:
        f.write(setup_code)
    
    print(f"Successfully installed for Maya {version}")
    return True

def main():
    print("ASU DSL Maya Tool Installer")
    print("-" * 50)
    
    # Find Maya installations
    maya_versions = find_maya_installations()
    
    if not maya_versions:
        print("\nNo Maya installations found automatically!")
        print("Options:")
        print("1. Enter path to Maya directory manually")
        print("2. Exit")
        choice = input("\nSelect option (1-2) or press Enter to exit: ").strip()
        
        if not choice or choice == "2":
            return
            
        if choice == "1":
            while True:
                path = input("\nEnter path to Maya directory (or press Enter to cancel): ").strip()
                if not path:
                    return
                    
                if os.path.exists(path):
                    found_versions = search_directory_for_maya(path)
                    if found_versions:
                        maya_versions.update(found_versions)
                        print(f"\nFound Maya installation(s) in specified path!")
                        break
                    else:
                        print("\nNo Maya installation found in specified path.")
                        continue
                else:
                    print("\nSpecified path does not exist. Please try again.")
    
    # Sort versions
    versions = sorted(maya_versions.keys())
    
    if len(versions) == 1:
        version = versions[0]
        print(f"Found Maya {version}")
        print(f"Installing...")
        install_to_maya(maya_versions[version], version)
    else:
        print("\nFound multiple Maya versions:")
        for i, version in enumerate(versions, 1):
            print(f"{i}. Maya {version}")
        print(f"{len(versions) + 1}. All versions")
        print("0. Cancel")
        
        while True:
            choice = input("\nSelect Maya version to install for (enter number): ")
            if choice == "0":
                return
            try:
                choice = int(choice)
                if choice == len(versions) + 1:
                    # Install for all versions
                    for version in versions:
                        print(f"\nInstalling for Maya {version}...")
                        install_to_maya(maya_versions[version], version)
                    break
                elif 1 <= choice <= len(versions):
                    version = versions[choice - 1]
                    print(f"\nInstalling for Maya {version}...")
                    install_to_maya(maya_versions[version], version)
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    print("\nInstallation complete!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()