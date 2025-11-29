import json
import pickle
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import hashlib
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Advanced learning features will be limited.")

class AdvancedLearningSystem:
    """Advanced learning system that continuously improves from corrections"""
  
    def __init__(self, model_dir: str = "learning_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
      
        # Learning components
        self.correction_classifier = None
        self.performance_tracker = PerformanceTracker()
      
        # Data storage
        self.correction_history = []
        self.user_feedback = []
        self.learned_patterns = defaultdict(list)
      
        self._load_existing_models()
  
    def _load_existing_models(self):
        """Load existing trained models if available"""
        if not SKLEARN_AVAILABLE:
            return
      
        model_files = {
            'correction_classifier': 'correction_classifier.pkl',
            'vectorizer': 'vectorizer.pkl'
        }
      
        for model_name, filename in model_files.items():
            model_path = self.model_dir / filename
            if model_path.exists():
                try:
                    if model_name == 'correction_classifier':
                        self.correction_classifier = joblib.load(model_path)
                    elif model_name == 'vectorizer':
                        self.vectorizer = joblib.load(model_path)
                except Exception as e:
                    logger.warning(f"Error loading {model_name}: {e}")
  
    def record_correction_outcome(self, original_code: str, corrected_code: str,
                                issues: List[Dict[str, Any]], success: bool,
                                correction_type: str, confidence: float,
                                user_feedback: Optional[int] = None):
        """Record the outcome of a correction for learning"""
        correction_record = {
            'timestamp': datetime.now().isoformat(),
            'original_code': original_code,
            'corrected_code': corrected_code,
            'issues': issues,
            'success': success,
            'correction_type': correction_type,
            'confidence': confidence,
            'user_feedback': user_feedback,
            'code_hash': self._hash_code(original_code),
            'features': self._extract_features(original_code, issues)
        }
      
        self.correction_history.append(correction_record)
      
        # Retrain models periodically
        if len(self.correction_history) % 50 == 0:
            self._retrain_models()
      
        self._save_learning_data()
  
    def _extract_features(self, code: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features from code and issues for machine learning"""
        features = {
            'code_length': len(code),
            'line_count': len(code.splitlines()),
            'issue_count': len(issues),
            'issue_types': [issue.get('type', 'unknown') for issue in issues],
            'severity_counts': Counter(issue.get('severity', 'unknown') for issue in issues),
            'has_imports': 'import ' in code,
            'has_functions': 'def ' in code,
            'has_classes': 'class ' in code,
            'complexity_estimate': self._estimate_complexity(code)
        }
        return features
  
    def _estimate_complexity(self, code: str) -> float:
        """Estimate code complexity using simple heuristics"""
        lines = code.splitlines()
        if not lines:
            return 0.0
      
        complexity_indicators = 0
        complexity_indicators += code.count('if ')
        complexity_indicators += code.count('for ')
        complexity_indicators += code.count('while ')
        complexity_indicators += code.count('try:')
        complexity_indicators += code.count('except ')
        complexity_indicators += code.count('with ')
      
        return complexity_indicators / len(lines)
  
    def _hash_code(self, code: str) -> str:
        """Create a hash of the code for deduplication"""
        return hashlib.md5(code.encode()).hexdigest()
  
    def predict_correction_success(self, code: str, issues: List[Dict[str, Any]]) -> float:
        """Predict the probability of successful correction"""
        if not self.correction_classifier or not SKLEARN_AVAILABLE:
            return 0.7  # Default confidence
      
        features = self._extract_features(code, issues)
        feature_vector = self._create_feature_vector(features)
      
        try:
            probability = self.correction_classifier.predict_proba([feature_vector])[0][1]
            return float(probability)
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.7
  
    def _create_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """Create a feature vector for machine learning"""
        vector = []
      
        # Numerical features
        vector.extend([
            features['code_length'],
            features['line_count'],
            features['issue_count'],
            features['complexity_estimate']
        ])
      
        # Boolean features
        vector.extend([
            float(features['has_imports']),
            float(features['has_functions']),
            float(features['has_classes'])
        ])
      
        # Severity counts
        severities = ['error', 'warning', 'info']
        for severity in severities:
            vector.append(features['severity_counts'].get(severity, 0))
      
        return vector
  
    def _retrain_models(self):
        """Retrain machine learning models with new data"""
        if not SKLEARN_AVAILABLE or len(self.correction_history) < 20:
            return  # Not enough data
      
        # Prepare training data
        X = []
        y = []
      
        for record in self.correction_history:
            features = record['features']
            feature_vector = self._create_feature_vector(features)
            X.append(feature_vector)
            y.append(1 if record['success'] else 0)
      
        if len(set(y)) < 2:
            return  # Need both success and failure examples
      
        # Train classifier
        self.correction_classifier = GradientBoostingClassifier(
            n_estimators=100, random_state=42, max_depth=5
        )
        self.correction_classifier.fit(X, y)
      
        # Save models
        joblib.dump(self.correction_classifier, self.model_dir / 'correction_classifier.pkl')
        logger.info(f"Models retrained with {len(X)} examples")
  
    def get_learned_rules(self) -> List[Dict[str, Any]]:
        """Get rules learned from correction patterns"""
        # This would integrate with PatternMiner in a real implementation
        return []
  
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics and insights"""
        return self.performance_tracker.get_metrics(self.correction_history)
  
    def _save_learning_data(self):
        """Save learning data to disk"""
        data = {
            'correction_history': self.correction_history,
            'user_feedback': self.user_feedback,
            'learned_patterns': dict(self.learned_patterns)
        }
      
        with open(self.model_dir / 'learning_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)

class PerformanceTracker:
    """Tracks and analyzes performance metrics"""
  
    def get_metrics(self, correction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not correction_history:
            return {}
      
        total_corrections = len(correction_history)
        successful_corrections = len([c for c in correction_history if c.get('success', False)])
      
        # Calculate success rate by correction type
        success_by_type = defaultdict(list)
        for correction in correction_history:
            corr_type = correction.get('correction_type', 'unknown')
            success_by_type[corr_type].append(correction.get('success', False))
      
        success_rates = {}
        for corr_type, successes in success_by_type.items():
            success_rates[corr_type] = sum(successes) / len(successes) if successes else 0
      
        # Most common issues
        all_issues = []
        for correction in correction_history:
            all_issues.extend([issue.get('type', 'unknown') for issue in correction.get('issues', [])])
      
        common_issues = Counter(all_issues).most_common(10)
      
        return {
            'total_corrections': total_corrections,
            'success_rate_overall': successful_corrections / total_corrections,
            'success_rate_by_type': success_rates,
            'most_common_issues': common_issues,
            'average_confidence': np.mean([c.get('confidence', 0) for c in correction_history]) if correction_history else 0
        }