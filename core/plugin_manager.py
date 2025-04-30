import os
import importlib.util
import sys
import maya.cmds as cmds
import traceback

class ToolRegistry:
    """Registry for all tool plugins that can be added to the shelf."""
    
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, tool_id, tool_config):
        """
        Register a new tool to the shelf.
        
        Args:
            tool_id (str): Unique identifier for the tool
            tool_config (dict): Configuration for the tool containing:
                - label: Button label
                - command: Command to run
                - icon: Path to icon (relative to tool's directory)
                - annotation: Tooltip text
        """
        if not all(key in tool_config for key in ['label', 'command']):
            print(f"Warning: Tool {tool_id} missing required configuration. Skipping.")
            return
            
        self.tools[tool_id] = tool_config
        print(f"Registered tool: {tool_id}")

# Global registry instance
registry = ToolRegistry()

def discover_tools():
    """Scan for and load all tool plugins."""
    try:
        # Get the root directory using the module path instead of __file__
        # First find this module's location using Python's module system
        core_module = sys.modules.get('core')
        if not core_module:
            print("WARNING: core module not in sys.modules, using fallback method")
            # Try to find it using environment variables or other means
            maya_module_paths = os.environ.get('MAYA_MODULE_PATH', '').split(';')
            root_dir = None
            for path in maya_module_paths:
                mod_path = os.path.join(path, 'asu_dsl_tools.mod')
                if os.path.exists(mod_path):
                    with open(mod_path, 'r') as f:
                        for line in f:
                            if line.startswith('+ ASU_DSL_TOOLS'):
                                parts = line.strip().split()
                                if len(parts) >= 3:
                                    root_dir = parts[2]
                                    break
                    if root_dir:
                        break
            
            if not root_dir:
                # Last resort: try to guess based on the current working directory
                root_dir = os.getcwd()
                print(f"WARNING: Using current working directory as root: {root_dir}")
        else:
            # Get the path from the module
            core_path = os.path.dirname(os.path.abspath(core_module.__file__))
            root_dir = os.path.dirname(core_path)
        
        print(f"Root directory: {root_dir}")
        
        # List of directories to skip
        skip_dirs = {'__pycache__', 'backup', 'logs', '.git', '.vscode'}
        
        print("Discovering tools...")
        
        # Scan for tool directories (directories with a tool_config.py file)
        for item in os.listdir(root_dir):
            if item in skip_dirs:
                continue
                
            tool_dir = os.path.join(root_dir, item)
            config_file = os.path.join(tool_dir, 'tool_config.py')
            
            if os.path.isdir(tool_dir) and os.path.exists(config_file):
                try:
                    # Load the tool's config
                    spec = importlib.util.spec_from_file_location("tool_config", config_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'TOOL_CONFIG'):
                        # Copy config from tool
                        config = module.TOOL_CONFIG.copy()

                        # Patch MEL path in command if 'mel/' is used
                        if 'command' in config and 'mel/' in config['command']:
                            config['command'] = config['command'].replace(
                                'mel/',
                                os.path.join(tool_dir, 'mel').replace('\\', '/') + '/'
                            )

                        # Patch icon path
                        if 'icon' in config:
                            config['icon'] = os.path.join(tool_dir, config['icon'])

                        # Add tool's mel directory to MAYA_SCRIPT_PATH using Python (not MEL!)
                        mel_dir = os.path.join(tool_dir, 'mel').replace("\\", "/")
                        if os.path.exists(mel_dir):
                            current_path = os.environ.get("MAYA_SCRIPT_PATH", "")
                            if mel_dir not in current_path:
                                os.environ["MAYA_SCRIPT_PATH"] = current_path + ";" + mel_dir

                        # Register the tool
                        registry.register_tool(item, config)
                    else:
                        print(f"Warning: {item} missing TOOL_CONFIG in tool_config.py")
                        
                except Exception as e:
                    print(f"Failed to load tool from {tool_dir}: {e}")
                    traceback.print_exc()
    except Exception as e:
        print(f"Error in discover_tools: {e}")
        traceback.print_exc()

def create_shelf():
    """Creates the shelf with all registered tools."""
    try:
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
        
        # Add buttons for all registered tools
        for tool_id, config in registry.tools.items():
            try:
                # Resolve icon path, use default if not found
                icon_path = config.get('icon', '')
                if not icon_path or not os.path.exists(icon_path):
                    icon_path = "commandButton.png"
                
                # Create the shelf button
                cmds.shelfButton(
                    parent=shelf,
                    label=config.get('label', tool_id),
                    annotation=config.get('annotation', ''),
                    image=icon_path,
                    command=config.get('command', ''),
                    sourceType="python",
                    style='iconAndTextCentered',
                    imageOverlayLabel=config.get('overlayLabel', ''),
                    width=32,
                    height=32
                )
            except Exception as e:
                print(f"Failed to create shelf button for {tool_id}: {e}")
                traceback.print_exc()
        
        print(f"Created shelf with {len(registry.tools)} tools")
    except Exception as e:
        print(f"Error in create_shelf: {e}")
        traceback.print_exc()