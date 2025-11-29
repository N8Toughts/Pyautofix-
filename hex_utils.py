"""
Hex Utilities Plugin - Hexadecimal viewing and analysis utilities
"""

import binascii
import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin


class HexUtilsPlugin(RAGEPlugin):
    """Hexadecimal utilities for file analysis"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "HexUtilsPlugin"
        self.supported_formats = ["ALL"]
        self.version = "1.0.0"
        self.description = "Hexadecimal viewing, editing, and analysis utilities"
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze file using hex utilities"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(4096)  # Read 4KB for hex analysis
       
        results = {
            'file_path': file_path,
            'analysis_method': 'hex_analysis',
            'hex_dump': {},
            'hex_patterns': {},
            'byte_analysis': {},
            'offset_analysis': {},
            'hex_conversions': {}
        }
       
        # Perform hex analysis
        results.update({
            'hex_dump': self._generate_hex_dump(file_data),
            'hex_patterns': self._analyze_hex_patterns(file_data),
            'byte_analysis': self._analyze_bytes(file_data),
            'offset_analysis': self._analyze_offsets(file_data),
            'hex_conversions': self._perform_conversions(file_data)
        })
       
        return results
   
    def _generate_hex_dump(self, data: bytes, bytes_per_line: int = 16) -> Dict[str, Any]:
        """Generate formatted hex dump"""
        hex_dump = {
            'total_bytes': len(data),
            'lines': [],
            'summary': {}
        }
       
        try:
            for i in range(0, len(data), bytes_per_line):
                chunk = data[i:i + bytes_per_line]
               
                # Hex representation
                hex_repr = ' '.join(f'{b:02x}' for b in chunk)
                hex_repr = hex_repr.ljust(bytes_per_line * 3 - 1)
               
                # ASCII representation
                ascii_repr = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
               
                hex_dump['lines'].append({
                    'offset': i,
                    'hex': hex_repr,
                    'ascii': ascii_repr,
                    'bytes': list(chunk)
                })
           
            # Summary
            hex_dump['summary'] = {
                'total_lines': len(hex_dump['lines']),
                'bytes_per_line': bytes_per_line,
                'non_printable_count': sum(1 for b in data if b < 32 or b > 126),
                'null_byte_count': data.count(0)
            }
           
        except Exception as e:
            hex_dump['error'] = f"Hex dump generation failed: {str(e)}"
       
        return hex_dump
   
    def _analyze_hex_patterns(self, data: bytes) -> Dict[str, Any]:
        """Analyze hexadecimal patterns"""
        patterns = {
            'repeated_sequences': [],
            'common_values': [],
            'runs': [],
            'transitions': []
        }
       
        try:
            # Find repeated byte sequences
            patterns['repeated_sequences'] = self._find_repeated_hex_sequences(data)
           
            # Find common byte values
            patterns['common_values'] = self._find_common_hex_values(data)
           
            # Find runs of identical bytes
            patterns['runs'] = self._find_hex_runs(data)
           
            # Analyze byte value transitions
            patterns['transitions'] = self._analyze_hex_transitions(data)
           
        except Exception as e:
            patterns['error'] = f"Pattern analysis failed: {str(e)}"
       
        return patterns
   
    def _analyze_bytes(self, data: bytes) -> Dict[str, Any]:
        """Perform detailed byte analysis"""
        analysis = {
            'value_distribution': {},
            'bit_analysis': {},
            'endianness_hints': {},
            'alignment_checks': {}
        }
       
        try:
            # Byte value distribution
            analysis['value_distribution'] = self._analyze_byte_distribution(data)
           
            # Bit-level analysis
            analysis['bit_analysis'] = self._analyze_bits(data)
           
            # Endianness hints
            analysis['endianness_hints'] = self._detect_endianness_patterns(data)
           
            # Alignment checks
            analysis['alignment_checks'] = self._check_alignment(data)
           
        except Exception as e:
            analysis['error'] = f"Byte analysis failed: {str(e)}"
       
        return analysis
   
    def _analyze_offsets(self, data: bytes) -> Dict[str, Any]:
        """Analyze offset patterns and structures"""
        offsets = {
            'potential_pointers': [],
            'offset_clusters': [],
            'gap_analysis': {},
            'structure_hints': []
        }
       
        try:
            # Find potential pointer values
            offsets['potential_pointers'] = self._find_potential_pointers(data)
           
            # Find offset clusters
            offsets['offset_clusters'] = self._find_offset_clusters(data)
           
            # Analyze gaps between data
            offsets['gap_analysis'] = self._analyze_gaps(data)
           
            # Find structure hints
            offsets['structure_hints'] = self._find_structure_hints(data)
           
        except Exception as e:
            offsets['error'] = f"Offset analysis failed: {str(e)}"
       
        return offsets
   
    def _perform_conversions(self, data: bytes) -> Dict[str, Any]:
        """Perform various hex conversions"""
        conversions = {
            'string_representations': {},
            'numeric_conversions': {},
            'encoding_tests': {}
        }
       
        try:
            # String representations
            conversions['string_representations'] = self._generate_string_reprs(data)
           
            # Numeric conversions
            conversions['numeric_conversions'] = self._perform_numeric_conversions(data)
           
            # Encoding tests
            conversions['encoding_tests'] = self._test_encodings(data)
           
        except Exception as e:
            conversions['error'] = f"Conversion failed: {str(e)}"
       
        return conversions
   
    def hex_dump_to_string(self, data: bytes, bytes_per_line: int = 16) -> str:
        """Convert data to formatted hex dump string"""
        result = []
       
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
           
            # Offset
            offset = f"{i:08x}"
           
            # Hex bytes
            hex_bytes = ' '.join(f"{b:02x}" for b in chunk)
            hex_bytes = hex_bytes.ljust(bytes_per_line * 3 - 1)
           
            # ASCII
            ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
           
            result.append(f"{offset}  {hex_bytes}  {ascii_str}")
       
        return '\n'.join(result)
   
    def find_hex_pattern(self, data: bytes, pattern: str) -> List[int]:
        """Find hexadecimal pattern in data"""
        try:
            # Convert hex pattern to bytes
            pattern_bytes = binascii.unhexlify(pattern.replace(' ', ''))
            positions = []
           
            pos = 0
            while pos < len(data):
                found = data.find(pattern_bytes, pos)
                if found == -1:
                    break
                positions.append(found)
                pos = found + 1
           
            return positions
           
        except Exception as e:
            raise Exception(f"Pattern search failed: {str(e)}")
   
    def patch_hex_data(self, data: bytes, offset: int, new_bytes: str) -> bytes:
        """Patch hexadecimal data at specified offset"""
        try:
            # Convert hex string to bytes
            patch_data = binascii.unhexlify(new_bytes.replace(' ', ''))
           
            # Create new bytes object with patch
            result = bytearray(data)
            result[offset:offset + len(patch_data)] = patch_data
           
            return bytes(result)
           
        except Exception as e:
            raise Exception(f"Hex patching failed: {str(e)}")
   
    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        from math import log2
       
        if len(data) == 0:
            return 0.0
       
        # Count byte frequencies
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
       
        # Calculate entropy
        entropy = 0.0
        for count in freq:
            if count > 0:
                p = count / len(data)
                entropy -= p * log2(p)
       
        return entropy
   
    def _find_repeated_hex_sequences(self, data: bytes, min_length: int = 2) -> List[Dict[str, Any]]:
        """Find repeated hexadecimal sequences"""
        sequences = []
       
        for length in range(min_length, min(8, len(data) // 2)):
            sequence_count = {}
           
            for i in range(0, len(data) - length):
                sequence = data[i:i + length]
                sequence_hex = sequence.hex()
               
                if sequence_hex in sequence_count:
                    sequence_count[sequence_hex]['count'] += 1
                    sequence_count[sequence_hex]['positions'].append(i)
                else:
                    sequence_count[sequence_hex] = {
                        'sequence': sequence_hex,
                        'count': 1,
                        'positions': [i],
                        'length': length
                    }
           
            # Filter for sequences that repeat significantly
            for seq_info in sequence_count.values():
                if seq_info['count'] >= 3:
                    sequences.append(seq_info)
       
        return sorted(sequences, key=lambda x: x['count'] * x['length'], reverse=True)[:10]
   
    def _find_common_hex_values(self, data: bytes) -> List[Dict[str, Any]]:
        """Find most common byte values"""
        from collections import Counter
       
        byte_counts = Counter(data)
        common_values = []
       
        for byte_val, count in byte_counts.most_common(10):
            common_values.append({
                'byte': byte_val,
                'hex': f'{byte_val:02x}',
                'count': count,
                'percentage': (count / len(data)) * 100,
                'char': chr(byte_val) if 32 <= byte_val <= 126 else '.'
            })
       
        return common_values
   
    def _find_hex_runs(self, data: bytes) -> List[Dict[str, Any]]:
        """Find runs of identical bytes"""
        runs = []
        current_run = None
       
        for i, byte_val in enumerate(data):
            if current_run is None:
                current_run = {'byte': byte_val, 'start': i, 'length': 1}
            elif current_run['byte'] == byte_val:
                current_run['length'] += 1
            else:
                if current_run['length'] >= 4:  # Only report runs of 4+ bytes
                    runs.append(current_run.copy())
                current_run = {'byte': byte_val, 'start': i, 'length': 1}
       
        # Add final run
        if current_run and current_run['length'] >= 4:
            runs.append(current_run)
       
        return sorted(runs, key=lambda x: x['length'], reverse=True)
   
    def _analyze_hex_transitions(self, data: bytes) -> Dict[str, Any]:
        """Analyze transitions between byte values"""
        if len(data) < 2:
            return {}
       
        transitions = {
            'average_change': 0,
            'max_change': 0,
            'common_transitions': [],
            'smoothness': 0.0
        }
       
        changes = []
        transition_count = {}
       
        for i in range(1, len(data)):
            change = abs(data[i] - data[i-1])
            changes.append(change)
           
            # Track common transitions
            transition = (data[i-1], data[i])
            transition_count[transition] = transition_count.get(transition, 0) + 1
       
        if changes:
            transitions['average_change'] = sum(changes) / len(changes)
            transitions['max_change'] = max(changes)
           
            # Calculate smoothness (lower average change = smoother)
            transitions['smoothness'] = 1.0 - (transitions['average_change'] / 255.0)
       
        # Most common transitions
        common_transitions = []
        for (from_byte, to_byte), count in sorted(transition_count.items(),
                                                key=lambda x: x[1], reverse=True)[:5]:
            common_transitions.append({
                'from': f'{from_byte:02x}',
                'to': f'{to_byte:02x}',
                'count': count,
                'percentage': (count / (len(data) - 1)) * 100
            })
       
        transitions['common_transitions'] = common_transitions
       
        return transitions
   
    def _analyze_byte_distribution(self, data: bytes) -> Dict[str, Any]:
        """Analyze byte value distribution"""
        distribution = {
            'value_range': {},
            'distribution_stats': {},
            'histogram_buckets': []
        }
       
        if not data:
            return distribution
       
        # Value range
        distribution['value_range'] = {
            'min': min(data),
            'max': max(data),
            'range': max(data) - min(data)
        }
       
        # Distribution statistics
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std_dev = variance ** 0.5
       
        distribution['distribution_stats'] = {
            'mean': mean,
            'variance': variance,
            'std_deviation': std_dev,
            'entropy': self.calculate_entropy(data)
        }
       
        # Histogram buckets
        bucket_size = 16
        histogram = [0] * (256 // bucket_size)
       
        for byte_val in data:
            bucket = byte_val // bucket_size
            histogram[bucket] += 1
       
        for i, count in enumerate(histogram):
            distribution['histogram_buckets'].append({
                'range': f'{i * bucket_size:02x}-{(i + 1) * bucket_size - 1:02x}',
                'count': count,
                'percentage': (count / len(data)) * 100
            })
       
        return distribution
   
    def _analyze_bits(self, data: bytes) -> Dict[str, Any]:
        """Perform bit-level analysis"""
        bit_analysis = {
            'bit_distribution': {},
            'bit_transitions': {},
            'bit_patterns': []
        }
       
        if not data:
            return bit_analysis
       
        # Bit distribution (across all bytes)
        bit_counts = [0] * 8
        for byte_val in data:
            for bit in range(8):
                if byte_val & (1 << bit):
                    bit_counts[bit] += 1
       
        bit_analysis['bit_distribution'] = {
            'bit_0': (bit_counts[0] / len(data)) * 100,
            'bit_1': (bit_counts[1] / len(data)) * 100,
            'bit_2': (bit_counts[2] / len(data)) * 100,
            'bit_3': (bit_counts[3] / len(data)) * 100,
            'bit_4': (bit_counts[4] / len(data)) * 100,
            'bit_5': (bit_counts[5] / len(data)) * 100,
            'bit_6': (bit_counts[6] / len(data)) * 100,
            'bit_7': (bit_counts[7] / len(data)) * 100
        }
       
        # Bit transitions
        bit_changes = [0] * 8
        for i in range(1, len(data)):
            for bit in range(8):
                prev_bit = (data[i-1] >> bit) & 1
                curr_bit = (data[i] >> bit) & 1
                if prev_bit != curr_bit:
                    bit_changes[bit] += 1
       
        bit_analysis['bit_transitions'] = {
            f'bit_{i}_changes': bit_changes[i] for i in range(8)
        }
       
        return bit_analysis
   
    def _detect_endianness_patterns(self, data: bytes) -> Dict[str, Any]:
        """Detect endianness patterns in data"""
        endianness = {
            'likely_endianness': 'unknown',
            'confidence': 0,
            'evidence': []
        }
       
        if len(data) < 8:
            return endianness
       
        # Check for common little-endian patterns
        le_evidence = 0
        be_evidence = 0
       
        # Check 32-bit values
        for i in range(0, len(data) - 7, 4):
            try:
                le_val = struct.unpack('<I', data[i:i+4])[0]
                be_val = struct.unpack('>I', data[i:i+4])[0]
               
                # Little-endian often has small values in first bytes
                if le_val < 0x1000 and be_val > 0x100000:
                    le_evidence += 1
                elif be_val < 0x1000 and le_val > 0x100000:
                    be_evidence += 1
                   
            except:
                pass
       
        # Determine likely endianness
        total_checks = le_evidence + be_evidence
        if total_checks > 0:
            if le_evidence > be_evidence:
                endianness['likely_endianness'] = 'little'
                endianness['confidence'] = (le_evidence / total_checks) * 100
            else:
                endianness['likely_endianness'] = 'big'
                endianness['confidence'] = (be_evidence / total_checks) * 100
       
        endianness['evidence'] = [
            f"Little-endian patterns: {le_evidence}",
            f"Big-endian patterns: {be_evidence}"
        ]
       
        return endianness
   
    def _check_alignment(self, data: bytes) -> Dict[str, Any]:
        """Check data alignment patterns"""
        alignment = {
            'preferred_alignment': 0,
            'alignment_efficiency': 0,
            'misaligned_count': 0
        }
       
        if len(data) < 16:
            return alignment
       
        # Check alignment at different boundaries
        align_counts = {1: 0, 2: 0, 4: 0, 8: 0, 16: 0}
       
        for offset in range(min(1000, len(data))):
            for align in [2, 4, 8, 16]:
                if offset % align == 0 and data[offset] != 0:
                    align_counts[align] += 1
       
        # Find preferred alignment
        if align_counts:
            alignment['preferred_alignment'] = max(align_counts.items(), key=lambda x: x[1])[0]
           
            # Calculate efficiency
            total_checks = sum(align_counts.values())
            if total_checks > 0:
                alignment['alignment_efficiency'] = (align_counts[alignment['preferred_alignment']] / total_checks) * 100
       
        return alignment
   
    def _find_potential_pointers(self, data: bytes) -> List[Dict[str, Any]]:
        """Find potential pointer values in data"""
        pointers = []
       
        # Look for values that could be memory addresses
        for i in range(0, len(data) - 7, 4):
            try:
                # Try both endiannesses
                le_val = struct.unpack('<I', data[i:i+4])[0]
                be_val = struct.unpack('>I', data[i:i+4])[0]
               
                # Common pointer ranges
                pointer_ranges = [
                    (0x00000000, 0x00010000, "Low memory"),
                    (0x00400000, 0x10000000, "Executable range"),
                    (0x10000000, 0x80000000, "Heap/memory")
                ]
               
                for start, end, description in pointer_ranges:
                    if start <= le_val <= end:
                        pointers.append({
                            'offset': i,
                            'value': le_val,
                            'hex': f'0x{le_val:08x}',
                            'endianness': 'little',
                            'description': description
                        })
                   
                    if start <= be_val <= end:
                        pointers.append({
                            'offset': i,
                            'value': be_val,
                            'hex': f'0x{be_val:08x}',
                            'endianness': 'big',
                            'description': description
                        })
                       
            except:
                continue
       
        return pointers[:20]  # Limit results
   
    def _find_offset_clusters(self, data: bytes) -> List[Dict[str, Any]]:
        """Find clusters of offset values"""
        clusters = []
       
        # Extract potential offsets (values that point within the file)
        potential_offsets = []
       
        for i in range(0, len(data) - 3, 4):
            try:
                le_val = struct.unpack('<I', data[i:i+4])[0]
                if 0 <= le_val < len(data):
                    potential_offsets.append((i, le_val, 'little'))
               
                be_val = struct.unpack('>I', data[i:i+4])[0]
                if 0 <= be_val < len(data):
                    potential_offsets.append((i, be_val, 'big'))
                   
            except:
                continue
       
        # Group offsets by target region
        region_size = len(data) // 10
        regions = {}
       
        for src, dst, endian in potential_offsets:
            region = dst // region_size
            if region not in regions:
                regions[region] = []
            regions[region].append({
                'source_offset': src,
                'target_offset': dst,
                'endianness': endian
            })
       
        # Find significant clusters
        for region, offsets in regions.items():
            if len(offsets) >= 3:
                clusters.append({
                    'target_region': f'{region * region_size:08x}-{(region + 1) * region_size:08x}',
                    'offset_count': len(offsets),
                    'offsets': offsets[:10]  # Limit details
                })
       
        return clusters
   
    def _analyze_gaps(self, data: bytes) -> Dict[str, Any]:
        """Analyze gaps in data (runs of nulls or padding)"""
        gaps = {
            'null_gaps': [],
            'padding_gaps': [],
            'total_gap_bytes': 0,
            'gap_efficiency': 0
        }
       
        current_gap = None
       
        for i, byte_val in enumerate(data):
            if byte_val == 0x00:  # Null gap
                if current_gap is None or current_gap['type'] != 'null':
                    if current_gap:
                        gaps[current_gap['type'] + '_gaps'].append(current_gap)
                    current_gap = {'start': i, 'length': 1, 'type': 'null'}
                else:
                    current_gap['length'] += 1
                   
            elif byte_val in [0xFF, 0xCC, 0xCD]:  # Padding gaps
                if current_gap is None or current_gap['type'] != 'padding':
                    if current_gap:
                        gaps[current_gap['type'] + '_gaps'].append(current_gap)
                    current_gap = {'start': i, 'length': 1, 'type': 'padding', 'pattern': f'{byte_val:02x}'}
                else:
                    current_gap['length'] += 1
                   
            else:
                if current_gap:
                    gaps[current_gap['type'] + '_gaps'].append(current_gap)
                    gaps['total_gap_bytes'] += current_gap['length']
                current_gap = None
       
        # Add final gap
        if current_gap:
            gaps[current_gap['type'] + '_gaps'].append(current_gap)
            gaps['total_gap_bytes'] += current_gap['length']
       
        # Calculate gap efficiency
        if len(data) > 0:
            gaps['gap_efficiency'] = (gaps['total_gap_bytes'] / len(data)) * 100
       
        # Sort gaps by length
        for gap_type in ['null_gaps', 'padding_gaps']:
            gaps[gap_type] = sorted(gaps[gap_type], key=lambda x: x['length'], reverse=True)[:10]
       
        return gaps
   
    def _find_structure_hints(self, data: bytes) -> List[Dict[str, Any]]:
        """Find hints about data structure"""
        hints = []
       
        # Look for potential structure markers
        structure_patterns = [
            (b'\x00\x00\x00\x00', 'Null separator'),
            (b'\xFF\xFF\xFF\xFF', 'End marker'),
            (b'\xDE\xAD\xBE\xEF', 'Magic number'),
            (b'\xCA\xFE\xBA\xBE', 'Magic number'),
        ]
       
        for pattern, description in structure_patterns:
            pos = data.find(pattern)
            if pos != -1:
                hints.append({
                    'offset': pos,
                    'pattern': pattern.hex(),
                    'description': description,
                    'context': self._get_hex_context(data, pos, 8)
                })
       
        # Look for size fields followed by data
        for i in range(0, len(data) - 8):
            try:
                size_le = struct.unpack('<I', data[i:i+4])[0]
                if 4 <= size_le <= len(data) - i - 4:
                    hints.append({
                        'offset': i,
                        'type': 'size_field',
                        'endianness': 'little',
                        'size': size_le,
                        'description': f'Potential little-endian size field: {size_le} bytes'
                    })
               
                size_be = struct.unpack('>I', data[i:i+4])[0]
                if 4 <= size_be <= len(data) - i - 4:
                    hints.append({
                        'offset': i,
                        'type': 'size_field',
                        'endianness': 'big',
                        'size': size_be,
                        'description': f'Potential big-endian size field: {size_be} bytes'
                    })
                   
            except:
                continue
       
        return sorted(hints, key=lambda x: x['offset'])[:15]
   
    def _generate_string_reprs(self, data: bytes) -> Dict[str, Any]:
        """Generate various string representations"""
        representations = {}
       
        try:
            # Hex string
            representations['hex_string'] = data.hex()
           
            # ASCII representation (printable only)
            ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
            representations['ascii_string'] = ascii_str
           
            # Escape sequences
            escape_str = ''
            for b in data:
                if 32 <= b <= 126:
                    escape_str += chr(b)
                else:
                    escape_str += f'\\x{b:02x}'
            representations['escape_sequence'] = escape_str
           
            # Base64
            import base64
            representations['base64'] = base64.b64encode(data).decode('ascii')
           
        except Exception as e:
            representations['error'] = f"String generation failed: {str(e)}"
       
        return representations
   
    def _perform_numeric_conversions(self, data: bytes) -> Dict[str, Any]:
        """Perform numeric conversions"""
        conversions = {}
       
        try:
            # Convert first few bytes to various numeric types
            sample = data[:8]
           
            conversions['sample_data'] = sample.hex()
           
            # Unsigned integers
            if len(sample) >= 1:
                conversions['uint8'] = struct.unpack('B', sample[0:1])[0]
            if len(sample) >= 2:
                conversions['uint16_le'] = struct.unpack('<H', sample[0:2])[0]
                conversions['uint16_be'] = struct.unpack('>H', sample[0:2])[0]
            if len(sample) >= 4:
                conversions['uint32_le'] = struct.unpack('<I', sample[0:4])[0]
                conversions['uint32_be'] = struct.unpack('>I', sample[0:4])[0]
            if len(sample) >= 8:
                conversions['uint64_le'] = struct.unpack('<Q', sample[0:8])[0]
                conversions['uint64_be'] = struct.unpack('>Q', sample[0:8])[0]
           
            # Signed integers
            if len(sample) >= 1:
                conversions['int8'] = struct.unpack('b', sample[0:1])[0]
            if len(sample) >= 2:
                conversions['int16_le'] = struct.unpack('<h', sample[0:2])[0]
                conversions['int16_be'] = struct.unpack('>h', sample[0:2])[0]
            if len(sample) >= 4:
                conversions['int32_le'] = struct.unpack('<i', sample[0:4])[0]
                conversions['int32_be'] = struct.unpack('>i', sample[0:4])[0]
           
            # Floating point
            if len(sample) >= 4:
                conversions['float_le'] = struct.unpack('<f', sample[0:4])[0]
                conversions['float_be'] = struct.unpack('>f', sample[0:4])[0]
            if len(sample) >= 8:
                conversions['double_le'] = struct.unpack('<d', sample[0:8])[0]
                conversions['double_be'] = struct.unpack('>d', sample[0:8])[0]
           
        except Exception as e:
            conversions['error'] = f"Numeric conversion failed: {str(e)}"
       
        return conversions
   
    def _test_encodings(self, data: bytes) -> Dict[str, Any]:
        """Test different character encodings"""
        encodings = {}
       
        encoding_list = ['utf-8', 'latin-1', 'cp1252', 'ascii', 'utf-16-le', 'utf-16-be']
       
        for encoding in encoding_list:
            try:
                decoded = data[:100].decode(encoding, errors='strict')
                encodings[encoding] = {
                    'success': True,
                    'sample': decoded[:50],
                    'valid_chars': len([c for c in decoded if c.isprintable()])
                }
            except UnicodeDecodeError:
                encodings[encoding] = {
                    'success': False,
                    'error': 'Decode error'
                }
            except Exception as e:
                encodings[encoding] = {
                    'success': False,
                    'error': str(e)
                }
       
        return encodings
   
    def _get_hex_context(self, data: bytes, offset: int, context_bytes: int = 8) -> str:
        """Get hex context around offset"""
        start = max(0, offset - context_bytes)
        end = min(len(data), offset + context_bytes)
       
        context = data[start:end]
        return context.hex()
   
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            'hex_dump_generation',
            'pattern_analysis',
            'byte_analysis',
            'offset_analysis',
            'hex_conversions',
            'data_patching'
        ]