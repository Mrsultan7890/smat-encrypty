"""Honeypot Defense System for Smart-Encrypt"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

class HoneypotDefenseSystem:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.trap_dir = os.path.expanduser('~/.smart_encrypt/trap')
        self.decoy_dir = os.path.expanduser('~/.smart_encrypt/decoy_vault')
        self.init_honeypot_tables()
        self.setup_trap_directories()
        self.create_decoy_vault()
    
    def init_honeypot_tables(self):
        """Initialize honeypot logging tables"""
        import sqlite3
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        # Honeypot events log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS honeypot_logs (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                file_path TEXT,
                file_hash TEXT,
                file_size INTEGER,
                threat_level TEXT,
                action_taken TEXT,
                metadata TEXT
            )
        ''')
        
        # Trapped files registry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trapped_files (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                original_path TEXT,
                trap_path TEXT,
                file_hash TEXT,
                file_size INTEGER,
                mime_type TEXT,
                threat_indicators TEXT,
                quarantine_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_trap_directories(self):
        """Create honeypot trap directories"""
        Path(self.trap_dir).mkdir(parents=True, exist_ok=True)
        Path(self.decoy_dir).mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions
        os.chmod(self.trap_dir, 0o700)
        os.chmod(self.decoy_dir, 0o700)
    
    def create_decoy_vault(self):
        """Create fake vault with dummy data for honeypot"""
        decoy_data = {
            'fake_passwords': [
                {'site': 'facebook.com', 'username': 'john.doe@email.com', 'password': 'password123'},
                {'site': 'gmail.com', 'username': 'jane.smith@gmail.com', 'password': 'mypassword'},
                {'site': 'bank.com', 'username': 'user123', 'password': 'secure123'}
            ],
            'fake_onion_links': [
                'http://3g2upl4pq6kufc4m.onion',  # DuckDuckGo (real but harmless)
                'http://facebookcorewwwi.onion',  # Facebook (real but harmless)
                'http://fake-marketplace-xyz123.onion',  # Fake
                'http://honeypot-trap-abc456.onion'  # Obvious honeypot
            ],
            'fake_crypto_wallets': [
                {'type': 'Bitcoin', 'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'balance': '0.5 BTC'},
                {'type': 'Ethereum', 'address': '0x742d35Cc6634C0532925a3b8D4C0d886E', 'balance': '2.3 ETH'}
            ],
            'fake_research_notes': [
                'Meeting with contact at location X on date Y',
                'Package delivery scheduled for tomorrow',
                'New identity documents ready for pickup'
            ]
        }
        
        decoy_file = os.path.join(self.decoy_dir, 'decoy_vault.json')
        with open(decoy_file, 'w') as f:
            json.dump(decoy_data, f, indent=2)
        
        os.chmod(decoy_file, 0o600)
    
    def analyze_file_threat(self, file_path: str) -> Dict[str, any]:
        """Analyze file for potential threats"""
        threats = []
        threat_level = 'LOW'
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        # Check for double extensions (common malware trick)
        if self._has_double_extension(filename):
            threats.append('Double file extension detected')
            threat_level = 'HIGH'
        
        # Check for suspicious extensions
        suspicious_exts = ['.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js']
        if any(filename.lower().endswith(ext) for ext in suspicious_exts):
            threats.append('Suspicious executable extension')
            threat_level = 'MEDIUM' if threat_level == 'LOW' else threat_level
        
        # Check for hidden extensions in common file types
        if self._has_hidden_executable(filename):
            threats.append('Hidden executable in document')
            threat_level = 'HIGH'
        
        # Check file size anomalies
        if file_size > 100 * 1024 * 1024:  # > 100MB
            threats.append('Unusually large file size')
            threat_level = 'MEDIUM' if threat_level == 'LOW' else threat_level
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path) if os.path.exists(file_path) else None
        
        return {
            'filename': filename,
            'file_path': file_path,
            'file_size': file_size,
            'file_hash': file_hash,
            'threats': threats,
            'threat_level': threat_level,
            'mime_type': mimetypes.guess_type(filename)[0]
        }
    
    def _has_double_extension(self, filename: str) -> bool:
        """Check for double file extensions"""
        dangerous_combos = [
            '.jpg.exe', '.pdf.exe', '.doc.exe', '.txt.exe',
            '.png.scr', '.gif.scr', '.mp3.exe', '.avi.exe',
            '.pdf.scr', '.doc.scr', '.xls.exe'
        ]
        filename_lower = filename.lower()
        return any(combo in filename_lower for combo in dangerous_combos)
    
    def _has_hidden_executable(self, filename: str) -> bool:
        """Check for executables disguised as documents"""
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        filename_lower = filename.lower()
        
        # Check if it appears to be a document but has executable characteristics
        for doc_ext in doc_extensions:
            if doc_ext in filename_lower and filename_lower.endswith('.exe'):
                return True
        
        return False
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None
    
    def trap_suspicious_file(self, file_path: str, source: str = 'unknown') -> Dict[str, any]:
        """Move suspicious file to honeypot trap"""
        analysis = self.analyze_file_threat(file_path)
        
        if analysis['threat_level'] in ['MEDIUM', 'HIGH']:
            # Move file to trap directory
            filename = os.path.basename(file_path)
            trap_path = os.path.join(self.trap_dir, f"trapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
            
            try:
                if os.path.exists(file_path):
                    os.rename(file_path, trap_path)
                    os.chmod(trap_path, 0o600)  # Restrict access
                
                # Log to database
                self._log_trapped_file(analysis, file_path, trap_path, source)
                self._log_honeypot_event('FILE_TRAPPED', file_path, analysis)
                
                return {
                    'trapped': True,
                    'trap_path': trap_path,
                    'threat_level': analysis['threat_level'],
                    'threats': analysis['threats']
                }
            except Exception as e:
                self._log_honeypot_event('TRAP_FAILED', file_path, {'error': str(e)})
                return {'trapped': False, 'error': str(e)}
        
        return {'trapped': False, 'reason': 'No significant threats detected'}
    
    def _log_trapped_file(self, analysis: Dict, original_path: str, trap_path: str, source: str):
        """Log trapped file to database"""
        import sqlite3
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trapped_files 
            (filename, original_path, trap_path, file_hash, file_size, mime_type, threat_indicators)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis['filename'],
            original_path,
            trap_path,
            analysis['file_hash'],
            analysis['file_size'],
            analysis['mime_type'],
            json.dumps(analysis['threats'])
        ))
        
        conn.commit()
        conn.close()
    
    def _log_honeypot_event(self, event_type: str, file_path: str, metadata: Dict):
        """Log honeypot event"""
        import sqlite3
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        file_hash = metadata.get('file_hash')
        file_size = metadata.get('file_size', 0)
        threat_level = metadata.get('threat_level', 'UNKNOWN')
        action_taken = f"File analyzed and {'trapped' if metadata.get('trapped') else 'monitored'}"
        
        cursor.execute('''
            INSERT INTO honeypot_logs 
            (event_type, file_path, file_hash, file_size, threat_level, action_taken, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_type,
            file_path,
            file_hash,
            file_size,
            threat_level,
            action_taken,
            json.dumps(metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def detect_intrusion_attempt(self, access_pattern: Dict) -> Dict[str, any]:
        """Detect potential intrusion attempts"""
        suspicious_indicators = []
        risk_score = 0
        
        # Check for rapid file access
        if access_pattern.get('files_accessed_per_minute', 0) > 10:
            suspicious_indicators.append('Rapid file enumeration detected')
            risk_score += 30
        
        # Check for system file access attempts
        system_paths = ['/etc/passwd', '/etc/shadow', '~/.ssh', '~/.gnupg']
        accessed_paths = access_pattern.get('paths_accessed', [])
        
        for sys_path in system_paths:
            if any(sys_path in path for path in accessed_paths):
                suspicious_indicators.append(f'System file access attempt: {sys_path}')
                risk_score += 40
        
        # Check for credential harvesting patterns
        if access_pattern.get('password_files_accessed', 0) > 3:
            suspicious_indicators.append('Credential harvesting pattern detected')
            risk_score += 50
        
        # Log intrusion attempt
        if risk_score > 50:
            self._log_honeypot_event('INTRUSION_DETECTED', 'multiple_files', {
                'risk_score': risk_score,
                'indicators': suspicious_indicators,
                'access_pattern': access_pattern
            })
        
        return {
            'intrusion_detected': risk_score > 50,
            'risk_score': risk_score,
            'indicators': suspicious_indicators
        }
    
    def get_honeypot_logs(self, limit: int = 100) -> List[Dict]:
        """Retrieve honeypot event logs"""
        import sqlite3
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, event_type, file_path, file_hash, file_size, 
                   threat_level, action_taken, metadata
            FROM honeypot_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'event_type': row[1],
                'file_path': row[2],
                'file_hash': row[3],
                'file_size': row[4],
                'threat_level': row[5],
                'action_taken': row[6],
                'metadata': json.loads(row[7]) if row[7] else {}
            })
        
        conn.close()
        return logs
    
    def get_trapped_files(self) -> List[Dict]:
        """Get list of trapped files"""
        import sqlite3
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, original_path, trap_path, file_hash, file_size,
                   mime_type, threat_indicators, quarantine_date
            FROM trapped_files
            ORDER BY quarantine_date DESC
        ''')
        
        files = []
        for row in cursor.fetchall():
            files.append({
                'filename': row[0],
                'original_path': row[1],
                'trap_path': row[2],
                'file_hash': row[3],
                'file_size': row[4],
                'mime_type': row[5],
                'threats': json.loads(row[6]) if row[6] else [],
                'quarantine_date': row[7]
            })
        
        conn.close()
        return files
    
    def cleanup_old_traps(self, days_old: int = 30):
        """Clean up old trapped files"""
        import sqlite3
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        # Get old trapped files
        cursor.execute('''
            SELECT trap_path FROM trapped_files 
            WHERE quarantine_date < ?
        ''', (cutoff_date.isoformat(),))
        
        old_files = cursor.fetchall()
        
        # Delete physical files
        for (trap_path,) in old_files:
            try:
                if os.path.exists(trap_path):
                    os.remove(trap_path)
            except:
                pass
        
        # Remove from database
        cursor.execute('DELETE FROM trapped_files WHERE quarantine_date < ?', 
                      (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()
        
        return len(old_files)