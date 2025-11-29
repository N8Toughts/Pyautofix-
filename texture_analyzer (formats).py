"""
Universal Texture Format Analyzer Plugin
"""

import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin 
import FormatPlugin


class TextureAnalyzerPlugin(FormatPlugin):
    """Universal texture format analyzer"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "TextureAnalyzerPlugin"
        self.supported_formats = ["DDS", "PNG", "JPG", "JPEG", "TGA", "BMP", "TIF", "TIFF"]
        self.version = "1.0.0"
        self.description = "Universal texture format analyzer with detailed metadata extraction"
       
        # Texture format signatures
        self.format_signatures = [
            b'DDS',           # DDS format
            b'\x89PNG',       # PNG format
            b'\xFF\xD8\xFF',  # JPEG format
            b'BM',           # BMP format
            b'\x00\x00\x02',  # TGA format (uncompressed)
            b'\x00\x00\x10',  # TGA format (RLE)
        ]
       
        # DDS format constants
        self.DDS_MAGIC = b'DDS '
        self.DDS_HEADER_SIZE = 124
        self.DDS_PIXELFORMAT_SIZE = 32
       
        # DDS pixel format flags
        self.DDPF_ALPHAPIXELS = 0x1
        self.DDPF_ALPHA = 0x2
        self.DDPF_FOURCC = 0x4
        self.DDPF_RGB = 0x40
        self.DDPF_YUV = 0x200
        self.DDPF_LUMINANCE = 0x20000
       
        # DDS FourCC codes
        self.FOURCC_DXT1 = b'DXT1'
        self.FOURCC_DXT3 = b'DXT3'
        self.FOURCC_DXT5 = b'DXT5'
        self.FOURCC_ATI1 = b'ATI1'
        self.FOURCC_ATI2 = b'ATI2'
        self.FOURCC_BC4U = b'BC4U'
        self.FOURCC_BC5U = b'BC5U'
   
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze texture file"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(8192)  # Read first 8KB for analysis
       
        results = {
            'file_path': file_path,
            'format_type': self._detect_texture_format(file_data),
            'analysis_method': 'texture_plugin',
            'is_texture': True,
            'texture_details': {},
            'compression_info': {},
            'image_properties': {},
            'mipmap_info': {},
            'compatibility': {},
            'issues': []
        }
       
        # Perform format-specific analysis
        format_type = results['format_type']
        if format_type == 'DDS':
            results.update(self._analyze_dds(file_path, file_data))
        elif format_type in ['PNG', 'JPEG', 'TGA', 'BMP']:
            results.update(self._analyze_standard_image(file_path, file_data, format_type))
        else:
            results.update(self._analyze_unknown_texture(file_path, file_data))
       
        return results
   
    def _detect_texture_format(self, file_data: bytes) -> str:
        """Detect texture format from signature"""
        if file_data.startswith(self.DDS_MAGIC):
            return 'DDS'
        elif file_data.startswith(b'\x89PNG'):
            return 'PNG'
        elif file_data.startswith(b'\xFF\xD8\xFF'):
            return 'JPEG'
        elif file_data.startswith(b'BM'):
            return 'BMP'
        elif file_data.startswith((b'\x00\x00\x02', b'\x00\x00\x10')):
            return 'TGA'
        else:
            return 'Unknown Texture'
   
    def _analyze_dds(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze DDS texture format"""
        texture_info = {
            'format': 'DDS',
            'width': 0,
            'height': 0,
            'depth': 0,
            'mipmap_count': 0,
            'format_fourcc': 'Unknown',
            'format_description': 'Unknown',
            'has_alpha': False,
            'is_compressed': False,
            'is_cubemap': False,
            'is_volume': False,
            'pixel_format': {},
            'caps': {},
            'file_size': len(file_data) if file_data else 0
        }
       
        try:
            if len(file_data) >= 128:  # Minimum DDS header size
                # Parse DDS header
                magic = file_data[0:4]
                if magic == self.DDS_MAGIC:
                    # Parse header
                    header_size = struct.unpack('<I', file_data[4:8])[0]
                    flags = struct.unpack('<I', file_data[8:12])[0]
                    height = struct.unpack('<I', file_data[12:16])[0]
                    width = struct.unpack('<I', file_data[16:20])[0]
                    pitch_or_linear_size = struct.unpack('<I', file_data[20:24])[0]
                    depth = struct.unpack('<I', file_data[24:28])[0]
                    mipmap_count = struct.unpack('<I', file_data[28:32])[0]
                   
                    texture_info.update({
                        'width': width,
                        'height': height,
                        'depth': depth,
                        'mipmap_count': mipmap_count,
                        'pitch_or_linear_size': pitch_or_linear_size
                    })
                   
                    # Parse pixel format
                    pf_offset = 76
                    if len(file_data) >= pf_offset + self.DDS_PIXELFORMAT_SIZE:
                        pf_size = struct.unpack('<I', file_data[pf_offset:pf_offset+4])[0]
                        pf_flags = struct.unpack('<I', file_data[pf_offset+4:pf_offset+8])[0]
                        pf_fourcc = file_data[pf_offset+8:pf_offset+12]
                        pf_rgb_bit_count = struct.unpack('<I', file_data[pf_offset+12:pf_offset+16])[0]
                        pf_r_bit_mask = struct.unpack('<I', file_data[pf_offset+16:pf_offset+20])[0]
                        pf_g_bit_mask = struct.unpack('<I', file_data[pf_offset+20:pf_offset+24])[0]
                        pf_b_bit_mask = struct.unpack('<I', file_data[pf_offset+24:pf_offset+28])[0]
                        pf_a_bit_mask = struct.unpack('<I', file_data[pf_offset+28:pf_offset+32])[0]
                       
                        texture_info['pixel_format'] = {
                            'size': pf_size,
                            'flags': pf_flags,
                            'fourcc': pf_fourcc.decode('ascii', errors='ignore').strip(),
                            'rgb_bit_count': pf_rgb_bit_count,
                            'r_bit_mask': hex(pf_r_bit_mask),
                            'g_bit_mask': hex(pf_g_bit_mask),
                            'b_bit_mask': hex(pf_b_bit_mask),
                            'a_bit_mask': hex(pf_a_bit_mask)
                        }
                       
                        # Determine format details
                        fourcc_str = pf_fourcc.decode('ascii', errors='ignore').strip()
                        texture_info['format_fourcc'] = fourcc_str
                        texture_info['format_description'] = self._get_dds_format_description(fourcc_str, pf_flags)
                        texture_info['has_alpha'] = bool(pf_flags & self.DDPF_ALPHAPIXELS)
                        texture_info['is_compressed'] = bool(pf_flags & self.DDPF_FOURCC)
                       
                        # Parse caps
                        caps1 = struct.unpack('<I', file_data[108:112])[0]
                        caps2 = struct.unpack('<I', file_data[112:116])[0]
                       
                        texture_info['caps'] = {
                            'caps1': caps1,
                            'caps2': caps2,
                            'is_cubemap': bool(caps2 & 0xFE00),  # DDSCAPS2_CUBEMAP
                            'is_volume': bool(caps2 & 0x200000)   # DDSCAPS2_VOLUME
                        }
                        texture_info['is_cubemap'] = texture_info['caps']['is_cubemap']
                        texture_info['is_volume'] = texture_info['caps']['is_volume']
           
        except Exception as e:
            texture_info['error'] = f"DDS analysis failed: {str(e)}"
       
        return {
            'texture_details': texture_info,
            'compression_info': self._get_compression_info(texture_info),
            'mipmap_info': self._get_mipmap_info(texture_info),
            'compatibility': self._get_texture_compatibility(texture_info)
        }
   
    def _analyze_standard_image(self, file_path: str, file_data: bytes, format_type: str) -> Dict[str, Any]:
        """Analyze standard image formats (PNG, JPEG, etc.)"""
        texture_info = {
            'format': format_type,
            'width': 0,
            'height': 0,
            'color_depth': 0,
            'has_alpha': False,
            'is_compressed': format_type == 'JPEG',
            'compression_type': 'Lossy' if format_type == 'JPEG' else 'Lossless',
            'file_size': len(file_data) if file_data else 0
        }
       
        try:
            # Basic dimension extraction for common formats
            if format_type == 'PNG' and len(file_data) >= 24:
                # PNG stores dimensions at bytes 16-24
                width = struct.unpack('>I', file_data[16:20])[0]
                height = struct.unpack('>I', file_data[20:24])[0]
                texture_info.update({'width': width, 'height': height})
               
            elif format_type == 'JPEG' and len(file_data) >= 20:
                # JPEG SOF marker analysis (simplified)
                texture_info.update(self._estimate_jpeg_dimensions(file_data))
               
            elif format_type == 'BMP' and len(file_data) >= 26:
                # BMP header analysis
                width = struct.unpack('<I', file_data[18:22])[0]
                height = struct.unpack('<I', file_data[22:26])[0]
                texture_info.update({'width': width, 'height': height})
               
            elif format_type == 'TGA' and len(file_data) >= 18:
                # TGA header analysis
                width = struct.unpack('<H', file_data[12:14])[0]
                height = struct.unpack('<H', file_data[14:16])[0]
                pixel_depth = file_data[16]
                texture_info.update({
                    'width': width,
                    'height': height,
                    'color_depth': pixel_depth
                })
               
        except Exception as e:
            texture_info['error'] = f"{format_type} analysis failed: {str(e)}"
       
        return {
            'texture_details': texture_info,
            'image_properties': self._get_image_properties(texture_info),
            'compatibility': {'universal_support': True, 'notes': 'Standard image format'}
        }
   
    def _analyze_unknown_texture(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze unknown texture format"""
        return {
            'texture_details': {
                'format': 'Unknown',
                'file_size': len(file_data),
                'analysis_method': 'heuristic'
            },
            'compatibility': {
                'universal_support': False,
                'notes': 'Unknown texture format - may require specialized tools'
            }
        }
   
    def _get_dds_format_description(self, fourcc: str, flags: int) -> str:
        """Get human-readable DDS format description"""
        format_descriptions = {
            'DXT1': 'BC1 Compression (DXT1)',
            'DXT3': 'BC2 Compression (DXT3)',
            'DXT5': 'BC3 Compression (DXT5)',
            'ATI1': 'BC4 Compression (ATI1)',
            'ATI2': 'BC5 Compression (ATI2)',
            'BC4U': 'BC4 Compression',
            'BC5U': 'BC5 Compression',
            'DX10': 'DX10 Extended Format',
            '': 'Uncompressed RGB'
        }
       
        if fourcc in format_descriptions:
            return format_descriptions[fourcc]
        elif flags & self.DDPF_RGB:
            return 'Uncompressed RGB'
        elif flags & self.DDPF_LUMINANCE:
            return 'Luminance'
        else:
            return f'Unknown Format ({fourcc})'
   
    def _get_compression_info(self, texture_info: Dict) -> Dict[str, Any]:
        """Get compression information"""
        fourcc = texture_info.get('format_fourcc', '')
        is_compressed = texture_info.get('is_compressed', False)
       
        if not is_compressed:
            return {'compressed': False, 'type': 'Uncompressed'}
       
        compression_types = {
            'DXT1': {'type': 'BC1', 'ratio': '6:1', 'quality': 'Good'},
            'DXT3': {'type': 'BC2', 'ratio': '4:1', 'quality': 'Good'},
            'DXT5': {'type': 'BC3', 'ratio': '4:1', 'quality': 'Better'},
            'ATI1': {'type': 'BC4', 'ratio': '2:1', 'quality': 'Normal'},
            'ATI2': {'type': 'BC5', 'ratio': '2:1', 'quality': 'Normal'}
        }
       
        return compression_types.get(fourcc, {'type': 'Unknown', 'ratio': 'Unknown', 'quality': 'Unknown'})
   
    def _get_mipmap_info(self, texture_info: Dict) -> Dict[str, Any]:
        """Get mipmap information"""
        mipmap_count = texture_info.get('mipmap_count', 0)
        width = texture_info.get('width', 0)
        height = texture_info.get('height', 0)
       
        mipmaps = []
        current_width = width
        current_height = height
       
        for i in range(mipmap_count):
            if current_width > 0 and current_height > 0:
                mipmaps.append({
                    'level': i,
                    'width': current_width,
                    'height': current_height,
                    'size_estimate': self._estimate_mipmap_size(current_width, current_height, texture_info)
                })
                current_width = max(1, current_width // 2)
                current_height = max(1, current_height // 2)
       
        return {
            'mipmap_count': mipmap_count,
            'mipmaps': mipmaps,
            'has_full_chain': mipmap_count > 1
        }
   
    def _get_image_properties(self, texture_info: Dict) -> Dict[str, Any]:
        """Get general image properties"""
        return {
            'aspect_ratio': self._calculate_aspect_ratio(texture_info.get('width', 0), texture_info.get('height', 0)),
            'megapixels': (texture_info.get('width', 0) * texture_info.get('height', 0)) / 1000000,
            'recommended_usage': self._get_recommended_usage(texture_info),
            'power_of_two': self._is_power_of_two(texture_info.get('width', 0)) and self._is_power_of_two(texture_info.get('height', 0))
        }
   
    def _get_texture_compatibility(self, texture_info: Dict) -> Dict[str, Any]:
        """Get texture compatibility information"""
        format_type = texture_info.get('format', '')
        fourcc = texture_info.get('format_fourcc', '')
       
        compatibility = {
            'universal_support': format_type in ['PNG', 'JPEG', 'BMP'],
            'game_engine_support': 'Good' if format_type == 'DDS' else 'Variable',
            'editing_tools': 'Specialized' if format_type == 'DDS' else 'Universal',
            'notes': ''
        }
       
        if format_type == 'DDS':
            if fourcc in ['DXT1', 'DXT3', 'DXT5']:
                compatibility['notes'] = 'Widely supported in game engines'
            else:
                compatibility['notes'] = 'May require specific hardware support'
       
        return compatibility
   
    def _estimate_jpeg_dimensions(self, file_data: bytes) -> Dict[str, Any]:
        """Estimate JPEG dimensions from SOF marker"""
        # Simplified JPEG dimension extraction
        for i in range(len(file_data) - 9):
            if file_data[i] == 0xFF and file_data[i+1] in [0xC0, 0xC2]:  # SOF0 or SOF2
                height = struct.unpack('>H', file_data[i+5:i+7])[0]
                width = struct.unpack('>H', file_data[i+7:i+9])[0]
                return {'width': width, 'height': height}
        return {'width': 0, 'height': 0}
   
    def _estimate_mipmap_size(self, width: int, height: int, texture_info: Dict) -> int:
        """Estimate mipmap size in bytes"""
        if texture_info.get('is_compressed', False):
            # Compressed texture size estimation
            fourcc = texture_info.get('format_fourcc', '')
            if fourcc == 'DXT1':
                return max(8, (width * height) // 2)  # BC1 is 4bpp
            else:
                return max(16, width * height)  # BC2/3 are 8bpp
        else:
            # Uncompressed size estimation
            bpp = texture_info.get('pixel_format', {}).get('rgb_bit_count', 32)
            return (width * height * bpp) // 8
   
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate aspect ratio"""
        if width == 0 or height == 0:
            return "Unknown"
       
        from math import gcd
        divisor = gcd(width, height)
        return f"{width//divisor}:{height//divisor}"
   
    def _get_recommended_usage(self, texture_info: Dict) -> str:
        """Get recommended texture usage"""
        width = texture_info.get('width', 0)
        height = texture_info.get('height', 0)
       
        if width >= 2048 or height >= 2048:
            return "High-resolution assets, environment textures"
        elif width >= 1024 or height >= 1024:
            return "Character textures, important assets"
        elif width >= 512 or height >= 512:
            return "UI elements, smaller assets"
        else:
            return "Icons, decals, small details"
   
    def _is_power_of_two(self, num: int) -> bool:
        """Check if number is power of two"""
        return num != 0 and (num & (num - 1)) == 0