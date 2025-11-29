import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json
import re

class AutoWriteManager:
    """
    Manages automatic writing of corrections with safety features.
    """
  
    def __init__(self, backup_dir: str = ".pyautofix_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.changes_made = []
  
    def safe_write_correction(self, file_path: str, new_content: str,
                            original_content: str, force: bool = False) -> Tuple[bool, str]:
        """
        Safely write corrections with backups and validation.
        """
        path = Path(file_path)
      
        # Create backup
        backup_path = self._create_backup(file_path, original_content)
      
        # Validate the correction
        validation_result = self._validate_correction(new_content, file_path)
        if not validation_result["valid"] and not force:
            return False, f"Validation failed: {validation_result['reason']}"
      
        try:
            # Write the corrected content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
          
            # Verify the write was successful
            with open(file_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
          
            if written_content != new_content:
                # Restore from backup
                self._restore_from_backup(file_path, backup_path)
                return False, "Write verification failed - content mismatch"
          
            # Record the change
            self._record_change(file_path, original_content, new_content, backup_path)
            return True, "Correction applied successfully"
          
        except Exception as e:
            # Restore from backup on error
            self._restore_from_backup(file_path, backup_path)
            return False, f"Write error: {e}"
  
    def _create_backup(self, file_path: str, content: str) -> Path:
        """Create a timestamped backup of the file."""
        path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.stem}_{timestamp}{path.suffix}.bak"
        backup_path = self.backup_dir / backup_name
      
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
      
        return backup_path
  
    def _restore_from_backup(self, file_path: str, backup_path: Path):
        """Restore a file from backup."""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
          
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        except Exception as e:
            print(f"Warning: Could not restore from backup: {e}")
  
    def _validate_correction(self, new_content: str, file_path: str) -> Dict[str, Any]:
        """Validate that the correction doesn't break the code."""
        try:
            # Syntax check
            compile(new_content, file_path, 'exec')
          
            # Basic safety checks
            if self._contains_dangerous_patterns(new_content):
                return {"valid": False, "reason": "Contains potentially dangerous patterns"}
          
            return {"valid": True, "reason": "Validation passed"}
          
        except SyntaxError as e:
            return {"valid": False, "reason": f"Syntax error: {e}"}
        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {e}"}
  
    def _contains_dangerous_patterns(self, content: str) -> bool:
        """Check for potentially dangerous code patterns."""
        dangerous_patterns = [
            r"__import__\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(",
            r"open\s*\([^)]*[wax]\+\s*\)",  # Write modes
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"shutil\.rmtree\s*\(",
        ]
      
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
      
        return False
  
    def _record_change(self, file_path: str, original: str, new: str, backup_path: Path):
        """Record the change for undo capability."""
        change_record = {
            'file': file_path,
            'timestamp': datetime.now().isoformat(),
            'backup_path': str(backup_path),
            'original_lines': len(original.splitlines()),
            'new_lines': len(new.splitlines()),
        }
      
        self.changes_made.append(change_record)
      
        # Save change log
        change_log = self.backup_dir / "changes.json"
        changes = []
        if change_log.exists():
            with open(change_log, 'r') as f:
                changes = json.load(f)
      
        changes.append(change_record)
      
        with open(change_log, 'w') as f:
            json.dump(changes, f, indent=2)
  
    def undo_last_change(self) -> bool:
        """Undo the last change made by the auto-writer."""
        if not self.changes_made:
            return False
      
        last_change = self.changes_made.pop()
        try:
            with open(last_change['backup_path'], 'r', encoding='utf-8') as f:
                backup_content = f.read()
          
            with open(last_change['file'], 'w', encoding='utf-8') as f:
                f.write(backup_content)
          
            print(f"Undid changes to {last_change['file']}")
            return True
          
        except Exception as e:
            print(f"Failed to undo changes: {e}")
            return False