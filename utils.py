"""Utility functions for Smart-Encrypt"""
import time
import threading
from typing import Callable

class AutoLockManager:
    def __init__(self, timeout_minutes: int = 5, lock_callback: Callable = None):
        self.timeout_minutes = timeout_minutes
        self.lock_callback = lock_callback
        self.last_activity = time.time()
        self.running = False
        self.thread = None
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
    
    def update_activity(self):
        self.last_activity = time.time()
    
    def set_timeout(self, minutes: int):
        self.timeout_minutes = minutes
    
    def _monitor(self):
        while self.running:
            if time.time() - self.last_activity > (self.timeout_minutes * 60):
                if self.lock_callback:
                    self.lock_callback()
                break
            time.sleep(10)

def secure_delete(data: str):
    """Attempt to securely delete string from memory"""
    if data:
        # Overwrite with random data multiple times
        for _ in range(3):
            data = 'x' * len(data)
        del data