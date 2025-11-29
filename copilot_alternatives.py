import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MultiAICodeAssistant:
    """Integration with various AI code assistance tools"""
   
    def __init__(self):
        self.active_services = {}
        self._initialize_services()
   
    def _initialize_services(self):
        """Initialize available AI services"""
        self.active_services = {
            'ollama': self._check_ollama(),
            'lm_studio': self._check_lm_studio(),
            'openai_compatible': self._check_openai_compatible()
        }
   
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False
   
    def _check_lm_studio(self) -> bool:
        """Check if LM Studio is available"""
        try:
            response = requests.get('http://localhost:1234/v1/models', timeout=2)
            return response.status_code == 200
        except:
            return False
   
    def _check_openai_compatible(self) -> bool:
        """Check for OpenAI-compatible endpoints"""
        endpoints = ['http://localhost:1234/v1', 'http://localhost:8080/v1']
        for endpoint in endpoints:
            try:
                response = requests.get(f"{endpoint}/models", timeout=2)
                if response.status_code == 200:
                    return True
            except:
                continue
        return False
   
    def get_code_suggestions(self, code: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get code suggestions from available AI services"""
        suggestions = []
       
        if self.active_services['ollama']:
            suggestions.extend(self._get_ollama_suggestions(code, context))
       
        return self._rank_suggestions(suggestions)
   
    def _get_ollama_suggestions(self, code: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggestions from Ollama"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "codellama",
                    "prompt": f"Fix this Python code: {code}",
                    "stream": False
                }
            )
           
            if response.status_code == 200:
                return [{
                    'source': 'ollama',
                    'suggestion': response.json().get('response', ''),
                    'confidence': 0.7
                }]
        except Exception as e:
            logger.warning(f"Ollama request failed: {e}")
       
        return []
   
    def _rank_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Rank suggestions by confidence"""
        return sorted(suggestions, key=lambda x: x.get('confidence', 0), reverse=True)