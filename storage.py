"""Storage module for Smart-Encrypt"""
import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from encryption import EncryptionManager

class StorageManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.smart_encrypt")
        
        Path(data_dir).mkdir(exist_ok=True)
        os.chmod(data_dir, 0o700)
        
        self.db_path = os.path.join(data_dir, "notes.db")
        self.encryption = EncryptionManager()
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        os.chmod(self.db_path, 0o600)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                category_id INTEGER,
                title_encrypted BLOB NOT NULL,
                content_encrypted BLOB NOT NULL,
                meta_json_encrypted BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value_encrypted BLOB
            )
        ''')
        
        # Default categories
        defaults = ['Personal', 'Credentials', 'Onion Links', 'Research']
        for cat in defaults:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
        
        conn.commit()
        conn.close()
    
    def set_master_password(self, password: str):
        password_hash = self.encryption.hash_password(password)
        self.encryption.initialize(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value_encrypted) VALUES (?, ?)', 
                      ('password_hash', password_hash.encode()))
        cursor.execute('INSERT OR REPLACE INTO settings (key, value_encrypted) VALUES (?, ?)', 
                      ('salt', self.encryption.salt))
        conn.commit()
        conn.close()
    
    def verify_master_password(self, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value_encrypted FROM settings WHERE key = ?', ('password_hash',))
        hash_result = cursor.fetchone()
        cursor.execute('SELECT value_encrypted FROM settings WHERE key = ?', ('salt',))
        salt_result = cursor.fetchone()
        
        conn.close()
        
        if not hash_result or not salt_result:
            return False
        
        stored_hash = hash_result[0].decode()
        salt = salt_result[0]
        
        if self.encryption.verify_password(password, stored_hash):
            self.encryption.initialize(password, salt)
            return True
        return False
    
    def is_first_run(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value_encrypted FROM settings WHERE key = ?', ('password_hash',))
        result = cursor.fetchone()
        conn.close()
        return result is None
    
    def add_entry(self, category_id: int, title: str, content: str, meta: Dict = None) -> int:
        encrypted_title = self.encryption.encrypt(title)
        encrypted_content = self.encryption.encrypt(content)
        encrypted_meta = self.encryption.encrypt(json.dumps(meta or {}))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (category_id, title_encrypted, content_encrypted, meta_json_encrypted)
            VALUES (?, ?, ?, ?)
        ''', (category_id, encrypted_title, encrypted_content, encrypted_meta))
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id
    
    def get_entries(self, category_id: int = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category_id:
            cursor.execute('''
                SELECT e.id, e.category_id, e.title_encrypted, e.content_encrypted, 
                       e.meta_json_encrypted, e.created_at, e.updated_at, c.name
                FROM entries e JOIN categories c ON e.category_id = c.id
                WHERE e.category_id = ?
                ORDER BY e.updated_at DESC
            ''', (category_id,))
        else:
            cursor.execute('''
                SELECT e.id, e.category_id, e.title_encrypted, e.content_encrypted, 
                       e.meta_json_encrypted, e.created_at, e.updated_at, c.name
                FROM entries e JOIN categories c ON e.category_id = c.id
                ORDER BY e.updated_at DESC
            ''')
        
        entries = []
        for row in cursor.fetchall():
            try:
                entry = {
                    'id': row[0],
                    'category_id': row[1],
                    'title': self.encryption.decrypt(row[2]),
                    'content': self.encryption.decrypt(row[3]),
                    'meta': json.loads(self.encryption.decrypt(row[4])),
                    'created_at': row[5],
                    'updated_at': row[6],
                    'category_name': row[7]
                }
                entries.append(entry)
            except:
                continue
        
        conn.close()
        return entries
    
    def search_entries(self, query: str) -> List[Dict]:
        entries = self.get_entries()
        results = []
        query_lower = query.lower()
        
        for entry in entries:
            if (query_lower in entry['title'].lower() or 
                query_lower in entry['content'].lower()):
                results.append(entry)
        
        return results
    
    def delete_entry(self, entry_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        conn.commit()
        conn.close()
    
    def get_categories(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM categories ORDER BY name')
        categories = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def add_category(self, name: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value_encrypted FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                return self.encryption.decrypt(result[0])
            except:
                pass
        return default
    
    def set_setting(self, key: str, value: str):
        encrypted_value = self.encryption.encrypt(value)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value_encrypted) VALUES (?, ?)', 
                      (key, encrypted_value))
        conn.commit()
        conn.close()