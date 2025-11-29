import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib.util

logger = logging.getLogger(__name__)

class ExternalAnalyzerInterface:
    """Interface for external analyzers and tools"""
  
    def __init__(self):
        self.available_analyzers = {}
        self._discover_analyzers()
  
    def _discover_analyzers(self):
        """Discover available external analyzers"""
        self.available_analyzers = {
            'ruff': self._check_ruff(),
            'pylint': self._check_pylint(),
            'mypy': self._check_mypy(),
            'black': self._check_black()
        }
  
    def _check_ruff(self) -> bool:
        """Check if Ruff is available"""
        try:
            import subprocess
            result = subprocess.run(['ruff', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
  
    def _check_pylint(self) -> bool:
        """Check if Pylint is available"""
        try:
            import subprocess
            result = subprocess.run(['pylint', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
  
    def _check_mypy(self) -> bool:
        """Check if MyPy is available"""
        try:
            import subprocess
            result = subprocess.run(['mypy', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
  
    def _check_black(self) -> bool:
        """Check if Black is available"""
        try:
            import subprocess
            result = subprocess.run(['black', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
  
    def run_external_analysis(self, file_path: str, analyzer_name: str) -> Dict[str, Any]:
        """Run external analyzer on file"""
        if analyzer_name not in self.available_analyzers:
            return {'error': f'Analyzer {analyzer_name} not available'}
      
        if not self.available_analyzers[analyzer_name]:
            return {'error': f'Analyzer {analyzer_name} not installed'}
      
        try:
            if analyzer_name == 'ruff':
                return self._run_ruff(file_path)
            elif analyzer_name == 'pylint':
                return self._run_pylint(file_path)
            elif analyzer_name == 'mypy':
                return self._run_mypy(file_path)
            elif analyzer_name == 'black':
                return self._run_black(file_path)
        except Exception as e:
            return {'error': f'{analyzer_name} analysis failed: {e}'}
      
        return {'error': f'Unknown analyzer: {analyzer_name}'}
  
    def _run_ruff(self, file_path: str) -> Dict[str, Any]:
        """Run Ruff analysis"""
        import subprocess
        result = subprocess.run(
            ['ruff', 'check', '--output-format=json', file_path],
            capture_output=True, text=True
        )
      
        return {
            'tool': 'ruff',
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        }
  
    def _run_pylint(self, file_path: str) -> Dict[str, Any]:
        """Run Pylint analysis"""
        import subprocess
        result = subprocess.run(
            ['pylint', '--output-format=json', file_path],
            capture_output=True, text=True
        )
      
        return {
            'tool': 'pylint',
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        }
  
    def _run_mypy(self, file_path: str) -> Dict[str, Any]:
        """Run MyPy analysis"""
        import subprocess
        result = subprocess.run(
            ['mypy', '--no-error-summary', file_path],
            capture_output=True, text=True
        )
      
        return {
            'tool': 'mypy',
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        }
  
    def _run_black(self, file_path: str) -> Dict[str, Any]:
        """Run Black formatting check"""
        import subprocess
        result = subprocess.run(
            ['black', '--check', '--diff', file_path],
            capture_output=True, text=True
        )
      
        return {
            'tool': 'black',
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        }