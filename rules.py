import re
import ast
from typing import List, Dict, Any, Callable, Optional

class CodeRule:
    """Represents a code correction rule"""
  
    def __init__(self, name: str, pattern: str, replacement: str,
                 description: str, severity: str = "warning"):
        self.name = name
        self.pattern = pattern
        self.replacement = replacement
        self.description = description
        self.severity = severity
  
    def matches(self, code: str) -> bool:
        """Check if rule matches the code"""
        return bool(re.search(self.pattern, code, re.MULTILINE | re.DOTALL))
  
    def apply(self, code: str) -> str:
        """Apply rule to code"""
        return re.sub(self.pattern, self.replacement, code, flags=re.MULTILINE | re.DOTALL)

class RuleEngine:
    """Engine for managing and applying code rules"""
  
    def __init__(self):
        self.rules: List[CodeRule] = []
        self.load_default_rules()
  
    def load_default_rules(self):
        """Load default correction rules"""
        try:
            from ..rules_database.default_rules import DEFAULT_RULES
            for rule_data in DEFAULT_RULES:
                rule = CodeRule(**rule_data)
                self.rules.append(rule)
        except ImportError:
            # Fallback basic rules
            self.rules = [
                CodeRule(
                    name='basic_none_check',
                    pattern=r'([\w\.]+)\s*==\s*None',
                    replacement=r'\1 is None',
                    description='Use "is" for None comparison'
                )
            ]
  
    def add_rule(self, rule: CodeRule):
        """Add a new rule"""
        self.rules.append(rule)
  
    def analyze_code(self, code: str, file_path: str = "") -> List[Dict[str, Any]]:
        """Analyze code for rule violations"""
        issues = []
        for rule in self.rules:
            if rule.matches(code):
                issues.append({
                    'type': 'rule_violation',
                    'rule': rule.name,
                    'description': rule.description,
                    'severity': rule.severity,
                    'file': file_path,
                    'fixable': True
                })
        return issues
  
    def correct_code(self, code: str, file_path: str = "") -> str:
        """Apply all matching rules to code"""
        corrected_code = code
        for rule in self.rules:
            if rule.matches(corrected_code):
                original = corrected_code
                corrected_code = rule.apply(corrected_code)
                if corrected_code != original:
                    print(f"Applied rule '{rule.name}' to {file_path}")
        return corrected_code