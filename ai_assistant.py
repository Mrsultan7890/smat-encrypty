"""Smart-Encrypt AI Core - Specialized Code Assistant"""
import sqlite3
import os
import re
import ast
import json
import hashlib
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import threading
import time

class CodeIndexer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_files (
                id INTEGER PRIMARY KEY,
                filepath TEXT UNIQUE,
                filename TEXT,
                content TEXT,
                file_hash TEXT,
                last_modified TIMESTAMP,
                file_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_functions (
                id INTEGER PRIMARY KEY,
                file_id INTEGER,
                function_name TEXT,
                class_name TEXT,
                line_start INTEGER,
                line_end INTEGER,
                code_snippet TEXT,
                docstring TEXT,
                FOREIGN KEY (file_id) REFERENCES code_files (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT,
                pattern_text TEXT,
                file_id INTEGER,
                line_number INTEGER,
                FOREIGN KEY (file_id) REFERENCES code_files (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def index_project(self, project_path: str):
        """Index all Python files in the project"""
        for py_file in Path(project_path).glob("*.py"):
            self.index_file(str(py_file))
    
    def index_file(self, filepath: str):
        """Index a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_hash = hashlib.md5(content.encode()).hexdigest()
            filename = os.path.basename(filepath)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if file already indexed with same hash
            cursor.execute('SELECT file_hash FROM code_files WHERE filepath = ?', (filepath,))
            result = cursor.fetchone()
            if result and result[0] == file_hash:
                conn.close()
                return
            
            # Insert/update file
            cursor.execute('''
                INSERT OR REPLACE INTO code_files 
                (filepath, filename, content, file_hash, last_modified, file_type)
                VALUES (?, ?, ?, ?, datetime('now'), 'python')
            ''', (filepath, filename, content, file_hash))
            
            file_id = cursor.lastrowid
            
            # Parse and index functions/classes
            self._parse_python_file(cursor, file_id, content)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error indexing {filepath}: {e}")
    
    def _parse_python_file(self, cursor, file_id: int, content: str):
        """Parse Python file and extract functions/classes"""
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node) or ""
                    class_name = None
                    
                    # Find parent class if any
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            for child in ast.walk(parent):
                                if child is node:
                                    class_name = parent.name
                                    break
                    
                    cursor.execute('''
                        INSERT INTO code_functions 
                        (file_id, function_name, class_name, line_start, line_end, 
                         code_snippet, docstring)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        file_id, node.name, class_name, node.lineno,
                        node.end_lineno or node.lineno + 10,
                        '\n'.join(lines[node.lineno-1:node.end_lineno or node.lineno+10]),
                        docstring
                    ))
                
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node) or ""
                    cursor.execute('''
                        INSERT INTO code_functions 
                        (file_id, function_name, class_name, line_start, line_end, 
                         code_snippet, docstring)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        file_id, f"class_{node.name}", node.name, node.lineno,
                        node.end_lineno or node.lineno + 20,
                        '\n'.join(lines[node.lineno-1:node.end_lineno or node.lineno+20]),
                        docstring
                    ))
        except:
            pass

class SmartEncryptAI:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.db_path = os.path.join(project_path, '.smart_encrypt_ai.db')
        self.indexer = CodeIndexer(self.db_path)
        self.patterns = self._load_patterns()
        self.indexer.index_project(project_path)
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load common code patterns for Smart-Encrypt"""
        return {
            'encryption': [
                'encrypt', 'decrypt', 'fernet', 'pbkdf2', 'hash_password',
                'cryptography', 'aes', 'cipher'
            ],
            'gui': [
                'tkinter', 'tk.', 'messagebox', 'filedialog', 'ttk.',
                'pack', 'grid', 'place', 'configure', 'bind'
            ],
            'database': [
                'sqlite3', 'cursor', 'execute', 'fetchone', 'fetchall',
                'commit', 'close', 'connect'
            ],
            'security': [
                'onion', 'tor', 'honeypot', 'threat', 'malware',
                'phishing', 'scan', 'quarantine'
            ],
            'audio': [
                'sound', 'audio', 'play', 'beep', 'paplay', 'spd-say',
                'numpy', 'wave', 'frequency'
            ]
        }
    
    def search_code(self, query: str) -> List[Dict]:
        """Search for code snippets matching query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search in function names and docstrings
        cursor.execute('''
            SELECT f.function_name, f.class_name, f.code_snippet, 
                   cf.filename, f.line_start
            FROM code_functions f
            JOIN code_files cf ON f.file_id = cf.id
            WHERE f.function_name LIKE ? OR f.docstring LIKE ? OR f.code_snippet LIKE ?
            ORDER BY f.function_name
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'function': row[0],
                'class': row[1],
                'code': row[2],
                'file': row[3],
                'line': row[4]
            })
        
        conn.close()
        return results
    
    def analyze_request(self, user_request: str) -> Dict:
        """Analyze user request and determine intent"""
        request_lower = user_request.lower()
        
        intent = 'unknown'
        category = 'general'
        keywords = []
        
        # Determine intent
        if any(word in request_lower for word in ['add', 'create', 'new', 'implement']):
            intent = 'create'
        elif any(word in request_lower for word in ['fix', 'bug', 'error', 'debug']):
            intent = 'fix'
        elif any(word in request_lower for word in ['modify', 'change', 'update', 'edit']):
            intent = 'modify'
        elif any(word in request_lower for word in ['search', 'find', 'show', 'list']):
            intent = 'search'
        
        # Determine category
        for cat, patterns in self.patterns.items():
            if any(pattern in request_lower for pattern in patterns):
                category = cat
                keywords.extend([p for p in patterns if p in request_lower])
                break
        
        return {
            'intent': intent,
            'category': category,
            'keywords': keywords,
            'original': user_request
        }
    
    def generate_code(self, analysis: Dict) -> str:
        """Generate code based on analysis"""
        intent = analysis['intent']
        category = analysis['category']
        
        if intent == 'create' and category == 'gui':
            return self._generate_gui_code(analysis)
        elif intent == 'create' and category == 'encryption':
            return self._generate_encryption_code(analysis)
        elif intent == 'fix':
            return self._generate_fix_code(analysis)
        else:
            return self._generate_generic_code(analysis)
    
    def _generate_gui_code(self, analysis: Dict) -> str:
        """Generate GUI code snippets"""
        if 'button' in analysis['original'].lower():
            return '''# Add button to GUI
button = tk.Button(
    parent_frame,
    text="New Button",
    bg='#003300',
    fg='#00ff41',
    font=('Courier', 9),
    command=self.button_callback
)
button.pack(pady=2, padx=5)

def button_callback(self):
    """Handle button click"""
    print("Button clicked")
'''
        elif 'window' in analysis['original'].lower():
            return '''# Create new window
new_window = tk.Toplevel(self.root)
new_window.title("New Window")
new_window.geometry("600x400")
new_window.configure(bg='#000000')
new_window.transient(self.root)

# Add content to window
tk.Label(new_window, text="New Window Content", 
         bg='#000000', fg='#00ff41',
         font=('Courier', 12, 'bold')).pack(pady=20)
'''
        else:
            return '''# Generic GUI component
frame = tk.Frame(parent, bg='#000000')
frame.pack(fill=tk.X, padx=20, pady=10)

label = tk.Label(frame, text="Label Text", 
                bg='#000000', fg='#00ff41',
                font=('Courier', 10))
label.pack(anchor='w')
'''
    
    def _generate_encryption_code(self, analysis: Dict) -> str:
        """Generate encryption-related code"""
        return '''# Encryption functionality
from cryptography.fernet import Fernet

def encrypt_data(self, data: str) -> bytes:
    """Encrypt data using Fernet"""
    if not hasattr(self, 'cipher'):
        key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    return self.cipher.encrypt(data.encode())

def decrypt_data(self, encrypted_data: bytes) -> str:
    """Decrypt data using Fernet"""
    return self.cipher.decrypt(encrypted_data).decode()
'''
    
    def _generate_fix_code(self, analysis: Dict) -> str:
        """Generate bug fix suggestions"""
        return '''# Common bug fixes:

# 1. Add try-except for error handling
try:
    # Your code here
    pass
except Exception as e:
    print(f"Error: {e}")

# 2. Check if widget exists before using
if hasattr(self, 'widget') and self.widget.winfo_exists():
    self.widget.configure(...)

# 3. Add null checks
if data is not None and len(data) > 0:
    # Process data
    pass
'''
    
    def _generate_generic_code(self, analysis: Dict) -> str:
        """Generate generic code based on keywords"""
        keywords = analysis['keywords']
        
        if 'audio' in keywords:
            return '''# Audio functionality
def play_sound(self, sound_type: str):
    """Play system sound"""
    try:
        if shutil.which('paplay'):
            subprocess.run(['paplay', sound_file], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Audio error: {e}")
'''
        elif 'database' in keywords:
            return '''# Database operation
def database_operation(self):
    """Perform database operation"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM table_name WHERE condition = ?", (value,))
        results = cursor.fetchall()
        return results
    finally:
        conn.close()
'''
        else:
            return '''# Generic function template
def new_function(self, parameter):
    """Function description"""
    try:
        # Implementation here
        result = parameter
        return result
    except Exception as e:
        print(f"Error in new_function: {e}")
        return None
'''
    
    def process_request(self, user_request: str) -> Dict:
        """Process user request and return response"""
        analysis = self.analyze_request(user_request)
        
        if analysis['intent'] == 'search':
            # Search existing code
            search_results = self.search_code(' '.join(analysis['keywords']))
            return {
                'type': 'search_results',
                'results': search_results[:5],  # Top 5 results
                'analysis': analysis
            }
        else:
            # Generate new code
            generated_code = self.generate_code(analysis)
            return {
                'type': 'code_generation',
                'code': generated_code,
                'analysis': analysis
            }
    
    def suggest_fix(self, error_traceback: str, source_code: str = None) -> str:
        """Suggest fixes for runtime errors"""
        error_lower = error_traceback.lower()
        
        if 'attributeerror' in error_lower:
            return '''# AttributeError Fix:
# Check if object has attribute before using
if hasattr(obj, 'attribute_name'):
    obj.attribute_name
else:
    # Handle missing attribute
    pass
'''
        elif 'keyerror' in error_lower:
            return '''# KeyError Fix:
# Use get() method with default value
value = dictionary.get('key', default_value)

# Or check if key exists
if 'key' in dictionary:
    value = dictionary['key']
'''
        elif 'indexerror' in error_lower:
            return '''# IndexError Fix:
# Check list length before accessing
if len(my_list) > index:
    value = my_list[index]
else:
    # Handle out of bounds
    value = None
'''
        elif 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
            return '''# Import Error Fix:
try:
    import module_name
    MODULE_AVAILABLE = True
except ImportError:
    MODULE_AVAILABLE = False
    print("Module not available, using fallback")

# Use conditional imports
if MODULE_AVAILABLE:
    # Use module functionality
    pass
else:
    # Fallback implementation
    pass
'''
        else:
            return '''# General Error Handling:
try:
    # Your code here
    pass
except SpecificException as e:
    # Handle specific exception
    print(f"Specific error: {e}")
except Exception as e:
    # Handle general exception
    print(f"General error: {e}")
finally:
    # Cleanup code
    pass
'''