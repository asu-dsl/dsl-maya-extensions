import json
import os

class ConfigManager:
    def __init__(self):
        # Get the directory where this file is located
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.config_dir, 'user_settings.json')
        self.default_settings = {
            'export_prefix': 'asset_',
            'last_export_path': '',  # Empty string as default
        }
        self.current_settings = {}
        self.load_settings()

    def load_settings(self):
        """Load settings from config file or create with defaults if it doesn't exist."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.current_settings = json.load(f)
                    
                # Validate the last_export_path if it exists
                if 'last_export_path' in self.current_settings:
                    path = self.current_settings['last_export_path']
                    if not os.path.exists(path):
                        print(f"Warning: Last export path '{path}' not found. Resetting to default.")
                        self.current_settings['last_export_path'] = ''
            else:
                self.current_settings = self.default_settings.copy()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_settings = self.default_settings.copy()

    def save_settings(self):
        """Save current settings to config file."""
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            with open(self.config_file, 'w') as f:
                json.dump(self.current_settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_setting(self, key, default=None):
        """
        Get a setting value by key.
        For paths, validates that they exist before returning.
        """
        value = self.current_settings.get(key, default)
        
        # Special handling for path settings
        if key == 'last_export_path' and value:
            if not os.path.exists(value):
                print(f"Warning: Path '{value}' not found. Using default.")
                return ''
        return value

    def set_setting(self, key, value):
        """Set a setting value and save to file."""
        # For paths, validate before saving
        if key == 'last_export_path':
            if value and not os.path.exists(value):
                print(f"Warning: Path '{value}' does not exist. Setting will not be saved.")
                return
        
        self.current_settings[key] = value
        self.save_settings()

    def get_default_export_name(self):
        """Generate default export name using prefix."""
        prefix = self.get_setting('export_prefix', 'asset_')
        return f"{prefix}export"