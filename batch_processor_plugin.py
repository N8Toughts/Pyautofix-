"""
Batch Processing Plugin for RAGE Analyzer
Provides batch operations for RDR1 file processing
"""

import os
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("RAGEAnalyzer.BatchProcessor")

def register_plugin():
    """Register this plugin with the RAGE Analyzer"""
    return {
        'name': 'Batch Processor',
        'version': '1.0.0',
        'author': 'RAGE Brainiac',
        'description': 'Batch processing operations for RDR1 files',
        'games': ['RDR1', 'RDR2', 'GTA5'],
        'formats': ['all']
    }

def get_format_database():
    """Batch processor doesn't provide format database"""
    return {}

def get_magic_numbers():
    """Batch processor doesn't provide magic numbers"""
    return {}

def can_handle(format_type: str, game: str = None) -> bool:
    """Batch processor can handle any format for batch operations"""
    return True

class RDR1BatchProcessor:
    """Batch processor for RDR1 file operations"""
   
    def __init__(self):
        self.progress_callback = None
        self.cancel_flag = False
       
    def set_progress_callback(self, callback):
        """Set progress callback function"""
        self.progress_callback = callback
   
    def cancel_operation(self):
        """Cancel current batch operation"""
        self.cancel_flag = True
   
    def batch_extract_archives(self, archive_paths: List[str], output_base_dir: str) -> Dict[str, Any]:
        """Batch extract multiple RDR1 archives"""
        results = {
            'total': len(archive_paths),
            'success': 0,
            'failed': 0,
            'errors': []
        }
       
        def process_archive(archive_path):
            if self.cancel_flag:
                return None
               
            try:
                archive_name = Path(archive_path).stem
                output_dir = Path(output_base_dir) / archive_name
               
                # Import here to avoid circular imports
                from rage_plugins.rdr1_enhanced_plugin import extract_archive
               
                if extract_archive(archive_path, str(output_dir)):
                    return ('success', archive_path)
                else:
                    return ('failed', archive_path, "Extraction failed")
                   
            except Exception as e:
                return ('error', archive_path, str(e))
       
        # Process archives with thread pool
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_archive = {executor.submit(process_archive, path): path for path in archive_paths}
           
            for i, future in enumerate(as_completed(future_to_archive)):
                if self.cancel_flag:
                    break
                   
                result = future.result()
                if result:
                    status, archive_path, *extra = result
                   
                    if status == 'success':
                        results['success'] += 1
                    elif status == 'failed':
                        results['failed'] += 1
                        results['errors'].append(f"{archive_path}: {extra[0]}")
                    else:  # error
                        results['failed'] += 1
                        results['errors'].append(f"{archive_path}: {extra[0]}")
               
                # Update progress
                if self.progress_callback:
                    progress = (i + 1) / len(archive_paths) * 100
                    self.progress_callback(progress, f"Processed {i + 1}/{len(archive_paths)}")
       
        return results
   
    def batch_convert_textures(self, texture_paths: List[str], output_dir: str, format: str = 'dds') -> Dict[str, Any]:
        """Batch convert multiple RDR1 textures"""
        results = {
            'total': len(texture_paths),
            'success': 0,
            'failed': 0,
            'errors': []
        }
       
        def process_texture(texture_path):
            if self.cancel_flag:
                return None
               
            try:
                texture_name = Path(texture_path).stem
                output_path = Path(output_dir) / f"{texture_name}.{format}"
               
                # Import here to avoid circular imports
                from rage_plugins.rdr1_enhanced_plugin import convert_texture
               
                if convert_texture(texture_path, str(output_path), format):
                    return ('success', texture_path)
                else:
                    return ('failed', texture_path, "Conversion failed")
                   
            except Exception as e:
                return ('error', texture_path, str(e))
       
        # Process textures with thread pool
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_texture = {executor.submit(process_texture, path): path for path in texture_paths}
           
            for i, future in enumerate(as_completed(future_to_texture)):
                if self.cancel_flag:
                    break
                   
                result = future.result()
                if result:
                    status, texture_path, *extra = result
                   
                    if status == 'success':
                        results['success'] += 1
                    elif status == 'failed':
                        results['failed'] += 1
                        results['errors'].append(f"{texture_path}: {extra[0]}")
                    else:  # error
                        results['failed'] += 1
                        results['errors'].append(f"{texture_path}: {extra[0]}")
               
                # Update progress
                if self.progress_callback:
                    progress = (i + 1) / len(texture_paths) * 100
                    self.progress_callback(progress, f"Processed {i + 1}/{len(texture_paths)}")
       
        return results
   
    def batch_convert_models(self, model_paths: List[str], output_dir: str, format: str = 'obj') -> Dict[str, Any]:
        """Batch convert multiple RDR1 models"""
        results = {
            'total': len(model_paths),
            'success': 0,
            'failed': 0,
            'errors': []
        }
       
        def process_model(model_path):
            if self.cancel_flag:
                return None
               
            try:
                model_name = Path(model_path).stem
                output_path = Path(output_dir) / f"{model_name}.{format}"
               
                # Import here to avoid circular imports
                from rage_plugins.rdr1_enhanced_plugin import convert_model
               
                if convert_model(model_path, str(output_path), format):
                    return ('success', model_path)
                else:
                    return ('failed', model_path, "Conversion failed")
                   
            except Exception as e:
                return ('error', model_path, str(e))
       
        # Process models with thread pool
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_model = {executor.submit(process_model, path): path for path in model_paths}
           
            for i, future in enumerate(as_completed(future_to_model)):
                if self.cancel_flag:
                    break
                   
                result = future.result()
                if result:
                    status, model_path, *extra = result
                   
                    if status == 'success':
                        results['success'] += 1
                    elif status == 'failed':
                        results['failed'] += 1
                        results['errors'].append(f"{model_path}: {extra[0]}")
                    else:  # error
                        results['failed'] += 1
                        results['errors'].append(f"{model_path}: {extra[0]}")
               
                # Update progress
                if self.progress_callback:
                    progress = (i + 1) / len(model_paths) * 100
                    self.progress_callback(progress, f"Processed {i + 1}/{len(model_paths)}")
       
        return results

def create_batch_processor() -> RDR1BatchProcessor:
    """Create batch processor instance"""
    return RDR1BatchProcessor()