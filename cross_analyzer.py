import ast
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class CrossScriptAnalyzer:
    """
    Analyzes multiple Python scripts to detect integration issues,
    dependency problems, and communication errors.
    """
  
    def __init__(self):
        self.file_dependencies = defaultdict(set)
        self.import_map = defaultdict(list)
        self.function_defs = defaultdict(list)
        self.class_defs = defaultdict(list)
  
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire project for cross-script issues"""
        project_root = Path(project_path)
        python_files = list(project_root.glob("**/*.py"))
      
        # Phase 1: Extract symbols from each file
        for py_file in python_files:
            self._analyze_file_symbols(py_file)
      
        # Phase 2: Detect cross-script issues
        issues = self._detect_cross_script_issues()
      
        return {
            'project_path': project_path,
            'files_analyzed': len(python_files),
            'total_dependencies': sum(len(deps) for deps in self.file_dependencies.values()),
            'issues': issues,
            'file_dependencies': dict(self.file_dependencies),
            'import_map': dict(self.import_map)
        }
  
    def _analyze_file_symbols(self, py_file: Path):
        """Extract all defined symbols from a Python file"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
          
            tree = ast.parse(content)
          
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.import_map[py_file].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.import_map[py_file].append(node.module)
          
            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.function_defs[py_file].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
              
                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    self.class_defs[py_file].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                      
        except Exception as e:
            logger.warning(f"Error analyzing {py_file}: {e}")
  
    def _detect_cross_script_issues(self) -> List[Dict[str, Any]]:
        """Detect issues across multiple scripts"""
        issues = []
      
        # Check for duplicate function names
        function_names = defaultdict(list)
        for file_path, funcs in self.function_defs.items():
            for func in funcs:
                function_names[func['name']].append(file_path)
      
        for func_name, files in function_names.items():
            if len(files) > 1:
                issues.append({
                    'type': 'duplicate_function',
                    'description': f'Function "{func_name}" defined in multiple files',
                    'files': [str(f) for f in files],
                    'severity': 'warning'
                })
      
        # Check for duplicate class names
        class_names = defaultdict(list)
        for file_path, classes in self.class_defs.items():
            for cls in classes:
                class_names[cls['name']].append(file_path)
      
        for class_name, files in class_names.items():
            if len(files) > 1:
                issues.append({
                    'type': 'duplicate_class',
                    'description': f'Class "{class_name}" defined in multiple files',
                    'files': [str(f) for f in files],
                    'severity': 'warning'
                })
      
        return issues