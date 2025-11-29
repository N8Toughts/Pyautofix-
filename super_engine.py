import asyncio
import concurrent.futures
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SuperCorrectionEngine:
    """
    Ultimate correction engine incorporating ALL features:
    - RAGE analyzer integration
    - Blender plugin testing
    - Advanced AI models
    - Cross-script analysis
    - Learning systems
    - Environment detection
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.performance_mode = config.get('performance_mode', 'balanced')
        self.max_workers = config.get('max_workers', 4)
      
        self.available_systems = {}
        self._initialize_subsystems()
      
    def _initialize_subsystems(self):
        """Initialize all available subsystems"""
        subsystems = [
            ('core_engine', self._init_core_engine),
            ('rage_analyzer', self._init_rage_analyzer),
            ('blender_analyzer', self._init_blender_analyzer),
            ('ai_integration', self._init_ai_integration),
            ('learning_system', self._init_learning_system),
            ('cross_analyzer', self._init_cross_analyzer),
            ('environment_detector', self._init_environment_detector),
            ('auto_writer', self._init_auto_writer)
        ]
      
        for name, init_func in subsystems:
            try:
                self.available_systems[name] = init_func()
                logger.info(f"✓ Initialized {name}")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize {name}: {e}")
                self.available_systems[name] = None

    def _init_core_engine(self):
        from .engine import CodeCorrectionEngine
        return CodeCorrectionEngine(self.config)

    def _init_rage_analyzer(self):
        try:
            from ..integrations.rage_analyzer import RAGEAnalyzerIntegration
            return RAGEAnalyzerIntegration()
        except ImportError:
            logger.warning("RAGE analyzer not available")
            return None

    def _init_blender_analyzer(self):
        try:
            from ..integrations.blender_analyzer import BlenderPluginAnalyzer
            return BlenderPluginAnalyzer()
        except ImportError:
            logger.warning("Blender analyzer not available")
            return None

    def _init_ai_integration(self):
        try:
            from ..integrations.advanced_ai import AdvancedAIIntegration
            return AdvancedAIIntegration()
        except ImportError:
            logger.warning("Advanced AI integration not available")
            return None

    def _init_learning_system(self):
        try:
            from ..learning.advanced_learning import AdvancedLearningSystem
            return AdvancedLearningSystem()
        except ImportError:
            from ..learning.feedback_learning import FeedbackLearner
            return FeedbackLearner()

    def _init_cross_analyzer(self):
        try:
            from .cross_analyzer import CrossScriptAnalyzer
            return CrossScriptAnalyzer()
        except ImportError:
            logger.warning("Cross-script analyzer not available")
            return None

    def _init_environment_detector(self):
        try:
            from .environment_detector import EnvironmentDetector
            return EnvironmentDetector()
        except ImportError:
            logger.warning("Environment detector not available")
            return None

    def _init_auto_writer(self):
        try:
            from .auto_writer import AutoWriteManager
            return AutoWriteManager()
        except ImportError:
            logger.warning("Auto writer not available")
            return None

    async def analyze_comprehensive(self, target_path: str) -> Dict[str, Any]:
        """Comprehensive analysis using all available systems"""
        results = {
            'target': target_path,
            'analysis_timestamp': self._current_timestamp(),
            'systems_used': [],
            'results': {}
        }
      
        tasks = []
      
        # File type detection
        if Path(target_path).is_file():
            tasks.append(self._analyze_file(target_path))
        else:
            tasks.append(self._analyze_directory(target_path))
          
        # Additional analyses based on detected type
        if self.available_systems.get('rage_analyzer'):
            tasks.append(self._analyze_with_rage(target_path))
          
        if self.available_systems.get('blender_analyzer') and self._is_blender_plugin(target_path):
            tasks.append(self._analyze_blender_plugin(target_path))
          
        # Execute all analyses
        analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
      
        # Compile results
        for result in analysis_results:
            if not isinstance(result, Exception) and isinstance(result, dict):
                results['results'].update(result)
              
        results['systems_used'] = [name for name, system in self.available_systems.items() if system is not None]
        return results

    async def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze single file with multiple systems"""
        analysis = {}
      
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
          
            # Core engine analysis
            if self.available_systems['core_engine']:
                analysis['core_issues'] = self.available_systems['core_engine'].analyze_code(code, file_path)
          
            # Environment detection
            if self.available_systems['environment_detector']:
                analysis['environment'] = self.available_systems['environment_detector'].analyze_environment(file_path)
              
            # AI analysis if available
            if self.available_systems['ai_integration']:
                try:
                    analysis['ai_suggestions'] = await self.available_systems['ai_integration'].analyze_code_async(code)
                except Exception as e:
                    analysis['ai_analysis_error'] = str(e)
                  
        except Exception as e:
            analysis['file_read_error'] = str(e)
          
        return analysis

    async def _analyze_directory(self, directory: str) -> Dict[str, Any]:
        """Analyze directory with cross-script analysis"""
        analysis = {}
      
        if self.available_systems['cross_analyzer']:
            try:
                analysis['cross_script'] = self.available_systems['cross_analyzer'].analyze_project(directory)
            except Exception as e:
                analysis['cross_analysis_error'] = str(e)
              
        return analysis

    async def _analyze_with_rage(self, target_path: str) -> Dict[str, Any]:
        """Analyze with RAGE analyzer"""
        try:
            return await self.available_systems['rage_analyzer'].analyze_file(target_path)
        except Exception as e:
            return {'rage_analysis_error': str(e)}

    async def _analyze_blender_plugin(self, plugin_path: str) -> Dict[str, Any]:
        """Analyze Blender plugin"""
        try:
            return self.available_systems['blender_analyzer'].analyze_plugin_structure(plugin_path)
        except Exception as e:
            return {'blender_analysis_error': str(e)}

    def _is_blender_plugin(self, path: str) -> bool:
        """Check if path contains Blender plugin"""
        try:
            path_obj = Path(path)
            if path_obj.is_file():
                return path_obj.suffix == '.py' and 'bl_info' in path_obj.read_text(encoding='utf-8', errors='ignore')
            else:
                # Check for __init__.py with bl_info
                init_file = path_obj / '__init__.py'
                return init_file.exists() and 'bl_info' in init_file.read_text(encoding='utf-8', errors='ignore')
        except:
            return False

    def _current_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()

    def correct_file(self, file_path: str) -> Dict[str, Any]:
        """Correct file using core engine"""
        if self.available_systems['core_engine']:
            return self.available_systems['core_engine'].correct_file(file_path)
        else:
            return {'success': False, 'error': 'Core engine not available'}

    def run_console(self):
        """Run comprehensive console interface"""
        print("PyAutoFix Super Engine - Complete Feature Set")
        print("=" * 60)
        print(f"Available systems: {', '.join(self.available_systems.keys())}")
        print()
      
        while True:
            print("\n" + "="*50)
            print("MAIN MENU - Comprehensive Analysis")
            print("="*50)
            print("1. Quick File Analysis")
            print("2. Comprehensive File Analysis")
            print("3. Directory Analysis")
            print("4. Blender Plugin Analysis")
            print("5. RAGE Format Analysis")
            print("6. AI-Powered Correction")
            print("7. Learning Insights")
            print("8. Exit")
          
            choice = input("\nSelect option (1-8): ").strip()
          
            if choice == '1':
                self._quick_file_analysis()
            elif choice == '2':
                self._comprehensive_file_analysis()
            elif choice == '3':
                self._directory_analysis()
            elif choice == '4':
                self._blender_plugin_analysis()
            elif choice == '5':
                self._rage_analysis()
            elif choice == '6':
                self._ai_correction()
            elif choice == '7':
                self._learning_insights()
            elif choice == '8':
                print("Thank you for using PyAutoFix Super Engine!")
                break
            else:
                print("Invalid option!")

    def _quick_file_analysis(self):
        """Quick file analysis"""
        file_path = input("Enter file path: ").strip()
        if not file_path or not Path(file_path).exists():
            print("File not found!")
            return
           
        if not self.available_systems['core_engine']:
            print("Core engine not available!")
            return
           
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
               
            issues = self.available_systems['core_engine'].analyze_code(code, file_path)
            print(f"\nQuick Analysis Results for: {file_path}")
            print("-" * 50)
           
            if not issues:
                print("✅ No issues found!")
            else:
                print(f"Found {len(issues)} issues:")
                for i, issue in enumerate(issues, 1):
                    print(f"{i}. {issue['description']}")
                    print(f"   Severity: {issue.get('severity', 'unknown')}")
                   
        except Exception as e:
            print(f"Error analyzing file: {e}")

    def _comprehensive_file_analysis(self):
        """Comprehensive file analysis"""
        file_path = input("Enter file path: ").strip()
        if not file_path or not Path(file_path).exists():
            print("File not found!")
            return
           
        print("Running comprehensive analysis...")
        try:
            async def analyze():
                return await self.analyze_comprehensive(file_path)
               
            results = asyncio.run(analyze())
            print(f"\nComprehensive Analysis Results for: {file_path}")
            print("=" * 60)
           
            for system, result in results['results'].items():
                print(f"\n{system.upper()}:")
                print("-" * 40)
                if isinstance(result, dict):
                    for key, value in result.items():
                        if key not in ['original_code', 'corrected_code']:
                            print(f"  {key}: {value}")
                elif isinstance(result, list):
                    for item in result[:5]:
                        print(f"  - {item}")
                else:
                    print(f"  {result}")
                   
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")

    def _directory_analysis(self):
        """Directory analysis"""
        directory = input("Enter directory path: ").strip()
        if not directory or not Path(directory).exists():
            print("Directory not found!")
            return
           
        print("Analyzing directory...")
        if self.available_systems['cross_analyzer']:
            try:
                result = self.available_systems['cross_analyzer'].analyze_project(directory)
                print(f"\nDirectory Analysis: {directory}")
                print("=" * 50)
                print(f"Files analyzed: {result['files_analyzed']}")
                print(f"Total dependencies: {result['total_dependencies']}")
                print(f"Issues found: {len(result['issues'])}")
               
                for issue in result['issues']:
                    print(f"\n• {issue['description']}")
                    print(f"  Files: {', '.join(issue['files'])}")
                   
            except Exception as e:
                print(f"Error analyzing directory: {e}")
        else:
            print("Cross-script analyzer not available!")

    def _blender_plugin_analysis(self):
        """Blender plugin analysis"""
        plugin_dir = input("Enter Blender plugin directory: ").strip()
        if not plugin_dir or not Path(plugin_dir).exists():
            print("Directory not found!")
            return
           
        if self.available_systems['blender_analyzer']:
            try:
                result = self.available_systems['blender_analyzer'].analyze_plugin_structure(plugin_dir)
                print(f"\nBlender Plugin Analysis: {plugin_dir}")
                print("=" * 50)
                print(f"Plugin name: {result.get('plugin_name', 'Unknown')}")
                print(f"Total files: {result.get('total_files', 0)}")
                print(f"Python files: {result.get('python_files', 0)}")
                print(f"Operators found: {len(result.get('operators_found', []))}")
                print(f"Dependencies: {', '.join(result.get('dependencies', []))}")
               
            except Exception as e:
                print(f"Error analyzing Blender plugin: {e}")
        else:
            print("Blender analyzer not available!")

    def _rage_analysis(self):
        """RAGE format analysis"""
        file_path = input("Enter game file path: ").strip()
        if not file_path or not Path(file_path).exists():
            print("File not found!")
            return
           
        if self.available_systems['rage_analyzer']:
            try:
                async def analyze():
                    return await self.available_systems['rage_analyzer'].analyze_file(file_path)
                   
                result = asyncio.run(analyze())
                print(f"\nRAGE Analysis: {file_path}")
                print("=" * 50)
               
                if 'error' in result:
                    print(f"Error: {result['error']}")
                else:
                    for key, value in result.items():
                        print(f"{key}: {value}")
                       
            except Exception as e:
                print(f"Error in RAGE analysis: {e}")
        else:
            print("RAGE analyzer not available!")

    def _ai_correction(self):
        """AI-powered correction"""
        print("AI-powered correction - Feature requires AI integration setup")
        file_path = input("Enter file path: ").strip()
        if not file_path or not Path(file_path).exists():
            print("File not found!")
            return
           
        print("AI correction would be performed here with integrated AI models")

    def _learning_insights(self):
        """Learning insights"""
        if self.available_systems['learning_system']:
            try:
                insights = self.available_systems['learning_system'].get_learning_insights()
                print("\nLearning Insights")
                print("=" * 50)
               
                if insights:
                    for key, value in insights.items():
                        print(f"{key}: {value}")
                else:
                    print("No learning data available yet.")
                   
            except Exception as e:
                print(f"Error getting learning insights: {e}")
        else:
            print("Learning system not available!")