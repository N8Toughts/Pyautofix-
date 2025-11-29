"""
Example plugin for RAGE Analyzer
"""

PLUGIN_NAME = "Example Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "An example plugin demonstrating the plugin system"
SUPPORTED_FORMATS = ['.xml', '.json', '.txt']

def analyze_file(file_path: str) -> list:
    """
    Analyze a file and return issues found
   
    Args:
        file_path: Path to the file to analyze
       
    Returns:
        List of issues found
    """
    issues = []
   
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
       
        # Example analysis rules
        if file_path.endswith('.xml'):
            if '<?xml' not in content:
                issues.append({
                    'type': 'format_error',
                    'message': 'Missing XML declaration',
                    'severity': 'warning'
                })
       
        elif file_path.endswith('.json'):
            import json
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                issues.append({
                    'type': 'syntax_error',
                    'message': f'Invalid JSON: {e}',
                    'severity': 'error'
                })
       
        elif file_path.endswith('.txt'):
            if len(content) > 10000:
                issues.append({
                    'type': 'size_warning',
                    'message': 'Large text file may impact performance',
                    'severity': 'warning'
                })
   
    except Exception as e:
        issues.append({
            'type': 'analysis_error',
            'message': f'Analysis failed: {e}',
            'severity': 'error'
        })
   
    return issues