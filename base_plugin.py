"""
Base Plugin Class for RAGE Analyzer Plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
import logging


class RAGEPlugin(ABC):
    """Base class for all RAGE analyzer plugins"""
   
    def __init__(self):
        self.plugin_name = self.__class__.__name__
        self.supported_formats = []
        self.version = "1.0.0"
        self.description = "Base RAGE analyzer plugin"
       
    @abstractmethod
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze file - must be implemented by subclasses"""
        pass
   
    def can_handle(self, file_path: str, file_data: bytes = None) -> bool:
        """Check if this plugin can handle the given file"""
        return False
   
    def get_format_info(self) -> Dict[str, Any]:
        """Get information about supported formats"""
        return {
            'plugin_name': self.plugin_name,
            'supported_formats': self.supported_formats,
            'version': self.version,
            'description': self.description
        }
   
    def get_capabilities(self) -> List[str]:
        """Get list of plugin capabilities"""
        return ["basic_analysis"]
   
    def validate_file(self, file_path: str) -> bool:
        """Validate if file can be processed"""
        import os
        return os.path.exists(file_path) and os.path.isfile(file_path)


class FormatPlugin(RAGEPlugin):
    """Base class for format-specific plugins"""
   
    def __init__(self):
        super().__init__()
        self.format_signatures = []  # List of byte signatures for this format
   
    def can_handle(self, file_path: str, file_data: bytes = None) -> bool:
        """Check if file matches this plugin's format signatures"""
        if file_data and len(file_data) > 0:
            # Check against signatures
            for signature in self.format_signatures:
                if file_data.startswith(signature):
                    return True
       
        # Check file extension as fallback
        import os
        file_ext = os.path.splitext(file_path)[1].lower()
        format_extensions = [f'.{fmt.lower()}' for fmt in self.supported_formats]
        return file_ext in format_extensions


class AnalysisPlugin(RAGEPlugin):
    """Base class for analysis method plugins"""
   
    def __init__(self):
        super().__init__()
        self.analysis_method = "generic"
   
    def can_handle(self, file_path: str, file_data: bytes = None) -> bool:
        """Analysis plugins can handle any file type"""
        return self.validate_file(file_path)