"""
Binary Structure Analyzer Plugin - File structure and layout analysis
"""

import struct
import binascii
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin 
import AnalysisPlugin


class StructureAnalyzerPlugin(AnalysisPlugin):
    """Binary structure and layout analyzer"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "StructureAnalyzerPlugin"
        self.supported_formats = ["ALL"]
        self.version = "1.0.0"
        self.description = "Binary structure analyzer with chunk/segment detection"
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze binary file structure"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(16384)  # Read 16KB for structure analysis
       
        results = {
            'file_path': file_path,
            'analysis_method': 'structure_analysis',
            'file_size': len(file_data),
            'structure_overview': {},
            'chunks_detected': [],
            'segments_found': [],
            'alignment_analysis': {},
            'padding_analysis': {},
            'pattern_analysis': {},
            'structural_issues': []
        }
       
        # Perform structure analysis
        results.update({
            'structure_overview': self._analyze_structure_overview(file_data),
            'chunks_detected': self._detect_chunks(file_data),
            'segments_found': self._find_segments(file_data),
            'alignment_analysis': self._analyze_alignment(file_data),
            'padding_analysis': self._analyze_padding(file_data),
            'pattern_analysis': self._analyze_patterns(file_data)
        })
       
        # Check for structural issues
        results['structural_issues'] = self._check_structural_issues(results)
       
        return results
   
    def _analyze_structure_overview(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze overall file structure"""
        file_size = len(file_data)
       
        return {
            'file_size': file_size,
            'size_category': self._categorize_size(file_size),
            'likely_structure_type': self._guess_structure_type(file_data),
            'header_present': len(file_data) >= 16,
            'trailer_present': len(file_data) >= 32,
            'estimated_chunk_count': self._estimate_chunk_count(file_data),
            'data_density': self._calculate_data_density(file_data),
            'structure_complexity': self._assess_complexity(file_data)
        }
   
    def _detect_chunks(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Detect chunks or blocks in binary data"""
        chunks = []
       
        # Look for common chunk patterns
        chunk_patterns = [
            (b'RIFF', self._analyze_riff_chunk),
            (b'FORM', self._analyze_form_chunk),
            (b'\x89PNG', self._analyze_png_chunk),
            (b'ID3', self._analyze_id3_chunk),
            (b'\x1aE\xdf\xa3', self._analyze_ebml_chunk),
        ]
       
        for pattern, analyzer in chunk_patterns:
            offset = 0
            while offset < len(file_data) - 8:
                found_offset = file_data.find(pattern, offset)
                if found_offset == -1:
                    break
               
                try:
                    chunk_info = analyzer(file_data, found_offset)
                    if chunk_info:
                        chunks.append(chunk_info)
                    offset = found_offset + len(pattern)
                except Exception as e:
                    offset = found_offset + 1
       
        # Look for generic chunk patterns (size + type)
        chunks.extend(self._find_generic_chunks(file_data))
       
        return sorted(chunks, key=lambda x: x.get('offset', 0))
   
    def _find_segments(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find segments or sections in binary data"""
        segments = []
       
        # Look for segment boundaries (abrupt changes in data)
        segments.extend(self._find_data_transitions(file_data))
       
        # Look for repeated patterns that might indicate segments
        segments.extend(self._find_repeated_structures(file_data))
       
        # Look for potential segment headers
        segments.extend(self._find_segment_headers(file_data))
       
        return sorted(segments, key=lambda x: x.get('start_offset', 0))
   
    def _analyze_alignment(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze data alignment patterns"""
        alignment_stats = {
            'common_alignments': [],
            'misaligned_data': 0,
            'preferred_alignment': 0,
            'alignment_efficiency': 0.0
        }
       
        # Check alignment at various boundaries
        alignments = {}
        for offset in range(0, min(1000, len(file_data) - 4), 4):
            if offset % 4 == 0 and file_data[offset:offset+4] != b'\x00\x00\x00\x00':
                alignments[4] = alignments.get(4, 0) + 1
            if offset % 8 == 0 and file_data[offset:offset+8] != b'\x00\x00\x00\x00\x00\x00\x00\x00':
                alignments[8] = alignments.get(8, 0) + 1
            if offset % 16 == 0 and file_data[offset:offset+16] != b'\x00' * 16:
                alignments[16] = alignments.get(16, 0) + 1
       
        if alignments:
            alignment_stats['common_alignments'] = [
                {'alignment': align, 'count': count}
                for align, count in sorted(alignments.items(), key=lambda x: x[1], reverse=True)
            ]
            alignment_stats['preferred_alignment'] = max(alignments.items(), key=lambda x: x[1])[0]
       
        return alignment_stats
   
    def _analyze_padding(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze padding patterns"""
        padding_info = {
            'total_padding_bytes': 0,
            'padding_patterns': [],
            'padding_efficiency': 0.0,
            'padding_blocks': []
        }
       
        # Common padding patterns
        padding_patterns = {
            b'\x00': 'Null padding',
            b'\xff': 'Ones padding',
            b'\xcd': 'Debug padding',
            b'\xcc': 'MSVC debug padding',
            b'\xde\xad\xbe\xef': 'Dead beef padding',
            b'\xca\xfe\xba\xbe': 'Cafe babe padding'
        }
       
        for pattern, description in padding_patterns.items():
            count = file_data.count(pattern)
            if count > len(pattern):  # More than just the pattern itself
                padding_info['padding_patterns'].append({
                    'pattern': pattern.hex(),
                    'description': description,
                    'occurrences': count // len(pattern),
                    'total_bytes': count
                })
                padding_info['total_padding_bytes'] += count
       
        # Find padding blocks (runs of identical bytes)
        padding_info['padding_blocks'] = self._find_padding_blocks(file_data)
       
        if len(file_data) > 0:
            padding_info['padding_efficiency'] = padding_info['total_padding_bytes'] / len(file_data)
       
        return padding_info
   
    def _analyze_patterns(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze data patterns and repetitions"""
        pattern_info = {
            'repeated_sequences': [],
            'common_byte_sequences': [],
            'data_regularity': 0.0,
            'pattern_diversity': 0.0
        }
       
        # Find repeated sequences
        pattern_info['repeated_sequences'] = self._find_repeated_sequences(file_data)
       
        # Find common byte sequences
        pattern_info['common_byte_sequences'] = self._find_common_sequences(file_data)
       
        # Calculate pattern metrics
        pattern_info.update(self._calculate_pattern_metrics(file_data))
       
        return pattern_info
   
    def _check_structural_issues(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for structural issues in the file"""
        issues = []
       
        chunks = analysis_results.get('chunks_detected', [])
        segments = analysis_results.get('segments_found', [])
        structure = analysis_results.get('structure_overview', {})
       
        # Check for overlapping chunks
        issue = self._check_overlapping_chunks(chunks)
        if issue:
            issues.append(issue)
       
        # Check for gaps between segments
        issue = self._check_segment_gaps(segments, structure.get('file_size', 0))
        if issue:
            issues.append(issue)
       
        # Check alignment issues
        alignment = analysis_results.get('alignment_analysis', {})
        issue = self._check_alignment_issues(alignment)
        if issue:
            issues.append(issue)
       
        # Check padding efficiency
        padding = analysis_results.get('padding_analysis', {})
        issue = self._check_padding_efficiency(padding)
        if issue:
            issues.append(issue)
       
        return issues
   
    def _analyze_riff_chunk(self, file_data: bytes, offset: int) -> Dict[str, Any]:
        """Analyze RIFF chunk structure"""
        if offset + 12 > len(file_data):
            return None
       
        chunk_id = file_data[offset:offset+4]
        chunk_size = struct.unpack('<I', file_data[offset+4:offset+8])[0]
        format_type = file_data[offset+8:offset+12]
       
        return {
            'type': 'RIFF',
            'offset': offset,
            'size': chunk_size + 8,  # Include header
            'chunk_id': chunk_id.decode('ascii', errors='ignore'),
            'format_type': format_type.decode('ascii', errors='ignore'),
            'description': f'RIFF chunk: {format_type.decode("ascii", errors="ignore")}',
            'confidence': 90
        }
   
    def _analyze_png_chunk(self, file_data: bytes, offset: int) -> Dict[str, Any]:
        """Analyze PNG chunk structure"""
        if offset + 12 > len(file_data):
            return None
       
        # PNG chunks are after the 8-byte header
        if offset == 0:
            # This is the PNG signature, look for first real chunk
            chunk_offset = 8
            if chunk_offset + 12 > len(file_data):
                return None
           
            chunk_length = struct.unpack('>I', file_data[chunk_offset:chunk_offset+4])[0]
            chunk_type = file_data[chunk_offset+4:chunk_offset+8]
           
            return {
                'type': 'PNG_CHUNK',
                'offset': chunk_offset,
                'size': chunk_length + 12,  # length + type + crc
                'chunk_type': chunk_type.decode('ascii', errors='ignore'),
                'description': f'PNG chunk: {chunk_type.decode("ascii", errors="ignore")}',
                'confidence': 85
            }
       
        return None
   
    def _analyze_id3_chunk(self, file_data: bytes, offset: int) -> Dict[str, Any]:
        """Analyze ID3 chunk structure"""
        if offset + 10 > len(file_data):
            return None
       
        version_major = file_data[offset+3]
        version_minor = file_data[offset+4]
        flags = file_data[offset+5]
        size = self._decode_sync_safe_int(file_data[offset+6:offset+10])
       
        return {
            'type': 'ID3',
            'offset': offset,
            'size': size + 10,
            'version': f'ID3v2.{version_major}.{version_minor}',
            'description': f'ID3v2 tag',
            'confidence': 80
        }
   
    def _analyze_ebml_chunk(self, file_data: bytes, offset: int) -> Dict[str, Any]:
        """Analyze EBML chunk structure (Matroska, WebM)"""
        return {
            'type': 'EBML',
            'offset': offset,
            'size': 4,
            'description': 'EBML header (Matroska/WebM)',
            'confidence': 75
        }
   
    def _analyze_form_chunk(self, file_data: bytes, offset: int) -> Dict[str, Any]:
        """Analyze FORM chunk structure (IFF files)"""
        if offset + 12 > len(file_data):
            return None
       
        chunk_size = struct.unpack('>I', file_data[offset+4:offset+8])[0]
        format_type = file_data[offset+8:offset+12]
       
        return {
            'type': 'FORM',
            'offset': offset,
            'size': chunk_size + 8,
            'format_type': format_type.decode('ascii', errors='ignore'),
            'description': f'IFF FORM chunk: {format_type.decode("ascii", errors="ignore")}',
            'confidence': 85
        }
   
    def _find_generic_chunks(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find generic chunk patterns (size + identifier)"""
        chunks = []
       
        for offset in range(0, len(file_data) - 8, 4):
            # Try to read a size field
            try:
                size_le = struct.unpack('<I', file_data[offset:offset+4])[0]
                size_be = struct.unpack('>I', file_data[offset:offset+4])[0]
               
                # Check if size seems reasonable and there's an identifier
                for size, endianness in [(size_le, 'little'), (size_be, 'big')]:
                    if 4 <= size <= len(file_data) - offset - 8:
                        # Check if next 4 bytes look like an identifier (printable ASCII)
                        id_bytes = file_data[offset+4:offset+8]
                        if self._looks_like_identifier(id_bytes):
                            chunks.append({
                                'type': 'GENERIC_CHUNK',
                                'offset': offset,
                                'size': size + 8,
                                'endianness': endianness,
                                'identifier': id_bytes.decode('ascii', errors='ignore'),
                                'description': f'Generic chunk: {id_bytes.decode("ascii", errors="ignore")}',
                                'confidence': 60
                            })
            except:
                continue
       
        return chunks
   
    def _find_data_transitions(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find transitions between different data types"""
        segments = []
        segment_start = 0
        current_type = self._classify_data_type(file_data[0:16])
       
        for i in range(16, len(file_data) - 16, 16):
            sample = file_data[i:i+16]
            data_type = self._classify_data_type(sample)
           
            if data_type != current_type:
                # Transition found
                segments.append({
                    'start_offset': segment_start,
                    'end_offset': i,
                    'size': i - segment_start,
                    'data_type': current_type,
                    'description': f'{current_type} segment',
                    'confidence': 70
                })
                segment_start = i
                current_type = data_type
       
        # Add final segment
        if segment_start < len(file_data):
            segments.append({
                'start_offset': segment_start,
                'end_offset': len(file_data),
                'size': len(file_data) - segment_start,
                'data_type': current_type,
                'description': f'{current_type} segment',
                'confidence': 70
            })
       
        return segments
   
    def _find_repeated_structures(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find repeated structural patterns"""
        segments = []
       
        # Look for repeated byte sequences that might indicate structured data
        for pattern_size in [16, 32, 64]:
            patterns = {}
            for i in range(0, len(file_data) - pattern_size, pattern_size):
                pattern = file_data[i:i+pattern_size]
                pattern_key = pattern.hex()
                patterns[pattern_key] = patterns.get(pattern_key, []) + [i]
           
            # Find patterns that repeat
            for pattern_key, positions in patterns.items():
                if len(positions) > 2:  # At least 3 occurrences
                    segments.append({
                        'start_offset': positions[0],
                        'end_offset': positions[-1] + pattern_size,
                        'size': (positions[-1] - positions[0]) + pattern_size,
                        'data_type': f'Repeated pattern ({pattern_size} bytes)',
                        'occurrences': len(positions),
                        'pattern_size': pattern_size,
                        'description': f'Repeating {pattern_size}-byte pattern ({len(positions)} occurrences)',
                        'confidence': 75
                    })
       
        return segments
   
    def _find_segment_headers(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find potential segment headers"""
        segments = []
       
        # Common header patterns
        header_patterns = [
            (b'\x7fELF', 'ELF header', 16),
            (b'MZ', 'DOS header', 64),
            (b'PE\x00\x00', 'PE header', 24),
            (b'#!', 'Shebang', 2),
        ]
       
        for pattern, description, typical_size in header_patterns:
            offset = file_data.find(pattern)
            if offset != -1:
                segments.append({
                    'start_offset': offset,
                    'end_offset': offset + typical_size,
                    'size': typical_size,
                    'data_type': 'Header',
                    'description': description,
                    'confidence': 85
                })
       
        return segments
   
    def _find_padding_blocks(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find blocks of padding bytes"""
        padding_blocks = []
        current_padding = None
       
        for i in range(len(file_data)):
            byte = file_data[i]
            if byte in [0x00, 0xFF, 0xCD, 0xCC]:  # Common padding bytes
                if current_padding is None:
                    current_padding = {'start': i, 'byte': byte, 'length': 1}
                elif current_padding['byte'] == byte:
                    current_padding['length'] += 1
                else:
                    if current_padding['length'] >= 4:  # Only report significant padding
                        padding_blocks.append(current_padding)
                    current_padding = {'start': i, 'byte': byte, 'length': 1}
            else:
                if current_padding is not None and current_padding['length'] >= 4:
                    padding_blocks.append(current_padding)
                current_padding = None
       
        # Add final padding block if exists
        if current_padding is not None and current_padding['length'] >= 4:
            padding_blocks.append(current_padding)
       
        return padding_blocks
   
    def _find_repeated_sequences(self, file_data: bytes, min_length: int = 4) -> List[Dict[str, Any]]:
        """Find repeated byte sequences"""
        sequences = []
       
        for length in range(min_length, min(32, len(file_data) // 4)):
            sequence_count = {}
           
            for i in range(0, len(file_data) - length):
                sequence = file_data[i:i+length]
                sequence_key = sequence.hex()
                sequence_count[sequence_key] = sequence_count.get(sequence_key, 0) + 1
           
            # Find sequences that repeat significantly
            for seq_key, count in sequence_count.items():
                if count >= 3 and count * length > 16:  # Meaningful repetition
                    sequences.append({
                        'length': length,
                        'occurrences': count,
                        'total_bytes': count * length,
                        'example': seq_key[:32] + '...' if len(seq_key) > 32 else seq_key,
                        'description': f'{length}-byte sequence repeated {count} times'
                    })
       
        return sorted(sequences, key=lambda x: x['total_bytes'], reverse=True)[:10]
   
    def _find_common_sequences(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find most common byte sequences"""
        from collections import Counter
       
        sequences = []
       
        # Count 2-byte sequences
        two_byte_counts = Counter()
        for i in range(len(file_data) - 1):
            two_byte_counts[file_data[i:i+2]] += 1
       
        # Count 4-byte sequences 
        four_byte_counts = Counter()
        for i in range(0, len(file_data) - 3, 4):
            four_byte_counts[file_data[i:i+4]] += 1
       
        # Get top sequences
        for seq, count in two_byte_counts.most_common(5):
            sequences.append({
                'length': 2,
                'sequence': seq.hex(),
                'count': count,
                'percentage': (count * 2 / len(file_data)) * 100
            })
       
        for seq, count in four_byte_counts.most_common(5):
            sequences.append({
                'length': 4,
                'sequence': seq.hex(),
                'count': count,
                'percentage': (count * 4 / len(file_data)) * 100
            })
       
        return sequences
   
    def _calculate_pattern_metrics(self, file_data: bytes) -> Dict[str, Any]:
        """Calculate pattern-based metrics"""
        if len(file_data) == 0:
            return {'data_regularity': 0.0, 'pattern_diversity': 0.0}
       
        # Calculate byte value distribution
        byte_counts = [0] * 256
        for byte in file_data:
            byte_counts[byte] += 1
       
        # Data regularity (how evenly bytes are distributed)
        max_count = max(byte_counts)
        regularity = 1.0 - (max_count / len(file_data)) if len(file_data) > 0 else 0.0
       
        # Pattern diversity (unique byte sequences)
        unique_sequences = len(set(file_data[i:i+4] for i in range(0, len(file_data) - 3, 4)))
        max_possible = min(256**4, len(file_data) // 4)
        diversity = unique_sequences / max_possible if max_possible > 0 else 0.0
       
        return {
            'data_regularity': regularity,
            'pattern_diversity': diversity,
            'unique_4byte_sequences': unique_sequences
        }
   
    def _check_overlapping_chunks(self, chunks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for overlapping chunks"""
        sorted_chunks = sorted(chunks, key=lambda x: x.get('offset', 0))
       
        for i in range(len(sorted_chunks) - 1):
            chunk1 = sorted_chunks[i]
            chunk2 = sorted_chunks[i + 1]
           
            end1 = chunk1.get('offset', 0) + chunk1.get('size', 0)
            start2 = chunk2.get('offset', 0)
           
            if end1 > start2:
                return {
                    'issue': 'Overlapping chunks',
                    'severity': 'Medium',
                    'description': f'Chunk at {chunk1["offset"]} overlaps with chunk at {start2}',
                    'chunk1': chunk1.get('description', 'Unknown'),
                    'chunk2': chunk2.get('description', 'Unknown')
                }
       
        return None
   
    def _check_segment_gaps(self, segments: List[Dict[str, Any]], file_size: int) -> Optional[Dict[str, Any]]:
        """Check for gaps between segments"""
        if not segments:
            return None
       
        sorted_segments = sorted(segments, key=lambda x: x.get('start_offset', 0))
       
        # Check gap at beginning
        if sorted_segments[0].get('start_offset', 0) > 0:
            return {
                'issue': 'Gap at file beginning',
                'severity': 'Low',
                'description': f'{sorted_segments[0]["start_offset"]} bytes before first segment',
                'gap_size': sorted_segments[0]['start_offset']
            }
       
        # Check gaps between segments
        for i in range(len(sorted_segments) - 1):
            end1 = sorted_segments[i].get('end_offset', 0)
            start2 = sorted_segments[i + 1].get('start_offset', 0)
           
            if start2 > end1:
                return {
                    'issue': 'Gap between segments',
                    'severity': 'Low',
                    'description': f'Gap of {start2 - end1} bytes between segments',
                    'gap_size': start2 - end1,
                    'segment1': sorted_segments[i].get('description', 'Unknown'),
                    'segment2': sorted_segments[i + 1].get('description', 'Unknown')
                }
       
        # Check gap at end
        last_segment_end = sorted_segments[-1].get('end_offset', 0)
        if last_segment_end < file_size:
            return {
                'issue': 'Gap at file end',
                'severity': 'Low',
                'description': f'{file_size - last_segment_end} bytes after last segment',
                'gap_size': file_size - last_segment_end
            }
       
        return None
   
    def _check_alignment_issues(self, alignment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for alignment issues"""
        common_alignments = alignment.get('common_alignments', [])
        if not common_alignments:
            return None
       
        primary_align = common_alignments[0]['alignment']
        primary_count = common_alignments[0]['count']
       
        # Check if alignment is inconsistent
        if len(common_alignments) > 2:
            return {
                'issue': 'Inconsistent alignment',
                'severity': 'Low',
                'description': f'Multiple alignments detected: {[a["alignment"] for a in common_alignments[:3]]}',
                'primary_alignment': primary_align,
                'alternative_alignments': [a['alignment'] for a in common_alignments[1:3]]
            }
       
        return None
   
    def _check_padding_efficiency(self, padding: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check padding efficiency issues"""
        padding_efficiency = padding.get('padding_efficiency', 0.0)
       
        if padding_efficiency > 0.3:  # More than 30% padding
            return {
                'issue': 'High padding ratio',
                'severity': 'Low',
                'description': f'{padding_efficiency:.1%} of file is padding',
                'padding_ratio': padding_efficiency,
                'total_padding_bytes': padding.get('total_padding_bytes', 0)
            }
       
        return None
   
    def _categorize_size(self, size: int) -> str:
        """Categorize file size"""
        if size < 1024:
            return "Tiny (<1KB)"
        elif size < 1024 * 1024:
            return "Small (<1MB)"
        elif size < 10 * 1024 * 1024:
            return "Medium (<10MB)"
        elif size < 100 * 1024 * 1024:
            return "Large (<100MB)"
        else:
            return "Very Large (>=100MB)"
   
    def _guess_structure_type(self, file_data: bytes) -> str:
        """Guess the type of file structure"""
        if len(file_data) < 16:
            return "Too small to determine"
       
        # Check for common structures
        if file_data.startswith(b'RIFF'):
            return "RIFF container"
        elif file_data.startswith(b'\x89PNG'):
            return "PNG with chunks"
        elif file_data.startswith(b'PK'):
            return "ZIP archive"
        elif file_data.startswith(b'MZ'):
            return "Executable with sections"
        elif file_data.startswith(b'%PDF'):
            return "PDF with objects"
       
        # Analyze data patterns
        null_ratio = file_data.count(b'\x00') / len(file_data)
        if null_ratio > 0.3:
            return "Sparse with padding"
       
        # Check for regular patterns
        if self._has_regular_patterns(file_data):
            return "Structured with regular patterns"
       
        return "Unknown or flat structure"
   
    def _estimate_chunk_count(self, file_data: bytes) -> int:
        """Estimate number of chunks in file"""
        # Count potential chunk boundaries
        boundary_count = 0
        for i in range(0, len(file_data) - 8, 4):
            if file_data[i:i+4] == b'\x00\x00\x00\x00':
                boundary_count += 1
       
        return max(1, boundary_count // 10)
   
    def _calculate_data_density(self, file_data: bytes) -> float:
        """Calculate data density (non-zero bytes ratio)"""
        if len(file_data) == 0:
            return 0.0
       
        non_zero = sum(1 for byte in file_data if byte != 0)
        return non_zero / len(file_data)
   
    def _assess_complexity(self, file_data: bytes) -> str:
        """Assess structural complexity"""
        if len(file_data) < 100:
            return "Simple"
       
        # Count unique byte patterns
        unique_patterns = len(set(file_data[i:i+8] for i in range(0, min(1000, len(file_data) - 7), 8)))
       
        if unique_patterns < 50:
            return "Simple"
        elif unique_patterns < 200:
            return "Moderate"
        else:
            return "Complex"
   
    def _looks_like_identifier(self, data: bytes) -> bool:
        """Check if data looks like an identifier (printable ASCII)"""
        if len(data) != 4:
            return False
       
        try:
            text = data.decode('ascii')
            return all(c.isalnum() or c in ' _-' for c in text)
        except:
            return False
   
    def _classify_data_type(self, data: bytes) -> str:
        """Classify type of data"""
        if len(data) == 0:
            return "Empty"
       
        # Check for all zeros
        if all(b == 0 for b in data):
            return "Zero padding"
       
        # Check for repeated pattern
        if len(set(data)) == 1:
            return "Uniform padding"
       
        # Check for text
        printable = sum(1 for b in data if 32 <= b <= 126)
        if printable / len(data) > 0.8:
            return "Text data"
       
        # Check for structured binary
        if len(data) >= 8 and data[:4] == data[4:8]:
            return "Repeated pattern"
       
        return "Binary data"
   
    def _has_regular_patterns(self, file_data: bytes) -> bool:
        """Check if file has regular patterns"""
        if len(file_data) < 32:
            return False
       
        # Check for repeating patterns at different intervals
        for interval in [4, 8, 16, 32]:
            if self._check_interval_pattern(file_data, interval):
                return True
       
        return False
   
    def _check_interval_pattern(self, file_data: bytes, interval: int) -> bool:
        """Check for patterns at specific intervals"""
        if len(file_data) < interval * 3:
            return False
       
        # Compare sequences at regular intervals
        base = file_data[:interval]
        matches = 0
        total = 0
       
        for i in range(interval, len(file_data) - interval, interval):
            if file_data[i:i+interval] == base:
                matches += 1
            total += 1
       
        return matches / total > 0.7 if total > 0 else False
   
    def _decode_sync_safe_int(self, data: bytes) -> int:
        """Decode sync-safe integer (used in ID3)"""
        value = 0
        for byte in data:
            value = (value << 7) | (byte & 0x7F)
        return value