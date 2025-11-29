#!/usr/bin/env python3
"""
PyAutoFix Ultimate - Advanced AI-powered code correction tool
With external analyzer system, learning capabilities, and full GUI/CLI support
"""

import argparse
import sys
import logging
import json
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from datetime import datetime
import importlib.util
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

__version__ = "2.1.0"
__author__ = "PyAutoFix Team"
__description__ = "Advanced AI-powered code correction tool with external analyzer support"

class ExternalAnalyzerInterface:
    """Interface for external analyzers"""
  
    def __init__(self):
        self.available_analyzers = {}
        self._discover_analyzers()
  
    def _discover_analyzers(self):
        """Discover available external analyzers"""
        # RAGE analyzer would be auto-discovered if available
        self.available_analyzers['rage_analyzer'] = {
            'name': 'RAGE Evolutionary Analyzer',
            'supported_files': ['.rpf', '.rpf6', '.wtd', '.wdr', '.wft'],
            'available': self._check_rage_analyzer_availability(),
            'description': 'Analyzes RAGE game engine archives and resources'
        }
  
    def _check_rage_analyzer_availability(self) -> bool:
        """Check if RAGE analyzer is available"""
        try:
            # Check if file_analyzer.py exists in current directory or parent
            if os.path.exists('file_analyzer.py'):
                return True
            # Check parent directory (RAGE_Brainiac root)
            parent_dir = Path(__file__).parent.parent
            if (parent_dir / 'file_analyzer.py').exists():
                return True
            # Check Python path
            spec = importlib.util.find_spec('file_analyzer')
            return spec is not None
        except:
            return False
  
    def run_analysis(self, file_path: str, analyzer_name: str) -> List[Dict[str, Any]]:
        """Run external analyzer on file"""
        if analyzer_name not in self.available_analyzers:
            return [{
                'tool': 'pyautofix',
                'type': 'analyzer_error',
                'message': f'External analyzer not found: {analyzer_name}',
                'severity': 'error'
            }]
      
        if analyzer_name == 'rage_analyzer':
            return self._run_rage_analyzer(file_path)
      
        return [{
            'tool': analyzer_name,
            'type': 'info',
            'message': f'External analysis would be performed by {analyzer_name}',
            'file': file_path,
            'severity': 'info'
        }]
  
    def _run_rage_analyzer(self, file_path: str) -> List[Dict[str, Any]]:
        """Run RAGE analyzer on file"""
        try:
            if not os.path.exists(file_path):
                return [{
                    'tool': 'rage_analyzer',
                    'type': 'file_error',
                    'message': f'File not found: {file_path}',
                    'severity': 'error'
                }]
          
            # Try multiple locations for file_analyzer.py
            rage_module = None
            possible_paths = [
                'file_analyzer.py',
                str(Path(__file__).parent.parent / 'file_analyzer.py')
            ]
          
            for analyzer_path in possible_paths:
                try:
                    if os.path.exists(analyzer_path):
                        spec = importlib.util.spec_from_file_location("file_analyzer", analyzer_path)
                        if spec is not None:
                            rage_module = importlib.util.module_from_spec(spec)
                            sys.modules["file_analyzer"] = rage_module
                            spec.loader.exec_module(rage_module)
                            break
                except Exception as e:
                    continue
          
            if rage_module is None:
                # Try Python path import
                try:
                    import file_analyzer as rage_module
                except ImportError:
                    return [{
                        'tool': 'rage_analyzer',
                        'type': 'import_error',
                        'message': 'RAGE analyzer not found. Make sure file_analyzer.py is in the current directory or RAGE_Brainiac root.',
                        'severity': 'error'
                    }]
          
            # Use RAGE analyzer's external interface
            if hasattr(rage_module, 'RAGEAnalyzerExternal'):
                analyzer = rage_module.RAGEAnalyzerExternal()
                return analyzer.analyze(file_path)
            else:
                return [{
                    'tool': 'rage_analyzer',
                    'type': 'interface_error',
                    'message': 'RAGE analyzer external interface not found',
                    'severity': 'warning'
                }]
              
        except Exception as e:
            return [{
                'tool': 'rage_analyzer',
                'type': 'analysis_error',
                'message': f'Failed to run RAGE analyzer: {e}',
                'severity': 'error'
            }]

class LearningSystem:
    """Machine learning system for code corrections"""
  
    def __init__(self):
        self.learned_rules = []
        self.correction_history = []
        self.performance_metrics = {
            'total_corrections': 0,
            'successful_corrections': 0,
            'learned_patterns': 0,
            'external_analyzer_calls': 0
        }
        # Updated path to match blueprint structure
        self.learning_data_file = "core/pyautofix_learning_data.json"
        self._load_learning_data()
  
    def _load_learning_data(self):
        """Load previously learned data"""
        try:
            if os.path.exists(self.learning_data_file):
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_rules = data.get('learned_rules', [])
                    self.performance_metrics.update(data.get('performance_metrics', {}))
                    logging.info(f"Loaded {len(self.learned_rules)} learned rules")
        except Exception as e:
            logging.warning(f"Failed to load learning data: {e}")
  
    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            data = {
                'learned_rules': self.learned_rules,
                'performance_metrics': self.performance_metrics,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save learning data: {e}")
  
    def learn_from_correction(self, original: str, corrected: str, success: bool):
        """Learn from a correction attempt"""
        self.performance_metrics['total_corrections'] += 1
        if success:
            self.performance_metrics['successful_corrections'] += 1
      
        # Extract pattern
        pattern = {
            'original_pattern': self._extract_pattern(original),
            'corrected_pattern': self._extract_pattern(corrected),
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'usage_count': 1
        }
      
        # Check for similar existing patterns
        existing_pattern = self._find_similar_pattern(pattern)
        if existing_pattern:
            existing_pattern['usage_count'] += 1
            existing_pattern['success_rate'] = ((existing_pattern.get('success_rate', 0) + (1 if success else 0)) / 2)
        else:
            pattern['success_rate'] = 1.0 if success else 0.0
            self.learned_rules.append(pattern)
            self.performance_metrics['learned_patterns'] += 1
      
        self._save_learning_data()
  
    def _extract_pattern(self, code: str) -> Dict[str, Any]:
        """Extract pattern from code"""
        # Simple pattern extraction
        lines = code.split('\n')
        return {
            'line_count': len(lines),
            'indentation_level': sum(len(line) - len(line.lstrip()) for line in lines if line.strip()),
            'common_patterns': self._find_common_patterns(code)
        }
  
    def _find_common_patterns(self, code: str) -> List[str]:
        """Find common code patterns"""
        patterns = []
        if ' == None' in code:
            patterns.append('none_comparison')
        if ' != None' in code:
            patterns.append('none_inequality')
        if 'len(' in code and ')==0' in code:
            patterns.append('empty_check')
        return patterns
  
    def _find_similar_pattern(self, new_pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find similar existing pattern"""
        for existing in self.learned_rules:
            if self._patterns_similar(existing['original_pattern'], new_pattern['original_pattern']):
                return existing
        return None
  
    def _patterns_similar(self, pattern1: Dict, pattern2: Dict, threshold: float = 0.7) -> bool:
        """Check if two patterns are similar"""
        similarity_score = 0
      
        # Compare line counts
        if pattern1.get('line_count') == pattern2.get('line_count'):
            similarity_score += 0.3
      
        # Compare common patterns
        patterns1 = set(pattern1.get('common_patterns', []))
        patterns2 = set(pattern2.get('common_patterns', []))
        if patterns1 and patterns2:
            pattern_similarity = len(patterns1.intersection(patterns2)) / len(patterns1.union(patterns2))
            similarity_score += pattern_similarity * 0.7
      
        return similarity_score >= threshold
  
    def get_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Get correction suggestions based on learned patterns"""
        suggestions = []
        current_pattern = self._extract_pattern(code)
      
        for rule in self.learned_rules:
            if (self._patterns_similar(rule['original_pattern'], current_pattern) and
                rule.get('success_rate', 0) > 0.7):
                suggestions.append({
                    'rule_id': id(rule),
                    'confidence': rule['success_rate'],
                    'suggestion': 'Apply learned correction pattern',
                    'usage_count': rule.get('usage_count', 1)
                })
      
        return suggestions[:5]  # Return top 5 suggestions
  
    def record_external_analysis(self, analyzer_name: str, file_type: str):
        """Record external analyzer usage"""
        self.performance_metrics['external_analyzer_calls'] += 1
        self._save_learning_data()
  
    def export_knowledge(self, file_path: str) -> bool:
        """Export learned knowledge to file"""
        try:
            data = {
                'learned_rules': self.learned_rules,
                'performance_metrics': self.performance_metrics,
                'export_timestamp': datetime.now().isoformat(),
                'total_rules': len(self.learned_rules),
                'success_rate': self.performance_metrics['successful_corrections'] / max(1, self.performance_metrics['total_corrections'])
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to export knowledge: {e}")
            return False
  
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights and metrics"""
        total_corrections = self.performance_metrics['total_corrections']
        successful_corrections = self.performance_metrics['successful_corrections']
      
        return {
            'performance_metrics': self.performance_metrics,
            'learned_rules': self.learned_rules,
            'success_rate': successful_corrections / max(1, total_corrections),
            'average_confidence': sum(r.get('success_rate', 0) for r in self.learned_rules) / max(1, len(self.learned_rules))
        }

class AICorrectionEngine:
    """AI-powered code correction engine"""
  
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.learning_system = LearningSystem()
        self.external_analyzers = ExternalAnalyzerInterface()
  
    async def correct_file(self, file_path: str, strategy: str = 'balanced') -> Dict[str, Any]:
        """Correct a file using AI-powered analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
          
            # Get suggestions from learning system
            suggestions = self.learning_system.get_suggestions(original_code)
          
            # Apply corrections based on strategy
            corrected_code = self._apply_corrections(original_code, strategy, suggestions)
          
            if corrected_code != original_code:
                # Create backup if configured
                if not self.config.get('no_backup', False):
                    backup_path = f"{file_path}.backup"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_code)
              
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(corrected_code)
              
                self.learning_system.learn_from_correction(
                    original_code, corrected_code, True
                )
              
                return {
                    'success': True,
                    'changes_made': True,
                    'file': file_path,
                    'strategy': strategy,
                    'suggestions_applied': len(suggestions),
                    'backup_created': not self.config.get('no_backup', False)
                }
            else:
                return {
                    'success': True,
                    'changes_made': False,
                    'file': file_path,
                    'message': 'No corrections needed',
                    'suggestions_considered': len(suggestions)
                }
              
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': file_path
            }
  
    def _apply_corrections(self, code: str, strategy: str, suggestions: List[Dict[str, Any]]) -> str:
        """Apply AI-powered corrections to code"""
        corrected_code = code
      
        # Apply basic corrections
        corrections = {
            'conservative': {
                ' == None': ' is None',
                ' != None': ' is not None',
            },
            'balanced': {
                ' == None': ' is None',
                ' != None': ' is not None',
                'len(x) == 0': 'not x',
                'len(x) > 0': 'x',
            },
            'aggressive': {
                ' == None': ' is None',
                ' != None': ' is not None',
                'len(x) == 0': 'not x',
                'len(x) > 0': 'x',
                ' == True': '',
                ' == False': ' not ',
            }
        }
      
        strategy_corrections = corrections.get(strategy, corrections['balanced'])
      
        for wrong, right in strategy_corrections.items():
            corrected_code = corrected_code.replace(wrong, right)
      
        return corrected_code
  
    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze file for issues"""
        issues = []
      
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
          
            # Basic static analysis
            analysis_patterns = [
                (' == None', 'code_smell', 'Use "is None" instead of "== None"'),
                (' != None', 'code_smell', 'Use "is not None" instead of "!= None"'),
                ('len(x) == 0', 'code_smell', 'Use "not x" instead of "len(x) == 0"'),
                ('import os', 'info', 'OS module imported'),
            ]
          
            for pattern, issue_type, message in analysis_patterns:
                if pattern in code:
                    # Simple line detection
                    lines = code.split('\n')
                    line_number = next((i + 1 for i, line in enumerate(lines) if pattern in line), 1)
                  
                    issues.append({
                        'tool': 'pyautofix',
                        'type': issue_type,
                        'message': message,
                        'line': line_number,
                        'severity': 'warning' if issue_type == 'code_smell' else 'info'
                    })
              
        except Exception as e:
            issues.append({
                'tool': 'pyautofix',
                'type': 'analysis_error',
                'message': f'Analysis failed: {e}',
                'severity': 'error'
            })
      
        return issues
  
    def analyze_with_external(self, file_path: str, analyzer_name: str = None) -> List[Dict[str, Any]]:
        """Analyze file with external analyzers"""
        issues = self.analyze_file(file_path)
      
        # Use external analyzers
        if analyzer_name:
            external_issues = self.external_analyzers.run_analysis(file_path, analyzer_name)
            issues.extend(external_issues)
            self.learning_system.record_external_analysis(analyzer_name, Path(file_path).suffix)
        else:
            # Use all available external analyzers
            for analyzer in self.external_analyzers.available_analyzers:
                if self.external_analyzers.available_analyzers[analyzer]['available']:
                    external_issues = self.external_analyzers.run_analysis(file_path, analyzer)
                    issues.extend(external_issues)
                    self.learning_system.record_external_analysis(analyzer, Path(file_path).suffix)
      
        return issues
  
    def analyze_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """Analyze all files in directory"""
        results = {
            'files_processed': 0,
            'python_files': 0,
            'external_files': 0,
            'issues_found': 0,
            'analysis_results': {},
            'external_analyzers_used': []
        }
      
        path = Path(directory)
        pattern = "**/*.py" if recursive else "*.py"
      
        for file_path in path.glob(pattern):
            if file_path.is_file():
                results['files_processed'] += 1
                results['python_files'] += 1
              
                issues = self.analyze_with_external(str(file_path))
                results['issues_found'] += len(issues)
              
                results['analysis_results'][str(file_path)] = {
                    'file_type': 'python',
                    'issues': issues,
                    'issue_count': len(issues)
                }
      
        # Analyze non-Python files with external analyzers
        other_patterns = ["**/*.rpf", "**/*.rpf6", "**/*.wtd"] if recursive else ["*.rpf", "*.rpf6", "*.wtd"]
        for pattern in other_patterns:
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    results['files_processed'] += 1
                    results['external_files'] += 1
                  
                    issues = self.analyze_with_external(str(file_path), 'rage_analyzer')
                    results['issues_found'] += len(issues)
                  
                    if issues and 'rage_analyzer' not in results['external_analyzers_used']:
                        results['external_analyzers_used'].append('rage_analyzer')
                  
                    results['analysis_results'][str(file_path)] = {
                        'file_type': Path(file_path).suffix,
                        'issues': issues,
                        'issue_count': len(issues)
                    }
      
        return results
  
    def correct_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """Correct all files in directory"""
        results = {
            'files_processed': 0,
            'files_corrected': 0,
            'files_analyzed': 0,
            'external_analysis': {},
            'external_analyzers_used': []
        }
      
        path = Path(directory)
        pattern = "**/*.py" if recursive else "*.py"
      
        for file_path in path.glob(pattern):
            if file_path.is_file():
                results['files_processed'] += 1
              
                # Analyze first
                issues = self.analyze_with_external(str(file_path))
                results['files_analyzed'] += 1
              
                if issues:
                    # Correct the file
                    correction_result = asyncio.run(self.correct_file(str(file_path)))
                    if correction_result.get('success') and correction_result.get('changes_made'):
                        results['files_corrected'] += 1
              
                # Record external analysis results
                if issues and any(issue.get('tool') != 'pyautofix' for issue in issues):
                    results['external_analysis'][str(file_path)] = issues
                    for issue in issues:
                        tool = issue.get('tool', '')
                        if tool.startswith('rage_analyzer') and 'rage_analyzer' not in results['external_analyzers_used']:
                            results['external_analyzers_used'].append('rage_analyzer')
      
        return results
  
    def get_external_analyzers_info(self) -> Dict[str, Any]:
        """Get information about external analyzers"""
        return self.external_analyzers.available_analyzers
  
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights"""
        return self.learning_system.get_learning_insights()
  
    def export_learned_knowledge(self, file_path: str) -> bool:
        """Export learned knowledge"""
        return self.learning_system.export_knowledge(file_path)

# [GUI and remaining code remains the same as in your original file...]
# Only the path-related functions are updated below

def verify_models():
    """Verify model installation - UPDATED for blueprint structure"""
    # Use relative path from the main pyautofix directory
    base_path = Path(__file__).parent / 'resources' / 'models'
  
    models_to_check = {
        'codegen-350m': ['pytorch_model.bin', 'config.json', 'vocab.json'],
        'codebert-base': ['pytorch_model.bin', 'config.json', 'vocab.json'],
        'sentence-transformers': ['pytorch_model.bin', 'config.json', 'vocab.txt']
    }
  
    print("Verifying model installation...")
    print(f"Base path: {base_path}")
    print()
  
    all_good = True
  
    for model_name, required_files in models_to_check.items():
        model_path = base_path / model_name
        print(f"Checking {model_name}:")
      
        if not model_path.exists():
            print(f"  ❌ Directory missing: {model_path}")
            all_good = False
            continue
          
        missing_files = []
        for file in required_files:
            if (model_path / file).exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} (missing)")
                missing_files.append(file)
              
        if missing_files:
            all_good = False
            print(f"  Missing files: {missing_files}")
        else:
            print(f"  ✅ {model_name} is complete!")
          
        print()
  
    if all_good:
        print("🎉 All models are properly installed!")
        print("You can now use PyAutoFix with AI capabilities.")
    else:
        print("❌ Some models are missing files.")
        print("Please check the downloads and directory structure.")
  
    return all_good

# [Rest of the main() and other functions remain the same...]

if __name__ == '__main__':
    main()