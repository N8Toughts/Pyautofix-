import json
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FeedbackLearner:
    """Learn from user feedback and correction results"""
  
    def __init__(self, feedback_file: str = "feedback_data.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_data = []
        self._load_feedback_data()
  
    def _load_feedback_data(self):
        """Load existing feedback data"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    self.feedback_data = json.load(f)
                logger.info(f"Loaded {len(self.feedback_data)} feedback records")
            except Exception as e:
                logger.warning(f"Failed to load feedback data: {e}")
                self.feedback_data = []
    def record_correction(self, original_code: str, corrected_code: str,
                         issues: List[Dict[str, Any]], success: bool):
        """Record a correction attempt for learning"""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'original_code': original_code,
            'corrected_code': corrected_code,
            'issues': issues,
            'success': success,
            'code_hash': hash(original_code)  # For deduplication
        }
      
        self.feedback_data.append(feedback_entry)
        self._save_feedback_data()
  
    def record_user_feedback(self, original_code: str, corrected_code: str,
                           user_rating: int, notes: str = ""):
        """Record explicit user feedback"""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'original_code': original_code,
            'corrected_code': corrected_code,
            'user_rating': user_rating,
            'notes': notes,
            'type': 'explicit_feedback'
        }
      
        self.feedback_data.append(feedback_entry)
        self._save_feedback_data()
  
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learned patterns"""
        if not self.feedback_data:
            return {}
      
        total_corrections = len(self.feedback_data)
        successful_corrections = len([f for f in self.feedback_data if f.get('success')])
      
        # Most common issues
        all_issues = []
        for feedback in self.feedback_data:
            all_issues.extend([issue.get('description', '') for issue in feedback.get('issues', [])])
      
        from collections import Counter
        common_issues = Counter(all_issues).most_common(5)
      
        return {
            'total_corrections': total_corrections,
            'success_rate': successful_corrections / total_corrections if total_corrections > 0 else 0,
            'most_common_issues': common_issues,
            'data_size': total_corrections
        }
  
    def _save_feedback_data(self):
        """Save feedback data to file"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feedback data: {e}")