"""
Enhanced Plugin Manager for RAGE Analyzer
Manages all plugins and provides unified interface
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger("RAGEAnalyzer.PluginManager")

class EnhancedPluginManager:
    """Enhanced plugin manager with hot-reloading and dependency handling"""
   
    def __init__(self):
        self.plugins = {}
        self.plugin_dirs = [
            Path(__file__).parent,
            Path.home() / ".analyzer" / "plugins"
        ]
        self._load_plugins()
   
    def _load_plugins(self):
        """Load all available plugins with dependency resolution"""
        # Load base plugins first
        base_plugins = []
        other_plugins = []
       
        for plugin_dir in self.plugin_dirs:
            if plugin_dir.exists():
                for plugin_file in plugin_dir.glob("*.py"):
                    if plugin_file.name != "__init__.py" and plugin_file.name != "plugin_manager.py":
                        plugin_info = self._analyze_plugin_dependencies(plugin_file)
                        if plugin_info.get('is_base', False):
                            base_plugins.append(plugin_file)
                        else:
                            other_plugins.append(plugin_file)
       
        # Load base plugins first, then others
        for plugin_file in base_plugins + other_plugins:
            self._load_plugin(plugin_file)
   
    def _analyze_plugin_dependencies(self, plugin_path: Path) -> Dict[str, Any]:
        """Analyze plugin dependencies without loading it"""
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
               
            # Simple dependency analysis
            is_base = 'base_format' in content.lower() or 'base_formats' in plugin_path.name.lower()
           
            return {
                'is_base': is_base,
                'path': plugin_path
            }
        except Exception as e:
            logger.error(f"Failed to analyze plugin {plugin_path}: {e}")
            return {'is_base': False, 'path': plugin_path}
   
    def _load_plugin(self, plugin_path: Path):
        """Load a single plugin with error handling"""
        try:
            spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
            module = importlib.util.module_from_spec(spec)
           
            # Add to sys.modules to allow relative imports
            sys.modules[plugin_path.stem] = module
            spec.loader.exec_module(module)
           
            if hasattr(module, 'register_plugin'):
                plugin_info = module.register_plugin()
                self.plugins[plugin_info['name']] = {
                    'module': module,
                    'info': plugin_info,
                    'path': plugin_path
                }
                logger.info(f"Loaded plugin: {plugin_info['name']} v{plugin_info['version']}")
            else:
                logger.warning(f"Plugin {plugin_path} has no register_plugin function")
               
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
   
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        if plugin_name in self.plugins:
            plugin_data = self.plugins[plugin_name]
            try:
                # Reload the module
                importlib.reload(plugin_data['module'])
                logger.info(f"Reloaded plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to reload plugin {plugin_name}: {e}")
        return False
   
    def get_plugin(self, plugin_name: str):
        """Get a specific plugin module"""
        return self.plugins.get(plugin_name, {}).get('module')
   
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [
            {
                'name': name,
                'version': data['info'].get('version', 'Unknown'),
                'author': data['info'].get('author', 'Unknown'),
                'description': data['info'].get('description', ''),
                'games': data['info'].get('games', []),
                'formats': data['info'].get('formats', [])
            }
            for name, data in self.plugins.items()
        ]
   
    def get_format_detector(self) -> tuple:
        """Get combined format database from all plugins"""
        format_db = {}
        magic_numbers = {}
       
        for plugin_name, plugin_data in self.plugins.items():
            if hasattr(plugin_data['module'], 'get_format_database'):
                plugin_db = plugin_data['module'].get_format_database()
                format_db.update(plugin_db)
           
            if hasattr(plugin_data['module'], 'get_magic_numbers'):
                plugin_magic = plugin_data['module'].get_magic_numbers()
                magic_numbers.update(plugin_magic)
       
        return format_db, magic_numbers
   
    def get_file_processor(self, format_type: str, game: str = None):
        """Get appropriate file processor for format and game"""
        # Try game-specific plugins first
        if game:
            for plugin_name, plugin_data in self.plugins.items():
                if (hasattr(plugin_data['module'], 'can_handle') and
                    plugin_data['module'].can_handle(format_type, game)):
                    return plugin_data['module']
       
        # Fall back to format-specific plugins
        for plugin_name, plugin_data in self.plugins.items():
            if (hasattr(plugin_data['module'], 'can_handle') and
                plugin_data['module'].can_handle(format_type)):
                return plugin_data['module']
       
        return None
   
    def execute_operation(self, operation: str, *args, **kwargs) -> Any:
        """Execute an operation across all compatible plugins"""
        results = []
       
        for plugin_name, plugin_data in self.plugins.items():
            if hasattr(plugin_data['module'], operation):
                try:
                    func = getattr(plugin_data['module'], operation)
                    result = func(*args, **kwargs)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} failed operation {operation}: {e}")
       
        return results

# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> EnhancedPluginManager:
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = EnhancedPluginManager()
    return _plugin_manager