"""
Format Discovery Engine - Aggressive format detection with multiple candidates
"""

import struct
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging


class FormatDiscoveryEngine:
    """Engine for aggressive format discovery and analysis"""
   
    def __init__(self):
        self.format_signatures = {
            b'RSC': 'RAGE Resource',
            b'WVD': 'RAGE WVD Model',
            b'WTD': 'RAGE WTD Texture',
            b'WFT': 'RAGE WFT Format',
            b'DDS': 'DirectDraw Surface',
            b'\x89PNG': 'PNG Image',
            b'\xFF\xD8\xFF': 'JPEG Image',
            b'BM': 'BMP Image',
            b'RIFF': 'Wave Audio',
            b'PK': 'ZIP Archive'
        }
   
    def analyze_file_aggressive(self, file_path: str) -> Dict[str, Any]:
        """Perform aggressive format discovery on file"""
        results = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'candidates': [],
            'primary_candidate': None,
            'analysis_methods_used': []
        }
       
        try:
            with open(file_path, 'rb') as f:
                header = f.read(512)  # Read first 512 bytes for analysis
               
                # Method 1: Signature detection
                signature_candidates = self._detect_by_signature(header)
                results['candidates'].extend(signature_candidates)
                results['analysis_methods_used'].append('signature_detection')
               
                # Method 2: Structure analysis
                structure_candidates = self._analyze_structure(header, file_path)
                results['candidates'].extend(structure_candidates)
                results['analysis_methods_used'].append('structure_analysis')
               
                # Method 3: Extension analysis
                extension_candidates = self._analyze_by_extension(file_path)
                results['candidates'].extend(extension_candidates)
                results['analysis_methods_used'].append('extension_analysis')
               
                # Remove duplicates and sort by confidence
                results['candidates'] = self._deduplicate_candidates(results['candidates'])
               
                # Select primary candidate
                if results['candidates']:
                    results['primary_candidate'] = max(
                        results['candidates'],
                        key=lambda x: x.get('confidence', 0)
                    )
                   
        except Exception as e:
            logging.error(f"Format discovery failed for {file_path}: {e}")
            results['error'] = str(e)
           
        return results
   
    def _detect_by_signature(self, header: bytes) -> List[Dict[str, Any]]:
        """Detect format by file signatures"""
        candidates = []
       
        for signature, format_name in self.format_signatures.items():
            if header.startswith(signature):
                candidates.append({
                    'format': format_name,
                    'confidence': 85.0,
                    'method': 'signature',
                    'signature': signature.hex(),
                    'description': f'Detected by signature: {signature}'
                })
       
        return candidates
   
    def _analyze_structure(self, header: bytes, file_path: str) -> List[Dict[str, Any]]:
        """Analyze file structure to determine format"""
        candidates = []
       
        # Simple structure analysis based on common patterns
        file_size = os.path.getsize(file_path)
       
        # Check for common game format patterns
        if len(header) >= 16:
            # Check for potential RAGE formats
            if self._looks_like_rage_format(header, file_size):
                candidates.append({
                    'format': 'RAGE Generic Resource',
                    'confidence': 70.0,
                    'method': 'structure_analysis',
                    'description': 'Matches RAGE resource structure patterns'
                })
           
            # Check for texture-like patterns
            if self._looks_like_texture(header, file_size):
                candidates.append({
                    'format': 'Unknown Texture Format',
                    'confidence': 60.0,
                    'method': 'structure_analysis',
                    'description': 'Has texture-like data patterns'
                })
       
        return candidates
   
    def _analyze_by_extension(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze format by file extension"""
        ext = Path(file_path).suffix.lower()
        extension_map = {
            '.wvd': ('RAGE WVD Model', 50.0),
            '.wtd': ('RAGE WTD Texture', 50.0),
            '.wft': ('RAGE WFT Format', 50.0),
            '.dds': ('DirectDraw Surface', 80.0),
            '.png': ('PNG Image', 90.0),
            '.jpg': ('JPEG Image', 90.0),
            '.jpeg': ('JPEG Image', 90.0),
            '.bmp': ('BMP Image', 90.0),
            '.tga': ('TGA Image', 85.0),
            '.txt': ('Text File', 95.0),
            '.xml': ('XML File', 95.0),
            '.json': ('JSON File', 95.0)
        }
       
        if ext in extension_map:
            format_name, confidence = extension_map[ext]
            return [{
                'format': format_name,
                'confidence': confidence,
                'method': 'extension',
                'description': f'Based on file extension: {ext}'
            }]
       
        return []
   
    def _looks_like_rage_format(self, header: bytes, file_size: int) -> bool:
        """Check if data looks like RAGE format"""
        # Simple heuristics for RAGE formats
        if len(header) < 16:
            return False
           
        # Check for common RAGE patterns
        # This would be expanded with actual RAGE format knowledge
        return any(pattern in header for pattern in [b'RSC', b'WVD', b'WTD'])
   
    def _looks_like_texture(self, header: bytes, file_size: int) -> bool:
        """Check if data looks like texture"""
        # Simple texture detection heuristics
        if len(header) < 8:
            return False
           
        # Check for common texture dimensions patterns
        # This is very basic and would be improved
        try:
            # Check if first bytes could be dimensions
            width = struct.unpack('<H', header[0:2])[0]
            height = struct.unpack('<H', header[2:4])[0]
           
            if 16 <= width <= 8192 and 16 <= height <= 8192:
                return True
        except:
            pass
           
        return False
   
    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Remove duplicate candidates and sort by confidence"""
        seen = set()
        unique_candidates = []
       
        for candidate in candidates:
            key = candidate['format']
            if key not in seen:
                seen.add(key)
                unique_candidates.append(candidate)
       
        return sorted(unique_candidates, key=lambda x: x.get('confidence', 0), reverse=True)