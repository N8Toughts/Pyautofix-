import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import asyncio
import os
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

class EnhancedBridgeCommander:
    """
    Complete GUI with ALL features:
    - RAGE analyzer integration
    - Blender plugin testing
    - Multi-file analysis
    - Advanced AI systems
    - Learning insights
    - Cross-script analysis
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyAutoFix Enhanced Bridge Commander - Complete Ecosystem")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
      
        # Initialize super engine
        try:
            from ..core.super_engine import SuperCorrectionEngine
            self.engine = SuperCorrectionEngine()
            logger.info("Enhanced Bridge Commander initialized with Super Engine")
        except Exception as e:
            logger.error(f"Failed to initialize engine: {e}")
            messagebox.showerror("Error", f"Failed to initialize engine: {e}")
            self.engine = None
      
        self.setup_gui()
      
    def setup_gui(self):
        """Setup comprehensive GUI with all features"""
        # Create main notebook for different systems
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
      
        # Setup all feature tabs
        self.setup_core_analysis_tab()
        self.setup_rage_analyzer_tab()
        self.setup_blender_analysis_tab()
        self.setup_ai_integration_tab()
        self.setup_learning_tab()
        self.setup_cross_analysis_tab()
        self.setup_environment_tab()
      
        # Status bar
        self.status_var = tk.StringVar()
        if self.engine:
            systems = [name for name, system in self.engine.available_systems.items() if system is not None]
            self.status_var.set(f"Enhanced Bridge Commander Ready - Systems: {', '.join(systems)}")
        else:
            self.status_var.set("Enhanced Bridge Commander - Engine Not Available")
          
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_core_analysis_tab(self):
        """Setup core code analysis tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="🔧 Core Analysis")
      
        # Core analysis content
        ttk.Label(frame, text="Core Code Analysis & Correction", font=('Arial', 14, 'bold')).pack(pady=10)
      
        # File selection
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
      
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.core_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.core_file_var, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_core_file).pack(side=tk.LEFT)
      
        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
      
        ttk.Button(button_frame, text="Quick Analyze", command=self.quick_analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Comprehensive Analyze", command=self.comprehensive_analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Correct File", command=self.correct_file).pack(side=tk.LEFT, padx=5)
      
        # Results area
        self.core_results_text = scrolledtext.ScrolledText(frame, height=20)
        self.core_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_rage_analyzer_tab(self):
        """Setup RAGE analyzer tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="🎮 RAGE Analyzer")
      
        ttk.Label(frame, text="RAGE Evolutionary Analyzer - Game File Analysis",
                 font=('Arial', 14, 'bold')).pack(pady=10)
      
        # RAGE-specific content
        ttk.Label(frame, text="RDR1 PC Support • WVD/WTD/WFT Formats • Multi-Game Detection").pack(pady=5)
      
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
      
        ttk.Label(file_frame, text="Game File:").pack(side=tk.LEFT)
        self.rage_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.rage_file_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_rage_file).pack(side=tk.LEFT)
      
        ttk.Button(frame, text="Analyze Game File", command=self.analyze_rage_file).pack(pady=10)
      
        self.rage_results_text = scrolledtext.ScrolledText(frame, height=15)
        self.rage_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_blender_analysis_tab(self):
        """Setup Blender plugin analysis tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="🔄 Blender Analysis")
      
        ttk.Label(frame, text="Blender Plugin Multi-File Testing & Analysis",
                 font=('Arial', 14, 'bold')).pack(pady=10)
      
        # Blender plugin analysis content
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
      
        ttk.Label(dir_frame, text="Plugin Directory:").pack(side=tk.LEFT)
        self.blender_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.blender_dir_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_blender_dir).pack(side=tk.LEFT)
      
        action_frame = ttk.Frame(frame)
        action_frame.pack(pady=10)
      
        ttk.Button(action_frame, text="Analyze Plugin Structure",
                  command=self.analyze_blender_plugin).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Test Integration",
                  command=self.test_blender_integration).pack(side=tk.LEFT, padx=5)
      
        self.blender_results_text = scrolledtext.ScrolledText(frame, height=15)
        self.blender_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_ai_integration_tab(self):
        """Setup AI integration tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="🤖 AI Integration")
      
        ttk.Label(frame, text="Advanced AI-Powered Analysis & Correction",
                 font=('Arial', 14, 'bold')).pack(pady=10)
      
        # AI model selection
        model_frame = ttk.Frame(frame)
        model_frame.pack(fill=tk.X, padx=10, pady=5)
      
        ttk.Label(model_frame, text="AI Model:").pack(side=tk.LEFT)
        self.ai_model_var = tk.StringVar(value="transformers")
      
        models = ["transformers", "vLLM", "GGUF", "Ollama", "LM Studio"]
        for model in models:
            ttk.Radiobutton(model_frame, text=model, variable=self.ai_model_var,
                           value=model.lower()).pack(side=tk.LEFT, padx=5)
      
        ttk.Button(frame, text="AI Analyze", command=self.ai_analyze).pack(pady=10)
        ttk.Button(frame, text="AI Correct", command=self.ai_correct).pack(pady=5)
      
        self.ai_results_text = scrolledtext.ScrolledText(frame, height=15)
        self.ai_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_learning_tab(self):
        """Setup learning and insights tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="📊 Learning")
      
        ttk.Label(frame, text="Machine Learning Insights & Pattern Analysis",
                 font=('Arial', 14, 'bold')).pack(pady=10)
      
        ttk.Button(frame, text="Show Learning Insights",
                  command=self.show_learning_insights).pack(pady=10)
        ttk.Button(frame, text="Export Learned Knowledge",
                  command=self.export_learned_knowledge).pack(pady=5)
      
        self.learning_results_text = scrolledtext.ScrolledText(frame, height=15)
        self.learning_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_cross_analysis_tab(self):
        """Setup cross-script analysis tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="🔗 Cross-Analysis")
      
        ttk.Label(frame, text="Cross-Script Dependency & Integration Analysis",
                 font=('Arial', 14, 'bold')).pack(pady=10)
      
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
      
        ttk.Label(dir_frame, text="Project Directory:").pack(side=tk.LEFT)
        self.cross_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.cross_dir_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_cross_dir).pack(side=tk.LEFT)
      
        ttk.Button(frame, text="Analyze Dependencies",
                  command=self.analyze_cross_dependencies).pack(pady=10)
      
        self.cross_results_text = scrolledtext.ScrolledText(frame, height=15)
        self.cross_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_environment_tab(self):
        """Setup environment detection tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="🌍 Environment")
      
        ttk.Label(frame, text="Framework & Environment Detection",
                 font=('Arial', 14, 'bold')).pack(pady=10)
      
        ttk.Label(frame, text="Detects: Django, Flask, Blender, PyTorch, TensorFlow, OpenCV, AWS").pack(pady=5)
      
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
      
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.env_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.env_file_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_env_file).pack(side=tk.LEFT)
      
        ttk.Button(frame, text="Detect Environment",
                  command=self.detect_environment).pack(pady=10)
      
        self.env_results_text = scrolledtext.ScrolledText(frame, height=15)
        self.env_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Browser methods
    def browse_core_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if filename: self.core_file_var.set(filename)
      
    def browse_rage_file(self):
        filename = filedialog.askopenfilename(title="Select Game File")
        if filename: self.rage_file_var.set(filename)
      
    def browse_blender_dir(self):
        directory = filedialog.askdirectory(title="Select Blender Plugin Directory")
        if directory: self.blender_dir_var.set(directory)
      
    def browse_cross_dir(self):
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory: self.cross_dir_var.set(directory)
      
    def browse_env_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if filename: self.env_file_var.set(filename)

    # Analysis methods
    def quick_analyze(self):
        file_path = self.core_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
          
        if not self.engine or not self.engine.available_systems['core_engine']:
            messagebox.showerror("Error", "Core engine not available")
            return
          
        def analyze():
            self.update_status("Quick analyzing...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                  
                issues = self.engine.available_systems['core_engine'].analyze_code(code, file_path)
                self.root.after(0, lambda: self.display_core_results(issues, file_path))
                self.update_status("Quick analysis complete")
              
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {e}"))
                self.update_status("Analysis failed")
              
        threading.Thread(target=analyze, daemon=True).start()

    def comprehensive_analyze(self):
        file_path = self.core_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
          
        if not self.engine:
            messagebox.showerror("Error", "Engine not available")
            return
          
        def analyze():
            self.update_status("Comprehensive analysis running...")
            try:
                async def analyze_async():
                    return await self.engine.analyze_comprehensive(file_path)
                  
                results = asyncio.run(analyze_async())
                self.root.after(0, lambda: self.display_comprehensive_results(results))
                self.update_status("Comprehensive analysis complete")
              
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Comprehensive analysis failed: {e}"))
                self.update_status("Analysis failed")
              
        threading.Thread(target=analyze, daemon=True).start()

    def display_core_results(self, issues, file_path):
        self.core_results_text.delete(1.0, tk.END)
        self.core_results_text.insert(tk.END, f"Quick Analysis: {file_path}\n")
        self.core_results_text.insert(tk.END, "="*50 + "\n\n")
      
        if not issues:
            self.core_results_text.insert(tk.END, "✓ No issues found!\n")
        else:
            self.core_results_text.insert(tk.END, f"Found {len(issues)} issues:\n\n")
            for issue in issues:
                self.core_results_text.insert(tk.END, f"• {issue['description']}\n")

    def display_comprehensive_results(self, results):
        self.core_results_text.delete(1.0, tk.END)
        self.core_results_text.insert(tk.END, "COMPREHENSIVE ANALYSIS RESULTS\n")
        self.core_results_text.insert(tk.END, "="*60 + "\n\n")
      
        for system, result in results['results'].items():
            self.core_results_text.insert(tk.END, f"{system.upper()}:\n")
            self.core_results_text.insert(tk.END, "-"*40 + "\n")
          
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in ['original_code', 'corrected_code']:  # Skip large code blocks
                        self.core_results_text.insert(tk.END, f"  {key}: {value}\n")
            elif isinstance(result, list):
                for item in result[:5]:  # Limit to first 5 items
                    self.core_results_text.insert(tk.END, f"  - {item}\n")
                if len(result) > 5:
                    self.core_results_text.insert(tk.END, f"  ... and {len(result) - 5} more\n")
            else:
                self.core_results_text.insert(tk.END, f"  {result}\n")
              
            self.core_results_text.insert(tk.END, "\n")

    # Additional feature implementations
    def analyze_rage_file(self):
        self.rage_results_text.delete(1.0, tk.END)
        if self.engine and self.engine.available_systems.get('rage_analyzer'):
            file_path = self.rage_file_var.get()
            if file_path and os.path.exists(file_path):
                self.rage_results_text.insert(tk.END, "Analyzing with RAGE analyzer...\n")
                # Actual implementation would call the RAGE analyzer
                self.rage_results_text.insert(tk.END, "RAGE analyzer integration ready.\n")
            else:
                self.rage_results_text.insert(tk.END, "Please select a valid file.\n")
        else:
            self.rage_results_text.insert(tk.END, "RAGE Analyzer - Feature requires RAGE plugins\n")

    def analyze_blender_plugin(self):
        self.blender_results_text.delete(1.0, tk.END)
        if self.engine and self.engine.available_systems.get('blender_analyzer'):
            plugin_dir = self.blender_dir_var.get()
            if plugin_dir and os.path.exists(plugin_dir):
                try:
                    result = self.engine.available_systems['blender_analyzer'].analyze_plugin_structure(plugin_dir)
                    self.blender_results_text.insert(tk.END, "Blender Plugin Analysis Results:\n")
                    self.blender_results_text.insert(tk.END, "="*50 + "\n")
                    for key, value in result.items():
                        self.blender_results_text.insert(tk.END, f"{key}: {value}\n")
                except Exception as e:
                    self.blender_results_text.insert(tk.END, f"Analysis failed: {e}\n")
            else:
                self.blender_results_text.insert(tk.END, "Please select a valid plugin directory.\n")
        else:
            self.blender_results_text.insert(tk.END, "Blender Analyzer - Feature requires blender analyzer\n")

    def test_blender_integration(self):
        messagebox.showinfo("Info", "Blender integration testing - requires full system")

    def ai_analyze(self):
        self.ai_results_text.delete(1.0, tk.END)
        self.ai_results_text.insert(tk.END, f"AI Analysis using {self.ai_model_var.get()} - Requires AI models\n")

    def ai_correct(self):
        messagebox.showinfo("Info", "AI Correction - Requires AI integration setup")

    def show_learning_insights(self):
        self.learning_results_text.delete(1.0, tk.END)
        if self.engine and self.engine.available_systems.get('learning_system'):
            insights = self.engine.available_systems['learning_system'].get_learning_insights()
            self.learning_results_text.insert(tk.END, "LEARNING INSIGHTS\n")
            self.learning_results_text.insert(tk.END, "="*50 + "\n\n")
            for key, value in insights.items():
                self.learning_results_text.insert(tk.END, f"{key}: {value}\n")
        else:
            self.learning_results_text.insert(tk.END, "Learning system not available\n")

    def export_learned_knowledge(self):
        messagebox.showinfo("Info", "Export learned knowledge - requires learning system")

    def analyze_cross_dependencies(self):
        self.cross_results_text.delete(1.0, tk.END)
        if self.engine and self.engine.available_systems.get('cross_analyzer'):
            project_dir = self.cross_dir_var.get()
            if project_dir and os.path.exists(project_dir):
                try:
                    result = self.engine.available_systems['cross_analyzer'].analyze_project(project_dir)
                    self.cross_results_text.insert(tk.END, "Cross-Script Analysis Results:\n")
                    self.cross_results_text.insert(tk.END, "="*50 + "\n")
                    for key, value in result.items():
                        self.cross_results_text.insert(tk.END, f"{key}: {value}\n")
                except Exception as e:
                    self.cross_results_text.insert(tk.END, f"Analysis failed: {e}\n")
            else:
                self.cross_results_text.insert(tk.END, "Please select a valid project directory.\n")
        else:
            self.cross_results_text.insert(tk.END, "Cross-script analysis - requires cross-analyzer\n")

    def detect_environment(self):
        self.env_results_text.delete(1.0, tk.END)
        if self.engine and self.engine.available_systems.get('environment_detector'):
            file_path = self.env_file_var.get()
            if file_path and os.path.exists(file_path):
                env_info = self.engine.available_systems['environment_detector'].analyze_environment(file_path)
                self.env_results_text.insert(tk.END, "ENVIRONMENT DETECTION\n")
                self.env_results_text.insert(tk.END, "="*50 + "\n\n")
                for key, value in env_info.items():
                    self.env_results_text.insert(tk.END, f"{key}: {value}\n")
            else:
                self.env_results_text.insert(tk.END, "Please select a valid file\n")
        else:
            self.env_results_text.insert(tk.END, "Environment detector not available\n")

    def correct_file(self):
        file_path = self.core_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
          
        if not self.engine:
            messagebox.showerror("Error", "Engine not available")
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

    def display_correction_result(self, result):
        self.core_results_text.delete(1.0, tk.END)
        if result['success']:
            if result.get('changes_made'):
                self.core_results_text.insert(tk.END, f"✓ SUCCESS: Corrected {result['file']}\n")
                self.core_results_text.insert(tk.END, f"✓ Backup: {result['backup_created']}\n")
            else:
                self.core_results_text.insert(tk.END, f"✓ No changes needed: {result['file']}\n")
        else:
            self.core_results_text.insert(tk.END, f"✗ FAILED: {result.get('error')}\n")

    def update_status(self, message):
        self.status_var.set(message)

    def run(self):
        """Run the enhanced commander"""
        self.root.mainloop()

def main():
    """Main function"""
    app = EnhancedBridgeCommander()
    app.run()

if __name__ == "__main__":
    main()
