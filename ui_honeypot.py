"""UI Integration for Honeypot Defense System"""
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from honeypot import HoneypotDefenseSystem
import os

class HoneypotUI:
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.honeypot = HoneypotDefenseSystem(parent_gui.storage)
    
    def add_honeypot_button(self, parent_frame):
        """Add honeypot security button to main interface"""
        honeypot_btn = tk.Button(
            parent_frame, 
            text="🍯 Security Logs",
            bg='#003300', 
            fg='#00ff41',
            font=('Courier', 9), 
            command=self.show_security_dashboard,
            width=20
        )
        honeypot_btn.pack(pady=2, padx=5)
        
        # Add hover effects
        def on_enter(e):
            honeypot_btn.configure(bg='#006600')
        
        def on_leave(e):
            honeypot_btn.configure(bg='#003300')
        
        honeypot_btn.bind('<Enter>', on_enter)
        honeypot_btn.bind('<Leave>', on_leave)
        
        return honeypot_btn
    
    def add_file_scanner_button(self, parent_frame):
        """Add file scanner button"""
        scanner_btn = tk.Button(
            parent_frame, 
            text="🔍 Scan File",
            bg='#003300', 
            fg='#00ff41',
            font=('Courier', 9), 
            command=self.scan_file_dialog,
            width=20
        )
        scanner_btn.pack(pady=2, padx=5)
        
        # Add hover effects
        def on_enter(e):
            scanner_btn.configure(bg='#006600')
        
        def on_leave(e):
            scanner_btn.configure(bg='#003300')
        
        scanner_btn.bind('<Enter>', on_enter)
        scanner_btn.bind('<Leave>', on_leave)
        
        return scanner_btn
    
    def scan_file_dialog(self):
        """Open file dialog to scan a file"""
        file_path = filedialog.askopenfilename(
            title="Select File to Scan",
            filetypes=[
                ("All Files", "*.*"),
                ("Executables", "*.exe;*.scr;*.bat;*.cmd"),
                ("Documents", "*.pdf;*.doc;*.docx;*.xls;*.xlsx"),
                ("Archives", "*.zip;*.rar;*.7z;*.tar.gz")
            ]
        )
        
        if file_path:
            self.scan_file(file_path)
    
    def scan_file(self, file_path: str):
        """Scan a specific file for threats"""
        try:
            # Show scanning dialog
            scan_dialog = tk.Toplevel(self.parent.root)
            scan_dialog.title("File Security Scan")
            scan_dialog.geometry("700x500")
            scan_dialog.configure(bg='#000000')
            scan_dialog.transient(self.parent.root)
            scan_dialog.grab_set()
            
            tk.Label(scan_dialog, text="◢ FILE SECURITY SCAN ◣", 
                    bg='#000000', fg='#ff0040', font=('Courier', 16, 'bold')).pack(pady=10)
            
            # File info
            info_frame = tk.Frame(scan_dialog, bg='#000000')
            info_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(info_frame, text=f"Scanning: {os.path.basename(file_path)}", 
                    bg='#000000', fg='#00ff41', font=('Courier', 12, 'bold')).pack(anchor='w')
            
            # Progress bar
            progress = ttk.Progressbar(scan_dialog, mode='indeterminate')
            progress.pack(pady=10, padx=40, fill=tk.X)
            progress.start()
            
            scan_dialog.update()
            
            # Perform analysis
            analysis = self.honeypot.analyze_file_threat(file_path)
            
            progress.stop()
            progress.destroy()
            
            # Results display
            results_text = tk.Text(scan_dialog, bg='#001100', fg='#00ff41', 
                                  font=('Courier', 10), height=20, width=80)
            results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Display results
            results_text.insert(tk.END, "=== SECURITY SCAN RESULTS ===\\n\\n")
            results_text.insert(tk.END, f"File: {analysis['filename']}\\n")
            results_text.insert(tk.END, f"Path: {analysis['file_path']}\\n")
            results_text.insert(tk.END, f"Size: {analysis['file_size']:,} bytes\\n")
            results_text.insert(tk.END, f"Type: {analysis['mime_type'] or 'Unknown'}\\n")
            results_text.insert(tk.END, f"Hash: {analysis['file_hash'] or 'N/A'}\\n\\n")
            
            # Threat level with color coding
            threat_level = analysis['threat_level']
            if threat_level == 'HIGH':
                results_text.insert(tk.END, "⚠️  THREAT LEVEL: HIGH\\n", 'high_threat')
            elif threat_level == 'MEDIUM':
                results_text.insert(tk.END, "⚠️  THREAT LEVEL: MEDIUM\\n", 'medium_threat')
            else:
                results_text.insert(tk.END, "✓ THREAT LEVEL: LOW\\n", 'low_threat')
            
            results_text.insert(tk.END, "\\n=== THREAT INDICATORS ===\\n")
            if analysis['threats']:
                for threat in analysis['threats']:
                    results_text.insert(tk.END, f"• {threat}\\n")
            else:
                results_text.insert(tk.END, "No significant threats detected\\n")
            
            # Configure text tags for colors
            results_text.tag_configure('high_threat', foreground='#ff0040')
            results_text.tag_configure('medium_threat', foreground='#ffaa00')
            results_text.tag_configure('low_threat', foreground='#00ff41')
            
            results_text.configure(state='disabled')
            
            # Action buttons
            btn_frame = tk.Frame(scan_dialog, bg='#000000')
            btn_frame.pack(fill=tk.X, padx=20, pady=10)
            
            def quarantine_file():
                result = self.honeypot.trap_suspicious_file(file_path, 'manual_scan')
                if result['trapped']:
                    messagebox.showinfo("File Quarantined", 
                        f"✓ File moved to secure quarantine\\n\\n"
                        f"Trap Path: {result['trap_path']}\\n"
                        f"Threat Level: {result['threat_level']}\\n"
                        f"Threats: {', '.join(result['threats'])}")
                    scan_dialog.destroy()
                else:
                    messagebox.showinfo("No Action Needed", 
                        f"File not quarantined: {result.get('reason', 'Unknown')}")
            
            def view_in_hex():
                self.show_hex_viewer(file_path)
            
            if threat_level in ['MEDIUM', 'HIGH']:
                tk.Button(btn_frame, text="🔒 QUARANTINE", bg='#330000', fg='#ff0040',
                         font=('Courier', 10, 'bold'), command=quarantine_file).pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="🔍 HEX VIEW", bg='#003300', fg='#00ff41',
                     font=('Courier', 10, 'bold'), command=view_in_hex).pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="◉ CLOSE", bg='#003300', fg='#00ff41',
                     font=('Courier', 10, 'bold'), command=scan_dialog.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Play alert sound for high threats
            if threat_level == 'HIGH' and hasattr(self.parent, 'audio_visual'):
                self.parent.audio_visual.play_sound_effect('alert')
        
        except Exception as e:
            messagebox.showerror("Scan Error", f"Failed to scan file: {str(e)}")
    
    def show_hex_viewer(self, file_path: str):
        """Show hex viewer for file analysis"""
        hex_window = tk.Toplevel(self.parent.root)
        hex_window.title(f"Hex Viewer - {os.path.basename(file_path)}")
        hex_window.geometry("900x600")
        hex_window.configure(bg='#000000')
        
        tk.Label(hex_window, text="◢ HEX VIEWER ◣", 
                bg='#000000', fg='#00ff41', font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Hex display
        hex_text = tk.Text(hex_window, bg='#001100', fg='#00ff41', 
                          font=('Courier', 8), wrap=tk.NONE)
        
        # Scrollbars
        v_scroll = tk.Scrollbar(hex_window, orient=tk.VERTICAL, command=hex_text.yview)
        h_scroll = tk.Scrollbar(hex_window, orient=tk.HORIZONTAL, command=hex_text.xview)
        hex_text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack with scrollbars
        hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=10)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X, padx=20)
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read(8192)  # Read first 8KB
                
                hex_lines = []
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    hex_part = ' '.join(f'{b:02x}' for b in chunk)
                    ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                    hex_lines.append(f'{i:08x}  {hex_part:<48} |{ascii_part}|')
                
                hex_text.insert(tk.END, '\\n'.join(hex_lines))
                
                if len(data) == 8192:
                    hex_text.insert(tk.END, '\\n\\n[Showing first 8KB only]')
        
        except Exception as e:
            hex_text.insert(tk.END, f"Error reading file: {str(e)}")
        
        hex_text.configure(state='disabled')
    
    def show_security_dashboard(self):
        """Show comprehensive security dashboard"""
        dashboard = tk.Toplevel(self.parent.root)
        dashboard.title("Security Dashboard")
        dashboard.geometry("1000x700")
        dashboard.configure(bg='#000000')
        
        tk.Label(dashboard, text="◢ SECURITY DASHBOARD ◣", 
                bg='#000000', fg='#ff0040', font=('Courier', 18, 'bold')).pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Honeypot Logs Tab
        logs_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(logs_frame, text='🍯 Honeypot Logs')
        
        self._create_honeypot_logs_tab(logs_frame)
        
        # Trapped Files Tab
        files_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(files_frame, text='🔒 Quarantined Files')
        
        self._create_trapped_files_tab(files_frame)
        
        # Statistics Tab
        stats_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(stats_frame, text='📊 Statistics')
        
        self._create_statistics_tab(stats_frame)
    
    def _create_honeypot_logs_tab(self, parent):
        """Create honeypot logs tab"""
        tk.Label(parent, text="Recent Security Events", 
                bg='#000000', fg='#00ff41', font=('Courier', 14, 'bold')).pack(pady=10)
        
        # Logs treeview
        columns = ('Timestamp', 'Event', 'File', 'Threat Level', 'Action')
        logs_tree = ttk.Treeview(parent, columns=columns, show='headings', 
                                style='Dark.Treeview', height=15)
        
        for col in columns:
            logs_tree.heading(col, text=f'◢ {col.upper()} ◣')
        
        logs_tree.column('Timestamp', width=150)
        logs_tree.column('Event', width=120)
        logs_tree.column('File', width=200)
        logs_tree.column('Threat Level', width=100)
        logs_tree.column('Action', width=150)
        
        logs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load logs
        logs = self.honeypot.get_honeypot_logs()
        for log in logs:
            logs_tree.insert('', tk.END, values=(
                log['timestamp'][:19] if log['timestamp'] else '',
                log['event_type'],
                os.path.basename(log['file_path']) if log['file_path'] else 'N/A',
                log['threat_level'],
                log['action_taken'][:30] + '...' if len(log['action_taken']) > 30 else log['action_taken']
            ))
        
        # Refresh button
        def refresh_logs():
            for item in logs_tree.get_children():
                logs_tree.delete(item)
            
            logs = self.honeypot.get_honeypot_logs()
            for log in logs:
                logs_tree.insert('', tk.END, values=(
                    log['timestamp'][:19] if log['timestamp'] else '',
                    log['event_type'],
                    os.path.basename(log['file_path']) if log['file_path'] else 'N/A',
                    log['threat_level'],
                    log['action_taken'][:30] + '...' if len(log['action_taken']) > 30 else log['action_taken']
                ))
        
        tk.Button(parent, text="🔄 REFRESH", bg='#003300', fg='#00ff41',
                 font=('Courier', 10, 'bold'), command=refresh_logs).pack(pady=10)
    
    def _create_trapped_files_tab(self, parent):
        """Create trapped files tab"""
        tk.Label(parent, text="Quarantined Files", 
                bg='#000000', fg='#ff0040', font=('Courier', 14, 'bold')).pack(pady=10)
        
        # Files treeview
        columns = ('Filename', 'Size', 'Threats', 'Quarantine Date')
        files_tree = ttk.Treeview(parent, columns=columns, show='headings', 
                                 style='Dark.Treeview', height=15)
        
        for col in columns:
            files_tree.heading(col, text=f'◢ {col.upper()} ◣')
        
        files_tree.column('Filename', width=250)
        files_tree.column('Size', width=100)
        files_tree.column('Threats', width=300)
        files_tree.column('Quarantine Date', width=150)
        
        files_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load trapped files
        trapped_files = self.honeypot.get_trapped_files()
        for file_info in trapped_files:
            files_tree.insert('', tk.END, values=(
                file_info['filename'],
                f"{file_info['file_size']:,} bytes" if file_info['file_size'] else 'Unknown',
                ', '.join(file_info['threats']) if file_info['threats'] else 'None',
                file_info['quarantine_date'][:19] if file_info['quarantine_date'] else ''
            ))
        
        # Action buttons
        btn_frame = tk.Frame(parent, bg='#000000')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def cleanup_old():
            count = self.honeypot.cleanup_old_traps(30)
            messagebox.showinfo("Cleanup Complete", f"Removed {count} old quarantined files")
            # Refresh the view
            for item in files_tree.get_children():
                files_tree.delete(item)
            trapped_files = self.honeypot.get_trapped_files()
            for file_info in trapped_files:
                files_tree.insert('', tk.END, values=(
                    file_info['filename'],
                    f"{file_info['file_size']:,} bytes" if file_info['file_size'] else 'Unknown',
                    ', '.join(file_info['threats']) if file_info['threats'] else 'None',
                    file_info['quarantine_date'][:19] if file_info['quarantine_date'] else ''
                ))
        
        tk.Button(btn_frame, text="🧹 CLEANUP OLD", bg='#330000', fg='#ff0040',
                 font=('Courier', 10, 'bold'), command=cleanup_old).pack(side=tk.LEFT, padx=5)
    
    def _create_statistics_tab(self, parent):
        """Create statistics tab"""
        tk.Label(parent, text="Security Statistics", 
                bg='#000000', fg='#00ff41', font=('Courier', 14, 'bold')).pack(pady=10)
        
        stats_text = tk.Text(parent, bg='#001100', fg='#00ff41', 
                            font=('Courier', 12), height=20, width=80)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Calculate statistics
        logs = self.honeypot.get_honeypot_logs()
        trapped_files = self.honeypot.get_trapped_files()
        
        total_events = len(logs)
        high_threats = len([log for log in logs if log['threat_level'] == 'HIGH'])
        medium_threats = len([log for log in logs if log['threat_level'] == 'MEDIUM'])
        low_threats = len([log for log in logs if log['threat_level'] == 'LOW'])
        
        stats_text.insert(tk.END, "=== SECURITY STATISTICS ===\\n\\n")
        stats_text.insert(tk.END, f"Total Security Events: {total_events}\\n")
        stats_text.insert(tk.END, f"High Threat Events: {high_threats}\\n")
        stats_text.insert(tk.END, f"Medium Threat Events: {medium_threats}\\n")
        stats_text.insert(tk.END, f"Low Threat Events: {low_threats}\\n\\n")
        
        stats_text.insert(tk.END, f"Files Quarantined: {len(trapped_files)}\\n")
        
        if trapped_files:
            total_size = sum(f['file_size'] for f in trapped_files if f['file_size'])
            stats_text.insert(tk.END, f"Total Quarantined Size: {total_size:,} bytes\\n")
        
        stats_text.insert(tk.END, "\\n=== THREAT BREAKDOWN ===\\n")
        
        # Count threat types
        threat_counts = {}
        for file_info in trapped_files:
            for threat in file_info['threats']:
                threat_counts[threat] = threat_counts.get(threat, 0) + 1
        
        for threat, count in sorted(threat_counts.items(), key=lambda x: x[1], reverse=True):
            stats_text.insert(tk.END, f"{threat}: {count}\\n")
        
        stats_text.configure(state='disabled')