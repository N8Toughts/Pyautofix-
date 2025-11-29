"""
File Signature Analyzer Plugin - Magic number and signature detection
"""

import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin 
import AnalysisPlugin


class SignatureAnalyzerPlugin(AnalysisPlugin):
    """File signature and magic number analyzer"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "SignatureAnalyzerPlugin"
        self.supported_formats = ["ALL"]  # Can analyze any file type
        self.version = "1.0.0"
        self.description = "File signature analyzer with extensive magic number database"
       
        # Extensive signature database
        self.signature_database = self._build_signature_database()
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze file signatures and magic numbers"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(4096)  # Read first 4KB for analysis
       
        results = {
            'file_path': file_path,
            'analysis_method': 'signature_analysis',
            'signature_matches': [],
            'primary_signature': None,
            'confidence_score': 0.0,
            'file_type_guesses': [],
            'byte_analysis': {},
            'header_analysis': {},
            'trailer_analysis': {}
        }
       
        # Perform signature analysis
        signature_matches = self._find_signature_matches(file_data)
        results['signature_matches'] = signature_matches
       
        if signature_matches:
            results['primary_signature'] = max(signature_matches, key=lambda x: x['confidence'])
            results['confidence_score'] = results['primary_signature']['confidence']
            results['file_type_guesses'] = self._generate_file_type_guesses(signature_matches)
       
        # Additional byte-level analysis
        results.update({
            'byte_analysis': self._analyze_bytes(file_data),
            'header_analysis': self._analyze_header(file_data),
            'trailer_analysis': self._analyze_trailer(file_path, file_data)
        })
       
        return results
   
    def _build_signature_database(self) -> List[Dict[str, Any]]:
        """Build extensive signature database"""
        signatures = []
       
        # Image formats
        signatures.extend([
            {'signature': b'\xFF\xD8\xFF', 'offset': 0, 'format': 'JPEG', 'description': 'JPEG image', 'confidence': 95},
            {'signature': b'\x89PNG\r\n\x1a\n', 'offset': 0, 'format': 'PNG', 'description': 'PNG image', 'confidence': 99},
            {'signature': b'GIF87a', 'offset': 0, 'format': 'GIF', 'description': 'GIF image (87a)', 'confidence': 95},
            {'signature': b'GIF89a', 'offset': 0, 'format': 'GIF', 'description': 'GIF image (89a)', 'confidence': 95},
            {'signature': b'BM', 'offset': 0, 'format': 'BMP', 'description': 'BMP image', 'confidence': 90},
            {'signature': b'II*\x00', 'offset': 0, 'format': 'TIFF', 'description': 'TIFF image (little-endian)', 'confidence': 90},
            {'signature': b'MM\x00*', 'offset': 0, 'format': 'TIFF', 'description': 'TIFF image (big-endian)', 'confidence': 90},
            {'signature': b'\x00\x00\x01\x00', 'offset': 0, 'format': 'ICO', 'description': 'Windows icon', 'confidence': 85},
            {'signature': b'\x00\x00\x02\x00', 'offset': 0, 'format': 'CUR', 'description': 'Windows cursor', 'confidence': 85},
        ])
       
        # Audio formats
        signatures.extend([
            {'signature': b'RIFF', 'offset': 0, 'format': 'WAV', 'description': 'Wave audio', 'confidence': 95},
            {'signature': b'ID3', 'offset': 0, 'format': 'MP3', 'description': 'MP3 audio with ID3 tag', 'confidence': 90},
            {'signature': b'OggS', 'offset': 0, 'format': 'OGG', 'description': 'Ogg Vorbis audio', 'confidence': 95},
            {'signature': b'fLaC', 'offset': 0, 'format': 'FLAC', 'description': 'Free Lossless Audio Codec', 'confidence': 95},
            {'signature': b'MThd', 'offset': 0, 'format': 'MIDI', 'description': 'MIDI audio', 'confidence': 90},
        ])
       
        # Video formats
        signatures.extend([
            {'signature': b'RIFF', 'offset': 0, 'format': 'AVI', 'description': 'AVI video', 'confidence': 90},
            {'signature': b'\x00\x00\x00 ftyp', 'offset': 4, 'format': 'MP4', 'description': 'MP4 video', 'confidence': 85},
            {'signature': b'\x00\x00\x00\x18ftyp', 'offset': 4, 'format': 'MP4', 'description': 'MP4 video', 'confidence': 85},
            {'signature': b'\x1aE\xdf\xa3', 'offset': 0, 'format': 'MKV', 'description': 'Matroska video', 'confidence': 90},
            {'signature': b'FLV', 'offset': 0, 'format': 'FLV', 'description': 'Flash video', 'confidence': 90},
        ])
       
        # Document formats
        signatures.extend([
            {'signature': b'%PDF', 'offset': 0, 'format': 'PDF', 'description': 'PDF document', 'confidence': 95},
            {'signature': b'PK\x03\x04', 'offset': 0, 'format': 'DOCX', 'description': 'ZIP-based Office document', 'confidence': 80},
            {'signature': b'PK\x03\x04', 'offset': 0, 'format': 'XLSX', 'description': 'ZIP-based Office spreadsheet', 'confidence': 80},
            {'signature': b'PK\x03\x04', 'offset': 0, 'format': 'PPTX', 'description': 'ZIP-based Office presentation', 'confidence': 80},
            {'signature': b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1', 'offset': 0, 'format': 'DOC', 'description': 'Microsoft Office document', 'confidence': 90},
            {'signature': b'{\\rtf', 'offset': 0, 'format': 'RTF', 'description': 'Rich Text Format', 'confidence': 95},
        ])
       
        # Archive formats
        signatures.extend([
            {'signature': b'PK\x03\x04', 'offset': 0, 'format': 'ZIP', 'description': 'ZIP archive', 'confidence': 95},
            {'signature': b'PK\x05\x06', 'offset': 0, 'format': 'ZIP', 'description': 'ZIP empty archive', 'confidence': 90},
            {'signature': b'PK\x07\x08', 'offset': 0, 'format': 'ZIP', 'description': 'ZIP spanned archive', 'confidence': 90},
            {'signature': b'Rar!\x1a\x07', 'offset': 0, 'format': 'RAR', 'description': 'RAR archive', 'confidence': 95},
            {'signature': b'7z\xbc\xaf\x27', 'offset': 0, 'format': '7Z', 'description': '7-Zip archive', 'confidence': 95},
            {'signature': b'\x1f\x8b', 'offset': 0, 'format': 'GZ', 'description': 'GZIP compressed file', 'confidence': 95},
            {'signature': b'BZh', 'offset': 0, 'format': 'BZ2', 'description': 'BZIP2 compressed file', 'confidence': 95},
            {'signature': b'\x1f\x9d', 'offset': 0, 'format': 'Z', 'description': 'Unix compress', 'confidence': 85},
        ])
       
        # Executable and system formats
        signatures.extend([
            {'signature': b'MZ', 'offset': 0, 'format': 'EXE', 'description': 'Windows executable', 'confidence': 95},
            {'signature': b'PE\x00\x00', 'offset': 0, 'format': 'PE', 'description': 'Portable Executable', 'confidence': 95},
            {'signature': b'ELF', 'offset': 0, 'format': 'ELF', 'description': 'Unix/Linux executable', 'confidence': 95},
            {'signature': b'#!', 'offset': 0, 'format': 'SCRIPT', 'description': 'Shell script', 'confidence': 80},
            {'signature': b'\x7fELF', 'offset': 0, 'format': 'ELF', 'description': 'ELF executable', 'confidence': 95},
        ])
       
        # Game-specific formats
        signatures.extend([
            {'signature': b'RPF', 'offset': 0, 'format': 'RPF', 'description': 'RAGE Package File', 'confidence': 95},
            {'signature': b'WTD', 'offset': 0, 'format': 'WTD', 'description': 'RAGE Texture Dictionary', 'confidence': 90},
            {'signature': b'WVD', 'offset': 0, 'format': 'WVD', 'description': 'RAGE Model File', 'confidence': 90},
            {'signature': b'WFT', 'offset': 0, 'format': 'WFT', 'description': 'RAGE Format File', 'confidence': 90},
            {'signature': b'RSC', 'offset': 0, 'format': 'RSC', 'description': 'RAGE Resource File', 'confidence': 90},
            {'signature': b'DDS', 'offset': 0, 'format': 'DDS', 'description': 'DirectDraw Surface', 'confidence': 95},
        ])
       
        # Database and data formats
        signatures.extend([
            {'signature': b'SQLite', 'offset': 0, 'format': 'SQLITE', 'description': 'SQLite database', 'confidence': 95},
            {'signature': b'\x00\x01\x00\x00', 'offset': 0, 'format': 'MDF', 'description': 'SQL Server database', 'confidence': 85},
            {'signature': b'PAR1', 'offset': 0, 'format': 'PARQUET', 'description': 'Apache Parquet', 'confidence': 90},
        ])
       
        return signatures
   
    def _find_signature_matches(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find all signature matches in file data"""
        matches = []
       
        for signature_info in self.signature_database:
            signature = signature_info['signature']
            offset = signature_info['offset']
           
            if offset + len(signature) <= len(file_data):
                if file_data[offset:offset+len(signature)] == signature:
                    matches.append(signature_info.copy())
       
        # Also check for partial matches and common patterns
        matches.extend(self._find_partial_matches(file_data))
        matches.extend(self._find_common_patterns(file_data))
       
        return matches
   
    def _find_partial_matches(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find partial signature matches"""
        partial_matches = []
       
        # Check for partial matches (at least 50% of signature)
        for sig_info in self.signature_database:
            signature = sig_info['signature']
            min_match_len = max(2, len(signature) // 2)
           
            for offset in range(0, min(100, len(file_data) - min_match_len)):
                match_len = 0
                for i in range(min_match_len):
                    if offset + i < len(file_data) and file_data[offset + i] == signature[i]:
                        match_len += 1
                    else:
                        break
               
                if match_len >= min_match_len:
                    partial_match = sig_info.copy()
                    partial_match['confidence'] = max(30, sig_info['confidence'] * match_len // len(signature))
                    partial_match['match_type'] = 'partial'
                    partial_match['match_length'] = match_len
                    partial_match['actual_offset'] = offset
                    partial_matches.append(partial_match)
       
        return partial_matches
   
    def _find_common_patterns(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find common file patterns"""
        patterns = []
       
        # Check for text files
        if self._looks_like_text(file_data):
            patterns.append({
                'format': 'TXT',
                'description': 'Text file',
                'confidence': 70,
                'match_type': 'pattern',
                'pattern': 'text_content'
            })
       
        # Check for XML
        if file_data.startswith(b'<?xml') or file_data.startswith(b'<xml'):
            patterns.append({
                'format': 'XML',
                'description': 'XML document',
                'confidence': 90,
                'match_type': 'pattern'
            })
       
        # Check for JSON
        if file_data.startswith(b'{') or file_data.startswith(b'['):
            try:
                # Quick JSON validation
                sample = file_data[:100].decode('utf-8', errors='ignore')
                if (sample.startswith('{') and sample.rstrip().endswith('}')) or \
                   (sample.startswith('[') and sample.rstrip().endswith(']')):
                    patterns.append({
                        'format': 'JSON',
                        'description': 'JSON data',
                        'confidence': 80,
                        'match_type': 'pattern'
                    })
            except:
                pass
       
        # Check for HTML
        if b'<html' in file_data[:100].lower() or b'<!DOCTYPE html' in file_data[:100].lower():
            patterns.append({
                'format': 'HTML',
                'description': 'HTML document',
                'confidence': 85,
                'match_type': 'pattern'
            })
       
        return patterns
   
    def _looks_like_text(self, file_data: bytes) -> bool:
        """Check if data looks like text"""
        if len(file_data) == 0:
            return False
       
        # Count printable ASCII characters
        printable_count = sum(1 for byte in file_data[:1000] if 32 <= byte <= 126 or byte in [9, 10, 13])
        printable_ratio = printable_count / min(1000, len(file_data))
       
        return printable_ratio > 0.95
   
    def _generate_file_type_guesses(self, signature_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate file type guesses based on signature matches"""
        guesses = []
       
        # Group by format and take the highest confidence for each
        format_groups = {}
        for match in signature_matches:
            fmt = match['format']
            if fmt not in format_groups or match['confidence'] > format_groups[fmt]['confidence']:
                format_groups[fmt] = match
       
        for fmt, match in format_groups.items():
            guesses.append({
                'format': fmt,
                'description': match['description'],
                'confidence': match['confidence'],
                'match_type': match.get('match_type', 'exact'),
                'evidence': [match['description']]
            })
       
        # Sort by confidence
        return sorted(guesses, key=lambda x: x['confidence'], reverse=True)
   
    def _analyze_bytes(self, file_data: bytes) -> Dict[str, Any]:
        """Perform byte-level analysis"""
        if len(file_data) == 0:
            return {}
       
        # Calculate entropy
        entropy = self._calculate_entropy(file_data[:4096])
       
        # Byte frequency analysis
        byte_freq = {}
        for byte in file_data[:1024]:
            byte_freq[byte] = byte_freq.get(byte, 0) + 1
       
        # Most common bytes
        common_bytes = sorted(byte_freq.items(), key=lambda x: x[1], reverse=True)[:10]
       
        return {
            'file_size_sample': len(file_data),
            'entropy': entropy,
            'entropy_interpretation': self._interpret_entropy(entropy),
            'most_common_bytes': [f"0x{b:02x} ({b}) - {count} times" for b, count in common_bytes],
            'null_byte_count': file_data.count(b'\x00'),
            'printable_ratio': self._calculate_printable_ratio(file_data),
            'is_likely_compressed': entropy > 7.5,
            'is_likely_encrypted': entropy > 7.8
        }
   
    def _analyze_header(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze file header"""
        if len(file_data) < 16:
            return {'error': 'File too small for header analysis'}
       
        header = file_data[:64]
       
        return {
            'header_hex': header.hex(),
            'header_ascii': ''.join(chr(b) if 32 <= b <= 126 else '.' for b in header),
            'byte_order_mark': self._detect_bom(header),
            'potential_offsets': self._find_potential_offsets(header),
            'magic_numbers': self._extract_magic_numbers(header)
        }
   
    def _analyze_trailer(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze file trailer (last bytes)"""
        try:
            file_size = len(file_data)
            if file_size < 16:
                return {'error': 'File too small for trailer analysis'}
           
            trailer = file_data[-32:]  # Last 32 bytes
           
            return {
                'trailer_hex': trailer.hex(),
                'trailer_ascii': ''.join(chr(b) if 32 <= b <= 126 else '.' for b in trailer),
                'end_markers': self._find_end_markers(trailer),
                'file_size_modulo': file_size % 1024,  # Common block sizes
                'has_trailer_data': any(b != 0 for b in trailer)
            }
        except Exception as e:
            return {'error': f'Trailer analysis failed: {str(e)}'}
   
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if len(data) == 0:
            return 0.0
       
        entropy = 0.0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                entropy += -p_x * (p_x.bit_length() - 1)
       
        return entropy
   
    def _interpret_entropy(self, entropy: float) -> str:
        """Interpret entropy value"""
        if entropy < 4.0:
            return "Very low (likely text or structured data)"
        elif entropy < 6.0:
            return "Low (compressed or some binary data)"
        elif entropy < 7.0:
            return "Medium (typical binary data)"
        elif entropy < 7.5:
            return "High (compressed data)"
        else:
            return "Very high (likely encrypted or random data)"
   
    def _calculate_printable_ratio(self, data: bytes) -> float:
        """Calculate ratio of printable characters"""
        if len(data) == 0:
            return 0.0
       
        printable = sum(1 for b in data if 32 <= b <= 126 or b in [9, 10, 13])
        return printable / len(data)
   
    def _detect_bom(self, data: bytes) -> str:
        """Detect Byte Order Mark"""
        bom_patterns = {
            b'\xef\xbb\xbf': 'UTF-8',
            b'\xff\xfe': 'UTF-16 LE',
            b'\xfe\xff': 'UTF-16 BE',
            b'\xff\xfe\x00\x00': 'UTF-32 LE',
            b'\x00\x00\xfe\xff': 'UTF-32 BE'
        }
       
        for bom, encoding in bom_patterns.items():
            if data.startswith(bom):
                return encoding
       
        return 'None detected'
   
    def _find_potential_offsets(self, header: bytes) -> List[Dict[str, Any]]:
        """Find potential offset values in header"""
        offsets = []
       
        # Check for common offset sizes (16, 32, 64-bit)
        for i in range(0, min(56, len(header) - 8), 4):
            # Try 32-bit little-endian
            try:
                offset_le = struct.unpack('<I', header[i:i+4])[0]
                if 0 < offset_le < 0xFFFFFF:
                    offsets.append({
                        'offset': i,
                        'value': offset_le,
                        'type': '32-bit LE',
                        'description': f'Potential offset at byte {i}'
                    })
            except:
                pass
           
            # Try 32-bit big-endian
            try:
                offset_be = struct.unpack('>I', header[i:i+4])[0]
                if 0 < offset_be < 0xFFFFFF:
                    offsets.append({
                        'offset': i,
                        'value': offset_be,
                        'type': '32-bit BE',
                        'description': f'Potential offset at byte {i}'
                    })
            except:
                pass
       
        return offsets
   
    def _extract_magic_numbers(self, header: bytes) -> List[Dict[str, Any]]:
        """Extract potential magic numbers from header"""
        magic_numbers = []
       
        # Common magic number positions
        positions = [0, 4, 8, 12, 16, 20, 24, 28]
       
        for pos in positions:
            if pos + 4 <= len(header):
                value_le = struct.unpack('<I', header[pos:pos+4])[0]
                value_be = struct.unpack('>I', header[pos:pos+4])[0]
               
                if value_le > 0:
                    magic_numbers.append({
                        'position': pos,
                        'value': value_le,
                        'endianness': 'little',
                        'hex': f'0x{value_le:08x}'
                    })
               
                if value_be > 0 and value_be != value_le:
                    magic_numbers.append({
                        'position': pos,
                        'value': value_be,
                        'endianness': 'big',
                        'hex': f'0x{value_be:08x}'
                    })
       
        return magic_numbers
   
    def _find_end_markers(self, trailer: bytes) -> List[str]:
        """Find common end markers in trailer"""
        markers = []
       
        end_patterns = {
            b'\x00\x00': 'Null padding',
            b'\xff\xff': 'All ones padding',
            b'EOF': 'EOF marker',
            b'END': 'END marker',
            b'IEND': 'PNG end chunk',
        }
       
        for pattern, description in end_patterns.items():
            if trailer.endswith(pattern):
                markers.append(description)
       
        # Check for common archive end markers
        if trailer.endswith(b'PK\x05\x06'):
            markers.append('ZIP end of central directory')
        elif trailer.endswith(b'PK\x07\x08'):
            markers.append('ZIP data descriptor')
       
        return markers