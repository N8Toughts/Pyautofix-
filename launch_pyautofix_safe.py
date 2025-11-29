"""
SAFE PyAutoFix Launcher - Won't affect your other tools
Place this in your main project folder and run it.
"""

import sys
import os

print("🔧 Safe PyAutoFix Launcher")
print("This won't affect your other tools...")

# Add current directory temporarily
original_path = sys.path.copy()
sys.path.insert(0, os.getcwd())

try:
    from pyautofix.gui.modern_gui import main as gui_main
    print("✅ PyAutoFix GUI loaded successfully!")
    print("🚀 Launching now...")
    gui_main()
   
except ImportError as e:
    print(f"❌ PyAutoFix not available: {e}")
    print("\n💡 This doesn't affect your other tools.")
    print("   They should still work normally.")
   
finally:
    # Restore original path - IMPORTANT for your other tools!
    sys.path = original_path

input("Press Enter to close...")