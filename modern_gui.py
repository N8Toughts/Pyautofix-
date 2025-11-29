import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

class PyAutoFixGUI:
    """Modern GUI for PyAutoFix with comprehensive features"""
  
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyAutoFix Ultimate - AI-Powered Code Correction")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
      
        # Initialize engine
        try:
            from ..core.super_engine import SuperCorrectionEngine
            self.engine = SuperCorrectionEngine()
            logger.info("Super engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize engine: {e}")
            messagebox.showerror("Error", f"Failed to initialize engine: {e}")
            self.engine = None
      
        self.setup_gui()
      
    def setup_gui(self):
        """Setup the modern GUI interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
      
        # Title
        title_label = ttk.Label(
            main_frame,
            text="PyAutoFix Ultimate",
            font=("Arial", 16, "bold"),
            foreground="#2E86AB"
        )
        title_label.pack(pady=(0, 20))
      
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Target Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
      
        # Single file selection
        file_row = ttk.Frame(file_frame)
        file_row.pack(fill=tk.X, pady=5)
      
        ttk.Label(file_row, text="Single File:").pack(side=tk.LEFT)
        self.file_path = tk.StringVar()
        ttk.Entry(file_row, textvariable=self.file_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_row, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
      
        # Directory selection
        dir_row = ttk.Frame(file_frame)
        dir_row.pack(fill=tk.X, pady=5)
      
        ttk.Label(dir_row, text="Directory:").pack(side=tk.LEFT)
        self.dir_path = tk.StringVar()
        ttk.Entry(dir_row, textvariable=self.dir_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_row, text="Browse", command=self.browse_directory).pack(side=tk.LEFT)
      
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
      
        ttk.Button(
            button_frame,
            text="Analyze File",
            command=self.analyze_file,
            width=15
        ).pack(side=tk.LEFT, padx=5)
      
        ttk.Button(
            button_frame,
            text="Correct File",
            command=self.correct_file,
            width=15
        ).pack(side=tk.LEFT, padx=5)
      
        ttk.Button(
            button_frame,
            text="Analyze Directory",
            command=self.analyze_directory,
            width=15
        ).pack(side=tk.LEFT, padx=5)
      
        ttk.Button(
            button_frame,
            text="Correct Directory",
            command=self.correct_directory,
            width=15
        ).pack(side=tk.LEFT, padx=5)
      
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
      
        # Create notebook for different views
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
      
        # Issues tab
        issues_frame = ttk.Frame(self.notebook)
        self.notebook.add(issues_frame, text="Issues")
      
        self.issues_text = scrolledtext.ScrolledText(issues_frame, wrap=tk.WORD)
        self.issues_text.pack(fill=tk.BOTH, expand=True)
      
        # Statistics tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
      
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
      
        # Learning tab
        learning_frame = ttk.Frame(self.notebook)
        self.notebook.add(learning_frame, text="Learning Insights")
      
        self.learning_text = scrolledtext.ScrolledText(learning_frame, wrap=tk.WORD)
        self.learning_text.pack(fill=tk.BOTH, expand=True)
      
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
      
        # Initialize learning insights
        self.update_learning_insights()
  
    def browse_file(self):
        """Browse for a file"""
        filename = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
  
    def browse_directory(self):
        """Browse for a directory"""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            self.dir_path.set(directory)
  
    def analyze_file(self):
        """Analyze a single file"""
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
      
        if not self.engine:
            messagebox.showerror("Error", "Engine not initialized")
            return
      
        def analyze_thread():
            self.update_status("Analyzing file...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
              
                if self.engine.available_systems['core_engine']:
                    issues = self.engine.available_systems['core_engine'].analyze_code(code, file_path)
                  
                    # Update GUI in main thread
                    self.root.after(0, self.display_analysis_results, issues, file_path)
                    self.update_status("Analysis complete")
                  
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {e}"))
                self.update_status("Analysis failed")
      
        threading.Thread(target=analyze_thread, daemon=True).start()
  
    def correct_file(self):
        """Correct a single file"""
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
      
        if not self.engine:
            messagebox.showerror("Error", "Engine not initialized")
            return
      
        def correct_thread():
            self.update_status("Correcting file...")
            try:
                result = self.engine.correct_file(file_path)
              
                # Update GUI in main thread
                self.root.after(0, self.display_correction_results, result)
                self.update_status("Correction complete")
              
                # Update learning insights
                self.root.after(0, self.update_learning_insights)
              
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Correction failed: {e}"))
                self.update_status("Correction failed")
      
        threading.Thread(target=correct_thread, daemon=True).start()
  
    def analyze_directory(self):
        """Analyze a directory"""
        directory = self.dir_path.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
      
        if not self.engine:
            messagebox.showerror("Error", "Engine not initialized")
            return
      
        def analyze_thread():
            self.update_status("Analyzing directory...")
            try:
                # Use core engine for directory analysis
                python_files = list(Path(directory).glob("**/*.py"))
                total_issues = 0
                file_results = []
              
                for py_file in python_files[:20]:  # Limit to first 20 files
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                  
                    issues = self.engine.available_systems['core_engine'].analyze_code(code, str(py_file))
                    total_issues += len(issues)
                    file_results.append({
                        'file': str(py_file),
                        'issues': len(issues)
                    })
              
                # Update GUI in main thread
                self.root.after(0, self.display_directory_analysis, file_results, total_issues, directory)
                self.update_status("Directory analysis complete")
              
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Directory analysis failed: {e}"))
                self.update_status("Directory analysis failed")
      
        threading.Thread(target=analyze_thread, daemon=True).start()
  
    def correct_directory(self):
        """Correct a directory"""
        directory = self.dir_path.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
      
        if not self.engine:
            messagebox.showerror("Error", "Engine not initialized")
            return
      
        def correct_thread():
            self.update_status("Correcting directory...")
            try:
                result = self.engine.available_systems['core_engine'].correct_directory(directory)
              
                # Update GUI in main thread
                self.root.after(0, self.display_directory_correction, result)
                self.update_status("Directory correction complete")
              
                # Update learning insights
                self.root.after(0, self.update_learning_insights)
              
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Directory correction failed: {e}"))
                self.update_status("Directory correction failed")
      
        threading.Thread(target=correct_thread, daemon=True).start()
  
    def display_analysis_results(self, issues, file_path):
        """Display analysis results"""
        self.issues_text.delete(1.0, tk.END)
        self.issues_text.insert(tk.END, f"Analysis Results for: {file_path}\n")
        self.issues_text.insert(tk.END, "=" * 50 + "\n\n")
      
        if not issues:
            self.issues_text.insert(tk.END, "✓ No issues found!\n")
        else:
            self.issues_text.insert(tk.END, f"Found {len(issues)} issues:\n\n")
            for i, issue in enumerate(issues, 1):
                self.issues_text.insert(tk.END, f"{i}. {issue['description']}\n")
                self.issues_text.insert(tk.END, f"   Type: {issue['type']}\n")
                self.issues_text.insert(tk.END, f"   Severity: {issue.get('severity', 'unknown')}\n")
                if issue.get('line'):
                    self.issues_text.insert(tk.END, f"   Line: {issue['line']}\n")
                self.issues_text.insert(tk.END, "\n")
      
        # Update statistics
        self.update_statistics(issues, file_path)
  
    def display_correction_results(self, result):
        """Display correction results"""
        self.issues_text.delete(1.0, tk.END)
      
        if result['success']:
            if result.get('changes_made'):
                self.issues_text.insert(tk.END, f"✓ SUCCESS: Corrected {result['file']}\n")
                self.issues_text.insert(tk.END, f"✓ Backup created: {result['backup_created']}\n")
                self.issues_text.insert(tk.END, f"✓ Issues fixed: {result['issues_found']}\n")
                self.issues_text.insert(tk.END, f"✓ Fixable issues: {result['fixable_issues']}\n")
            else:
                self.issues_text.insert(tk.END, f"✓ No changes needed for: {result['file']}\n")
                self.issues_text.insert(tk.END, f"✓ Issues found: {result['issues_found']}\n")
                self.issues_text.insert(tk.END, f"✓ Fixable issues: {result['fixable_issues']}\n")
        else:
            self.issues_text.insert(tk.END, f"✗ FAILED: {result['file']}\n")
            self.issues_text.insert(tk.END, f"Error: {result.get('error', 'Unknown error')}\n")
  
    def display_directory_analysis(self, file_results, total_issues, directory):
        """Display directory analysis results"""
        self.issues_text.delete(1.0, tk.END)
        self.issues_text.insert(tk.END, f"Directory Analysis: {directory}\n")
        self.issues_text.insert(tk.END, "=" * 50 + "\n\n")
        self.issues_text.insert(tk.END, f"Files analyzed: {len(file_results)}\n")
        self.issues_text.insert(tk.END, f"Total issues found: {total_issues}\n\n")
      
        self.issues_text.insert(tk.END, "File Results:\n")
        for result in file_results:
            self.issues_text.insert(tk.END, f"  {result['file']}: {result['issues']} issues\n")
  
    def display_directory_correction(self, result):
        """Display directory correction results"""
        self.issues_text.delete(1.0, tk.END)
        self.issues_text.insert(tk.END, f"Directory Correction: {result['directory']}\n")
        self.issues_text.insert(tk.END, "=" * 50 + "\n\n")
        self.issues_text.insert(tk.END, f"Files processed: {result['files_processed']}\n")
        self.issues_text.insert(tk.END, f"Files corrected: {result['files_corrected']}\n")
        self.issues_text.insert(tk.END, f"Files failed: {result['files_failed']}\n")
        self.issues_text.insert(tk.END, f"Total issues: {result['total_issues']}\n")
        self.issues_text.insert(tk.END, f"Fixable issues: {result['total_fixable_issues']}\n")
  
    def update_statistics(self, issues, file_path):
        """Update statistics tab"""
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, f"Statistics for: {file_path}\n")
        self.stats_text.insert(tk.END, "=" * 50 + "\n\n")
      
        if not issues:
            self.stats_text.insert(tk.END, "No issues to analyze.\n")
            return
      
        # Categorize issues
        by_severity = {}
        by_type = {}
      
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            issue_type = issue.get('type', 'unknown')
          
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[issue_type] = by_type.get(issue_type, 0) + 1
      
        self.stats_text.insert(tk.END, "Issues by Severity:\n")
        for severity, count in by_severity.items():
            self.stats_text.insert(tk.END, f"  {severity}: {count}\n")
      
        self.stats_text.insert(tk.END, "\nIssues by Type:\n")
        for issue_type, count in by_type.items():
            self.stats_text.insert(tk.END, f"  {issue_type}: {count}\n")
      
        fixable_count = len([i for i in issues if i.get('fixable', False)])
        self.stats_text.insert(tk.END, f"\nFixable issues: {fixable_count}/{len(issues)}\n")
  
    def update_learning_insights(self):
        """Update learning insights tab"""
        if not self.engine or not self.engine.available_systems.get('learning_system'):
            self.learning_text.delete(1.0, tk.END)
            self.learning_text.insert(tk.END, "Learning system not available.\n")
            return
      
        insights = self.engine.available_systems['learning_system'].get_learning_insights()
        self.learning_text.delete(1.0, tk.END)
      
        if insights:
            self.learning_text.insert(tk.END, "Learning Insights\n")
            self.learning_text.insert(tk.END, "=" * 50 + "\n\n")
            self.learning_text.insert(tk.END, f"Total corrections: {insights.get('total_corrections', 0)}\n")
            self.learning_text.insert(tk.END, f"Success rate: {insights.get('success_rate', 0):.1%}\n")
            self.learning_text.insert(tk.END, f"Data points: {insights.get('data_size', 0)}\n")
          
            if 'most_common_issues' in insights:
                self.learning_text.insert(tk.END, "\nMost Common Issues:\n")
                for issue, count in insights['most_common_issues']:
                    self.learning_text.insert(tk.END, f"  {issue}: {count}\n")
        else:
            self.learning_text.insert(tk.END, "No learning data yet. Run some corrections to build insights.\n")
  
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
  
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function to run the GUI"""
    app = PyAutoFixGUI()
    app.run()

if __name__ == "__main__":
    main()
