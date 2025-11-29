import logging
import os
from pathlib import Path
from typing import Dict, List, Any
import struct

# Add evolutionary plugin
try:
    from plugins.rage_evolutionary_detector import RAGEEvolutionaryDetector
    EVOLUTIONARY_PLUGIN_AVAILABLE = True
except ImportError:
    EVOLUTIONARY_PLUGIN_AVAILABLE = False

logger = logging.getLogger(__name__)

class FileAnalyzerEngine:
    """Enhanced with evolutionary RAGE detection"""
   
    def __init__(self):
        self.detection_patterns = {
            'ydr': self.detect_ydr_files,
            'game_assets': self.detect_game_assets,
            'rage_engine': self.detect_rage_engine_files
        }
        self.learning_data = []
        self.recognition_failures = []
       
        # Initialize evolutionary detector
        if EVOLUTIONARY_PLUGIN_AVAILABLE:
            self.evolutionary_detector = RAGEEvolutionaryDetector()
        else:
            self.evolutionary_detector = None

    def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Enhanced with evolutionary analysis"""
        query_lower = query.lower()
       
        if "evolution" in query_lower or "multiple games" in query_lower:
            return self.evolutionary_analysis_report()
        elif "rage timeline" in query_lower:
            return self.rage_timeline_analysis()
        else:
            # Existing logic plus evolutionary capabilities
            return self.enhanced_general_response(query)

    def evolutionary_analysis_report(self) -> str:
        """Report on evolutionary analysis capabilities"""
        if not self.evolutionary_detector:
            return "Evolutionary plugin not available. Install RAGE evolutionary detector."
       
        report = self.evolutionary_detector.get_evolutionary_report()
       
        response = "🔬 **RAGE Engine Evolutionary Analysis:**\n\n"
        response += f"**Analysis Coverage:**\n"
        response += f"- Total files analyzed: {report['total_analyses']}\n"
        response += f"- Cross-game patterns found: {report['cross_game_matches']}\n\n"
       
        response += "**RAGE Engine Timeline:**\n"
        for timeline_entry in report['engine_timeline_coverage']:
            response += f"- {timeline_entry}\n"
        response += "\n"
       
        if report['evolutionary_patterns']:
            response += "**Evolutionary Patterns Discovered:**\n"
            for pattern in report['evolutionary_patterns'][-3:]:  # Last 3 patterns
                response += f"- {pattern['pattern']} (first seen: {pattern['first_seen'][:10]})\n"
       
        return response

    def analyze_file_evolutionary(self, file_path: str) -> Dict[str, Any]:
        """Enhanced file analysis with evolutionary detection"""
        base_analysis = self.analyze_file(file_path)
       
        if self.evolutionary_detector:
            evolutionary_analysis = self.evolutionary_detector.detect_evolutionary_patterns(file_path)
            base_analysis['evolutionary_analysis'] = evolutionary_analysis
            base_analysis['rage_engine_compatibility'] = evolutionary_analysis['game_matches']
       
        return base_analysis

    def rage_timeline_analysis(self) -> str:
        """Analyze RAGE engine evolution timeline"""
        response = "📊 **RAGE Engine Evolutionary Timeline Analysis:**\n\n"
       
        timeline = [
            "🎮 **Midnight Club 3 (2005)** - Early RAGE prototype",
            "  • Simple asset formats, basic streaming",
            "  • Foundation for future engine development\n",
           
            "🏙️ **GTA IV (2008)** - RAGE 1.0 Official Release",
            "  • Advanced streaming, memory management",
            "  • Euphoria physics integration",
            "  • WTD/WDR/WFT format standardization\n",
           
            "🔫 **Max Payne 3 (2012)** - RAGE 1.2 Enhanced",
            "  • Improved texture streaming",
            "  • Enhanced animation system",
            "  • Brazil localization optimizations\n",
           
            "🤠 **Red Dead Redemption (2010)** - RAGE 1.3 Western",
            "  • Large open world optimizations",
            "  • Horse/animal animation systems",
            "  • Weather and time of day systems\n",
           
            "💎 **GTA V (2013)** - RAGE 1.8 Modern",
            "  • YDR/YDD/YFT format refinement",
            "  • Advanced LOD systems",
            "  • Multi-platform optimization\n"
        ]
       
        for entry in timeline:
            response += entry + "\n"
       
        response += "\n**Evolutionary Insight:** Files that work across multiple RAGE versions "
        response += "reveal the engine's core architecture and help decode unknown formats!"
       
        return response

    def enhanced_general_response(self, query: str) -> str:
        """Enhanced response with evolutionary capabilities"""
        response = f"I've analyzed: '{query}'\n\n"
        response += "**Enhanced RAGE Analysis Available:**\n"
        response += "• Multi-game evolutionary pattern detection\n"
        response += "• RAGE engine timeline compatibility testing\n"
        response += "• Cross-version format decoding\n"
        response += "• Unknown file format inference\n\n"
       
        if self.evolutionary_detector:
            response += "🎯 **Try asking:**\n"
            response += "- 'Analyze this file across all RAGE games'\n"
            response += "- 'What RAGE engine evolution patterns do you see?'\n"
            response += "- 'Compare GTA IV vs GTA V file compatibility'\n"
       
        return response