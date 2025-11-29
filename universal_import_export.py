import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class UniversalImportExport:
    """Handles import/export across ALL game engines with reader testing"""
   
    def __init__(self):
        self.import_export_tools = {
            'rage_engine': {
                'import_tools': ['OpenIV', 'CodeWalker', 'RAGE Studio Suite', 'Blender RAGE Tools'],
                'export_tools': ['OpenIV', 'CodeWalker', 'RAGE Studio Suite'],
                'test_readers': ['openiv_reader', 'codewalker_reader', 'rage_studio_reader']
            },
            'unreal_engine': {
                'import_tools': ['Unreal Editor', 'UModel', 'FModel', 'Blender UE Tools'],
                'export_tools': ['Unreal Editor', 'Blender UE Tools'],
                'test_readers': ['unreal_editor_reader', 'umodel_reader', 'fmodel_reader']
            },
            'unity_engine': {
                'import_tools': ['Unity Editor', 'AssetStudio', 'UABEA', 'DevX'],
                'export_tools': ['Unity Editor', 'Blender Unity Tools'],
                'test_readers': ['unity_editor_reader', 'assetstudio_reader', 'uabea_reader']
            },
            'source_engine': {
                'import_tools': ['Blender Source Tools', 'Crowbar', 'VTFEdit', 'Hammer Editor'],
                'export_tools': ['Blender Source Tools', 'Hammer Editor'],
                'test_readers': ['source_tools_reader', 'crowbar_reader', 'vtfedit_reader']
            }
        }
       
        self.known_converters = {
            'rage_to_unreal': ['RAGE Studio Suite', 'Custom Python Scripts'],
            'unreal_to_rage': ['RAGE Studio Suite', 'Manual Recreation'],
            'unity_to_rage': ['AssetStudio -> RAGE Studio Suite'],
            'source_to_rage': ['Blender Source Tools -> RAGE Studio Suite'],
            'cross_engine': ['Blender (Universal)', 'Assimp', 'Custom Converters']
        }

    def get_import_export_advice(self, file_path: str, target_engine: str = None) -> Dict[str, Any]:
        """Get comprehensive import/export advice for any file"""
        # First identify the file
        from core.universal_plugin_manager import UniversalPluginManager
        plugin_manager = UniversalPluginManager()
        analysis = plugin_manager.universal_file_analysis(file_path)
       
        advice = {
            'file_analysis': analysis,
            'import_options': [],
            'export_options': [],
            'conversion_paths': [],
            'reader_test_results': [],
            'recommended_workflow': []
        }
       
        # Get import options for detected engines
        for engine_match in analysis.get('engine_matches', []):
            engine = engine_match['engine']
            if engine in self.import_export_tools:
                advice['import_options'].extend(
                    self.import_export_tools[engine]['import_tools']
                )
                advice['export_options'].extend(
                    self.import_export_tools[engine]['export_tools']
                )
       
        # Test readers aggressively
        advice['reader_test_results'] = self.aggressive_reader_testing(file_path, analysis)
       
        # Generate conversion paths
        if target_engine:
            advice['conversion_paths'] = self.generate_conversion_paths(
                analysis, target_engine
            )
       
        # Recommended workflow
        advice['recommended_workflow'] = self.generate_recommended_workflow(
            advice, target_engine
        )
       
        return advice

    def aggressive_reader_testing(self, file_path: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggressively test various readers to identify files"""
        test_results = []
       
        for engine_match in analysis.get('engine_matches', []):
            engine = engine_match['engine']
            if engine in self.import_export_tools:
                readers = self.import_export_tools[engine]['test_readers']
               
                for reader in readers:
                    result = self.test_reader_compatibility(file_path, reader, engine)
                    test_results.append(result)
       
        # Also test universal readers
        universal_readers = ['blender_universal', 'assimp_reader', 'custom_python_reader']
        for reader in universal_readers:
            result = self.test_reader_compatibility(file_path, reader, 'universal')
            test_results.append(result)
       
        return sorted(test_results, key=lambda x: x['success_score'], reverse=True)

    def test_reader_compatibility(self, file_path: str, reader: str, engine: str) -> Dict[str, Any]:
        """Test if a specific reader can handle the file"""
        result = {
            'reader': reader,
            'engine': engine,
            'success_score': 0,
            'test_method': 'simulated',
            'details': '',
            'recommended_action': ''
        }
       
        try:
            # Simulated reader testing (in real implementation, would actually call tools)
            if engine == 'rage_engine':
                if reader == 'openiv_reader':
                    result['success_score'] = self.simulate_openiv_test(file_path)
                    result['details'] = 'OpenIV RAGE format specialist'
                    result['recommended_action'] = 'Use OpenIV for RAGE asset extraction'
               
                elif reader == 'codewalker_reader':
                    result['success_score'] = self.simulate_codewalker_test(file_path)
                    result['details'] = 'CodeWalker GTA V specialist'
                    result['recommended_action'] = 'Use CodeWalker for GTA V map/data editing'
               
                elif reader == 'rage_studio_reader':
                    result['success_score'] = self.simulate_rage_studio_test(file_path)
                    result['details'] = 'RAGE Studio Suite universal RAGE tool'
                    result['recommended_action'] = 'Use RAGE Studio Suite for cross-game RAGE assets'
           
            elif engine == 'unreal_engine':
                if reader == 'unreal_editor_reader':
                    result['success_score'] = 0.9
                    result['details'] = 'Native Unreal Engine editor'
                    result['recommended_action'] = 'Import directly into Unreal Editor'
           
            # Universal readers
            elif engine == 'universal':
                if reader == 'blender_universal':
                    result['success_score'] = 0.7
                    result['details'] = 'Blender with all import plugins'
                    result['recommended_action'] = 'Try importing into Blender with relevant addons'
               
                elif reader == 'assimp_reader':
                    result['success_score'] = 0.6
                    result['details'] = 'Assimp library multi-format support'
                    result['recommended_action'] = 'Use Assimp for format conversion'
       
        except Exception as e:
            result['details'] = f'Test error: {str(e)}'
            result['success_score'] = 0
       
        return result

    def simulate_openiv_test(self, file_path: str) -> float:
        """Simulate OpenIV compatibility testing"""
        path = Path(file_path)
       
        # OpenIV known formats
        openiv_formats = ['.ydr', '.ydd', '.yft', '.ytd', '.wdr', '.wdd', '.wft', '.wtd', '.rpf']
        if path.suffix.lower() in openiv_formats:
            return 0.95
        else:
            return 0.3  # OpenIV might still work with plugins

    def simulate_codewalker_test(self, file_path: str) -> float:
        """Simulate CodeWalker compatibility testing"""
        path = Path(file_path)
       
        # CodeWalker specializes in GTA V
        if path.suffix.lower() in ['.ytyp', '.ymap', '.ybn']:
            return 0.98  # CodeWalker's specialty
        elif path.suffix.lower() in ['.ydr', '.ydd', '.yft']:
            return 0.8   # CodeWalker can view these
        else:
            return 0.2   # Not CodeWalker's focus

    def simulate_rage_studio_test(self, file_path: str) -> float:
        """Simulate RAGE Studio Suite compatibility testing"""
        # RAGE Studio Suite is designed for cross-game RAGE assets
        path = Path(file_path)
       
        rage_formats = ['.ydr', '.ydd', '.yft', '.wdr', '.wdd', '.wft', '.rpf']
        if path.suffix.lower() in rage_formats:
            return 0.9  # RAGE Studio Suite's specialty
        elif 'map' in path.name.lower() or 'terrain' in path.name.lower():
            return 0.85  # Map/terrain tools
        else:
            return 0.4   # Might work with custom importers

    def generate_conversion_paths(self, analysis: Dict[str, Any], target_engine: str) -> List[Dict[str, Any]]:
        """Generate conversion paths from source to target engine"""
        conversion_paths = []
       
        source_engines = [match['engine'] for match in analysis.get('engine_matches', [])]
       
        for source_engine in source_engines:
            conversion_key = f"{source_engine}_to_{target_engine}"
           
            if conversion_key in self.known_converters:
                path = {
                    'source_engine': source_engine,
                    'target_engine': target_engine,
                    'tools': self.known_converters[conversion_key],
                    'complexity': self.estimate_conversion_complexity(source_engine, target_engine),
                    'success_likelihood': self.estimate_success_likelihood(source_engine, target_engine)
                }
                conversion_paths.append(path)
       
        # Add universal conversion paths
        universal_path = {
            'source_engine': 'any',
            'target_engine': target_engine,
            'tools': ['Blender (Universal Converter)', 'Custom Python Scripts', 'Manual Recreation'],
            'complexity': 'medium',
            'success_likelihood': 'variable'
        }
        conversion_paths.append(universal_path)
       
        return conversion_paths

    def estimate_conversion_complexity(self, source: str, target: str) -> str:
        """Estimate conversion complexity between engines"""
        complexity_map = {
            'rage_to_unreal': 'medium',
            'unreal_to_rage': 'high',
            'unity_to_rage': 'medium',
            'source_to_rage': 'high',
            'rage_to_unity': 'medium',
            'unreal_to_unity': 'low',
            'unity_to_unreal': 'low'
        }
       
        key = f"{source}_to_{target}"
        return complexity_map.get(key, 'unknown')

    def estimate_success_likelihood(self, source: str, target: str) -> str:
        """Estimate likelihood of successful conversion"""
        likelihood_map = {
            'rage_to_unreal': 'high',
            'unreal_to_rage': 'medium',
            'unity_to_rage': 'medium',
            'source_to_rage': 'low',
            'rage_to_unity': 'high',
            'unreal_to_unity': 'high',
            'unity_to_unreal': 'high'
        }
       
        key = f"{source}_to_{target}"
        return likelihood_map.get(key, 'unknown')

    def generate_recommended_workflow(self, advice: Dict[str, Any], target_engine: str) -> List[str]:
        """Generate step-by-step workflow recommendations"""
        workflow = []
       
        # Start with identification
        workflow.append("1. File identified by multiple engine detectors")
       
        # Add reader recommendations
        successful_readers = [r for r in advice['reader_test_results'] if r['success_score'] > 0.7]
        if successful_readers:
            best_reader = successful_readers[0]
            workflow.append(f"2. Use {best_reader['reader']} for initial import ({best_reader['success_score']:.0%} success)")
       
        # Add conversion steps if target specified
        if target_engine and advice['conversion_paths']:
            best_path = max(advice['conversion_paths'], key=lambda x: x['success_likelihood'])
            workflow.append(f"3. Convert using: {', '.join(best_path['tools'])}")
            workflow.append(f"4. Expected complexity: {best_path['complexity']}")
       
        # Final recommendation
        workflow.append("5. Test import in target environment and validate")
       
        return workflow

    def get_tool_installation_guide(self, tool_name: str) -> Dict[str, Any]:
        """Get installation and usage guide for specific tools"""
        guides = {
            'OpenIV': {
                'purpose': 'RAGE engine asset browser and editor',
                'installation': 'Download from OpenIV.com, install, enable modding mode',
                'usage': 'Browse RPF archives, extract/edit/reimport assets',
                'supported_formats': 'All RAGE formats (RPF, YDR, WDR, etc.)'
            },
            'CodeWalker': {
                'purpose': 'GTA V map and data editor',
                'installation': 'Download from GitHub releases, requires .NET',
                'usage': 'Edit maps, placements, explore game data',
                'supported_formats': 'GTA V specific (YMAP, YTYP, YBN)'
            },
            'RAGE Studio Suite': {
                'purpose': 'Universal RAGE engine content creation',
                'installation': 'Blender plugin - install via Preferences > Add-ons',
                'usage': 'Import/export RAGE assets, terrain tools, map creation',
                'supported_formats': 'Cross-game RAGE assets, heightmap processing'
            },
            'Blender': {
                'purpose': 'Universal 3D content creation',
                'installation': 'Download from blender.org, install relevant import/export addons',
                'usage': 'Use File > Import/Export with appropriate formats',
                'supported_formats': 'Universal with plugins (FBX, OBJ, plus engine-specific)'
            }
        }
       
        return guides.get(tool_name, {'error': 'Tool guide not available'})