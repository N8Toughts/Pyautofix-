"""
Heuristic Analyzer Plugin - Pattern-based file type detection
"""

import struct
import math
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin
import AnalysisPlugin


class HeuristicAnalyzerPlugin(AnalysisPlugin):
    """Heuristic file type analyzer using pattern matching"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "HeuristicAnalyzerPlugin"
        self.supported_formats = ["ALL"]
        self.version = "1.0.0"
        self.description = "Heuristic analyzer using statistical patterns and machine learning-like features"
       
        # Heuristic patterns database
        self.heuristic_patterns = self._build_heuristic_patterns()
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze file using heuristic patterns"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(8192)  # Read 8KB for heuristic analysis
       
        results = {
            'file_path': file_path,
            'analysis_method': 'heuristic_analysis',
            'heuristic_matches': [],
            'statistical_features': {},
            'pattern_scores': {},
            'confidence_metrics': {},
            'file_type_predictions': [],
            'anomaly_detection': {}
        }
       
        # Perform heuristic analysis
        results.update({
            'heuristic_matches': self._find_heuristic_matches(file_data),
            'statistical_features': self._extract_statistical_features(file_data),
            'pattern_scores': self._calculate_pattern_scores(file_data),
            'confidence_metrics': self._calculate_confidence_metrics(file_data),
            'file_type_predictions': self._predict_file_type(file_data),
            'anomaly_detection': self._detect_anomalies(file_data)
        })
       
        return results
   
    def _build_heuristic_patterns(self) -> List[Dict[str, Any]]:
        """Build database of heuristic patterns for file types"""
        patterns = []
       
        # Text files
        patterns.extend([
            {
                'file_type': 'TEXT',
                'patterns': [
                    {'type': 'byte_range', 'min': 0x20, 'max': 0x7E, 'weight': 2},  # Printable ASCII
                    {'type': 'common_chars', 'chars': [0x0A, 0x0D, 0x20], 'weight': 1},  # Newlines, spaces
                ],
                'threshold': 0.8,
                'description': 'Plain text file'
            },
            {
                'file_type': 'XML',
                'patterns': [
                    {'type': 'string_match', 'string': '<?xml', 'weight': 10},
                    {'type': 'tag_pattern', 'weight': 5},
                ],
                'threshold': 0.7,
                'description': 'XML document'
            },
            {
                'file_type': 'JSON',
                'patterns': [
                    {'type': 'first_byte', 'byte': 0x7B, 'weight': 5},  # {
                    {'type': 'first_byte', 'byte': 0x5B, 'weight': 5},  # [
                    {'type': 'structure_match', 'pattern': 'balanced_braces', 'weight': 8},
                ],
                'threshold': 0.6,
                'description': 'JSON data'
            }
        ])
       
        # Executable files
        patterns.extend([
            {
                'file_type': 'EXE_WIN',
                'patterns': [
                    {'type': 'string_match', 'string': 'MZ', 'weight': 10},
                    {'type': 'string_match', 'string': 'PE', 'weight': 10},
                    {'type': 'byte_pattern', 'pattern': [0x4D, 0x5A], 'weight': 8},
                ],
                'threshold': 0.9,
                'description': 'Windows executable'
            },
            {
                'file_type': 'ELF',
                'patterns': [
                    {'type': 'string_match', 'string': 'ELF', 'weight': 10},
                    {'type': 'byte_pattern', 'pattern': [0x7F, 0x45, 0x4C, 0x46], 'weight': 10},
                ],
                'threshold': 0.9,
                'description': 'ELF executable'
            }
        ])
       
        # Archive files
        patterns.extend([
            {
                'file_type': 'ZIP',
                'patterns': [
                    {'type': 'string_match', 'string': 'PK', 'weight': 10},
                    {'type': 'byte_pattern', 'pattern': [0x50, 0x4B, 0x03, 0x04], 'weight': 10},
                ],
                'threshold': 0.95,
                'description': 'ZIP archive'
            },
            {
                'file_type': 'RAR',
                'patterns': [
                    {'type': 'string_match', 'string': 'Rar!', 'weight': 10},
                    {'type': 'byte_pattern', 'pattern': [0x52, 0x61, 0x72, 0x21], 'weight': 10},
                ],
                'threshold': 0.95,
                'description': 'RAR archive'
            }
        ])
       
        # Image files
        patterns.extend([
            {
                'file_type': 'JPEG',
                'patterns': [
                    {'type': 'byte_pattern', 'pattern': [0xFF, 0xD8, 0xFF], 'weight': 10},
                    {'type': 'string_match', 'string': 'JFIF', 'weight': 5},
                ],
                'threshold': 0.9,
                'description': 'JPEG image'
            },
            {
                'file_type': 'PNG',
                'patterns': [
                    {'type': 'byte_pattern', 'pattern': [0x89, 0x50, 0x4E, 0x47], 'weight': 10},
                    {'type': 'string_match', 'string': 'IHDR', 'weight': 5},
                ],
                'threshold': 0.95,
                'description': 'PNG image'
            }
        ])
       
        # Document files
        patterns.extend([
            {
                'file_type': 'PDF',
                'patterns': [
                    {'type': 'string_match', 'string': '%PDF', 'weight': 10},
                    {'type': 'string_match', 'string': '%%EOF', 'weight': 5},
                ],
                'threshold': 0.9,
                'description': 'PDF document'
            },
            {
                'file_type': 'DOC',
                'patterns': [
                    {'type': 'byte_pattern', 'pattern': [0xD0, 0xCF, 0x11, 0xE0], 'weight': 10},
                ],
                'threshold': 0.8,
                'description': 'Microsoft Word document'
            }
        ])
       
        return patterns
   
    def _find_heuristic_matches(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find heuristic pattern matches"""
        matches = []
       
        for pattern_set in self.heuristic_patterns:
            file_type = pattern_set['file_type']
            total_weight = 0
            matched_weight = 0
            matched_patterns = []
           
            for pattern in pattern_set['patterns']:
                weight = pattern['weight']
                total_weight += weight
               
                if self._check_pattern(file_data, pattern):
                    matched_weight += weight
                    matched_patterns.append({
                        'type': pattern['type'],
                        'weight': weight,
                        'description': self._describe_pattern(pattern)
                    })
           
            if total_weight > 0:
                score = matched_weight / total_weight
                if score >= pattern_set['threshold']:
                    matches.append({
                        'file_type': file_type,
                        'score': score,
                        'confidence': min(100, int(score * 100)),
                        'description': pattern_set['description'],
                        'matched_patterns': matched_patterns,
                        'total_patterns': len(pattern_set['patterns']),
                        'threshold': pattern_set['threshold']
                    })
       
        return sorted(matches, key=lambda x: x['score'], reverse=True)
   
    def _extract_statistical_features(self, file_data: bytes) -> Dict[str, Any]:
        """Extract statistical features from file data"""
        if len(file_data) == 0:
            return {}
       
        # Byte value distribution
        byte_counts = [0] * 256
        for byte in file_data:
            byte_counts[byte] += 1
       
        # Calculate entropy
        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                p = count / len(file_data)
                entropy -= p * math.log2(p)
       
        # Statistical moments
        mean = sum(i * count for i, count in enumerate(byte_counts)) / len(file_data)
        variance = sum((i - mean) ** 2 * count for i, count in enumerate(byte_counts)) / len(file_data)
        std_dev = math.sqrt(variance)
       
        # Skewness and kurtosis
        if std_dev > 0:
            skewness = sum((i - mean) ** 3 * count for i, count in enumerate(byte_counts)) / (len(file_data) * std_dev ** 3)
            kurtosis = sum((i - mean) ** 4 * count for i, count in enumerate(byte_counts)) / (len(file_data) * std_dev ** 4) - 3
        else:
            skewness = 0
            kurtosis = 0
       
        return {
            'entropy': entropy,
            'mean_byte_value': mean,
            'std_deviation': std_dev,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'byte_distribution': self._summarize_byte_distribution(byte_counts),
            'most_common_byte': byte_counts.index(max(byte_counts)),
            'least_common_byte': byte_counts.index(min(byte_counts)),
            'null_byte_ratio': byte_counts[0] / len(file_data),
            'printable_ratio': sum(byte_counts[32:127]) / len(file_data)
        }
   
    def _calculate_pattern_scores(self, file_data: bytes) -> Dict[str, Any]:
        """Calculate various pattern-based scores"""
        scores = {}
       
        # Repetition score
        scores['repetition_score'] = self._calculate_repetition_score(file_data)
       
        # Regularity score
        scores['regularity_score'] = self._calculate_regularity_score(file_data)
       
        # Compression score (how compressible the data appears)
        scores['compression_score'] = self._calculate_compression_score(file_data)
       
        # Randomness score
        scores['randomness_score'] = self._calculate_randomness_score(file_data)
       
        # Structure score
        scores['structure_score'] = self._calculate_structure_score(file_data)
       
        return scores
   
    def _calculate_confidence_metrics(self, file_data: bytes) -> Dict[str, Any]:
        """Calculate confidence metrics for analysis"""
        features = self._extract_statistical_features(file_data)
        pattern_scores = self._calculate_pattern_scores(file_data)
       
        return {
            'data_quality_score': self._calculate_data_quality(features),
            'analysis_reliability': self._calculate_reliability(features, pattern_scores),
            'sample_adequacy': min(100, int((len(file_data) / 8192) * 100)),  # Based on 8KB sample
            'feature_stability': self._assess_feature_stability(file_data),
            'pattern_consistency': self._assess_pattern_consistency(file_data)
        }
   
    def _predict_file_type(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Predict file type based on combined heuristics"""
        predictions = []
       
        # Get heuristic matches
        heuristic_matches = self._find_heuristic_matches(file_data)
       
        # Get statistical predictions
        statistical_predictions = self._statistical_file_type_prediction(file_data)
       
        # Combine predictions
        all_predictions = {}
       
        for match in heuristic_matches:
            file_type = match['file_type']
            score = match['score'] * 0.7  # Heuristic weight
            all_predictions[file_type] = all_predictions.get(file_type, 0) + score
       
        for stat_pred in statistical_predictions:
            file_type = stat_pred['file_type']
            score = stat_pred['confidence'] * 0.3  # Statistical weight
            all_predictions[file_type] = all_predictions.get(file_type, 0) + score
       
        # Convert to list and sort
        for file_type, score in all_predictions.items():
            predictions.append({
                'file_type': file_type,
                'combined_score': score,
                'confidence': min(100, int(score * 100)),
                'method': 'combined_heuristic'
            })
       
        return sorted(predictions, key=lambda x: x['combined_score'], reverse=True)[:5]
   
    def _detect_anomalies(self, file_data: bytes) -> Dict[str, Any]:
        """Detect anomalies in file data"""
        anomalies = []
       
        # Check for unexpected patterns
        if self._has_suspicious_patterns(file_data):
            anomalies.append({
                'type': 'Suspicious patterns',
                'severity': 'Medium',
                'description': 'Contains patterns commonly found in obfuscated or malicious files'
            })
       
        # Check entropy anomalies
        features = self._extract_statistical_features(file_data)
        if features['entropy'] > 7.8:
            anomalies.append({
                'type': 'High entropy',
                'severity': 'High',
                'description': 'Very high entropy suggests encrypted or compressed data'
            })
        elif features['entropy'] < 2.0:
            anomalies.append({
                'type': 'Low entropy',
                'severity': 'Low',
                'description': 'Very low entropy suggests repetitive or structured data'
            })
       
        # Check file size anomalies
        if 0 < len(file_data) < 16:
            anomalies.append({
                'type': 'Very small file',
                'severity': 'Low',
                'description': 'File is unusually small for meaningful analysis'
            })
       
        # Check for mixed content
        if self._has_mixed_content(file_data):
            anomalies.append({
                'type': 'Mixed content',
                'severity': 'Medium',
                'description': 'File contains both text and binary data patterns'
            })
       
        return {
            'anomalies_detected': anomalies,
            'total_anomalies': len(anomalies),
            'risk_level': self._assess_risk_level(anomalies)
        }
   
    def _check_pattern(self, file_data: bytes, pattern: Dict[str, Any]) -> bool:
        """Check if file data matches a specific pattern"""
        pattern_type = pattern['type']
       
        if pattern_type == 'byte_range':
            min_val = pattern['min']
            max_val = pattern['max']
            printable_count = sum(1 for byte in file_data if min_val <= byte <= max_val)
            ratio = printable_count / len(file_data)
            return ratio > 0.8  # 80% of bytes in range
       
        elif pattern_type == 'common_chars':
            chars = pattern['chars']
            common_count = sum(file_data.count(bytes([char])) for char in chars)
            return common_count > len(file_data) * 0.1  # 10% of bytes are common chars
       
        elif pattern_type == 'string_match':
            string = pattern['string'].encode('ascii')
            return file_data.startswith(string)
       
        elif pattern_type == 'first_byte':
            return file_data[0] == pattern['byte'] if len(file_data) > 0 else False
       
        elif pattern_type == 'byte_pattern':
            pattern_bytes = pattern['pattern']
            return file_data.startswith(bytes(pattern_bytes))
       
        elif pattern_type == 'tag_pattern':
            # Check for XML-like tags
            return b'<' in file_data and b'>' in file_data
       
        elif pattern_type == 'structure_match':
            if pattern['pattern'] == 'balanced_braces':
                return self._check_balanced_braces(file_data)
       
        return False
   
    def _calculate_repetition_score(self, file_data: bytes) -> float:
        """Calculate repetition score (0-1)"""
        if len(file_data) < 8:
            return 0.0
       
        # Check for repeated sequences
        unique_4byte = len(set(file_data[i:i+4] for i in range(0, len(file_data) - 3, 4)))
        max_unique = min(256**4, len(file_data) // 4)
       
        return 1.0 - (unique_4byte / max_unique)
   
    def _calculate_regularity_score(self, file_data: bytes) -> float:
        """Calculate regularity score (0-1)"""
        if len(file_data) < 32:
            return 0.0
       
        # Check for regular patterns at different intervals
        regularity_count = 0
        intervals = [4, 8, 16, 32]
       
        for interval in intervals:
            if self._check_regular_interval(file_data, interval):
                regularity_count += 1
       
        return regularity_count / len(intervals)
   
    def _calculate_compression_score(self, file_data: bytes) -> float:
        """Calculate compression score (0-1)"""
        features = self._extract_statistical_features(file_data)
        entropy = features['entropy']
       
        # Normalize entropy to 0-1 scale (assuming max 8.0 for random data)
        return min(1.0, entropy / 8.0)
   
    def _calculate_randomness_score(self, file_data: bytes) -> float:
        """Calculate randomness score (0-1)"""
        features = self._extract_statistical_features(file_data)
       
        # High entropy + low skewness + low kurtosis = more random
        entropy_factor = features['entropy'] / 8.0
        skewness_factor = 1.0 - min(1.0, abs(features['skewness']) / 2.0)
        kurtosis_factor = 1.0 - min(1.0, abs(features['kurtosis']) / 10.0)
       
        return (entropy_factor + skewness_factor + kurtosis_factor) / 3.0
   
    def _calculate_structure_score(self, file_data: bytes) -> float:
        """Calculate structure score (0-1)"""
        pattern_scores = self._calculate_pattern_scores(file_data)
       
        # Low repetition + medium regularity = more structured
        repetition = pattern_scores['repetition_score']
        regularity = pattern_scores['regularity_score']
       
        # Structured data typically has medium regularity and low repetition
        structure_indicator = (1.0 - repetition) * regularity
       
        return structure_indicator
   
    def _calculate_data_quality(self, features: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)"""
        # Good quality data has reasonable entropy and distribution
        entropy_score = 1.0 - abs(features['entropy'] - 4.0) / 4.0  # Ideal around 4.0
        distribution_score = 1.0 - features['skewness'] / 2.0 if abs(features['skewness']) < 2.0 else 0.0
       
        return (entropy_score + distribution_score) / 2.0
   
    def _calculate_reliability(self, features: Dict[str, Any], pattern_scores: Dict[str, Any]) -> float:
        """Calculate analysis reliability score (0-1)"""
        # Reliability is higher when features are consistent and patterns are clear
        consistency_score = 1.0 - features['std_deviation'] / 128.0  # Normalize std dev
        clarity_score = pattern_scores['structure_score']
       
        return (consistency_score + clarity_score) / 2.0
   
    def _assess_feature_stability(self, file_data: bytes) -> float:
        """Assess stability of features across file segments"""
        if len(file_data) < 100:
            return 0.5  # Not enough data
       
        # Compare features from different segments
        segment_size = len(file_data) // 4
        entropies = []
       
        for i in range(4):
            segment = file_data[i*segment_size:(i+1)*segment_size]
            if len(segment) > 0:
                features = self._extract_statistical_features(segment)
                entropies.append(features['entropy'])
       
        if len(entropies) < 2:
            return 0.5
       
        # Calculate coefficient of variation
        mean_entropy = sum(entropies) / len(entropies)
        if mean_entropy == 0:
            return 0.5
       
        std_entropy = math.sqrt(sum((e - mean_entropy) ** 2 for e in entropies) / len(entropies))
        cv = std_entropy / mean_entropy
       
        return 1.0 - min(1.0, cv)  # Lower variation = higher stability
   
    def _assess_pattern_consistency(self, file_data: bytes) -> float:
        """Assess consistency of patterns throughout file"""
        if len(file_data) < 200:
            return 0.5
       
        # Check if patterns are consistent in different segments
        segment_size = len(file_data) // 4
        consistent_patterns = 0
        total_patterns = 0
       
        for pattern_set in self.heuristic_patterns[:10]:  # Check first 10 pattern sets
            segment_matches = []
           
            for i in range(4):
                segment = file_data[i*segment_size:(i+1)*segment_size]
                if len(segment) > 0:
                    match = any(self._check_pattern(segment, pattern) for pattern in pattern_set['patterns'])
                    segment_matches.append(match)
           
            # Count how many segments agree
            if len(segment_matches) >= 2:
                agreement = sum(segment_matches) / len(segment_matches)
                if agreement > 0.7 or agreement < 0.3:  # Either mostly true or mostly false
                    consistent_patterns += 1
                total_patterns += 1
       
        return consistent_patterns / total_patterns if total_patterns > 0 else 0.5
   
    def _statistical_file_type_prediction(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Predict file type based on statistical features"""
        features = self._extract_statistical_features(file_data)
        predictions = []
       
        # Simple rule-based statistical classifier
        entropy = features['entropy']
        printable_ratio = features['printable_ratio']
        null_ratio = features['null_byte_ratio']
       
        if printable_ratio > 0.9:
            predictions.append({'file_type': 'TEXT', 'confidence': 0.8})
        elif entropy > 7.5:
            predictions.append({'file_type': 'ENCRYPTED', 'confidence': 0.7})
            predictions.append({'file_type': 'COMPRESSED', 'confidence': 0.6})
        elif null_ratio > 0.3:
            predictions.append({'file_type': 'SPARSE', 'confidence': 0.6})
        elif 4.0 < entropy < 6.0:
            predictions.append({'file_type': 'STRUCTURED_BINARY', 'confidence': 0.5})
       
        return predictions
   
    def _has_suspicious_patterns(self, file_data: bytes) -> bool:
        """Check for suspicious patterns"""
        suspicious_patterns = [
            b'\x90' * 16,  # NOP sled
            b'\x00' * 16,  # Large null padding
            b'\xFF' * 16,  # Large ones padding
            b'\xCC' * 8,   # Debug breakpoints
        ]
       
        return any(pattern in file_data for pattern in suspicious_patterns)
   
    def _has_mixed_content(self, file_data: bytes) -> bool:
        """Check for mixed text/binary content"""
        if len(file_data) < 100:
            return False
       
        # Check first and second halves for different characteristics
        half = len(file_data) // 2
        first_half = file_data[:half]
        second_half = file_data[half:]
       
        first_printable = sum(1 for byte in first_half if 32 <= byte <= 126) / len(first_half)
        second_printable = sum(1 for byte in second_half if 32 <= byte <= 126) / len(second_half)
       
        # Significant difference in printable character ratio
        return abs(first_printable - second_printable) > 0.4
   
    def _assess_risk_level(self, anomalies: List[Dict[str, Any]]) -> str:
        """Assess overall risk level based on anomalies"""
        if not anomalies:
            return 'None'
       
        severities = [anomaly['severity'] for anomaly in anomalies]
       
        if 'High' in severities:
            return 'High'
        elif 'Medium' in severities:
            return 'Medium'
        else:
            return 'Low'
   
    def _summarize_byte_distribution(self, byte_counts: List[int]) -> Dict[str, float]:
        """Summarize byte value distribution"""
        total = sum(byte_counts)
        if total == 0:
            return {}
       
        return {
            'null_bytes': byte_counts[0] / total,
            'printable_ascii': sum(byte_counts[32:127]) / total,
            'control_chars': sum(byte_counts[0:32]) / total + byte_counts[127] / total,
            'high_bytes': sum(byte_counts[128:256]) / total
        }
   
    def _check_balanced_braces(self, file_data: bytes) -> bool:
        """Check if braces are balanced (for JSON detection)"""
        try:
            text = file_data.decode('utf-8', errors='ignore')
            stack = []
           
            for char in text:
                if char == '{' or char == '[':
                    stack.append(char)
                elif char == '}':
                    if not stack or stack.pop() != '{':
                        return False
                elif char == ']':
                    if not stack or stack.pop() != '[':
                        return False
           
            return len(stack) == 0
        except:
            return False
   
    def _check_regular_interval(self, file_data: bytes, interval: int) -> bool:
        """Check for regular patterns at specific interval"""
        if len(file_data) < interval * 3:
            return False
       
        base = file_data[:interval]
        matches = 0
        checks = 0
       
        for i in range(interval, len(file_data) - interval, interval):
            if file_data[i:i+interval] == base:
                matches += 1
            checks += 1
       
        return matches / checks > 0.6 if checks > 0 else False
   
    def _describe_pattern(self, pattern: Dict[str, Any]) -> str:
        """Generate description for a pattern"""
        pattern_type = pattern['type']
       
        if pattern_type == 'byte_range':
            return f"Bytes in range 0x{pattern['min']:02x}-0x{pattern['max']:02x}"
        elif pattern_type == 'common_chars':
            return f"Common characters: {[chr(c) for c in pattern['chars']]}"
        elif pattern_type == 'string_match':
            return f"Starts with: {pattern['string']}"
        elif pattern_type == 'first_byte':
            return f"First byte: 0x{pattern['byte']:02x}"
        elif pattern_type == 'byte_pattern':
            return f"Byte pattern: {[hex(b) for b in pattern['pattern']]}"
        elif pattern_type == 'tag_pattern':
            return "XML-like tag structure"
        elif pattern_type == 'structure_match':
            return f"Structure: {pattern['pattern']}"
       
        return "Unknown pattern"