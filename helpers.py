import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileHelper:
    """File system utilities for PyAutoFix"""
   
    @staticmethod
    def safe_read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """Safely read file with error handling"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Cannot read file {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Cannot read file {file_path}: {e}")
   
    @staticmethod
    def safe_write_file(file_path: str, content: str, backup: bool = True) -> bool:
        """Safely write file with backup option"""
        try:
            if backup and Path(file_path).exists():
                backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                Path(file_path).rename(backup_path)
                logger.info(f"Backup created: {backup_path}")
           
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False
   
    @staticmethod
    def find_python_files(directory: str, recursive: bool = True) -> List[Path]:
        """Find all Python files in directory"""
        path = Path(directory)
        pattern = "**/*.py" if recursive else "*.py"
        return list(path.glob(pattern))
   
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate MD5 hash of file content"""
        content = FileHelper.safe_read_file(file_path)
        return hashlib.md5(content.encode()).hexdigest()
   
    @staticmethod
    def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> bool:
        """Create directory structure"""
        try:
            base = Path(base_path)
            base.mkdir(parents=True, exist_ok=True)
           
            for name, content in structure.items():
                item_path = base / name
                if isinstance(content, dict):
                    # It's a directory
                    item_path.mkdir(exist_ok=True)
                    FileHelper.create_directory_structure(str(item_path), content)
                else:
                    # It's a file
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory structure: {e}")
            return False

class ConfigHelper:
    """Configuration management utilities"""
   
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
            return {}
   
    @staticmethod
    def save_config(config_path: str, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save config {config_path}: {e}")
            return False
   
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'core': {
                'learn_from_corrections': True,
                'auto_suggest_rules': True,
                'learning_confidence_threshold': 0.7,
                'backup_files': True
            },
            'gui': {
                'theme': 'default',
                'window_width': 1200,
                'window_height': 800,
                'show_line_numbers': True
            },
            'integrations': {
                'enable_ai': True,
                'enable_rage_analyzer': True,
                'enable_blender_analyzer': True
            }
        }
   
    @staticmethod
    def merge_configs(user_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with default config"""
        merged = default_config.copy()
       
        def deep_merge(source, destination):
            for key, value in source.items():
                if isinstance(value, dict) and key in destination and isinstance(destination[key], dict):
                    deep_merge(value, destination[key])
                else:
                    destination[key] = value
       
        deep_merge(user_config, merged)
        return merged