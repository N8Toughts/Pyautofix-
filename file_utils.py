"""
File Utilities Plugin - Common file operations and utilities
"""

import os
import hashlib
import zlib
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin


class FileUtilsPlugin(RAGEPlugin):
    """File utility functions for common operations"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "FileUtilsPlugin"
        self.supported_formats = ["ALL"]
        self.version = "1.0.0"
        self.description = "File utility functions for checksums, validation, and basic operations"
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze file using utility functions"""
        results = {
            'file_path': file_path,
            'analysis_method': 'file_utilities',
            'file_operations': {},
            'checksums': {},
            'validation_results': {},
            'file_properties': {}
        }
       
        # Perform various file utility analyses
        results.update({
            'file_operations': self._perform_file_operations(file_path),
            'checksums': self._calculate_checksums(file_path, file_data),
            'validation_results': self._validate_file(file_path, file_data),
            'file_properties': self._get_file_properties(file_path)
        })
       
        return results
   
    def _perform_file_operations(self, file_path: str) -> Dict[str, Any]:
        """Perform basic file operations"""
        operations = {}
       
        try:
            file_stats = Path(file_path)
           
            operations.update({
                'exists': file_stats.exists(),
                'is_file': file_stats.is_file(),
                'is_directory': file_stats.is_dir(),
                'is_symlink': file_stats.is_symlink(),
                'file_size': file_stats.stat().st_size if file_stats.exists() else 0,
                'permissions': oct(file_stats.stat().st_mode) if file_stats.exists() else 'Unknown',
                'last_modified': file_stats.stat().st_mtime if file_stats.exists() else 0,
                'last_accessed': file_stats.stat().st_atime if file_stats.exists() else 0,
                'created': file_stats.stat().st_ctime if file_stats.exists() else 0
            })
           
        except Exception as e:
            operations['error'] = f"File operations failed: {str(e)}"
       
        return operations
   
    def _calculate_checksums(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Calculate various checksums for the file"""
        checksums = {}
       
        try:
            if file_data is None:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
           
            # MD5
            checksums['md5'] = hashlib.md5(file_data).hexdigest()
           
            # SHA1
            checksums['sha1'] = hashlib.sha1(file_data).hexdigest()
           
            # SHA256
            checksums['sha256'] = hashlib.sha256(file_data).hexdigest()
           
            # SHA512
            checksums['sha512'] = hashlib.sha512(file_data).hexdigest()
           
            # CRC32
            checksums['crc32'] = hex(zlib.crc32(file_data) & 0xffffffff)
           
            # BLAKE2b
            checksums['blake2b'] = hashlib.blake2b(file_data).hexdigest()
           
            # File size based checksum (simple)
            checksums['size_based'] = self._size_based_checksum(file_data)
           
        except Exception as e:
            checksums['error'] = f"Checksum calculation failed: {str(e)}"
       
        return checksums
   
    def _validate_file(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Validate file integrity and structure"""
        validation = {
            'basic_checks': {},
            'structure_validation': {},
            'safety_checks': {}
        }
       
        try:
            # Basic file checks
            validation['basic_checks'] = self._perform_basic_checks(file_path, file_data)
           
            # Structure validation
            validation['structure_validation'] = self._validate_structure(file_path, file_data)
           
            # Safety checks
            validation['safety_checks'] = self._perform_safety_checks(file_path)
           
        except Exception as e:
            validation['error'] = f"Validation failed: {str(e)}"
       
        return validation
   
    def _get_file_properties(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file properties"""
        properties = {}
       
        try:
            file_stats = Path(file_path)
           
            if file_stats.exists():
                stat_info = file_stats.stat()
               
                properties.update({
                    'name': file_stats.name,
                    'stem': file_stats.stem,
                    'suffix': file_stats.suffix,
                    'parent': str(file_stats.parent),
                    'absolute_path': str(file_stats.absolute()),
                    'size': stat_info.st_size,
                    'size_human': self._format_bytes(stat_info.st_size),
                    'permissions': self._format_permissions(stat_info.st_mode),
                    'inode': stat_info.st_ino,
                    'device': stat_info.st_dev,
                    'hard_links': stat_info.st_nlink,
                    'uid': stat_info.st_uid,
                    'gid': stat_info.st_gid,
                    'is_readable': os.access(file_path, os.R_OK),
                    'is_writable': os.access(file_path, os.W_OK),
                    'is_executable': os.access(file_path, os.X_OK)
                })
               
                # File type detection
                properties['file_type'] = self._detect_file_type(file_path)
               
        except Exception as e:
            properties['error'] = f"Property extraction failed: {str(e)}"
       
        return properties
   
    def calculate_checksum(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate specific checksum for a file"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
           
            if algorithm.lower() == 'md5':
                return hashlib.md5(file_data).hexdigest()
            elif algorithm.lower() == 'sha1':
                return hashlib.sha1(file_data).hexdigest()
            elif algorithm.lower() == 'sha256':
                return hashlib.sha256(file_data).hexdigest()
            elif algorithm.lower() == 'sha512':
                return hashlib.sha512(file_data).hexdigest()
            elif algorithm.lower() == 'crc32':
                return hex(zlib.crc32(file_data) & 0xffffffff)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
               
        except Exception as e:
            raise Exception(f"Checksum calculation failed: {str(e)}")
   
    def verify_checksum(self, file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """Verify file against expected checksum"""
        try:
            actual_hash = self.calculate_checksum(file_path, algorithm)
            return actual_hash == expected_hash.lower()
        except Exception as e:
            raise Exception(f"Checksum verification failed: {str(e)}")
   
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        return self._get_file_properties(file_path)
   
    def create_temp_copy(self, file_path: str) -> str:
        """Create a temporary copy of the file"""
        try:
            temp_dir = tempfile.mkdtemp()
            temp_file = Path(temp_dir) / Path(file_path).name
           
            shutil.copy2(file_path, temp_file)
            return str(temp_file)
           
        except Exception as e:
            raise Exception(f"Temp copy creation failed: {str(e)}")
   
    def cleanup_temp_file(self, temp_path: str):
        """Clean up temporary file"""
        try:
            temp_file = Path(temp_path)
            if temp_file.exists():
                if temp_file.is_file():
                    temp_file.unlink()
                # Also remove parent temp directory if empty
                temp_dir = temp_file.parent
                if temp_dir.exists() and temp_dir.is_dir():
                    try:
                        temp_dir.rmdir()
                    except OSError:
                        pass  # Directory not empty
                       
        except Exception as e:
            raise Exception(f"Temp cleanup failed: {str(e)}")
   
    def _perform_basic_checks(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Perform basic file validation checks"""
        checks = {}
       
        try:
            file_stats = Path(file_path)
           
            if not file_stats.exists():
                checks['exists'] = False
                return checks
           
            checks['exists'] = True
            checks['is_file'] = file_stats.is_file()
            checks['is_directory'] = file_stats.is_dir()
            checks['is_symlink'] = file_stats.is_symlink()
            checks['size_valid'] = file_stats.stat().st_size > 0
            checks['readable'] = os.access(file_path, os.R_OK)
           
            if file_data is not None:
                checks['data_size_matches'] = len(file_data) == file_stats.stat().st_size
                checks['has_data'] = len(file_data) > 0
                checks['null_data'] = all(b == 0 for b in file_data)
           
        except Exception as e:
            checks['error'] = f"Basic checks failed: {str(e)}"
       
        return checks
   
    def _validate_structure(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Validate file structure based on type"""
        validation = {}
       
        try:
            if file_data is None:
                with open(file_path, 'rb') as f:
                    file_data = f.read(8192)  # Read first 8KB
           
            # Check for common file structure issues
            validation['has_header'] = len(file_data) >= 4
            validation['has_trailer'] = len(file_data) >= 8
           
            # Check for truncated files
            if len(file_data) < 16:
                validation['possibly_truncated'] = True
           
            # Check for common corruption patterns
            validation['all_null_bytes'] = all(b == 0 for b in file_data)
            validation['all_same_byte'] = len(set(file_data)) == 1 if file_data else False
           
            # File type specific validation
            file_type = self._detect_file_type_from_data(file_data)
            validation['detected_type'] = file_type
           
            if file_type == 'JPEG':
                validation.update(self._validate_jpeg_structure(file_data))
            elif file_type == 'PNG':
                validation.update(self._validate_png_structure(file_data))
            elif file_type == 'ZIP':
                validation.update(self._validate_zip_structure(file_data))
           
        except Exception as e:
            validation['error'] = f"Structure validation failed: {str(e)}"
       
        return validation
   
    def _perform_safety_checks(self, file_path: str) -> Dict[str, Any]:
        """Perform safety and security checks"""
        safety = {}
       
        try:
            file_stats = Path(file_path)
            file_name = file_stats.name.lower()
           
            # Check for potentially dangerous extensions
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.sh', '.py', '.js']
            safety['has_dangerous_extension'] = any(file_name.endswith(ext) for ext in dangerous_extensions)
           
            # Check file size limits
            file_size = file_stats.stat().st_size
            safety['is_very_large'] = file_size > 100 * 1024 * 1024  # 100MB
            safety['is_very_small'] = file_size < 16  # 16 bytes
           
            # Check permissions
            safety['is_world_writable'] = os.access(file_path, os.W_OK)
            safety['is_executable'] = os.access(file_path, os.X_OK)
           
            # Check for hidden files
            safety['is_hidden'] = file_name.startswith('.') or 'hidden' in file_name
           
        except Exception as e:
            safety['error'] = f"Safety checks failed: {str(e)}"
       
        return safety
   
    def _size_based_checksum(self, data: bytes) -> str:
        """Create a simple size-based checksum"""
        if not data:
            return "0" * 8
       
        # Simple algorithm using file size and first/last bytes
        size = len(data)
        first_bytes = data[:4] if len(data) >= 4 else data
        last_bytes = data[-4:] if len(data) >= 4 else data
       
        checksum = (size ^ int.from_bytes(first_bytes, 'little') ^
                   int.from_bytes(last_bytes, 'little'))
       
        return hex(checksum & 0xFFFFFFFF)[2:].zfill(8)
   
    def _format_bytes(self, size: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
   
    def _format_permissions(self, mode: int) -> str:
        """Format file permissions in Unix style"""
        permissions = [
            'r' if mode & 0o400 else '-',
            'w' if mode & 0o200 else '-',
            'x' if mode & 0o100 else '-',
            'r' if mode & 0o040 else '-',
            'w' if mode & 0o020 else '-',
            'x' if mode & 0o010 else '-',
            'r' if mode & 0o004 else '-',
            'w' if mode & 0o002 else '-',
            'x' if mode & 0o001 else '-'
        ]
        return ''.join(permissions)
   
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type using multiple methods"""
        try:
            # First try Python's mimetype
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                return mime_type
           
            # Fall back to extension-based detection
            extension = Path(file_path).suffix.lower()
            type_map = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                '.gif': 'image/gif', '.bmp': 'image/bmp', '.tiff': 'image/tiff',
                '.pdf': 'application/pdf', '.zip': 'application/zip',
                '.txt': 'text/plain', '.html': 'text/html', '.xml': 'text/xml',
                '.json': 'application/json'
            }
           
            return type_map.get(extension, 'application/octet-stream')
           
        except:
            return 'application/octet-stream'
   
    def _detect_file_type_from_data(self, data: bytes) -> str:
        """Detect file type from data content"""
        if len(data) < 4:
            return 'Unknown'
       
        # Check magic numbers
        if data.startswith(b'\xFF\xD8\xFF'):
            return 'JPEG'
        elif data.startswith(b'\x89PNG'):
            return 'PNG'
        elif data.startswith(b'GIF8'):
            return 'GIF'
        elif data.startswith(b'BM'):
            return 'BMP'
        elif data.startswith(b'%PDF'):
            return 'PDF'
        elif data.startswith(b'PK'):
            return 'ZIP'
        elif data.startswith(b'RIFF'):
            return 'RIFF'
        elif data.startswith(b'\x7FELF'):
            return 'ELF'
        elif data.startswith(b'MZ'):
            return 'PE'
        else:
            return 'Unknown'
   
    def _validate_jpeg_structure(self, data: bytes) -> Dict[str, Any]:
        """Validate JPEG file structure"""
        validation = {}
       
        try:
            # Check for SOI marker
            validation['has_soi'] = data.startswith(b'\xFF\xD8')
           
            # Check for EOI marker
            validation['has_eoi'] = data.endswith(b'\xFF\xD9')
           
            # Check for APP0 marker (JFIF)
            validation['has_app0'] = b'JFIF' in data[:100]
           
            # Check for valid marker sequence
            pos = 2  # Start after SOI
            valid_markers = True
           
            while pos < len(data) - 1:
                if data[pos] != 0xFF:
                    valid_markers = False
                    break
                marker = data[pos+1]
                if marker == 0xD9:  # EOI
                    break
                pos += 2
           
            validation['valid_markers'] = valid_markers
           
        except Exception as e:
            validation['error'] = f"JPEG validation failed: {str(e)}"
       
        return validation
   
    def _validate_png_structure(self, data: bytes) -> Dict[str, Any]:
        """Validate PNG file structure"""
        validation = {}
       
        try:
            # Check PNG signature
            validation['valid_signature'] = data.startswith(b'\x89PNG\r\n\x1a\n')
           
            # Check for IHDR chunk
            validation['has_ihdr'] = b'IHDR' in data[:50]
           
            # Check for IEND chunk
            validation['has_iend'] = b'IEND' in data[-20:]
           
            # Basic chunk structure check
            if len(data) >= 24:
                # IHDR should be at position 12-16
                validation['ihdr_position'] = data[12:16] == b'IHDR'
           
        except Exception as e:
            validation['error'] = f"PNG validation failed: {str(e)}"
       
        return validation
   
    def _validate_zip_structure(self, data: bytes) -> Dict[str, Any]:
        """Validate ZIP file structure"""
        validation = {}
       
        try:
            # Check local file header signature
            validation['has_local_header'] = data.startswith(b'PK\x03\x04')
           
            # Check for central directory
            validation['has_central_dir'] = b'PK\x01\x02' in data
           
            # Check for end of central directory
            validation['has_eocd'] = b'PK\x05\x06' in data
           
            # Basic size validation
            if len(data) >= 30:
                # Check if declared sizes seem reasonable
                local_header_size = struct.unpack('<H', data[26:28])[0]
                file_name_length = struct.unpack('<H', data[26:28])[0]
                extra_field_length = struct.unpack('<H', data[28:30])[0]
               
                total_header_size = 30 + file_name_length + extra_field_length
                validation['reasonable_header_size'] = total_header_size < len(data)
           
        except Exception as e:
            validation['error'] = f"ZIP validation failed: {str(e)}"
       
        return validation
   
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            'checksum_calculation',
            'file_validation',
            'property_extraction',
            'safety_checks',
            'temp_file_management'
        ]