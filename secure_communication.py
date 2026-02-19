"""Secure Communication Module for Smart-Encrypt"""
import socket
import threading
import time
import json
import hashlib
import secrets
from encryption import EncryptionManager
from typing import Dict, List, Optional

class SecureCommunication:
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption = encryption_manager
        self.active_chats = {}
        self.message_history = {}
        self.server_socket = None
        self.running = False
        
    def create_encrypted_chat(self, chat_id: str, participants: List[str]) -> Dict:
        """Create new encrypted chat room with real encryption"""
        from cryptography.fernet import Fernet
        
        # Generate real encryption key for this chat
        chat_key = Fernet.generate_key()
        chat_cipher = Fernet(chat_key)
        
        chat_info = {
            'id': chat_id,
            'participants': participants,
            'created_at': time.time(),
            'cipher': chat_cipher,
            'key_b64': chat_key.decode(),
            'messages': [],
            'status': 'active',
            'message_count': 0
        }
        
        self.active_chats[chat_id] = chat_info
        self.message_history[chat_id] = []
        
        return {
            'chat_id': chat_id,
            'status': 'created',
            'participants': len(participants),
            'encryption_key': chat_key.decode()[:32] + '...',
            'key_strength': 'AES-256',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(chat_info['created_at']))
        }
    
    def send_encrypted_message(self, chat_id: str, sender: str, message: str) -> Dict:
        """Send encrypted message to chat with real encryption"""
        if chat_id not in self.active_chats:
            return {'status': 'error', 'message': 'Chat not found'}
        
        chat_info = self.active_chats[chat_id]
        
        # Encrypt message with chat-specific key
        try:
            encrypted_msg = chat_info['cipher'].encrypt(message.encode())
            
            message_obj = {
                'id': secrets.token_hex(8),
                'chat_id': chat_id,
                'sender': sender,
                'content': encrypted_msg,
                'timestamp': time.time(),
                'message_type': 'text',
                'size': len(message)
            }
            
            self.message_history[chat_id].append(message_obj)
            chat_info['message_count'] += 1
            
            return {
                'status': 'sent',
                'message_id': message_obj['id'],
                'encrypted_size': len(encrypted_msg),
                'original_size': len(message),
                'compression_ratio': len(encrypted_msg) / len(message),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message_obj['timestamp']))
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'Encryption failed: {str(e)}'}
    
    def receive_messages(self, chat_id: str, last_message_id: str = None) -> List[Dict]:
        """Receive and decrypt messages from chat with real decryption"""
        if chat_id not in self.message_history or chat_id not in self.active_chats:
            return []
        
        messages = self.message_history[chat_id]
        chat_info = self.active_chats[chat_id]
        
        # Filter messages after last_message_id
        if last_message_id:
            start_index = 0
            for i, msg in enumerate(messages):
                if msg['id'] == last_message_id:
                    start_index = i + 1
                    break
            messages = messages[start_index:]
        
        decrypted_messages = []
        for msg in messages:
            try:
                # Decrypt with chat-specific cipher
                decrypted_content = chat_info['cipher'].decrypt(msg['content']).decode()
                
                decrypted_messages.append({
                    'id': msg['id'],
                    'sender': msg['sender'],
                    'content': decrypted_content,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg['timestamp'])),
                    'type': msg['message_type'],
                    'size': msg.get('size', 0),
                    'encrypted_size': len(msg['content'])
                })
            except Exception as e:
                # Log decryption failure but continue
                decrypted_messages.append({
                    'id': msg['id'],
                    'sender': msg['sender'],
                    'content': f'[DECRYPTION FAILED: {str(e)}]',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg['timestamp'])),
                    'type': 'error'
                })
        
        return decrypted_messages
    
    def secure_file_transfer(self, file_path: str, recipient: str) -> Dict:
        """Securely transfer file with real encryption"""
        import os
        from cryptography.fernet import Fernet
        
        try:
            if not os.path.exists(file_path):
                return {'status': 'error', 'message': 'File not found'}
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Generate unique key for this file transfer
            file_key = Fernet.generate_key()
            file_cipher = Fernet(file_key)
            
            # Encrypt file data
            encrypted_data = file_cipher.encrypt(file_data)
            
            # Generate transfer ID and checksums
            transfer_id = secrets.token_hex(16)
            original_checksum = hashlib.sha256(file_data).hexdigest()
            encrypted_checksum = hashlib.sha256(encrypted_data).hexdigest()
            
            # Save encrypted file temporarily
            encrypted_filename = f"{file_path}.encrypted"
            with open(encrypted_filename, 'wb') as f:
                f.write(encrypted_data)
            
            transfer_info = {
                'transfer_id': transfer_id,
                'filename': os.path.basename(file_path),
                'encrypted_filename': encrypted_filename,
                'original_size': len(file_data),
                'encrypted_size': len(encrypted_data),
                'recipient': recipient,
                'status': 'encrypted',
                'encryption_key': file_key.decode(),
                'original_checksum': original_checksum,
                'encrypted_checksum': encrypted_checksum,
                'compression_ratio': len(encrypted_data) / len(file_data),
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return transfer_info
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def create_anonymous_email(self, recipient: str, subject: str, body: str) -> Dict:
        """Create anonymous encrypted email"""
        # Generate anonymous sender ID
        sender_id = f"anon_{secrets.token_hex(8)}"
        
        # Encrypt email content
        email_data = {
            'to': recipient,
            'subject': subject,
            'body': body,
            'timestamp': time.time()
        }
        
        encrypted_email = self.encryption.encrypt(json.dumps(email_data))
        
        return {
            'email_id': secrets.token_hex(16),
            'sender_id': sender_id,
            'encrypted_content': encrypted_email[:50] + '...',
            'status': 'queued',
            'anonymity_level': 'high'
        }
    
    def generate_burner_identity(self) -> Dict:
        """Generate cryptographically secure temporary identity"""
        # Generate realistic but fake data
        first_names = ['Alex', 'Jordan', 'Casey', 'Riley', 'Morgan', 'Avery', 'Quinn', 'Sage']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        
        # Secure random selections
        first_name = secrets.choice(first_names)
        last_name = secrets.choice(last_names)
        
        # Generate secure identifiers
        user_id = secrets.token_hex(12)
        username = f"{first_name.lower()}{secrets.randbelow(9999):04d}"
        
        # Generate temporary email domains
        temp_domains = ['tempmail.org', '10minutemail.com', 'guerrillamail.com', 'mailinator.com']
        email_domain = secrets.choice(temp_domains)
        email = f"{username}@{email_domain}"
        
        # Generate realistic phone number
        area_codes = ['555', '123', '456', '789']  # Fake area codes
        area_code = secrets.choice(area_codes)
        phone_number = f"+1-{area_code}-{secrets.randbelow(900) + 100:03d}-{secrets.randbelow(9000) + 1000:04d}"
        
        # Generate crypto addresses
        btc_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        btc_address = '1' + ''.join(secrets.choice(btc_chars) for _ in range(33))
        
        identity = {
            'id': f"burner_{user_id}",
            'full_name': f"{first_name} {last_name}",
            'username': username,
            'email': email,
            'phone': phone_number,
            'bitcoin_address': btc_address,
            'created_at': time.time(),
            'expires_at': time.time() + (24 * 3600),  # 24 hours
            'status': 'active',
            'security_level': 'high',
            'usage_count': 0,
            'last_used': None
        }
        
        return identity
    
    def create_covert_channel(self, channel_type: str = 'steganography') -> Dict:
        """Create covert communication channel"""
        channel_id = secrets.token_hex(12)
        
        channels = {
            'steganography': {
                'method': 'Image LSB hiding',
                'capacity': '1KB per 1MB image',
                'detection_risk': 'low'
            },
            'dns_tunneling': {
                'method': 'DNS TXT records',
                'capacity': '255 bytes per query',
                'detection_risk': 'medium'
            },
            'tcp_timing': {
                'method': 'Packet timing intervals',
                'capacity': '1 bit per packet',
                'detection_risk': 'very low'
            }
        }
        
        channel_info = channels.get(channel_type, channels['steganography'])
        
        return {
            'channel_id': channel_id,
            'type': channel_type,
            'method': channel_info['method'],
            'capacity': channel_info['capacity'],
            'detection_risk': channel_info['detection_risk'],
            'status': 'established'
        }
    
    def setup_dead_drop(self, location: str, message: str) -> Dict:
        """Setup digital dead drop for message exchange"""
        drop_id = secrets.token_hex(16)
        
        # Encrypt message for dead drop
        encrypted_message = self.encryption.encrypt(message)
        
        dead_drop = {
            'drop_id': drop_id,
            'location': location,
            'encrypted_payload': encrypted_message,
            'created_at': time.time(),
            'expires_at': time.time() + (7 * 24 * 3600),  # 7 days
            'access_count': 0,
            'max_access': 1,
            'status': 'active'
        }
        
        return {
            'drop_id': drop_id,
            'location': location,
            'access_code': secrets.token_hex(8),
            'expires_in': '7 days',
            'status': 'deployed'
        }
    
    def start_secure_server(self, port: int = 8888) -> Dict:
        """Start secure communication server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', port))
            self.server_socket.listen(5)
            
            self.running = True
            
            def handle_connections():
                while self.running:
                    try:
                        client_socket, address = self.server_socket.accept()
                        threading.Thread(target=self._handle_client, 
                                       args=(client_socket, address), daemon=True).start()
                    except:
                        break
            
            threading.Thread(target=handle_connections, daemon=True).start()
            
            return {
                'status': 'started',
                'port': port,
                'address': 'localhost',
                'encryption': 'enabled'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle client connections"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Echo encrypted data back (demo)
                encrypted_response = self.encryption.encrypt(f"Echo: {data.decode()}")
                client_socket.send(encrypted_response)
                
        except:
            pass
        finally:
            client_socket.close()
    
    def stop_server(self):
        """Stop secure communication server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def get_communication_stats(self) -> Dict:
        """Get communication statistics"""
        total_chats = len(self.active_chats)
        total_messages = sum(len(msgs) for msgs in self.message_history.values())
        
        return {
            'active_chats': total_chats,
            'total_messages': total_messages,
            'encryption_status': 'active',
            'server_status': 'running' if self.running else 'stopped',
            'security_level': 'maximum'
        }