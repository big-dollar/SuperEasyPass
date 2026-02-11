import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        # Default path: User Home/.SuperEasyPass/config.json
        self.config_dir = os.path.join(os.path.expanduser("~"), ".SuperEasyPass")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
    def load_config(self):
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
            
    def save_config(self, config_data):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
            
    def get_db_path(self):
        data = self.load_config()
        return data.get("db_path", None)
        
    def set_db_path(self, path):
        data = self.load_config()
        data["db_path"] = path
        self.save_config(data)
