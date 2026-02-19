#!/usr/bin/env python3
"""
Aaliya GUI - Beautiful chat interface for Aaliya AI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
from aaliya_ai import AaliyaAI

class AaliyaGUI:
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.aaliya = AaliyaAI()
        self.chat_window = None
        self.chat_display = None
        self.chat_entry = None
        self.status_label = None
        self.model_loading = False
        
        # Aaliya's color scheme
        self.colors = {
            'bg': '#1a0d1a',           # Dark purple background
            'chat_bg': '#2d1b2d',      # Chat area background
            'user_bubble': '#4a4a4a',  # User message bubble
            'aaliya_bubble': '#663399', # Aaliya message bubble
            'text': '#ffffff',         # White text
            'accent': '#ff69b4',       # Pink accent
            'online': '#00ff00',       # Online status
            'offline': '#ff4444'       # Offline status
        }
    
    def show_aaliya_chat(self):
        """Show Aaliya chat window"""
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return
        
        self.chat_window = tk.Toplevel(self.parent.root)
        self.chat_window.title("💜 Aaliya - Your AI Assistant")
        self.chat_window.geometry("800x600")
        self.chat_window.configure(bg=self.colors['bg'])
        self.chat_window.transient(self.parent.root)
        
        self._create_chat_interface()
        self._load_chat_history()
        
        # Auto-load model in background
        if not self.aaliya.model_loaded:
            self._load_model_async()
    
    def _create_chat_interface(self):
        """Create the chat interface"""
        # Header with status
        header_frame = tk.Frame(self.chat_window, bg=self.colors['bg'], height=60)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        # Aaliya title and avatar
        title_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side='left', fill='y')
        
        # Avatar (simple emoji for now)
        avatar_label = tk.Label(title_frame, text="👩‍💻", font=('Arial', 24),
                               bg=self.colors['bg'], fg=self.colors['accent'])
        avatar_label.pack(side='left', padx=(0, 10))
        
        # Title and subtitle
        name_frame = tk.Frame(title_frame, bg=self.colors['bg'])
        name_frame.pack(side='left', fill='y')
        
        tk.Label(name_frame, text="Aaliya", font=('Arial', 16, 'bold'),
                bg=self.colors['bg'], fg=self.colors['accent']).pack(anchor='w')
        tk.Label(name_frame, text="Your Personal AI Assistant", font=('Arial', 10),
                bg=self.colors['bg'], fg=self.colors['text']).pack(anchor='w')
        
        # Status indicator
        status_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        status_frame.pack(side='right', fill='y')
        
        self.status_label = tk.Label(status_frame, text="🔴 Loading...", 
                                    font=('Arial', 12, 'bold'),
                                    bg=self.colors['bg'], fg=self.colors['offline'])
        self.status_label.pack(side='right', pady=10)
        
        # Chat display area
        chat_frame = tk.Frame(self.chat_window, bg=self.colors['chat_bg'])
        chat_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Custom scrollable chat area
        self.chat_canvas = tk.Canvas(chat_frame, bg=self.colors['chat_bg'], 
                                    highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(chat_frame, orient="vertical", 
                                          command=self.chat_canvas.yview,
                                          bg=self.colors['bg'])
        self.chat_frame_inner = tk.Frame(self.chat_canvas, bg=self.colors['chat_bg'])
        
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_canvas.create_window((0, 0), window=self.chat_frame_inner, anchor="nw")
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def on_mousewheel(event):
            self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.chat_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Input area
        input_frame = tk.Frame(self.chat_window, bg=self.colors['bg'], height=80)
        input_frame.pack(fill='x', padx=10, pady=5)
        input_frame.pack_propagate(False)
        
        # Chat input
        self.chat_entry = tk.Text(input_frame, height=3, wrap='word',
                                 bg=self.colors['user_bubble'], fg=self.colors['text'],
                                 font=('Arial', 11), relief='flat', bd=5)
        self.chat_entry.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.chat_entry.bind('<Return>', self._on_enter_key)
        
        # Send button
        send_btn = tk.Button(input_frame, text="💜\nSend", 
                           command=self._send_message,
                           bg=self.colors['aaliya_bubble'], fg=self.colors['text'],
                           font=('Arial', 10, 'bold'), relief='flat', bd=0,
                           width=8, height=3)
        send_btn.pack(side='right')
        
        # Control buttons
        control_frame = tk.Frame(self.chat_window, bg=self.colors['bg'])
        control_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(control_frame, text="🗑️ Clear Chat", command=self._clear_chat,
                 bg=self.colors['user_bubble'], fg=self.colors['text'],
                 font=('Arial', 9), relief='flat').pack(side='left', padx=5)
        
        tk.Button(control_frame, text="💾 Load Model", command=self._load_model_async,
                 bg=self.colors['aaliya_bubble'], fg=self.colors['text'],
                 font=('Arial', 9), relief='flat').pack(side='left', padx=5)
        
        tk.Button(control_frame, text="🔄 Unload Model", command=self._unload_model,
                 bg=self.colors['user_bubble'], fg=self.colors['text'],
                 font=('Arial', 9), relief='flat').pack(side='left', padx=5)
    
    def _on_enter_key(self, event):
        """Handle Enter key press"""
        if event.state & 0x4:  # Ctrl+Enter for new line
            return
        else:  # Enter to send
            self._send_message()
            return "break"
    
    def _send_message(self):
        """Send user message to Aaliya"""
        message = self.chat_entry.get(1.0, 'end-1c').strip()
        if not message:
            return
        
        self.chat_entry.delete(1.0, 'end')
        
        # Add user message
        self._add_message(message, is_user=True)
        
        # Show typing indicator
        typing_frame = self._add_message("💭 Aaliya is thinking...", is_user=False, is_typing=True)
        
        # Generate response in background
        def generate_response():
            try:
                response = self.aaliya.generate_response(message)
                self.aaliya.save_chat(message, response)
                
                # Update UI in main thread
                self.chat_window.after(0, lambda: self._replace_typing_with_response(typing_frame, response))
                
            except Exception as e:
                error_response = f"Sorry, I encountered an error: {str(e)} 💜"
                self.chat_window.after(0, lambda: self._replace_typing_with_response(typing_frame, error_response))
        
        threading.Thread(target=generate_response, daemon=True).start()
    
    def _add_message(self, text, is_user=False, is_typing=False):
        """Add message bubble to chat"""
        # Message container
        msg_container = tk.Frame(self.chat_frame_inner, bg=self.colors['chat_bg'])
        msg_container.pack(fill='x', padx=10, pady=5)
        
        if is_user:
            # User message (right side)
            bubble_frame = tk.Frame(msg_container, bg=self.colors['chat_bg'])
            bubble_frame.pack(anchor='e')
            
            bubble = tk.Label(bubble_frame, text=text, 
                            bg=self.colors['user_bubble'], fg=self.colors['text'],
                            font=('Arial', 10), wraplength=400, justify='left',
                            padx=15, pady=10, relief='flat')
            bubble.pack(side='right')
            
            # User label
            tk.Label(bubble_frame, text="You 👤", 
                    bg=self.colors['chat_bg'], fg=self.colors['text'],
                    font=('Arial', 8)).pack(side='right', padx=(0, 5))
        else:
            # Aaliya message (left side)
            bubble_frame = tk.Frame(msg_container, bg=self.colors['chat_bg'])
            bubble_frame.pack(anchor='w')
            
            # Aaliya label and avatar
            tk.Label(bubble_frame, text="👩‍💻 Aaliya", 
                    bg=self.colors['chat_bg'], fg=self.colors['accent'],
                    font=('Arial', 8, 'bold')).pack(side='left', padx=(5, 0))
            
            bubble = tk.Label(bubble_frame, text=text,
                            bg=self.colors['aaliya_bubble'], fg=self.colors['text'],
                            font=('Arial', 10), wraplength=400, justify='left',
                            padx=15, pady=10, relief='flat')
            bubble.pack(side='left')
        
        # Auto-scroll to bottom
        self.chat_window.after(100, self._scroll_to_bottom)
        
        return msg_container if is_typing else None
    
    def _replace_typing_with_response(self, typing_frame, response):
        """Replace typing indicator with actual response"""
        if typing_frame:
            typing_frame.destroy()
        self._add_message(response, is_user=False)
    
    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        self.chat_frame_inner.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)
    
    def _load_chat_history(self):
        """Load previous chat history"""
        history = self.aaliya.get_chat_history(20)  # Last 20 messages
        
        if not history:
            # Welcome message
            welcome = "Hello! I'm Aaliya, your personal AI assistant! 💜\n\nI'm here to help you with:\n• Smart-Encrypt development\n• Code generation and debugging\n• Friendly conversation\n\nHow can I assist you today? 😊"
            self._add_message(welcome, is_user=False)
        else:
            for user_msg, aaliya_msg, timestamp in history:
                self._add_message(user_msg, is_user=True)
                self._add_message(aaliya_msg, is_user=False)
    
    def _clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear all chat history?"):
            # Clear GUI
            for widget in self.chat_frame_inner.winfo_children():
                widget.destroy()
            
            # Clear database
            self.aaliya.clear_history()
            
            # Add welcome message
            welcome = "Chat cleared! I'm still here to help you. What would you like to work on? 💜"
            self._add_message(welcome, is_user=False)
    
    def _load_model_async(self):
        """Load AI model in background"""
        if self.model_loading or self.aaliya.model_loaded:
            return
        
        self.model_loading = True
        self.status_label.configure(text="🟡 Loading Model...", fg='#ffaa00')
        
        def load_model():
            try:
                # Try to download and load model
                model_path = os.path.join(self.aaliya.models_dir, self.aaliya.model_name)
                if not os.path.exists(model_path):
                    self.chat_window.after(0, lambda: self.status_label.configure(text="⬇️ Downloading...", fg='#ffaa00'))
                    
                    def progress_callback(message, progress):
                        self.chat_window.after(0, lambda: self.status_label.configure(text=f"⬇️ {progress:.0f}%", fg='#ffaa00'))
                    
                    success = self.aaliya.download_model(progress_callback)
                    if not success:
                        self.chat_window.after(0, lambda: self.status_label.configure(text="⚠️ Fallback Mode", fg='#ffaa00'))
                        self.model_loading = False
                        return
                
                # Load the model
                success = self.aaliya.load_model()
                
                if success and self.aaliya.model:
                    self.chat_window.after(0, lambda: self.status_label.configure(text="🟢 AI Online", fg=self.colors['online']))
                    self.chat_window.after(0, lambda: self._add_message("I'm now fully loaded with AI model! Ready to help! 💜✨", is_user=False))
                else:
                    self.chat_window.after(0, lambda: self.status_label.configure(text="🟡 Fallback Mode", fg='#ffaa00'))
                    self.chat_window.after(0, lambda: self._add_message("I'm running in fallback mode but still ready to help! 💜", is_user=False))
                
            except Exception as e:
                self.chat_window.after(0, lambda: self.status_label.configure(text="❌ Error", fg=self.colors['offline']))
                self.chat_window.after(0, lambda: self._add_message(f"Had trouble loading, but I'm still here! Error: {str(e)} 💜", is_user=False))
            
            finally:
                self.model_loading = False
        
        threading.Thread(target=load_model, daemon=True).start()
    
    def _unload_model(self):
        """Unload model to free memory"""
        self.aaliya.unload_model()
        self.status_label.configure(text="🔴 Offline", fg=self.colors['offline'])
        self._add_message("Model unloaded to save memory. I can still chat in fallback mode! 💜", is_user=False)
    
    def add_aaliya_button(self, parent_frame):
        """Add Aaliya button to main interface"""
        aaliya_btn = tk.Button(
            parent_frame,
            text="💜 Aaliya AI",
            bg='#663399',
            fg='white',
            font=('Arial', 9, 'bold'),
            command=self.show_aaliya_chat,
            width=20,
            relief='flat'
        )
        aaliya_btn.pack(pady=2, padx=5)
        
        # Hover effects
        def on_enter(e):
            aaliya_btn.configure(bg='#8844bb')
        
        def on_leave(e):
            aaliya_btn.configure(bg='#663399')
        
        aaliya_btn.bind('<Enter>', on_enter)
        aaliya_btn.bind('<Leave>', on_leave)
        
        return aaliya_btn