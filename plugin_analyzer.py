"""
Blender Plugin Analyzer - Specialized analysis for Blender add-ons
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from rage_plugins.base_plugin import rage_plugins


class BlenderPluginAnalyzer(rage_plugins):
    """Specialized analyzer for Blender plugin structure and compatibility"""
   
    def __init__(self):
        super().__init__()
        self.plugin_name = "BlenderPluginAnalyzer"
        self.supported_formats = ["PY"]  # Python files for Blender
        self.version = "1.0.0"
        self.description = "Blender plugin structure, compatibility, and best practices analysis"
       
        # Blender-specific patterns
        self.operator_patterns = [
            r'bpy\.types\.Operator',
            r'class.*\(bpy\.types\.Operator\)',
            r'bl_idname\s*=\s*["\']([^"\']*)["\']',
            r'bl_label\s*=\s*["\']([^"\']*)["\']'
        ]
       
        self.blender_api_patterns = [
            r'bpy\.ops\.',
            r'bpy\.data\.',
            r'bpy\.context\.',
            r'bpy\.types\.',
            r'bpy\.utils\.',
            r'bl_',
        ]
       
    def analyze(self, file_path: str, file_data: bytes = None) -> Dict[str, Any]:
        """Analyze Blender plugin file"""
        if file_data is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        else:
            file_content = file_data.decode('utf-8', errors='ignore')
       
        results = {
            'file_path': file_path,
            'analysis_method': 'blender_plugin_analysis',
            'plugin_structure': {},
            'compatibility_analysis': {},
            'best_practices': {},
            'performance_analysis': {},
            'issues_found': []
        }
       
        # Perform Blender-specific analysis
        results.update({
            'plugin_structure': self._analyze_plugin_structure(file_path, file_content),
            'compatibility_analysis': self._analyze_compatibility(file_content),
            'best_practices': self._check_best_practices(file_content),
            'performance_analysis': self._analyze_performance(file_content),
            'issues_found': self._find_issues(results)
        })
       
        return results
   
    def _analyze_plugin_structure(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze Blender plugin structure"""
        structure = {
            'is_blender_plugin': False,
            'operators_found': [],
            'panels_found': [],
            'menus_found': [],
            'keymaps_found': [],
            'properties_found': [],
            'addon_metadata': {}
        }
       
        try:
            # Check if this is a Blender plugin
            structure['is_blender_plugin'] = self._is_blender_plugin(content)
           
            # Extract operators
            structure['operators_found'] = self._extract_operators(content)
           
            # Extract panels
            structure['panels_found'] = self._extract_panels(content)
           
            # Extract menus
            structure['menus_found'] = self._extract_menus(content)
           
            # Extract addon metadata
            structure['addon_metadata'] = self._extract_addon_metadata(content)
           
            # Check for keymaps
            structure['keymaps_found'] = self._find_keymaps(content)
           
            # Check for custom properties
            structure['properties_found'] = self._find_properties(content)
           
        except Exception as e:
            structure['error'] = f"Structure analysis failed: {str(e)}"
       
        return structure
   
    def _analyze_compatibility(self, content: str) -> Dict[str, Any]:
        """Analyze Blender version compatibility"""
        compatibility = {
            'blender_versions': [],
            'python_versions': [],
            'api_usage': {},
            'deprecated_features': [],
            'compatibility_issues': []
        }
       
        try:
            # Extract Blender version requirements
            compatibility['blender_versions'] = self._extract_blender_versions(content)
           
            # Extract Python version requirements
            compatibility['python_versions'] = self._extract_python_versions(content)
           
            # Analyze API usage
            compatibility['api_usage'] = self._analyze_api_usage(content)
           
            # Check for deprecated features
            compatibility['deprecated_features'] = self._find_deprecated_features(content)
           
            # Check compatibility issues
            compatibility['compatibility_issues'] = self._check_compatibility_issues(content)
           
        except Exception as e:
            compatibility['error'] = f"Compatibility analysis failed: {str(e)}"
       
        return compatibility
   
    def _check_best_practices(self, content: str) -> Dict[str, Any]:
        """Check Blender plugin best practices"""
        practices = {
            'code_quality': {},
            'documentation': {},
            'user_experience': {},
            'security': {},
            'recommendations': []
        }
       
        try:
            # Code quality checks
            practices['code_quality'] = self._check_code_quality(content)
           
            # Documentation checks
            practices['documentation'] = self._check_documentation(content)
           
            # User experience checks
            practices['user_experience'] = self._check_user_experience(content)
           
            # Security checks
            practices['security'] = self._check_security(content)
           
            # Generate recommendations
            practices['recommendations'] = self._generate_recommendations(practices)
           
        except Exception as e:
            practices['error'] = f"Best practices check failed: {str(e)}"
       
        return practices
   
    def _analyze_performance(self, content: str) -> Dict[str, Any]:
        """Analyze plugin performance characteristics"""
        performance = {
            'efficiency_issues': [],
            'memory_usage': {},
            'execution_time': {},
            'optimization_suggestions': []
        }
       
        try:
            # Find efficiency issues
            performance['efficiency_issues'] = self._find_efficiency_issues(content)
           
            # Estimate memory usage
            performance['memory_usage'] = self._estimate_memory_usage(content)
           
            # Estimate execution time
            performance['execution_time'] = self._estimate_execution_time(content)
           
            # Generate optimization suggestions
            performance['optimization_suggestions'] = self._generate_optimization_suggestions(content)
           
        except Exception as e:
            performance['error'] = f"Performance analysis failed: {str(e)}"
       
        return performance
   
    def _find_issues(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find issues from analysis results"""
        issues = []
       
        structure = analysis_results.get('plugin_structure', {})
        compatibility = analysis_results.get('compatibility_analysis', {})
        practices = analysis_results.get('best_practices', {})
        performance = analysis_results.get('performance_analysis', {})
       
        # Structure issues
        if not structure.get('is_blender_plugin'):
            issues.append({
                'type': 'Not a Blender Plugin',
                'severity': 'High',
                'description': 'File does not appear to be a Blender plugin',
                'suggestion': 'Add required Blender plugin structure (bl_info, register/unregister functions)'
            })
       
        # Compatibility issues
        comp_issues = compatibility.get('compatibility_issues', [])
        issues.extend(comp_issues)
       
        deprecated_features = compatibility.get('deprecated_features', [])
        for feature in deprecated_features:
            issues.append({
                'type': 'Deprecated Feature',
                'severity': 'Medium',
                'description': f'Uses deprecated feature: {feature}',
                'suggestion': 'Update to use current Blender API'
            })
       
        # Best practices issues
        code_quality = practices.get('code_quality', {})
        if not code_quality.get('has_register_function'):
            issues.append({
                'type': 'Missing Register Function',
                'severity': 'High',
                'description': 'Plugin missing register() function',
                'suggestion': 'Add register() function to properly initialize the plugin'
            })
       
        if not code_quality.get('has_unregister_function'):
            issues.append({
                'type': 'Missing Unregister Function',
                'severity': 'High',
                'description': 'Plugin missing unregister() function',
                'suggestion': 'Add unregister() function to properly clean up the plugin'
            })
       
        # Performance issues
        efficiency_issues = performance.get('efficiency_issues', [])
        issues.extend(efficiency_issues)
       
        return sorted(issues, key=lambda x: {'High': 3, 'Medium': 2, 'Low': 1}.get(x['severity'], 0), reverse=True)
   
    def _is_blender_plugin(self, content: str) -> bool:
        """Check if file is a Blender plugin"""
        # Check for bl_info dictionary (required for Blender plugins)
        if 'bl_info' in content:
            return True
       
        # Check for Blender operator classes
        if 'bpy.types.Operator' in content:
            return True
       
        # Check for register/unregister functions
        if 'def register()' in content and 'def unregister()' in content:
            return True
       
        return False
   
    def _extract_operators(self, content: str) -> List[Dict[str, Any]]:
        """Extract Blender operators from content"""
        operators = []
       
        try:
            # Parse Python AST
            tree = ast.parse(content)
           
            # Find operator classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this is an operator class
                    is_operator = False
                    bl_idname = None
                    bl_label = None
                   
                    # Check base classes
                    for base in node.bases:
                        if isinstance(base, ast.Attribute):
                            if base.attr == 'Operator':
                                is_operator = True
                        elif isinstance(base, ast.Name):
                            if base.id == 'Operator':
                                is_operator = True
                   
                    # Extract operator properties
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id == 'bl_idname' and isinstance(item.value, ast.Str):
                                        bl_idname = item.value.s
                                    elif target.id == 'bl_label' and isinstance(item.value, ast.Str):
                                        bl_label = item.value.s
                   
                    if is_operator:
                        operators.append({
                            'name': node.name,
                            'bl_idname': bl_idname,
                            'bl_label': bl_label,
                            'line_number': node.lineno
                        })
                       
        except Exception as e:
            # Fallback to regex if AST parsing fails
            operator_pattern = r'class\s+(\w+)\s*\(\s*.*Operator\s*\)'
            matches = re.finditer(operator_pattern, content)
           
            for match in matches:
                operators.append({
                    'name': match.group(1),
                    'bl_idname': 'Unknown',
                    'bl_label': 'Unknown',
                    'line_number': content[:match.start()].count('\n') + 1
                })
       
        return operators
   
    def _extract_panels(self, content: str) -> List[Dict[str, Any]]:
        """Extract Blender panels from content"""
        panels = []
       
        # Look for panel classes
        panel_pattern = r'class\s+(\w+)\s*\(\s*.*Panel\s*\)'
        matches = re.finditer(panel_pattern, content)
       
        for match in matches:
            panels.append({
                'name': match.group(1),
                'line_number': content[:match.start()].count('\n') + 1
            })
       
        return panels
   
    def _extract_menus(self, content: str) -> List[Dict[str, Any]]:
        """Extract Blender menus from content"""
        menus = []
       
        # Look for menu classes
        menu_pattern = r'class\s+(\w+)\s*\(\s*.*Menu\s*\)'
        matches = re.finditer(menu_pattern, content)
       
        for match in matches:
            menus.append({
                'name': match.group(1),
                'line_number': content[:match.start()].count('\n') + 1
            })
       
        return menus
   
    def _extract_addon_metadata(self, content: str) -> Dict[str, Any]:
        """Extract addon metadata from bl_info"""
        metadata = {}
       
        # Look for bl_info dictionary
        bl_info_match = re.search(r'bl_info\s*=\s*\{([^}]+)\}', content)
        if bl_info_match:
            bl_info_content = bl_info_match.group(1)
           
            # Extract common bl_info fields
            fields = {
                'name': r"'name'\s*:\s*'([^']+)'",
                'author': r"'author'\s*:\s*'([^']+)'",
                'version': r"'version'\s*:\s*\(([^)]+)\)",
                'blender': r"'blender'\s*:\s*\(([^)]+)\)",
                'description': r"'description'\s*:\s*'([^']+)'",
                'category': r"'category'\s*:\s*'([^']+)'"
            }
           
            for field, pattern in fields.items():
                match = re.search(pattern, bl_info_content)
                if match:
                    metadata[field] = match.group(1).strip()
       
        return metadata
   
    def _find_keymaps(self, content: str) -> List[Dict[str, Any]]:
        """Find keymap registrations"""
        keymaps = []
       
        # Look for keymap registration patterns
        keymap_patterns = [
            r'bpy\.context\.wm\.keyconfigs\.addon\.keymaps\.new\(',
            r'wm\.keyconfigs\.addon\.keymaps\.new\('
        ]
       
        for pattern in keymap_patterns:
            if re.search(pattern, content):
                keymaps.append({
                    'type': 'Keymap',
                    'description': 'Keymap registration found'
                })
                break
       
        return keymaps
   
    def _find_properties(self, content: str) -> List[Dict[str, Any]]:
        """Find custom property definitions"""
        properties = []
       
        # Look for property declarations
        prop_pattern = r'bpy\.types\.\w+\.bl_rna\.properties\.new\('
        matches = re.finditer(prop_pattern, content)
       
        for match in matches:
            properties.append({
                'type': 'Custom Property',
                'line_number': content[:match.start()].count('\n') + 1
            })
       
        return properties
   
    def _extract_blender_versions(self, content: str) -> List[str]:
        """Extract Blender version requirements"""
        versions = []
       
        # Look for version requirements in bl_info
        bl_info_match = re.search(r"'blender'\s*:\s*\(([^)]+)\)", content)
        if bl_info_match:
            version_str = bl_info_match.group(1)
            versions.append(f"Blender {version_str}")
       
        # Look for version comments
        version_comments = re.findall(r'#.*[Bb]lender\s+\d+\.\d+', content)
        versions.extend(version_comments)
       
        return versions
   
    def _extract_python_versions(self, content: str) -> List[str]:
        """Extract Python version requirements"""
        versions = []
       
        # Look for Python version requirements
        py_versions = re.findall(r'#.*[Pp]ython\s+\d+\.\d+', content)
        versions.extend(py_versions)
       
        # Check for version checks in code
        if 'sys.version_info' in content:
            versions.append('Uses sys.version_info for version checking')
       
        return versions
   
    def _analyze_api_usage(self, content: str) -> Dict[str, Any]:
        """Analyze Blender API usage"""
        api_usage = {
            'bpy_modules_used': [],
            'common_patterns': [],
            'api_complexity': 'Low'
        }
       
        # Check for bpy module usage
        bpy_modules = ['bpy.ops', 'bpy.data', 'bpy.context', 'bpy.types', 'bpy.utils']
       
        for module in bpy_modules:
            if module in content:
                api_usage['bpy_modules_used'].append(module)
       
        # Check for common API patterns
        patterns = [
            (r'bpy\.ops\.\w+\.\w+\(', 'Operator Calls'),
            (r'bpy\.data\.\w+\["', 'Data Access'),
            (r'bpy\.context\.\w+', 'Context Access'),
            (r'@classmethod', 'Class Methods'),
            (r'@staticmethod', 'Static Methods'),
        ]
       
        for pattern, description in patterns:
            if re.search(pattern, content):
                api_usage['common_patterns'].append(description)
       
        # Estimate API complexity
        operator_calls = len(re.findall(r'bpy\.ops\.\w+\.\w+\(', content))
        data_access = len(re.findall(r'bpy\.data\.\w+\["', content))
       
        total_api_calls = operator_calls + data_access
       
        if total_api_calls > 20:
            api_usage['api_complexity'] = 'High'
        elif total_api_calls > 10:
            api_usage['api_complexity'] = 'Medium'
        else:
            api_usage['api_complexity'] = 'Low'
       
        return api_usage
   
    def _find_deprecated_features(self, content: str) -> List[str]:
        """Find deprecated Blender features"""
        deprecated = []
       
        # Common deprecated features (this would need regular updating)
        deprecated_patterns = [
            # Add actual deprecated Blender API patterns here
            r'bpy\.ops\.scene\.',  # Example pattern
            r'Mesh\.polygons\[',   # Example pattern
        ]
       
        for pattern in deprecated_patterns:
            if re.search(pattern, content):
                deprecated.append(f"Uses deprecated pattern: {pattern}")
       
        return deprecated
   
    def _check_compatibility_issues(self, content: str) -> List[Dict[str, Any]]:
        """Check for compatibility issues"""
        issues = []
       
        # Check for Python 2 compatibility issues
        if 'print ' in content and 'print(' not in content:
            issues.append({
                'type': 'Python 2 Print Statement',
                'severity': 'Medium',
                'description': 'Uses Python 2 print statement',
                'suggestion': 'Update to Python 3 print function'
            })
       
        # Check for old Blender API patterns
        if 'Blender.' in content:
            issues.append({
                'type': 'Old Blender API',
                'severity': 'High',
                'description': 'Uses old Blender API (Blender module)',
                'suggestion': 'Update to use bpy module'
            })
       
        return issues
   
    def _check_code_quality(self, content: str) -> Dict[str, Any]:
        """Check code quality aspects"""
        quality = {
            'has_register_function': 'def register()' in content or 'def register(' in content,
            'has_unregister_function': 'def unregister()' in content or 'def unregister(' in content,
            'has_proper_docstrings': False,
            'code_complexity': 'Low',
            'error_handling': 'Basic'
        }
       
        # Check for docstrings
        if '"""' in content or "'''" in content:
            quality['has_proper_docstrings'] = True
       
        # Estimate code complexity
        line_count = content.count('\n')
        function_count = len(re.findall(r'def\s+\w+\(', content))
        class_count = len(re.findall(r'class\s+\w+', content))
       
        if line_count > 500 or function_count > 20 or class_count > 10:
            quality['code_complexity'] = 'High'
        elif line_count > 200 or function_count > 10 or class_count > 5:
            quality['code_complexity'] = 'Medium'
       
        # Check error handling
        if 'try:' in content and 'except:' in content:
            quality['error_handling'] = 'Good'
        elif 'except' in content:
            quality['error_handling'] = 'Basic'
       
        return quality
   
    def _check_documentation(self, content: str) -> Dict[str, Any]:
        """Check documentation quality"""
        documentation = {
            'has_module_docstring': False,
            'has_class_docstrings': False,
            'has_function_docstrings': False,
            'documentation_completeness': 'Poor'
        }
       
        # Check for module docstring
        lines = content.split('\n')
        if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
            documentation['has_module_docstring'] = True
       
        # Check for class and function docstrings (simplified)
        if '"""' in content or "'''" in content:
            documentation['has_class_docstrings'] = True
            documentation['has_function_docstrings'] = True
       
        # Estimate documentation completeness
        doc_count = content.count('"""') + content.count("'''")
        if doc_count > 10:
            documentation['documentation_completeness'] = 'Excellent'
        elif doc_count > 5:
            documentation['documentation_completeness'] = 'Good'
        elif doc_count > 2:
            documentation['documentation_completeness'] = 'Fair'
       
        return documentation
   
    def _check_user_experience(self, content: str) -> Dict[str, Any]:
        """Check user experience aspects"""
        ux = {
            'has_ui_elements': False,
            'has_tooltips': False,
            'has_proper_labels': False,
            'user_friendliness': 'Basic'
        }
       
        # Check for UI elements
        if 'bl_label' in content:
            ux['has_ui_elements'] = True
            ux['has_proper_labels'] = True
       
        # Check for tooltips
        if 'bl_description' in content or 'tooltip' in content.lower():
            ux['has_tooltips'] = True
       
        # Estimate user friendliness
        if ux['has_tooltips'] and ux['has_proper_labels']:
            ux['user_friendliness'] = 'Good'
        elif ux['has_ui_elements']:
            ux['user_friendliness'] = 'Fair'
       
        return ux
   
    def _check_security(self, content: str) -> Dict[str, Any]:
        """Check security aspects"""
        security = {
            'has_exec_calls': False,
            'has_file_operations': False,
            'has_network_calls': False,
            'security_risk': 'Low'
        }
       
        # Check for potentially dangerous operations
        dangerous_patterns = [
            r'eval\(',
            r'exec\(',
            r'__import__\(',
            r'open\(',
            r'urllib\.',
            r'requests\.',
            r'socket\.'
        ]
       
        risk_found = False
        for pattern in dangerous_patterns:
            if re.search(pattern, content):
                risk_found = True
                if pattern in [r'eval\(', r'exec\(', r'__import__\(']:
                    security['has_exec_calls'] = True
                elif pattern == r'open\(':
                    security['has_file_operations'] = True
                elif pattern in [r'urllib\.', r'requests\.', r'socket\.']:
                    security['has_network_calls'] = True
       
        if security['has_exec_calls']:
            security['security_risk'] = 'High'
        elif risk_found:
            security['security_risk'] = 'Medium'
       
        return security
   
    def _generate_recommendations(self, practices: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on best practices analysis"""
        recommendations = []
       
        code_quality = practices.get('code_quality', {})
        documentation = practices.get('documentation', {})
        user_experience = practices.get('user_experience', {})
        security = practices.get('security', {})
       
        # Code quality recommendations
        if not code_quality.get('has_register_function'):
            recommendations.append("Add a register() function for proper plugin initialization")
       
        if not code_quality.get('has_unregister_function'):
            recommendations.append("Add an unregister() function for proper cleanup")
       
        if code_quality.get('error_handling') == 'Basic':
            recommendations.append("Improve error handling with specific exception types")
       
        # Documentation recommendations
        if not documentation.get('has_module_docstring'):
            recommendations.append("Add a module-level docstring")
       
        if documentation.get('documentation_completeness') in ['Poor', 'Fair']:
            recommendations.append("Improve documentation coverage for classes and functions")
       
        # User experience recommendations
        if not user_experience.get('has_tooltips'):
            recommendations.append("Add tooltips to UI elements for better user guidance")
       
        # Security recommendations
        if security.get('security_risk') == 'High':
            recommendations.append("Review use of eval/exec for potential security issues")
       
        return recommendations
   
    def _find_efficiency_issues(self, content: str) -> List[Dict[str, Any]]:
        """Find efficiency issues"""
        issues = []
       
        # Look for common efficiency problems in Blender plugins
        efficiency_patterns = [
            (r'bpy\.data\.objects\.new\s*\([^)]+\)[^;]+bpy\.context\.scene\.objects\.link',
             'Object Creation Inefficiency',
             'Create and link objects in single operation when possible'),
           
            (r'for\s+\w+\s+in\s+bpy\.data\.\w+[:]',
             'Inefficient Data Iteration',
             'Consider using list comprehension or generator expressions'),
           
            (r'bpy\.ops\.\w+\.\w+\([^)]*\)\s*;\s*bpy\.ops\.\w+\.\w+\([^)]*\)',
             'Multiple Operator Calls',
             'Batch operations or use lower-level API when possible'),
        ]
       
        for pattern, issue, suggestion in efficiency_patterns:
            if re.search(pattern, content):
                issues.append({
                    'type': issue,
                    'severity': 'Low',
                    'description': f'Found pattern: {pattern}',
                    'suggestion': suggestion
                })
       
        return issues
   
    def _estimate_memory_usage(self, content: str) -> Dict[str, Any]:
        """Estimate memory usage patterns"""
        memory = {
            'estimated_usage': 'Low',
            'memory_patterns': [],
            'suggestions': []
        }
       
        # Look for memory-intensive patterns
        if 'bpy.data.meshes.new' in content:
            memory['memory_patterns'].append('Mesh creation')
            memory['estimated_usage'] = 'Medium'
       
        if 'bpy.data.images.new' in content:
            memory['memory_patterns'].append('Image creation')
            memory['estimated_usage'] = 'High'
       
        if 'import numpy' in content or 'import array' in content:
            memory['memory_patterns'].append('Large data structures')
            memory['estimated_usage'] = 'High'
       
        # Generate suggestions
        if memory['estimated_usage'] == 'High':
            memory['suggestions'].append('Consider using data cleanup and memory management techniques')
       
        return memory
   
    def _estimate_execution_time(self, content: str) -> Dict[str, Any]:
        """Estimate execution time characteristics"""
        execution = {
            'estimated_time': 'Fast',
            'bottlenecks': [],
            'optimization_areas': []
        }
       
        # Look for potential performance bottlenecks
        if 'bpy.ops.mesh.' in content:
            execution['bottlenecks'].append('Mesh operations')
            execution['estimated_time'] = 'Medium'
       
        if 'bpy.ops.object.' in content and 'mode_set' in content:
            execution['bottlenecks'].append('Mode changes')
            execution['estimated_time'] = 'Slow'
       
        if 'for' in content and 'bpy.data' in content:
            execution['bottlenecks'].append('Data iteration in loops')
            execution['optimization_areas'].append('Optimize data access patterns')
       
        return execution
   
    def _generate_optimization_suggestions(self, content: str) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
       
        # Performance suggestions
        if 'bpy.ops.' in content and content.count('bpy.ops.') > 5:
            suggestions.append("Consider batching operator calls or using lower-level API")
       
        if 'for ' in content and 'bpy.data.' in content:
            suggestions.append("Precompute data outside loops when possible")
       
        if 'import ' in content and content.count('import ') > 10:
            suggestions.append("Consolidate imports and use specific imports")
       
        return suggestions
   
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            'blender_plugin_detection',
            'operator_analysis',
            'compatibility_checking',
            'best_practices_validation',
            'performance_analysis'
        ]