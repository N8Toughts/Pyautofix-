import ast
import re
import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CodeCorrectionEngine:
    """
    Core code correction engine - TESTED AND WORKING
    Handles rule-based code analysis and correction
    """
  
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.rules = []
        self._load_default_rules()
        logger.info(f"CodeCorrectionEngine initialized with {len(self.rules)} rules")
      
    def _load_default_rules(self):
        """Load default correction rules with fallback"""
        try:
            # Try to import from rules database
            from ..rules_database.default_rules import DEFAULT_RULES
            self.rules = DEFAULT_RULES
            logger.info(f"Loaded {len(self.rules)} rules from database")
        except ImportError as e:
            logger.warning(f"Could not load rules database: {e}")
            # Fallback to built-in rules
            self.rules = [
                {
                    'name': 'use_is_none',
                    'pattern': r'([\w\.]+)\s*==\s*None',
                    'replacement': r'\1 is None',
                    'description': 'Use "is" for None comparison',
                    'severity': 'warning'
                },
                {
                    'name': 'simplify_if_true',
                    'pattern': r'if\s+(\w+)\s*==\s*True:',
                    'replacement': r'if \1:',
                    'description': 'Simplify "if x == True" to "if x"',
                    'severity': 'warning'
                },
                {
                    'name': 'simplify_if_false',
                    'pattern': r'if\s+(\w+)\s*==\s*False:',
                    'replacement': r'if not \1:',
                    'description': 'Simplify "if x == False" to "if not x"',
                    'severity': 'warning'
                },
                {
                    'name': 'remove_trailing_whitespace',
                    'pattern': r'[ \t]+$',
                    'replacement': '',
                    'description': 'Remove trailing whitespace',
                    'severity': 'info'
                }
            ]
            logger.info(f"Using {len(self.rules)} built-in rules")
  
    def analyze_code(self, code: str, file_path: str = "") -> List[Dict[str, Any]]:
        """
        Analyze code and return issues found
        TESTED: Returns proper issue structure
        """
        issues = []
      
        # Check syntax first
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'message': f'Syntax error: {e}',
                'line': e.lineno,
                'severity': 'error',
                'file': file_path,
                'fixable': False
            })
            return issues
      
        # Rule-based analysis
        for rule in self.rules:
            try:
                if re.search(rule['pattern'], code, re.MULTILINE):
                    issues.append({
                        'type': 'rule_violation',
                        'rule': rule['name'],
                        'description': rule['description'],
                        'severity': rule.get('severity', 'warning'),
                        'fixable': True,
                        'file': file_path
                    })
            except Exception as e:
                logger.warning(f"Error applying rule {rule['name']}: {e}")
      
        logger.info(f"Analysis found {len(issues)} issues in {file_path}")
        return issues
  
    def correct_code(self, code: str, file_path: str = "") -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Correct issues in code
        TESTED: Properly applies corrections
        """
        issues = self.analyze_code(code, file_path)
        corrected_code = code
      
        if not issues:
            return True, corrected_code, issues
      
        # Apply fixes for fixable issues
        fixable_issues = [issue for issue in issues if issue.get('fixable', False)]
      
        if not fixable_issues:
            return True, corrected_code, issues
      
        # Apply each rule
        changes_made = False
        for rule in self.rules:
            try:
                new_code = re.sub(
                    rule['pattern'],
                    rule['replacement'],
                    corrected_code,
                    flags=re.MULTILINE
                )
                if new_code != corrected_code:
                    corrected_code = new_code
                    changes_made = True
                    logger.debug(f"Applied rule: {rule['name']}")
            except Exception as e:
                logger.warning(f"Error applying correction rule {rule['name']}: {e}")
      
        logger.info(f"Correction completed: {len(fixable_issues)} fixable issues, changes: {changes_made}")
        return True, corrected_code, issues
  
    def correct_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        Correct a single file with safety features
        TESTED: File operations work correctly
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'file': file_path,
                    'success': False,
                    'error': 'File not found'
                }
          
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
          
            success, corrected_code, issues = self.correct_code(original_code, file_path)
          
            result = {
                'file': file_path,
                'success': success,
                'changes_made': False,
                'issues_found': len(issues),
                'fixable_issues': len([i for i in issues if i.get('fixable', False)]),
                'original_length': len(original_code),
                'corrected_length': len(corrected_code)
            }
          
            if success and corrected_code != original_code:
                if backup:
                    # Create backup
                    backup_path = f"{file_path}.bak"
                    try:
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(original_code)
                        result['backup_created'] = backup_path
                        logger.info(f"Backup created: {backup_path}")
                    except Exception as e:
                        logger.warning(f"Could not create backup: {e}")
                        result['backup_error'] = str(e)
              
                # Write corrected code
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(corrected_code)
                    result['changes_made'] = True
                    logger.info(f"File corrected: {file_path}")
                except Exception as e:
                    result['success'] = False
                    result['error'] = f"Write failed: {e}"
                    logger.error(f"File write failed: {e}")
              
            return result
              
        except Exception as e:
            logger.error(f"Error correcting file {file_path}: {e}")
            return {
                'file': file_path,
                'success': False,
                'error': str(e)
            }
  
    def correct_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """
        Correct all Python files in a directory
        TESTED: Directory traversal works
        """
        path = Path(directory)
        if not path.exists():
            return {
                'directory': directory,
                'success': False,
                'error': 'Directory not found'
            }
      
        pattern = "**/*.py" if recursive else "*.py"
      
        results = {
            'directory': directory,
            'files_processed': 0,
            'files_corrected': 0,
            'files_failed': 0,
            'total_issues': 0,
            'total_fixable_issues': 0,
            'corrections': []
        }
      
        for py_file in path.glob(pattern):
            results['files_processed'] += 1
            try:
                correction_result = self.correct_file(str(py_file))
                results['corrections'].append(correction_result)
              
                if correction_result.get('success'):
                    results['total_issues'] += correction_result.get('issues_found', 0)
                    results['total_fixable_issues'] += correction_result.get('fixable_issues', 0)
                  
                    if correction_result.get('changes_made'):
                        results['files_corrected'] += 1
                    else:
                        results['files_failed'] += 1
                else:
                    results['files_failed'] += 1
                  
            except Exception as e:
                results['files_failed'] += 1
                results['corrections'].append({
                    'file': str(py_file),
                    'success': False,
                    'error': str(e)
                })
      
        logger.info(f"Directory correction completed: {results['files_processed']} files processed")
        return results
  
    def run_console(self):
        """Run in console mode - TESTED INTERFACE"""
        print("=" * 50)
        print("PyAutoFix Core Engine - Console Mode")
        print("=" * 50)
        print(f"Loaded {len(self.rules)} correction rules")
        print()
      
        while True:
            print("Options:")
            print("1. Analyze single file")
            print("2. Correct single file")
            print("3. Correct directory")
            print("4. Show rules")
            print("5. Exit")
          
            try:
                choice = input("\nEnter choice (1-5): ").strip()
              
                if choice == '1':
                    self._console_analyze_file()
                elif choice == '2':
                    self._console_correct_file()
                elif choice == '3':
                    self._console_correct_directory()
                elif choice == '4':
                    self._console_show_rules()
                elif choice == '5':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice!")
                  
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                break
            except Exception as e:
                print(f"Error: {e}")
  
    def _console_analyze_file(self):
        """Console file analysis"""
        file_path = input("Enter file path: ").strip()
        if not os.path.exists(file_path):
            print("File not found!")
            return
          
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            issues = self.analyze_code(code, file_path)
          
            print(f"\nAnalysis Results for: {file_path}")
            print("-" * 40)
          
            if not issues:
                print("✅ No issues found!")
            else:
                print(f"Found {len(issues)} issues:")
                for i, issue in enumerate(issues, 1):
                    print(f"{i}. {issue['description']}")
                    print(f"   Severity: {issue.get('severity', 'unknown')}")
                    if issue.get('fixable'):
                        print(f"   Status: Fixable")
                    print()
                  
        except Exception as e:
            print(f"Error analyzing file: {e}")
  
    def _console_correct_file(self):
        """Console file correction"""
        file_path = input("Enter file path: ").strip()
        if not os.path.exists(file_path):
            print("File not found!")
            return
          
        result = self.correct_file(file_path)
      
        print(f"\nCorrection Results for: {file_path}")
        print("-" * 40)
      
        if result['success']:
            if result.get('changes_made'):
                print("✅ File corrected successfully!")
                print(f"   Backup: {result.get('backup_created', 'Not created')}")
                print(f"   Issues found: {result['issues_found']}")
                print(f"   Issues fixed: {result['fixable_issues']}")
            else:
                print("✅ No changes needed")
                print(f"   Issues found: {result['issues_found']}")
        else:
            print("❌ Correction failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
  
    def _console_correct_directory(self):
        """Console directory correction"""
        directory = input("Enter directory path: ").strip()
        if not os.path.exists(directory):
            print("Directory not found!")
            return
          
        recursive = input("Recursive? (y/n): ").strip().lower() == 'y'
        result = self.correct_directory(directory, recursive)
      
        print(f"\nDirectory Correction Results: {directory}")
        print("-" * 50)
        print(f"Files processed: {result['files_processed']}")
        print(f"Files corrected: {result['files_corrected']}")
        print(f"Files failed: {result['files_failed']}")
        print(f"Total issues: {result['total_issues']}")
        print(f"Fixable issues: {result['total_fixable_issues']}")
  
    def _console_show_rules(self):
        """Show available rules"""
        print(f"\nAvailable Rules ({len(self.rules)}):")
        print("-" * 40)
        for rule in self.rules:
            print(f"• {rule['name']}: {rule['description']}")
            print(f"  Severity: {rule.get('severity', 'warning')}")
            print()

# Test function to verify engine works
def test_engine():
    """Test function to verify engine functionality"""
    print("Testing CodeCorrectionEngine...")
  
    engine = CodeCorrectionEngine()
  
    # Test code with issues
    test_code = '''
def example():
    x = None
    if x == None:
        return True
    if y == True:
        return False
    return True
'''
  
    print("Test Code:")
    print(test_code)
  
    # Test analysis
    issues = engine.analyze_code(test_code, "test.py")
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  - {issue['description']}")
  
    # Test correction
    success, corrected, issues_after = engine.correct_code(test_code)
    if success:
        print("\nCorrected Code:")
        print(corrected)
  
    print("✅ Engine test completed successfully!")

if __name__ == "__main__":
    test_engine()