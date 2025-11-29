import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import asyncio
import sys
import os
from pathlib import Path
import logging

# Add the parent directory to path so we can import pyautofix modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pyautofix.core.enhanced_engine import LearningEnhancedEngine
    from pyautofix.learning.advanced_learning import AdvancedLearningSystem
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"Import error: {e}")

class PyAutoFixGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAutoFix Ultimate - AI-Powered Code Correction")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
      
        # Initialize engine
        self.engine = None
        self.setup_engine()
      
        # Setup GUI
        self.setup_gui()
      
        # Status
        self.is_processing = False
      
    def setup_engine(self):
        """Initialize the correction engine"""
        if not MODULES_AVAILABLE:
            messagebox.showerror(
                "Import Error",
                "Could not import PyAutoFix modules. Please ensure all dependencies are installed."
            )
            return
          
        try:
            config = {
                'learn_from_corrections': True,
                'auto_suggest_rules': True,
                'learning_confidence_threshold': 0.7
            }
            self.engine = LearningEnhancedEngine(config)
            self.log("Engine initialized successfully")
        except Exception as e:
            messagebox.showerror("Engine Error", f"Failed to initialize engine: {e}")
  
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
      
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
      
        # Title
        title_label = ttk.Label(
            main_frame,
            text="PyAutoFix Ultimate",
            font=("Arial", 16, "bold"),
            foreground="#2E86AB"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
      
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Target Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
       
        # File selection row
        file_row = ttk.Frame(file_frame)
        file_row.pack(fill=tk.X, pady=5)
       
        ttk.Label(file_row, text="File:").pack(side=tk.LEFT)
        self.file_var = tk.StringVar()
        ttk.Entry(file_row, textvariable=self.file_var, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_row, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
       
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
       
        ttk.Button(button_frame, text="Analyze", command=self.analyze_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Correct", command=self.correct_file).pack(side=tk.LEFT, padx=5)
       
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
       
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True)
       
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

    def browse_file(self):
        """Browse for a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.file_var.set(filename)

    def analyze_file(self):
        """Analyze selected file"""
        file_path = self.file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
           
        if not self.engine:
            messagebox.showerror("Error", "Engine not initialized")
            return
           
        def analyze():
            self.update_status("Analyzing file...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                   
                issues = self.engine.analyze_code(code, file_path)
                self.root.after(0, lambda: self.display_results(issues, file_path))
                self.update_status("Analysis complete")
               
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {e}"))
                self.update_status("Analysis failed")
               
        threading.Thread(target=analyze, daemon=True).start()

    def correct_file(self):
        """Correct selected file"""
        file_path = self.file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
           
        if not self.engine:
            messagebox.showerror("Error", "Engine not initialized")
            return
           
        def correct():
            self.update_status("Correcting file...")
            try:
                result = self.engine.correct_file(file_path)
                self.root.after(0, lambda: self.display_correction_result(result))
                self.update_status("Correction complete")
               
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Correction failed: {e}"))
                self.update_status("Correction failed")
               
        threading.Thread(target=correct, daemon=True).start()

    def display_results(self, issues, file_path):
        """Display analysis results"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Analysis Results: {file_path}\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
       
        if not issues:
            self.results_text.insert(tk.END, "✓ No issues found!\n")
        else:
            self.results_text.insert(tk.END, f"Found {len(issues)} issues:\n\n")
            for issue in issues:
                self.results_text.insert(tk.END, f"• {issue.get('description', 'Unknown issue')}\n")
                if issue.get('line'):
                    self.results_text.insert(tk.END, f"  Line: {issue['line']}\n")
                self.results_text.insert(tk.END, f"  Severity: {issue.get('severity', 'unknown')}\n\n")

    def display_correction_result(self, result):
        """Display correction results"""
        self.results_text.delete(1.0, tk.END)
       
        if result['success']:
            if result.get('changes_made'):
                self.results_text.insert(tk.END, f"✓ SUCCESS: Corrected {result['file']}\n")
                self.results_text.insert(tk.END, f"✓ Backup: {result.get('backup_created', 'Not created')}\n")
                self.results_text.insert(tk.END, f"✓ Issues found: {result['issues_found']}\n")
                self.results_text.insert(tk.END, f"✓ Fixable issues: {result['fixable_issues']}\n")
            else:
                self.results_text.insert(tk.END, f"✓ No changes needed: {result['file']}\n")
        else:
            self.results_text.insert(tk.END, f"✗ FAILED: {result.get('error', 'Unknown error')}\n")

    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)

    def log(self, message):
        """Log message to results"""
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)