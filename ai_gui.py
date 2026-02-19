"""AI Assistant GUI Integration for Smart-Encrypt"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import traceback
from ai_assistant import SmartEncryptAI
from ai_model import LightweightCodeModel

class AIAssistantGUI:
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.ai_core = SmartEncryptAI(parent_gui.storage.db_path.replace('notes.db', ''))
        self.ai_model = LightweightCodeModel()
        self.ai_window = None
    
    def show_ai_assistant(self):
        """Show AI Assistant interface"""
        if self.ai_window and self.ai_window.winfo_exists():
            self.ai_window.lift()
            return
        
        self.ai_window = tk.Toplevel(self.parent.root)
        self.ai_window.title("Smart-Encrypt AI Core")
        self.ai_window.geometry("900x700")
        self.ai_window.configure(bg='#000000')
        self.ai_window.transient(self.parent.root)
        
        # Header
        tk.Label(self.ai_window, text="◢ SMART-ENCRYPT AI CORE ◣", 
                bg='#000000', fg='#00ff41', font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.ai_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat Tab
        chat_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(chat_frame, text='💬 AI Chat')
        self._create_chat_tab(chat_frame)
        
        # Code Assistant Tab
        assistant_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(assistant_frame, text='🤖 Code Assistant')
        self._create_assistant_tab(assistant_frame)
        
        # Error Debugger Tab
        debugger_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(debugger_frame, text='🐛 Error Debugger')
        self._create_debugger_tab(debugger_frame)
        
        # Code Search Tab
        search_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(search_frame, text='🔍 Code Search')
        self._create_search_tab(search_frame)
    
    def _create_chat_tab(self, parent):
        """Create AI chat tab"""
        # Chat history area
        chat_frame = tk.Frame(parent, bg='#000000')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(chat_frame, text="AI Chat - Ask anything about Smart-Encrypt:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, bg='#001100', fg='#00ff41', font=('Courier', 10),
            height=25, wrap=tk.WORD, state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Input area
        input_frame = tk.Frame(parent, bg='#000000')
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.chat_entry = tk.Entry(input_frame, bg='#001100', fg='#00ff41',
                                  font=('Courier', 11))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.chat_entry.bind('<Return>', lambda e: self._send_chat_message())
        
        tk.Button(input_frame, text="💬 SEND", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=self._send_chat_message).pack(side=tk.RIGHT)
        
        # Quick actions
        quick_frame = tk.Frame(parent, bg='#000000')
        quick_frame.pack(fill=tk.X, padx=20, pady=5)
        
        quick_actions = [
            "How to add new encryption method?",
            "Explain the GUI structure",
            "Show me database schema",
            "Generate OSINT search code",
            "Create new security feature"
        ]
        
        for action in quick_actions:
            btn = tk.Button(quick_frame, text=action, bg='#001100', fg='#666666',
                           font=('Courier', 8), relief='flat',
                           command=lambda a=action: self._quick_chat(a))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Initialize chat
        self._add_chat_message("AI", "Hello! I'm Smart-Encrypt AI. Ask me anything about the codebase, request new features, or get coding help.")
    
    def _send_chat_message(self):
        """Send chat message to AI"""
        message = self.chat_entry.get().strip()
        if not message:
            return
        
        self.chat_entry.delete(0, tk.END)
        self._add_chat_message("You", message)
        
        # Show typing indicator
        self._add_chat_message("AI", "🤖 Thinking...")
        
        def process_chat():
            try:
                # Real conversational AI responses
                message_lower = message.lower()
                
                # Greetings
                if any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste']):
                    reply = "Hello! I'm Smart-Encrypt AI. I can help you with coding, debugging, and new features. What would you like to work on?"
                
                # Questions about capabilities
                elif any(word in message_lower for word in ['what can you do', 'help me', 'capabilities']):
                    reply = "I can help you with:\n\n💻 Code Generation - Ask me to create functions, classes, or features\n🐛 Bug Fixing - Share errors and I'll suggest solutions\n📁 Architecture - Explain how Smart-Encrypt works\n🔍 OSINT Tools - Help with investigation features\n🔒 Security - Encryption and protection methods\n\nJust ask me anything in natural language!"
                
                # Code generation requests
                elif any(word in message_lower for word in ['add', 'create', 'make', 'build', 'generate']):
                    if 'button' in message_lower:
                        reply = f"I'll create a button for you! Here's the code:\n\n```python\ndef add_custom_button(self, parent, text='{message.split()[-1] if len(message.split()) > 2 else 'New Button'}'):\n    btn = tk.Button(parent, text=text,\n                   bg='#003300', fg='#00ff41',\n                   font=('Courier', 10, 'bold'))\n    btn.pack(pady=5)\n    return btn\n```\n\nThis creates a themed button that matches Smart-Encrypt's style. Need any modifications?"
                    
                    elif any(word in message_lower for word in ['function', 'method', 'def']):
                        reply = f"Here's a function template based on your request:\n\n```python\ndef {message.split()[-1] if message.split()[-1].isalpha() else 'new_function'}(self, *args, **kwargs):\n    \"\"\"Function for: {message}\"\"\"\n    try:\n        # Your implementation here\n        result = self.process_data(args)\n        return result\n    except Exception as e:\n        print(f'Error: {e}')\n        return None\n```\n\nWant me to customize this further?"
                    
                    elif 'osint' in message_lower:
                        reply = "Great idea! Here's an OSINT function:\n\n```python\ndef osint_search(self, target, platforms=['instagram', 'facebook']):\n    \"\"\"Search target across platforms\"\"\"\n    results = []\n    for platform in platforms:\n        try:\n            url = f'https://{platform}.com/{target}'\n            # Add your scraping logic\n            results.append({'platform': platform, 'url': url})\n        except Exception as e:\n            continue\n    return results\n```\n\nThis is a starting point. What specific platforms do you want to target?"
                    
                    else:
                        reply = f"I understand you want to create something! Based on '{message}', here's a general template:\n\n```python\nclass NewFeature:\n    def __init__(self):\n        self.name = '{message.replace('create', '').replace('make', '').strip()}'\n        self.active = True\n    \n    def execute(self):\n        \"\"\"Execute the feature\"\"\"\n        try:\n            # Implementation goes here\n            return True\n        except Exception as e:\n            print(f'Error in {self.name}: {e}')\n            return False\n```\n\nTell me more details about what you want to build!"
                
                # Debugging and fixes
                elif any(word in message_lower for word in ['error', 'fix', 'debug', 'problem', 'issue']):
                    reply = f"I can help debug that! Common solutions for '{message}':\n\n🔧 **Quick Fixes:**\n• Check imports and dependencies\n• Verify file paths and permissions\n• Look for typos in variable names\n• Ensure proper indentation\n\n📝 **Share the error traceback** and I'll give you a specific solution!\n\nWhat exactly is the error message you're seeing?"
                
                # Explanations
                elif any(word in message_lower for word in ['how', 'what', 'explain', 'show me']):
                    if 'work' in message_lower or 'structure' in message_lower:
                        reply = "Smart-Encrypt works like this:\n\n📱 **Core Components:**\n• GUI (gui.py) - Main interface with neon theme\n• Encryption (encryption.py) - AES-256 Fernet encryption\n• Storage (storage.py) - SQLite with encrypted fields\n• OSINT (osint_image.py) - Image analysis across 35+ platforms\n\n🔒 **Security Flow:**\n1. Master password → PBKDF2 key derivation\n2. Individual Fernet keys for each entry\n3. Auto-lock after inactivity\n\nWhat specific part interests you most?"
                    else:
                        reply = f"Let me explain '{message}':\n\nSmart-Encrypt is a cybersecurity tool with:\n• Military-grade encryption\n• OSINT image analysis\n• Dark web tools\n• AI-powered assistance\n• Cross-platform support\n\nWhich feature would you like me to dive deeper into?"
                
                # Personal questions
                elif any(word in message_lower for word in ['who are you', 'what are you', 'your name']):
                    reply = "I'm Smart-Encrypt AI, your coding assistant! I'm built specifically for this cybersecurity application. I can:\n\n• Generate code in Python\n• Help with GUI development\n• Debug errors and issues\n• Explain the codebase\n• Suggest new features\n\nI'm here to make your development faster and easier!"
                
                # Default conversational response
                else:
                    reply = f"Interesting! You said: '{message}'\n\nI'm not sure exactly what you need, but I can help with:\n\n💻 **Coding**: 'Create a login function'\n🔍 **OSINT**: 'Add Twitter scraping'\n🐛 **Debugging**: 'Fix this error: [paste error]'\n📁 **Architecture**: 'How does encryption work?'\n\nCould you be more specific about what you'd like me to help with?"
                
                self.ai_window.after(0, lambda: self._replace_last_message("AI", reply))
                
            except Exception as e:
                error_reply = f"Oops! I had a small hiccup: {str(e)}\n\nBut I'm still here to help! Try asking me:\n• 'Create a new function'\n• 'How does Smart-Encrypt work?'\n• 'Fix my code error'\n• 'Add OSINT feature'"
                self.ai_window.after(0, lambda: self._replace_last_message("AI", error_reply))
        
        threading.Thread(target=process_chat, daemon=True).start()
    
    def _quick_chat(self, message):
        """Send quick chat message"""
        self.chat_entry.delete(0, tk.END)
        self.chat_entry.insert(0, message)
        self._send_chat_message()
    
    def _add_chat_message(self, sender, message):
        """Add message to chat display"""
        self.chat_display.config(state='normal')
        
        # Add timestamp
        import time
        timestamp = time.strftime("%H:%M")
        
        if sender == "You":
            self.chat_display.insert(tk.END, f"[{timestamp}] 👤 You: {message}\n\n")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] 🤖 AI: {message}\n\n")
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def _replace_last_message(self, sender, message):
        """Replace the last message (for updating typing indicator)"""
        self.chat_display.config(state='normal')
        
        # Get all text and find last AI message
        content = self.chat_display.get(1.0, tk.END)
        lines = content.split('\n')
        
        # Remove last AI message lines
        while lines and not lines[-1].strip():
            lines.pop()
        
        if lines and '🤖 AI:' in lines[-1]:
            lines.pop()
        
        # Rebuild content without last AI message
        new_content = '\n'.join(lines)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.insert(1.0, new_content)
        
        # Add new message
        import time
        timestamp = time.strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] 🤖 AI: {message}\n\n")
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def _create_assistant_tab(self, parent):
        """Create code assistant tab"""
        # Input area
        input_frame = tk.Frame(parent, bg='#000000')
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="Natural Language Request:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        self.request_entry = tk.Entry(input_frame, bg='#001100', fg='#00ff41',
                                     font=('Courier', 11), width=80)
        self.request_entry.pack(fill=tk.X, pady=5)
        self.request_entry.bind('<Return>', lambda e: self._process_request())
        
        # Examples
        examples_frame = tk.Frame(parent, bg='#000000')
        examples_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(examples_frame, text="Examples:", 
                bg='#000000', fg='#666666', font=('Courier', 9)).pack(anchor='w')
        
        examples = [
            "Add a new button to the GUI",
            "Create encryption function",
            "Fix database connection error",
            "Add audio feedback to button click"
        ]
        
        for example in examples:
            btn = tk.Button(examples_frame, text=example, bg='#001100', fg='#666666',
                           font=('Courier', 8), relief='flat',
                           command=lambda ex=example: self.request_entry.insert(0, ex))
            btn.pack(anchor='w', pady=1)
        
        # Response area
        response_frame = tk.Frame(parent, bg='#000000')
        response_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(response_frame, text="AI Response:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        self.response_text = scrolledtext.ScrolledText(
            response_frame, bg='#001100', fg='#00ff41', font=('Courier', 10),
            height=20, wrap=tk.WORD
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(parent, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="🤖 PROCESS REQUEST", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=self._process_request).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📋 COPY CODE", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=self._copy_code).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🔄 CLEAR", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=self._clear_response).pack(side=tk.RIGHT, padx=5)
    
    def _create_debugger_tab(self, parent):
        """Create error debugger tab"""
        # Error input
        error_frame = tk.Frame(parent, bg='#000000')
        error_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(error_frame, text="Paste Error Traceback:", 
                bg='#000000', fg='#ff0040', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        self.error_text = scrolledtext.ScrolledText(
            error_frame, bg='#110000', fg='#ff0040', font=('Courier', 9),
            height=8, wrap=tk.WORD
        )
        self.error_text.pack(fill=tk.X, pady=5)
        
        # Fix suggestions
        fix_frame = tk.Frame(parent, bg='#000000')
        fix_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(fix_frame, text="Suggested Fixes:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        self.fix_text = scrolledtext.ScrolledText(
            fix_frame, bg='#001100', fg='#00ff41', font=('Courier', 10),
            height=15, wrap=tk.WORD
        )
        self.fix_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Debug button
        tk.Button(parent, text="🐛 ANALYZE ERROR", bg='#330000', fg='#ff0040',
                 font=('Courier', 12, 'bold'), command=self._analyze_error).pack(pady=10)
    
    def _create_search_tab(self, parent):
        """Create code search tab"""
        # Search input
        search_frame = tk.Frame(parent, bg='#000000')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="Search Code:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        search_input_frame = tk.Frame(search_frame, bg='#000000')
        search_input_frame.pack(fill=tk.X, pady=5)
        
        self.search_entry = tk.Entry(search_input_frame, bg='#001100', fg='#00ff41',
                                    font=('Courier', 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self._search_code())
        
        tk.Button(search_input_frame, text="🔍 SEARCH", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=self._search_code).pack(side=tk.RIGHT)
        
        # Results area
        results_frame = tk.Frame(parent, bg='#000000')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="Search Results:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
        
        # Results treeview
        columns = ('Function', 'File', 'Line', 'Class')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings',
                                        style='Dark.Treeview', height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=f'◢ {col.upper()} ◣')
        
        self.results_tree.column('Function', width=200)
        self.results_tree.column('File', width=150)
        self.results_tree.column('Line', width=80)
        self.results_tree.column('Class', width=150)
        
        self.results_tree.pack(fill=tk.X, pady=5)
        self.results_tree.bind('<<TreeviewSelect>>', self._on_result_select)
        
        # Code preview
        tk.Label(results_frame, text="Code Preview:", 
                bg='#000000', fg='#00ff41', font=('Courier', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        
        self.preview_text = scrolledtext.ScrolledText(
            results_frame, bg='#001100', fg='#00ff41', font=('Courier', 9),
            height=12, wrap=tk.NONE
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def _process_request(self):
        """Process user request with AI"""
        request = self.request_entry.get().strip()
        if not request:
            return
        
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, "🤖 Processing request...\n\n")
        self.response_text.update()
        
        def process_async():
            try:
                # Use lightweight model for better code generation
                intent = self.ai_model.analyze_intent(request)
                
                if intent['confidence'] > 0.5:
                    # Use lightweight model
                    generated_code = self.ai_model.generate_code(intent)
                    response = {
                        'type': 'code_generation',
                        'code': generated_code,
                        'analysis': {
                            'intent': intent['action'],
                            'category': intent['category'] or 'general',
                            'keywords': [intent['component_type']] if intent['component_type'] else [],
                            'confidence': intent['confidence']
                        }
                    }
                else:
                    # Fallback to original AI core
                    response = self.ai_core.process_request(request)
                
                self.ai_window.after(0, lambda: self._display_response(response))
                
            except Exception as e:
                error_msg = f"AI Error: {str(e)}\n{traceback.format_exc()}"
                self.ai_window.after(0, lambda: self._display_error(error_msg))
        
        threading.Thread(target=process_async, daemon=True).start()
    
    def _display_response(self, response):
        """Display AI response"""
        self.response_text.delete(1.0, tk.END)
        
        if response['type'] == 'code_generation':
            analysis = response['analysis']
            self.response_text.insert(tk.END, f"🎯 Intent: {analysis['intent'].upper()}\n")
            self.response_text.insert(tk.END, f"📂 Category: {analysis['category'].upper()}\n")
            self.response_text.insert(tk.END, f"🔑 Keywords: {', '.join(analysis['keywords'])}\n")
            if 'confidence' in analysis:
                self.response_text.insert(tk.END, f"🎯 Confidence: {analysis['confidence']:.1%}\n")
            self.response_text.insert(tk.END, "\n")
            self.response_text.insert(tk.END, "📝 Generated Code:\n")
            self.response_text.insert(tk.END, "=" * 50 + "\n")
            self.response_text.insert(tk.END, response['code'])
            
        elif response['type'] == 'search_results':
            results = response['results']
            self.response_text.insert(tk.END, f"🔍 Found {len(results)} matching code snippets:\n\n")
            
            for i, result in enumerate(results, 1):
                self.response_text.insert(tk.END, f"{i}. {result['function']}")
                if result['class']:
                    self.response_text.insert(tk.END, f" (in {result['class']})")
                self.response_text.insert(tk.END, f" - {result['file']}:{result['line']}\n")
                self.response_text.insert(tk.END, "-" * 40 + "\n")
                self.response_text.insert(tk.END, result['code'][:200] + "...\n\n")
    
    def _display_error(self, error_msg):
        """Display error message"""
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, "❌ Error occurred:\n\n")
        self.response_text.insert(tk.END, error_msg)
    
    def _analyze_error(self):
        """Analyze error and suggest fixes"""
        error_traceback = self.error_text.get(1.0, tk.END).strip()
        if not error_traceback:
            return
        
        self.fix_text.delete(1.0, tk.END)
        self.fix_text.insert(tk.END, "🔧 Analyzing error...\n\n")
        self.fix_text.update()
        
        try:
            fix_suggestion = self.ai_core.suggest_fix(error_traceback)
            self.fix_text.delete(1.0, tk.END)
            self.fix_text.insert(tk.END, "🔧 Suggested Fix:\n")
            self.fix_text.insert(tk.END, "=" * 40 + "\n")
            self.fix_text.insert(tk.END, fix_suggestion)
            
        except Exception as e:
            self.fix_text.delete(1.0, tk.END)
            self.fix_text.insert(tk.END, f"❌ Error analyzing: {str(e)}")
    
    def _search_code(self):
        """Search code in project"""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.preview_text.delete(1.0, tk.END)
        
        try:
            results = self.ai_core.search_code(query)
            
            for result in results:
                self.results_tree.insert('', tk.END, values=(
                    result['function'],
                    result['file'],
                    result['line'],
                    result['class'] or ''
                ), tags=(result,))
                
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search: {str(e)}")
    
    def _on_result_select(self, event):
        """Handle result selection"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        result = item['tags'][0] if item['tags'] else None
        
        if result and isinstance(result, dict):
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"File: {result['file']}\n")
            self.preview_text.insert(tk.END, f"Function: {result['function']}\n")
            if result['class']:
                self.preview_text.insert(tk.END, f"Class: {result['class']}\n")
            self.preview_text.insert(tk.END, f"Line: {result['line']}\n")
            self.preview_text.insert(tk.END, "=" * 50 + "\n")
            self.preview_text.insert(tk.END, result['code'])
    
    def _copy_code(self):
        """Copy generated code to clipboard"""
        code = self.response_text.get(1.0, tk.END)
        if code.strip():
            self.ai_window.clipboard_clear()
            self.ai_window.clipboard_append(code)
            messagebox.showinfo("Copied", "Code copied to clipboard!")
    
    def _clear_response(self):
        """Clear response area"""
        self.response_text.delete(1.0, tk.END)
        self.request_entry.delete(0, tk.END)
    
    def add_ai_button(self, parent_frame):
        """Add AI assistant button to main interface"""
        ai_btn = tk.Button(
            parent_frame,
            text="🤖 AI Assistant",
            bg='#003300',
            fg='#00ff41',
            font=('Courier', 9),
            command=self.show_ai_assistant,
            width=20
        )
        ai_btn.pack(pady=2, padx=5)
        
        # Add hover effects
        def on_enter(e):
            ai_btn.configure(bg='#006600')
        
        def on_leave(e):
            ai_btn.configure(bg='#003300')
        
        ai_btn.bind('<Enter>', on_enter)
        ai_btn.bind('<Leave>', on_leave)
        
        return ai_btn