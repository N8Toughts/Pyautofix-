"""
Compatibility Plugin - Version and system compatibility checking
"""

import sys
import platform
import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import RAGEPlugin


class CompatibilityPlugin(RAGEPlugin):
    """Compatibility checking for files and systems"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "CompatibilityPlugin"
        self.supported_formats = ["ALL"]
        self.version = "1.0.0"
        self.description = "System and version compatibility analysis"
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze file compatibility"""
        if file_data is None:
            with open(file_path, 'rb') as f:
                file_data = f.read(4096)  # Read 4KB for compatibility analysis
       
        results = {
            'file_path': file_path,
            'analysis_method': 'compatibility_analysis',
            'system_compatibility': {},
            'version_compatibility': {},
            'architecture_analysis': {},
            'dependency_check': {},
            'compatibility_issues': []
        }
       
        # Perform compatibility analysis
        results.update({
            'system_compatibility': self._check_system_compatibility(file_path, file_data),
            'version_compatibility': self._check_version_compatibility(file_path, file_data),
            'architecture_analysis': self._analyze_architecture(file_data),
            'dependency_check': self._check_dependencies(file_path, file_data),
            'compatibility_issues': self._find_compatibility_issues(results)
        })
       
        return results
   
    def _check_system_compatibility(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Check system compatibility"""
        compatibility = {
            'current_system': {},
            'detected_systems': [],
            'cross_platform': False,
            'system_requirements': {}
        }
       
        try:
            # Get current system info
            compatibility['current_system'] = self._get_system_info()
           
            # Detect target systems from file
            compatibility['detected_systems'] = self._detect_target_systems(file_data)
           
            # Check cross-platform compatibility
            compatibility['cross_platform'] = self._is_cross_platform(file_data)
           
            # Estimate system requirements
            compatibility['system_requirements'] = self._estimate_requirements(file_path, file_data)
           
        except Exception as e:
            compatibility['error'] = f"System compatibility check failed: {str(e)}"
       
        return compatibility
   
    def _check_version_compatibility(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Check version compatibility"""
        version_info = {
            'file_versions': [],
            'compatibility_ranges': {},
            'version_issues': [],
            'migration_info': {}
        }
       
        try:
            # Detect file format versions
            version_info['file_versions'] = self._detect_file_versions(file_data)
           
            # Check compatibility ranges
            version_info['compatibility_ranges'] = self._check_version_ranges(file_data)
           
            # Find version-specific issues
            version_info['version_issues'] = self._find_version_issues(file_data)
           
            # Provide migration information
            version_info['migration_info'] = self._get_migration_info(file_data)
           
        except Exception as e:
            version_info['error'] = f"Version compatibility check failed: {str(e)}"
       
        return version_info
   
    def _analyze_architecture(self, file_data: bytes) -> Dict[str, Any]:
        """Analyze system architecture requirements"""
        architecture = {
            'detected_architectures': [],
            'bitness': 'Unknown',
            'endianness': 'Unknown',
            'instruction_sets': [],
            'memory_requirements': {}
        }
       
        try:
            # Detect CPU architectures
            architecture['detected_architectures'] = self._detect_architectures(file_data)
           
            # Determine bitness (32/64-bit)
            architecture['bitness'] = self._detect_bitness(file_data)
           
            # Detect endianness
            architecture['endianness'] = self._detect_endianness(file_data)
           
            # Detect instruction sets
            architecture['instruction_sets'] = self._detect_instruction_sets(file_data)
           
            # Estimate memory requirements
            architecture['memory_requirements'] = self._estimate_memory_requirements(file_data)
           
        except Exception as e:
            architecture['error'] = f"Architecture analysis failed: {str(e)}"
       
        return architecture
   
    def _check_dependencies(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Check file dependencies"""
        dependencies = {
            'external_dependencies': [],
            'internal_dependencies': [],
            'library_references': [],
            'api_calls': [],
            'dependency_issues': []
        }
       
        try:
            # Find external dependencies
            dependencies['external_dependencies'] = self._find_external_dependencies(file_data)
           
            # Find internal dependencies
            dependencies['internal_dependencies'] = self._find_internal_dependencies(file_data)
           
            # Find library references
            dependencies['library_references'] = self._find_library_references(file_data)
           
            # Find API calls
            dependencies['api_calls'] = self._find_api_calls(file_data)
           
            # Check for dependency issues
            dependencies['dependency_issues'] = self._check_dependency_issues(dependencies)
           
        except Exception as e:
            dependencies['error'] = f"Dependency check failed: {str(e)}"
       
        return dependencies
   
    def _find_compatibility_issues(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find compatibility issues from analysis results"""
        issues = []
       
        system_comp = analysis_results.get('system_compatibility', {})
        version_comp = analysis_results.get('version_compatibility', {})
        arch_analysis = analysis_results.get('architecture_analysis', {})
        dep_check = analysis_results.get('dependency_check', {})
       
        # Check system compatibility issues
        current_system = system_comp.get('current_system', {})
        detected_systems = system_comp.get('detected_systems', [])
       
        if detected_systems and current_system.get('os_family') not in detected_systems:
            issues.append({
                'type': 'System Incompatibility',
                'severity': 'High',
                'description': f"File appears targeted for {detected_systems} but current system is {current_system.get('os_family')}",
                'suggestion': 'Check if compatible version exists or use emulation'
            })
       
        # Check architecture issues
        current_arch = current_system.get('architecture')
        detected_archs = arch_analysis.get('detected_architectures', [])
       
        if detected_archs and current_arch not in detected_archs:
            issues.append({
                'type': 'Architecture Mismatch',
                'severity': 'High',
                'description': f"File requires {detected_archs} but current architecture is {current_arch}",
                'suggestion': 'Use compatible hardware or emulation'
            })
       
        # Check bitness issues
        current_bits = current_system.get('bitness')
        file_bits = arch_analysis.get('bitness')
       
        if file_bits != 'Unknown' and current_bits != file_bits:
            issues.append({
                'type': 'Bitness Mismatch',
                'severity': 'Medium',
                'description': f"File is {file_bits}-bit but system is {current_bits}-bit",
                'suggestion': 'Use compatibility mode or appropriate runtime'
            })
       
        # Check dependency issues
        dep_issues = dep_check.get('dependency_issues', [])
        issues.extend(dep_issues)
       
        # Check version issues
        version_issues = version_comp.get('version_issues', [])
        issues.extend(version_issues)
       
        return sorted(issues, key=lambda x: {'High': 3, 'Medium': 2, 'Low': 1}.get(x['severity'], 0), reverse=True)
   
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        system_info = {
            'os_family': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'bitness': '64-bit' if sys.maxsize > 2**32 else '32-bit',
            'python_version': platform.python_version(),
            'system_alias': platform.platform()
        }
       
        # Additional platform-specific info
        if system_info['os_family'] == 'Windows':
            system_info['windows_edition'] = platform.win32_edition() if hasattr(platform, 'win32_edition') else 'Unknown'
        elif system_info['os_family'] == 'Linux':
            system_info['libc_version'] = platform.libc_ver()
       
        return system_info
   
    def _detect_target_systems(self, file_data: bytes) -> List[str]:
        """Detect target operating systems from file data"""
        systems = []
       
        # Check for system-specific signatures
        system_signatures = {
            'Windows': [
                b'MZ',  # DOS/Windows executable
                b'PE\x00\x00',  # Portable Executable
                b'This program cannot be run in DOS mode',
                b'KERNEL32.DLL',
                b'USER32.DLL'
            ],
            'Linux': [
                b'\x7FELF',  # ELF executable
                b'/lib/', b'/usr/lib/',
                b'GNU'
            ],
            'macOS': [
                b'\xFE\xED\xFA\xCE',  # Mach-O (32-bit)
                b'\xFE\xED\xFA\xCF',  # Mach-O (64-bit)
                b'\xCE\xFA\xED\xFE',  # Mach-O (reverse 32-bit)
                b'\xCF\xFA\xED\xFE',  # Mach-O (reverse 64-bit)
                b'/Applications/',
                b'.app/'
            ],
            'Unix': [
                b'#!/bin/sh', b'#!/bin/bash',
                b'#!/usr/bin/env',
                b'/etc/', b'/var/'
            ]
        }
       
        for system, signatures in system_signatures.items():
            for signature in signatures:
                if signature in file_data:
                    systems.append(system)
                    break
       
        return list(set(systems))  # Remove duplicates
   
    def _is_cross_platform(self, file_data: bytes) -> bool:
        """Check if file appears to be cross-platform"""
        # Files with multiple system signatures are likely cross-platform
        systems = self._detect_target_systems(file_data)
       
        if len(systems) > 1:
            return True
       
        # Check for cross-platform formats
        cross_platform_formats = [
            b'#!/usr/bin/env python',
            b'#!/usr/bin/env ruby',
            b'#!/usr/bin/env perl',
            b'Java',
            b'.class',
            b'PK'  # ZIP-based formats (Java JAR, etc.)
        ]
       
        return any(sig in file_data for sig in cross_platform_formats)
   
    def _estimate_requirements(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Estimate system requirements"""
        requirements = {
            'minimum_ram': 'Unknown',
            'storage_space': 'Unknown',
            'processor_speed': 'Unknown',
            'graphics': 'Unknown',
            'additional_software': []
        }
       
        try:
            file_size = len(file_data)
            file_ext = Path(file_path).suffix.lower()
           
            # Estimate based on file size and type
            if file_size < 1024 * 1024:  # < 1MB
                requirements['minimum_ram'] = '16MB'
                requirements['storage_space'] = '1MB'
            elif file_size < 10 * 1024 * 1024:  # < 10MB
                requirements['minimum_ram'] = '64MB'
                requirements['storage_space'] = '10MB'
            elif file_size < 100 * 1024 * 1024:  # < 100MB
                requirements['minimum_ram'] = '256MB'
                requirements['storage_space'] = '100MB'
            else:
                requirements['minimum_ram'] = '1GB'
                requirements['storage_space'] = f'{file_size // (1024*1024)}MB'
           
            # Estimate based on file type
            if file_ext in ['.exe', '.dll', '.so', '.dylib']:
                requirements['processor_speed'] = '1GHz'
            elif file_ext in ['.jpg', '.png', '.gif']:
                requirements['graphics'] = 'Basic 2D'
            elif file_ext in ['.mp4', '.avi', '.mkv']:
                requirements['graphics'] = 'Hardware video acceleration recommended'
           
            # Common software dependencies
            if file_ext == '.pdf':
                requirements['additional_software'].append('PDF Reader')
            elif file_ext in ['.doc', '.docx']:
                requirements['additional_software'].append('Word Processor')
            elif file_ext in ['.xls', '.xlsx']:
                requirements['additional_software'].append('Spreadsheet Software')
           
        except Exception as e:
            requirements['error'] = f"Requirement estimation failed: {str(e)}"
       
        return requirements
   
    def _detect_file_versions(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Detect file format versions"""
        versions = []
       
        # Common version signatures
        version_patterns = [
            (b'PDF-1.', 'PDF 1.x', 1),
            (b'%PDF-1.', 'PDF 1.x', 1),
            (b'VERSION 2.', 'Version 2.x', 2),
            (b'v3.', 'Version 3.x', 3),
            (b'Version 4.', 'Version 4.x', 4),
            (b'Python 3.', 'Python 3.x', 3),
            (b'Python 2.', 'Python 2.x', 2),
        ]
       
        for pattern, description, version in version_patterns:
            if pattern in file_data:
                versions.append({
                    'version': version,
                    'description': description,
                    'confidence': 'High',
                    'evidence': f'Found pattern: {pattern}'
                })
       
        # Check for specific format versions
        if file_data.startswith(b'\x89PNG'):
            versions.append({
                'version': '1.2',
                'description': 'PNG 1.2',
                'confidence': 'High',
                'evidence': 'PNG signature'
            })
       
        if file_data.startswith(b'GIF89a'):
            versions.append({
                'version': '89a',
                'description': 'GIF 89a',
                'confidence': 'High',
                'evidence': 'GIF89a signature'
            })
       
        if file_data.startswith(b'GIF87a'):
            versions.append({
                'version': '87a',
                'description': 'GIF 87a',
                'confidence': 'High',
                'evidence': 'GIF87a signature'
            })
       
        return versions
   
    def _check_version_ranges(self, file_data: bytes) -> Dict[str, Any]:
        """Check version compatibility ranges"""
        ranges = {
            'supported_versions': [],
            'deprecated_versions': [],
            'migration_paths': [],
            'compatibility_notes': []
        }
       
        # This would typically query a compatibility database
        # For now, provide some basic heuristics
       
        file_versions = self._detect_file_versions(file_data)
       
        for version_info in file_versions:
            version = version_info.get('version')
            description = version_info.get('description', '')
           
            if isinstance(version, int):
                if version < 2:
                    ranges['deprecated_versions'].append(f"{description} (legacy)")
                    ranges['compatibility_notes'].append(f"{description} may have limited modern support")
                elif version < 4:
                    ranges['supported_versions'].append(f"{description} (well-supported)")
                else:
                    ranges['supported_versions'].append(f"{description} (current)")
           
            elif 'PDF-1.0' in description or 'PDF-1.1' in description:
                ranges['deprecated_versions'].append(description)
                ranges['migration_paths'].append("Upgrade to PDF 1.4 or later for better compatibility")
           
            elif 'Python 2' in description:
                ranges['deprecated_versions'].append(description)
                ranges['migration_paths'].append("Migrate to Python 3 for ongoing support")
       
        return ranges
   
    def _find_version_issues(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find version-specific compatibility issues"""
        issues = []
       
        file_versions = self._detect_file_versions(file_data)
       
        for version_info in file_versions:
            version = version_info.get('version')
            description = version_info.get('description', '')
           
            if isinstance(version, int) and version < 2:
                issues.append({
                    'type': 'Legacy Version',
                    'severity': 'Medium',
                    'description': f"File uses {description} which may have compatibility issues",
                    'suggestion': 'Consider upgrading to a newer version if possible'
                })
           
            if 'Python 2' in description:
                issues.append({
                    'type': 'Deprecated Runtime',
                    'severity': 'High',
                    'description': 'File requires Python 2 which is no longer supported',
                    'suggestion': 'Migrate to Python 3 or use compatibility layers'
                })
       
        return issues
   
    def _get_migration_info(self, file_data: bytes) -> Dict[str, Any]:
        """Get migration information for outdated formats"""
        migration = {
            'migration_paths': [],
            'tools_available': [],
            'compatibility_layers': [],
            'risks': []
        }
       
        file_versions = self._detect_file_versions(file_data)
       
        for version_info in file_versions:
            description = version_info.get('description', '')
           
            if 'Python 2' in description:
                migration['migration_paths'].append('Use 2to3 tool for automatic Python 2 to 3 conversion')
                migration['tools_available'].append('2to3 (included with Python)')
                migration['compatibility_layers'].append('Python 2 compatibility mode in some environments')
                migration['risks'].append('Some Python 2 features may not have direct Python 3 equivalents')
           
            if 'PDF-1.0' in description or 'PDF-1.1' in description:
                migration['migration_paths'].append('Use PDF editing software to save as newer PDF version')
                migration['tools_available'].append('Adobe Acrobat, Ghostscript, online converters')
                migration['risks'].append('Some legacy PDF features may not be preserved')
       
        return migration
   
    def _detect_architectures(self, file_data: bytes) -> List[str]:
        """Detect CPU architectures from file data"""
        architectures = []
       
        # Architecture signatures
        arch_signatures = {
            'x86': [
                b'\x4D\x5A',  # MZ (DOS/Windows)
                b'\x7FELF\x01',  # ELF 32-bit
                b'\xCE\xFA\xED\xFE',  # Mach-O 32-bit
            ],
            'x86_64': [
                b'\x7FELF\x02',  # ELF 64-bit
                b'\xCF\xFA\xED\xFE',  # Mach-O 64-bit
                b'AMD64',
                b'x86-64'
            ],
            'ARM': [
                b'\x7FELF\x01\x01',  # ELF ARM
                b'\xFE\xED\xFA\xCE',  # Mach-O ARM
                b'ARM',
                b'Cortex'
            ],
            'ARM64': [
                b'\x7FELF\x02\x0B',  # ELF AArch64
                b'\xFE\xED\xFA\xCF',  # Mach-O ARM64
                b'ARM64',
                b'AArch64'
            ],
            'PowerPC': [
                b'\x7FELF\x01\x14',  # ELF PowerPC
                b'\xFE\xED\xFA\xCE',  # Mach-O PowerPC
                b'PowerPC'
            ]
        }
       
        for arch, signatures in arch_signatures.items():
            for signature in signatures:
                if signature in file_data:
                    architectures.append(arch)
                    break
       
        return list(set(architectures))
   
    def _detect_bitness(self, file_data: bytes) -> str:
        """Detect 32-bit vs 64-bit"""
        if file_data.startswith(b'\x7FELF\x01'):
            return '32-bit'
        elif file_data.startswith(b'\x7FELF\x02'):
            return '64-bit'
        elif file_data.startswith(b'\xCE\xFA\xED\xFE'):
            return '32-bit'
        elif file_data.startswith(b'\xCF\xFA\xED\xFE'):
            return '64-bit'
        elif b'32-bit' in file_data:
            return '32-bit'
        elif b'64-bit' in file_data:
            return '64-bit'
        else:
            return 'Unknown'
   
    def _detect_endianness(self, file_data: bytes) -> str:
        """Detect endianness"""
        if file_data.startswith(b'\xFF\xFE'):  # UTF-16 LE BOM
            return 'Little-endian'
        elif file_data.startswith(b'\xFE\xFF'):  # UTF-16 BE BOM
            return 'Big-endian'
        elif file_data.startswith(b'\x00\x00\xFE\xFF'):  # UTF-32 BE BOM
            return 'Big-endian'
        elif file_data.startswith(b'\xFF\xFE\x00\x00'):  # UTF-32 LE BOM
            return 'Little-endian'
        else:
            return 'Unknown'
   
    def _detect_instruction_sets(self, file_data: bytes) -> List[str]:
        """Detect CPU instruction sets"""
        instruction_sets = []
       
        # Look for instruction set references
        isa_patterns = {
            'SSE': [b'SSE', b'SSE2', b'SSE3', b'SSE4'],
            'AVX': [b'AVX', b'AVX2', b'AVX512'],
            'NEON': [b'NEON'],
            'Altivec': [b'Altivec', b'VMX'],
            'MMX': [b'MMX'],
            '3DNow!': [b'3DNow!']
        }
       
        for isa, patterns in isa_patterns.items():
            for pattern in patterns:
                if pattern in file_data:
                    instruction_sets.append(isa)
                    break
       
        return list(set(instruction_sets))
   
    def _estimate_memory_requirements(self, file_data: bytes) -> Dict[str, Any]:
        """Estimate memory requirements"""
        memory = {
            'minimum_ram': 'Unknown',
            'recommended_ram': 'Unknown',
            'virtual_memory': 'Unknown',
            'memory_notes': []
        }
       
        file_size = len(file_data)
       
        # Very rough estimation based on file size and type
        if file_size < 1024 * 1024:  # < 1MB
            memory.update({
                'minimum_ram': '8MB',
                'recommended_ram': '16MB',
                'virtual_memory': '32MB'
            })
        elif file_size < 10 * 1024 * 1024:  # < 10MB
            memory.update({
                'minimum_ram': '64MB',
                'recommended_ram': '128MB',
                'virtual_memory': '256MB'
            })
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            memory.update({
                'minimum_ram': '256MB',
                'recommended_ram': '512MB',
                'virtual_memory': '1GB'
            })
        else:
            memory.update({
                'minimum_ram': '1GB',
                'recommended_ram': '2GB',
                'virtual_memory': '4GB'
            })
       
        # Adjust based on file type hints
        if b'3D' in file_data or b'OpenGL' in file_data or b'DirectX' in file_data:
            memory['memory_notes'].append('3D/graphics applications may require additional VRAM')
       
        if b'database' in file_data.lower() or b'SQL' in file_data:
            memory['memory_notes'].append('Database applications may benefit from additional RAM for caching')
       
        return memory
   
    def _find_external_dependencies(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find external dependencies"""
        dependencies = []
       
        # Common dependency patterns
        dependency_patterns = [
            (b'.dll', 'Windows DLL'),
            (b'.so', 'Unix Shared Object'),
            (b'.dylib', 'macOS Dynamic Library'),
            (b'.framework', 'macOS Framework'),
            (b'lib', 'Library'),
            (b'vcruntime', 'Visual C++ Runtime'),
            (b'msvcrt', 'Microsoft C Runtime'),
            (b'kernel32', 'Windows Kernel'),
            (b'user32', 'Windows User Interface'),
            (b'gdi32', 'Windows Graphics'),
        ]
       
        for pattern, description in dependency_patterns:
            if pattern in file_data:
                dependencies.append({
                    'name': description,
                    'type': 'External Library',
                    'confidence': 'Medium',
                    'description': f'References {description}'
                })
       
        return dependencies
   
    def _find_internal_dependencies(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find internal dependencies"""
        dependencies = []
       
        # Look for internal references (simplified)
        if b'import' in file_data or b'require' in file_data or b'#include' in file_data:
            dependencies.append({
                'name': 'Internal Modules',
                'type': 'Code Dependency',
                'confidence': 'Low',
                'description': 'File contains import/require statements'
            })
       
        return dependencies
   
    def _find_library_references(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find library references"""
        libraries = []
       
        # Common library names
        library_names = [
            'opengl', 'directx', 'sdl', 'glfw', 'qt', 'gtk',
            'boost', 'stl', 'stdlib', 'libc', 'libm'
        ]
       
        for lib_name in library_names:
            if lib_name.encode() in file_data.lower():
                libraries.append({
                    'name': lib_name.upper(),
                    'type': 'Library',
                    'confidence': 'Low',
                    'description': f'References {lib_name} library'
                })
       
        return libraries
   
    def _find_api_calls(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Find API calls"""
        api_calls = []
       
        # Common API patterns
        api_patterns = [
            (b'CreateWindow', 'Windows API'),
            (b'printf', 'C Standard Library'),
            (b'malloc', 'C Memory Management'),
            (b'fopen', 'C File I/O'),
            (b'socket', 'Network API'),
            (b'pthread', 'POSIX Threads'),
        ]
       
        for pattern, description in api_patterns:
            if pattern in file_data:
                api_calls.append({
                    'name': description,
                    'type': 'API Call',
                    'confidence': 'Medium',
                    'description': f'Uses {description}'
                })
       
        return api_calls
   
    def _check_dependency_issues(self, dependencies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for dependency-related issues"""
        issues = []
       
        external_deps = dependencies.get('external_dependencies', [])
        library_refs = dependencies.get('library_references', [])
       
        # Check for platform-specific dependencies on wrong platform
        current_system = self._get_system_info()
        current_os = current_system.get('os_family', '')
       
        for dep in external_deps:
            dep_name = dep.get('name', '')
           
            if '.dll' in dep_name and current_os != 'Windows':
                issues.append({
                    'type': 'Platform Dependency',
                    'severity': 'High',
                    'description': f'File requires Windows DLL but running on {current_os}',
                    'suggestion': 'Use Wine compatibility layer or find native equivalent'
                })
           
            if ('.so' in dep_name or '.dylib' in dep_name) and current_os == 'Windows':
                issues.append({
                    'type': 'Platform Dependency',
                    'severity': 'High',
                    'description': f'File requires Unix library but running on Windows',
                    'suggestion': 'Use Windows Subsystem for Linux or find Windows equivalent'
                })
       
        return issues
   
    def check_system_compatibility(self, file_path: str) -> Dict[str, Any]:
        """Check if file is compatible with current system"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read(4096)
           
            analysis = self.analyze(file_path, file_data)
            issues = analysis.get('compatibility_issues', [])
           
            # Determine overall compatibility
            high_issues = [issue for issue in issues if issue.get('severity') == 'High']
            medium_issues = [issue for issue in issues if issue.get('severity') == 'Medium']
           
            if high_issues:
                compatibility = 'Incompatible'
            elif medium_issues:
                compatibility = 'Partially Compatible'
            else:
                compatibility = 'Compatible'
           
            return {
                'compatibility': compatibility,
                'issues_found': len(issues),
                'high_severity_issues': len(high_issues),
                'medium_severity_issues': len(medium_issues),
                'details': analysis
            }
           
        except Exception as e:
            return {
                'compatibility': 'Unknown',
                'error': f"Compatibility check failed: {str(e)}"
            }
   
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            'system_compatibility_check',
            'version_compatibility',
            'architecture_analysis',
            'dependency_checking',
            'compatibility_issue_detection'
        ]