import logging
from pathlib import Path
from typing import Dict, List, Any
import struct
import datetime

logger = logging.getLogger(__name__)

class RAGEEvolutionaryDetector:
    """Evolutionary file detection across all RAGE engine games"""
   
    def __init__(self):
        self.game_profiles = {
            'max_payne_3': self.MaxPayne3Profile(),
            'gta_iv': self.GTAIVProfile(),
            'midnight_club_3': self.MidnightClub3Profile(),
            'red_dead_redemption': self.RDR1Profile(),
            'gta_v': self.GTAVProfile()
        }
        self.evolutionary_patterns = []
        self.cross_game_matches = []

    def detect_evolutionary_patterns(self, file_path: str) -> Dict[str, Any]:
        """Test file against all RAGE engine variants"""
        results = {
            'file_path': file_path,
            'game_matches': [],
            'confidence_scores': {},
            'evolutionary_insights': [],
            'recommended_reader': None
        }

        # Test against all game profiles
        for game_name, profile in self.game_profiles.items():
            match_result = profile.analyze_file(file_path)
            if match_result['confidence'] > 0.3:  # Threshold for potential match
                results['game_matches'].append({
                    'game': game_name,
                    'confidence': match_result['confidence'],
                    'detection_methods': match_result['methods'],
                    'file_type_suggested': match_result['suggested_type']
                })
                results['confidence_scores'][game_name] = match_result['confidence']

        # Evolutionary analysis
        results['evolutionary_insights'] = self.analyze_evolutionary_patterns(results['game_matches'])
        results['recommended_reader'] = self.suggest_best_reader(results)

        # Learn from this analysis
        self.record_evolutionary_learning(file_path, results)
        return results

    class MaxPayne3Profile:
        """Max Payne 3 (RAGE 1.2) file profile"""
       
        def analyze_file(self, file_path: str) -> Dict[str, Any]:
            path = Path(file_path)
            result = {'confidence': 0.0, 'methods': [], 'suggested_type': 'unknown'}

            # Max Payne 3 specific signatures
            mp3_signatures = {
                b'MP3H': 'Max Payne 3 header',
                b'MP3T': 'Max Payne 3 texture',
                b'MP3M': 'Max Payne 3 model'
            }

            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)

                # Check for MP3 specific signatures
                for sig, desc in mp3_signatures.items():
                    if sig in header:
                        result['confidence'] = 0.9
                        result['methods'].append(f"MP3 signature: {desc}")
                        result['suggested_type'] = desc.split()[-1]
                        return result

                # Check file structure patterns
                if self.has_mp3_structure(file_path):
                    result['confidence'] = 0.7
                    result['methods'].append("MP3 structure pattern")
                    result['suggested_type'] = 'game_asset'

            except Exception as e:
                logger.warning(f"MP3 analysis error: {e}")

            return result

        def has_mp3_structure(self, file_path: str) -> bool:
            """Check for Max Payne 3 file structure patterns"""
            try:
                with open(file_path, 'rb') as f:
                    # MP3 often uses specific padding and alignment
                    data = f.read(64)
                # Look for MP3-specific patterns
                return b'\x00\x00\x00\x00MP3' in data or data[4:8] == b'MP3_'
            except Exception:
                return False

    class GTAIVProfile:
        """GTA IV (RAGE 1.0) file profile"""
       
        def analyze_file(self, file_path: str) -> Dict[str, Any]:
            path = Path(file_path)
            result = {'confidence': 0.0, 'methods': [], 'suggested_type': 'unknown'}

            # GTA IV specific patterns
            gta4_patterns = {
                b'IVB\x00': 'GTA IV binary',
                b'IVT\x00': 'GTA IV texture',
                b'IVM\x00': 'GTA IV model',
                b'RAGEIV': 'GTA IV RAGE header'
            }

            try:
                with open(file_path, 'rb') as f:
                    header = f.read(12)

                # Check GTA IV signatures
                for sig, desc in gta4_patterns.items():
                    if sig in header:
                        result['confidence'] = 0.85
                        result['methods'].append(f"GTA IV signature: {desc}")
                        result['suggested_type'] = desc.split()[-1]
                        return result

                # Extension-based detection for GTA IV
                gta4_extensions = ['.wtd', '.wdr', '.wft', '.wbn']
                if path.suffix.lower() in gta4_extensions:
                    result['confidence'] = 0.6
                    result['methods'].append("GTA IV extension match")
                    result['suggested_type'] = path.suffix[1:].upper() + ' file'

            except Exception as e:
                logger.warning(f"GTA IV analysis error: {e}")

            return result

    class MidnightClub3Profile:
        """Midnight Club 3 (Early RAGE) file profile"""
       
        def analyze_file(self, file_path: str) -> Dict[str, Any]:
            result = {'confidence': 0.0, 'methods': [], 'suggested_type': 'unknown'}

            # MC3 uses simpler, earlier RAGE format
            mc3_patterns = {
                b'MC3': 'Midnight Club 3 header',
                b'RACECAR': 'MC3 vehicle data',
                b'TRACK': 'MC3 track data'
            }

            try:
                with open(file_path, 'rb') as f:
                    header = f.read(16)

                for sig, desc in mc3_patterns.items():
                    if sig in header:
                        result['confidence'] = 0.8
                        result['methods'].append(f"MC3 signature: {desc}")
                        result['suggested_type'] = 'mc3_' + desc.split()[-1]
                        return result

                # MC3 often has specific file size patterns
                file_size = Path(file_path).stat().st_size
                if 1024 <= file_size <= 10485760:  # Common MC3 asset sizes
                    if self.has_mc3_compression_pattern(header):
                        result['confidence'] = 0.5
                        result['methods'].append("MC3 compression pattern")

            except Exception as e:
                logger.warning(f"MC3 analysis error: {e}")

            return result

        def has_mc3_compression_pattern(self, data: bytes) -> bool:
            """Check for MC3-specific compression patterns"""
            return data[:4] == b'\x78\x9C' or data[:2] == b'\x1F\x8B'  # zlib/gzip

    class RDR1Profile:
        """Red Dead Redemption 1 profile"""
       
        def analyze_file(self, file_path: str) -> Dict[str, Any]:
            result = {'confidence': 0.0, 'methods': [], 'suggested_type': 'unknown'}

            rdr1_patterns = {
                b'RDR1': 'RDR1 header',
                b'RDRT': 'RDR1 texture',
                b'RDRM': 'RDR1 model',
                b'WEST': 'RDR1 western asset'
            }

            try:
                with open(file_path, 'rb') as f:
                    header = f.read(16)

                for sig, desc in rdr1_patterns.items():
                    if sig in header:
                        result['confidence'] = 0.95
                        result['methods'].append(f"RDR1 signature: {desc}")
                        result['suggested_type'] = desc.split()[-1]
                        return result

                # RDR1 specific file structure
                if self.has_rdr1_world_pattern(header):
                    result['confidence'] = 0.7
                    result['methods'].append("RDR1 world data pattern")
                    result['suggested_type'] = 'world_data'

            except Exception as e:
                logger.warning(f"RDR1 analysis error: {e}")

            return result

        def has_rdr1_world_pattern(self, data: bytes) -> bool:
            """RDR1 world data often has specific coordinate patterns"""
            return b'\x00\x00\x80\x3F' in data or b'\x00\x00\x00\x40' in data  # Float patterns

    class GTAVProfile:
        """GTA V (RAGE 1.8) profile for comparison"""
       
        def analyze_file(self, file_path: str) -> Dict[str, Any]:
            result = {'confidence': 0.0, 'methods': [], 'suggested_type': 'unknown'}

            gta5_patterns = {
                b'RPF7': 'GTA V RPF archive',
                b'YDR\x00': 'GTA V drawable',
                b'YDD\x00': 'GTA V drawable dictionary',
                b'YFT\x00': 'GTA V fragment'
            }

            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)

                for sig, desc in gta5_patterns.items():
                    if sig in header:
                        result['confidence'] = 0.9
                        result['methods'].append(f"GTA V signature: {desc}")
                        result['suggested_type'] = desc.split()[-1]
                        return result

            except Exception as e:
                logger.warning(f"GTA V analysis error: {e}")

            return result

    def analyze_evolutionary_patterns(self, matches: List[Dict]) -> List[str]:
        """Analyze evolutionary patterns across game matches"""
        insights = []

        if len(matches) > 1:
            games = [match['game'] for match in matches]
            insights.append(f"Cross-game compatibility detected: {', '.join(games)}")

            # Check for evolutionary progression
            game_evolution = ['midnight_club_3', 'gta_iv', 'max_payne_3', 'red_dead_redemption', 'gta_v']
            matched_evolution = [game for game in game_evolution if game in games]

            if len(matched_evolution) > 1:
                insights.append(f"Evolutionary lineage: {' → '.join(matched_evolution)}")

        # Analyze confidence patterns
        high_confidence_games = [m for m in matches if m['confidence'] > 0.7]
        if high_confidence_games:
            best_match = max(high_confidence_games, key=lambda x: x['confidence'])
            insights.append(f"Best match: {best_match['game']} ({best_match['confidence']:.1%} confidence)")

        return insights

    def suggest_best_reader(self, results: Dict) -> str:
        """Suggest the best reader based on evolutionary analysis"""
        if not results['game_matches']:
            return "universal_binary_reader"

        # Prefer later engine versions (more features)
        evolution_order = {
            'gta_v': 5,
            'red_dead_redemption': 4,
            'max_payne_3': 3,
            'gta_iv': 2,
            'midnight_club_3': 1
        }

        best_game = max(results['game_matches'], key=lambda x: (x['confidence'], evolution_order.get(x['game'], 0)))
        return f"{best_game['game']}_reader"

    def record_evolutionary_learning(self, file_path: str, results: Dict):
        """Record evolutionary learning patterns"""
        learning_entry = {
            'file': file_path,
            'timestamp': datetime.datetime.now().isoformat(),
            'matches': results['game_matches'],
            'insights': results['evolutionary_insights'],
            'engine_evolution_detected': len(results['game_matches']) > 1
        }

        self.evolutionary_patterns.append(learning_entry)

        # Detect new evolutionary patterns
        if learning_entry['engine_evolution_detected']:
            self.detect_new_evolutionary_pattern(learning_entry)

    def detect_new_evolutionary_pattern(self, learning_entry: Dict):
        """Detect new evolutionary patterns across RAGE engine"""
        games = [match['game'] for match in learning_entry['matches']]
        pattern_key = '->'.join(sorted(games))

        # Check if this is a new cross-game pattern
        existing_patterns = [p.get('pattern') for p in self.cross_game_matches]
        if pattern_key not in existing_patterns:
            new_pattern = {
                'pattern': pattern_key,
                'first_seen': learning_entry['timestamp'],
                'file_type': Path(learning_entry['file']).suffix,
                'confidence_scores': {m['game']: m['confidence'] for m in learning_entry['matches']}
            }
            self.cross_game_matches.append(new_pattern)
            logger.info(f"New evolutionary pattern detected: {pattern_key}")

    def get_evolutionary_report(self) -> Dict[str, Any]:
        """Generate evolutionary learning report"""
        return {
            'total_analyses': len(self.evolutionary_patterns),
            'cross_game_matches': len(self.cross_game_matches),
            'evolutionary_patterns': self.cross_game_matches,
            'engine_timeline_coverage': self.get_engine_timeline_coverage()
        }

    def get_engine_timeline_coverage(self) -> List[str]:
        """Get RAGE engine timeline coverage"""
        timeline = [
            'Midnight Club 3 (2005) - RAGE 0.5',
            'GTA IV (2008) - RAGE 1.0',
            'Max Payne 3 (2012) - RAGE 1.2',
            'Red Dead Redemption (2010) - RAGE 1.3',
            'GTA V (2013) - RAGE 1.8'
        ]
        return timeline