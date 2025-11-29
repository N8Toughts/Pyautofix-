"""
Base Format Support Plugin for RAGE Evolutionary Analyzer
Provides common format detection and processing capabilities
"""

import os
import struct
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger("RAGEAnalyzer.BaseFormatsPlugin")

def register_plugin():
    """Register this plugin with the RAGE Analyzer"""
    return {
        'name': 'Base Format Support',
        'version': '1.0.0',
        'author': 'RAGE Brainiac',
        'description': 'Common file format detection and processing',
        'games': ['Multiple'],
        'formats': ['dds', 'png', 'jpg', 'xml', 'json', 'txt']
    }

def get_format_database():
    """Provide base format database"""
    return {
        'dds': {
            'name': 'DirectDraw Surface',
            'magic': b'DDS ',
            'games': ['Multiple'],
            'extensions': ['.dds'],
            'structure': 'texture',
            'confidence': 95
        },
        'png': {
            'name': 'Portable Network Graphics',
            'magic': b'\x89PNG',
            'games': ['Multiple'],
            'extensions': ['.png'],
            'structure': 'image',
            'confidence': 99
        },
        'jpg': {
            'name': 'JPEG Image',
            'magic': b'\xFF\xD8\xFF',
            'games': ['Multiple'],
            'extensions': ['.jpg', '.jpeg'],
            'structure': 'image',
            'confidence': 98
        },
        'xml': {
            'name': 'XML Data',
            'magic': b'<?xml',
            'games': ['Multiple'],
            'extensions': ['.xml'],
            'structure': 'data',
            'confidence': 90
        },
        'json': {
            'name': 'JSON Data',
            'magic': b'{',
            'games': ['Multiple'],
            'extensions': ['.json'],
            'structure': 'data',
            'confidence': 95
        },
        'txt': {
            'name': 'Text File',
            'magic': b'',
            'games': ['Multiple'],
            'extensions': ['.txt'],
            'structure': 'text',
            'confidence': 80
        }
    }

def get_magic_numbers():
    """Provide base magic numbers"""
    return {
        b'DDS ': 'dds',
        b'\x89PNG': 'png',
        b'\xFF\xD8\xFF': 'jpg',
        b'<?xml': 'xml',
        b'{': 'json'
    }

def can_handle(format_type: str, game: str = None) -> bool:
    """Check if this plugin can handle the given format"""
    base_formats = ['dds', 'png', 'jpg', 'xml', 'json', 'txt']
    return format_type.lower() in base_formats