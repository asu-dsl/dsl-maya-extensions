# playblast/config/settings.py
import json
import os

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.config_dir, 'playblast_settings.json')
        self.default_settings = {
            'last_playblast_path': '',
            'default_width': 1920,
            'default_height': 1080,
            'default_quality': 100,
        }
        self.current_settings = {}
        self.load_settings()
        
    def load_settings(self):
        """Load settings from config file or create with defaults if it doesn't exist."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.current_settings = json.load(f)
                    
                # Validate paths
                if 'last_playblast_path' in self.current_settings:
                    path = self.current_settings['last_playblast_path']
                    if not os.path.exists(path):
                        print(f"Warning: Last playblast path '{path}' not found. Resetting to default.")
                        self.current_settings['last_playblast_path'] = ''
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
        """Get a setting value by key."""
        return self.current_settings.get(key, default)
        
    def set_setting(self, key, value):
        """Set a setting value and save to file."""
        self.current_settings[key] = value
        self.save_settings()