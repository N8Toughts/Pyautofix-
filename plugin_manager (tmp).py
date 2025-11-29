"""
RAGE Plugin Manager - Handles plugin loading and management
"""

import importlib.util
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging


class PluginManager:
    """Manages RAGE analyzer plugins"""
   
    def __init__(self, plugins_dir: str = "rage_plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins = {}
        self.available_formats = {}
       
        self._discover_plugins()
   
    def _discover_plugins(self):
        """Discover and load available plugins"""
        if not self.plugins_dir.exists():
            logging.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
       
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name == "__init__.py" or plugin_file.name == "plugin_manager.py":
                continue
               
            try:
                self._load_plugin(plugin_file)
            except Exception as e:
                logging.error(f"Failed to load plugin {plugin_file}: {e}")
   
    def _load_plugin(self, plugin_file: Path):
        """Load individual plugin"""
        plugin_name = plugin_file.stem
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if spec is None:
            return
           
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module
        spec.loader.exec_module(module)
       
        # Check for plugin class
        if hasattr(module, 'RAGEPlugin'):
            plugin_instance = module.RAGEPlugin()
            self.plugins[plugin_name] = plugin_instance
           
            # Register formats
            for format_name in plugin_instance.supported_formats:
                self.available_formats[format_name] = plugin_name
           
            logging.info(f"Loaded plugin: {plugin_name} (supports {plugin_instance.supported_formats})")
   
    def get_plugin_for_format(self, format_name: str):
        """Get plugin that supports the specified format"""
        plugin_name = self.available_formats.get(format_name)
        return self.plugins.get(plugin_name) if plugin_name else None
   
    def analyze_file(self, file_path: str, format_hint: str = None) -> Dict[str, Any]:
        """Analyze file using appropriate plugin"""
        # This would be implemented to try different plugins
        # based on file signature and format hints
        return {}


class RAGEPlugin:
    """Base class for RAGE analyzer plugins"""
   
    def __init__(self):
        self.supported_formats = []
        self.plugin_name = self.__class__.__name__
   
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """Analyze file - to be implemented by specific plugins"""
        raise NotImplementedError("Plugin must implement analyze method")
   
    def get_format_info(self) -> Dict[str, Any]:
        """Get information about supported formats"""
        return {
            'plugin_name': self.plugin_name,
            'supported_formats': self.supported_formats,
            'capabilities': []  # To be overridden
        }