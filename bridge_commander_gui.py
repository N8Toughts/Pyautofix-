#!/usr/bin/env python3

"""
PyAutoFix Bridge Commander - Advanced AI-Powered Analysis Hub
Enhanced with Multi-File Plugin Testing, Cross-Script Analysis,
and RAGE Evolutionary Analyzer Integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from datetime import datetime
import importlib.util
import sys
import ast
import inspect
import re

# Import PyAutoFix core
try:
    from pyautofix.core.engine import AICorrectionEngine
    from pyautofix.core.learning_system import LearningSystem
    from pyautofix.core.external_interface import ExternalAnalyzerInterface
    PYAUTOFIX_AVAILABLE = True
except ImportError:
    PYAUTOFIX_AVAILABLE = False
    # Fallback - create minimal classes
    class AICorrectionEngine:
        def __init__(self, config=None):
            self.config = config or {}
            self.available = False

    class LearningSystem:
        def __init__(self):
            self.available = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

# Import plugin system
try:
    from rage_plugins.plugin_manager import PluginManager
    from rage_plugins.format_discovery import FormatDiscoveryEngine
    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError:
    PLUGIN_SYSTEM_AVAILABLE = False
    logging.warning("RAGE Plugin system not available, using legacy analyzer")

class BlenderPluginAnalyzer:
    """Specialized analyzer for Blender plugin multi-file testing"""
   
    def __init__(self):
        self.operator_patterns = [
            r'bpy\.types\.Operator',
            r'class.*\(bpy\.types\.Operator\)',
            r'bl_idname\s*=\s*["\']([^"\']*)["\']',
            r'bl_label\s*=\s*["\']([^"\']*)["\']'
        ]
        self.dependency_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'bpy\.ops\.(\w+)\.',
            r'bpy\.data\.(\w+)',
            r'bpy\.context\.(\w+)'
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
            'file_interactions': {},
            'potential_issues': [],
            'cross_references': [],
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
           
            # Collect operators
            analysis['operators_found'].extend(file_analysis.get('operators', []))
           
            # Collect dependencies
            analysis['dependencies'].update(file_analysis.get('dependencies', []))
           
            # Collect potential issues
            analysis['potential_issues'].extend(file_analysis.get('issues', []))

        # Analyze cross-file interactions
        analysis['cross_references'] = self.analyze_cross_references(analysis['file_analysis'])
       
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
            'issues': [],
            'functions': [],
            'classes': [],
            'imports': [],
            'file_size': file_path.stat().st_size,
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
           
            # Extract functions and classes
            analysis['functions'] = self.extract_functions(tree)
            analysis['classes'] = self.extract_classes(tree)
            analysis['imports'] = self.extract_imports(tree)
           
            # Check for common issues
            analysis['issues'] = self.check_common_issues(content, tree, file_path.name)
           
        except Exception as e:
            analysis['issues'].append(f'Parse error: {str(e)}')

        return analysis

    def extract_operators(self, content: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract Blender operators from file"""
        operators = []

        # Look for operator classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
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
                        class_info['base_classes'].append(self.get_attr_name(base))

                # Check for operator attributes
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attr_name = target.id
                                if isinstance(item.value, ast.Str):
                                    attr_value = item.value.s
                                    if attr_name == 'bl_idname':
                                        class_info['bl_idname'] = attr_value
                                    elif attr_name == 'bl_label':
                                        class_info['bl_label'] = attr_value

                # Check if this is an operator class
                if any('Operator' in base for base in class_info['base_classes']):
                    operators.append(class_info)

        return operators

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

        # Extract from patterns in content
        for pattern in self.dependency_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match and match not in ['bpy', 'os', 'sys', 'json', 'math']:  # Common built-ins
                    dependencies.add(match)

        return dependencies

    def extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args]
                })
        return functions

    def extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'bases': [self.get_attr_name(base) for base in node.bases]
                })
        return classes

    def extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'type': 'import',
                        'module': name.name,
                        'alias': name.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    'type': 'from_import',
                    'module': node.module,
                    'names': [name.name for name in node.names],
                    'line': node.lineno
                })
        return imports

    def check_common_issues(self, content: str, tree: ast.AST, filename: str) -> List[str]:
        """Check for common Blender plugin issues"""
        issues = []

        # Check for register/unregister functions
        has_register = any(node.name == 'register' for node in ast.walk(tree)
                          if isinstance(node, ast.FunctionDef))
        has_unregister = any(node.name == 'unregister' for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef))

        if not has_register:
            issues.append("Missing 'register' function")
        if not has_unregister:
            issues.append("Missing 'unregister' function")

        # Check for operator registration
        if 'register_class' not in content and has_register:
            issues.append("register function doesn't register classes")

        # Check for proper bl_info
        if 'bl_info' not in content and filename in ['__init__.py', 'plugin_main.py']:
            issues.append("Missing bl_info dictionary")

        return issues

    def analyze_cross_references(self, file_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze cross-references between files"""
        cross_refs = []

        # Collect all operators and functions
        all_operators = {}
        all_functions = {}

        for file_path, analysis in file_analysis.items():
            for op in analysis.get('operators', []):
                if op.get('bl_idname'):
                    all_operators[op['bl_idname']] = {
                        'file': file_path,
                        'operator': op
                    }
           
            for func in analysis.get('functions', []):
                all_functions[func['name']] = {
                    'file': file_path,
                    'function': func
                }

        # Check for cross-file references
        for file_path, analysis in file_analysis.items():
            file_content = ""
            try:
                with open(file_path, 'r') as f:
                    file_content = f.read()
            except:
                continue

            # Check for operator calls
            for op_id, op_info in all_operators.items():
                if op_info['file'] != file_path and op_id in file_content:
                    cross_refs.append({
                        'type': 'operator_call',
                        'source_file': file_path,
                        'target_file': op_info['file'],
                        'operator': op_id,
                        'description': f'Operator {op_id} called from different file'
                    })

            # Check for function calls
            for func_name, func_info in all_functions.items():
                if func_info['file'] != file_path and f"{func_name}(" in file_content:
                    cross_refs.append({
                        'type': 'function_call',
                        'source_file': file_path,
                        'target_file': func_info['file'],
                        'function': func_name,
                        'description': f'Function {func_name} called from different file'
                    })

        return cross_refs

    def generate_plugin_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plugin summary"""
        total_issues = len(analysis['potential_issues'])
        total_operators = len(analysis['operators_found'])
        total_dependencies = len(analysis['dependencies'])
        total_cross_refs = len(analysis['cross_references'])
       
        health_score = 100
        health_score -= total_issues * 5
        health_score = max(0, health_score)

        return {
            'health_score': health_score,
            'total_issues': total_issues,
            'total_operators': total_operators,
            'total_dependencies': total_dependencies,
            'total_cross_references': total_cross_refs,
            'file_count': analysis['python_files'],
            'assessment': self.assess_plugin_health(health_score)
        }

    def assess_plugin_health(self, score: int) -> str:
        """Assess plugin health based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"

    def get_attr_name(self, node: ast.AST) -> str:
        """Get attribute name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_attr_name(node.value)}.{node.attr}"
        return "Unknown"


class RAGEAnalyzerIntegration:
    """Handles integration with RAGE analyzer using plugin system with fallback"""
   
    def __init__(self):
        self.plugin_manager = None
        self.format_discovery = None
        self.legacy_analyzer = None
        self.available = False
       
        self._initialize_analyzer()
   
    def _initialize_analyzer(self):
        """Initialize RAGE analyzer with plugin system fallback"""
        # Try new plugin system first
        if PLUGIN_SYSTEM_AVAILABLE:
            try:
                self.plugin_manager = PluginManager()
                self.format_discovery = FormatDiscoveryEngine()
                self.available = True
                logging.info("RAGE Plugin system initialized successfully")
                return
            except Exception as e:
                logging.warning(f"RAGE Plugin system failed: {e}")
       
        # Fallback to legacy analyzer
        try:
            self.legacy_analyzer = self._initialize_legacy_analyzer()
            self.available = True
            logging.info("Legacy RAGE analyzer initialized as fallback")
        except Exception as e:
            logging.error(f"All RAGE analyzer initialization failed: {e}")
            self.available = False
   
    def _initialize_legacy_analyzer(self):
        """Initialize legacy RAGE analyzer"""
        possible_paths = [
            'file_analyzer.py',
            str(Path(__file__).parent.parent / 'file_analyzer.py'),
            str(Path(__file__).parent / 'file_analyzer.py')
        ]

        for analyzer_path in possible_paths:
            if os.path.exists(analyzer_path):
                spec = importlib.util.spec_from_file_location("file_analyzer", analyzer_path)
                if spec is not None:
                    rage_module = importlib.util.module_from_spec(spec)
                    sys.modules["file_analyzer"] = rage_module
                    spec.loader.exec_module(rage_module)

                    if hasattr(rage_module, 'RAGEAnalyzerExternal'):
                        return rage_module.RAGEAnalyzerExternal()
       
        raise ImportError("No legacy RAGE analyzer found")
   
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file using available analyzer system"""
        if not self.available:
            return {'error': 'No RAGE analyzer available'}
       
        # Try plugin system first
        if self.plugin_manager and self.format_discovery:
            try:
                return self._analyze_with_plugins(file_path)
            except Exception as e:
                logging.warning(f"Plugin analysis failed, falling back: {e}")
       
        # Fallback to legacy analyzer
        if self.legacy_analyzer:
            try:
                return self.legacy_analyzer.analyze_file(file_path)
            except Exception as e:
                logging.error(f"Legacy analyzer failed: {e}")
       
        return {'error': 'All analysis methods failed'}
   
    def _analyze_with_plugins(self, file_path: str) -> Dict[str, Any]:
        """Analyze file using plugin system"""
        results = {
            'file_path': file_path,
            'analysis_method': 'plugin_system',
            'format_candidates': [],
            'primary_format': None,
            'confidence': 0.0,
            'metadata': {},
            'rdr1_specific': {}
        }
       
        # Use format discovery for aggressive analysis
        discovery_results = self.format_discovery.analyze_file_aggressive(file_path)
       
        if discovery_results.get('candidates'):
            candidates = discovery_results['candidates']
            results['format_candidates'] = candidates
           
            # Select primary format (highest confidence)
            if candidates:
                primary = max(candidates, key=lambda x: x.get('confidence', 0))
                results['primary_format'] = primary.get('format')
                results['confidence'] = primary.get('confidence', 0)
                results['metadata'] = primary.get('metadata', {})
               
                # RDR1-specific processing
                if primary.get('format') in ['WVD', 'WTD', 'WFT']:
                    results['rdr1_specific'] = self._process_rdr1_format(file_path, primary)
       
        return results
   
    def _process_rdr1_format(self, file_path: str, format_info: Dict) -> Dict[str, Any]:
        """Process RDR1-specific formats"""
        return {
            'format_type': format_info.get('format'),
            'texture_info': self._extract_texture_info(file_path),
            'model_info': self._extract_model_info(file_path),
            'compatibility': self._check_rdr1_compatibility(format_info)
        }
   
    def _extract_texture_info(self, file_path: str) -> Dict[str, Any]:
        """Extract texture information from RDR1 files"""
        # Placeholder - would integrate actual texture extraction
        return {
            'texture_count': 0,
            'dimensions': 'Unknown',
            'format': 'Unknown',
            'mipmaps': 0
        }
   
    def _extract_model_info(self, file_path: str) -> Dict[str, Any]:
        """Extract model information from RDR1 files"""
        # Placeholder - would integrate actual model extraction
        return {
            'vertex_count': 0,
            'triangle_count': 0,
            'material_count': 0,
            'bone_count': 0
        }
   
    def _check_rdr1_compatibility(self, format_info: Dict) -> Dict[str, Any]:
        """Check RDR1 format compatibility"""
        return {
            'pc_compatible': True,
            'tool_support': 'Limited',
            'notes': 'RDR1 PC format support in development'
        }


class AdvancedAILearningOrchestrator:
    """Enhanced orchestrator with multi-file plugin testing and RAGE analyzer integration"""
   
    def __init__(self):
        self.pyautofix_engine = None
        self.rage_analyzer = RAGEAnalyzerIntegration()
        self.plugin_analyzer = BlenderPluginAnalyzer()
        self.learning_sessions = []
        self.cross_training_data = []

        if PYAUTOFIX_AVAILABLE:
            self.pyautofix_engine = AICorrectionEngine()
            logging.info("PyAutoFix engine initialized")

    def analyze_plugin_comprehensive(self, plugin_dir: str) -> Dict[str, Any]:
        """Comprehensive analysis of a Blender plugin"""
        results = {
            'plugin_directory': plugin_dir,
            'plugin_name': Path(plugin_dir).name,
            'analysis_timestamp': datetime.now().isoformat(),
            'plugin_structure': {},
            'file_analyses': {},
            'cross_script_analysis': {},
            'ai_insights': [],
            'recommendations': [],
            'health_assessment': {}
        }

        # 1. Analyze plugin structure
        results['plugin_structure'] = self.plugin_analyzer.analyze_plugin_structure(plugin_dir)

        # 2. Analyze individual files with PyAutoFix
        results['file_analyses'] = self.analyze_plugin_files_individually(plugin_dir)

        # 3. Cross-script communication analysis
        results['cross_script_analysis'] = self.analyze_cross_script_communication(results)

        # 4. Generate AI insights
        results['ai_insights'] = self.generate_plugin_insights(results)

        # 5. Generate recommendations
        results['recommendations'] = self.generate_plugin_recommendations(results)

        # 6. Health assessment
        results['health_assessment'] = self.assess_plugin_health(results)

        # Record learning session
        self.learning_sessions.append({
            'type': 'plugin_analysis',
            'plugin_data': results,
            'timestamp': datetime.now().isoformat()
        })

        return results

    def analyze_plugin_files_individually(self, plugin_dir: str) -> Dict[str, Any]:
        """Analyze each plugin file individually with PyAutoFix"""
        file_analyses = {}
        plugin_path = Path(plugin_dir)

        for py_file in plugin_path.rglob("*.py"):
            try:
                if self.pyautofix_engine and self.pyautofix_engine.available:
                    # Use PyAutoFix for code analysis
                    analysis = self.pyautofix_engine.analyze_file(str(py_file))
                    file_analyses[str(py_file)] = {
                        'pyautofix_analysis': analysis,
                        'file_size': py_file.stat().st_size,
                        'file_name': py_file.name
                    }

                # Additional file-level analysis
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_analyses[str(py_file)]['line_count'] = len(content.splitlines())
                file_analyses[str(py_file)]['has_errors'] = 'error' in content.lower()

            except Exception as e:
                file_analyses[str(py_file)] = {
                    'error': str(e),
                    'file_name': py_file.name
                }

        return file_analyses

    def analyze_cross_script_communication(self, plugin_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication and dependencies between scripts"""
        cross_analysis = {
            'operator_dependencies': [],
            'function_calls': [],
            'import_dependencies': [],
            'potential_issues': [],
            'communication_map': {}
        }

        structure = plugin_analysis['plugin_structure']

        # Analyze operator dependencies
        for cross_ref in structure.get('cross_references', []):
            if cross_ref['type'] == 'operator_call':
                cross_analysis['operator_dependencies'].append({
                    'source': cross_ref['source_file'],
                    'target': cross_ref['target_file'],
                    'operator': cross_ref['operator'],
                    'description': cross_ref['description']
                })

        # Analyze import dependencies
        all_imports = set()
        for file_analysis in structure.get('file_analysis', {}).values():
            all_imports.update(file_analysis.get('dependencies', []))

        cross_analysis['import_dependencies'] = list(all_imports)

        # Check for potential communication issues
        self._check_communication_issues(cross_analysis, structure)

        return cross_analysis

    def _check_communication_issues(self, cross_analysis: Dict[str, Any], structure: Dict[str, Any]):
        """Check for potential communication issues between scripts"""
        # Check for circular dependencies
        operator_deps = cross_analysis['operator_dependencies']
        file_deps = {}

        for dep in operator_deps:
            source = dep['source']
            target = dep['target']
            if source not in file_deps:
                file_deps[source] = set()
            file_deps[source].add(target)

        # Simple circular dependency check
        for file, deps in file_deps.items():
            for dep in deps:
                if dep in file_deps and file in file_deps[dep]:
                    cross_analysis['potential_issues'].append(
                        f'Circular dependency between {file} and {dep}'
                    )

        # Check for missing operator implementations
        all_operators = {op['bl_idname'] for op in structure.get('operators_found', [])
                        if op.get('bl_idname')}

        for dep in operator_deps:
            if dep['operator'] not in all_operators:
                cross_analysis['potential_issues'].append(
                    f'Missing operator implementation: {dep["operator"]}'
                )

    def generate_plugin_insights(self, plugin_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights for the plugin"""
        insights = []
        structure = plugin_analysis['plugin_structure']
        summary = structure.get('summary', {})

        # Health insights
        health_score = summary.get('health_score', 0)
        if health_score >= 80:
            insights.append({
                'type': 'positive',
                'message': f'Plugin has excellent health score: {health_score}/100',
                'confidence': 90
            })
        elif health_score <= 40:
            insights.append({
                'type': 'critical',
                'message': f'Plugin needs immediate attention. Health score: {health_score}/100',
                'confidence': 95
            })

        # Operator insights
        operator_count = summary.get('total_operators', 0)
        if operator_count == 0:
            insights.append({
                'type': 'warning',
                'message': 'No Blender operators found. Plugin may not have user interface components',
                'confidence': 85
            })
        elif operator_count > 20:
            insights.append({
                'type': 'info',
                'message': f'Large number of operators ({operator_count}). Consider organizing into panels',
                'confidence': 75
            })

        # Dependency insights
        deps = summary.get('total_dependencies', 0)
        if deps > 10:
            insights.append({
                'type': 'warning',
                'message': f'High dependency count ({deps}). May affect compatibility',
                'confidence': 80
            })

        # Cross-script insights
        cross_refs = summary.get('total_cross_references', 0)
        if cross_refs == 0:
            insights.append({
                'type': 'info',
                'message': 'No cross-script dependencies detected. Scripts operate independently',
                'confidence': 70
            })
        elif cross_refs > 10:
            insights.append({
                'type': 'info',
                'message': f'Complex cross-script communication ({cross_refs} references). Good integration',
                'confidence': 85
            })

        return insights

    def generate_plugin_recommendations(self, plugin_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for plugin improvement"""
        recommendations = []
        structure = plugin_analysis['plugin_structure']

        # Check for missing register/unregister
        issues = structure.get('potential_issues', [])
        for issue in issues:
            if 'register' in issue.lower():
                recommendations.append({
                    'priority': 'high',
                    'category': 'structure',
                    'description': issue,
                    'suggestion': 'Add proper register and unregister functions'
                })

        # Check operator organization
        operators = structure.get('operators_found', [])
        if len(operators) > 10:
            recommendations.append({
                'priority': 'medium',
                'category': 'organization',
                'description': 'Large number of operators',
                'suggestion': 'Group related operators into separate modules or use operator categories'
            })

        # Check file organization
        file_count = structure.get('python_files', 0)
        if file_count > 15:
            recommendations.append({
                'priority': 'medium',
                'category': 'organization',
                'description': 'Large number of Python files',
                'suggestion': 'Consider organizing files into subdirectories by functionality'
            })

        # Check for error handling
        file_analyses = plugin_analysis.get('file_analyses', {})
        files_without_errors = sum(1 for analysis in file_analyses.values()
                                 if not analysis.get('has_errors', True))

        if files_without_errors < len(file_analyses) * 0.8:  # Less than 80% clean
            recommendations.append({
                'priority': 'high',
                'category': 'code_quality',
                'description': 'Multiple files contain potential errors',
                'suggestion': 'Run comprehensive error checking and add proper exception handling'
            })

        return recommendations

    def assess_plugin_health(self, plugin_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive plugin health assessment"""
        structure = plugin_analysis['plugin_structure']
        summary = structure.get('summary', {})
        cross_analysis = plugin_analysis['cross_script_analysis']

        health_score = summary.get('health_score', 0)
        total_issues = len(plugin_analysis['recommendations']) + len(cross_analysis['potential_issues'])

        # Calculate component scores
        structure_score = max(0, 100 - len(structure.get('potential_issues', [])) * 10)
        communication_score = max(0, 100 - len(cross_analysis.get('potential_issues', [])) * 15)
        code_quality_score = 80  # Placeholder - would analyze actual code quality

        overall_score = (structure_score + communication_score + code_quality_score) // 3

        return {
            'overall_score': overall_score,
            'structure_score': structure_score,
            'communication_score': communication_score,
            'code_quality_score': code_quality_score,
            'total_issues': total_issues,
            'readiness': 'Production Ready' if overall_score >= 80 else 'Needs Work',
            'risk_level': 'Low' if overall_score >= 80 else 'Medium' if overall_score >= 60 else 'High'
        }

    def test_plugin_integration(self, plugin_dir: str) -> Dict[str, Any]:
        """Test plugin integration and communication"""
        test_results = {
            'plugin_directory': plugin_dir,
            'tests_run': [],
            'integration_issues': [],
            'communication_tests': [],
            'operator_tests': [],
            'overall_integration_score': 0
        }

        # Analyze plugin first
        plugin_analysis = self.analyze_plugin_comprehensive(plugin_dir)

        # Run integration tests
        test_results['tests_run'].extend(self._run_operator_tests(plugin_analysis))
        test_results['tests_run'].extend(self._run_communication_tests(plugin_analysis))
        test_results['tests_run'].extend(self._run_dependency_tests(plugin_analysis))

        # Calculate integration score
        passed_tests = sum(1 for test in test_results['tests_run'] if test.get('passed', False))
        total_tests = len(test_results['tests_run'])

        if total_tests > 0:
            test_results['overall_integration_score'] = (passed_tests / total_tests) * 100

        # Collect integration issues
        for test in test_results['tests_run']:
            if not test.get('passed', False):
                test_results['integration_issues'].append(test['description'])

        return test_results

    def _run_operator_tests(self, plugin_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test operator functionality and registration"""
        tests = []
        structure = plugin_analysis['plugin_structure']

        # Test 1: Check operator registration
        has_register = any('register' in issue for issue in structure.get('potential_issues', []))
        tests.append({
            'test': 'operator_registration',
            'passed': not has_register,
            'description': 'Operator registration functions present'
        })

        # Test 2: Check operator uniqueness
        operators = structure.get('operators_found', [])
        bl_idnames = [op['bl_idname'] for op in operators if op.get('bl_idname')]
        unique_operators = len(bl_idnames) == len(set(bl_idnames))
        tests.append({
            'test': 'operator_uniqueness',
            'passed': unique_operators,
            'description': 'All operators have unique bl_idnames'
        })

        return tests

    def _run_communication_tests(self, plugin_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test inter-script communication"""
        tests = []
        cross_analysis = plugin_analysis['cross_script_analysis']

        # Test 1: Check for circular dependencies
        has_circular = any('circular' in issue.lower() for issue in cross_analysis.get('potential_issues', []))
        tests.append({
            'test': 'no_circular_dependencies',
            'passed': not has_circular,
            'description': 'No circular dependencies between scripts'
        })

        # Test 2: Check operator call consistency
        missing_operators = any('missing operator' in issue.lower() for issue in cross_analysis.get('potential_issues', []))
        tests.append({
            'test': 'operator_call_consistency',
            'passed': not missing_operators,
            'description': 'All operator calls have implementations'
        })

        return tests

    def _run_dependency_tests(self, plugin_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test external dependencies"""
        tests = []
        structure = plugin_analysis['plugin_structure']

        # Test 1: Check for problematic dependencies
        dependencies = structure.get('dependencies', set())
        problematic_deps = {'os', 'sys', 'subprocess'}  # Can be expanded
        has_problematic = any(dep in problematic_deps for dep in dependencies)
        tests.append({
            'test': 'safe_dependencies',
            'passed': not has_problematic,
            'description': 'No potentially problematic dependencies'
        })

        return tests

    def analyze_file_with_rage(self, file_path: str) -> Dict[str, Any]:
        """Analyze file using RAGE analyzer with plugin system"""
        return self.rage_analyzer.analyze_file(file_path)


class EnhancedBridgeCommanderGUI:
    """Enhanced Bridge Commander with Plugin Testing and RAGE Analyzer Integration"""
   
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyAutoFix Bridge Commander - Advanced Plugin Testing & RAGE Integration")
        self.root.geometry("1600x1000")

        # Initialize enhanced orchestrator
        self.orchestrator = AdvancedAILearningOrchestrator()

        self.setup_gui()

    def setup_gui(self):
        """Setup the enhanced GUI with plugin testing and RAGE integration"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Setup all tabs
        self.setup_plugin_testing_tab()
        self.setup_format_discovery_tab()
        self.setup_rdr1_analysis_tab()
        self.setup_legacy_analysis_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_plugin_testing_tab(self):
        """Setup dedicated plugin testing tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔧 Plugin Testing")

        # Plugin selection
        ttk.Label(frame, text="Blender Plugin Directory:").grid(
            row=0, column=0, sticky='w', padx=5, pady=10)

        self.plugin_path_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.plugin_path_var, width=80).grid(
            row=0, column=1, padx=5, pady=10)

        ttk.Button(frame, text="Browse Plugin", command=self.browse_plugin_directory).grid(
            row=0, column=2, padx=5, pady=10)

        # Testing options
        ttk.Label(frame, text="Testing Mode:").grid(
            row=1, column=0, sticky='w', padx=5, pady=5)

        self.testing_mode_var = tk.StringVar(value="comprehensive")
        modes = [
            ("Comprehensive Analysis", "comprehensive"),
            ("Integration Testing", "integration"),
            ("Quick Health Check", "quick"),
            ("Cross-Script Analysis", "cross_script")
        ]

        mode_frame = ttk.Frame(frame)
        mode_frame.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=5)

        for i, (text, mode) in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=text, variable=self.testing_mode_var,
                          value=mode).grid(row=0, column=i, padx=5)

        # Action buttons
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=20)

        ttk.Button(action_frame, text="Analyze Plugin Structure",
                 command=self.analyze_plugin_structure, width=25).pack(side=tk.LEFT, padx=10)

        ttk.Button(action_frame, text="Test Integration",
                 command=self.test_plugin_integration, width=25).pack(side=tk.LEFT, padx=10)

        ttk.Button(action_frame, text="Full Plugin Report",
                 command=self.generate_plugin_report, width=25).pack(side=tk.LEFT, padx=10)

        # Results area
        self.plugin_results_text = scrolledtext.ScrolledText(frame, height=25, width=100)
        self.plugin_results_text.grid(row=3, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)

        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def setup_format_discovery_tab(self):
        """Setup format discovery tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔍 Format Discovery")

        # File selection
        ttk.Label(frame, text="File to Analyze:").grid(
            row=0, column=0, sticky='w', padx=5, pady=10)

        self.format_file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.format_file_var, width=80).grid(
            row=0, column=1, padx=5, pady=10)

        ttk.Button(frame, text="Browse File", command=self.browse_format_file).grid(
            row=0, column=2, padx=5, pady=10)

        # Analysis options
        ttk.Label(frame, text="Analysis Depth:").grid(
            row=1, column=0, sticky='w', padx=5, pady=5)

        self.analysis_depth_var = tk.StringVar(value="aggressive")
        depths = [("Quick", "quick"), ("Standard", "standard"), ("Aggressive", "aggressive")]

        depth_frame = ttk.Frame(frame)
        depth_frame.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=5)

        for i, (text, depth) in enumerate(depths):
            ttk.Radiobutton(depth_frame, text=text, variable=self.analysis_depth_var,
                          value=depth).grid(row=0, column=i, padx=5)

        # Action buttons
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=20)

        ttk.Button(action_frame, text="Analyze Format",
                 command=self.analyze_format, width=25).pack(side=tk.LEFT, padx=10)

        ttk.Button(action_frame, text="Multi-Format Analysis",
                 command=self.multi_format_analysis, width=25).pack(side=tk.LEFT, padx=10)

        # Results area with treeview for candidates
        results_frame = ttk.Frame(frame)
        results_frame.grid(row=3, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)

        # Treeview for format candidates
        columns = ('format', 'confidence', 'size', 'description')
        self.format_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
       
        # Define headings
        self.format_tree.heading('format', text='Format')
        self.format_tree.heading('confidence', text='Confidence')
        self.format_tree.heading('size', text='Size')
        self.format_tree.heading('description', text='Description')

        self.format_tree.column('format', width=100)
        self.format_tree.column('confidence', width=80)
        self.format_tree.column('size', width=80)
        self.format_tree.column('description', width=200)

        self.format_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.format_tree.yview)
        self.format_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Detailed results text
        self.format_results_text = scrolledtext.ScrolledText(frame, height=10, width=100)
        self.format_results_text.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)

        frame.grid_rowconfigure(3, weight=1)
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def setup_rdr1_analysis_tab(self):
        """Setup RDR1-specific analysis tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎮 RDR1 Analysis")

        ttk.Label(frame, text="RDR1 PC Format Analysis - Coming Soon",
                 font=('Arial', 14)).pack(expand=True)

        # Placeholder for RDR1-specific functionality
        ttk.Label(frame, text="WVD/WTD/WFT format support will be implemented here").pack()

    def setup_legacy_analysis_tab(self):
        """Setup legacy analysis tab for backward compatibility"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔙 Legacy Analysis")

        ttk.Label(frame, text="Legacy File Analysis - Backward Compatibility",
                 font=('Arial', 12)).pack(pady=10)

        # Legacy file selection
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.legacy_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.legacy_file_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_legacy_file).pack(side=tk.LEFT)

        # Legacy analysis button
        ttk.Button(frame, text="Run Legacy Analysis",
                 command=self.run_legacy_analysis).pack(pady=10)

        # Legacy results
        self.legacy_results_text = scrolledtext.ScrolledText(frame, height=15, width=100)
        self.legacy_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def browse_plugin_directory(self):
        """Browse for plugin directory"""
        directory = filedialog.askdirectory(title="Select Blender Plugin Directory")
        if directory:
            self.plugin_path_var.set(directory)

    def browse_format_file(self):
        """Browse for format analysis file"""
        filename = filedialog.askopenfilename(title="Select File for Format Analysis")
        if filename:
            self.format_file_var.set(filename)

    def browse_legacy_file(self):
        """Browse for legacy analysis file"""
        filename = filedialog.askopenfilename(title="Select File for Legacy Analysis")
        if filename:
            self.legacy_file_var.set(filename)

    def analyze_plugin_structure(self):
        """Analyze plugin structure"""
        plugin_dir = self.plugin_path_var.get()
        if not plugin_dir or not os.path.exists(plugin_dir):
            messagebox.showerror("Error", "Please select a valid plugin directory")
            return

        def analyze_thread():
            self.update_status("Analyzing plugin structure...")
            try:
                results = self.orchestrator.analyze_plugin_comprehensive(plugin_dir)
                self.display_plugin_analysis(results)
                self.update_status("Plugin analysis complete")
            except Exception as e:
                self.update_status(f"Plugin analysis failed: {e}")
                messagebox.showerror("Error", f"Plugin analysis failed: {e}")

        threading.Thread(target=analyze_thread, daemon=True).start()

    def test_plugin_integration(self):
        """Test plugin integration"""
        plugin_dir = self.plugin_path_var.get()
        if not plugin_dir or not os.path.exists(plugin_dir):
            messagebox.showerror("Error", "Please select a valid plugin directory")
            return

        def test_thread():
            self.update_status("Testing plugin integration...")
            try:
                results = self.orchestrator.test_plugin_integration(plugin_dir)
                self.display_integration_test_results(results)
                self.update_status("Integration testing complete")
            except Exception as e:
                self.update_status(f"Integration testing failed: {e}")
                messagebox.showerror("Error", f"Integration testing failed: {e}")

        threading.Thread(target=test_thread, daemon=True).start()

    def generate_plugin_report(self):
        """Generate comprehensive plugin report"""
        plugin_dir = self.plugin_path_var.get()
        if not plugin_dir or not os.path.exists(plugin_dir):
            messagebox.showerror("Error", "Please select a valid plugin directory")
            return

        def report_thread():
            self.update_status("Generating plugin report...")
            try:
                # Run both analysis and integration tests
                analysis = self.orchestrator.analyze_plugin_comprehensive(plugin_dir)
                integration = self.orchestrator.test_plugin_integration(plugin_dir)

                self.display_comprehensive_report(analysis, integration)
                self.update_status("Plugin report generated")
            except Exception as e:
                self.update_status(f"Report generation failed: {e}")
                messagebox.showerror("Error", f"Report generation failed: {e}")

        threading.Thread(target=report_thread, daemon=True).start()

    def analyze_format(self):
        """Analyze file format using RAGE analyzer"""
        file_path = self.format_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return

        def analyze_thread():
            self.update_status("Analyzing file format...")
            try:
                results = self.orchestrator.analyze_file_with_rage(file_path)
                self.display_format_analysis(results)
                self.update_status("Format analysis complete")
            except Exception as e:
                self.update_status(f"Format analysis failed: {e}")
                messagebox.showerror("Error", f"Format analysis failed: {e}")

        threading.Thread(target=analyze_thread, daemon=True).start()

    def multi_format_analysis(self):
        """Perform multi-format analysis"""
        file_path = self.format_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return

        def analyze_thread():
            self.update_status("Running multi-format analysis...")
            try:
                # This would use the aggressive format discovery
                results = self.orchestrator.analyze_file_with_rage(file_path)
                self.display_multi_format_results(results)
                self.update_status("Multi-format analysis complete")
            except Exception as e:
                self.update_status(f"Multi-format analysis failed: {e}")
                messagebox.showerror("Error", f"Multi-format analysis failed: {e}")

        threading.Thread(target=analyze_thread, daemon=True).start()

    def run_legacy_analysis(self):
        """Run legacy analysis for backward compatibility"""
        file_path = self.legacy_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return

        def analyze_thread():
            self.update_status("Running legacy analysis...")
            try:
                results = self.orchestrator.analyze_file_with_rage(file_path)
                self.display_legacy_results(results)
                self.update_status("Legacy analysis complete")
            except Exception as e:
                self.update_status(f"Legacy analysis failed: {e}")
                messagebox.showerror("Error", f"Legacy analysis failed: {e}")

        threading.Thread(target=analyze_thread, daemon=True).start()

    def display_plugin_analysis(self, results: Dict[str, Any]):
        """Display plugin analysis results"""
        self.plugin_results_text.delete(1.0, tk.END)

        structure = results['plugin_structure']
        summary = structure.get('summary', {})
        health = results['health_assessment']

        self.plugin_results_text.insert(tk.END, "🔧 BLENDER PLUGIN ANALYSIS REPORT\n")
        self.plugin_results_text.insert(tk.END, "=" * 50 + "\n\n")

        # Basic info
        self.plugin_results_text.insert(tk.END, f"Plugin: {results['plugin_name']}\n")
        self.plugin_results_text.insert(tk.END, f"Directory: {results['plugin_directory']}\n")
        self.plugin_results_text.insert(tk.END, f"Analysis: {results['analysis_timestamp']}\n\n")

        # Health assessment
        self.plugin_results_text.insert(tk.END, "❤️ HEALTH ASSESSMENT\n")
        self.plugin_results_text.insert(tk.END, f"Overall Score: {health['overall_score']}/100\n")
        self.plugin_results_text.insert(tk.END, f"Readiness: {health['readiness']}\n")
        self.plugin_results_text.insert(tk.END, f"Risk Level: {health['risk_level']}\n")
        self.plugin_results_text.insert(tk.END, f"Total Issues: {health['total_issues']}\n\n")

        # Plugin structure
        self.plugin_results_text.insert(tk.END, "📁 PLUGIN STRUCTURE\n")
        self.plugin_results_text.insert(tk.END, f"Total Files: {structure['total_files']}\n")
        self.plugin_results_text.insert(tk.END, f"Python Files: {structure['python_files']}\n")
        self.plugin_results_text.insert(tk.END, f"Operators Found: {summary['total_operators']}\n")
        self.plugin_results_text.insert(tk.END, f"Dependencies: {summary['total_dependencies']}\n")
        self.plugin_results_text.insert(tk.END, f"Cross-References: {summary['total_cross_references']}\n\n")

        # AI Insights
        insights = results['ai_insights']
        if insights:
            self.plugin_results_text.insert(tk.END, "🤖 AI INSIGHTS\n")
            for insight in insights:
                icon = "✅" if insight['type'] == 'positive' else "⚠️" if insight['type'] == 'warning' else "❌"
                self.plugin_results_text.insert(tk.END, f"{icon} {insight['message']}\n")
            self.plugin_results_text.insert(tk.END, "\n")

        # Recommendations
        recommendations = results['recommendations']
        if recommendations:
            self.plugin_results_text.insert(tk.END, "💡 RECOMMENDATIONS\n")
            for rec in recommendations:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🔵"
                self.plugin_results_text.insert(tk.END, f"{priority_icon} {rec['description']}\n")
                self.plugin_results_text.insert(tk.END, f"   Suggestion: {rec['suggestion']}\n\n")

    def display_integration_test_results(self, results: Dict[str, Any]):
        """Display integration test results"""
        self.plugin_results_text.delete(1.0, tk.END)

        self.plugin_results_text.insert(tk.END, "🔄 PLUGIN INTEGRATION TEST RESULTS\n")
        self.plugin_results_text.insert(tk.END, "=" * 50 + "\n\n")

        self.plugin_results_text.insert(tk.END, f"Plugin: {results['plugin_directory']}\n")
        self.plugin_results_text.insert(tk.END, f"Integration Score: {results['overall_integration_score']:.1f}%\n\n")

        # Test results
        self.plugin_results_text.insert(tk.END, "🧪 TEST RESULTS\n")
        for test in results['tests_run']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            self.plugin_results_text.insert(tk.END, f"{status} {test['test']}\n")
            self.plugin_results_text.insert(tk.END, f"   {test['description']}\n\n")

        # Integration issues
        issues = results['integration_issues']
        if issues:
            self.plugin_results_text.insert(tk.END, "🚨 INTEGRATION ISSUES\n")
            for issue in issues:
                self.plugin_results_text.insert(tk.END, f"• {issue}\n")

    def display_comprehensive_report(self, analysis: Dict[str, Any], integration: Dict[str, Any]):
        """Display comprehensive plugin report"""
        self.plugin_results_text.delete(1.0, tk.END)

        self.plugin_results_text.insert(tk.END, "📊 COMPREHENSIVE PLUGIN REPORT\n")
        self.plugin_results_text.insert(tk.END, "=" * 50 + "\n\n")

        # Executive summary
        health = analysis['health_assessment']
        self.plugin_results_text.insert(tk.END, "🏆 EXECUTIVE SUMMARY\n")
        self.plugin_results_text.insert(tk.END, f"Plugin: {analysis['plugin_name']}\n")
        self.plugin_results_text.insert(tk.END, f"Overall Health: {health['overall_score']}/100\n")
        self.plugin_results_text.insert(tk.END, f"Integration Score: {integration['overall_integration_score']:.1f}%\n")
        self.plugin_results_text.insert(tk.END, f"Readiness: {health['readiness']}\n")
        self.plugin_results_text.insert(tk.END, f"Risk Level: {health['risk_level']}\n\n")

        # Combined recommendations
        all_recommendations = analysis['recommendations']
        high_priority = [r for r in all_recommendations if r['priority'] == 'high']
        medium_priority = [r for r in all_recommendations if r['priority'] == 'medium']

        if high_priority:
            self.plugin_results_text.insert(tk.END, "🔴 HIGH PRIORITY ACTIONS\n")
            for rec in high_priority:
                self.plugin_results_text.insert(tk.END, f"• {rec['description']}\n")
                self.plugin_results_text.insert(tk.END, f"  Solution: {rec['suggestion']}\n\n")

        if medium_priority:
            self.plugin_results_text.insert(tk.END, "🟡 MEDIUM PRIORITY ACTIONS\n")
            for rec in medium_priority:
                self.plugin_results_text.insert(tk.END, f"• {rec['description']}\n")
                self.plugin_results_text.insert(tk.END, f"  Solution: {rec['suggestion']}\n\n")

        # Integration status
        passed_tests = sum(1 for test in integration['tests_run'] if test.get('passed', False))
        total_tests = len(integration['tests_run'])
        self.plugin_results_text.insert(tk.END, "🔄 INTEGRATION STATUS\n")
        self.plugin_results_text.insert(tk.END, f"Tests Passed: {passed_tests}/{total_tests}\n")

        if integration['integration_issues']:
            self.plugin_results_text.insert(tk.END, "\n🚨 CRITICAL INTEGRATION ISSUES\n")
            for issue in integration['integration_issues'][:5]:  # Show top 5
                self.plugin_results_text.insert(tk.END, f"• {issue}\n")

    def display_format_analysis(self, results: Dict[str, Any]):
        """Display format analysis results"""
        # Clear treeview
        for item in self.format_tree.get_children():
            self.format_tree.delete(item)

        self.format_results_text.delete(1.0, tk.END)

        self.format_results_text.insert(tk.END, "🔍 FORMAT ANALYSIS RESULTS\n")
        self.format_results_text.insert(tk.END, "=" * 50 + "\n\n")

        if 'error' in results:
            self.format_results_text.insert(tk.END, f"Error: {results['error']}\n")
            return

        self.format_results_text.insert(tk.END, f"File: {results.get('file_path', 'Unknown')}\n")
        self.format_results_text.insert(tk.END, f"Analysis Method: {results.get('analysis_method', 'Unknown')}\n")
        self.format_results_text.insert(tk.END, f"Primary Format: {results.get('primary_format', 'Unknown')}\n")
        self.format_results_text.insert(tk.END, f"Confidence: {results.get('confidence', 0):.1f}%\n\n")

        # Add candidates to treeview
        candidates = results.get('format_candidates', [])
        for candidate in candidates:
            self.format_tree.insert('', tk.END, values=(
                candidate.get('format', 'Unknown'),
                f"{candidate.get('confidence', 0):.1f}%",
                candidate.get('size', 'Unknown'),
                candidate.get('description', 'No description')
            ))

        # Show metadata
        metadata = results.get('metadata', {})
        if metadata:
            self.format_results_text.insert(tk.END, "📋 METADATA\n")
            for key, value in metadata.items():
                self.format_results_text.insert(tk.END, f"{key}: {value}\n")

        # Show RDR1 specific info if available
        rdr1_info = results.get('rdr1_specific', {})
        if rdr1_info:
            self.format_results_text.insert(tk.END, "\n🎮 RDR1 SPECIFIC INFORMATION\n")
            for key, value in rdr1_info.items():
                self.format_results_text.insert(tk.END, f"{key}: {value}\n")

    def display_multi_format_results(self, results: Dict[str, Any]):
        """Display multi-format analysis results"""
        self.display_format_analysis(results)
       
        # Additional multi-format specific display
        candidates = results.get('format_candidates', [])
        if len(candidates) > 1:
            self.format_results_text.insert(tk.END, f"\n🔍 Found {len(candidates)} potential formats\n")
            self.format_results_text.insert(tk.END, "Formats sorted by confidence:\n")
           
            for i, candidate in enumerate(sorted(candidates, key=lambda x: x.get('confidence', 0), reverse=True)):
                self.format_results_text.insert(tk.END,
                    f"{i+1}. {candidate.get('format')} ({candidate.get('confidence', 0):.1f}%)\n")

    def display_legacy_results(self, results: Dict[str, Any]):
        """Display legacy analysis results"""
        self.legacy_results_text.delete(1.0, tk.END)

        self.legacy_results_text.insert(tk.END, "🔙 LEGACY ANALYSIS RESULTS\n")
        self.legacy_results_text.insert(tk.END, "=" * 50 + "\n\n")

        if 'error' in results:
            self.legacy_results_text.insert(tk.END, f"Error: {results['error']}\n")
            return

        # Display results in a compatible format
        for key, value in results.items():
            if isinstance(value, (dict, list)):
                self.legacy_results_text.insert(tk.END, f"{key}:\n")
                self.legacy_results_text.insert(tk.END, f"{json.dumps(value, indent=2)}\n\n")
            else:
                self.legacy_results_text.insert(tk.END, f"{key}: {value}\n")

    def update_status(self, message: str):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def run(self):
        """Run the enhanced Bridge Commander"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("PyAutoFix Bridge Commander - Advanced Plugin Testing & RAGE Integration")
    print("Multi-file Blender plugin analysis and integration testing")
    print("RAGE Evolutionary Analyzer with Plugin System")
    print("=" * 70)

    app = EnhancedBridgeCommanderGUI()
    app.run()


if __name__ == "__main__":
    main()