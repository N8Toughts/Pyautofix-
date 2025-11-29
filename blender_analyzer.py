import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)

class BlenderPluginAnalyzer:
    """Specialized analyzer for Blender plugin multi-file testing"""
  
    def __init__(self):
        self.operator_patterns = [
            r'bpy\.types\.Operator',
            r'class.*\(bpy\.types\.Operator\)',
            r'bl_idname\s*=\s*["\']([^"\']*)["\']',
            r'bl_label\s*=\s*["\']([^"\']*)["\']'
        ]
  
    def analyze_plugin_structure(self, plugin_dir: str) -> Dict[str, Any]:
        """Analyze complete Blender plugin structure"""
        plugin_path = Path(plugin_dir)
      
        if not plugin_path.exists():
            return {'error': f'Plugin directory not found: {plugin_dir}'}
      
        analysis = {
            'plugin_name': plugin_path.name,
            'total_files': 0,
            'python_files': 0,
            'operators_found': [],
            'dependencies': set(),
            'file_analysis': {},
            'summary': {}
        }
      
        # Analyze all Python files in the plugin
        python_files = list(plugin_path.rglob("*.py"))
        analysis['python_files'] = len(python_files)
        analysis['total_files'] = len(list(plugin_path.rglob("*")))
      
        for py_file in python_files:
            file_analysis = self.analyze_plugin_file(py_file, plugin_path)
            analysis['file_analysis'][str(py_file)] = file_analysis
          
            # Collect operators and dependencies
            analysis['operators_found'].extend(file_analysis.get('operators', []))
            analysis['dependencies'].update(file_analysis.get('dependencies', []))
      
        # Convert set to list for JSON serialization
        analysis['dependencies'] = list(analysis['dependencies'])
      
        # Generate summary
        analysis['summary'] = self.generate_plugin_summary(analysis)
      
        return analysis
  
    def analyze_plugin_file(self, file_path: Path, plugin_root: Path) -> Dict[str, Any]:
        """Analyze individual plugin file"""
        analysis = {
            'file_name': file_path.name,
            'relative_path': str(file_path.relative_to(plugin_root)),
            'operators': [],
            'dependencies': set(),
            'has_register': False,
            'has_unregister': False,
            'line_count': 0
        }
      
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
          
            analysis['line_count'] = len(content.splitlines())
          
            # Parse Python AST
            tree = ast.parse(content)
          
            # Extract operators
            analysis['operators'] = self.extract_operators(content, tree)
          
            # Extract dependencies
            analysis['dependencies'] = self.extract_dependencies(content, tree)
          
            # Check for register/unregister functions
            analysis['has_register'] = 'def register' in content
            analysis['has_unregister'] = 'def unregister' in content
          
            # Check for bl_info
            analysis['has_bl_info'] = 'bl_info' in content
          
        except Exception as e:
            analysis['error'] = str(e)
      
        # Convert set to list
        analysis['dependencies'] = list(analysis['dependencies'])
      
        return analysis
  
    def extract_operators(self, content: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract Blender operators from file"""
        operators = []
      
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this is an operator class
                class_info = self._analyze_class_for_operator(node, content)
                if class_info:
                    operators.append(class_info)
      
        return operators
  
    def _analyze_class_for_operator(self, node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """Analyze if a class is a Blender operator"""
        class_info = {
            'name': node.name,
            'base_classes': [],
            'bl_idname': None,
            'bl_label': None,
            'line': node.lineno
        }
      
        # Check base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info['base_classes'].append(base.id)
            elif isinstance(base, ast.Attribute):
                class_info['base_classes'].append(self._get_attr_name(base))
      
        # Check if this is an operator class
        is_operator = any('Operator' in base for base in class_info['base_classes'])
      
        if is_operator:
            # Extract operator properties from class body
            class_info.update(self._extract_operator_properties(node, content))
            return class_info
      
        return None
  
    def _extract_operator_properties(self, node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """Extract operator properties like bl_idname, bl_label"""
        properties = {}
      
        # Simple regex extraction (would be more robust with AST analysis)
        bl_idname_match = re.search(r'bl_idname\s*=\s*["\']([^"\']*)["\']', content)
        if bl_idname_match:
            properties['bl_idname'] = bl_idname_match.group(1)
      
        bl_label_match = re.search(r'bl_label\s*=\s*["\']([^"\']*)["\']', content)
        if bl_label_match:
            properties['bl_label'] = bl_label_match.group(1)
      
        return properties
  
    def extract_dependencies(self, content: str, tree: ast.AST) -> Set[str]:
        """Extract dependencies from imports and usage"""
        dependencies = set()
      
        # Extract from imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    dependencies.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split('.')[0])
      
        # Extract Blender-specific dependencies
        blender_patterns = [r'bpy\.ops\.(\w+)', r'bpy\.data\.(\w+)', r'bpy\.context\.(\w+)']
        for pattern in blender_patterns:
            matches = re.findall(pattern, content)
            dependencies.update(matches)
      
        return dependencies
  
    def _get_attr_name(self, node: ast.AST) -> str:
        """Get attribute name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attr_name(node.value)}.{node.attr}"
        return "Unknown"
  
    def generate_plugin_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plugin summary"""
        return {
            'total_operators': len(analysis['operators_found']),
            'total_dependencies': len(analysis['dependencies']),
            'files_with_register': sum(1 for fa in analysis['file_analysis'].values() if fa.get('has_register')),
            'files_with_unregister': sum(1 for fa in analysis['file_analysis'].values() if fa.get('has_unregister')),
            'files_with_bl_info': sum(1 for fa in analysis['file_analysis'].values() if fa.get('has_bl_info'))
        }