"""
Texture analysis plugin for RAGE Analyzer
"""

PLUGIN_NAME = "Texture Analyzer"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Analyzes texture files for game assets"
SUPPORTED_FORMATS = ['.dds', '.png', '.jpg', '.wtd']

def analyze_file(file_path: str) -> list:
    """
    Analyze a texture file
   
    Args:
        file_path: Path to the texture file
       
    Returns:
        List of issues found
    """
    issues = []
   
    try:
        file_size = len(open(file_path, 'rb').read())
       
        # Size-based analysis
        if file_size > 50 * 1024 * 1024:  # 50MB
            issues.append({
                'type': 'size_warning',
                'message': 'Very large texture file may impact performance',
                'severity': 'warning'
            })
        elif file_size > 10 * 1024 * 1024:  # 10MB
            issues.append({
                'type': 'size_info',
                'message': 'Large texture file',
                'severity': 'info'
            })
       
        # Format-specific checks
        if file_path.endswith('.dds'):
            issues.append({
                'type': 'format_info',
                'message': 'DDS texture format detected',
                'severity': 'info'
            })
       
        elif file_path.endswith('.wtd'):
            issues.append({
                'type': 'format_info',
                'message': 'RAGE texture dictionary detected',
                'severity': 'info'
            })
   
    except Exception as e:
        issues.append({
            'type': 'analysis_error',
            'message': f'Texture analysis failed: {e}',
            'severity': 'error'
        })
   
    return issues