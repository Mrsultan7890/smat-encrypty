#!/usr/bin/env python3
"""
Smart-Encrypt - Secure Personal Vault
Production-ready encrypted notes manager
"""
import sys
import os

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import cryptography
    except ImportError:
        missing.append('cryptography')
    
    try:
        import numpy
    except ImportError:
        missing.append('numpy')
    
    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')
    
    if missing:
        print("Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("◉ SMART-ENCRYPT v1.0 ◉")
    print("Secure Personal Vault")
    print("=" * 30)
    
    if not check_dependencies():
        sys.exit(1)
    
    try:
        from gui import SmartEncryptGUI
        app = SmartEncryptGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n[!] Application interrupted")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()