import ast
import re
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class IntelligentRuleSuggester:
    """Suggests new correction rules based on code analysis and patterns"""
  
    def __init__(self):
        self.pattern_database = PatternDatabase()
        self.similarity_analyzer = CodeSimilarityAnalyzer()
  
    def suggest_rules_from_codebase(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Suggest rules by analyzing codebase patterns"""
        suggestions = []
      
        # Analyze each file for potential improvements
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                file_suggestions = self._analyze_file_for_rule_suggestions(code, file_path)
                suggestions.extend(file_suggestions)
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
      
        # Deduplicate and rank suggestions
        return self._rank_suggestions(suggestions)
  
    def _analyze_file_for_rule_suggestions(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze a single file for rule suggestions"""
        suggestions = []
      
        # Check for common anti-patterns
        suggestions.extend(self._detect_anti_patterns(code, file_path))
      
        # Check for code style issues
        suggestions.extend(self._detect_style_issues(code, file_path))
      
        # Check for performance improvements
        suggestions.extend(self._detect_performance_issues(code, file_path))
      
        # Check for modern Python features
        suggestions.extend(self._detect_modernization_opportunities(code, file_path))
      
        return suggestions
  
    def _detect_anti_patterns(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect common anti-patterns"""
        anti_patterns = []
      
        # Check for range(len()) pattern
        if re.search(r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', code):
            anti_patterns.append({
                'type': 'anti_pattern',
                'pattern': 'range(len(...)) iteration',
                'description': 'Use direct iteration instead of range(len())',
                'example_before': 'for i in range(len(items)):',
                'example_after': 'for item in items:',
                'severity': 'warning',
                'confidence': 0.8
            })
      
        # Check for unnecessary list creation
        if re.search(r'list\(\[.*\]\)', code):
            anti_patterns.append({
                'type': 'anti_pattern',
                'pattern': 'unnecessary list creation',
                'description': 'Remove unnecessary list() call around list literal',
                'example_before': 'list([1, 2, 3])',
                'example_after': '[1, 2, 3]',
                'severity': 'info',
                'confidence': 0.9
            })
      
        return anti_patterns
  
    def _detect_style_issues(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect code style issues"""
        style_issues = []
        lines = code.splitlines()
      
        # Check line length
        for i, line in enumerate(lines):
            if len(line) > 100:  # PEP 8 suggests 79, but 100 is more practical
                style_issues.append({
                    'type': 'style',
                    'pattern': 'line too long',
                    'description': f'Line {i+1} exceeds 100 characters',
                    'line_number': i + 1,
                    'severity': 'info',
                    'confidence': 1.0
                })
      
        # Check for trailing whitespace
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                style_issues.append({
                    'type': 'style',
                    'pattern': 'trailing whitespace',
                    'description': f'Line {i+1} has trailing whitespace',
                    'line_number': i + 1,
                    'severity': 'info',
                    'confidence': 1.0
                })
      
        return style_issues
  
    def _detect_performance_issues(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect performance improvement opportunities"""
        performance_issues = []
      
        # Check for string concatenation in loops
        if re.search(r'(\w+\s*\+=\s*\w+)\s*#.*loop', code, re.IGNORECASE):
            performance_issues.append({
                'type': 'performance',
                'pattern': 'string concatenation in loop',
                'description': 'Use list and join for string concatenation in loops',
                'example_before': 'result = ""\nfor item in items:\n    result += str(item)',
                'example_after': 'result = "".join(str(item) for item in items)',
                'severity': 'warning',
                'confidence': 0.7
            })
      
        return performance_issues
  
    def _detect_modernization_opportunities(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect opportunities to use modern Python features"""
        modernizations = []
      
        # Check for f-string opportunities
        if re.search(r'\"[^\"]*%[^\"]*\"\s*%\s*\([^)]*\)', code):
            modernizations.append({
                'type': 'modernization',
                'pattern': 'f-string conversion',
                'description': 'Convert % formatting to f-string',
                'example_before': '"Hello %s" % name',
                'example_after': 'f"Hello {name}"',
                'severity': 'info',
                'confidence': 0.9
            })
      
        return modernizations
  
    def _rank_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank suggestions by relevance and impact"""
        scored_suggestions = []
      
        for suggestion in suggestions:
            score = self._calculate_suggestion_score(suggestion)
            scored_suggestions.append((score, suggestion))
      
        # Sort by score (descending)
        scored_suggestions.sort(key=lambda x: x[0], reverse=True)
        return [suggestion for score, suggestion in scored_suggestions]
  
    def _calculate_suggestion_score(self, suggestion: Dict[str, Any]) -> float:
        """Calculate a score for suggestion ranking"""
        score = 0.0
      
        # Base score from confidence
        score += suggestion.get('confidence', 0.5) * 40
      
        # Severity weighting
        severity_weights = {
            'error': 30,
            'warning': 20,
            'info': 10
        }
        score += severity_weights.get(suggestion.get('severity', 'info'), 10)
      
        # Type weighting
        type_weights = {
            'performance': 25,
            'anti_pattern': 20,
            'modernization': 15,
            'style': 5
        }
        score += type_weights.get(suggestion.get('type', 'info'), 10)
      
        return score

class PatternDatabase:
    """Database of known code patterns and their improvements"""
  
    def __init__(self):
        self.patterns = self._load_known_patterns()
  
    def _load_known_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load known improvement patterns"""
        return {
            'range_len_iteration': {
                'description': 'Use direct iteration instead of index-based loops',
                'before': 'for i in range(len(items)):',
                'after': 'for item in items:',
                'category': 'readability',
                'confidence': 0.9
            },
            'unnecessary_list': {
                'description': 'Remove unnecessary list() creation',
                'before': 'list([1, 2, 3])',
                'after': '[1, 2, 3]',
                'category': 'performance',
                'confidence': 0.8
            },
            'f_string_conversion': {
                'description': 'Convert .format() to f-string',
                'before': '"Hello {}".format(name)',
                'after': 'f"Hello {name}"',
                'category': 'modernization',
                'confidence': 0.95
            }
        }

class CodeSimilarityAnalyzer:
    """Analyzes code similarity to find patterns"""
  
    def find_similar_patterns(self, code1: str, code2: str, threshold: float = 0.7) -> float:
        """Calculate similarity between two code snippets"""
        # Simple similarity based on token overlap
        tokens1 = set(self._tokenize_code(code1))
        tokens2 = set(self._tokenize_code(code2))
      
        if not tokens1 or not tokens2:
            return 0.0
      
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return intersection / union if union > 0 else 0.0
  
    def _tokenize_code(self, code: str) -> List[str]:
        """Tokenize code for similarity analysis"""
        # Simple tokenization - split by common Python operators and whitespace
        tokens = re.findall(r'[a-zA-Z_]\w*|\d+|\S', code)
        return [token for token in tokens if len(token) > 1]  # Filter out single characters