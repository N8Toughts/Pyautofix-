#!/usr/bin/env python3
"""
RAGE Evolutionary Analyzer - Enhanced Edition
Complete RPF6 Archive Reader/Writer With Advanced Format Detection, GUI Viewer, and Multi-Game Support
Now with Plugin Architecture and True RDR1 PC Support
"""

# where to add these?
#def get_import_export_advice(self, file_path: str, target_engine: str = None) -> Dict[str, Any]:
#    """Get import/export advice with reader testing"""
#    try:
#        from plugins.universal_import_export import UniversalImportExport
#        import_export = UniversalImportExport()
#        return import_export.get_import_export_advice(file_path, target_engine)
#   except ImportError:
#       return {'error': 'Import/Export plugin not available'}
#
#def aggressive_reader_testing(self, file_path: str) -> List[Dict[str, Any]]:
#   """Perform aggressive reader compatibility testing"""
#    try:
#        from plugins.universal_import_export import UniversalImportExport
#        import_export = UniversalImportExport()
#       
#        # Get file analysis first
#       analysis = self.analyze_file_with_openiv(file_path)  # Uses all available analysis
#        return import_export.aggressive_reader_testing(file_path, analysis)
#    except ImportError:
#        return [{'error': 'Import/Export plugin not available'}]
#
import os
import sys
import json
import struct
import zlib
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
from datetime import datetime
import importlib.util
import glob
import hashlib
import binascii

# Third-party imports for enhanced functionality
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rage_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RAGEAnalyzer")

class PluginManager:
    """Manages RAGE analyzer plugins for different game formats"""
   
    def __init__(self):
        self.plugins = {}
        self.plugin_dirs = [
            Path(__file__).parent / "rage_plugins",
            Path.home() / ".analyzer" / "plugins"
        ]
        self._load_plugins()
   
    def _load_plugins(self):
        """Load all available plugins"""
        for plugin_dir in self.plugin_dirs:
            if plugin_dir.exists():
                for plugin_file in plugin_dir.glob("*.py"):
                    if plugin_file.name != "__init__.py":
                        self._load_plugin(plugin_file)
   
    def _load_plugin(self, plugin_path: Path):
        """Load a single plugin"""
        try:
            spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
           
            if hasattr(module, 'register_plugin'):
                plugin_info = module.register_plugin()
                self.plugins[plugin_info['name']] = {
                    'module': module,
                    'info': plugin_info
                }
                logger.info(f"Loaded plugin: {plugin_info['name']}")
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
   
    def get_format_detector(self):
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
        for plugin_name, plugin_data in self.plugins.items():
            if hasattr(plugin_data['module'], 'can_handle'):
                if plugin_data['module'].can_handle(format_type, game):
                    return plugin_data['module']
        return None

class AdvancedFormatDetector:
    """Advanced file format detection with evolutionary pattern recognition"""
   
    def __init__(self, plugin_manager: PluginManager = None):
        self.plugin_manager = plugin_manager or PluginManager()
        self.format_database, self.known_magic_numbers = self.plugin_manager.get_format_detector()
        self.detection_history = []
        self.confidence_threshold = 0.7
   
    def detect_format(self, file_path: str, aggressive: bool = False) -> Dict[str, Any]:
        """Detect file format with optional aggressive analysis"""
        file_ext = Path(file_path).suffix.lower()
        file_size = os.path.getsize(file_path)
       
        # Basic detection
        basic_result = self._basic_detection(file_path, file_ext, file_size)
       
        if basic_result['confidence'] >= self.confidence_threshold:
            return basic_result
       
        # Aggressive analysis if requested or confidence is low
        if aggressive or basic_result['confidence'] < 0.5:
            aggressive_result = self._aggressive_analysis(file_path, file_size)
            if aggressive_result['confidence'] > basic_result['confidence']:
                return aggressive_result
       
        return basic_result
   
    def _basic_detection(self, file_path: str, file_ext: str, file_size: int) -> Dict[str, Any]:
        """Perform basic format detection"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(512)  # Read more bytes for better detection
           
            # Check magic numbers
            magic_result = self._check_magic_numbers(header)
            if magic_result:
                return magic_result
           
            # Check extension against database
            for format_id, format_info in self.format_database.items():
                if file_ext in format_info.get('extensions', []):
                    base_info = format_info.copy()
                    base_info['detection_method'] = 'extension'
                    base_info['file_size'] = file_size
                    base_info['confidence'] = format_info.get('confidence', 70) * 0.8  # Reduce confidence for extension-only
                    return base_info
           
            # Structural analysis
            structure_result = self._structural_analysis(file_path, header, file_size)
            return structure_result
           
        except Exception as e:
            return {
                'name': 'Unknown Format',
                'games': ['Unknown'],
                'confidence': 30,
                'detection_method': 'error',
                'error': str(e)
            }
   
    def _aggressive_analysis(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Perform aggressive format analysis trying multiple detection methods"""
        best_result = {'name': 'Unknown Format', 'confidence': 0}
       
        detection_methods = [
            self._try_rpf_structure,
            self._try_texture_format,
            self._try_model_format,
            self._try_script_format,
            self._try_archive_format
        ]
       
        for method in detection_methods:
            try:
                result = method(file_path, file_size)
                if result['confidence'] > best_result['confidence']:
                    best_result = result
                if result['confidence'] >= self.confidence_threshold:
                    break
            except Exception as e:
                logger.debug(f"Aggressive analysis method failed: {e}")
                continue
       
        best_result['detection_method'] = 'aggressive_analysis'
        return best_result
   
    def _try_rpf_structure(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Try to detect RPF archive structure"""
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic in [b'RPF6', b'RPF7']:
                    return {
                        'name': f'RAGE Package File ({magic.decode("ascii", errors="ignore")})',
                        'games': ['RDR1', 'RDR2', 'GTA5'],
                        'confidence': 95,
                        'structure': 'archive'
                    }
           
            # Check for RPF structure without magic
            f.seek(0)
            header = f.read(24)
            if len(header) >= 24:
                # Check for RPF-like structure
                entry_count = struct.unpack('<I', header[8:12])[0]
                if 0 < entry_count < 100000:  # Reasonable entry count
                    return {
                        'name': 'Possible RPF Archive',
                        'games': ['RAGE Engine'],
                        'confidence': 70,
                        'structure': 'archive'
                    }
        except:
            pass
       
        return {'name': 'Unknown', 'confidence': 0}
   
    def _try_texture_format(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Try to detect texture formats"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(128)
               
                # Check for DDS
                if header.startswith(b'DDS '):
                    return {
                        'name': 'DDS Texture',
                        'games': ['Multiple'],
                        'confidence': 95,
                        'structure': 'texture'
                    }
               
                # Check for PNG
                if header.startswith(b'\x89PNG'):
                    return {
                        'name': 'PNG Image',
                        'games': ['Multiple'],
                        'confidence': 99,
                        'structure': 'image'
                    }
               
                # Check for RAGE textures
                if len(header) > 16:
                    # Look for texture-like patterns
                    if struct.unpack('<I', header[0:4])[0] in [0x00, 0x08, 0x10]:  # Common texture flags
                        return {
                            'name': 'Possible RAGE Texture',
                            'games': ['RDR1', 'RDR2', 'GTA4', 'GTA5'],
                            'confidence': 65,
                            'structure': 'texture'
                        }
        except:
            pass
       
        return {'name': 'Unknown', 'confidence': 0}
   
    def _try_model_format(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Try to detect 3D model formats"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(64)
               
                # Check for common model patterns
                if len(header) >= 16:
                    # Look for vertex count or mesh data patterns
                    first_int = struct.unpack('<I', header[0:4])[0]
                    second_int = struct.unpack('<I', header[4:8])[0]
                   
                    # Common model structure patterns
                    if (0 < first_int < 100000 and 0 < second_int < 100000 and
                        first_int * second_int < file_size):
                        return {
                            'name': 'Possible 3D Model',
                            'games': ['RAGE Engine'],
                            'confidence': 60,
                            'structure': 'model'
                        }
        except:
            pass
       
        return {'name': 'Unknown', 'confidence': 0}
   
    def _try_script_format(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Try to detect script formats"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024)
                text_content = content.decode('utf-8', errors='ignore')
               
                if 'function' in text_content.lower() or 'procedure' in text_content.lower():
                    return {
                        'name': 'Script File',
                        'games': ['Multiple'],
                        'confidence': 80,
                        'structure': 'script'
                    }
               
                if '<?xml' in text_content or '<root>' in text_content:
                    return {
                        'name': 'XML Data',
                        'games': ['Multiple'],
                        'confidence': 90,
                        'structure': 'data'
                    }
        except:
            pass
       
        return {'name': 'Unknown', 'confidence': 0}
   
    def _try_archive_format(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Try to detect archive formats"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
               
                # Check for ZIP-like structure
                if header.startswith(b'PK'):
                    return {
                        'name': 'ZIP Archive',
                        'games': ['Multiple'],
                        'confidence': 95,
                        'structure': 'archive'
                    }
                # Check for RAGE resource
                if header[0:4] in [b'\x52\x53\x43', b'\x52\x53\x44']:  # RSC, RSD
                    return {
                        'name': 'RAGE Resource',
                        'games': ['RAGE Engine'],
                        'confidence': 85,
                        'structure': 'resource'
                    }
        except:
            pass
       
        return {'name': 'Unknown', 'confidence': 0}
   
    def _check_magic_numbers(self, header: bytes) -> Optional[Dict[str, Any]]:
        """Check header against known magic numbers"""
        for magic, format_id in self.known_magic_numbers.items():
            if header.startswith(magic):
                format_info = self.format_database.get(format_id, {})
               
                return {
                    'name': format_info.get('name', format_id.upper()),
                    'games': format_info.get('games', ['Multiple']),
                    'confidence': format_info.get('confidence', 85),
                    'detection_method': 'magic_number',
                    'structure': format_info.get('structure', 'unknown')
                }
        return None
   
    def _structural_analysis(self, file_path: str, header: bytes, file_size: int) -> Dict[str, Any]:
        """Analyze file structure patterns"""
        entropy = self._calculate_entropy(header)
       
        if entropy > 0.9 and file_size > 1000:
            return {
                'name': 'Compressed/Encrypted Data',
                'games': ['Unknown'],
                'confidence': 75,
                'detection_method': 'entropy_analysis',
                'structure': 'compressed'
            }
        elif entropy < 0.3:
            return {
                'name': 'Structured Data',
                'games': ['Unknown'],
                'confidence': 60,
                'detection_method': 'entropy_analysis',
                'structure': 'structured'
            }
        return {
            'name': 'Unknown Binary',
            'games': ['Unknown'],
            'confidence': 50,
            'detection_method': 'fallback',
            'structure': 'binary'
        }
   
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if len(data) == 0:
            return 0.0
       
        entropy = 0.0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += -p_x * (p_x.bit_length() - 1)  # log2 approximation
       
        return entropy / 8.0  # Normalize to 0-1

class FileViewerSystem:
    def __init__(self, plugin_manager: PluginManager = None):
        self.plugin_manager = plugin_manager or PluginManager()
        self.viewers = {}
        self._register_viewers()
   
    def _register_viewers(self):
        """Register all available file viewers"""
        # Text viewers
        self.viewers['text'] = self._view_text_file
        self.viewers['script'] = self._view_script_file
        self.viewers['xml'] = self._view_xml_file
        self.viewers['json'] = self._view_json_file
       
        # Binary viewers
        self.viewers['binary'] = self._view_binary_file
        self.viewers['hex'] = self._view_hex_file
       
        # Specialized viewers
        if HAS_PIL:
            self.viewers['image'] = self._view_image_file
            self.viewers['texture'] = self._view_texture_file
       
        self.viewers['archive'] = self._view_archive_file
   
    def view_file(self, file_path: str, format_info: Dict[str, Any], parent_widget) -> tk.Frame:
        """Create appropriate viewer for file"""
        structure = format_info.get('structure', 'binary')
        viewer_func = self.viewers.get(structure, self._view_binary_file)
       
        viewer_frame = tk.Frame(parent_widget)
        try:
            viewer_func(file_path, format_info, viewer_frame)
        except Exception as e:
            logger.error(f"Viewer failed for {file_path}: {e}")
            self._view_error_file(file_path, str(e), viewer_frame)
       
        return viewer_frame
   
    def _view_text_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View text-based files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
           
            text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=80, height=30)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
           
        except Exception as e:
            self._view_binary_file(file_path, format_info, parent)
   
    def _view_script_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View script files with syntax highlighting"""
        self._view_text_file(file_path, format_info, parent)
   
    def _view_xml_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View XML files"""
        self._view_text_file(file_path, format_info, parent)
   
    def _view_json_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View JSON files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                formatted = json.dumps(data, indent=2)
           
            text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=80, height=30)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text_widget.insert(tk.END, formatted)
            text_widget.config(state=tk.DISABLED)
           
        except:
            self._view_text_file(file_path, format_info, parent)
   
    def _view_binary_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View binary files in hex format"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
           
            # Create hex viewer
            hex_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=80, height=30)
            hex_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
           
            # Format as hex dump
            hex_dump = self._create_hex_dump(content)
            hex_text.insert(tk.END, hex_dump)
            hex_text.config(state=tk.DISABLED)
           
        except Exception as e:
            self._view_error_file(file_path, str(e), parent)
   
    def _view_hex_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View files in hex format"""
        self._view_binary_file(file_path, format_info, parent)
   
    def _view_image_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View image files"""
        if not HAS_PIL:
            self._view_binary_file(file_path, format_info, parent)
            return
       
        try:
            image = Image.open(file_path)
            photo = ImageTk.PhotoImage(image)
           
            label = tk.Label(parent, image=photo)
            label.image = photo  # Keep a reference
            label.pack(padx=5, pady=5)
           
        except Exception as e:
            self._view_binary_file(file_path, format_info, parent)
   
    def _view_texture_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View texture files"""
        self._view_image_file(file_path, format_info, parent)
   
    def _view_archive_file(self, file_path: str, format_info: Dict[str, Any], parent: tk.Frame):
        """View archive files - show file list"""
        try:
            # Try to use plugin for archive viewing
            processor = self.plugin_manager.get_file_processor('archive', format_info.get('games', ['Unknown'])[0])
            if processor and hasattr(processor, 'view_archive'):
                processor.view_archive(file_path, format_info, parent)
                return
           
            # Fallback to basic binary view
            self._view_binary_file(file_path, format_info, parent)
           
        except Exception as e:
            self._view_binary_file(file_path, format_info, parent)
   
    def _view_error_file(self, file_path: str, error: str, parent: tk.Frame):
        """Display error message when viewer fails"""
        error_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=80, height=10)
        error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        error_text.insert(tk.END, f"Error viewing file {file_path}:\n{error}")
        error_text.config(state=tk.DISABLED)
   
    def _create_hex_dump(self, data: bytes, bytes_per_line: int = 16) -> str:
        """Create formatted hex dump"""
        result = []
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            result.append(f'{i:08x}: {hex_str:<48} {ascii_str}')
        return '\n'.join(result)

# Main application class (simplified for example)
class RAGEAnalyzerApp:
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.format_detector = AdvancedFormatDetector(self.plugin_manager)
        self.file_viewer = FileViewerSystem(self.plugin_manager)
        # ... rest of application code

if __name__ == "__main__":
    app = RAGEAnalyzerApp()
    print("RAGE Evolutionary Analyzer with Plugin System Ready!")