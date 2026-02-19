"""Data Visualization Module for Smart-Encrypt"""
import tkinter as tk
from tkinter import ttk
import math
import random
import time
from typing import List, Dict, Tuple

class DataVisualizer:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = None
        self.animation_running = False
        
    def create_security_dashboard(self) -> tk.Toplevel:
        """Create security metrics dashboard"""
        dashboard = tk.Toplevel(self.parent)
        dashboard.title("Security Dashboard")
        dashboard.geometry("1000x700")
        dashboard.configure(bg='#000000')
        
        # Header
        tk.Label(dashboard, text="◉ SECURITY METRICS DASHBOARD ◉", 
                bg='#000000', fg='#00ff41', font=('Courier', 16, 'bold')).pack(pady=10)
        
        # Main canvas for visualizations
        self.canvas = tk.Canvas(dashboard, bg='#000000', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = tk.Frame(dashboard, bg='#000000')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(control_frame, text="📊 THREAT CHART", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=self.draw_threat_chart).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="🌐 NETWORK MAP", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=self.draw_network_diagram).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="📈 ACTIVITY GRAPH", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=self.draw_activity_timeline).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="🔥 HEAT MAP", bg='#003300', fg='#00ff41',
                 font=('Courier', 9, 'bold'), command=self.draw_heat_map).pack(side=tk.LEFT, padx=5)
        
        return dashboard
    
    def draw_threat_chart(self):
        """Draw animated threat level pie chart"""
        self.canvas.delete("all")
        
        # Mock threat data
        threats = [
            ("Malware", 35, "#ff0040"),
            ("Phishing", 25, "#ff8000"),
            ("Exploits", 20, "#ffff00"),
            ("Social Eng", 15, "#00ff80"),
            ("Other", 5, "#0080ff")
        ]
        
        center_x, center_y = 200, 200
        radius = 120
        start_angle = 0
        
        # Draw pie chart
        for name, percentage, color in threats:
            extent = (percentage / 100) * 360
            
            # Draw pie slice
            self.canvas.create_arc(center_x - radius, center_y - radius,
                                 center_x + radius, center_y + radius,
                                 start=start_angle, extent=extent,
                                 fill=color, outline='#ffffff', width=2)
            
            # Draw label
            label_angle = math.radians(start_angle + extent/2)
            label_x = center_x + (radius + 40) * math.cos(label_angle)
            label_y = center_y + (radius + 40) * math.sin(label_angle)
            
            self.canvas.create_text(label_x, label_y, text=f"{name}\n{percentage}%",
                                  fill='#00ff41', font=('Courier', 9, 'bold'))
            
            start_angle += extent
        
        # Center title
        self.canvas.create_text(center_x, center_y, text="THREAT\nLEVELS",
                              fill='#ffffff', font=('Courier', 12, 'bold'))
        
        # Draw security score gauge
        self.draw_security_gauge(500, 200, 85)
        
        # Draw threat timeline
        self.draw_mini_timeline(650, 50)
    
    def draw_security_gauge(self, x: int, y: int, score: int):
        """Draw animated security score gauge"""
        radius = 80
        
        # Draw gauge background
        self.canvas.create_arc(x - radius, y - radius, x + radius, y + radius,
                             start=0, extent=180, outline='#333333', width=8, style='arc')
        
        # Draw score arc
        score_extent = (score / 100) * 180
        color = '#00ff41' if score > 70 else '#ffff00' if score > 40 else '#ff0040'
        
        self.canvas.create_arc(x - radius, y - radius, x + radius, y + radius,
                             start=0, extent=score_extent, outline=color, width=8, style='arc')
        
        # Draw needle
        needle_angle = math.radians(score_extent)
        needle_x = x + (radius - 20) * math.cos(needle_angle)
        needle_y = y + (radius - 20) * math.sin(needle_angle)
        
        self.canvas.create_line(x, y, needle_x, needle_y, fill='#ffffff', width=3)
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='#ffffff', outline='#ffffff')
        
        # Labels
        self.canvas.create_text(x, y + 30, text=f"SECURITY SCORE\n{score}%",
                              fill='#00ff41', font=('Courier', 10, 'bold'))
    
    def draw_network_diagram(self):
        """Draw animated network topology"""
        self.canvas.delete("all")
        
        # Network nodes
        nodes = [
            ("FIREWALL", 150, 100, "#ff0040"),
            ("ROUTER", 300, 150, "#00ff41"),
            ("SERVER", 450, 100, "#0080ff"),
            ("CLIENT1", 200, 250, "#ffff00"),
            ("CLIENT2", 400, 250, "#ff8000"),
            ("DATABASE", 550, 200, "#ff00ff")
        ]
        
        # Draw connections
        connections = [
            (0, 1), (1, 2), (1, 3), (1, 4), (2, 5)
        ]
        
        for start, end in connections:
            x1, y1 = nodes[start][1], nodes[start][2]
            x2, y2 = nodes[end][1], nodes[end][2]
            
            # Animated connection line
            self.canvas.create_line(x1, y1, x2, y2, fill='#00ff41', width=2, dash=(5, 5))
            
            # Data flow animation (mock)
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
            self.canvas.create_oval(mid_x-3, mid_y-3, mid_x+3, mid_y+3, 
                                  fill='#ffffff', outline='#ffffff')
        
        # Draw nodes
        for name, x, y, color in nodes:
            # Node circle
            self.canvas.create_oval(x-25, y-25, x+25, y+25, 
                                  fill=color, outline='#ffffff', width=2)
            
            # Node label
            self.canvas.create_text(x, y, text=name, fill='#000000', 
                                  font=('Courier', 8, 'bold'))
            
            # Status indicator
            status_color = random.choice(['#00ff41', '#ffff00', '#ff0040'])
            self.canvas.create_oval(x+20, y-20, x+30, y-10, 
                                  fill=status_color, outline=status_color)
        
        # Network stats
        self.draw_network_stats(650, 50)
    
    def draw_activity_timeline(self):
        """Draw activity timeline graph"""
        self.canvas.delete("all")
        
        # Timeline data (mock)
        hours = list(range(24))
        activity = [random.randint(10, 100) for _ in hours]
        
        # Graph dimensions
        graph_x, graph_y = 50, 50
        graph_w, graph_h = 600, 300
        
        # Draw axes
        self.canvas.create_line(graph_x, graph_y + graph_h, 
                              graph_x + graph_w, graph_y + graph_h, 
                              fill='#00ff41', width=2)
        self.canvas.create_line(graph_x, graph_y, graph_x, graph_y + graph_h, 
                              fill='#00ff41', width=2)
        
        # Draw grid
        for i in range(0, 101, 20):
            y = graph_y + graph_h - (i * graph_h / 100)
            self.canvas.create_line(graph_x, y, graph_x + graph_w, y, 
                                  fill='#333333', width=1, dash=(2, 2))
            self.canvas.create_text(graph_x - 20, y, text=f"{i}%", 
                                  fill='#00ff41', font=('Courier', 8))
        
        # Draw activity bars
        bar_width = graph_w / len(hours)
        for i, value in enumerate(activity):
            x = graph_x + i * bar_width
            bar_height = (value / 100) * graph_h
            y = graph_y + graph_h - bar_height
            
            # Color based on activity level
            color = '#ff0040' if value > 80 else '#ffff00' if value > 50 else '#00ff41'
            
            self.canvas.create_rectangle(x, y, x + bar_width - 2, graph_y + graph_h,
                                       fill=color, outline=color)
            
            # Hour labels
            if i % 4 == 0:
                self.canvas.create_text(x + bar_width/2, graph_y + graph_h + 20, 
                                      text=f"{i:02d}:00", fill='#00ff41', 
                                      font=('Courier', 8))
        
        # Title and labels
        self.canvas.create_text(graph_x + graph_w/2, graph_y - 20, 
                              text="24-HOUR ACTIVITY TIMELINE", 
                              fill='#00ff41', font=('Courier', 12, 'bold'))
        
        # Draw threat events
        self.draw_threat_events(graph_x, graph_y, graph_w, graph_h)
    
    def draw_heat_map(self):
        """Draw security heat map"""
        self.canvas.delete("all")
        
        # Heat map grid
        grid_size = 20
        cell_size = 25
        start_x, start_y = 50, 50
        
        # Generate heat data
        heat_data = [[random.randint(0, 100) for _ in range(grid_size)] for _ in range(grid_size)]
        
        for row in range(grid_size):
            for col in range(grid_size):
                x = start_x + col * cell_size
                y = start_y + row * cell_size
                
                intensity = heat_data[row][col]
                
                # Color based on intensity
                if intensity > 80:
                    color = '#ff0040'
                elif intensity > 60:
                    color = '#ff8000'
                elif intensity > 40:
                    color = '#ffff00'
                elif intensity > 20:
                    color = '#80ff00'
                else:
                    color = '#00ff41'
                
                self.canvas.create_rectangle(x, y, x + cell_size, y + cell_size,
                                           fill=color, outline='#000000', width=1)
        
        # Legend
        self.draw_heat_legend(600, 100)
        
        # Title
        self.canvas.create_text(300, 20, text="SECURITY THREAT HEAT MAP", 
                              fill='#00ff41', font=('Courier', 14, 'bold'))
    
    def draw_mini_timeline(self, x: int, y: int):
        """Draw mini threat timeline"""
        events = [
            ("Malware Detected", "#ff0040"),
            ("Login Attempt", "#ffff00"),
            ("File Access", "#00ff41"),
            ("Network Scan", "#ff8000"),
            ("System Update", "#0080ff")
        ]
        
        self.canvas.create_text(x, y, text="RECENT EVENTS", 
                              fill='#00ff41', font=('Courier', 10, 'bold'))
        
        for i, (event, color) in enumerate(events):
            event_y = y + 30 + i * 25
            
            # Event indicator
            self.canvas.create_oval(x - 100, event_y - 5, x - 90, event_y + 5,
                                  fill=color, outline=color)
            
            # Event text
            self.canvas.create_text(x - 80, event_y, text=event, anchor='w',
                                  fill='#ffffff', font=('Courier', 8))
            
            # Timestamp
            timestamp = f"{random.randint(1, 23):02d}:{random.randint(0, 59):02d}"
            self.canvas.create_text(x + 50, event_y, text=timestamp,
                                  fill='#666666', font=('Courier', 8))
    
    def draw_network_stats(self, x: int, y: int):
        """Draw network statistics"""
        stats = [
            ("Packets/sec", random.randint(1000, 9999)),
            ("Bandwidth", f"{random.randint(10, 99)} Mbps"),
            ("Connections", random.randint(50, 500)),
            ("Blocked IPs", random.randint(10, 100))
        ]
        
        self.canvas.create_text(x, y, text="NETWORK STATS", 
                              fill='#00ff41', font=('Courier', 10, 'bold'))
        
        for i, (label, value) in enumerate(stats):
            stat_y = y + 30 + i * 25
            
            self.canvas.create_text(x - 50, stat_y, text=f"{label}:", anchor='w',
                                  fill='#ffffff', font=('Courier', 9))
            self.canvas.create_text(x + 50, stat_y, text=str(value), anchor='w',
                                  fill='#00ff41', font=('Courier', 9, 'bold'))
    
    def draw_threat_events(self, graph_x: int, graph_y: int, graph_w: int, graph_h: int):
        """Draw threat event markers on timeline"""
        threat_times = [2, 8, 14, 18, 22]  # Hours when threats occurred
        
        for hour in threat_times:
            x = graph_x + (hour / 24) * graph_w
            
            # Threat marker
            self.canvas.create_line(x, graph_y, x, graph_y + graph_h, 
                                  fill='#ff0040', width=2, dash=(3, 3))
            
            # Threat icon
            self.canvas.create_text(x, graph_y - 10, text="⚠", 
                                  fill='#ff0040', font=('Courier', 12, 'bold'))
    
    def draw_heat_legend(self, x: int, y: int):
        """Draw heat map legend"""
        colors = ['#00ff41', '#80ff00', '#ffff00', '#ff8000', '#ff0040']
        labels = ['Low', 'Med-Low', 'Medium', 'Med-High', 'High']
        
        self.canvas.create_text(x, y, text="THREAT LEVEL", 
                              fill='#00ff41', font=('Courier', 10, 'bold'))
        
        for i, (color, label) in enumerate(zip(colors, labels)):
            legend_y = y + 30 + i * 20
            
            # Color box
            self.canvas.create_rectangle(x - 30, legend_y - 8, x - 10, legend_y + 8,
                                       fill=color, outline='#ffffff')
            
            # Label
            self.canvas.create_text(x - 5, legend_y, text=label, anchor='w',
                                  fill='#ffffff', font=('Courier', 8))
    
    def create_flow_chart(self) -> tk.Toplevel:
        """Create security process flow chart"""
        flow_window = tk.Toplevel(self.parent)
        flow_window.title("Security Process Flow")
        flow_window.geometry("800x600")
        flow_window.configure(bg='#000000')
        
        canvas = tk.Canvas(flow_window, bg='#000000', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Flow chart nodes
        nodes = [
            ("START", 100, 50, "#00ff41"),
            ("SCAN", 100, 150, "#0080ff"),
            ("ANALYZE", 100, 250, "#ffff00"),
            ("THREAT?", 250, 250, "#ff8000"),
            ("BLOCK", 400, 200, "#ff0040"),
            ("ALLOW", 400, 300, "#00ff41"),
            ("LOG", 250, 400, "#ff00ff"),
            ("END", 100, 500, "#00ff41")
        ]
        
        # Draw nodes
        for name, x, y, color in nodes:
            if name == "THREAT?":
                # Diamond for decision
                points = [x, y-20, x+40, y, x, y+20, x-40, y]
                canvas.create_polygon(points, fill=color, outline='#ffffff', width=2)
            else:
                # Rectangle for process
                canvas.create_rectangle(x-40, y-15, x+40, y+15, 
                                      fill=color, outline='#ffffff', width=2)
            
            canvas.create_text(x, y, text=name, fill='#000000', 
                             font=('Courier', 8, 'bold'))
        
        # Draw flow arrows
        arrows = [
            (0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6), (6, 7)
        ]
        
        for start, end in arrows:
            x1, y1 = nodes[start][1], nodes[start][2]
            x2, y2 = nodes[end][1], nodes[end][2]
            
            canvas.create_line(x1, y1, x2, y2, fill='#00ff41', width=2, arrow=tk.LAST)
        
        return flow_window