#!/usr/bin/env python3
"""
Smart-Encrypt with Aaliya AI
Production launcher with AI model setup
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import threading

def check_dependencies():
    """Check and install required dependencies"""
    try:
        import cryptography
        import numpy
        import requests
        import PIL
        # gpt4all is optional - will use fallback if not available
        try:
            import gpt4all
        except ImportError:
            print("Note: gpt4all not available, using fallback mode")
        return True
    except ImportError as e:
        missing = str(e).split("'")[1]
        print(f"Missing required module: {missing}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_directories():
    """Setup required directories"""
    base_dir = os.path.expanduser("~/.smart_encrypt")
    dirs = [
        base_dir,
        os.path.join(base_dir, "models"),
        os.path.join(base_dir, "osint_results")
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

def show_splash():
    """Show splash screen while loading"""
    splash = tk.Tk()
    splash.title("Smart-Encrypt")
    splash.geometry("400x300")
    splash.configure(bg='#000000')
    splash.resizable(False, False)
    
    # Center the window
    splash.eval('tk::PlaceWindow . center')
    
    # Logo and title
    tk.Label(splash, text="◉ SMART-ENCRYPT ◉", 
            bg='#000000', fg='#00ff41', 
            font=('Courier', 20, 'bold')).pack(pady=30)
    
    tk.Label(splash, text="with", 
            bg='#000000', fg='#ffffff', 
            font=('Arial', 12)).pack()
    
    tk.Label(splash, text="💜 Aaliya AI", 
            bg='#000000', fg='#ff69b4', 
            font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Loading message
    loading_label = tk.Label(splash, text="Initializing...", 
                           bg='#000000', fg='#00ff41', 
                           font=('Courier', 12))
    loading_label.pack(pady=20)
    
    # Progress bar simulation
    progress_frame = tk.Frame(splash, bg='#000000')
    progress_frame.pack(pady=10)
    
    progress_bar = tk.Frame(progress_frame, bg='#003300', width=300, height=20)
    progress_bar.pack()
    
    progress_fill = tk.Frame(progress_bar, bg='#00ff41', height=20)
    progress_fill.place(x=0, y=0, width=0)
    
    def animate_progress():
        for i in range(101):
            progress_fill.configure(width=i * 3)
            if i < 30:
                loading_label.configure(text="Checking dependencies...")
            elif i < 60:
                loading_label.configure(text="Setting up directories...")
            elif i < 90:
                loading_label.configure(text="Loading Aaliya AI...")
            else:
                loading_label.configure(text="Ready! 💜")
            
            splash.update()
            threading.Event().wait(0.02)
        
        threading.Event().wait(1)
        splash.destroy()
    
    # Start animation
    threading.Thread(target=animate_progress, daemon=True).start()
    
    splash.mainloop()

def main():
    """Main application launcher"""
    print("◉ SMART-ENCRYPT v1.0 with Aaliya AI ◉")
    print("Secure Personal Vault with AI Assistant")
    print("=" * 40)
    
    # Show splash screen
    show_splash()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Setup directories
    setup_directories()
    
    try:
        # Import and run main application
        from app import main as app_main
        app_main()
        
    except Exception as e:
        messagebox.showerror("Application Error", 
                           f"Failed to start Smart-Encrypt:\n{str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()