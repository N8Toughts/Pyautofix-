"""
Discovery GUI Plugin
Shows multiple format candidates and allows user exploration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger("RAGEAnalyzer.DiscoveryGUI")

def register_plugin():
    return {
        'name': 'Discovery GUI',
        'version': '1.0.0',
        'author': 'RAGE Brainiac',
        'description': 'GUI for exploring multiple format candidates',
        'games': ['ALL'],
        'formats': ['discovery']
    }

class FormatDiscoveryViewer:
    """Shows multiple format candidates for user exploration"""
   
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.candidates = []
        self.current_file = None
        self.create_widgets()
   
    def create_widgets(self):
        """Create discovery viewer widgets"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
       
        ttk.Label(header_frame, text="Aggressive Format Discovery",
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
       
        ttk.Label(header_frame, text="Tries ALL known RAGE formats without blocking",
                 font=("Arial", 9)).pack(anchor=tk.W)
       
        # Candidates list
        candidate_frame = ttk.LabelFrame(main_frame, text="Format Candidates")
        candidate_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Treeview for candidates
        columns = ('confidence', 'method', 'games', 'evidence')
        self.candidate_tree = ttk.Treeview(candidate_frame, columns=columns, show='headings')
       
        self.candidate_tree.heading('confidence', text='Confidence')
        self.candidate_tree.heading('method', text='Method')
        self.candidate_tree.heading('games', text='Games')
        self.candidate_tree.heading('evidence', text='Evidence')
       
        self.candidate_tree.column('confidence', width=80)
        self.candidate_tree.column('method', width=100)
        self.candidate_tree.column('games', width=120)
        self.candidate_tree.column('evidence', width=200)
       
        # Scrollbar
        scrollbar = ttk.Scrollbar(candidate_frame, orient=tk.VERTICAL, command=self.candidate_tree.yview)
        self.candidate_tree.configure(yscrollcommand=scrollbar.set)
       
        self.candidate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       
        # Bind selection
        self.candidate_tree.bind('<<TreeviewSelect>>', self.on_candidate_select)
       
        # Details frame
        self.details_frame = ttk.LabelFrame(main_frame, text="Candidate Details")
        self.details_frame.pack(fill=tk.X, padx=5, pady=5)
       
        self.details_text = tk.Text(self.details_frame, height=6, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.config(state=tk.DISABLED)
       
        # Action frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
       
        ttk.Button(action_frame, text="Try Best Candidate",
                  command=self.try_best_candidate).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Try Selected Candidate",
                  command=self.try_selected_candidate).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Export Discovery Report",
                  command=self.export_report).pack(side=tk.RIGHT, padx=2)
   
    def analyze_file(self, file_path: str):
        """Analyze file and show discovery results"""
        self.current_file = file_path
        self.candidate_tree.delete(*self.candidate_tree.get_children())
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)
       
        try:
            from rage_plugins.aggressive_discovery_plugin import aggressively_analyze_file
            self.candidates = aggressively_analyze_file(file_path)
           
            for i, candidate in enumerate(self.candidates):
                confidence_pct = f"{candidate.confidence*100:.1f}%"
                games_str = ", ".join(candidate.games)
                evidence_preview = candidate.evidence[0][:50] + "..." if candidate.evidence else "No evidence"
               
                tags = ('high_confidence',) if candidate.confidence > 0.7 else ('medium_confidence',) if candidate.confidence > 0.4 else ('low_confidence',)
               
                self.candidate_tree.insert('', tk.END, values=(
                    confidence_pct,
                    candidate.method.value,
                    games_str,
                    evidence_preview
                ), tags=tags)
           
            # Configure tags for color coding
            self.candidate_tree.tag_configure('high_confidence', background='#d4edda')
            self.candidate_tree.tag_configure('medium_confidence', background='#fff3cd')
            self.candidate_tree.tag_configure('low_confidence', background='#f8d7da')
           
            if self.candidates:
                self.candidate_tree.selection_set(self.candidate_tree.get_children()[0])
                self.on_candidate_select(None)
               
        except Exception as e:
            logger.error(f"Discovery analysis failed: {e}")
            messagebox.showerror("Error", f"Discovery analysis failed: {e}")
   
    def on_candidate_select(self, event):
        """Show details for selected candidate"""
        selection = self.candidate_tree.selection()
        if not selection or not self.candidates:
            return
       
        index = self.candidate_tree.index(selection[0])
        if index < len(self.candidates):
            candidate = self.candidates[index]
           
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
           
            details = (f"Format: {candidate.format_name}\n"
                      f"Confidence: {candidate.confidence*100:.1f}%\n"
                      f"Detection Method: {candidate.method.value}\n"
                      f"Games: {', '.join(candidate.games)}\n"
                      f"Structure Type: {candidate.structure_type}\n"
                      f"Can Process: {candidate.can_process}\n\n"
                      f"Evidence:\n")
           
            for evidence in candidate.evidence:
                details += f"• {evidence}\n"
           
            self.details_text.insert(tk.END, details)
            self.details_text.config(state=tk.DISABLED)
   
    def try_best_candidate(self):
        """Try to process file using the best candidate"""
        if not self.candidates or not self.current_file:
            return
       
        best_candidate = self.candidates[0]
        self._try_process_candidate(best_candidate)
   
    def try_selected_candidate(self):
        """Try to process file using the selected candidate"""
        selection = self.candidate_tree.selection()
        if not selection or not self.candidates:
            return
       
        index = self.candidate_tree.index(selection[0])
        if index < len(self.candidates):
            candidate = self.candidates[index]
            self._try_process_candidate(candidate)
   
    def _try_process_candidate(self, candidate: Any):
        """Try to process file using the given candidate"""
        if not candidate.can_process:
            messagebox.showinfo("Cannot Process",
                              f"Candidate '{candidate.format_name}' cannot be processed automatically.\n"
                              f"Confidence too low: {candidate.confidence*100:.1f}%")
            return
       
        try:
            # Try to find appropriate processor
            processor = self._find_processor_for_candidate(candidate)
            if processor:
                messagebox.showinfo("Processor Found",
                                  f"Found processor for: {candidate.format_name}\n"
                                  f"Would attempt to process: {self.current_file}")
            else:
                messagebox.showinfo("No Processor",
                                  f"No processor available for: {candidate.format_name}\n"
                                  f"This may be a newly discovered format.")
               
        except Exception as e:
            logger.error(f"Processor search failed: {e}")
            messagebox.showerror("Error", f"Processor search failed: {e}")
   
    def _find_processor_for_candidate(self, candidate: Any):
        """Find appropriate processor for candidate format"""
        # This would interface with the plugin system to find processors
        # Placeholder implementation
        return None
   
    def export_report(self):
        """Export discovery report to file"""
        if not self.candidates or not self.current_file:
            return
       
        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{Path(self.current_file).stem}_discovery_report.txt"
        )
       
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"RAGE Format Discovery Report\n")
                    f.write(f"File: {self.current_file}\n")
                    f.write(f"Size: {os.path.getsize(self.current_file)} bytes\n")
                    f.write(f"Candidates Found: {len(self.candidates)}\n")
                    f.write("="*50 + "\n\n")
                   
                    for i, candidate in enumerate(self.candidates):
                        f.write(f"Candidate #{i+1}:\n")
                        f.write(f"  Format: {candidate.format_name}\n")
                        f.write(f"  Confidence: {candidate.confidence*100:.1f}%\n")
                        f.write(f"  Method: {candidate.method.value}\n")
                        f.write(f"  Games: {', '.join(candidate.games)}\n")
                        f.write(f"  Structure: {candidate.structure_type}\n")
                        f.write(f"  Can Process: {candidate.can_process}\n")
                        f.write(f"  Evidence:\n")
                        for evidence in candidate.evidence:
                            f.write(f"    • {evidence}\n")
                        f.write("\n")
               
                messagebox.showinfo("Success", f"Discovery report exported to {output_path}")
               
            except Exception as e:
                logger.error(f"Export failed: {e}")
                messagebox.showerror("Error", f"Export failed: {e}")

def create_discovery_viewer(parent_frame) -> FormatDiscoveryViewer:
    """Create format discovery viewer instance"""
    return FormatDiscoveryViewer(parent_frame)