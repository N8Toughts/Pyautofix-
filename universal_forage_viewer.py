import logging
import struct
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BinaryRegion:
    """Represents a region of binary data with semantic meaning"""
    name: str
    start: int
    end: int
    data_type: str  # 'header', 'string_table', 'vertex_data', 'face_data', 'unknown'
    confidence: float
    interpretation: str

class UniversalForageViewer:
    """
    AGGRESSIVE universal file viewer that can preview ANY file
    by brute-force analysis and pattern recognition
    """
   
    def __init__(self):
        self.analysis_engines = {
            'binary_structure': self.analyze_binary_structure,
            'text_patterns': self.analyze_text_patterns,
            'geometry_detection': self.detect_geometry_data,
            'texture_detection': self.detect_texture_data,
            'archive_structure': self.analyze_archive_structure,
            'compression_detection': self.detect_compression
        }
       
        self.visualization_methods = {
            '3d_geometry': self.visualize_3d_geometry,
            'texture_preview': self.visualize_texture,
            'binary_hex': self.visualize_hex_dump,
            'data_visualization': self.visualize_data_structures,
            'archive_contents': self.visualize_archive
        }

    def aggressive_file_preview(self, file_path: str, known_format: str = None) -> Dict[str, Any]:
        """
        AGGRESSIVELY attempt to preview ANY file using multiple analysis methods
        """
        logger.info(f"🔍 Aggressive preview attempt: {file_path}")
       
        results = {
            'file_path': file_path,
            'preview_methods': [],
            'confident_previews': [],
            'speculative_previews': [],
            'binary_analysis': {},
            'recommended_viewers': []
        }
       
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
           
            # Phase 1: Multi-engine analysis
            analysis_results = self.run_all_analyses(file_data, file_path)
            results['binary_analysis'] = analysis_results
           
            # Phase 2: Attempt multiple visualization methods
            preview_attempts = self.attempt_all_visualizations(file_data, file_path, analysis_results)
           
            # Phase 3: Categorize results by confidence
            for attempt in preview_attempts:
                if attempt['confidence'] > 0.8:
                    results['confident_previews'].append(attempt)
                elif attempt['confidence'] > 0.3:
                    results['speculative_previews'].append(attempt)
                results['preview_methods'].append(attempt['method'])
           
            # Phase 4: Generate viewer recommendations
            results['recommended_viewers'] = self.generate_viewer_recommendations(analysis_results)
           
        except Exception as e:
            logger.error(f"Aggressive preview failed: {e}")
            results['error'] = str(e)
       
        return results

    def run_all_analyses(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        """Run ALL analysis engines on the file data"""
        analysis_results = {}
       
        for engine_name, engine_func in self.analysis_engines.items():
            try:
                result = engine_func(file_data, file_path)
                analysis_results[engine_name] = result
                logger.info(f"✅ {engine_name} analysis completed")
            except Exception as e:
                logger.warning(f"❌ {engine_name} analysis failed: {e}")
                analysis_results[engine_name] = {'error': str(e)}
       
        return analysis_results

    def analyze_binary_structure(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        """Analyze binary structure to identify data regions"""
        regions = []
       
        # Look for common binary patterns
        patterns = [
            (b'\x00\x00\x00\x00', 'null_padding', 0.3),
            (b'\xFF\xFF\xFF\xFF', 'padding_ffff', 0.3),
            (b'\xCD\xCD\xCD\xCD', 'debug_fill', 0.7),
            (b'\xAB\xAB\xAB\xAB', 'memory_fill', 0.6),
        ]
       
        # Identify potential headers
        header_candidates = self.find_potential_headers(file_data)
        regions.extend(header_candidates)
       
        # Look for string tables
        string_regions = self.find_string_regions(file_data)
        regions.extend(string_regions)
       
        # Look for numerical data patterns (vertices, indices, etc.)
        numerical_regions = self.find_numerical_data(file_data)
        regions.extend(numerical_regions)
       
        return {
            'total_regions': len(regions),
            'regions': sorted(regions, key=lambda x: x.start),
            'file_size': len(file_data),
            'entropy': self.calculate_entropy(file_data),
            'suspected_structure': self.infer_file_structure(regions)
        }

    def find_potential_headers(self, file_data: bytes) -> List[BinaryRegion]:
        """Find potential file headers and metadata regions"""
        regions = []
       
        # Common header sizes to check
        header_sizes = [4, 8, 16, 32, 64, 128, 256]
       
        for size in header_sizes:
            if len(file_data) >= size:
                header_data = file_data[:size]
               
                # Analyze header characteristics
                confidence = self.assess_header_confidence(header_data)
                if confidence > 0.4:
                    regions.append(BinaryRegion(
                        name=f"header_{size}",
                        start=0,
                        end=size-1,
                        data_type='header',
                        confidence=confidence,
                        interpretation=self.interpret_header(header_data)
                    ))
       
        return regions

    def assess_header_confidence(self, header_data: bytes) -> float:
        """Assess confidence that this is actually a header"""
        confidence = 0.0
       
        # Check for magic numbers/common patterns
        magic_patterns = {
            b'RIFF': 0.9, b'PNG': 0.95, b'\x89PNG': 0.98,
            b'\xFF\xD8\xFF': 0.95,  # JPEG
            b'BM': 0.9,  # BMP
            b'\x49\x49\x2A\x00': 0.9,  # TIFF little-endian
            b'\x4D\x4D\x00\x2A': 0.9,  # TIFF big-endian
        }
       
        for pattern, pattern_confidence in magic_patterns.items():
            if header_data.startswith(pattern):
                confidence = max(confidence, pattern_confidence)
       
        # Check for common game format patterns
        game_patterns = {
            b'YDR': 0.8, b'YDD': 0.8, b'YFT': 0.8,
            b'WDR': 0.8, b'WDD': 0.8, b'WFT': 0.8,
            b'RDR': 0.7, b'RDD': 0.7, b'RFT': 0.7,
            b'RPF': 0.9, b'PACK': 0.7, b'Unity': 0.8
        }
       
        for pattern, pattern_confidence in game_patterns.items():
            if pattern in header_data:
                confidence = max(confidence, pattern_confidence)
       
        # Structural analysis
        if len(header_data) >= 8:
            # Check for potential size fields
            potential_size = struct.unpack('<I', header_data[4:8])[0]
            if potential_size <= 100 * 1024 * 1024:  # Reasonable file size
                confidence = max(confidence, 0.6)
       
        return confidence

    def find_string_regions(self, file_data: bytes) -> List[BinaryRegion]:
        """Find regions containing strings and text"""
        regions = []
       
        # Look for null-terminated strings
        string_start = -1
        for i in range(len(file_data)):
            byte = file_data[i]
           
            # Printable ASCII range
            if 32 <= byte <= 126:
                if string_start == -1:
                    string_start = i
            else:
                if string_start != -1 and (i - string_start) >= 4:  # Minimum string length
                    string_length = i - string_start
                    regions.append(BinaryRegion(
                        name=f"string_at_{string_start}",
                        start=string_start,
                        end=i-1,
                        data_type='string',
                        confidence=0.7,
                        interpretation=file_data[string_start:i].decode('ascii', errors='ignore')
                    ))
                string_start = -1
       
        return regions

    def find_numerical_data(self, file_data: bytes) -> List[BinaryRegion]:
        """Find regions containing numerical data (vertices, indices, etc.)"""
        regions = []
       
        # Look for sequences of floats or integers
        candidate_regions = self.find_regular_numerical_sequences(file_data)
        regions.extend(candidate_regions)
       
        # Look for face index data (typically 3 consecutive integers)
        face_regions = self.find_face_data(file_data)
        regions.extend(face_regions)
       
        return regions

    def find_regular_numerical_sequences(self, file_data: bytes) -> List[BinaryRegion]:
        """Find regular sequences of numerical data"""
        regions = []
       
        # Try different numerical formats
        formats_to_try = [
            ('<f', 4, 'float_le'),  # Little-endian float
            ('>f', 4, 'float_be'),  # Big-endian float 
            ('<I', 4, 'uint32_le'), # Little-endian uint32
            ('>I', 4, 'uint32_be'), # Big-endian uint32
            ('<H', 2, 'uint16_le'), # Little-endian uint16
            ('>H', 2, 'uint16_be'), # Big-endian uint16
        ]
       
        for fmt, size, data_type in formats_to_try:
            sequences = self.find_regular_sequences(file_data, fmt, size)
            for seq_start, seq_length in sequences:
                if seq_length >= 3:  # Need at least 3 values to be interesting
                    regions.append(BinaryRegion(
                        name=f"{data_type}_sequence",
                        start=seq_start,
                        end=seq_start + (seq_length * size) - 1,
                        data_type='numerical_sequence',
                        confidence=0.6,
                        interpretation=f"{seq_length} {data_type} values"
                    ))
       
        return regions

    def find_regular_sequences(self, file_data: bytes, fmt: str, element_size: int) -> List[Tuple[int, int]]:
        """Find sequences of regularly formatted numerical data"""
        sequences = []
        current_seq_start = -1
        current_seq_length = 0
       
        for i in range(0, len(file_data) - element_size + 1, element_size):
            try:
                # Try to unpack the data
                chunk = file_data[i:i+element_size]
                struct.unpack(fmt, chunk)
               
                # Valid numerical data
                if current_seq_start == -1:
                    current_seq_start = i
                current_seq_length += 1
               
            except struct.error:
                # End of sequence
                if current_seq_start != -1 and current_seq_length >= 3:
                    sequences.append((current_seq_start, current_seq_length))
                current_seq_start = -1
                current_seq_length = 0
       
        # Don't forget the last sequence
        if current_seq_start != -1 and current_seq_length >= 3:
            sequences.append((current_seq_start, current_seq_length))
       
        return sequences

    def detect_geometry_data(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        """Detect 3D geometry data in unknown files"""
        geometry_indicators = {
            'vertex_count': 0,
            'face_count': 0,
            'has_normals': False,
            'has_uvs': False,
            'bounding_box': None,
            'confidence': 0.0
        }
       
        # Look for vertex data patterns
        vertex_candidates = self.find_vertex_candidates(file_data)
        if vertex_candidates:
            geometry_indicators['vertex_count'] = len(vertex_candidates)
            geometry_indicators['confidence'] += 0.3
       
        # Look for face index patterns
        face_candidates = self.find_face_candidates(file_data)
        if face_candidates:
            geometry_indicators['face_count'] = len(face_candidates)
            geometry_indicators['confidence'] += 0.3
       
        # Try to detect bounding box
        bbox = self.detect_bounding_box(file_data)
        if bbox:
            geometry_indicators['bounding_box'] = bbox
            geometry_indicators['confidence'] += 0.2
       
        return geometry_indicators

    def find_vertex_candidates(self, file_data: bytes) -> List[List[float]]:
        """Find potential vertex data in binary"""
        vertices = []
       
        # Look for sequences of 3 floats (x, y, z)
        for i in range(0, len(file_data) - 11, 4):
            try:
                x = struct.unpack('<f', file_data[i:i+4])[0]
                y = struct.unpack('<f', file_data[i+4:i+8])[0]
                z = struct.unpack('<f', file_data[i+8:i+12])[0]
               
                # Check if values are reasonable coordinates
                if -10000.0 <= x <= 10000.0 and -10000.0 <= y <= 10000.0 and -10000.0 <= z <= 10000.0:
                    vertices.append([x, y, z])
                   
            except (struct.error, IndexError):
                continue
       
        return vertices

    def find_face_candidates(self, file_data: bytes) -> List[List[int]]:
        """Find potential face index data"""
        faces = []
       
        # Look for sequences of 3 uint16 or uint32 (triangle indices)
        for i in range(0, len(file_data) - 5, 2):
            try:
                # Try uint16 first
                a = struct.unpack('<H', file_data[i:i+2])[0]
                b = struct.unpack('<H', file_data[i+2:i+4])[0]
                c = struct.unpack('<H', file_data[i+4:i+6])[0]
               
                if a < 65535 and b < 65535 and c < 65535:
                    faces.append([a, b, c])
                   
            except (struct.error, IndexError):
                continue
       
        return faces

    def detect_bounding_box(self, file_data: bytes) -> Optional[List[List[float]]]:
        """Try to detect bounding box from vertex data"""
        vertices = self.find_vertex_candidates(file_data)
       
        if not vertices:
            return None
       
        # Calculate min/max for each axis
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        min_z = min(v[2] for v in vertices)
        max_z = max(v[2] for v in vertices)
       
        return [
            [min_x, min_y, min_z],
            [max_x, max_y, max_z]
        ]

    def attempt_all_visualizations(self, file_data: bytes, file_path: str,
                                 analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Attempt ALL possible visualization methods"""
        visualizations = []
       
        for method_name, method_func in self.visualization_methods.items():
            try:
                result = method_func(file_data, file_path, analysis_results)
                visualizations.append(result)
            except Exception as e:
                logger.warning(f"Visualization {method_name} failed: {e}")
                visualizations.append({
                    'method': method_name,
                    'success': False,
                    'error': str(e),
                    'confidence': 0.0
                })
       
        return visualizations

    def visualize_3d_geometry(self, file_data: bytes, file_path: str,
                            analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to visualize as 3D geometry"""
        geometry_data = analysis_results.get('geometry_detection', {})
       
        if geometry_data.get('vertex_count', 0) > 0:
            # We found potential geometry data!
            vertices = self.find_vertex_candidates(file_data)
            faces = self.find_face_candidates(file_data)
           
            # Create simple 3D preview
            preview_data = self.create_geometry_preview(vertices, faces)
           
            return {
                'method': '3d_geometry',
                'success': True,
                'confidence': geometry_data.get('confidence', 0.5),
                'preview_type': '3d_mesh',
                'vertex_count': len(vertices),
                'face_count': len(faces),
                'bounding_box': geometry_data.get('bounding_box'),
                'preview_data': preview_data
            }
       
        return {
            'method': '3d_geometry',
            'success': False,
            'confidence': 0.0,
            'reason': 'No geometry data detected'
        }

    def create_geometry_preview(self, vertices: List[List[float]], faces: List[List[int]]) -> Dict[str, Any]:
        """Create simplified geometry preview data"""
        # Normalize vertices for better visualization
        if vertices:
            # Calculate center
            center = [0, 0, 0]
            for v in vertices:
                center[0] += v[0]
                center[1] += v[1]
                center[2] += v[2]
            center = [c / len(vertices) for c in center]
           
            # Normalize to unit sphere
            max_distance = 0.001  # Avoid division by zero
            for v in vertices:
                distance = ((v[0]-center[0])**2 + (v[1]-center[1])**2 + (v[2]-center[2])**2) ** 0.5
                max_distance = max(max_distance, distance)
           
            normalized_vertices = []
            for v in vertices:
                normalized_vertices.append([
                    (v[0] - center[0]) / max_distance,
                    (v[1] - center[1]) / max_distance,
                    (v[2] - center[2]) / max_distance
                ])
           
            return {
                'vertices': normalized_vertices,
                'faces': faces,
                'center': center,
                'scale': max_distance
            }
       
        return {'vertices': [], 'faces': []}

    def visualize_hex_dump(self, file_data: bytes, file_path: str,
                          analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create an intelligent hex dump visualization"""
        binary_analysis = analysis_results.get('binary_structure', {})
        regions = binary_analysis.get('regions', [])
       
        # Create annotated hex dump
        hex_dump = self.create_annotated_hex_dump(file_data, regions)
       
        return {
            'method': 'binary_hex',
            'success': True,
            'confidence': 0.9,  # Always works!
            'preview_type': 'hex_dump',
            'data_size': len(file_data),
            'regions_identified': len(regions),
            'hex_dump': hex_dump
        }

    def create_annotated_hex_dump(self, file_data: bytes, regions: List[BinaryRegion]) -> List[Dict[str, Any]]:
        """Create an annotated hex dump with region highlighting"""
        dump_lines = []
       
        bytes_per_line = 16
        for i in range(0, len(file_data), bytes_per_line):
            chunk = file_data[i:i+bytes_per_line]
           
            # Find which regions this line belongs to
            line_regions = []
            for region in regions:
                if i >= region.start and i < region.end:
                    line_regions.append(region.name)
           
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
           
            dump_lines.append({
                'offset': i,
                'hex': hex_part,
                'ascii': ascii_part,
                'regions': line_regions,
                'highlight': len(line_regions) > 0
            })
       
        return dump_lines

    def generate_viewer_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate aggressive viewer recommendations based on analysis"""
        recommendations = []
       
        # Based on detected data types
        if analysis_results.get('geometry_detection', {}).get('vertex_count', 0) > 0:
            recommendations.append({
                'viewer': 'Blender',
                'reason': '3D geometry data detected',
                'confidence': 0.8,
                'action': 'Import as raw vertex data'
            })
       
        if analysis_results.get('texture_detection', {}).get('is_texture', False):
            recommendations.append({
                'viewer': 'ImageMagick/Photoshop',
                'reason': 'Texture data patterns detected',
                'confidence': 0.7,
                'action': 'Try various texture formats'
            })
       
        # Always recommend hex editors
        recommendations.append({
            'viewer': 'HxD/Hex Fiend/010 Editor',
            'reason': 'Binary analysis capabilities',
            'confidence': 1.0,
            'action': 'Manual binary analysis'
        })
       
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)

    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of the data"""
        if not data:
            return 0.0
       
        entropy = 0.0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
       
        return entropy

    def infer_file_structure(self, regions: List[BinaryRegion]) -> str:
        """Infer the most likely file structure"""
        if not regions:
            return "unknown"
       
        # Count region types
        type_counts = {}
        for region in regions:
            type_counts[region.data_type] = type_counts.get(region.data_type, 0) + 1
       
        # Make inference based on region patterns
        if type_counts.get('header', 0) > 0 and type_counts.get('numerical_sequence', 0) > 10:
            return "3d_model"
        elif type_counts.get('string', 0) > 20:
            return "text_data"
        elif len(regions) == 1 and regions[0].data_type == 'header':
            return "simple_binary"
        else:
            return "structured_binary"

    # Other analysis methods would be implemented similarly...
    def analyze_text_patterns(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        return {'method': 'text_patterns', 'status': 'implemented_in_full_version'}

    def detect_texture_data(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        return {'method': 'texture_detection', 'status': 'implemented_in_full_version'}

    def analyze_archive_structure(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        return {'method': 'archive_analysis', 'status': 'implemented_in_full_version'}

    def detect_compression(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        return {'method': 'compression_detection', 'status': 'implemented_in_full_version'}

    def visualize_texture(self, file_data: bytes, file_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'method': 'texture_preview', 'status': 'implemented_in_full_version'}

    def visualize_data_structures(self, file_data: bytes, file_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'method': 'data_visualization', 'status': 'implemented_in_full_version'}

    def visualize_archive(self, file_data: bytes, file_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'method': 'archive_contents', 'status': 'implemented_in_full_version'}