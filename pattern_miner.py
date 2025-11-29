import re
import ast
from typing import List, Dict, Any, Set
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class PatternMiner:
    """Mines patterns from code corrections to learn new rules"""
  
    def __init__(self):
        self.patterns = defaultdict(list)
        self.common_fixes = {}
  
    def analyze_correction_pair(self, original: str, corrected: str, issues: List[Dict[str, Any]]):
        """Analyze a correction to identify patterns"""
        if original == corrected:
            return  # No changes made
      
        # Extract line-level changes
        original_lines = original.splitlines()
        corrected_lines = corrected.splitlines()
      
        changes = self._extract_line_changes(original_lines, corrected_lines)
      
        for change in changes:
            pattern_type = self._classify_change_pattern(change, issues)
            if pattern_type:
                self.patterns[pattern_type].append(change)
  
    def _extract_line_changes(self, original_lines: List[str], corrected_lines: List[str]) -> List[Dict[str, Any]]:
        """Extract specific line changes"""
        changes = []
        max_lines = min(len(original_lines), len(corrected_lines))
      
        for i in range(max_lines):
            if original_lines[i] != corrected_lines[i]:
                changes.append({
                    'line_number': i + 1,
                    'original': original_lines[i],
                    'corrected': corrected_lines[i],
                    'context_before': original_lines[max(0, i-2):i],
                    'context_after': original_lines[i+1:min(len(original_lines), i+3)]
                })
      
        return changes
  
    def _classify_change_pattern(self, change: Dict[str, Any], issues: List[Dict[str, Any]]) -> Optional[str]:
        """Classify the type of change pattern"""
        original = change['original']
        corrected = change['corrected']
      
        # Pattern classification logic
        if ' == None' in original and ' is None' in corrected:
            return 'none_comparison_fix'
        elif '.format(' in original and 'f"' in corrected:
            return 'f_string_conversion'
        elif 'import ' in original and 'import ' in corrected and original != corrected:
            return 'import_optimization'
        elif 'def ' in original and 'def ' in corrected and original != corrected:
            return 'function_optimization'
      
        return None
  
    def get_learned_rules(self) -> List[Dict[str, Any]]:
        """Extract learned rules from patterns"""
        rules = []
      
        for pattern_type, examples in self.patterns.items():
            if len(examples) >= 2:  # Need multiple examples to learn a rule
                rule = self._create_rule_from_pattern(pattern_type, examples)
                if rule:
                    rules.append(rule)
      
        return rules
  
    def _create_rule_from_pattern(self, pattern_type: str, examples: List[Dict]) -> Optional[Dict[str, Any]]:
        """Create a correction rule from pattern examples"""
        if not examples:
            return None
      
        # Create rule based on pattern type
        rule_template = self._get_rule_template(pattern_type)
        if not rule_template:
            return None
      
        return {
            'name': f'learned_{pattern_type}',
            'pattern': rule_template['pattern'],
            'replacement': rule_template['replacement'],
            'description': f'Learned rule for {pattern_type}',
            'severity': 'info',
            'confidence': len(examples) / 10.0,  # Normalize confidence
            'source': 'learned',
            'examples_count': len(examples)
        }
  
    def _get_rule_template(self, pattern_type: str) -> Optional[Dict[str, str]]:
        """Get rule template for different pattern types"""
        templates = {
            'none_comparison_fix': {
                'pattern': r'(\w+)\s*==\s*None',
                'replacement': r'\1 is None'
            },
            'f_string_conversion': {
                'pattern': r'\"(.*?)\.format\((.*?)\)',
                'replacement': r'f"\1{\2}"'
            }
        }
      
        return templates.get(pattern_type)