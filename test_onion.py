#!/usr/bin/env python3
import os
import subprocess
import time

# Create hidden service directory
hidden_dir = '/tmp/test_hidden_service'
os.makedirs(hidden_dir, exist_ok=True)
os.chmod(hidden_dir, 0o700)

# Create simple torrc config
torrc_content = f"""
DataDirectory /tmp/tor_data
HiddenServiceDir {hidden_dir}
HiddenServicePort 80 127.0.0.1:5000
"""

# Write torrc
with open('/tmp/test_torrc', 'w') as f:
    f.write(torrc_content)

# Start tor with custom config
print("Starting Tor with hidden service...")
tor_process = subprocess.Popen([
    'tor', '-f', '/tmp/test_torrc'
], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for hostname file
hostname_file = os.path.join(hidden_dir, 'hostname')
for i in range(30):
    if os.path.exists(hostname_file):
        with open(hostname_file, 'r') as f:
            onion_url = f.read().strip()
            print(f"Generated .onion URL: http://{onion_url}")
            break
    time.sleep(1)
    print(f"Waiting for .onion generation... {i+1}/30")
else:
    print("Failed to generate .onion URL")

# Cleanup
tor_process.terminate()