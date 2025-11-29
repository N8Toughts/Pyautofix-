from .default_rules import DEFAULT_RULES

__all__ = [
    'DEFAULT_RULES'
]

#root/rules_database/default_rules.py
DEFAULT_RULES = [
    {
        'name': 'use_is_none',
        'pattern': r'([\w\.]+)\s*==\s*None',
        'replacement': r'\1 is None',
        'description': 'Use "is" for None comparison',
        'severity': 'warning'
    },
    {
        'name': 'use_is_not_none',
        'pattern': r'([\w\.]+)\s*!=\s*None',
        'replacement': r'\1 is not None',
        'description': 'Use "is not" for None comparison',
        'severity': 'warning'
    },
    {
        'name': 'simplify_if_expression',
        'pattern': r'if\s+(\w+)\s*==\s*True:',
        'replacement': r'if \1:',
        'description': 'Simplify "if x == True" to "if x"',
        'severity': 'warning'
    },
    {
        'name': 'simplify_if_not_expression',
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
    },
    {
        'name': 'use_f_string',
        'pattern': r'\"([^\"]*)\"\.format\(([^)]+)\)',
        'replacement': r'f"\1{\2}"',
        'description': 'Convert .format() to f-string',
        'severity': 'info'
    },
    {
        'name': 'prefer_list_comprehension',
        'pattern': r'(\w+)\s*=\s*\[\]\s*for\s+(\w+)\s+in\s+(\w+)\s*:\s*\1\.append\(([^)]+)\)',
        'replacement': r'\1 = [\4 for \2 in \3]',
        'description': 'Use list comprehension instead of append in loop',
        'severity': 'info'
    },
    {
        'name': 'simplify_boolean_return',
        'pattern': r'if\s+(\w+)\s*:\s*return\s+True\s*else\s*:\s*return\s+False',
        'replacement': r'return \1',
        'description': 'Simplify boolean return statement',
        'severity': 'info'
    },
    {
        'name': 'use_join_for_strings',
        'pattern': r'(\w+)\s*=\s*""\s*for\s+(\w+)\s+in\s+(\w+)\s*:\s*\1\s*\+=\s*str\((\w+)\)',
        'replacement': r'\1 = "".join(str(\4) for \2 in \3]',
        'description': 'Use join for string concatenation in loops',
        'severity': 'warning'
    },
    {
        'name': 'prefer_get_with_default',
        'pattern': r'if\s+(\w+)\s+in\s+(\w+)\s*:\s*\3\s*=\s*\2\[\1\]\s*else\s*:\s*\3\s*=\s*([^\\n]+)',
        'replacement': r'\3 = \2.get(\1, \4)',
        'description': 'Use dict.get() with default value',
        'severity': 'info'
    }
]