import logging
import struct
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SourceEngineDetector:
    """Source Engine evolutionary analysis - GoldSrc to Source 2"""
   
    def __init__(self):
        self.source_signatures = {
            b'VBSP': {'format': 'Source Map', 'engine': 'source'},
            b'VMF\x00': {'format': 'Valve Map File', 'engine': 'source'},
            b'MDL\x00': {'format': 'Source Model', 'engine': 'source'},
            b'VTF\x00': {'format': 'Valve Texture', 'engine': 'source'},
            b'VMT\x00': {'format': 'Valve Material', 'engine': 'source'},
            b'PACK': {'format': 'Source Package', 'engine': 'source'},
            b'VPK\x00': {'format': 'Valve Package', 'engine': 'source2'},
            b'VSND': {'format': 'Source Sound', 'engine': 'source'},
        }
       
        self.source_evolution = {
            'goldsrc': {
                'years': '1998-2004',
                'games': ['Half-Life', 'Counter-Strike 1.6', 'Team Fortress Classic'],
                'formats': ['BSP', 'MDL', 'WAD'],
                'features': 'Quake-based, brush-based levels'
            },
            'source1_2004': {
                'years': '2004-2006',
                'games': ['Half-Life 2', 'Counter-Strike: Source'],
                'formats': ['VBSP', 'VMF', 'MDL', 'VTF', 'VMT'],
                'features': 'Physics, normal mapping, facial animation'
            },
            'source1_2007': {
                'years': '2007-2010',
                'games': ['Portal', 'Team Fortress 2', 'Left 4 Dead'],
                'formats': ['VPK early'],
                'features': 'Cartoon rendering, advanced physics'
            },
            'source1_2010': {
                'years': '2010-2013',
                'games': ['Portal 2', 'Left 4 Dead 2', 'Counter-Strike: Global Offensive'],
                'formats': ['VPK'],
                'features': 'Improved AI, cooperative gameplay'
            },
            'source2_2015': {
                'years': '2015-2020',
                'games': ['Dota 2 Reborn', 'Artifact', 'Half-Life: Alyx'],
                'formats': ['VMDL', 'VMAT', 'VPK v2'],
                'features': 'Vulkan, VR, new asset system'
            }
        }

    def detect_source_asset(self, file_path: str) -> Dict[str, Any]:
        """Evolutionary Source engine asset detection"""
        result = {
            'engine': 'source',
            'generation_detected': [],
            'game_lineage': [],
            'compatible_tools': ['Hammer Editor', 'Source SDK', 'Crowbar', 'VTFEdit', 'Blender Source Tools'],
            'source_specific': {
                'map_entities': self.detect_map_entities(file_path),
                'model_data': self.analyze_model_structure(file_path),
                'texture_info': self.get_texture_information(file_path)
            }
        }
       
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
               
                # Check Source engine signatures across generations
                for signature, info in self.source_signatures.items():
                    if signature in header:
                        generation = self.map_signature_to_generation(signature, header)
                        result['generation_detected'].append({
                            'generation': generation,
                            'format': info['format'],
                            'engine': info['engine'],
                            'confidence': 0.9,
                            'compatible_games': self.get_compatible_games(generation)
                        })
               
                # Game lineage analysis
                result['game_lineage'] = self.analyze_game_lineage(header, file_path)
               
        except Exception as e:
            logger.error(f"Source engine analysis error: {e}")
           
        return result

    def map_signature_to_generation(self, signature: bytes, header: bytes) -> str:
        """Map signature to Source engine generation"""
        if signature == b'VPK\x00':
            # Check Source 2 VPK
            if len(header) > 8 and header[4:8] == b'\x02\x00\x00\x00':
                return 'source2_2015'
            else:
                return 'source1_2010'
        elif signature in [b'VMDL', b'VMAT']:
            return 'source2_2015'
        else:
            return 'source1_2004'

    def analyze_game_lineage(self, header: bytes, file_path: str) -> List[Dict[str, Any]]:
        """Analyze which Source games this asset might belong to"""
        lineage = []
        path = Path(file_path)
       
        # BSP version detection
        if header.startswith(b'VBSP'):
            try:
                version = struct.unpack('<I', header[4:8])[0]
                if version == 19:  # Half-Life 2
                    lineage.append({'game': 'Half-Life 2', 'confidence': 0.9})
                elif version == 20:  # Episode 1
                    lineage.append({'game': 'Half-Life 2: Episode One', 'confidence': 0.9})
                elif version == 21:  # Episode 2, Portal
                    lineage.append({'game': 'Half-Life 2: Episode Two / Portal', 'confidence': 0.8})
                elif version >= 22:  # Later games
                    lineage.append({'game': 'Left 4 Dead / Portal 2', 'confidence': 0.7})
            except:
                pass
       
        # Model format hints
        if header.startswith(b'MDL'):
            try:
                # Check for specific game model signatures
                if b'hl2' in path.name.lower():
                    lineage.append({'game': 'Half-Life 2', 'confidence': 0.8})
                elif b'cs_' in path.name.lower():
                    lineage.append({'game': 'Counter-Strike: Source', 'confidence': 0.7})
                elif b'tf_' in path.name.lower():
                    lineage.append({'game': 'Team Fortress 2', 'confidence': 0.8})
                elif b'portal' in path.name.lower():
                    lineage.append({'game': 'Portal', 'confidence': 0.9})
            except:
                pass
               
        return lineage

    def detect_map_entities(self, file_path: str) -> List[str]:
        """Detect map entities for level design analysis"""
        entities = []
        try:
            with open(file_path, 'rb', encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)  # Read more for entity scanning
               
                # Common Source engine entities
                entity_patterns = {
                    b'worldspawn': 'World Geometry',
                    b'prop_static': 'Static Prop',
                    b'prop_dynamic': 'Dynamic Prop',
                    b'light': 'Light Source',
                    b'env_cubemap': 'Reflection Cubemap',
                    b'func_door': 'Door',
                    b'func_button': 'Button',
                    b'trigger_multiple': 'Trigger Area',
                    b'info_player_start': 'Player Spawn',
                    b'npc_': 'NPC Entity',
                    b'weapon_': 'Weapon Entity'
                }
               
                for pattern, description in entity_patterns.items():
                    if pattern in content.lower():
                        entities.append(description)
                       
        except:
            pass
           
        return list(set(entities))  # Remove duplicates

    def analyze_model_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze Source model structure"""
        model_info = {'is_model': False, 'lod_count': 0, 'has_physics': False}
       
        try:
            with open(file_path, 'rb') as f:
                header = f.read(64)
               
                if header.startswith(b'MDL'):
                    model_info['is_model'] = True
                   
                    # Simplified LOD detection
                    if len(header) > 0x30:
                        # Check for LOD sections (simplified)
                        lod_count = struct.unpack('<I', header[0x30:0x34])[0]
                        model_info['lod_count'] = min(lod_count, 8)  # Reasonable max
                   
                    # Physics detection
                    if b'VPHY' in header:
                        model_info['has_physics'] = True
                       
        except:
            pass
           
        return model_info

    def get_texture_information(self, file_path: str) -> Dict[str, Any]:
        """Get Source texture information"""
        texture_info = {'is_texture': False, 'format': 'unknown', 'dimensions': 'unknown'}
       
        try:
            with open(file_path, 'rb') as f:
                header = f.read(64)
               
                if header.startswith(b'VTF'):
                    texture_info['is_texture'] = True
                   
                    # VTF version
                    if len(header) >= 8:
                        version = struct.unpack('<II', header[4:12])
                        texture_info['version'] = f"{version[0]}.{version[1]}"
                   
                    # Dimensions (simplified)
                    if len(header) >= 20:
                        width = struct.unpack('<H', header[12:14])[0]
                        height = struct.unpack('<H', header[14:16])[0]
                        texture_info['dimensions'] = f"{width}x{height}"
                       
        except:
            pass
           
        return texture_info

    def get_compatible_games(self, generation: str) -> List[str]:
        """Get games compatible with detected generation"""
        return self.source_evolution.get(generation, {}).get('games', [])