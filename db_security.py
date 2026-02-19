"""Database Security Extensions for Smart-Encrypt"""
import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime

class SecurityDatabaseManager:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.init_security_tables()
    
    def init_security_tables(self):
        """Initialize all security-related database tables"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        # Browser launch logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browser_logs (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sandbox_method TEXT NOT NULL,
                status TEXT NOT NULL,
                command_used TEXT,
                error_message TEXT
            )
        ''')
        
        # Honeypot event logs
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
        
        # Trapped/quarantined files
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
        
        # Security alerts and notifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                source_module TEXT,
                acknowledged BOOLEAN DEFAULT FALSE,
                metadata TEXT
            )
        ''')
        
        # System access monitoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_monitor (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_type TEXT NOT NULL,
                resource_path TEXT,
                process_name TEXT,
                user_agent TEXT,
                ip_address TEXT,
                success BOOLEAN,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_security_alert(self, alert_type: str, severity: str, title: str, 
                          description: str = None, source_module: str = None, 
                          metadata: Dict = None) -> int:
        """Log a security alert"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_alerts 
            (alert_type, severity, title, description, source_module, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert_type,
            severity,
            title,
            description,
            source_module,
            json.dumps(metadata) if metadata else None
        ))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alert_id
    
    def get_security_alerts(self, unacknowledged_only: bool = False, 
                           limit: int = 100) -> List[Dict]:
        """Retrieve security alerts"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, timestamp, alert_type, severity, title, description, 
                   source_module, acknowledged, metadata
            FROM security_alerts
        '''
        
        if unacknowledged_only:
            query += ' WHERE acknowledged = FALSE'
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        
        cursor.execute(query, (limit,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'timestamp': row[1],
                'alert_type': row[2],
                'severity': row[3],
                'title': row[4],
                'description': row[5],
                'source_module': row[6],
                'acknowledged': bool(row[7]),
                'metadata': json.loads(row[8]) if row[8] else {}
            })
        
        conn.close()
        return alerts
    
    def acknowledge_alert(self, alert_id: int):
        """Mark a security alert as acknowledged"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE security_alerts 
            SET acknowledged = TRUE 
            WHERE id = ?
        ''', (alert_id,))
        
        conn.commit()
        conn.close()
    
    def log_access_attempt(self, access_type: str, resource_path: str = None,
                          process_name: str = None, success: bool = True,
                          metadata: Dict = None):
        """Log system access attempts for monitoring"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_monitor 
            (access_type, resource_path, process_name, success, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            access_type,
            resource_path,
            process_name,
            success,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_access_logs(self, access_type: str = None, 
                       failed_only: bool = False, 
                       limit: int = 200) -> List[Dict]:
        """Retrieve access monitoring logs"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT timestamp, access_type, resource_path, process_name, 
                   success, metadata
            FROM access_monitor
        '''
        
        conditions = []
        params = []
        
        if access_type:
            conditions.append('access_type = ?')
            params.append(access_type)
        
        if failed_only:
            conditions.append('success = FALSE')
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'access_type': row[1],
                'resource_path': row[2],
                'process_name': row[3],
                'success': bool(row[4]),
                'metadata': json.loads(row[5]) if row[5] else {}
            })
        
        conn.close()
        return logs
    
    def get_security_summary(self) -> Dict:
        """Get security summary statistics"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        # Count alerts by severity
        cursor.execute('''
            SELECT severity, COUNT(*) 
            FROM security_alerts 
            GROUP BY severity
        ''')
        alert_counts = dict(cursor.fetchall())
        
        # Count unacknowledged alerts
        cursor.execute('''
            SELECT COUNT(*) 
            FROM security_alerts 
            WHERE acknowledged = FALSE
        ''')
        unacknowledged = cursor.fetchone()[0]
        
        # Count trapped files
        cursor.execute('SELECT COUNT(*) FROM trapped_files')
        trapped_files = cursor.fetchone()[0]
        
        # Count browser launches
        cursor.execute('SELECT COUNT(*) FROM browser_logs')
        browser_launches = cursor.fetchone()[0]
        
        # Count honeypot events
        cursor.execute('SELECT COUNT(*) FROM honeypot_logs')
        honeypot_events = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM security_alerts 
            WHERE timestamp > datetime('now', '-1 day')
        ''')
        recent_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'alert_counts': alert_counts,
            'unacknowledged_alerts': unacknowledged,
            'trapped_files': trapped_files,
            'browser_launches': browser_launches,
            'honeypot_events': honeypot_events,
            'recent_alerts_24h': recent_alerts
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Clean up old security logs"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        tables_to_clean = [
            'browser_logs',
            'honeypot_logs', 
            'access_monitor'
        ]
        
        total_deleted = 0
        
        for table in tables_to_clean:
            cursor.execute(f'''
                DELETE FROM {table} 
                WHERE timestamp < datetime('now', '-{days_to_keep} days')
            ''')
            total_deleted += cursor.rowcount
        
        # Keep acknowledged alerts for longer (1 year)
        cursor.execute('''
            DELETE FROM security_alerts 
            WHERE acknowledged = TRUE 
            AND timestamp < datetime('now', '-365 days')
        ''')
        total_deleted += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return total_deleted