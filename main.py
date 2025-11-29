#!/usr/bin/env python3
"""
PyAutoFix Ultimate - Main Entry Point
Tested and verified working
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pyautofix.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("PyAutoFix")

def setup_environment():
    """Setup paths safely"""
    current_dir = Path(__file__).parent
    package_dir = current_dir
  
    # Add package directory to path
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    logger.info(f"Added to path: {package_dir}")

def main():
    """Main entry point with robust error handling"""
    setup_environment()
  
    logger.info("Starting PyAutoFix Ultimate...")
  
    try:
        # Try Enhanced Commander first
        from pyautofix.gui.enhanced_commander import EnhancedBridgeCommander
        logger.info("Launching Enhanced Bridge Commander")
        app = EnhancedBridgeCommander()
        app.run()
      
    except ImportError as e:
        logger.warning(f"Enhanced Commander failed: {e}")
      
        try:
            # Fallback to Modern GUI
            from pyautofix.gui.modern_gui import PyAutoFixGUI
            logger.info("Launching Modern GUI")
            app = PyAutoFixGUI()
            app.run()
          
        except ImportError as e:
            logger.warning(f"Modern GUI failed: {e}")
          
            try:
                # Final fallback to Console
                from pyautofix.core.super_engine import SuperCorrectionEngine
                logger.info("Launching Console Mode")
                engine = SuperCorrectionEngine()
                engine.run_console()
              
            except ImportError as e:
                logger.error(f"All launch methods failed: {e}")
                print("❌ ERROR: Could not start PyAutoFix")
                print(f"   Details: {e}")
                input("Press Enter to exit...")

if __name__ == "__main__":
    main()