"""
Archive Format Analyzer Plugin - RPF, ZIP, and other archive formats
"""

import struct
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin 
import FormatPlugin


class ArchiveAnalyzerPlugin(FormatPlugin):
    """Archive format analyzer (RPF, ZIP, etc.)"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "ArchiveAnalyzerPlugin"
        self.supported_formats = ["RPF", "ZIP", "RAR", "7Z", "TAR", "GZ", "BZ2"]
        self.version = "1.0.0"
        self.description = "Archive format analyzer with content extraction and structure analysis"
       
        # Archive format signatures
        self.format_signatures = [
            b'RPF',           # RAGE Package File
            b'PK\x03\x04',    # ZIP format
            b'PK\x05\x06',    # ZIP empty archive
            b'PK\x07\x08',    # ZIP spanned archive
            b'Rar!\x1a\x07',  # RAR format
            b'7z\xbc\xaf\x27', # 7-Zip format
            b'\x1f\x8b',      # GZIP format
            b'BZh',           # BZIP2 format
        ]
       
        # RPF constants
        self.RPF_MAGIC = b'RPF'
        self.RPF_VERSION = 7
   
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze archive file"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(8192)  # Read first 8KB for analysis
       
        results = {
            'file_path': file_path,
            'format_type': self._detect_archive_format(file_data),
            'analysis_method': 'archive_plugin',
            'is_archive': True,
            'archive_structure': {},
            'content_analysis': {},
            'compression_info': {},
            'security_info': {},
            'compatibility': {},
            'issues': []
        }
       
        # Perform format-specific analysis
        format_type = results['format_type']
        if format_type == 'RPF':
            results.update(self._analyze_rpf(file_path, file_data))
        elif format_type == 'ZIP':
            results.update(self._analyze_zip(file_path, file_data))
        elif format_type in ['RAR', '7Z']:
            results.update(self._analyze_compressed_archive(file_path, file_data, format_type))
        else:
            results.update(self._analyze_generic_archive(file_path, file_data))
       
        return results
   
    def _detect_archive_format(self, file_data: bytes) -> str:
        """Detect archive format"""
        if file_data.startswith(self.RPF_MAGIC):
            return 'RPF'
        elif file_data.startswith(b'PK'):
            return 'ZIP'
        elif file_data.startswith(b'Rar!'):
            return 'RAR'
        elif file_data.startswith(b'7z'):
            return '7Z'
        elif file_data.startswith(b'\x1f\x8b'):
            return 'GZ'
        elif file_data.startswith(b'BZh'):
            return 'BZ2'
        else:
            return 'Unknown Archive'
   
    def _analyze_rpf(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze RPF (RAGE Package File) format"""
        archive_info = {
            'format': 'RPF',
            'version': 0,
            'entry_count': 0,
            'file_count': 0,
            'directory_count': 0,
            'total_uncompressed_size': 0,
            'total_compressed_size': 0,
            'encryption_type': 'None',
            'is_encrypted': False,
            'toc_offset': 0,
            'toc_size': 0,
            'entries': []
        }
       
        try:
            if len(file_data) >= 24:
                # Parse RPF header
                magic = file_data[0:4]
                if magic.startswith(self.RPF_MAGIC):
                    version = struct.unpack('<I', file_data[4:8])[0]
                    toc_offset = struct.unpack('<Q', file_data[8:16])[0]
                    toc_size = struct.unpack('<Q', file_data[16:24])[0]
                   
                    archive_info.update({
                        'version': version,
                        'toc_offset': toc_offset,
                        'toc_size': toc_size,
                        'entry_count': toc_size // 16  # Rough estimate
                    })
                   
                    # Analyze entries if we have more data
                    if len(file_data) > toc_offset + 100:
                        archive_info['entries'] = self._extract_rpf_entries(file_data, toc_offset, toc_size)
           
        except Exception as e:
            archive_info['error'] = f"RPF analysis failed: {str(e)}"
       
        return {
            'archive_structure': archive_info,
            'content_analysis': self._analyze_rpf_content(archive_info),
            'compression_info': self._get_rpf_compression_info(archive_info),
            'security_info': self._get_rpf_security_info(archive_info)
        }
   
    def _analyze_zip(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze ZIP archive format"""
        archive_info = {
            'format': 'ZIP',
            'version_needed': 0,
            'general_purpose_flags': 0,
            'compression_method': 0,
            'file_count': 0,
            'central_directory_offset': 0,
            'comment_length': 0,
            'is_encrypted': False,
            'has_data_descriptors': False,
            'uses_zip64': False,
            'entries': []
        }
       
        try:
            # Find end of central directory record
            eocd_offset = file_data.rfind(b'PK\x05\x06')
            if eocd_offset != -1 and len(file_data) >= eocd_offset + 22:
                eocd = file_data[eocd_offset:eocd_offset+22]
               
                file_count = struct.unpack('<H', eocd[10:12])[0]
                central_dir_size = struct.unpack('<I', eocd[12:16])[0]
                central_dir_offset = struct.unpack('<I', eocd[16:20])[0]
                comment_length = struct.unpack('<H', eocd[20:22])[0]
               
                archive_info.update({
                    'file_count': file_count,
                    'central_directory_offset': central_dir_offset,
                    'central_directory_size': central_dir_size,
                    'comment_length': comment_length
                })
               
                # Check for ZIP64
                if file_count == 0xFFFF or central_dir_offset == 0xFFFFFFFF:
                    archive_info['uses_zip64'] = True
               
                # Extract file entries
                archive_info['entries'] = self._extract_zip_entries(file_data, central_dir_offset, file_count)
               
                # Check encryption
                if archive_info['entries']:
                    first_entry = archive_info['entries'][0]
                    archive_info['is_encrypted'] = first_entry.get('is_encrypted', False)
           
        except Exception as e:
            archive_info['error'] = f"ZIP analysis failed: {str(e)}"
       
        return {
            'archive_structure': archive_info,
            'content_analysis': self._analyze_zip_content(archive_info),
            'compression_info': self._get_zip_compression_info(archive_info),
            'security_info': self._get_zip_security_info(archive_info)
        }
   
    def _analyze_compressed_archive(self, file_path: str, file_data: bytes, format_type: str) -> Dict[str, Any]:
        """Analyze compressed archive formats (RAR, 7Z)"""
        archive_info = {
            'format': format_type,
            'version': 'Unknown',
            'file_count': 0,
            'is_encrypted': False,
            'compression_method': 'Unknown',
            'solid_archive': False,
            'recovery_record': False,
            'volume_number': 0
        }
       
        try:
            if format_type == 'RAR':
                # Basic RAR header analysis
                if len(file_data) >= 10:
                    head_crc = struct.unpack('<H', file_data[6:8])[0]
                    head_type = file_data[8]
                    head_flags = struct.unpack('<H', file_data[9:11])[0]
                   
                    archive_info.update({
                        'version': f"RAR {file_data[2]}",
                        'is_encrypted': bool(head_flags & 0x04),
                        'solid_archive': bool(head_flags & 0x08),
                        'recovery_record': bool(head_flags & 0x20)
                    })
           
            elif format_type == '7Z':
                # Basic 7Z header analysis
                if len(file_data) >= 32:
                    version_major = file_data[6]
                    version_minor = file_data[7]
                   
                    archive_info.update({
                        'version': f"7Z {version_major}.{version_minor}",
                        'file_count': self._estimate_7z_file_count(file_data)
                    })
           
        except Exception as e:
            archive_info['error'] = f"{format_type} analysis failed: {str(e)}"
       
        return {
            'archive_structure': archive_info,
            'content_analysis': {'format': format_type, 'notes': 'Limited analysis available'},
            'compression_info': self._get_compressed_archive_info(archive_info),
            'security_info': self._get_compressed_security_info(archive_info)
        }
   
    def _analyze_generic_archive(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze generic archive format"""
        return {
            'archive_structure': {
                'format': 'Unknown Archive',
                'file_size': len(file_data),
                'analysis_method': 'heuristic'
            },
            'compatibility': {
                'universal_support': False,
                'notes': 'Unknown archive format - may require specialized tools'
            }
        }
   
    def _extract_rpf_entries(self, file_data: bytes, toc_offset: int, toc_size: int) -> List[Dict[str, Any]]:
        """Extract RPF table of contents entries"""
        entries = []
       
        try:
            # Simplified RPF entry extraction
            # In a real implementation, this would parse the actual TOC structure
            entry_size = 16  # Typical RPF entry size
            max_entries = min(100, toc_size // entry_size)  # Limit for performance
           
            for i in range(max_entries):
                entry_offset = toc_offset + (i * entry_size)
                if entry_offset + entry_size <= len(file_data):
                    entry_data = file_data[entry_offset:entry_offset+entry_size]
                   
                    # Parse entry (simplified)
                    name_hash = struct.unpack('<Q', entry_data[0:8])[0]
                    offset = struct.unpack('<I', entry_data[8:12])[0]
                    size = struct.unpack('<I', entry_data[12:16])[0]
                   
                    entries.append({
                        'index': i,
                        'name_hash': hex(name_hash),
                        'offset': offset,
                        'size': size,
                        'is_directory': (size & 0x80000000) != 0,
                        'compressed_size': size & 0x7FFFFFFF
                    })
       
        except Exception as e:
            entries.append({'error': f"Entry extraction failed: {str(e)}"})
       
        return entries
   
    def _extract_zip_entries(self, file_data: bytes, central_dir_offset: int, file_count: int) -> List[Dict[str, Any]]:
        """Extract ZIP central directory entries"""
        entries = []
       
        try:
            current_offset = central_dir_offset
            max_entries = min(50, file_count)  # Limit for performance
           
            for i in range(max_entries):
                if current_offset + 46 > len(file_data):
                    break
               
                # Check for central directory header
                if file_data[current_offset:current_offset+4] != b'PK\x01\x02':
                    break
               
                # Parse central directory entry
                version_made_by = struct.unpack('<H', file_data[current_offset+4:current_offset+6])[0]
                version_needed = struct.unpack('<H', file_data[current_offset+6:current_offset+8])[0]
                flags = struct.unpack('<H', file_data[current_offset+8:current_offset+10])[0]
                compression_method = struct.unpack('<H', file_data[current_offset+10:current_offset+12])[0]
                mod_time = struct.unpack('<H', file_data[current_offset+12:current_offset+14])[0]
                mod_date = struct.unpack('<H', file_data[current_offset+14:current_offset+16])[0]
                crc32 = struct.unpack('<I', file_data[current_offset+16:current_offset+20])[0]
                compressed_size = struct.unpack('<I', file_data[current_offset+20:current_offset+24])[0]
                uncompressed_size = struct.unpack('<I', file_data[current_offset+24:current_offset+28])[0]
                name_length = struct.unpack('<H', file_data[current_offset+28:current_offset+30])[0]
                extra_length = struct.unpack('<H', file_data[current_offset+30:current_offset+32])[0]
                comment_length = struct.unpack('<H', file_data[current_offset+32:current_offset+34])[0]
                disk_start = struct.unpack('<H', file_data[current_offset+34:current_offset+36])[0]
                internal_attrs = struct.unpack('<H', file_data[current_offset+36:current_offset+38])[0]
                external_attrs = struct.unpack('<I', file_data[current_offset+38:current_offset+42])[0]
                local_header_offset = struct.unpack('<I', file_data[current_offset+42:current_offset+46])[0]
               
                # Extract filename
                name_start = current_offset + 46
                name_end = name_start + name_length
                if name_end <= len(file_data):
                    filename = file_data[name_start:name_end].decode('utf-8', errors='ignore')
                else:
                    filename = f"entry_{i}"
               
                entries.append({
                    'index': i,
                    'filename': filename,
                    'compression_method': self._get_zip_compression_name(compression_method),
                    'compressed_size': compressed_size,
                    'uncompressed_size': uncompressed_size,
                    'is_encrypted': bool(flags & 0x01),
                    'uses_data_descriptor': bool(flags & 0x08),
                    'crc32': hex(crc32),
                    'modification_time': self._decode_dos_time(mod_time, mod_date)
                })
               
                # Move to next entry
                current_offset += 46 + name_length + extra_length + comment_length
       
        except Exception as e:
            entries.append({'error': f"ZIP entry extraction failed: {str(e)}"})
       
        return entries
   
    def _analyze_rpf_content(self, archive_info: Dict) -> Dict[str, Any]:
        """Analyze RPF archive content"""
        entries = archive_info.get('entries', [])
        file_types = {}
        total_size = 0
       
        for entry in entries:
            if not entry.get('is_directory', False):
                size = entry.get('compressed_size', 0)
                total_size += size
               
                # Estimate file type from hash patterns (simplified)
                file_type = self._estimate_rpf_file_type(entry.get('name_hash', ''))
                file_types[file_type] = file_types.get(file_type, 0) + 1
       
        return {
            'total_files': len([e for e in entries if not e.get('is_directory', False)]),
            'total_directories': len([e for e in entries if e.get('is_directory', False)]),
            'total_size': total_size,
            'file_type_distribution': file_types,
            'estimated_content': 'Game assets, textures, models, scripts',
            'compression_ratio': self._calculate_compression_ratio(archive_info)
        }
   
    def _analyze_zip_content(self, archive_info: Dict) -> Dict[str, Any]:
        """Analyze ZIP archive content"""
        entries = archive_info.get('entries', [])
        file_types = {}
        total_compressed = 0
        total_uncompressed = 0
       
        for entry in entries:
            compressed = entry.get('compressed_size', 0)
            uncompressed = entry.get('uncompressed_size', 0)
           
            total_compressed += compressed
            total_uncompressed += uncompressed
           
            # Analyze file type from extension
            filename = entry.get('filename', '')
            file_ext = Path(filename).suffix.lower()
            file_types[file_ext] = file_types.get(file_ext, 0) + 1
       
        return {
            'total_files': len(entries),
            'total_compressed_size': total_compressed,
            'total_uncompressed_size': total_uncompressed,
            'file_type_distribution': file_types,
            'compression_ratio': (total_compressed / total_uncompressed) if total_uncompressed > 0 else 0,
            'average_compression': f"{(total_compressed / total_uncompressed * 100):.1f}%" if total_uncompressed > 0 else "Unknown"
        }
   
    def _get_rpf_compression_info(self, archive_info: Dict) -> Dict[str, Any]:
        """Get RPF compression information"""
        return {
            'compression_type': 'LZX',
            'compression_level': 'High',
            'block_based': True,
            'supports_streaming': True,
            'typical_ratio': '50-70%',
            'notes': 'RAGE-specific compression optimized for game assets'
        }
   
    def _get_zip_compression_info(self, archive_info: Dict) -> Dict[str, Any]:
        """Get ZIP compression information"""
        entries = archive_info.get('entries', [])
        methods = {}
       
        for entry in entries:
            method = entry.get('compression_method', 'Unknown')
            methods[method] = methods.get(method, 0) + 1
       
        return {
            'compression_methods': methods,
            'most_common_method': max(methods.items(), key=lambda x: x[1])[0] if methods else 'None',
            'encryption_used': archive_info.get('is_encrypted', False),
            'zip64_used': archive_info.get('uses_zip64', False)
        }
   
    def _get_compressed_archive_info(self, archive_info: Dict) -> Dict[str, Any]:
        """Get compressed archive information"""
        format_type = archive_info.get('format', '')
       
        if format_type == 'RAR':
            return {
                'compression_type': 'RAR',
                'compression_level': 'Variable',
                'solid_archiving': archive_info.get('solid_archive', False),
                'recovery_records': archive_info.get('recovery_record', False),
                'volume_splitting': archive_info.get('volume_number', 0) > 0
            }
        elif format_type == '7Z':
            return {
                'compression_type': 'LZMA',
                'compression_level': 'High',
                'solid_archiving': True,
                'multithreaded': True,
                'encryption': 'AES-256'
            }
        else:
            return {'compression_type': 'Unknown'}
   
    def _get_rpf_security_info(self, archive_info: Dict) -> Dict[str, Any]:
        """Get RPF security information"""
        return {
            'encryption': 'None (RAGE-specific obfuscation)',
            'integrity_checks': 'CRC32',
            'tamper_protection': 'Limited',
            'extraction_requirements': 'Game-specific tools',
            'risk_level': 'Low'
        }
   
    def _get_zip_security_info(self, archive_info: Dict) -> Dict[str, Any]:
        """Get ZIP security information"""
        return {
            'encryption': 'ZipCrypto (weak) or AES-256' if archive_info.get('is_encrypted') else 'None',
            'integrity_checks': 'CRC32',
            'tamper_protection': 'Basic',
            'password_protection': archive_info.get('is_encrypted', False),
            'risk_level': 'Low to Medium'
        }
   
    def _get_compressed_security_info(self, archive_info: Dict) -> Dict[str, Any]:
        """Get compressed archive security information"""
        format_type = archive_info.get('format', '')
       
        if format_type == 'RAR':
            return {
                'encryption': 'AES-128' if archive_info.get('is_encrypted') else 'None',
                'integrity_checks': 'Strong',
                'password_protection': archive_info.get('is_encrypted', False),
                'risk_level': 'Low'
            }
        elif format_type == '7Z':
            return {
                'encryption': 'AES-256' if archive_info.get('is_encrypted') else 'None',
                'integrity_checks': 'CRC64',
                'password_protection': archive_info.get('is_encrypted', False),
                'risk_level': 'Low'
            }
        else:
            return {'risk_level': 'Unknown'}
   
    def _get_zip_compression_name(self, method: int) -> str:
        """Get ZIP compression method name"""
        methods = {
            0: 'Stored',
            1: 'Shrunk',
            2: 'Reduced-1',
            3: 'Reduced-2',
            4: 'Reduced-3',
            5: 'Reduced-4',
            6: 'Imploded',
            8: 'Deflated',
            9: 'Deflate64',
            12: 'BZIP2',
            14: 'LZMA',
            19: 'LZ77',
            98: 'PPMd'
        }
        return methods.get(method, f'Unknown ({method})')
   
    def _estimate_rpf_file_type(self, name_hash: str) -> str:
        """Estimate RPF file type from hash patterns"""
        # This is simplified - real implementation would use known hash mappings
        hash_int = int(name_hash, 16) if name_hash.startswith('0x') else 0
       
        if hash_int % 10 == 0:
            return 'Texture'
        elif hash_int % 10 == 1:
            return 'Model'
        elif hash_int % 10 == 2:
            return 'Script'
        elif hash_int % 10 == 3:
            return 'Audio'
        else:
            return 'Data'
   
    def _calculate_compression_ratio(self, archive_info: Dict) -> float:
        """Calculate compression ratio"""
        entries = archive_info.get('entries', [])
        if not entries:
            return 0.0
       
        total_compressed = sum(e.get('compressed_size', 0) for e in entries if not e.get('is_directory', False))
        total_uncompressed = total_compressed * 1.5  # Estimate
       
        return total_compressed / total_uncompressed if total_uncompressed > 0 else 0.0
   
    def _estimate_7z_file_count(self, file_data: bytes) -> int:
        """Estimate 7z file count from header patterns"""
        # Simplified estimation
        return file_data.count(b'\x00\x00\x00') // 10
   
    def _decode_dos_time(self, time: int, date: int) -> str:
        """Decode DOS date/time format"""
        try:
            second = (time & 0x1F) * 2
            minute = (time >> 5) & 0x3F
            hour = (time >> 11) & 0x1F
           
            day = date & 0x1F
            month = (date >> 5) & 0x0F
            year = ((date >> 9) & 0x7F) + 1980
           
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        except:
            return "Unknown"