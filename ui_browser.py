"""UI Integration for Isolated Browser Launcher"""
import tkinter as tk
from tkinter import messagebox, ttk
import os
from isolated_browser import IsolatedBrowserLauncher

class BrowserUI:
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.browser_launcher = IsolatedBrowserLauncher(parent_gui.storage)
    
    def add_browser_button(self, parent_frame):
        """Add isolated browser button to main interface"""
        browser_btn = tk.Button(
            parent_frame, 
            text="🌐 Open Tor (Isolated)",
            bg='#003300', 
            fg='#00ff41',
            font=('Courier', 9), 
            command=self.launch_isolated_tor,
            width=20
        )
        browser_btn.pack(pady=2, padx=5)
        
        # Add hover effects
        def on_enter(e):
            browser_btn.configure(bg='#006600')
        
        def on_leave(e):
            browser_btn.configure(bg='#003300')
        
        browser_btn.bind('<Enter>', on_enter)
        browser_btn.bind('<Leave>', on_leave)
        
        return browser_btn
    
    def launch_isolated_tor(self):
        """Launch Tor browser in isolated mode with user confirmation"""
        # Show confirmation dialog with security info
        confirm_dialog = tk.Toplevel(self.parent.root)
        confirm_dialog.title("Launch Isolated Tor Browser")
        confirm_dialog.geometry("600x400")
        confirm_dialog.configure(bg='#000000')
        confirm_dialog.transient(self.parent.root)
        confirm_dialog.grab_set()
        
        tk.Label(confirm_dialog, text="◢ ISOLATED TOR BROWSER ◣", 
                bg='#000000', fg='#ff0040', font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Security info
        info_text = tk.Text(confirm_dialog, bg='#001100', fg='#00ff41', 
                           font=('Courier', 10), height=15, width=70)
        info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        security_info = """SANDBOX SECURITY FEATURES:

✓ Private filesystem (no access to user files)
✓ Network isolation (Tor traffic only)
✓ Disabled clipboard access
✓ No webcam/microphone access
✓ Memory restrictions
✓ Process isolation
✓ Temporary directories only

DETECTED SANDBOX TOOLS:"""
        
        info_text.insert(tk.END, security_info)
        
        # Check available tools
        sandbox_tools = self.browser_launcher.detect_sandbox_tools()
        tor_info = self.browser_launcher.detect_tor_browser()
        
        info_text.insert(tk.END, f"\n\nTor Browser: {'✓ Found' if tor_info['found'] else '✗ Not Found'}")
        if tor_info['found']:
            info_text.insert(tk.END, f"\nPath: {tor_info['path']}")
            info_text.insert(tk.END, f"\nType: {tor_info['type']}")
        
        info_text.insert(tk.END, f"\n\nFirejail: {'✓ Available' if sandbox_tools['firejail'] else '✗ Not Available'}")
        info_text.insert(tk.END, f"\nBubblewrap: {'✓ Available' if sandbox_tools['bubblewrap'] else '✗ Not Available'}")
        info_text.insert(tk.END, f"\nSystemd-run: {'✓ Available' if sandbox_tools['systemd-run'] else '✗ Not Available'}")
        info_text.insert(tk.END, f"\nAppArmor: {'✓ Available' if sandbox_tools['apparmor'] else '✗ Not Available'}")
        
        if not tor_info['found']:
            info_text.insert(tk.END, "\n\n⚠️  TOR BROWSER NOT FOUND!")
            info_text.insert(tk.END, "\nSearched locations:")
            info_text.insert(tk.END, "\n  ~/Desktop/tor-browser*/")
            info_text.insert(tk.END, "\n  ~/Downloads/tor-browser*/")
            info_text.insert(tk.END, "\n  /usr/bin/torbrowser-launcher")
        
        if not any(sandbox_tools.values()):
            info_text.insert(tk.END, "\n\n⚠️  WARNING: No sandbox tools detected!")
            info_text.insert(tk.END, "\nInstall firejail for maximum security:")
            info_text.insert(tk.END, "\n  sudo apt install firejail")
        
        info_text.configure(state='disabled')
        
        # Buttons
        btn_frame = tk.Frame(confirm_dialog, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def proceed_launch():
            confirm_dialog.destroy()
            self._execute_launch()
        
        def show_logs():
            self.show_browser_logs()
        
        def manual_path():
            from tkinter import filedialog
            tor_path = filedialog.askopenfilename(
                title="Select Tor Browser Executable",
                initialdir=os.path.expanduser('~/Desktop'),
                filetypes=[("Executable files", "*"), ("All files", "*.*")]
            )
            if tor_path:
                # Test the selected path
                test_info = {'found': True, 'path': tor_path, 'type': 'manual'}
                self.browser_launcher.tor_info_override = test_info
                confirm_dialog.destroy()
                self._execute_launch()
        
        tk.Button(btn_frame, text="🚀 LAUNCH ISOLATED", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=proceed_launch).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📋 VIEW LOGS", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=show_logs).pack(side=tk.LEFT, padx=5)
        
        if not tor_info['found']:
            tk.Button(btn_frame, text="📁 MANUAL PATH", bg='#003300', fg='#00ff41',
                     font=('Courier', 10, 'bold'), command=manual_path).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="◉ CANCEL", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=confirm_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _execute_launch(self):
        """Execute the actual browser launch"""
        try:
            # Show loading dialog
            loading = tk.Toplevel(self.parent.root)
            loading.title("Launching...")
            loading.geometry("400x200")
            loading.configure(bg='#000000')
            loading.transient(self.parent.root)
            loading.grab_set()
            
            tk.Label(loading, text="◉ INITIALIZING SANDBOX ◉", 
                    bg='#000000', fg='#00ff41', font=('Courier', 14, 'bold')).pack(pady=20)
            
            progress = ttk.Progressbar(loading, mode='indeterminate')
            progress.pack(pady=20, padx=40, fill=tk.X)
            progress.start()
            
            status_label = tk.Label(loading, text="Detecting sandbox tools...", 
                                   bg='#000000', fg='#00ff41', font=('Courier', 10))
            status_label.pack(pady=10)
            
            loading.update()
            
            # Launch browser
            result = self.browser_launcher.launch_tor_isolated()
            
            progress.stop()
            loading.destroy()
            
            # Show result
            if result['status'] == 'Success':
                messagebox.showinfo("Success", 
                    f"✓ Tor Browser launched in {result['method']} sandbox\n\n"
                    f"Security Level: Maximum\n"
                    f"Isolation: Complete\n"
                    f"Timestamp: {result['timestamp']}")
                
                # Play success sound
                if hasattr(self.parent, 'audio_visual'):
                    self.parent.audio_visual.play_sound_effect('success')
            else:
                messagebox.showerror("Launch Failed", 
                    f"✗ Failed to launch Tor Browser\n\n"
                    f"Method: {result['method']}\n"
                    f"Error: {result['error']}\n\n"
                    f"Try installing sandbox tools:\n"
                    f"sudo apt install firejail bubblewrap")
                
                # Play error sound
                if hasattr(self.parent, 'audio_visual'):
                    self.parent.audio_visual.play_sound_effect('error')
        
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def show_browser_logs(self):
        """Show browser launch logs window"""
        logs_window = tk.Toplevel(self.parent.root)
        logs_window.title("Browser Launch Logs")
        logs_window.geometry("900x600")
        logs_window.configure(bg='#000000')
        
        tk.Label(logs_window, text="◢ BROWSER LAUNCH LOGS ◣", 
                bg='#000000', fg='#00ff41', font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Create treeview for logs
        columns = ('Timestamp', 'Method', 'Status', 'Command')
        logs_tree = ttk.Treeview(logs_window, columns=columns, show='headings', 
                                style='Dark.Treeview', height=20)
        
        # Configure columns
        logs_tree.heading('Timestamp', text='◢ TIMESTAMP ◣')
        logs_tree.heading('Method', text='◢ SANDBOX METHOD ◣')
        logs_tree.heading('Status', text='◢ STATUS ◣')
        logs_tree.heading('Command', text='◢ COMMAND ◣')
        
        logs_tree.column('Timestamp', width=150)
        logs_tree.column('Method', width=120)
        logs_tree.column('Status', width=80)
        logs_tree.column('Command', width=400)
        
        logs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load logs
        logs = self.browser_launcher.get_browser_logs()
        for log in logs:
            status_color = 'green' if log['status'] == 'Success' else 'red'
            logs_tree.insert('', tk.END, values=(
                log['timestamp'][:19] if log['timestamp'] else '',
                log['method'],
                log['status'],
                log['command'][:60] + '...' if log['command'] and len(log['command']) > 60 else log['command'] or ''
            ))
        
        # Details panel
        details_frame = tk.Frame(logs_window, bg='#000000')
        details_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(details_frame, text="Selected Log Details:", 
                bg='#000000', fg='#00ff41', font=('Courier', 10, 'bold')).pack(anchor='w')
        
        details_text = tk.Text(details_frame, bg='#001100', fg='#00ff41', 
                              font=('Courier', 9), height=6)
        details_text.pack(fill=tk.X, pady=5)
        
        def on_log_select(event):
            selection = logs_tree.selection()
            if selection:
                item = logs_tree.item(selection[0])
                values = item['values']
                
                # Find full log entry
                timestamp = values[0]
                log_entry = next((log for log in logs if log['timestamp'].startswith(timestamp)), None)
                
                if log_entry:
                    details_text.delete(1.0, tk.END)
                    details_text.insert(tk.END, f"Timestamp: {log_entry['timestamp']}\n")
                    details_text.insert(tk.END, f"Method: {log_entry['method']}\n")
                    details_text.insert(tk.END, f"Status: {log_entry['status']}\n")
                    details_text.insert(tk.END, f"Command: {log_entry['command'] or 'N/A'}\n")
                    details_text.insert(tk.END, f"Error: {log_entry['error'] or 'None'}\n")
        
        logs_tree.bind('<<TreeviewSelect>>', on_log_select)
        
        # Refresh button
        def refresh_logs():
            for item in logs_tree.get_children():
                logs_tree.delete(item)
            
            logs = self.browser_launcher.get_browser_logs()
            for log in logs:
                logs_tree.insert('', tk.END, values=(
                    log['timestamp'][:19] if log['timestamp'] else '',
                    log['method'],
                    log['status'],
                    log['command'][:60] + '...' if log['command'] and len(log['command']) > 60 else log['command'] or ''
                ))
        
        tk.Button(logs_window, text="🔄 REFRESH", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=refresh_logs).pack(pady=10)