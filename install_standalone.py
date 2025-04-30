import os
from pathlib import Path

def search_directory_for_maya(start: Path) -> dict:
    """Recursively search a directory for Maya installations."""
    maya_versions = {}
    try:
        # If this is the user's maya docs folder, look for year subfolders
        if start.name.lower() == "maya":
            for sub in start.iterdir():
                if sub.is_dir() and sub.name.isdigit():
                    maya_versions[sub.name] = start

        # Walk looking for maya.exe or mayapy.exe
        for root, dirs, files in os.walk(start):
            if "maya.exe" in files or "mayapy.exe" in files:
                parts = Path(root).parts
                for part in parts:
                    if part.lower().startswith("maya20"):
                        ver = part.lower().replace("maya", "")
                        if ver.isdigit():
                            maya_versions[ver] = root
                            break
    except Exception as e:
        print(f"[Warning] Error scanning {start}: {e}")
    return maya_versions

def find_maya_installations() -> dict:
    """Return a dict of installed Maya versions: {version: path}."""
    candidates = [
        Path.home() / "Documents" / "maya",
        Path("C:/Program Files/Autodesk"),
        Path("C:/Autodesk"),
        Path.home(),
    ]
    found = {}
    print("Searching for Maya installations…")
    for i, p in enumerate(candidates):
        if p.exists():
            print(f"  Scanning {p} …")
            vs = search_directory_for_maya(p)
            if vs:
                found.update(vs)
                if i < len(candidates) - 1:
                    print("  Found Maya installs; skipping deeper search.")
                    break
    return found

import os
from pathlib import Path
import shutil

def install_to_maya(maya_version):
    """Install to a specific Maya version with direct path checks."""
    print(f"\n→ Installing into Maya {maya_version}…")

    # Paths in the user Documents tree
    scripts_dir = Path.home() / "Documents" / "maya" / maya_version / "scripts"
    modules_dir = Path.home() / "Documents" / "maya" / maya_version / "modules"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    # Get current script directory (absolute path)
    tool_root = os.path.dirname(os.path.abspath(__file__))
    
    # Check if 'core' directory exists, create it if not
    core_dir = os.path.join(tool_root, "core")
    if not os.path.exists(core_dir):
        print(f"  • Creating missing 'core' directory at: {core_dir}")
        os.makedirs(core_dir, exist_ok=True)
    
    # Verify plugin_manager.py exists in core directory
    plugin_manager_path = os.path.join(core_dir, "plugin_manager.py")
    if not os.path.exists(plugin_manager_path):
        # Try to locate it elsewhere
        for root, dirs, files in os.walk(tool_root):
            if "plugin_manager.py" in files:
                source_path = os.path.join(root, "plugin_manager.py")
                print(f"  • Found plugin_manager.py at: {source_path}")
                print(f"  • Copying to core directory")
                shutil.copy2(source_path, plugin_manager_path)
                break
        else:
            # Create a simple version if not found
            print(f"  • Creating basic plugin_manager.py in core directory")
            with open(plugin_manager_path, "w", encoding="utf-8") as f:
                f.write('''import os
import maya.cmds as cmds

class ToolRegistry:
    """Registry for all tool plugins that can be added to the shelf."""
    
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, tool_id, tool_config):
        if not all(key in tool_config for key in ['label', 'command']):
            print(f"Warning: Tool {tool_id} missing required configuration. Skipping.")
            return
            
        self.tools[tool_id] = tool_config
        print(f"Registered tool: {tool_id}")

# Global registry instance
registry = ToolRegistry()

def discover_tools():
    """Scan for and load all tool plugins."""
    print("Discover tools called - basic implementation")
    
def create_shelf():
    """Creates the shelf with all registered tools."""
    shelf_name = "ASU_DSL_Shelf"
    
    # Delete existing shelf
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name)
    
    # Get all shelves layouts
    all_shelves = cmds.layout('ShelfLayout', query=True, childArray=True)
    if not all_shelves:
        cmds.warning("Could not find main shelf layout")
        return
        
    # Create new shelf
    shelf = cmds.shelfLayout(shelf_name, parent='ShelfLayout')
    
    print(f"Created shelf with {len(registry.tools)} tools")
''')
    
    # Create a proper __init__.py in the core directory
    init_file = os.path.join(core_dir, "__init__.py")
    with open(init_file, "w", encoding="utf-8") as f:
        f.write('"""ASU DSL Tools core package."""\n')
    
    # Write the module file with direct path
    mod_file = os.path.join(modules_dir, "asu_dsl_tools.mod")
    with open(mod_file, "w", encoding="utf-8") as f:
        tool_root_path = tool_root.replace("\\", "/")
        f.write(f"+ ASU_DSL_TOOLS 1.0 {tool_root_path}\n")
        f.write("python: .\n")
        f.write("scripts: .\n")
    
    # Create a robust userSetup.py
    usersetup = os.path.join(scripts_dir, "userSetup.py")
    tool_root_path = tool_root.replace("\\", "/")
    
    setup_code = f'''import os
import sys
import maya.cmds as cmds
import traceback

def load_asu_dsl_tools(*args):
    """Deferred loader for ASU DSL Tools."""
    try:
        # Direct path approach - explicitly add the tool root to sys.path
        tool_path = "{tool_root_path}"
        if tool_path not in sys.path:
            sys.path.insert(0, tool_path)
            print(f"ASU_DSL_TOOLS: Added {{tool_path}} to Python path")
        
        # Also verify the core directory is directly in sys.path
        core_path = os.path.join("{tool_root_path}", "core")
        parent_path = os.path.dirname("{tool_root_path}")
        
        # Print some diagnostic info
        print(f"Tool path: {{tool_path}}")
        print(f"Core path: {{core_path}}")
        
        # Check if core directory exists
        if not os.path.exists(core_path):
            print(f"ERROR: Core directory doesn't exist at {{core_path}}")
            return
            
        # Check for plugin_manager.py
        plugin_manager_file = os.path.join(core_path, "plugin_manager.py")
        if not os.path.exists(plugin_manager_file):
            print(f"ERROR: plugin_manager.py doesn't exist at {{plugin_manager_file}}")
            return
            
        # Print current sys.path
        print("Current sys.path:")
        for i, path in enumerate(sys.path):
            print(f"  {{i}}: {{path}}")
            
        # Try to import the plugin manager
        print("Importing core.plugin_manager...")
        import core.plugin_manager as plugin_manager
        
        print("ASU_DSL_TOOLS: Successfully imported plugin_manager")
        
        # Call the plugin manager functions
        plugin_manager.discover_tools()
        plugin_manager.create_shelf()
        
        print("ASU_DSL_TOOLS: Successfully loaded!")
    except Exception as e:
        cmds.warning(f"Failed to load ASU DSL tools: {{e}}")
        traceback.print_exc()

# Register the function to be called after Maya UI is initialized
cmds.evalDeferred(load_asu_dsl_tools, lowestPriority=True)
print("ASU_DSL_TOOLS: Registered for deferred loading")
'''
    
    with open(usersetup, "w", encoding="utf-8") as f:
        f.write(setup_code)
    
    print(f"  • Wrote userSetup.py: {usersetup}")
    print(f"  • Wrote module file: {mod_file}")
    print(f"  • Created/verified core/__init__.py: {init_file}")
    print(f"  • Created/verified core/plugin_manager.py: {plugin_manager_path}")
    
    print(f"\n✅ Installation successful for Maya {maya_version}")
    print(f"   Tool root: {tool_root}")

def main():
    print("=== ASU DSL Maya Tool Directory Structure Fixer ===")
    
    # Prompt for Maya version
    maya_version = input("Enter Maya version (e.g., 2024): ").strip()
    
    if not maya_version:
        print("No version specified. Using 2024 as default.")
        maya_version = "2024"
        
    install_to_maya(maya_version)
    
    print("\nInstallation complete! Press Enter to exit.")
    input()

if __name__ == "__main__":
    main()