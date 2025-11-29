"""
PyAutoFix Blender Enhanced Integration
Advanced real-time code analysis and error detection for Blender
"""

bl_info = {
    "name": "PyAutoFix Enhanced Blender Integration",
    "author": "PyAutoFix Team",
    "version": (2, 2, 0),
    "blender": (3, 0, 0),
    "location": "Text Editor > Sidebar > PyAutoFix & Top Bar > PyAutoFix Monitor",
    "description": "Enhanced real-time code analysis, error detection, and auto-fixing with PyAutoFix integration",
    "category": "Development",
}

import bpy
import os
import sys
import subprocess
import json
import threading
import traceback
from pathlib import Path
from bpy.types import Panel, Operator, PropertyGroup, Menu
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty, FloatProperty
from bpy.app.handlers import persistent

# Enhanced error monitoring
original_excepthook = sys.excepthook
detected_errors = []

def enhanced_excepthook(exc_type, exc_value, exc_traceback):
    """Enhanced exception hook to capture and analyze errors in real-time"""
    # Call original hook first
    original_excepthook(exc_type, exc_value, exc_traceback)
   
    # Capture error information
    error_info = {
        'type': exc_type.__name__,
        'message': str(exc_value),
        'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback),
        'timestamp': bpy.utils.system_time(),
        'blender_context': get_blender_context()
    }
   
    detected_errors.append(error_info)
   
    # Auto-analyze if enabled
    try:
        if hasattr(bpy.context, 'scene') and hasattr(bpy.context.scene, 'pyautofix_enhanced_props'):
            props = bpy.context.scene.pyautofix_enhanced_props
            if props.auto_analyze_errors:
                analyze_error_async(error_info)
    except:
        pass

def get_blender_context():
    """Get current Blender context information"""
    try:
        return {
            'mode': bpy.context.mode,
            'active_object': bpy.context.active_object.name if bpy.context.active_object else None,
            'selected_objects': [obj.name for obj in bpy.context.selected_objects],
            'area': bpy.context.area.type if bpy.context.area else None,
            'scene': bpy.context.scene.name
        }
    except:
        return {}

def analyze_error_async(error_info):
    """Analyze error asynchronously"""
    def analyze():
        try:
            suggestions = generate_error_suggestions(error_info)
            print(f"🎯 PyAutoFix detected {error_info['type']}: {error_info['message']}")
            print(f"💡 Suggestions: {suggestions}")
           
            # Update UI if possible
            try:
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'TEXT_EDITOR':
                            area.tag_redraw()
            except:
                pass
               
        except Exception as e:
            print(f"Error analysis failed: {e}")
   
    threading.Thread(target=analyze, daemon=True).start()

def generate_error_suggestions(error_info):
    """Generate intelligent suggestions for errors"""
    error_type = error_info['type']
    error_message = error_info['message']
   
    suggestions_db = {
        'AttributeError': {
            'pattern': "object has no attribute",
            'suggestions': [
                "Check if the object exists before accessing attributes",
                "Verify import statements for the module",
                "Check for typos in attribute names",
                "Use hasattr() to check for attribute existence"
            ]
        },
        'NameError': {
            'pattern': "name.*is not defined",
            'suggestions': [
                "Check if the variable/function is defined",
                "Verify import statements",
                "Check for typos in variable/function names",
                "Ensure the name is in the correct scope"
            ]
        },
        'ImportError': {
            'pattern': "No module named",
            'suggestions': [
                "Check if the module is installed: pip install module_name",
                "Verify the module name spelling",
                "Check Python path configuration",
                "For Blender addons, check if the addon is enabled"
            ]
        },
        'TypeError': {
            'pattern': "unexpected keyword argument",
            'suggestions': [
                "Check function argument names for typos",
                "Verify the function signature",
                "Check if you're using the correct Blender API version"
            ]
        }
    }
   
    for error_class, info in suggestions_db.items():
        if error_type == error_class or info['pattern'] in error_message:
            return " | ".join(info['suggestions'])
   
    return "Review the error context and check Blender Python API documentation"

class PyAutoFixEnhancedProperties(PropertyGroup):
    """Enhanced properties for PyAutoFix integration"""
   
    # Analysis settings
    auto_analyze: BoolProperty(
        name="Auto Analyze on Save",
        description="Automatically analyze scripts when saved",
        default=True
    )
   
    auto_analyze_errors: BoolProperty(
        name="Auto Analyze Errors",
        description="Automatically analyze Python errors when they occur",
        default=True
    )
   
    auto_fix: BoolProperty(
        name="Auto Fix",
        description="Automatically fix common issues when possible",
        default=False
    )
   
    # Display settings
    show_suggestions: BoolProperty(
        name="Show Suggestions",
        description="Show code improvement suggestions",
        default=True
    )
   
    show_performance: BoolProperty(
        name="Show Performance Tips",
        description="Show performance optimization suggestions",
        default=True
    )
   
    # Integration settings
    pyautofix_path: StringProperty(
        name="PyAutoFix Path",
        description="Path to PyAutoFix installation (leave empty for auto-detection)",
        default="",
        subtype='DIR_PATH'
    )
   
    # Results
    analysis_results: StringProperty(
        name="Analysis Results",
        description="Results from PyAutoFix analysis",
        default=""
    )
   
    last_analysis_time: StringProperty(
        name="Last Analysis",
        description="Timestamp of last analysis",
        default=""
    )
   
    error_count: IntProperty(
        name="Error Count",
        description="Number of errors detected in this session",
        default=0
    )

class PYAUTOFIX_OT_analyze_with_suggestions(Operator):
    """Analyze current script with intelligent suggestions"""
    bl_idname = "pyautofix.analyze_with_suggestions"
    bl_label = "Analyze with Suggestions"
    bl_description = "Analyze current script and provide intelligent improvement suggestions"
   
    def execute(self, context):
        text_editor = context.space_data
        if not text_editor or not text_editor.text:
            self.report({'WARNING'}, "No active script in text editor")
            return {'CANCELLED'}
       
        script_content = text_editor.text.as_string()
        script_name = text_editor.text.name
       
        # Create temporary file
        temp_dir = Path(bpy.app.tempdir) / "pyautofix_blender"
        temp_dir.mkdir(exist_ok=True)
       
        temp_script_path = temp_dir / f"analyze_{script_name}.py"
        with open(temp_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
       
        # Run enhanced analysis
        props = context.scene.pyautofix_enhanced_props
        results = self.enhanced_analysis(str(temp_script_path), script_content, props.pyautofix_path)
       
        props.analysis_results = results
        props.last_analysis_time = f"Last analysis: {bpy.utils.smpte_from_frame(bpy.context.scene.frame_current)}"
       
        # Show notification
        if "No issues found" in results:
            self.report({'INFO'}, "Script analysis complete - No issues found!")
        else:
            self.report({'WARNING'}, "Script analysis complete - Issues found!")
       
        # Clean up
        try:
            temp_script_path.unlink()
        except:
            pass
       
        return {'FINISHED'}
   
    def enhanced_analysis(self, script_path: str, script_content: str, pyautofix_path: str) -> str:
        """Run enhanced analysis with intelligent suggestions"""
        try:
            # Basic PyAutoFix analysis
            if pyautofix_path and os.path.exists(pyautofix_path):
                pyautofix_cmd = [sys.executable, "-m", "pyautofix", script_path, "--analyze-only"]
            else:
                pyautofix_cmd = ["pyautofix", script_path, "--analyze-only"]
           
            result = subprocess.run(
                pyautofix_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
           
            base_analysis = ""
            if result.returncode == 0:
                base_analysis = self.format_analysis_results(result.stdout, script_path)
            else:
                base_analysis = f"PyAutoFix analysis failed:\n{result.stderr}"
           
            # Add intelligent suggestions
            suggestions = self.generate_intelligent_suggestions(script_content)
           
            return f"{base_analysis}\n\n🎯 INTELLIGENT SUGGESTIONS:\n{suggestions}"
           
        except Exception as e:
            return f"Enhanced analysis error: {str(e)}"
   
    def generate_intelligent_suggestions(self, script_content: str) -> str:
        """Generate intelligent code suggestions"""
        suggestions = []
       
        # Performance suggestions
        if "bpy.ops." in script_content and "context" not in script_content:
            suggestions.append("⚡ Use bpy.context instead of bpy.ops for better performance")
       
        if "import bpy" in script_content and "from bpy import" not in script_content:
            suggestions.append("📦 Use 'from bpy import data, context, ops' for cleaner imports")
       
        if "bpy.data.objects" in script_content and "bpy.data.collections" not in script_content:
            suggestions.append("🗂️ Consider using collections for better object organization")
       
        # Code quality suggestions
        if "==" in script_content and "is" not in script_content:
            suggestions.append("🔍 Use 'is' for None comparisons instead of '=='")
       
        if "len(" in script_content and "if obj:" not in script_content:
            suggestions.append("📏 Use truthiness checks instead of len() for empty collections")
       
        # Blender-specific suggestions
        if "bpy.ops.mesh" in script_content and "bpy.types.Operator" not in script_content:
            suggestions.append("🎯 Consider creating custom operators for complex mesh operations")
       
        if "bpy.context.scene.frame_current" in script_content and "driver" not in script_content:
            suggestions.append("🎞️ Consider using drivers for frame-based animations")
       
        if suggestions:
            return "\n".join(suggestions)
        else:
            return "✅ Code follows Blender best practices!"

class PYAUTOFIX_OT_quick_fix_all(Operator):
    """Quick fix all common issues in current script"""
    bl_idname = "pyautofix.quick_fix_all"
    bl_label = "Quick Fix All"
    bl_description = "Quickly fix all common issues in the current script"
   
    def execute(self, context):
        text_editor = context.space_data
        if not text_editor or not text_editor.text:
            self.report({'WARNING'}, "No active script in text editor")
            return {'CANCELLED'}
       
        original_content = text_editor.text.as_string()
        fixed_content = self.apply_quick_fixes(original_content)
       
        if fixed_content != original_content:
            text_editor.text.clear()
            text_editor.text.write(fixed_content)
            self.report({'INFO'}, "Quick fixes applied successfully!")
        else:
            self.report({'INFO'}, "No quick fixes needed!")
       
        return {'FINISHED'}
   
    def apply_quick_fixes(self, content: str) -> str:
        """Apply quick fixes to script content"""
        fixes = {
            ' == None': ' is None',
            ' != None': ' is not None',
            'len(x) == 0': 'not x',
            'len(x) > 0': 'x',
            'import bpy\n\n': 'import bpy\nfrom bpy import context, data, ops\n\n',
            'bpy.context.scene': 'context.scene',
            'bpy.data.objects': 'data.objects',
        }
       
        fixed_content = content
        for wrong, right in fixes.items():
            fixed_content = fixed_content.replace(wrong, right)
       
        return fixed_content

class PYAUTOFIX_OT_scan_blender_environment(Operator):
    """Scan Blender environment for issues and optimizations"""
    bl_idname = "pyautofix.scan_blender_environment"
    bl_label = "Scan Blender Environment"
    bl_description = "Scan Blender environment for common issues and optimization opportunities"
   
    def execute(self, context):
        scan_results = self.perform_environment_scan()
        props = context.scene.pyautofix_enhanced_props
        props.analysis_results = scan_results
       
        self.report({'INFO'}, "Environment scan complete!")
        return {'FINISHED'}
   
    def perform_environment_scan(self) -> str:
        """Perform comprehensive Blender environment scan"""
        results = ["🔍 BLENDER ENVIRONMENT SCAN RESULTS", "=" * 50, ""]
       
        # Check Blender version and compatibility
        results.append(f"📊 Blender Version: {bpy.app.version_string}")
        results.append(f"📁 Python Version: {sys.version}")
        results.append("")
       
        # Check installed addons
        addon_count = len([addon for addon in bpy.context.preferences.addons])
        results.append(f"📦 Installed Addons: {addon_count}")
       
        # Check for common issues
        issues_found = self.check_common_issues()
        if issues_found:
            results.append("🚨 COMMON ISSUES FOUND:")
            results.extend(issues_found)
        else:
            results.append("✅ No common issues found")
       
        results.append("")
       
        # Performance suggestions
        performance_tips = self.get_performance_tips()
        if performance_tips:
            results.append("⚡ PERFORMANCE OPTIMIZATIONS:")
            results.extend(performance_tips)
       
        return "\n".join(results)
   
    def check_common_issues(self):
        """Check for common Blender environment issues"""
        issues = []
       
        # Check for undo steps (memory usage)
        if hasattr(bpy.context, 'window_manager'):
            issues.append("💾 Consider limiting undo steps in Preferences > System")
       
        # Check viewport settings
        if bpy.context.space_data and hasattr(bpy.context.space_data, 'viewport_shade'):
            if bpy.context.space_data.viewport_shade == 'RENDERED':
                issues.append("🎨 Switch to Solid mode for better viewport performance")
       
        # Check for large files
        if bpy.data.filepath and os.path.exists(bpy.data.filepath):
            file_size = os.path.getsize(bpy.data.filepath) / (1024 * 1024)  # MB
            if file_size > 100:
                issues.append(f"📁 Large file size: {file_size:.1f}MB - Consider using File > Clean Up")
       
        return issues
   
    def get_performance_tips(self):
        """Get performance optimization tips"""
        tips = []
       
        # Scene optimization tips
        if len(bpy.data.objects) > 1000:
            tips.append("🗑️ High object count - Consider using collections and instancing")
       
        if len(bpy.data.meshes) > 500:
            tips.append("📐 High mesh count - Consider using LODs or decimation")
       
        if len(bpy.data.materials) > 200:
            tips.append("🎨 High material count - Consider reusing materials")
       
        # Memory optimization tips
        tips.append("💾 Use File > Clean Up regularly to remove unused data blocks")
        tips.append("🚀 Enable GPU rendering in Preferences > System for better performance")
        tips.append("📊 Use Statistics overlay (N-panel) to monitor performance")
       
        return tips

class PYAUTOFIX_OT_show_error_log(Operator):
    """Show detailed error log with analysis"""
    bl_idname = "pyautofix.show_error_log"
    bl_label = "Error Log & Analysis"
    bl_description = "Show detailed error log with intelligent analysis"
   
    def execute(self, context):
        # Create error log text block
        error_log = bpy.data.texts.new("PyAutoFix_Enhanced_Error_Log")
       
        log_content = ["🔍 PYTHON ERROR LOG & ANALYSIS", "=" * 50, ""]
        log_content.append(f"Total errors detected: {len(detected_errors)}")
        log_content.append("")
       
        for i, error in enumerate(detected_errors, 1):
            log_content.append(f"ERROR #{i}:")
            log_content.append(f"Type: {error['type']}")
            log_content.append(f"Message: {error['message']}")
            log_content.append(f"Time: {error['timestamp']}")
            log_content.append("")
           
            # Add analysis
            suggestions = generate_error_suggestions(error)
            log_content.append("💡 SUGGESTED FIXES:")
            log_content.append(suggestions)
            log_content.append("")
           
            log_content.append("📋 TRACEBACK:")
            log_content.extend(error['traceback'])
            log_content.append("-" * 50)
            log_content.append("")
       
        error_log.write("\n".join(log_content))
       
        # Show in text editor
        for area in context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces.active.text = error_log
                break
       
        self.report({'INFO'}, f"Error log created with {len(detected_errors)} entries")
        return {'FINISHED'}

class PYAUTOFIX_OT_optimize_blender_scene(Operator):
    """Optimize current Blender scene for better performance"""
    bl_idname = "pyautofix.optimize_blender_scene"
    bl_label = "Optimize Scene"
    bl_description = "Optimize current Blender scene for better performance"
   
    def execute(self, context):
        optimizations = self.perform_scene_optimization()
       
        props = context.scene.pyautofix_enhanced_props
        props.analysis_results = optimizations
       
        self.report({'INFO'}, "Scene optimization complete!")
        return {'FINISHED'}
   
    def perform_scene_optimization(self) -> str:
        """Perform scene optimization analysis"""
        results = ["⚡ SCENE OPTIMIZATION ANALYSIS", "=" * 50, ""]
       
        # Analyze scene statistics
        total_objects = len(bpy.data.objects)
        total_vertices = sum(len(mesh.vertices) for mesh in bpy.data.meshes if hasattr(mesh, 'vertices'))
        total_materials = len(bpy.data.materials)
       
        results.append(f"📊 SCENE STATISTICS:")
        results.append(f"  Objects: {total_objects}")
        results.append(f"  Total Vertices: {total_vertices:,}")
        results.append(f"  Materials: {total_materials}")
        results.append("")
       
        # Optimization suggestions
        suggestions = []
       
        if total_objects > 500:
            suggestions.append("🗑️ High object count - Use collections and instancing")
       
        if total_vertices > 1000000:
            suggestions.append("📐 High vertex count - Consider using decimation or LODs")
       
        if total_materials > 100:
            suggestions.append("🎨 High material count - Reuse materials where possible")
       
        # Check for unused data
        unused_meshes = [mesh for mesh in bpy.data.meshes if not mesh.users]
        unused_materials = [mat for mat in bpy.data.materials if not mat.users]
       
        if unused_meshes:
            suggestions.append(f"📦 {len(unused_meshes)} unused meshes - Use File > Clean Up")
       
        if unused_materials:
            suggestions.append(f"🎨 {len(unused_materials)} unused materials - Use File > Clean Up")
       
        if suggestions:
            results.append("💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in suggestions:
                results.append(f"  • {suggestion}")
        else:
            results.append("✅ Scene is well optimized!")
       
        return "\n".join(results)

class PYAUTOFIX_MT_analysis_menu(Menu):
    """Analysis menu for PyAutoFix"""
    bl_label = "PyAutoFix Analysis"
    bl_idname = "PYAUTOFIX_MT_analysis_menu"
   
    def draw(self, context):
        layout = self.layout
        layout.operator("pyautofix.analyze_with_suggestions", icon='VIEWZOOM')
        layout.operator("pyautofix.quick_fix_all", icon='AUTO')
        layout.separator()
        layout.operator("pyautofix.scan_blender_environment", icon='PREFERENCES')
        layout.operator("pyautofix.optimize_blender_scene", icon='LIGHT_SUN')
        layout.separator()
        layout.operator("pyautofix.show_error_log", icon='ERROR')

class PYAUTOFIX_PT_enhanced_panel(Panel):
    """Enhanced PyAutoFix panel in the text editor"""
    bl_label = "PyAutoFix Enhanced"
    bl_idname = "PYAUTOFIX_PT_enhanced_panel"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "PyAutoFix"
   
    def draw(self, context):
        layout = self.layout
        props = context.scene.pyautofix_enhanced_props
       
        # Quick actions
        box = layout.box()
        box.label(text="Quick Actions", icon='PLAY')
       
        row = box.row()
        row.menu("PYAUTOFIX_MT_analysis_menu", text="Run Analysis", icon='DOWNARROW_HLT')
        row.operator("pyautofix.quick_fix_all", text="Quick Fix", icon='AUTO')
       
        # Analysis settings
        box = layout.box()
        box.label(text="Analysis Settings", icon='PREFERENCES')
       
        box.prop(props, "auto_analyze", toggle=True)
        box.prop(props, "auto_analyze_errors", toggle=True)
        box.prop(props, "auto_fix", toggle=True)
       
        # Display settings
        row = box.row()
        row.prop(props, "show_suggestions", toggle=True)
        row.prop(props, "show_performance", toggle=True)
       
        # Environment info
        box = layout.box()
        box.label(text="Environment Info", icon='INFO')
       
        row = box.row()
        row.label(text=f"Blender: {bpy.app.version_string}")
       
        row = box.row()
        row.label(text=f"Python: {sys.version.split()[0]}")
       
        # Error monitoring
        if detected_errors:
            box = layout.box()
            box.label(text="Error Monitor", icon='ERROR')
            box.label(text=f"Errors detected: {len(detected_errors)}")
            box.operator("pyautofix.show_error_log", icon='TEXT')
       
        # Results display
        if props.analysis_results:
            box = layout.box()
            box.label(text="Analysis Results", icon='TEXT')
           
            # Show last analysis time
            if props.last_analysis_time:
                box.label(text=props.last_analysis_time, icon='TIME')
           
            # Display results in a scrollable text area
            for line in props.analysis_results.split('\n'):
                if not line.strip():
                    continue
                   
                icon = 'DOT'
                if any(marker in line for marker in ['🚨', '❌', 'ERROR']):
                    icon = 'ERROR'
                elif any(marker in line for marker in ['⚡', '💡', 'SUGGESTION']):
                    icon = 'LIGHT'
                elif any(marker in line for marker in ['✅', '✔', 'SUCCESS']):
                    icon = 'CHECKMARK'
                elif any(marker in line for marker in ['📊', '📦', 'INFO']):
                    icon = 'INFO'
               
                box.label(text=line, icon=icon)

class PYAUTOFIX_PT_enhanced_header_panel(Panel):
    """Enhanced PyAutoFix panel in the header"""
    bl_label = "PyAutoFix Monitor"
    bl_idname = "PYAUTOFIX_PT_enhanced_header_panel"
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
   
    def draw(self, context):
        layout = self.layout
        props = context.scene.pyautofix_enhanced_props
       
        row = layout.row()
       
        # Error counter with alert
        if detected_errors:
            row.alert = True
            row.label(text=f"Errors: {len(detected_errors)}", icon='ERROR')
            row.alert = False
        else:
            row.label(text="No errors", icon='CHECKMARK')
       
        # Quick analysis button
        row.operator("pyautofix.analyze_with_suggestions", text="Analyze", icon='VIEWZOOM')
       
        # Settings menu
        row.menu("PYAUTOFIX_MT_analysis_menu", text="", icon='DOWNARROW_HLT')

@persistent
def auto_analyze_on_save(dummy):
    """Auto-analyze script on save"""
    try:
        context = bpy.context
        props = context.scene.pyautofix_enhanced_props
       
        if props.auto_analyze and context.space_data and context.space_data.text:
            def analyze_async():
                try:
                    op = PYAUTOFIX_OT_analyze_with_suggestions()
                    op.execute(context)
                except Exception as e:
                    print(f"Auto-analysis failed: {e}")
           
            thread = threading.Thread(target=analyze_async)
            thread.daemon = True
            thread.start()
    except:
        pass

def register():
    """Register the enhanced addon"""
    # Register classes
    bpy.utils.register_class(PyAutoFixEnhancedProperties)
    bpy.utils.register_class(PYAUTOFIX_OT_analyze_with_suggestions)
    bpy.utils.register_class(PYAUTOFIX_OT_quick_fix_all)
    bpy.utils.register_class(PYAUTOFIX_OT_scan_blender_environment)
    bpy.utils.register_class(PYAUTOFIX_OT_show_error_log)
    bpy.utils.register_class(PYAUTOFIX_OT_optimize_blender_scene)
    bpy.utils.register_class(PYAUTOFIX_MT_analysis_menu)
    bpy.utils.register_class(PYAUTOFIX_PT_enhanced_panel)
    bpy.utils.register_class(PYAUTOFIX_PT_enhanced_header_panel)
   
    # Add properties to scene
    bpy.types.Scene.pyautofix_enhanced_props = bpy.props.PointerProperty(type=PyAutoFixEnhancedProperties)
   
    # Register handlers
    bpy.app.handlers.save_pre.append(auto_analyze_on_save)
   
    # Enable enhanced error monitoring
    sys.excepthook = enhanced_excepthook
   
    print("PyAutoFix Enhanced Blender Integration registered successfully")

def unregister():
    """Unregister the enhanced addon"""
    # Restore original exception hook
    sys.excepthook = original_excepthook
   
    # Remove handlers
    if auto_analyze_on_save in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(auto_analyze_on_save)
   
    # Remove properties
    del bpy.types.Scene.pyautofix_enhanced_props
   
    # Unregister classes
    bpy.utils.unregister_class(PYAUTOFIX_PT_enhanced_header_panel)
    bpy.utils.unregister_class(PYAUTOFIX_PT_enhanced_panel)
    bpy.utils.unregister_class(PYAUTOFIX_MT_analysis_menu)
    bpy.utils.unregister_class(PYAUTOFIX_OT_optimize_blender_scene)
    bpy.utils.unregister_class(PYAUTOFIX_OT_show_error_log)
    bpy.utils.unregister_class(PYAUTOFIX_OT_scan_blender_environment)
    bpy.utils.unregister_class(PYAUTOFIX_OT_quick_fix_all)
    bpy.utils.unregister_class(PYAUTOFIX_OT_analyze_with_suggestions)
    bpy.utils.unregister_class(PyAutoFixEnhancedProperties)

if __name__ == "__main__":
    register()