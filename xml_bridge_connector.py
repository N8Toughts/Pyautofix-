import logging
import xml.etree.ElementTree as ET
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

logger = logging.getLogger(__name__)

class XMLBridgeConnector:
    """Bridges PyAutoFix with RAGE Studio Suite Blender plugin via XML"""
   
    def __init__(self):
        self.supported_formats = {
            'import': ['ydr', 'ydd', 'yft', 'wdr', 'wdd', 'wft', 'rpf', 'dds', 'ytd', 'wtd'],
            'export': ['ydr', 'ydd', 'yft', 'wdr', 'wdd', 'wft', 'fbx', 'obj', 'dae', 'xml']
        }
       
        self.conversion_profiles = {
            'gta_v_to_blender': {
                'description': 'GTA V to Blender with materials and UVs',
                'xml_schema': 'rage_blender_v1',
                'material_conversion': True,
                'lod_preservation': True,
                'collision_data': True
            },
            'gta_iv_to_blender': {
                'description': 'GTA IV to Blender with shader conversion',
                'xml_schema': 'rage_blender_v1',
                'material_conversion': True,
                'lod_preservation': True,
                'collision_data': True
            },
            'blender_to_gta_v': {
                'description': 'Blender to GTA V with RAGE optimization',
                'xml_schema': 'blender_rage_v1',
                'material_conversion': True,
                'lod_generation': True,
                'collision_generation': True
            },
            'blender_to_gta_iv': {
                'description': 'Blender to GTA IV with format adaptation',
                'xml_schema': 'blender_rage_v1',
                'material_conversion': True,
                'lod_generation': True,
                'collision_generation': True
            }
        }

    def create_import_xml(self, source_file: str, target_format: str, options: Dict[str, Any] = None) -> str:
        """Create XML instruction file for Blender import"""
        options = options or {}
       
        # Analyze source file to determine best conversion profile
        analysis = self.analyze_source_file(source_file)
        conversion_profile = self.select_conversion_profile(analysis, target_format)
       
        # Create XML structure
        root = ET.Element("RageStudioImport")
        root.set("version", "1.0")
        root.set("schema", conversion_profile['xml_schema'])
       
        # Source information
        source_elem = ET.SubElement(root, "Source")
        ET.SubElement(source_elem, "FilePath").text = source_file
        ET.SubElement(source_elem, "Format").text = analysis.get('format', 'unknown')
        ET.SubElement(source_elem, "Game").text = analysis.get('game', 'unknown')
       
        # Target information
        target_elem = ET.SubElement(root, "Target")
        ET.SubElement(target_elem, "Format").text = target_format
        ET.SubElement(target_elem, "Application").text = "Blender"
        ET.SubElement(target_elem, "Plugin").text = "RAGE Studio Suite"
       
        # Conversion settings
        settings_elem = ET.SubElement(root, "ConversionSettings")
        ET.SubElement(settings_elem, "Profile").text = conversion_profile['description']
        ET.SubElement(settings_elem, "PreserveMaterials").text = str(conversion_profile['material_conversion'])
        ET.SubElement(settings_elem, "HandleLODs").text = str(conversion_profile.get('lod_preservation', True))
        ET.SubElement(settings_elem, "IncludeCollision").text = str(conversion_profile.get('collision_data', True))
       
        # Additional options from user
        if options:
            options_elem = ET.SubElement(root, "UserOptions")
            for key, value in options.items():
                ET.SubElement(options_elem, key).text = str(value)
       
        # Generate XML content
        xml_content = ET.tostring(root, encoding='unicode', method='xml')
        pretty_xml = self.prettify_xml(xml_content)
       
        return pretty_xml

    def create_export_xml(self, blender_file: str, target_format: str, target_game: str, options: Dict[str, Any] = None) -> str:
        """Create XML instruction file for Blender export to RAGE format"""
        options = options or {}
       
        root = ET.Element("RageStudioExport")
        root.set("version", "1.0")
        root.set("schema", "blender_rage_v1")
       
        # Source information (Blender file)
        source_elem = ET.SubElement(root, "Source")
        ET.SubElement(source_elem, "BlenderFile").text = blender_file
        ET.SubElement(source_elem, "Collection").text = options.get('collection', 'RAGE_Export')
        ET.SubElement(source_elem, "ApplyTransforms").text = str(options.get('apply_transforms', True))
       
        # Target information
        target_elem = ET.SubElement(root, "Target")
        ET.SubElement(target_elem, "Format").text = target_format
        ET.SubElement(target_elem, "Game").text = target_game
        ET.SubElement(target_elem, "OutputPath").text = options.get('output_path', '')
       
        # Export settings
        settings_elem = ET.SubElement(root, "ExportSettings")
        ET.SubElement(settings_elem, "GenerateLODs").text = str(options.get('generate_lods', True))
        ET.SubElement(settings_elem, "LODLevels").text = str(options.get('lod_levels', 4))
        ET.SubElement(settings_elem, "CreateCollision").text = str(options.get('create_collision', True))
        ET.SubElement(settings_elem, "OptimizeGeometry").text = str(options.get('optimize_geometry', True))
        ET.SubElement(settings_elem, "PreserveVertexColors").text = str(options.get('preserve_vertex_colors', True))
       
        # Material settings
        materials_elem = ET.SubElement(root, "MaterialSettings")
        ET.SubElement(materials_elem, "ConvertShaders").text = str(options.get('convert_shaders', True))
        ET.SubElement(materials_elem, "TextureFormat").text = options.get('texture_format', 'dds')
        ET.SubElement(materials_elem, "GenerateMipmaps").text = str(options.get('generate_mipmaps', True))
       
        # CodeWalker integration for live streaming
        if options.get('enable_live_streaming', False):
            streaming_elem = ET.SubElement(root, "LiveStreaming")
            ET.SubElement(streaming_elem, "Enabled").text = "true"
            ET.SubElement(streaming_elem, "CodeWalkerIntegration").text = "true"
            ET.SubElement(streaming_elem, "LightingCycles").text = str(options.get('lighting_cycles', True))
            ET.SubElement(streaming_elem, "TimeOfDay").text = str(options.get('time_of_day', True))
       
        # Generate XML
        xml_content = ET.tostring(root, encoding='unicode', method='xml')
        pretty_xml = self.prettify_xml(xml_content)
       
        return pretty_xml

    def analyze_source_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze source file to determine conversion needs"""
        analysis = {
            'format': Path(file_path).suffix.lower().lstrip('.'),
            'game': 'unknown',
            'type': 'unknown',
            'needs_conversion': True
        }
       
        # Simple format-based analysis
        rage_formats = {
            'ydr': {'game': 'gta_v', 'type': 'model'},
            'ydd': {'game': 'gta_v', 'type': 'model_dictionary'},
            'yft': {'game': 'gta_v', 'type': 'fragment_model'},
            'wdr': {'game': 'gta_iv', 'type': 'model'},
            'wdd': {'game': 'gta_iv', 'type': 'model_dictionary'},
            'wft': {'game': 'gta_iv', 'type': 'fragment_model'},
            'ytd': {'game': 'gta_v', 'type': 'texture_dictionary'},
            'wtd': {'game': 'gta_iv', 'type': 'texture_dictionary'},
            'dds': {'game': 'multiple', 'type': 'texture'}
        }
       
        file_format = analysis['format']
        if file_format in rage_formats:
            analysis.update(rage_formats[file_format])
       
        return analysis

    def select_conversion_profile(self, analysis: Dict[str, Any], target_format: str) -> Dict[str, Any]:
        """Select the appropriate conversion profile"""
        source_game = analysis.get('game', 'unknown')
       
        if source_game in ['gta_v', 'gta_iv'] and target_format == 'blender':
            profile_key = f"{source_game}_to_blender"
        elif target_format in ['ydr', 'ydd', 'yft', 'wdr', 'wdd', 'wft']:
            profile_key = f"blender_to_{source_game}"
        else:
            profile_key = "gta_v_to_blender"  # Default fallback
       
        return self.conversion_profiles.get(profile_key, self.conversion_profiles['gta_v_to_blender'])

    def prettify_xml(self, xml_string: str) -> str:
        """Prettify XML output with indentation"""
        try:
            from xml.dom import minidom
            parsed = minidom.parseString(xml_string)
            return parsed.toprettyxml(indent="  ")
        except:
            return xml_string  # Fallback to original if prettify fails

    def save_xml_instruction(self, xml_content: str, file_path: str = None) -> str:
        """Save XML instruction to file"""
        if file_path is None:
            # Create temp file
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"ragestudio_instruction_{os.getpid()}.xml")
       
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
       
        return file_path

    def execute_blender_import(self, xml_instruction_file: str, blender_executable: str = None) -> Dict[str, Any]:
        """Execute Blender with the XML import instruction"""
        result = {'success': False, 'message': '', 'output_file': ''}
       
        try:
            # Determine Blender executable
            if blender_executable is None:
                blender_executable = self.find_blender_executable()
           
            if not blender_executable:
                result['message'] = "Blender executable not found"
                return result
           
            # Create Python script to process XML instruction
            python_script = self.create_blender_import_script(xml_instruction_file)
            script_path = self.save_temp_script(python_script)
           
            # Execute Blender with script
            command = f'"{blender_executable}" --background --python "{script_path}"'
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
           
            if process.returncode == 0:
                result['success'] = True
                result['message'] = "Blender import executed successfully"
                # Parse output to get result file
                result['output_file'] = self.extract_output_from_blender_log(process.stdout)
            else:
                result['message'] = f"Blender execution failed: {process.stderr}"
           
            # Cleanup temp script
            os.unlink(script_path)
           
        except Exception as e:
            result['message'] = f"Error executing Blender import: {str(e)}"
       
        return result

    def execute_blender_export(self, xml_instruction_file: str, blender_executable: str = None) -> Dict[str, Any]:
        """Execute Blender with the XML export instruction"""
        result = {'success': False, 'message': '', 'exported_files': []}
       
        try:
            if blender_executable is None:
                blender_executable = self.find_blender_executable()
           
            if not blender_executable:
                result['message'] = "Blender executable not found"
                return result
           
            # Create Python script for export
            python_script = self.create_blender_export_script(xml_instruction_file)
            script_path = self.save_temp_script(python_script)
           
            # Execute Blender
            command = f'"{blender_executable}" --background --python "{script_path}"'
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
           
            if process.returncode == 0:
                result['success'] = True
                result['message'] = "Blender export executed successfully"
                result['exported_files'] = self.extract_exported_files(process.stdout)
            else:
                result['message'] = f"Blender export failed: {process.stderr}"
           
            # Cleanup
            os.unlink(script_path)
           
        except Exception as e:
            result['message'] = f"Error executing Blender export: {str(e)}"
       
        return result

    def find_blender_executable(self) -> Optional[str]:
        """Find Blender executable on the system"""
        # Common Blender installation paths
        possible_paths = [
            "blender",  # In PATH
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",
            "D:\\Blender\\blender.exe",
            "/usr/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender"
        ]
       
        for path in possible_paths:
            if os.path.exists(path):
                return path
       
        # Try to find via command line
        try:
            result = subprocess.run("where blender" if os.name == 'nt' else "which blender",
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
       
        return None

    def create_blender_import_script(self, xml_file: str) -> str:
        """Create Python script for Blender to process XML import"""
        return f'''
import bpy
import os
import xml.etree.ElementTree as ET
import sys

# Add RAGE Studio Suite to path (adjust as needed)
rage_studio_path = r"C:\\Path\\To\\RAGE Studio Suite"  # UPDATE THIS PATH
if rage_studio_path not in sys.path:
    sys.path.append(rage_studio_path)

try:
    from rage_studio_suite import RageImporter
   
    # Parse XML instruction
    tree = ET.parse(r"{xml_file}")
    root = tree.getroot()
   
    # Extract import parameters
    source_file = root.find("Source/FilePath").text
    target_format = root.find("Target/Format").text
    conversion_profile = root.find("ConversionSettings/Profile").text
   
    # Initialize RAGE importer
    importer = RageImporter()
   
    # Configure based on XML
    settings = {{
        'preserve_materials': root.find("ConversionSettings/PreserveMaterials").text.lower() == 'true',
        'handle_lods': root.find("ConversionSettings/HandleLODs").text.lower() == 'true',
        'include_collision': root.find("ConversionSettings/IncludeCollision").text.lower() == 'true'
    }}
   
    # Execute import
    result = importer.import_rage_asset(source_file, settings)
   
    if result['success']:
        print(f"SUCCESS:{{result['output_file']}}")
    else:
        print(f"ERROR:{{result['message']}}")
       
except Exception as e:
    print(f"IMPORT_ERROR:{{str(e)}}")
'''

    def create_blender_export_script(self, xml_file: str) -> str:
        """Create Python script for Blender to process XML export"""
        return f'''
import bpy
import os
import xml.etree.ElementTree as ET
import sys

# Add RAGE Studio Suite to path
rage_studio_path = r"C:\\Path\\To\\RAGE Studio Suite"  # UPDATE THIS PATH
if rage_studio_path not in sys.path:
    sys.path.append(rage_studio_path)

try:
    from rage_studio_suite import RageExporter
   
    # Parse XML instruction
    tree = ET.parse(r"{xml_file}")
    root = tree.getroot()
   
    # Extract export parameters
    target_format = root.find("Target/Format").text
    target_game = root.find("Target/Game").text
    output_path = root.find("Target/OutputPath").text
   
    # Export settings
    settings = {{
        'generate_lods': root.find("ExportSettings/GenerateLODs").text.lower() == 'true',
        'lod_levels': int(root.find("ExportSettings/LODLevels").text),
        'create_collision': root.find("ExportSettings/CreateCollision").text.lower() == 'true',
        'optimize_geometry': root.find("ExportSettings/OptimizeGeometry").text.lower() == 'true',
        'convert_shaders': root.find("MaterialSettings/ConvertShaders").text.lower() == 'true'
    }}
   
    # Live streaming settings
    streaming_elem = root.find("LiveStreaming")
    if streaming_elem is not None and streaming_elem.find("Enabled").text.lower() == 'true':
        settings['live_streaming'] = True
        settings['lighting_cycles'] = streaming_elem.find("LightingCycles").text.lower() == 'true'
        settings['time_of_day'] = streaming_elem.find("TimeOfDay").text.lower() == 'true'
   
    # Initialize exporter
    exporter = RageExporter()
   
    # Execute export
    result = exporter.export_rage_asset(output_path, target_format, target_game, settings)
   
    if result['success']:
        for file_path in result['exported_files']:
            print(f"EXPORTED:{{file_path}}")
    else:
        print(f"EXPORT_ERROR:{{result['message']}}")
       
except Exception as e:
    print(f"EXPORT_ERROR:{{str(e)}}")
'''

    def save_temp_script(self, script_content: str) -> str:
        """Save temporary Python script file"""
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, f"blender_script_{os.getpid()}.py")
       
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
       
        return script_path

    def extract_output_from_blender_log(self, log_output: str) -> str:
        """Extract output file path from Blender execution log"""
        for line in log_output.split('\n'):
            if line.startswith('SUCCESS:'):
                return line.replace('SUCCESS:', '').strip()
        return ''

    def extract_exported_files(self, log_output: str) -> List[str]:
        """Extract exported file paths from Blender execution log"""
        files = []
        for line in log_output.split('\n'):
            if line.startswith('EXPORTED:'):
                files.append(line.replace('EXPORTED:', '').strip())
        return files

    def get_conversion_status(self) -> Dict[str, Any]:
        """Get status of XML bridge connection"""
        blender_found = self.find_blender_executable() is not None
       
        return {
            'blender_available': blender_found,
            'blender_path': self.find_blender_executable(),
            'supported_import_formats': self.supported_formats['import'],
            'supported_export_formats': self.supported_formats['export'],
            'conversion_profiles': list(self.conversion_profiles.keys())
        }