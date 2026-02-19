"""Lightweight AI Model for Smart-Encrypt Code Generation"""
import json
import re
import os
from typing import Dict, List, Tuple
import sqlite3

class LightweightCodeModel:
    """Simple rule-based model for code generation - under 1MB"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "smart_encrypt_model.json"
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.context_memory = []
        
    def _load_patterns(self) -> Dict:
        """Load code patterns and rules"""
        return {
            'gui_patterns': {
                'button': {
                    'keywords': ['button', 'click', 'press'],
                    'template': 'button_template',
                    'imports': ['tkinter']
                },
                'window': {
                    'keywords': ['window', 'dialog', 'popup'],
                    'template': 'window_template',
                    'imports': ['tkinter']
                },
                'frame': {
                    'keywords': ['frame', 'container', 'panel'],
                    'template': 'frame_template',
                    'imports': ['tkinter']
                }
            },
            'crypto_patterns': {
                'encrypt': {
                    'keywords': ['encrypt', 'cipher', 'secure'],
                    'template': 'encrypt_template',
                    'imports': ['cryptography.fernet']
                },
                'hash': {
                    'keywords': ['hash', 'digest', 'checksum'],
                    'template': 'hash_template',
                    'imports': ['hashlib']
                }
            },
            'database_patterns': {
                'query': {
                    'keywords': ['select', 'query', 'fetch'],
                    'template': 'query_template',
                    'imports': ['sqlite3']
                },
                'insert': {
                    'keywords': ['insert', 'add', 'create'],
                    'template': 'insert_template',
                    'imports': ['sqlite3']
                }
            },
            'audio_patterns': {
                'play': {
                    'keywords': ['play', 'sound', 'audio', 'beep'],
                    'template': 'audio_template',
                    'imports': ['subprocess']
                }
            }
        }
    
    def _load_templates(self) -> Dict:
        """Load code templates"""
        return {
            'button_template': '''# Create button
{name}_btn = tk.Button(
    {parent},
    text="{text}",
    bg='#003300',
    fg='#00ff41',
    font=('Courier', 9),
    command=self.{callback}
)
{name}_btn.pack(pady=2, padx=5)

def {callback}(self):
    """Handle {name} button click"""
    # TODO: Implement button functionality
    pass''',
            
            'window_template': '''# Create new window
{name}_window = tk.Toplevel(self.root)
{name}_window.title("{title}")
{name}_window.geometry("600x400")
{name}_window.configure(bg='#000000')
{name}_window.transient(self.root)

# Add window content
tk.Label({name}_window, text="{title}", 
         bg='#000000', fg='#00ff41',
         font=('Courier', 14, 'bold')).pack(pady=20)''',
            
            'frame_template': '''# Create frame
{name}_frame = tk.Frame({parent}, bg='#000000')
{name}_frame.pack(fill=tk.{fill}, padx={padx}, pady={pady})

# Add frame content
tk.Label({name}_frame, text="{label}", 
         bg='#000000', fg='#00ff41',
         font=('Courier', 10)).pack(anchor='w')''',
            
            'encrypt_template': '''# Encryption function
def encrypt_{name}(self, data: str) -> bytes:
    """Encrypt data using Fernet"""
    from cryptography.fernet import Fernet
    
    if not hasattr(self, '{name}_cipher'):
        key = Fernet.generate_key()
        self.{name}_cipher = Fernet(key)
    
    return self.{name}_cipher.encrypt(data.encode())

def decrypt_{name}(self, encrypted_data: bytes) -> str:
    """Decrypt data using Fernet"""
    return self.{name}_cipher.decrypt(encrypted_data).decode()''',
            
            'hash_template': '''# Hash function
def hash_{name}(self, data: str) -> str:
    """Generate hash of data"""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()''',
            
            'query_template': '''# Database query
def query_{name}(self, {params}):
    """Query database for {name}"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM {table} WHERE {condition}", ({params},))
        results = cursor.fetchall()
        return results
    finally:
        conn.close()''',
            
            'insert_template': '''# Database insert
def insert_{name}(self, {params}):
    """Insert {name} into database"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO {table} ({columns}) VALUES ({placeholders})", 
                      ({params},))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()''',
            
            'audio_template': '''# Audio function
def play_{name}_sound(self):
    """Play {name} sound"""
    try:
        import subprocess
        import shutil
        
        if shutil.which('paplay'):
            subprocess.run(['paplay', '{sound_file}'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        else:
            print('\\a')  # Terminal bell fallback
    except Exception as e:
        print(f"Audio error: {{e}}")'''
        }
    
    def analyze_intent(self, text: str) -> Dict:
        """Analyze user intent from natural language"""
        text_lower = text.lower()
        
        # Determine action
        action = 'create'
        if any(word in text_lower for word in ['fix', 'debug', 'error', 'bug']):
            action = 'fix'
        elif any(word in text_lower for word in ['modify', 'change', 'update']):
            action = 'modify'
        elif any(word in text_lower for word in ['search', 'find', 'show']):
            action = 'search'
        
        # Determine component type
        component_type = None
        category = None
        
        for cat, patterns in self.patterns.items():
            for comp, pattern_info in patterns.items():
                if any(keyword in text_lower for keyword in pattern_info['keywords']):
                    component_type = comp
                    category = cat.replace('_patterns', '')
                    break
            if component_type:
                break
        
        # Extract parameters
        params = self._extract_parameters(text, component_type)
        
        return {
            'action': action,
            'category': category,
            'component_type': component_type,
            'parameters': params,
            'confidence': self._calculate_confidence(text, component_type)
        }
    
    def _extract_parameters(self, text: str, component_type: str) -> Dict:
        """Extract parameters from text"""
        params = {}
        
        # Extract quoted strings as names/labels
        quotes = re.findall(r'"([^"]*)"', text)
        if quotes:
            params['text'] = quotes[0]
            params['title'] = quotes[0]
            params['label'] = quotes[0]
        
        # Extract common GUI parameters
        if 'parent' in text.lower():
            params['parent'] = 'parent_frame'
        else:
            params['parent'] = 'self.root'
        
        # Default values
        params.setdefault('name', component_type or 'new')
        params.setdefault('text', params['name'].title())
        params.setdefault('title', params['name'].title())
        params.setdefault('label', params['name'].title())
        params.setdefault('callback', f"on_{params['name']}_click")
        params.setdefault('fill', 'X')
        params.setdefault('padx', '20')
        params.setdefault('pady', '10')
        
        return params
    
    def _calculate_confidence(self, text: str, component_type: str) -> float:
        """Calculate confidence score"""
        if not component_type:
            return 0.1
        
        # Count matching keywords
        matches = 0
        total_keywords = 0
        
        for cat, patterns in self.patterns.items():
            if component_type in patterns:
                keywords = patterns[component_type]['keywords']
                total_keywords = len(keywords)
                matches = sum(1 for keyword in keywords if keyword in text.lower())
                break
        
        if total_keywords == 0:
            return 0.5
        
        return min(matches / total_keywords + 0.3, 1.0)
    
    def generate_code(self, intent: Dict) -> str:
        """Generate code based on intent"""
        if intent['confidence'] < 0.3:
            return self._generate_generic_code(intent)
        
        component_type = intent['component_type']
        category = intent['category']
        
        # Find template
        template_name = None
        for cat, patterns in self.patterns.items():
            if category and category in cat and component_type in patterns:
                template_name = patterns[component_type]['template']
                break
        
        if not template_name or template_name not in self.templates:
            return self._generate_generic_code(intent)
        
        # Generate code from template
        template = self.templates[template_name]
        params = intent['parameters']
        
        try:
            generated_code = template.format(**params)
            
            # Add imports if needed
            imports = self._get_required_imports(category, component_type)
            if imports:
                import_lines = '\n'.join(f"import {imp}" for imp in imports)
                generated_code = f"{import_lines}\n\n{generated_code}"
            
            return generated_code
            
        except KeyError as e:
            return f"# Error generating code: Missing parameter {e}\n# Template: {template_name}\n# Parameters: {params}"
    
    def _get_required_imports(self, category: str, component_type: str) -> List[str]:
        """Get required imports for component"""
        for cat, patterns in self.patterns.items():
            if category and category in cat and component_type in patterns:
                return patterns[component_type].get('imports', [])
        return []
    
    def _generate_generic_code(self, intent: Dict) -> str:
        """Generate generic code when specific template not found"""
        action = intent['action']
        params = intent['parameters']
        
        if action == 'create':
            return f'''# Generic {params['name']} implementation
def {params['name']}_function(self):
    """Implement {params['name']} functionality"""
    try:
        # TODO: Add implementation
        result = None
        return result
    except Exception as e:
        print(f"Error in {params['name']}_function: {{e}}")
        return None'''
        
        elif action == 'fix':
            return '''# Common bug fixes:
try:
    # Your code here
    pass
except AttributeError as e:
    # Handle missing attribute
    print(f"Attribute error: {e}")
except KeyError as e:
    # Handle missing key
    print(f"Key error: {e}")
except Exception as e:
    # Handle general error
    print(f"General error: {e}")'''
        
        else:
            return f'''# {action.title()} operation
def {action}_{params['name']}(self):
    """Perform {action} operation on {params['name']}"""
    # TODO: Implement {action} logic
    pass'''
    
    def learn_from_code(self, code: str, context: str = None):
        """Learn patterns from existing code (simple pattern extraction)"""
        # Extract function definitions
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', code)
        
        # Extract class definitions
        classes = re.findall(r'class\s+(\w+)\s*[:\(]', code)
        
        # Extract imports
        imports = re.findall(r'(?:from\s+\S+\s+)?import\s+([^\n]+)', code)
        
        # Store in context memory
        self.context_memory.append({
            'code': code[:500],  # First 500 chars
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'context': context
        })
        
        # Keep only last 50 entries
        if len(self.context_memory) > 50:
            self.context_memory = self.context_memory[-50:]
    
    def get_suggestions(self, partial_code: str) -> List[str]:
        """Get code completion suggestions"""
        suggestions = []
        
        # Common Smart-Encrypt patterns
        if 'tk.' in partial_code:
            suggestions.extend([
                'tk.Button', 'tk.Label', 'tk.Frame', 'tk.Entry',
                'tk.Text', 'tk.Canvas', 'tk.Toplevel'
            ])
        
        if 'self.' in partial_code:
            suggestions.extend([
                'self.root', 'self.storage', 'self.encryption',
                'self.audio_visual', 'self.darkweb'
            ])
        
        if 'cursor.execute' in partial_code:
            suggestions.extend([
                'cursor.fetchone()', 'cursor.fetchall()',
                'conn.commit()', 'conn.close()'
            ])
        
        return suggestions[:10]  # Top 10 suggestions
    
    def save_model(self):
        """Save model state to file"""
        model_data = {
            'patterns': self.patterns,
            'templates': self.templates,
            'context_memory': self.context_memory[-20:]  # Save last 20 entries
        }
        
        with open(self.model_path, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self):
        """Load model state from file"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    model_data = json.load(f)
                
                self.patterns.update(model_data.get('patterns', {}))
                self.templates.update(model_data.get('templates', {}))
                self.context_memory = model_data.get('context_memory', [])
                
            except Exception as e:
                print(f"Error loading model: {e}")