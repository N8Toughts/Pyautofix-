import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class UniversalPluginManager:
    """Manages ALL game engine plugins for ultimate evolutionary analysis"""
   
    def __init__(self):
        self.engine_plugins = {}
        self.cross_engine_patterns = []
        self.load_all_plugins()
   
    def load_all_plugins(self):
        """Dynamically load ALL available game engine plugins"""
        plugins_to_try = [
            ('rage_engine', 'plugins.rage_evolutionary_detector', 'RAGEEvolutionaryDetector'),
            ('unreal_engine', 'plugins.unreal_engine_detector', 'UnrealEngineDetector'),
            ('unity_engine', 'plugins.unity_engine_detector', 'UnityEngineDetector'),
            ('source_engine', 'plugins.source_engine_detector', 'SourceEngineDetector'),
            ('openiv_database', 'plugins.openiv_format_database', 'OpenIVFormatDatabase')
        ]
       
        for engine_name, module_path, class_name in plugins_to_try:
            try:
                module = __import__(module_path, fromlist=[class_name])
                plugin_class = getattr(module, class_name)
                self.engine_plugins[engine_name] = plugin_class()
                logger.info(f"✅ Loaded {engine_name} plugin")
            except ImportError as e:
                logger.info(f"❌ {engine_name} plugin not available: {e}")
   
    def universal_file_analysis(self, file_path: str) -> Dict[str, Any]:
        """Analyze file with EVERY available engine plugin"""
        results = {
            'file_path': file_path,
            'engine_matches': [],
            'cross_engine_insights': [],
            'evolutionary_timeline': [],
            'universal_recommendations': []
        }
       
        # Run all plugin analyses
        for engine_name, plugin in self.engine_plugins.items():
            try:
                if hasattr(plugin, 'detect_asset'):
                    engine_result = plugin.detect_asset(file_path)
                elif hasattr(plugin, 'identify_file_format'):
                    engine_result = plugin.identify_file_format(file_path)
                else:
                    continue
                   
                if engine_result and self.has_detections(engine_result):
                    results['engine_matches'].append({
                        'engine': engine_name,
                        'results': engine_result,
                        'confidence': self.calculate_confidence(engine_result)
                    })
            except Exception as e:
                logger.error(f"Plugin {engine_name} error: {e}")
       
        # Cross-engine analysis
        results['cross_engine_insights'] = self.analyze_cross_engine_patterns(results['engine_matches'])
        results['evolutionary_timeline'] = self.build_evolutionary_timeline(results['engine_matches'])
        results['universal_recommendations'] = self.generate_universal_recommendations(results)
       
        return results

    def has_detections(self, engine_result: Dict[str, Any]) -> bool:
        """Check if engine found anything meaningful"""
        detection_keys = ['detected_assets', 'engine_matches', 'identified_format', 'era_detected']
        for key in detection_keys:
            if engine_result.get(key):
                return True
        return False

    def calculate_confidence(self, engine_result: Dict[str, Any]) -> float:
        """Calculate confidence score for engine detection"""
        confidence = 0.0
       
        if engine_result.get('detected_assets'):
            confidence = max(confidence, 0.8)
        if engine_result.get('identified_format'):
            confidence = max(confidence, 0.9)
        if engine_result.get('era_detected'):
            confidence = max(confidence, 0.7)
           
        return confidence

    def analyze_cross_engine_patterns(self, engine_matches: List[Dict]) -> List[Dict[str, Any]]:
        """Find patterns across different game engines"""
        insights = []
       
        if len(engine_matches) > 1:
            engines = [match['engine'] for match in engine_matches]
            insights.append({
                'type': 'multi_engine_compatibility',
                'description': f'File compatible with multiple engines: {", ".join(engines)}',
                'significance': 'high'
            })
       
        # Check for engine evolution patterns
        engine_evolution = ['source_engine', 'unreal_engine', 'unity_engine', 'rage_engine']
        detected_evolution = [match['engine'] for match in engine_matches if match['engine'] in engine_evolution]
       
        if len(detected_evolution) > 1:
            insights.append({
                'type': 'engine_evolution_showcase',
                'description': f'Shows game engine evolution: {" → ".join(detected_evolution)}',
                'significance': 'medium'
            })
           
        return insights

    def build_evolutionary_timeline(self, engine_matches: List[Dict]) -> List[Dict[str, Any]]:
        """Build a timeline of game engine evolution based on detections"""
        timeline = []
       
        # Engine release timelines (simplified)
        engine_timelines = {
            'source_engine': {'start': 1998, 'end': 2023, 'name': 'Source Engine'},
            'unreal_engine': {'start': 1998, 'end': 2023, 'name': 'Unreal Engine'},
            'unity_engine': {'start': 2005, 'end': 2023, 'name': 'Unity Engine'},
            'rage_engine': {'start': 2006, 'end': 2023, 'name': 'RAGE Engine'}
        }
       
        for match in engine_matches:
            engine = match['engine']
            if engine in engine_timelines:
                timeline.append(engine_timelines[engine])
       
        return sorted(timeline, key=lambda x: x['start'])

    def generate_universal_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on all engine analyses"""
        recommendations = []
       
        if results['engine_matches']:
            recommendations.append("File successfully identified by multiple game engine detectors")
           
            if len(results['engine_matches']) > 1:
                recommendations.append("Consider this file for cross-engine modding projects")
               
            # Tool recommendations from all engines
            all_tools = set()
            for match in results['engine_matches']:
                engine_tools = match['results'].get('compatible_tools', [])
                all_tools.update(engine_tools)
               
            if all_tools:
                recommendations.append(f"Compatible tools: {', '.join(sorted(all_tools))}")
        else:
            recommendations.append("File format not recognized by any game engine detector")
            recommendations.append("Consider manual analysis or custom tool development")
           
        return recommendations

    def get_engine_coverage_report(self) -> Dict[str, Any]:
        """Report on which game engines are covered"""
        return {
            'total_engines': len(self.engine_plugins),
            'available_engines': list(self.engine_plugins.keys()),
            'coverage': {
                'rage_engine': 'Rockstar Advanced Game Engine (2006-present)',
                'unreal_engine': 'Unreal Engine (1998-present)',
                'unity_engine': 'Unity Engine (2005-present)',
                'source_engine': 'Source Engine (1998-present)'
            }
        }