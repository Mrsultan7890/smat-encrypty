"""Isolated Browser Launcher for Smart-Encrypt"""
import os
import subprocess
import shutil
from typing import Dict, Optional
from datetime import datetime

class IsolatedBrowserLauncher:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.tor_info_override = None  # For manual path selection
        self.init_browser_logs_table()
    
    def init_browser_logs_table(self):
        """Initialize browser logs table in SQLite"""
        import sqlite3
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
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
        
        conn.commit()
        conn.close()
    
    def detect_tor_browser(self) -> Dict[str, any]:
        """Detect if Tor Browser is installed on the system"""
        tor_paths = [
            '/usr/bin/torbrowser-launcher',
            '/usr/bin/tor-browser',
            '/opt/tor-browser/start-tor-browser',
            os.path.expanduser('~/tor-browser/start-tor-browser'),
            os.path.expanduser('~/Desktop/tor-browser/start-tor-browser'),
            os.path.expanduser('~/Desktop/tor-browser_en-US/Browser/start-tor-browser'),
            os.path.expanduser('~/Desktop/Tor Browser/start-tor-browser'),
            os.path.expanduser('~/Downloads/tor-browser/start-tor-browser'),
            os.path.expanduser('~/Downloads/tor-browser_en-US/Browser/start-tor-browser'),
            '/Applications/Tor Browser.app/Contents/MacOS/firefox'  # macOS
        ]
        
        # Also search for common Tor Browser folder patterns
        search_dirs = [
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~'),
            '/opt'
        ]
        
        # Search for Tor Browser folders
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                try:
                    for item in os.listdir(search_dir):
                        if 'tor-browser' in item.lower():
                            potential_paths = [
                                os.path.join(search_dir, item, 'start-tor-browser'),
                                os.path.join(search_dir, item, 'Browser', 'start-tor-browser'),
                                os.path.join(search_dir, item, 'tor-browser', 'start-tor-browser')
                            ]
                            tor_paths.extend(potential_paths)
                except:
                    continue
        
        # Check all potential paths
        for path in tor_paths:
            if os.path.exists(path):
                # Make executable if not already
                try:
                    os.chmod(path, 0o755)
                except:
                    pass
                
                if os.access(path, os.X_OK):
                    return {
                        'found': True,
                        'path': path,
                        'type': self._get_browser_type(path)
                    }
        
        # Check if torbrowser-launcher is available via which
        try:
            result = subprocess.run(['which', 'torbrowser-launcher'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {
                    'found': True,
                    'path': result.stdout.strip(),
                    'type': 'torbrowser-launcher'
                }
        except:
            pass
        
        # Manual search in Desktop for any executable files containing 'tor'
        desktop_path = os.path.expanduser('~/Desktop')
        if os.path.exists(desktop_path):
            try:
                for root, dirs, files in os.walk(desktop_path):
                    for file in files:
                        if 'tor' in file.lower() and ('browser' in file.lower() or 'start' in file.lower()):
                            full_path = os.path.join(root, file)
                            if os.access(full_path, os.X_OK):
                                return {
                                    'found': True,
                                    'path': full_path,
                                    'type': 'tor-browser-manual'
                                }
            except:
                pass
        
        return {'found': False, 'path': None, 'type': None}
    
    def _get_browser_type(self, path: str) -> str:
        """Determine browser type from path"""
        if 'torbrowser-launcher' in path:
            return 'torbrowser-launcher'
        elif 'tor-browser' in path:
            return 'tor-browser-bundle'
        elif 'Tor Browser.app' in path:
            return 'tor-browser-macos'
        return 'unknown'
    
    def detect_sandbox_tools(self) -> Dict[str, bool]:
        """Detect available sandboxing tools"""
        tools = {
            'firejail': shutil.which('firejail') is not None,
            'apparmor': os.path.exists('/sys/kernel/security/apparmor'),
            'bubblewrap': shutil.which('bwrap') is not None,
            'systemd-run': shutil.which('systemd-run') is not None
        }
        return tools
    
    def create_firejail_profile(self) -> str:
        """Create custom Firejail profile for Tor Browser"""
        profile_content = """# Firejail profile for Tor Browser isolation
# Restrict file system access
private-home
private-tmp
private-dev
private-etc passwd,group,hostname,hosts,nsswitch.conf,resolv.conf,ssl

# Network restrictions - only allow Tor
net none
netfilter

# Disable dangerous features
noroot
nosound
novideo
nodvd
notv
nou2f

# Disable clipboard access
noclipboard

# Memory and process restrictions
rlimit-nproc 50
rlimit-fsize 1000000000

# Disable X11 forwarding
nox11

# Seccomp filter
seccomp
"""
        profile_path = os.path.expanduser('~/.config/firejail/tor-browser-isolated.profile')
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        with open(profile_path, 'w') as f:
            f.write(profile_content)
        
        return profile_path
    
    def launch_tor_isolated(self) -> Dict[str, any]:
        """Launch Tor Browser in isolated sandbox environment"""
        # Use manual override if available, otherwise detect
        if self.tor_info_override:
            tor_info = self.tor_info_override
            self.tor_info_override = None  # Reset after use
        else:
            tor_info = self.detect_tor_browser()
        
        if not tor_info['found']:
            return self._log_browser_event('None', 'Failed', None, 'Tor Browser not found')
        
        # Detect sandbox tools
        sandbox_tools = self.detect_sandbox_tools()
        
        # Try Firejail first (most comprehensive)
        if sandbox_tools['firejail']:
            return self._launch_with_firejail(tor_info)
        
        # Fallback to bubblewrap
        elif sandbox_tools['bubblewrap']:
            return self._launch_with_bubblewrap(tor_info)
        
        # Fallback to systemd-run (basic isolation)
        elif sandbox_tools['systemd-run']:
            return self._launch_with_systemd(tor_info)
        
        # No sandbox available - show warning
        else:
            return self._log_browser_event('None', 'Failed', None, 
                                         'No sandbox tools available (firejail, bubblewrap, systemd-run)')
    
    def _launch_with_firejail(self, tor_info: Dict) -> Dict[str, any]:
        """Launch Tor Browser with Firejail sandbox"""
        try:
            # Create custom profile
            profile_path = self.create_firejail_profile()
            
            # Build command
            cmd = [
                'firejail',
                '--profile=' + profile_path,
                '--private',  # Private home directory
                '--private-tmp',  # Private /tmp
                '--noroot',  # Drop root privileges
                '--net=none',  # No network (Tor will handle)
                '--nosound',  # Disable audio
                '--novideo',  # Disable video devices
                '--noclipboard',  # Disable clipboard
                '--seccomp',  # Enable seccomp filtering
                tor_info['path']
            ]
            
            # Launch in background
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            return self._log_browser_event('Firejail', 'Success', ' '.join(cmd), None)
            
        except Exception as e:
            return self._log_browser_event('Firejail', 'Failed', None, str(e))
    
    def _launch_with_bubblewrap(self, tor_info: Dict) -> Dict[str, any]:
        """Launch Tor Browser with Bubblewrap sandbox"""
        try:
            cmd = [
                'bwrap',
                '--ro-bind', '/usr', '/usr',
                '--ro-bind', '/lib', '/lib',
                '--ro-bind', '/lib64', '/lib64',
                '--ro-bind', '/bin', '/bin',
                '--ro-bind', '/sbin', '/sbin',
                '--tmpfs', '/tmp',
                '--tmpfs', '/home',
                '--proc', '/proc',
                '--dev', '/dev',
                '--unshare-all',
                '--share-net',  # Allow network for Tor
                tor_info['path']
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            return self._log_browser_event('Bubblewrap', 'Success', ' '.join(cmd), None)
            
        except Exception as e:
            return self._log_browser_event('Bubblewrap', 'Failed', None, str(e))
    
    def _launch_with_systemd(self, tor_info: Dict) -> Dict[str, any]:
        """Launch Tor Browser with systemd-run (basic isolation)"""
        try:
            cmd = [
                'systemd-run',
                '--user',
                '--scope',
                '--property=PrivateNetwork=false',  # Allow network for Tor
                '--property=PrivateTmp=true',
                '--property=ProtectHome=true',
                '--property=ProtectSystem=strict',
                '--property=NoNewPrivileges=true',
                tor_info['path']
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            return self._log_browser_event('systemd-run', 'Success', ' '.join(cmd), None)
            
        except Exception as e:
            return self._log_browser_event('systemd-run', 'Failed', None, str(e))
    
    def _log_browser_event(self, method: str, status: str, command: Optional[str], 
                          error: Optional[str]) -> Dict[str, any]:
        """Log browser launch event to database"""
        import sqlite3
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO browser_logs (sandbox_method, status, command_used, error_message)
            VALUES (?, ?, ?, ?)
        ''', (method, status, command, error))
        
        conn.commit()
        conn.close()
        
        return {
            'method': method,
            'status': status,
            'command': command,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_browser_logs(self, limit: int = 50) -> list:
        """Retrieve browser launch logs"""
        import sqlite3
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, sandbox_method, status, command_used, error_message
            FROM browser_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'method': row[1],
                'status': row[2],
                'command': row[3],
                'error': row[4]
            })
        
        conn.close()
        return logs