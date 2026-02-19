#!/usr/bin/env python3
"""
Smart-Encrypt OSINT Image GUI Integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from PIL import Image, ImageTk
import threading
from osint_image import OSINTImageAnalyzer

class OSINTImageGUI:
    def __init__(self, parent_frame, theme_colors):
        self.parent = parent_frame
        self.colors = theme_colors
        self.analyzer = OSINTImageAnalyzer()
        self.current_case_id = None
        self.current_target_id = None
        self.scan_thread = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup OSINT Image GUI"""
        # Main container
        main_frame = tk.Frame(self.parent, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🔍 IMAGE OSINT ANALYZER", 
                              font=('Courier', 16, 'bold'),
                              fg=self.colors['accent'], bg=self.colors['bg'])
        title_label.pack(pady=(0, 20))
        
        # Upload section
        upload_frame = tk.LabelFrame(main_frame, text="Target Image", 
                                   fg=self.colors['fg'], bg=self.colors['bg'],
                                   font=('Courier', 10, 'bold'))
        upload_frame.pack(fill='x', pady=(0, 10))
        
        upload_btn_frame = tk.Frame(upload_frame, bg=self.colors['bg'])
        upload_btn_frame.pack(fill='x', padx=10, pady=10)
        
        self.upload_btn = tk.Button(upload_btn_frame, text="📁 Upload Image",
                                   command=self.upload_image,
                                   bg=self.colors['accent'], fg=self.colors['bg'],
                                   font=('Courier', 10, 'bold'))
        self.upload_btn.pack(side='left')
        
        self.case_id_var = tk.StringVar(value="case_001")
        tk.Label(upload_btn_frame, text="Case ID:", fg=self.colors['fg'], 
                bg=self.colors['bg'], font=('Courier', 10)).pack(side='left', padx=(20, 5))
        case_entry = tk.Entry(upload_btn_frame, textvariable=self.case_id_var,
                             bg=self.colors['entry_bg'], fg=self.colors['fg'],
                             font=('Courier', 10), width=15)
        case_entry.pack(side='left')
        
        # Image preview
        self.image_preview = tk.Label(upload_frame, text="No image selected",
                                     fg=self.colors['fg'], bg=self.colors['bg'],
                                     font=('Courier', 10))
        self.image_preview.pack(pady=10)
        
        # Search options
        search_frame = tk.LabelFrame(main_frame, text="Search Options", 
                                   fg=self.colors['fg'], bg=self.colors['bg'],
                                   font=('Courier', 10, 'bold'))
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search mode selection
        mode_frame = tk.Frame(search_frame, bg=self.colors['bg'])
        mode_frame.pack(fill='x', padx=10, pady=5)
        
        self.search_mode = tk.StringVar(value="username")
        tk.Radiobutton(mode_frame, text="Username Search", variable=self.search_mode, value="username",
                      bg=self.colors['bg'], fg=self.colors['fg'], selectcolor=self.colors['bg'],
                      font=('Courier', 10), command=self.toggle_search_mode).pack(side='left')
        tk.Radiobutton(mode_frame, text="URL Search", variable=self.search_mode, value="url",
                      bg=self.colors['bg'], fg=self.colors['fg'], selectcolor=self.colors['bg'],
                      font=('Courier', 10), command=self.toggle_search_mode).pack(side='left', padx=(20, 0))
        
        # Username search section
        self.username_frame = tk.Frame(search_frame, bg=self.colors['bg'])
        self.username_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(self.username_frame, text="Username:", fg=self.colors['fg'], 
                bg=self.colors['bg'], font=('Courier', 10)).pack(side='left')
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(self.username_frame, textvariable=self.username_var,
                                 bg=self.colors['entry_bg'], fg=self.colors['fg'],
                                 font=('Courier', 10), width=20)
        username_entry.pack(side='left', padx=(10, 20))
        
        # Platform selection
        tk.Label(self.username_frame, text="Platforms:", fg=self.colors['fg'], 
                bg=self.colors['bg'], font=('Courier', 10)).pack(side='left')
        
        platforms_frame = tk.Frame(self.username_frame, bg=self.colors['bg'])
        platforms_frame.pack(side='left', padx=(10, 0))
        
        self.platform_vars = {}
        platforms = ['instagram', 'facebook', 'twitter', 'linkedin', 'github', 'reddit', 
                    'tiktok', 'pinterest', 'snapchat', 'youtube', 'telegram', 'discord',
                    'onlyfans', 'pornhub', 'xvideos', 'xhamster', 'redtube', 'chaturbate',
                    'cam4', 'myfreecams', 'tinder', 'bumble', 'badoo', 'match', 'pof', 'okcupid',
                    'doodstream', 'streamtape', 'mixdrop', 'uploadgig', 'rapidgator', 'mega',
                    'mediafire', 'anonfiles', 'gofile']
        
        # Create scrollable platform selection
        platform_canvas = tk.Canvas(platforms_frame, bg=self.colors['bg'], height=100, width=400)
        platform_scrollbar = tk.Scrollbar(platforms_frame, orient="vertical", command=platform_canvas.yview)
        platform_inner_frame = tk.Frame(platform_canvas, bg=self.colors['bg'])
        
        platform_canvas.configure(yscrollcommand=platform_scrollbar.set)
        platform_canvas.create_window((0, 0), window=platform_inner_frame, anchor="nw")
        
        for i, platform in enumerate(platforms):
            var = tk.BooleanVar(value=True if platform in ['instagram', 'facebook', 'twitter', 'onlyfans', 'pornhub'] else False)
            self.platform_vars[platform] = var
            cb = tk.Checkbutton(platform_inner_frame, text=platform.title(), variable=var,
                               bg=self.colors['bg'], fg=self.colors['fg'], 
                               selectcolor=self.colors['bg'], font=('Courier', 7))
            cb.grid(row=i//4, column=i%4, sticky='w', padx=3, pady=1)
        
        platform_inner_frame.update_idletasks()
        platform_canvas.configure(scrollregion=platform_canvas.bbox("all"))
        
        platform_canvas.pack(side="left", fill="both", expand=True)
        platform_scrollbar.pack(side="right", fill="y")
        
        # URLs section
        self.urls_frame = tk.LabelFrame(main_frame, text="Target URLs", 
                                      fg=self.colors['fg'], bg=self.colors['bg'],
                                      font=('Courier', 10, 'bold'))
        self.urls_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.urls_text = scrolledtext.ScrolledText(self.urls_frame, height=6,
                                                  bg=self.colors['entry_bg'], 
                                                  fg=self.colors['fg'],
                                                  font=('Courier', 9))
        self.urls_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.urls_text.insert('1.0', "https://example.com\nhttps://another-site.com")
        
        # Hide URL frame initially
        self.urls_frame.pack_forget()
        
        # Select all/none buttons
        select_frame = tk.Frame(search_frame, bg=self.colors['bg'])
        select_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(select_frame, text="Select All", command=self.select_all_platforms,
                 bg=self.colors['accent'], fg=self.colors['bg'], font=('Courier', 8)).pack(side='left')
        tk.Button(select_frame, text="Select None", command=self.select_no_platforms,
                 bg=self.colors['accent'], fg=self.colors['bg'], font=('Courier', 8)).pack(side='left', padx=(5, 0))
        tk.Button(select_frame, text="Adult Only", command=self.select_adult_platforms,
                 bg='#ff4444', fg='white', font=('Courier', 8)).pack(side='left', padx=(5, 0))
        tk.Button(select_frame, text="Social Only", command=self.select_social_platforms,
                 bg='#4444ff', fg='white', font=('Courier', 8)).pack(side='left', padx=(5, 0))
        tk.Button(select_frame, text="File Hosts", command=self.select_filehost_platforms,
                 bg='#ff8800', fg='white', font=('Courier', 8)).pack(side='left', padx=(5, 0))
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(fill='x', pady=(0, 10))
        
        self.scan_btn = tk.Button(control_frame, text="🔍 Start Username Scan",
                                 command=self.start_scan,
                                 bg=self.colors['accent'], fg=self.colors['bg'],
                                 font=('Courier', 10, 'bold'), state='disabled')
        self.scan_btn.pack(side='left')
        
        self.report_btn = tk.Button(control_frame, text="📄 Generate Report",
                                   command=self.generate_report,
                                   bg=self.colors['accent'], fg=self.colors['bg'],
                                   font=('Courier', 10, 'bold'), state='disabled')
        self.report_btn.pack(side='left', padx=(10, 0))
        
        self.stop_btn = tk.Button(control_frame, text="⏹ Stop",
                                 command=self.stop_scan,
                                 bg='#ff4444', fg='white',
                                 font=('Courier', 10, 'bold'), state='disabled')
        self.stop_btn.pack(side='left', padx=(10, 0))
        
        # Progress section
        progress_frame = tk.LabelFrame(main_frame, text="Progress", 
                                     fg=self.colors['fg'], bg=self.colors['bg'],
                                     font=('Courier', 10, 'bold'))
        progress_frame.pack(fill='both', expand=True)
        
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=8,
                                                      bg=self.colors['entry_bg'], 
                                                      fg=self.colors['fg'],
                                                      font=('Courier', 9))
        self.progress_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Results section
        results_frame = tk.LabelFrame(main_frame, text="Results", 
                                    fg=self.colors['fg'], bg=self.colors['bg'],
                                    font=('Courier', 10, 'bold'))
        results_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Results treeview
        columns = ('URL', 'Confidence', 'Date')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', pady=10, padx=(0, 10))
    
    def upload_image(self):
        """Upload target image"""
        file_path = filedialog.askopenfilename(
            title="Select Target Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            try:
                # Display preview
                img = Image.open(file_path)
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                self.image_preview.configure(image=photo, text="")
                self.image_preview.image = photo
                
                # Add to analyzer
                case_id = self.case_id_var.get() or "case_001"
                target_id = self.analyzer.add_target_image(file_path, case_id)
                
                if target_id:
                    self.current_case_id = case_id
                    self.current_target_id = target_id
                    self.scan_btn.configure(state='normal')
                    self.log_progress(f"✓ Target image loaded: {os.path.basename(file_path)}")
                    self.log_progress(f"✓ Case ID: {case_id}")
                else:
                    messagebox.showerror("Error", "Failed to process image")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def toggle_search_mode(self):
        """Toggle between username and URL search modes"""
        if self.search_mode.get() == "username":
            self.urls_frame.pack_forget()
            self.username_frame.pack(fill='x', padx=10, pady=5)
            self.scan_btn.configure(text="🔍 Start Username Scan")
        else:
            self.username_frame.pack_forget()
            self.urls_frame.pack(fill='both', expand=True, pady=(0, 10))
            self.scan_btn.configure(text="🔍 Start URL Scan")
    
    def start_scan(self):
        """Start OSINT scan"""
        if not self.current_target_id:
            messagebox.showwarning("Warning", "Please upload a target image first")
            return
        
        # Update UI state
        self.scan_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.progress_text.delete('1.0', 'end')
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if self.search_mode.get() == "username":
            # Username search
            username = self.username_var.get().strip()
            if not username:
                messagebox.showwarning("Warning", "Please enter a username")
                self.scan_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')
                return
            
            # Get selected platforms
            selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
            
            if not selected_platforms:
                messagebox.showwarning("Warning", "Please select at least one platform")
                self.scan_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')
                return
            
            self.log_progress(f"🚀 Starting username scan for '{username}' on {len(selected_platforms)} platforms...")
            
            # Start username scan
            self.scan_thread = self.analyzer.start_username_scan(
                self.current_case_id, 
                self.current_target_id, 
                username,
                selected_platforms,
                self.log_progress
            )
        else:
            # URL search
            urls_text = self.urls_text.get('1.0', 'end-1c').strip()
            if not urls_text:
                messagebox.showwarning("Warning", "Please enter target URLs")
                self.scan_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')
                return
            
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            if not urls:
                messagebox.showwarning("Warning", "No valid URLs found")
                self.scan_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')
                return
            
            self.log_progress(f"🚀 Starting scan of {len(urls)} URLs...")
            
            # Start URL scan
            self.scan_thread = self.analyzer.start_scan(
                self.current_case_id, 
                self.current_target_id, 
                urls, 
                self.log_progress
            )
        
        # Monitor completion
        self.monitor_scan()
    
    def monitor_scan(self):
        """Monitor scan completion"""
        if self.scan_thread and self.scan_thread.is_alive():
            self.parent.after(1000, self.monitor_scan)
        else:
            # Scan completed
            self.scan_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
            self.report_btn.configure(state='normal')
            self.load_results()
    
    def stop_scan(self):
        """Stop current scan"""
        if self.scan_thread:
            self.log_progress("⏹ Stopping scan...")
            # Note: Thread will complete current operation
            self.scan_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
    
    def load_results(self):
        """Load scan results"""
        if not self.current_case_id:
            return
        
        matches = self.analyzer.get_matches(self.current_case_id)
        
        for match in matches:
            url, local_path, confidence, metadata, created_at = match
            self.results_tree.insert('', 'end', values=(
                url[:50] + "..." if len(url) > 50 else url,
                f"{confidence:.1%}",
                created_at[:16]
            ))
        
        self.log_progress(f"✓ Loaded {len(matches)} results")
    
    def generate_report(self):
        """Generate PDF report"""
        if not self.current_case_id:
            messagebox.showwarning("Warning", "No case data available")
            return
        
        self.log_progress("📄 Generating PDF report...")
        
        try:
            report_path = self.analyzer.generate_report(self.current_case_id)
            if report_path:
                self.log_progress(f"✓ Report saved: {report_path}")
                messagebox.showinfo("Success", f"Report generated:\n{report_path}")
            else:
                messagebox.showerror("Error", "Failed to generate report")
        except Exception as e:
            messagebox.showerror("Error", f"Report generation failed: {str(e)}")
    
    def select_all_platforms(self):
        for var in self.platform_vars.values():
            var.set(True)
    
    def select_no_platforms(self):
        for var in self.platform_vars.values():
            var.set(False)
    
    def select_adult_platforms(self):
        adult_platforms = ['onlyfans', 'pornhub', 'xvideos', 'xhamster', 'redtube', 'chaturbate', 'cam4', 'myfreecams']
        for platform, var in self.platform_vars.items():
            var.set(platform in adult_platforms)
    
    def select_social_platforms(self):
        social_platforms = ['instagram', 'facebook', 'twitter', 'linkedin', 'github', 'reddit', 'tiktok', 'pinterest', 'snapchat', 'youtube', 'telegram', 'discord']
        for platform, var in self.platform_vars.items():
            var.set(platform in social_platforms)
    
    def select_filehost_platforms(self):
        filehost_platforms = ['doodstream', 'streamtape', 'mixdrop', 'uploadgig', 'rapidgator', 'mega', 'mediafire', 'anonfiles', 'gofile']
        for platform, var in self.platform_vars.items():
            var.set(platform in filehost_platforms)
    
    def log_progress(self, message):
        """Log progress message"""
        timestamp = time.strftime("%H:%M:%S")
        self.progress_text.insert('end', f"[{timestamp}] {message}\n")
        self.progress_text.see('end')
        self.parent.update_idletasks()