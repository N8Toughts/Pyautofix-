#!/usr/bin/env python3
"""
PyAutoFix Standalone Engine - No GUI Required
For modders who want direct engine access
"""

import sys
import os
import logging
from pathlib import Path

class PyAutoFixStandalone:
    """Pure engine without GUI - perfect for modding workflows"""
   
    def __init__(self):
        self.setup_logging()
        self.engine = self.initialize_engine()
       
    def setup_logging(self):
        """Simple logging for modders"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger("PyAutoFixStandalone")
   
    def initialize_engine(self):
        """Initialize just the core engine"""
        try:
            from .super_engine import SuperCorrectionEngine
            return SuperCorrectionEngine()
        except ImportError:
            self.logger.error("Could not import PyAutoFix engine")
            return None
   
    def quick_fix_file(self, file_path: str):
        """One-command file fixing - modder friendly"""
        if not self.engine:
            return {"success": False, "error": "Engine not available"}
       
        self.logger.info(f"🔧 Quick fixing: {file_path}")
       
        try:
            # Analyze
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
           
            issues = self.engine.analyze_code(code, file_path)
           
            # Auto-correct if issues found
            if issues:
                result = self.engine.correct_file(file_path)
                return {
                    "success": True,
                    "issues_found": len(issues),
                    "changes_made": result.get('changes_made', False),
                    "backup_created": result.get('backup_created'),
                    "issues": issues
                }
            else:
                return {
                    "success": True,
                    "issues_found": 0,
                    "changes_made": False,
                    "message": "No issues found - file is clean!"
                }
               
        except Exception as e:
            return {"success": False, "error": str(e)}
   
    def batch_process_mod(self, mod_folder: str):
        """Process entire mod folder - classic modder workflow"""
        mod_path = Path(mod_folder)
        python_files = list(mod_path.glob("**/*.py"))
       
        results = {
            "total_files": len(python_files),
            "files_fixed": 0,
            "total_issues": 0,
            "details": []
        }
       
        for py_file in python_files:
            file_result = self.quick_fix_file(str(py_file))
            results["details"].append({
                "file": str(py_file),
                "result": file_result
            })
           
            if file_result.get("success") and file_result.get("changes_made"):
                results["files_fixed"] += 1
                results["total_issues"] += file_result.get("issues_found", 0)
       
        return results

# Command line interface for modders
def main():
    if len(sys.argv) < 2:
        print("PyAutoFix Standalone - Modder Edition")
        print("Usage:")
        print("  python standalone_engine.py fix <file.py>")
        print("  python standalone_engine.py batch <mod_folder>")
        print("  python standalone_engine.py analyze <file.py>")
        return
   
    engine = PyAutoFixStandalone()
    command = sys.argv[1]
   
    if command == "fix" and len(sys.argv) == 3:
        result = engine.quick_fix_file(sys.argv[2])
        print(f"Result: {result}")
   
    elif command == "batch" and len(sys.argv) == 3:
        result = engine.batch_process_mod(sys.argv[2])
        print(f"Batch result: {result}")
   
    elif command == "analyze" and len(sys.argv) == 3:
        # Just analyze, don't fix
        if engine.engine:
            with open(sys.argv[2], 'r') as f:
                code = f.read()
            issues = engine.engine.analyze_code(code, sys.argv[2])
            print(f"Analysis found {len(issues)} issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Engine not available")
   
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()