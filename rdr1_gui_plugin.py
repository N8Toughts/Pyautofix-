"""
RDR1 PC GUI Plugin
Specialized GUI components for RDR1 PC formats
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger("RAGEAnalyzer.RDR1GUIPlugin")

def register_plugin():
    """Register this plugin with the RAGE Analyzer"""
    return {
        'name': 'RDR1 PC GUI',
        'version': '1.0.0',
        'author': 'RAGE Brainiac',
        'description': 'GUI components for RDR1 PC file formats',
        'games': ['RDR1'],
        'formats': ['wtd', 'wvd', 'wdd', 'wft', 'wtb']
    }

class RDR1TextureViewer:
    """Texture viewer for RDR1 WTD files"""
   
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.textures = []
        self.current_texture = 0
        self.create_widgets()
   
    def create_widgets(self):
        """Create texture viewer widgets"""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Texture list
        list_frame = ttk.LabelFrame(main_frame, text="Textures")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
       
        self.texture_listbox = tk.Listbox(list_frame, width=25, height=15)
        self.texture_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.texture_listbox.bind('<<ListboxSelect>>', self.on_texture_select)
       
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        self.canvas = tk.Canvas(preview_frame, width=400, height=400, bg='#2b2b2b')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Info frame
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
       
        self.info_label = ttk.Label(info_frame, text="No texture selected")
        self.info_label.pack(anchor=tk.W)
       
        # Control frame
        control_frame = ttk.Frame(preview_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
       
        ttk.Button(control_frame, text="Export DDS", command=self.export_texture).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Export All", command=self.export_all_textures).pack(side=tk.LEFT, padx=2)
   
    def load_wtd_file(self, wtd_path: str):
        """Load WTD file and populate texture list"""
        try:
            # Import here to avoid circular imports
            from rage_plugins.rdr1_pc_corrected_plugin import get_texture_info
           
            texture_info = get_texture_info(wtd_path)
            if not texture_info:
                messagebox.showerror("Error", "Failed to parse WTD file")
                return
           
            self.textures = texture_info.get('textures', [])
            self.texture_listbox.delete(0, tk.END)
           
            for texture in self.textures:
                self.texture_listbox.insert(tk.END, f"{texture['name']} ({texture['width']}x{texture['height']})")
           
            if self.textures:
                self.texture_listbox.selection_set(0)
                self.display_texture(0)
               
        except Exception as e:
            logger.error(f"Failed to load WTD file: {e}")
            messagebox.showerror("Error", f"Failed to load WTD file: {e}")
   
    def on_texture_select(self, event):
        """Handle texture selection"""
        selection = self.texture_listbox.curselection()
        if selection:
            self.current_texture = selection[0]
            self.display_texture(self.current_texture)
   
    def display_texture(self, texture_index: int):
        """Display texture information"""
        if texture_index < len(self.textures):
            texture = self.textures[texture_index]
           
            # Update info label
            info_text = (f"Name: {texture['name']}\n"
                        f"Size: {texture['width']} x {texture['height']}\n"
                        f"Format: {texture['format_name']}\n"
                        f"Mip Levels: {texture['mip_levels']}")
            self.info_label.config(text=info_text)
           
            # Draw placeholder preview
            self.canvas.delete("all")
            self.canvas.create_rectangle(50, 50, 350, 350, fill="#444444", outline="#666666")
            self.canvas.create_text(200, 200, text=f"Texture Preview\n{texture['name']}\n{texture['width']}x{texture['height']}",
                                  fill="white", font=("Arial", 12), justify=tk.CENTER)
   
    def export_texture(self):
        """Export selected texture as DDS"""
        if not self.textures or self.current_texture >= len(self.textures):
            return
       
        texture = self.textures[self.current_texture]
        output_path = filedialog.asksaveasfilename(
            defaultextension=".dds",
            filetypes=[("DDS files", "*.dds"), ("All files", "*.*")],
            initialfile=f"{texture['name']}.dds"
        )
       
        if output_path:
            try:
                from rage_plugins.rdr1_pc_corrected_plugin import extract_texture
               
                if extract_texture(self.current_wtd_path, self.current_texture, output_path):
                    messagebox.showinfo("Success", f"Texture exported to {output_path}")
                else:
                    messagebox.showerror("Error", "Failed to export texture")
                   
            except Exception as e:
                logger.error(f"Export failed: {e}")
                messagebox.showerror("Error", f"Export failed: {e}")
   
    def export_all_textures(self):
        """Export all textures from WTD file"""
        if not self.textures:
            return
       
        output_dir = filedialog.askdirectory(title="Select output directory")
        if output_dir:
            try:
                from rage_plugins.rdr1_pc_corrected_plugin import extract_texture
               
                success_count = 0
                for i, texture in enumerate(self.textures):
                    output_path = Path(output_dir) / f"{texture['name']}.dds"
                    if extract_texture(self.current_wtd_path, i, str(output_path)):
                        success_count += 1
               
                messagebox.showinfo("Success", f"Exported {success_count}/{len(self.textures)} textures")
               
            except Exception as e:
                logger.error(f"Batch export failed: {e}")
                messagebox.showerror("Error", f"Batch export failed: {e}")

class RDR1ModelViewer:
    """Model viewer for RDR1 WVD files"""
   
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.model_info = {}
        self.create_widgets()
   
    def create_widgets(self):
        """Create model viewer widgets"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Model info frame
        info_frame = ttk.LabelFrame(main_frame, text="Model Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
       
        self.info_text = tk.Text(info_frame, height=8, width=60)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.config(state=tk.DISABLED)
       
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="3D Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        self.canvas = tk.Canvas(preview_frame, width=400, height=300, bg='#1a1a1a')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
       
        ttk.Button(control_frame, text="Export OBJ", command=self.export_model).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Generate Preview", command=self.generate_preview).pack(side=tk.LEFT, padx=2)
   
    def load_wvd_file(self, wvd_path: str):
        """Load WVD file and display model information"""
        try:
            from rage_plugins.rdr1_pc_corrected_plugin import get_model_preview
           
            self.model_info = get_model_preview(wvd_path)
            self.current_wvd_path = wvd_path
           
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
           
            if self.model_info:
                info_str = (f"Format: {self.model_info['format']}\n"
                           f"Vertices: {self.model_info['vertex_count']:,}\n"
                           f"Faces: {self.model_info['face_count']:,}\n"
                           f"File Size: {self.model_info['file_size']:,} bytes\n"
                           f"Bounding Box: {self.model_info['bounding_box']}")
                self.info_text.insert(tk.END, info_str)
            else:
                self.info_text.insert(tk.END, "Failed to parse WVD file")
           
            self.info_text.config(state=tk.DISABLED)
            self.generate_preview()
           
        except Exception as e:
            logger.error(f"Failed to load WVD file: {e}")
            messagebox.showerror("Error", f"Failed to load WVD file: {e}")
   
    def generate_preview(self):
        """Generate 3D preview of model"""
        self.canvas.delete("all")
       
        if not self.model_info:
            self.canvas.create_text(200, 150, text="No model loaded", fill="white", font=("Arial", 14))
            return
       
        # Draw bounding box representation
        bbox = self.model_info.get('bounding_box', {})
        min_pos = bbox.get('min', (-1, -1, -1))
        max_pos = bbox.get('max', (1, 1, 1))
        center = bbox.get('center', (0, 0, 0))
       
        # Convert 3D to 2D for simple preview
        scale = 80
        offset_x, offset_y = 200, 150
       
        # Draw bounding box
        x1 = offset_x + min_pos[0] * scale
        y1 = offset_y + min_pos[1] * scale
        x2 = offset_x + max_pos[0] * scale
        y2 = offset_y + max_pos[1] * scale
       
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00ff00", width=2)
       
        # Draw center point
        cx = offset_x + center[0] * scale
        cy = offset_y + center[1] * scale
        self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#ff0000")
       
        # Draw info
        self.canvas.create_text(200, 280,
                               text=f"Vertices: {self.model_info['vertex_count']:,} | Faces: {self.model_info['face_count']:,}",
                               fill="white", font=("Arial", 10))
   
    def export_model(self):
        """Export model to OBJ format"""
        if not hasattr(self, 'current_wvd_path'):
            return
       
        output_path = filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")],
            initialfile=Path(self.current_wvd_path).stem + ".obj"
        )
       
        if output_path:
            try:
                from rage_plugins.rdr1_porrected_plugin import convert_model
               
                if convert_model(self.current_wvd_path, output_path, 'obj'):
                    messagebox.showinfo("Success", f"Model exported to {output_path}")
                else:
                    messagebox.showerror("Error", "Failed to export model")
                   
            except Exception as e:
                logger.error(f"Export failed: {e}")
                messagebox.showerror("Error", f"Export failed: {e}")

def create_texture_viewer(parent_frame) -> RDR1TextureViewer:
    """Create RDR1 texture viewer instance"""
    return RDR1TextureViewer(parent_frame)

def create_model_viewer(parent_frame) -> RDR1ModelViewer:
    """Create RDR1 model viewer instance"""
    return RDR1ModelViewer(parent_frame)