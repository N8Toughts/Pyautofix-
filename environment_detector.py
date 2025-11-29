import re
import ast
from typing import Dict, List, Any, Set, Optional
from pathlib import Path

class EnvironmentDetector:
    """
    Detects and handles different Python environments and external dependencies.
    """
  
    # Known environment patterns
    ENVIRONMENT_PATTERNS = {
        'blender': [
            r'import bpy',
            r'from bpy\s+import',
            r'bpy\.ops\.',
            r'bpy\.context',
            r'bpy\.data',
        ],
        'django': [
            r'from django\.',
            r'import django',
            r'@login_required',
            r'class.*View',
            r'from rest_framework',
        ],
        'flask': [
            r'from flask\s+import',
            r'import flask',
            r'@app\.route',
            r'flask\.render_template',
        ],
        'pytorch': [
            r'import torch',
            r'from torch\s+import',
            r'torch\.nn',
            r'torch\.optim',
        ],
        'tensorflow': [
            r'import tensorflow',
            r'import tf\.',
            r'tf\.Session',
            r'tensorflow\.keras',
        ],
        'opencv': [
            r'import cv2',
            r'cv2\.imread',
            r'cv2\.VideoCapture',
        ],
        'aws': [
            r'import boto3',
            r'boto3\.client',
            r'boto3\.resource',
        ]
    }
  
    def __init__(self):
        self.detected_environments = set()
        self.external_dependencies = set()
  
    def analyze_environment(self, file_path: str) -> Dict[str, Any]:
        """Analyze a file to detect its environment and dependencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
          
            environment_info = {
                'file': file_path,
                'detected_environments': self._detect_environments(content),
                'external_dependencies': self._find_external_dependencies(content),
                'environment_specific_issues': self._find_environment_specific_issues(content)
            }
            return environment_info
          
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'detected_environments': [],
                'external_dependencies': []
            }
  
    def _detect_environments(self, content: str) -> List[str]:
        """Detect which environments this code belongs to"""
        detected = []
        for env_name, patterns in self.ENVIRONMENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    detected.append(env_name)
                    break  # No need to check other patterns for this environment
        return list(set(detected))
  
    def _find_external_dependencies(self, content: str) -> List[Dict[str, str]]:
        """Find external dependencies and try to determine their purpose"""
        dependencies = []
      
        # Common external library patterns
        external_patterns = {
            'requests': r'import requests',
            'numpy': r'import numpy',
            'pandas': r'import pandas',
            'matplotlib': r'import matplotlib',
            'selenium': r'import selenium',
            'beautifulsoup4': r'from bs4\s+import|import bs4',
            'scikit-learn': r'from sklearn\s+import|import sklearn',
            'sqlalchemy': r'import sqlalchemy',
        }
      
        for dep_name, pattern in external_patterns.items():
            if re.search(pattern, content):
                dependencies.append({
                    'name': dep_name,
                    'purpose': self._guess_dependency_purpose(dep_name, content),
                    'confidence': 'high'
                })
        return dependencies
  
    def _guess_dependency_purpose(self, dep_name: str, content: str) -> str:
        """Guess what a dependency is used for based on usage patterns"""
        purpose_patterns = {
            'requests': {
                'api_client': r'requests\.(get|post|put|delete)',
                'web_scraping': r'requests\.get.*\.text|requests\.get.*\.content',
            },
            'numpy': {
                'numerical_computing': r'np\.array|numpy\.array',
                'linear_algebra': r'np\.dot|np\.linalg',
            },
            'pandas': {
                'data_analysis': r'pd\.read_csv|df\.groupby',
                'data_cleaning': r'df\.fillna|df\.dropna',
            }
        }
      
        if dep_name in purpose_patterns:
            for purpose, pattern in purpose_patterns[dep_name].items():
                if re.search(pattern, content):
                    return purpose
      
        return 'general'
  
    def _find_environment_specific_issues(self, content: str) -> List[Dict[str, Any]]:
        """Find issues specific to detected environments"""
        issues = []
        environments = self._detect_environments(content)
      
        for env in environments:
            env_issues = self._get_environment_issues(env, content)
            issues.extend(env_issues)
      
        return issues
  
    def _get_environment_issues(self, environment: str, content: str) -> List[Dict[str, Any]]:
        """Get environment-specific issues"""
        issues = []
      
        if environment == 'blender':
            issues.extend(self._check_blender_issues(content))
        elif environment == 'django':
            issues.extend(self._check_django_issues(content))
      
        return issues
  
    def _check_blender_issues(self, content: str) -> List[Dict[str, Any]]:
        """Check for Blender-specific issues"""
        issues = []
      
        # Check for common Blender anti-patterns
        blender_anti_patterns = [
            {
                'pattern': r'bpy\.context\.scene\.update\(\)',
                'description': 'Avoid bpy.context.scene.update() - use depsgraph.update() instead',
                'severity': 'warning'
            }
        ]
      
        for anti_pattern in blender_anti_patterns:
            if re.search(anti_pattern['pattern'], content):
                issues.append({
                    'type': 'environment_anti_pattern',
                    'environment': 'blender',
                    'description': anti_pattern['description'],
                    'severity': anti_pattern['severity']
                })
      
        return issues
  
    def _check_django_issues(self, content: str) -> List[Dict[str, Any]]:
        """Check for Django-specific issues"""
        issues = []
      
        django_anti_patterns = [
            {
                'pattern': r'from django\.shortcuts import render_to_response',
                'description': 'render_to_response is deprecated, use render instead',
                'severity': 'warning'
            }
        ]
      
        for anti_pattern in django_anti_patterns:
            if re.search(anti_pattern['pattern'], content):
                issues.append(anti_pattern)
      
        return issues