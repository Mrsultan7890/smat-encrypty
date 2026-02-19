"""Advanced Chart Components for Smart-Encrypt"""
import tkinter as tk
import math
import random
import time
from typing import List, Dict, Tuple

class AdvancedCharts:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.animations = {}
        
    def draw_radar_chart(self, x: int, y: int, data: Dict[str, float], radius: int = 100):
        """Draw animated radar/spider chart"""
        categories = list(data.keys())
        values = list(data.values())
        num_categories = len(categories)
        
        if num_categories == 0:
            return
        
        angle_step = 2 * math.pi / num_categories
        
        # Draw background grid
        for i in range(1, 6):
            grid_radius = radius * i / 5
            points = []
            for j in range(num_categories):
                angle = j * angle_step - math.pi/2
                px = x + grid_radius * math.cos(angle)
                py = y + grid_radius * math.sin(angle)
                points.extend([px, py])
            
            if len(points) >= 6:
                self.canvas.create_polygon(points, fill='', outline='#333333', width=1)
        
        # Draw axis lines
        for i in range(num_categories):
            angle = i * angle_step - math.pi/2
            end_x = x + radius * math.cos(angle)
            end_y = y + radius * math.sin(angle)
            
            self.canvas.create_line(x, y, end_x, end_y, fill='#666666', width=1)
            
            # Category labels
            label_x = x + (radius + 30) * math.cos(angle)
            label_y = y + (radius + 30) * math.sin(angle)
            self.canvas.create_text(label_x, label_y, text=categories[i], 
                                  fill='#00ff41', font=('Courier', 8, 'bold'))
        
        # Draw data polygon
        data_points = []
        for i, value in enumerate(values):
            angle = i * angle_step - math.pi/2
            data_radius = radius * (value / 100)  # Assuming values are 0-100
            px = x + data_radius * math.cos(angle)
            py = y + data_radius * math.sin(angle)
            data_points.extend([px, py])
        
        if len(data_points) >= 6:
            self.canvas.create_polygon(data_points, fill='#00ff4140', outline='#00ff41', width=2)
            
            # Draw data points
            for i in range(0, len(data_points), 2):
                px, py = data_points[i], data_points[i+1]
                self.canvas.create_oval(px-3, py-3, px+3, py+3, fill='#00ff41', outline='#ffffff')
    
    def draw_gantt_chart(self, x: int, y: int, tasks: List[Dict], width: int = 400, height: int = 200):
        """Draw Gantt chart for project timeline"""
        if not tasks:
            return
        
        # Chart background
        self.canvas.create_rectangle(x, y, x + width, y + height, 
                                   fill='#001100', outline='#00ff41', width=2)
        
        # Time grid (30 days)
        days = 30
        day_width = width / days
        
        for i in range(0, days + 1, 5):
            grid_x = x + i * day_width
            self.canvas.create_line(grid_x, y, grid_x, y + height, 
                                  fill='#333333', width=1, dash=(2, 2))
            
            if i % 10 == 0:
                self.canvas.create_text(grid_x, y - 10, text=f"Day {i}", 
                                      fill='#00ff41', font=('Courier', 8))
        
        # Draw tasks
        task_height = height / len(tasks)
        colors = ['#ff0040', '#ff8000', '#ffff00', '#00ff80', '#0080ff', '#ff00ff']
        
        for i, task in enumerate(tasks):
            task_y = y + i * task_height
            start_day = task.get('start', 0)
            duration = task.get('duration', 5)
            
            bar_x = x + start_day * day_width
            bar_width = duration * day_width
            color = colors[i % len(colors)]
            
            # Task bar
            self.canvas.create_rectangle(bar_x, task_y + 5, bar_x + bar_width, 
                                       task_y + task_height - 5, 
                                       fill=color, outline='#ffffff', width=1)
            
            # Task label
            self.canvas.create_text(bar_x + bar_width/2, task_y + task_height/2, 
                                  text=task.get('name', f'Task {i+1}'), 
                                  fill='#000000', font=('Courier', 8, 'bold'))
            
            # Progress indicator
            progress = task.get('progress', 0) / 100
            progress_width = bar_width * progress
            self.canvas.create_rectangle(bar_x, task_y + 5, bar_x + progress_width, 
                                       task_y + task_height - 5, 
                                       fill='#ffffff', stipple='gray50')
    
    def draw_tree_diagram(self, x: int, y: int, tree_data: Dict, level: int = 0, max_width: int = 400):
        """Draw hierarchical tree diagram"""
        if not tree_data:
            return
        
        node_width = 80
        node_height = 30
        level_height = 60
        
        # Draw root node
        root_name = tree_data.get('name', 'Root')
        children = tree_data.get('children', [])
        
        # Node rectangle
        self.canvas.create_rectangle(x - node_width//2, y - node_height//2, 
                                   x + node_width//2, y + node_height//2,
                                   fill='#003300', outline='#00ff41', width=2)
        
        # Node text
        self.canvas.create_text(x, y, text=root_name, fill='#00ff41', 
                              font=('Courier', 8, 'bold'))
        
        # Draw children
        if children:
            child_spacing = max_width / len(children)
            start_x = x - max_width//2 + child_spacing//2
            
            for i, child in enumerate(children):
                child_x = start_x + i * child_spacing
                child_y = y + level_height
                
                # Connection line
                self.canvas.create_line(x, y + node_height//2, child_x, child_y - node_height//2,
                                      fill='#00ff41', width=1)
                
                # Recursively draw child
                self.draw_tree_diagram(child_x, child_y, child, level + 1, child_spacing)
    
    def draw_mind_map(self, x: int, y: int, central_topic: str, branches: List[Dict]):
        """Draw mind map visualization"""
        # Central node
        self.canvas.create_oval(x - 40, y - 20, x + 40, y + 20, 
                              fill='#00ff41', outline='#ffffff', width=2)
        self.canvas.create_text(x, y, text=central_topic, fill='#000000', 
                              font=('Courier', 9, 'bold'))
        
        # Branch angles
        if not branches:
            return
        
        angle_step = 2 * math.pi / len(branches)
        
        for i, branch in enumerate(branches):
            angle = i * angle_step
            branch_length = 120
            
            # Branch line
            end_x = x + branch_length * math.cos(angle)
            end_y = y + branch_length * math.sin(angle)
            
            self.canvas.create_line(x + 40 * math.cos(angle), y + 20 * math.sin(angle),
                                  end_x, end_y, fill='#00ff41', width=3)
            
            # Branch node
            node_color = branch.get('color', '#ff8000')
            self.canvas.create_oval(end_x - 25, end_y - 15, end_x + 25, end_y + 15,
                                  fill=node_color, outline='#ffffff', width=2)
            
            # Branch text
            branch_text = branch.get('text', f'Branch {i+1}')
            self.canvas.create_text(end_x, end_y, text=branch_text, fill='#000000',
                                  font=('Courier', 8, 'bold'))
            
            # Sub-branches
            sub_branches = branch.get('sub_branches', [])
            if sub_branches:
                sub_angle_step = math.pi / 3 / len(sub_branches)
                base_sub_angle = angle - math.pi / 6
                
                for j, sub_branch in enumerate(sub_branches):
                    sub_angle = base_sub_angle + j * sub_angle_step
                    sub_length = 60
                    
                    sub_x = end_x + sub_length * math.cos(sub_angle)
                    sub_y = end_y + sub_length * math.sin(sub_angle)
                    
                    # Sub-branch line
                    self.canvas.create_line(end_x, end_y, sub_x, sub_y, 
                                          fill='#ffff00', width=2)
                    
                    # Sub-branch node
                    self.canvas.create_oval(sub_x - 15, sub_y - 10, sub_x + 15, sub_y + 10,
                                          fill='#ffff00', outline='#ffffff', width=1)
                    
                    self.canvas.create_text(sub_x, sub_y, text=sub_branch, fill='#000000',
                                          font=('Courier', 7))
    
    def draw_sankey_diagram(self, x: int, y: int, flows: List[Dict], width: int = 300, height: int = 200):
        """Draw Sankey flow diagram"""
        if not flows:
            return
        
        # Get unique sources and targets
        sources = list(set(flow['source'] for flow in flows))
        targets = list(set(flow['target'] for flow in flows))
        
        source_y_step = height / len(sources) if sources else height
        target_y_step = height / len(targets) if targets else height
        
        # Draw source nodes
        for i, source in enumerate(sources):
            source_y = y + i * source_y_step + source_y_step/2
            self.canvas.create_rectangle(x, source_y - 10, x + 20, source_y + 10,
                                       fill='#00ff41', outline='#ffffff')
            self.canvas.create_text(x - 10, source_y, text=source, anchor='e',
                                  fill='#00ff41', font=('Courier', 8))
        
        # Draw target nodes
        for i, target in enumerate(targets):
            target_y = y + i * target_y_step + target_y_step/2
            self.canvas.create_rectangle(x + width - 20, target_y - 10, x + width, target_y + 10,
                                       fill='#ff8000', outline='#ffffff')
            self.canvas.create_text(x + width + 10, target_y, text=target, anchor='w',
                                  fill='#ff8000', font=('Courier', 8))
        
        # Draw flows
        for flow in flows:
            source_idx = sources.index(flow['source'])
            target_idx = targets.index(flow['target'])
            
            source_y = y + source_idx * source_y_step + source_y_step/2
            target_y = y + target_idx * target_y_step + target_y_step/2
            
            # Flow thickness based on value
            thickness = max(2, flow.get('value', 10) / 5)
            
            # Curved flow line
            mid_x = x + width/2
            
            # Create smooth curve using multiple line segments
            segments = 20
            for i in range(segments):
                t = i / segments
                t_next = (i + 1) / segments
                
                # Bezier curve calculation
                curve_y = source_y + (target_y - source_y) * t
                curve_x = x + 20 + (width - 40) * t
                
                curve_y_next = source_y + (target_y - source_y) * t_next
                curve_x_next = x + 20 + (width - 40) * t_next
                
                self.canvas.create_line(curve_x, curve_y, curve_x_next, curve_y_next,
                                      fill='#00ff4180', width=int(thickness))
    
    def animate_chart_elements(self, chart_type: str):
        """Add animations to chart elements"""
        if chart_type == "pulse":
            self.pulse_animation()
        elif chart_type == "rotate":
            self.rotate_animation()
        elif chart_type == "fade":
            self.fade_animation()
    
    def pulse_animation(self):
        """Create pulsing effect on chart elements"""
        # Implementation for pulsing animation
        pass
    
    def rotate_animation(self):
        """Create rotation effect on circular charts"""
        # Implementation for rotation animation
        pass
    
    def fade_animation(self):
        """Create fade in/out effects"""
        # Implementation for fade animation
        pass