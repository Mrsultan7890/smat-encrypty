# Smart-Encrypt v1.0
## Secure Personal Vault

A production-ready cross-platform encrypted notes manager with a futuristic terminal-inspired interface.

### 🔐 Features

- **Military-grade encryption** using Fernet (AES-256) with PBKDF2 key derivation
- **Cross-platform** support (Linux, Android via Termux/Pydroid)
- **Futuristic UI** inspired by edex-ui with neon themes
- **Auto-lock** with configurable timeout (1-30 minutes)
- **Full-text search** across encrypted content
- **Categories** for organizing different types of data
- **Startup chime** (optional) synthesized in Python
- **Secure storage** with owner-only file permissions

### 🚀 Quick Start

#### Linux (including Kali Nethunter)
```bash
# Clone or download the project
cd smart-encrypt

# Make launcher executable
chmod +x run.sh

# Run (installs dependencies automatically)
./run.sh
```

#### Manual Installation
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run application
python3 app.py
```

#### Android (Termux)
```bash
# Install required packages
pkg install python python-tkinter

# Install Python dependencies
pip install cryptography numpy

# Note: Audio may not work on all Android devices
# Set ENABLE_SOUND_BY_DEFAULT = False in gui.py if needed

# Run application
python app.py
```

#### Android (Pydroid 3)
1. Install Pydroid 3 from Google Play
2. Install required libraries via Pydroid's pip
3. Copy project files to Pydroid directory
4. Run `app.py`

### 🎨 Themes

Smart-Encrypt includes three built-in themes:
- **Neon Green** (default) - Classic terminal green
- **Neon Purple** - Cyberpunk purple aesthetic  
- **Monochrome** - Clean black and white

Change themes in Settings after unlocking the vault.

### 🔒 Security Features

#### Encryption
- **Algorithm**: Fernet (AES-256 in CBC mode with HMAC-SHA256)
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 200,000 iterations
- **Salt**: 32-byte random salt per password
- **No plaintext storage**: All sensitive data encrypted before writing to disk

#### Access Control
- **Master password**: Single password protects entire vault
- **Auto-lock**: Configurable timeout (default 5 minutes)
- **Secure deletion**: Attempts to overwrite sensitive data in memory
- **File permissions**: Database files set to owner-only (600)

#### Security Recommendations
1. **Use a strong master password** (12+ characters, mixed case, numbers, symbols)
2. **Regular backups** - Export encrypted backups to secure locations
3. **Keep software updated** - Update dependencies regularly
4. **Secure environment** - Use on trusted devices only
5. **Memory considerations** - Restart application periodically on shared systems

### 📁 Data Storage

Smart-Encrypt stores all data in `~/.smart_encrypt/`:
- `notes.db` - SQLite database with encrypted fields
- Temporary audio files (if sound enabled)

**Database Schema:**
- `categories` - Note categories/folders
- `entries` - Encrypted notes with metadata
- `settings` - Application preferences (encrypted)

### 🎵 Audio Features

Optional startup chime synthesized using NumPy:
- **Harmonic chord progression** (A4, C#5, E5)
- **0.8 second duration** with fade in/out
- **Cross-platform playback** via simpleaudio
- **Disable in settings** if not needed

### 🔧 Configuration

Default settings (modify in source before first run):
```python
DEFAULT_AUTOLOCK_MINUTES = 5
PBKDF2_ITERATIONS = 200000
DEFAULT_THEME = "neon-green"
ENABLE_SOUND_BY_DEFAULT = False
```

### 🧪 Testing

Run the test suite:
```bash
python test_encryption.py
# or
pytest test_encryption.py
```

Tests cover:
- Encryption/decryption functionality
- Password hashing and verification
- Database operations
- Search functionality

### 📱 Platform-Specific Notes

#### Kali Nethunter Rootless
- Works out of the box with standard Python installation
- Audio requires ALSA/PulseAudio support
- File permissions properly enforced

#### Termux (Android)
- Install `python-tkinter` package for GUI support
- Audio may not work on all devices
- Storage location: `/data/data/com.termux/files/home/.smart_encrypt`

#### Pydroid 3 (Android)
- GUI works with built-in tkinter
- Install cryptography and numpy via Pydroid pip
- Limited audio support

### 🚨 Security Warnings

⚠️ **Critical Security Notes:**
- **Single point of failure**: Master password protects everything
- **No password recovery**: Lost password = lost data
- **Memory exposure**: Decrypted data temporarily in RAM
- **Backup responsibility**: No automatic cloud backup
- **Device security**: Secure your device with screen lock/encryption

### 🔄 Backup & Recovery

#### Export Backup
1. Open Smart-Encrypt
2. Go to Settings → Export
3. Choose secure location
4. Use strong export passphrase (different from master password)

#### Import Backup
1. Open Smart-Encrypt
2. Go to Settings → Import
3. Select backup file
4. Enter export passphrase

### 🐛 Troubleshooting

#### Common Issues

**"Missing dependencies" error:**
```bash
pip3 install -r requirements.txt --user
```

**"Permission denied" on database:**
```bash
chmod 600 ~/.smart_encrypt/notes.db
```

**GUI not appearing (Linux):**
```bash
sudo apt-get install python3-tk
```

**Audio not working:**
- Disable sound in settings
- Install system audio libraries
- Check device audio permissions

#### Debug Mode
Run with debug output:
```bash
python3 -u app.py
```

### 📄 License

This project is provided as-is for educational and personal use. 

**Disclaimer**: While Smart-Encrypt uses industry-standard encryption, no software is 100% secure. Use at your own risk and maintain proper backups.

### 🤝 Contributing

This is a minimal production-ready implementation. For additional features:
- Export/Import functionality
- Multiple vault support  
- Cloud sync integration
- Mobile-optimized UI
- Advanced search filters

### 📞 Support

For issues related to:
- **Encryption**: Check cryptography library documentation
- **GUI**: Verify tkinter installation
- **Audio**: Test simpleaudio compatibility
- **Android**: Check Termux/Pydroid specific forums

---

**Remember**: Your master password is the key to everything. Choose wisely and never forget it! 🔐# smat-encrypty
