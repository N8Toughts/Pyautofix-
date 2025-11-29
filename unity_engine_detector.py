import logging
import struct
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class UnityEngineDetector:
    """Unity Engine evolutionary analysis - from 2005 to present"""
   
    def __init__(self):
        self.unity_signatures = {
            b'UnityWeb': {'format': 'Unity Web Player', 'era': 'early'},
            b'UnityFS': {'format': 'Unity Asset Bundle', 'era': 'modern'},
            b'\x22\x48\x4C\x46': {'format': 'Unity Asset File', 'era': 'legacy'},  # "HLF"
            b'\x55\x6E\x69\x74\x79': {'format': 'Unity Raw Asset', 'era': 'all'},  # "Unity"
        }
       
        self.unity_evolution = {
            'unity_1': {'years': '2005-2006', 'formats': ['.unity3d'], 'features': 'Basic 3D'},
            'unity_2': {'years': '2007-2009', 'formats': ['.asset', '.prefab'], 'features': 'Asset Pipeline'},
            'unity_3': {'years': '2010-2012', 'formats': ['.unity'], 'features': 'AssetBundles'},
            'unity_4': {'years': '2012-2015', 'formats': ['.unitypackage'], 'features': 'Native 2D'},
            'unity_5': {'years': '2015-2017', 'formats': ['.assets'], 'features': 'PBR, VR'},
            'unity_2017': {'years': '2017-2018', 'formats': ['UnityFS'], 'features': 'Scriptable Render Pipeline'},
            'unity_2019': {'years': '2019-2020', 'formats': ['.blob'], 'features': 'DOTS, Burst'},
            'unity_2020': {'years': '2020-2021', 'formats': ['.hash'], 'features': 'Asset Database V2'},
            'unity_2021': {'years': '2021-2022', 'formats': ['.resource'], 'features': 'Unity Cloud'},
            'unity_2022': {'years': '2022-2023', 'formats': ['.meta'], 'features': 'AI Tools'},
        }

    def detect_unity_asset(self, file_path: str) -> Dict[str, Any]:
        """Evolutionary Unity asset detection"""
        result = {
            'engine': 'unity',
            'era_detected': [],
            'evolution_path': [],
            'compatible_tools': ['Unity Editor', 'AssetStudio', 'UABEA', 'DevX'],
            'unity_specific': {
                'potential_assets': self.detect_unity_asset_types(file_path),
                'version_hints': self.detect_unity_version(file_path),
                'bundle_info': self.analyze_asset_bundle(file_path)
            }
        }
       
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
               
                # Check Unity signatures across eras
                for signature, info in self.unity_signatures.items():
                    if signature in header:
                        era = info['era']
                        result['era_detected'].append({
                            'era': era,
                            'format': info['format'],
                            'confidence': 0.85,
                            'compatible_versions': self.get_compatible_versions(era)
                        })
               
                # Evolutionary analysis
                result['evolution_path'] = self.analyze_unity_evolution(header, file_path)
               
        except Exception as e:
            logger.error(f"Unity analysis error: {e}")
           
        return result

    def analyze_unity_evolution(self, header: bytes, file_path: str) -> List[Dict[str, Any]]:
        """Analyze Unity's engine evolution through file patterns"""
        evolution = []
        path = Path(file_path)
       
        # File extension evolution
        ext_evolution = {
            '.unity3d': 'unity_1',
            '.asset': 'unity_2',
            '.prefab': 'unity_2',
            '.unity': 'unity_3',
            '.unitypackage': 'unity_4',
            '.assets': 'unity_5',
        }
       
        if path.suffix.lower() in ext_evolution:
            version = ext_evolution[path.suffix.lower()]
            evolution.append({
                'type': 'file_extension',
                'version': version,
                'description': f'{self.unity_evolution[version]["years"]} - {self.unity_evolution[version]["features"]}',
                'confidence': 0.7
            })
       
        # Header pattern evolution
        if b'UnityFS' in header:
            evolution.append({
                'type': 'bundle_format',
                'version': 'unity_2017+',
                'description': 'Modern Asset Bundle (2017+) with improved compression',
                'confidence': 0.9
            })
       
        if b'UnityWeb' in header:
            evolution.append({
                'type': 'web_player',
                'version': 'unity_3',
                'description': 'Unity Web Player era (2010-2014)',
                'confidence': 0.8
            })
           
        return evolution

    def detect_unity_asset_types(self, file_path: str) -> List[str]:
        """Detect specific Unity asset types"""
        asset_types = []
        try:
            with open(file_path, 'rb', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)
               
                # Common Unity asset patterns
                if b'Texture2D' in content:
                    asset_types.append('Texture2D')
                if b'GameObject' in content:
                    asset_types.append('GameObject')
                if b'Mesh' in content:
                    asset_types.append('Mesh')
                if b'Material' in content:
                    asset_types.append('Material')
                if b'Shader' in content:
                    asset_types.append('Shader')
                if b'AnimationClip' in content:
                    asset_types.append('Animation')
                   
        except:
            pass
           
        return asset_types

    def detect_unity_version(self, file_path: str) -> List[str]:
        """Detect Unity version hints"""
        versions = []
        try:
            with open(file_path, 'rb', encoding='utf-8', errors='ignore') as f:
                content = f.read(2048)
               
                # Version string patterns
                if b'5.x' in content:
                    versions.append('Unity 5.x (2015-2017)')
                if b'2017' in content:
                    versions.append('Unity 2017+')
                if b'2018' in content:
                    versions.append('Unity 2018+')
                if b'2019' in content:
                    versions.append('Unity 2019+')
                if b'2020' in content:
                    versions.append('Unity 2020+')
                if b'2021' in content:
                    versions.append('Unity 2021+')
                if b'2022' in content:
                    versions.append('Unity 2022+')
                   
        except:
            pass
           
        return versions

    def analyze_asset_bundle(self, file_path: str) -> Dict[str, Any]:
        """Analyze Unity Asset Bundle structure"""
        bundle_info = {'is_bundle': False, 'compression': 'unknown', 'assets_count': 'unknown'}
       
        try:
            with open(file_path, 'rb') as f:
                header = f.read(64)
               
                if b'UnityFS' in header:
                    bundle_info['is_bundle'] = True
                   
                    # Check compression (simplified)
                    if header[0x08:0x0C] == b'\x00\x00\x00\x00':
                        bundle_info['compression'] = 'none'
                    elif header[0x08:0x0C] == b'\x01\x00\x00\x00':
                        bundle_info['compression'] = 'lz4'
                    elif header[0x08:0x0C] == b'\x02\x00\x00\x00':
                        bundle_info['compression'] = 'lzma'
                       
        except:
            pass
           
        return bundle_info

    def get_compatible_versions(self, era: str) -> List[str]:
        """Get Unity versions compatible with detected era"""
        era_to_versions = {
            'early': ['unity_1', 'unity_2', 'unity_3'],
            'legacy': ['unity_3', 'unity_4', 'unity_5'],
            'modern': ['unity_2017', 'unity_2019', 'unity_2020', 'unity_2021', 'unity_2022'],
            'all': list(self.unity_evolution.keys())
        }
        return era_to_versions.get(era, [])