"""GUI module for Smart-Encrypt"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import time
from storage import StorageManager
# from sound import SoundManager  # Removed
from utils import AutoLockManager
from darkweb_tools import DarkWebTools
from ai_engine import AIEngine
from secure_communication import SecureCommunication
from data_visualization import DataVisualizer
from audio_visual import AudioVisualFeedback
from ui_browser import BrowserUI
from ui_honeypot import HoneypotUI
from ai_gui import AIAssistantGUI
from aaliya_gui import AaliyaGUI
from ui_osint_image import OSINTImageGUI


DEFAULT_AUTOLOCK_MINUTES = 5
DEFAULT_THEME = "neon-green"
ENABLE_SOUND_BY_DEFAULT = True

class SmartEncryptGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.storage = StorageManager()
        # self.sound = SoundManager()  # Removed
        self.auto_lock = AutoLockManager(DEFAULT_AUTOLOCK_MINUTES, self.lock_app)
        self.darkweb = DarkWebTools()
        self.ai_engine = AIEngine()
        self.secure_comm = None
        self.visualizer = DataVisualizer(self.root)
        self.audio_visual = AudioVisualFeedback(self.root)
        self.browser_ui = None
        self.honeypot_ui = None
        self.is_locked = True
        self.current_theme = DEFAULT_THEME
        
        self.setup_window()
        self.setup_styles()
        self.load_settings()
        
        if self.storage.is_first_run():
            self.setup_master_password()
        else:
            self.show_login()
    
    def setup_window(self):
        self.root.title("Smart-Encrypt")
        self.root.geometry("1200x800")
        self.root.configure(bg='#000000')
        
        # Bind activity events
        self.root.bind('<Motion>', lambda e: self.auto_lock.update_activity())
        self.root.bind('<Key>', lambda e: self.auto_lock.update_activity())
        self.root.bind('<Button>', lambda e: self.auto_lock.update_activity())
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        themes = {
            "neon-green": {
                'bg': '#000000', 'fg': '#00ff41', 'select': '#001100', 'accent': '#40ff80'
            },
            "neon-purple": {
                'bg': '#000000', 'fg': '#ff00ff', 'select': '#110011', 'accent': '#ff80ff'
            },
            "monochrome": {
                'bg': '#000000', 'fg': '#ffffff', 'select': '#333333', 'accent': '#cccccc'
            }
        }
        
        theme = themes.get(self.current_theme, themes["neon-green"])
        
        style.configure('Dark.TFrame', background=theme['bg'])
        style.configure('Dark.TLabel', background=theme['bg'], foreground=theme['fg'], 
                       font=('Courier', 10))
        style.configure('Dark.TButton', background=theme['select'], foreground=theme['fg'],
                       font=('Courier', 9, 'bold'))
        style.configure('Dark.TEntry', background=theme['select'], foreground=theme['fg'],
                       font=('Courier', 10))
        style.configure('Dark.Treeview', background=theme['select'], foreground=theme['fg'],
                       font=('Courier', 9))
        style.configure('Dark.Treeview.Heading', background=theme['bg'], 
                       foreground=theme['accent'], font=('Courier', 10, 'bold'))
    
    def load_settings(self):
        self.current_theme = self.storage.get_setting('theme', DEFAULT_THEME)
        # sound_enabled = self.storage.get_setting('sound_enabled', str(ENABLE_SOUND_BY_DEFAULT))
        # self.sound.set_enabled(sound_enabled.lower() == 'true')  # Removed
        
        timeout = int(self.storage.get_setting('autolock_minutes', str(DEFAULT_AUTOLOCK_MINUTES)))
        self.auto_lock.set_timeout(timeout)
    
    def setup_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Setup Master Password")
        dialog.geometry("500x300")
        dialog.configure(bg='#000000')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="◉ SMART-ENCRYPT INITIALIZATION ◉", 
                bg='#000000', fg='#00ff41', font=('Courier', 16, 'bold')).pack(pady=20)
        
        tk.Label(dialog, text="Create your master password:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12)).pack(pady=10)
        
        password_var = tk.StringVar()
        password_entry = tk.Entry(dialog, textvariable=password_var, show='●',
                                 bg='#001100', fg='#00ff41', font=('Courier', 14),
                                 insertbackground='#00ff41', width=30)
        password_entry.pack(pady=15)
        
        def create_password():
            password = password_var.get()
            if len(password) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters")
                return
            
            self.storage.set_master_password(password)
            self.is_locked = False
            dialog.destroy()
            self.create_main_interface()
            # self.sound.play_startup_chime()  # Removed
        
        tk.Button(dialog, text="◉ CREATE VAULT ◉", bg='#001100', fg='#00ff41',
                 font=('Courier', 12, 'bold'), command=create_password).pack(pady=20)
        
        password_entry.focus()
        password_entry.bind('<Return>', lambda e: create_password())
    
    def show_login(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Unlock Smart-Encrypt")
        dialog.geometry("400x250")
        dialog.configure(bg='#000000')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="◉ VAULT LOCKED ◉", 
                bg='#000000', fg='#ff0040', font=('Courier', 16, 'bold')).pack(pady=20)
        
        tk.Label(dialog, text="Enter master password:", 
                bg='#000000', fg='#00ff41', font=('Courier', 12)).pack(pady=10)
        
        password_var = tk.StringVar()
        password_entry = tk.Entry(dialog, textvariable=password_var, show='●',
                                 bg='#001100', fg='#00ff41', font=('Courier', 14),
                                 insertbackground='#00ff41', width=25)
        password_entry.pack(pady=15)
        
        def unlock():
            password = password_var.get()
            if self.storage.verify_master_password(password):
                self.is_locked = False
                dialog.destroy()
                self.create_main_interface()
                self.auto_lock.start()
                # self.sound.play_startup_chime()  # Removed
            else:
                messagebox.showerror("Error", "Invalid password")
                password_entry.delete(0, tk.END)
        
        tk.Button(dialog, text="◉ UNLOCK ◉", bg='#001100', fg='#00ff41',
                 font=('Courier', 12, 'bold'), command=unlock).pack(pady=15)
        
        password_entry.focus()
        password_entry.bind('<Return>', lambda e: unlock())
    
    def create_main_interface(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#000000')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text="◉ SMART-ENCRYPT VAULT ◉", 
                bg='#000000', fg='#00ff41', font=('Courier', 18, 'bold')).pack(side=tk.LEFT)
        
        tk.Button(header_frame, text="⚠ LOCK NOW", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=self.lock_app).pack(side=tk.RIGHT)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#000000')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar with scrollbar
        sidebar_container = tk.Frame(content_frame, bg='#001100', width=250)
        sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_container.pack_propagate(False)
        
        # Create canvas and scrollbar
        sidebar_canvas = tk.Canvas(sidebar_container, bg='#001100', highlightthickness=0, width=230)
        sidebar_scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", command=sidebar_canvas.yview, bg='#003300')
        sidebar_frame = tk.Frame(sidebar_canvas, bg='#001100')
        
        # Configure scrolling
        def configure_scroll(event):
            sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        
        sidebar_frame.bind("<Configure>", configure_scroll)
        
        # Create window in canvas
        canvas_window = sidebar_canvas.create_window((0, 0), window=sidebar_frame, anchor="nw")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        # Pack canvas and scrollbar
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            sidebar_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event):
            sidebar_canvas.unbind_all("<MouseWheel>")
        
        sidebar_canvas.bind('<Enter>', bind_mousewheel)
        sidebar_canvas.bind('<Leave>', unbind_mousewheel)
        
        # Update canvas window width
        def configure_canvas(event):
            canvas_width = event.width
            sidebar_canvas.itemconfig(canvas_window, width=canvas_width-20)
        
        sidebar_canvas.bind('<Configure>', configure_canvas)
        
        tk.Label(sidebar_frame, text="◢ CATEGORIES ◣", 
                bg='#001100', fg='#00ff41', font=('Courier', 12, 'bold')).pack(pady=10)
        
        self.category_listbox = tk.Listbox(sidebar_frame, bg='#001100', fg='#00ff41',
                                          selectbackground='#003300', font=('Courier', 10),
                                          activestyle='none')
        self.category_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 10))
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Quick actions
        tk.Label(sidebar_frame, text="◢ QUICK ACTIONS ◣", 
                bg='#001100', fg='#00ff41', font=('Courier', 10, 'bold')).pack(pady=(10, 5))
        
        # Initialize UI modules
        self.browser_ui = BrowserUI(self)
        self.honeypot_ui = HoneypotUI(self)
        self.ai_assistant = AIAssistantGUI(self)
        self.aaliya = AaliyaGUI(self)
        self.osint_image = OSINTImageGUI(self.root, {'bg': '#000000', 'fg': '#00ff41', 'accent': '#40ff80', 'entry_bg': '#001100'})

        
        actions = [
            ("+ New Entry", self.new_entry),
            ("🌐 Dark Web", self.show_darkweb_tools),
            ("🤖 AI Tools", self.show_ai_tools),
            ("💬 Secure Chat", self.show_secure_comm),
            ("🔍 Image OSINT", self.show_osint_image),
            ("📈 Dashboard", self.show_dashboard),
            ("⚙ Settings", self.show_settings),
            ("↑ Export", self.export_data),
            ("↓ Import", self.import_data)
        ]
        
        for text, command in actions:
            btn = tk.Button(sidebar_frame, text=text, bg='#003300', fg='#00ff41',
                           font=('Courier', 9), command=command, width=20)
            btn.pack(pady=2, padx=5)
            
            # Add hover effects
            def on_enter(e, button=btn):
                button.configure(bg='#006600')
            
            def on_leave(e, button=btn):
                button.configure(bg='#003300')
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
        
        # Add security features separator
        tk.Label(sidebar_frame, text="◢ SECURITY TOOLS ◣", 
                bg='#001100', fg='#ff0040', font=('Courier', 10, 'bold')).pack(pady=(15, 5))
        
        # Add isolated browser button
        self.browser_ui.add_browser_button(sidebar_frame)
        
        # Add honeypot buttons
        self.honeypot_ui.add_honeypot_button(sidebar_frame)
        self.honeypot_ui.add_file_scanner_button(sidebar_frame)
        
        # Add AI assistant button
        self.ai_assistant.add_ai_button(sidebar_frame)
        
        # Add Aaliya AI button
        self.aaliya.add_aaliya_button(sidebar_frame)
        

        
        # Force canvas update after all widgets added
        self.root.after(100, lambda: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        
        # Main pane
        main_pane = tk.Frame(content_frame, bg='#000000')
        main_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Search
        search_frame = tk.Frame(main_pane, bg='#000000')
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="◉ SEARCH:", bg='#000000', fg='#00ff41',
                font=('Courier', 12, 'bold')).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    bg='#001100', fg='#00ff41', font=('Courier', 11),
                                    insertbackground='#00ff41')
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        tk.Button(search_frame, text="CLR", bg='#330000', fg='#ff0040',
                 font=('Courier', 9), command=self.clear_search).pack(side=tk.RIGHT)
        
        # Entries list
        self.entries_tree = ttk.Treeview(main_pane, columns=('Title', 'Category', 'Date'),
                                        show='headings', style='Dark.Treeview', height=20)
        
        self.entries_tree.heading('Title', text='◢ TITLE ◣')
        self.entries_tree.heading('Category', text='◢ CATEGORY ◣')
        self.entries_tree.heading('Date', text='◢ MODIFIED ◣')
        
        self.entries_tree.column('Title', width=400)
        self.entries_tree.column('Category', width=150)
        self.entries_tree.column('Date', width=120)
        
        self.entries_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.entries_tree.bind('<Double-1>', self.edit_entry)
        
        # Entry buttons
        entry_buttons = tk.Frame(main_pane, bg='#000000')
        entry_buttons.pack(fill=tk.X)
        
        tk.Button(entry_buttons, text="◉ NEW", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=self.new_entry).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(entry_buttons, text="◉ EDIT", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=self.edit_entry).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(entry_buttons, text="◉ DELETE", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=self.delete_entry).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="◉ UNLOCKED | Last Activity: " + time.strftime("%H:%M:%S"))
        status_bar = tk.Label(self.root, textvariable=self.status_var, bg='#001100', fg='#00ff41',
                             font=('Courier', 9), relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.load_categories()
        self.load_entries()
        self.update_status()
    
    def load_categories(self):
        self.category_listbox.delete(0, tk.END)
        categories = self.storage.get_categories()
        for cat in categories:
            self.category_listbox.insert(tk.END, cat['name'])
    
    def load_entries(self, category_id=None):
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        entries = self.storage.get_entries(category_id)
        for entry in entries:
            date_str = entry['updated_at'][:16] if entry['updated_at'] else ''
            self.entries_tree.insert('', tk.END, values=(
                entry['title'][:50] + ('...' if len(entry['title']) > 50 else ''),
                entry['category_name'],
                date_str
            ), tags=(entry['id'],))
    
    def on_category_select(self, event=None):
        selection = self.category_listbox.curselection()
        if selection:
            categories = self.storage.get_categories()
            category_id = categories[selection[0]]['id']
            self.load_entries(category_id)
    
    def on_search(self, event=None):
        query = self.search_var.get()
        if len(query) < 2:
            self.load_entries()
            return
        
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        results = self.storage.search_entries(query)
        for entry in results:
            date_str = entry['updated_at'][:16] if entry['updated_at'] else ''
            self.entries_tree.insert('', tk.END, values=(
                entry['title'][:50] + ('...' if len(entry['title']) > 50 else ''),
                entry['category_name'],
                date_str
            ), tags=(entry['id'],))
    
    def clear_search(self):
        self.search_var.set("")
        self.load_entries()
    
    def new_entry(self):
        self.open_entry_editor()
    
    def edit_entry(self, event=None):
        selection = self.entries_tree.selection()
        if not selection:
            return
        
        entry_id = self.entries_tree.item(selection[0])['tags'][0]
        entries = self.storage.get_entries()
        entry = next((e for e in entries if e['id'] == entry_id), None)
        if entry:
            self.open_entry_editor(entry)
    
    def open_entry_editor(self, entry=None):
        editor = tk.Toplevel(self.root)
        editor.title("Entry Editor")
        editor.geometry("700x600")
        editor.configure(bg='#000000')
        
        tk.Label(editor, text="◢ ENTRY EDITOR ◣", bg='#000000', fg='#00ff41',
                font=('Courier', 14, 'bold')).pack(pady=10)
        
        # Title
        title_frame = tk.Frame(editor, bg='#000000')
        title_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(title_frame, text="Title:", bg='#000000', fg='#00ff41',
                font=('Courier', 10, 'bold')).pack(side=tk.LEFT)
        
        title_var = tk.StringVar(value=entry['title'] if entry else '')
        title_entry = tk.Entry(title_frame, textvariable=title_var, bg='#001100', fg='#00ff41',
                              font=('Courier', 11), insertbackground='#00ff41')
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Category
        cat_frame = tk.Frame(editor, bg='#000000')
        cat_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(cat_frame, text="Category:", bg='#000000', fg='#00ff41',
                font=('Courier', 10, 'bold')).pack(side=tk.LEFT)
        
        category_var = tk.StringVar()
        categories = self.storage.get_categories()
        category_combo = ttk.Combobox(cat_frame, textvariable=category_var,
                                     values=[cat['name'] for cat in categories])
        if entry:
            category_var.set(entry['category_name'])
        category_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Content
        tk.Label(editor, text="Content:", bg='#000000', fg='#00ff41',
                font=('Courier', 10, 'bold')).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        content_text = tk.Text(editor, bg='#001100', fg='#00ff41', font=('Courier', 10),
                              insertbackground='#00ff41', selectbackground='#003300')
        content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        if entry:
            content_text.insert(1.0, entry['content'])
        
        # Buttons
        btn_frame = tk.Frame(editor, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_entry():
            title = title_var.get().strip()
            category_name = category_var.get().strip()
            content = content_text.get(1.0, tk.END).strip()
            
            if not title or not category_name:
                messagebox.showerror("Error", "Title and category are required")
                return
            
            # Find category ID
            category_id = next((cat['id'] for cat in categories if cat['name'] == category_name), None)
            if not category_id:
                category_id = self.storage.add_category(category_name)
            
            if entry:
                # Update existing entry (would need update method in storage)
                pass
            else:
                self.storage.add_entry(category_id, title, content)
            
            editor.destroy()
            self.load_categories()
            self.load_entries()
        
        tk.Button(btn_frame, text="◉ SAVE & ENCRYPT", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=save_entry).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="◉ CANCEL", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=editor.destroy).pack(side=tk.LEFT, padx=(10, 0))
    
    def delete_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Confirm", "Delete this entry permanently?"):
            entry_id = self.entries_tree.item(selection[0])['tags'][0]
            self.storage.delete_entry(entry_id)
            self.load_entries()
    
    def show_darkweb_tools(self):
        """Show dark web tools interface"""
        tools_window = tk.Toplevel(self.root)
        tools_window.title("Dark Web Tools")
        tools_window.geometry("800x600")
        tools_window.configure(bg='#000000')
        
        tk.Label(tools_window, text="◢ DARK WEB TOOLKIT ◣", bg='#000000', fg='#ff0040',
                font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Tor status
        status_frame = tk.Frame(tools_window, bg='#000000')
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tor_status = self.darkweb.check_tor_status()
        status_color = '#00ff41' if tor_status['running'] else '#ff0040'
        status_text = 'ONLINE' if tor_status['running'] else 'OFFLINE'
        
        tk.Label(status_frame, text=f"Tor Status: {status_text}", bg='#000000', fg=status_color,
                font=('Courier', 12, 'bold')).pack(side=tk.LEFT)
        
        # Onion URL validator
        validator_frame = tk.Frame(tools_window, bg='#000000')
        validator_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(validator_frame, text="Onion URL Validator:", bg='#000000', fg='#00ff41',
                font=('Courier', 10, 'bold')).pack(anchor=tk.W)
        
        url_var = tk.StringVar()
        url_entry = tk.Entry(validator_frame, textvariable=url_var, bg='#001100', fg='#00ff41',
                            font=('Courier', 10), width=60)
        url_entry.pack(fill=tk.X, pady=5)
        
        result_text = tk.Text(tools_window, bg='#001100', fg='#00ff41', font=('Courier', 9),
                             height=15, width=80)
        result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def validate_url():
            url = url_var.get()
            if url:
                result = self.darkweb.validate_onion_url(url)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"URL: {url}\n")
                result_text.insert(tk.END, f"Valid: {result['valid']}\n")
                result_text.insert(tk.END, f"Version: {result['version']}\n")
                result_text.insert(tk.END, f"Security Score: {result['security_score']}/10\n")
        
        def generate_onion():
            result = self.darkweb.generate_onion_address()
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Generated Address: {result['address']}\n")
            result_text.insert(tk.END, f"Version: {result['version']}\n")
            result_text.insert(tk.END, "Note: This is a mock address for demonstration\n")
        
        btn_frame = tk.Frame(tools_window, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="◉ VALIDATE", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=validate_url).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="◉ GENERATE", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=generate_onion).pack(side=tk.LEFT)
    
    def show_ai_tools(self):
        """Show AI tools interface"""
        ai_window = tk.Toplevel(self.root)
        ai_window.title("AI Security Tools")
        ai_window.geometry("900x700")
        ai_window.configure(bg='#000000')
        
        tk.Label(ai_window, text="◢ AI SECURITY TOOLKIT ◣", bg='#000000', fg='#00ff41',
                font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Input area
        input_frame = tk.Frame(ai_window, bg='#000000')
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="Input Text/Code for Analysis:", bg='#000000', fg='#00ff41',
                font=('Courier', 10, 'bold')).pack(anchor=tk.W)
        
        input_text = tk.Text(input_frame, bg='#001100', fg='#00ff41', font=('Courier', 9),
                            height=8, width=80)
        input_text.pack(fill=tk.X, pady=5)
        
        # Results area
        results_text = tk.Text(ai_window, bg='#001100', fg='#00ff41', font=('Courier', 9),
                              height=20, width=80)
        results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def analyze_threats():
            text = input_text.get(1.0, tk.END).strip()
            if text:
                result = self.ai_engine.analyze_threat_intelligence(text)
                results_text.delete(1.0, tk.END)
                results_text.insert(tk.END, "=== THREAT ANALYSIS ===\n")
                results_text.insert(tk.END, f"Threats: {result['threats_detected']}\n")
                results_text.insert(tk.END, f"Confidence: {result['confidence_score']}%\n")
                results_text.insert(tk.END, f"Risk Level: {result['risk_level']}\n")
                results_text.insert(tk.END, f"Recommendations: {result['recommendations']}\n")
        
        def detect_phishing():
            text = input_text.get(1.0, tk.END).strip()
            if text:
                result = self.ai_engine.detect_phishing(text)
                results_text.delete(1.0, tk.END)
                results_text.insert(tk.END, "=== PHISHING DETECTION ===\n")
                results_text.insert(tk.END, f"Is Phishing: {result['is_phishing']}\n")
                results_text.insert(tk.END, f"Risk Score: {result['risk_score']}%\n")
                results_text.insert(tk.END, f"Indicators: {result['indicators_found']}\n")
                results_text.insert(tk.END, f"Recommendation: {result['recommendation']}\n")
        
        def classify_malware():
            text = input_text.get(1.0, tk.END).strip()
            if text:
                result = self.ai_engine.classify_malware(text)
                results_text.delete(1.0, tk.END)
                results_text.insert(tk.END, "=== MALWARE CLASSIFICATION ===\n")
                results_text.insert(tk.END, f"Classifications: {result['classifications']}\n")
                results_text.insert(tk.END, f"Confidence Scores: {result['confidence_scores']}\n")
                results_text.insert(tk.END, f"Matches Found: {result['matches_found']:.1f}\n")
        
        btn_frame = tk.Frame(ai_window, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="🔍 THREAT ANALYSIS", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=analyze_threats).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_frame, text="🎣 PHISHING DETECT", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=detect_phishing).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_frame, text="🦠 MALWARE CLASSIFY", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=classify_malware).pack(side=tk.LEFT)
    
    def show_secure_comm(self):
        """Show secure communication interface"""
        if not self.secure_comm:
            self.secure_comm = SecureCommunication(self.storage.encryption)
        
        comm_window = tk.Toplevel(self.root)
        comm_window.title("Secure Communication")
        comm_window.geometry("800x600")
        comm_window.configure(bg='#000000')
        
        tk.Label(comm_window, text="◢ SECURE COMMUNICATION ◣", bg='#000000', fg='#00ff41',
                font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Chat creation
        chat_frame = tk.Frame(comm_window, bg='#000000')
        chat_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(chat_frame, text="Create Encrypted Chat:", bg='#000000', fg='#00ff41',
                font=('Courier', 10, 'bold')).pack(anchor=tk.W)
        
        chat_id_var = tk.StringVar()
        tk.Entry(chat_frame, textvariable=chat_id_var, bg='#001100', fg='#00ff41',
                font=('Courier', 10), width=30).pack(side=tk.LEFT, padx=(0, 10))
        
        # Results area
        comm_results = tk.Text(comm_window, bg='#001100', fg='#00ff41', font=('Courier', 9),
                              height=20, width=80)
        comm_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def create_chat():
            chat_id = chat_id_var.get()
            if chat_id:
                result = self.secure_comm.create_encrypted_chat(chat_id, ['user1', 'user2'])
                comm_results.delete(1.0, tk.END)
                comm_results.insert(tk.END, "=== ENCRYPTED CHAT CREATED ===\n")
                comm_results.insert(tk.END, f"Chat ID: {result['chat_id']}\n")
                comm_results.insert(tk.END, f"Status: {result['status']}\n")
                comm_results.insert(tk.END, f"Participants: {result['participants']}\n")
                comm_results.insert(tk.END, f"Encryption Key: {result['encryption_key']}\n")
        
        def generate_burner():
            identity = self.secure_comm.generate_burner_identity()
            comm_results.delete(1.0, tk.END)
            comm_results.insert(tk.END, "=== BURNER IDENTITY GENERATED ===\n")
            comm_results.insert(tk.END, f"ID: {identity['id']}\n")
            comm_results.insert(tk.END, f"Username: {identity['username']}\n")
            comm_results.insert(tk.END, f"Email: {identity['email']}\n")
            comm_results.insert(tk.END, f"Phone: {identity['phone']}\n")
            comm_results.insert(tk.END, f"Expires: 24 hours\n")
        
        def create_covert_channel():
            channel = self.secure_comm.create_covert_channel('steganography')
            comm_results.delete(1.0, tk.END)
            comm_results.insert(tk.END, "=== COVERT CHANNEL ESTABLISHED ===\n")
            comm_results.insert(tk.END, f"Channel ID: {channel['channel_id']}\n")
            comm_results.insert(tk.END, f"Method: {channel['method']}\n")
            comm_results.insert(tk.END, f"Capacity: {channel['capacity']}\n")
            comm_results.insert(tk.END, f"Detection Risk: {channel['detection_risk']}\n")
        
        btn_frame = tk.Frame(comm_window, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="💬 CREATE CHAT", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=create_chat).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_frame, text="🎭 BURNER ID", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=generate_burner).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_frame, text="🕳️ COVERT CHANNEL", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=create_covert_channel).pack(side=tk.LEFT)
    
    def show_dashboard(self):
        """Show data visualization dashboard"""
        dashboard = self.visualizer.create_security_dashboard()
        
        # Add real-time data updates
        def update_dashboard():
            if dashboard.winfo_exists():
                # Refresh visualizations every 5 seconds
                self.visualizer.draw_threat_chart()
                dashboard.after(5000, update_dashboard)
        
        dashboard.after(1000, update_dashboard)
    
    def show_settings(self):
        settings = tk.Toplevel(self.root)
        settings.title("Advanced Settings")
        settings.geometry("700x600")
        settings.configure(bg='#000000')
        
        # Create notebook for tabbed settings
        notebook = ttk.Notebook(settings)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Audio Settings Tab
        audio_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(audio_frame, text='🔊 Audio')
        
        tk.Label(audio_frame, text="◢ AUDIO SETTINGS ◣", bg='#000000', fg='#00ff41',
                font=('Courier', 14, 'bold')).pack(pady=10)
        
        # Sound settings
        sound_var = tk.BooleanVar(value=False)  # Sound removed
        tk.Checkbutton(audio_frame, text="Enable Startup Sound", variable=sound_var,
                      bg='#000000', fg='#00ff41', selectcolor='#003300',
                      font=('Courier', 10)).pack(pady=5, anchor='w', padx=20)
        
        audio_effects_var = tk.BooleanVar(value=self.audio_visual.enabled)
        tk.Checkbutton(audio_frame, text="Enable Audio Effects", variable=audio_effects_var,
                      bg='#000000', fg='#00ff41', selectcolor='#003300',
                      font=('Courier', 10)).pack(pady=5, anchor='w', padx=20)
        
        tts_var = tk.BooleanVar(value=False)
        tk.Checkbutton(audio_frame, text="Enable Text-to-Speech", variable=tts_var,
                      bg='#000000', fg='#00ff41', selectcolor='#003300',
                      font=('Courier', 10)).pack(pady=5, anchor='w', padx=20)
        
        # Volume control
        volume_frame = tk.Frame(audio_frame, bg='#000000')
        volume_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(volume_frame, text="Volume:", bg='#000000', fg='#00ff41',
                font=('Courier', 10)).pack(side=tk.LEFT)
        
        volume_var = tk.DoubleVar(value=self.audio_visual.volume * 100)
        volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                               variable=volume_var, bg='#001100', fg='#00ff41',
                               font=('Courier', 9), length=200)
        volume_scale.pack(side=tk.LEFT, padx=(10, 0))
        
        # Visual Effects Tab
        visual_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(visual_frame, text='✨ Visual')
        
        tk.Label(visual_frame, text="◢ VISUAL EFFECTS ◣", bg='#000000', fg='#00ff41',
                font=('Courier', 14, 'bold')).pack(pady=10)
        
        visual_effects_var = tk.BooleanVar(value=self.audio_visual.visual_effects)
        tk.Checkbutton(visual_frame, text="Enable Visual Effects", variable=visual_effects_var,
                      bg='#000000', fg='#00ff41', selectcolor='#003300',
                      font=('Courier', 10)).pack(pady=5, anchor='w', padx=20)
        
        haptic_var = tk.BooleanVar(value=self.audio_visual.haptic_enabled)
        tk.Checkbutton(visual_frame, text="Enable Haptic Feedback", variable=haptic_var,
                      bg='#000000', fg='#00ff41', selectcolor='#003300',
                      font=('Courier', 10)).pack(pady=5, anchor='w', padx=20)
        
        # Security Tab
        security_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(security_frame, text='🔒 Security')
        
        tk.Label(security_frame, text="◢ SECURITY SETTINGS ◣", bg='#000000', fg='#00ff41',
                font=('Courier', 14, 'bold')).pack(pady=10)
        
        # Auto-lock timeout
        timeout_frame = tk.Frame(security_frame, bg='#000000')
        timeout_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(timeout_frame, text="Auto-lock timeout (minutes):", bg='#000000', fg='#00ff41',
                font=('Courier', 10)).pack(side=tk.LEFT)
        
        timeout_var = tk.StringVar(value=str(self.auto_lock.timeout_minutes))
        timeout_entry = tk.Entry(timeout_frame, textvariable=timeout_var, bg='#001100', fg='#00ff41',
                                font=('Courier', 10), width=5)
        timeout_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save/Cancel buttons
        button_frame = tk.Frame(settings, bg='#000000')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def save_settings():
            # Audio settings
            # self.sound.set_enabled(sound_var.get())  # Removed
            self.audio_visual.set_enabled(audio_effects_var.get())
            self.audio_visual.set_volume(volume_var.get() / 100)
            
            # Visual settings
            self.audio_visual.set_visual_effects(visual_effects_var.get())
            self.audio_visual.set_haptic_feedback(haptic_var.get())
            
            # Security settings
            try:
                timeout = int(timeout_var.get())
                if 1 <= timeout <= 30:
                    self.auto_lock.set_timeout(timeout)
                    self.storage.set_setting('autolock_minutes', str(timeout))
            except ValueError:
                pass
            
            # Save all settings to storage
            # self.storage.set_setting('sound_enabled', str(sound_var.get()))  # Removed
            self.storage.set_setting('audio_effects', str(audio_effects_var.get()))
            self.storage.set_setting('visual_effects', str(visual_effects_var.get()))
            
            # Audio effects removed
            pass
            settings.destroy()
        
        def test_audio():
            # Audio test disabled
            messagebox.showinfo("Audio Test", "Audio system disabled")
        
        tk.Button(button_frame, text="🔊 TEST AUDIO", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=test_audio).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="◉ SAVE SETTINGS", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=save_settings).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(button_frame, text="◉ CANCEL", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=settings.destroy).pack(side=tk.RIGHT, padx=5)
    
    def export_data(self):
        messagebox.showinfo("Export", "Export functionality not implemented in minimal version")
    
    def import_data(self):
        messagebox.showinfo("Import", "Import functionality not implemented in minimal version")
    
    def show_osint_image(self):
        """Show OSINT Image Analyzer interface"""
        osint_window = tk.Toplevel(self.root)
        osint_window.title("Image OSINT Analyzer")
        osint_window.geometry("1000x700")
        osint_window.configure(bg='#000000')
        
        # Initialize OSINT GUI in the window
        osint_gui = OSINTImageGUI(osint_window, {
            'bg': '#000000', 'fg': '#00ff41', 'accent': '#40ff80', 'entry_bg': '#001100'
        })
        
        # Audio effects removed
        pass
    
    def lock_app(self):
        self.is_locked = True
        self.auto_lock.stop()
        # Audio effects removed
        pass
        self.show_login()
    
    def update_status(self):
        if not self.is_locked:
            self.status_var.set("◉ UNLOCKED | Last Activity: " + time.strftime("%H:%M:%S"))
            self.root.after(1000, self.update_status)
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            # self.sound.cleanup()  # Removed
            pass
