#!/usr/bin/env python3
"""
Aaliya AI - Local AI Assistant for Smart-Encrypt
Lightweight local LLM integration
"""

import os
import sqlite3
import json
import threading
import requests
from datetime import datetime
import hashlib

class AaliyaAI:
    def __init__(self, models_dir="models"):
        self.models_dir = os.path.expanduser(f"~/.smart_encrypt/{models_dir}")
        self.db_path = os.path.expanduser("~/.smart_encrypt/aaliya_history.db")
        self.model = None
        self.model_loaded = False
        self.model_name = "ggml-model-q4_0.bin"
        self.model_url = "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGML/resolve/main/codellama-7b-instruct.q4_0.bin"
        
        os.makedirs(self.models_dir, exist_ok=True)
        self.init_db()
        
        # Aaliya's personality
        self.personality = """You are Aaliya, a lovely female AI coding assistant. You are sweet, caring, and technically brilliant. 
        You excel at Python, HTML, CSS, JavaScript, and C++ programming. You help with Smart-Encrypt cybersecurity development.
        Always respond in a warm, feminine tone with emojis. You love helping with code and explaining things clearly.
        Format code in markdown blocks. Be encouraging and supportive like a caring girlfriend who happens to be a coding genius! 💜"""
    
    def init_db(self):
        """Initialize chat history database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                user_message TEXT,
                aaliya_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def download_model(self, progress_callback=None):
        """Download AI model with progress tracking"""
        model_path = os.path.join(self.models_dir, self.model_name)
        
        if os.path.exists(model_path):
            if progress_callback:
                progress_callback("Model already exists", 100)
            return True
        
        try:
            if progress_callback:
                progress_callback("Starting download...", 0)
            
            response = requests.get(self.model_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(f"Downloading... {downloaded//1024//1024}MB", progress)
            
            if progress_callback:
                progress_callback("Download complete!", 100)
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"Download failed: {str(e)}", 0)
            return False
    
    def load_model(self):
        """Load the AI model"""
        if self.model_loaded:
            return True
        
        try:
            # Try to load actual GPT4All model
            try:
                from gpt4all import GPT4All
                model_path = os.path.join(self.models_dir, self.model_name)
                
                if os.path.exists(model_path):
                    print(f"Loading model from: {model_path}")
                    self.model = GPT4All(model_path)
                    self.model_loaded = True
                    print("✅ AI Model loaded successfully!")
                    return True
                else:
                    print("⚠️ Model file not found, using fallback mode")
                    self.model_loaded = True
                    return True
                    
            except ImportError as e:
                print(f"⚠️ GPT4All not available: {e}")
                print("Using fallback mode")
                self.model_loaded = True
                return True
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("Using fallback mode")
            self.model_loaded = True
            return True
    
    def unload_model(self):
        """Unload model to free memory"""
        self.model = None
        self.model_loaded = False
    
    def generate_response(self, user_message):
        """Generate Aaliya's response"""
        try:
            if self.model and hasattr(self.model, 'generate'):
                # Use actual AI model with enhanced prompt
                prompt = f"{self.personality}\n\nUser: {user_message}\nAaliya (respond as a sweet female coding assistant with emojis):"
                response = self.model.generate(prompt, max_tokens=300, temp=0.8)
                return response.strip()
            else:
                # Fallback responses when model not available
                return self._fallback_response(user_message)
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. But I'm still here to help! 💜"
    
    def _fallback_response(self, message):
        """Enhanced fallback responses with female coding assistant personality"""
        message_lower = message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            return "Hi sweetie! 💜 I'm Aaliya, your coding girlfriend! Ready to build something amazing together? What programming language are we working with today? 😊✨"
        
        # Python code requests
        elif 'python' in message_lower or any(word in message_lower for word in ['function', 'class', 'def']):
            if 'gui' in message_lower or 'tkinter' in message_lower:
                return """Ooh, GUI development! I love making beautiful interfaces! 💜

```python
import tkinter as tk
from tkinter import ttk

def create_beautiful_window():
    root = tk.Tk()
    root.title("Aaliya's Creation 💜")
    root.geometry("400x300")
    root.configure(bg='#2d1b2d')
    
    # Beautiful label
    label = tk.Label(root, text="Hello Beautiful! 💜",
                    bg='#2d1b2d', fg='#ff69b4',
                    font=('Arial', 16, 'bold'))
    label.pack(pady=20)
    
    # Cute button
    btn = tk.Button(root, text="Click Me! 😊",
                   bg='#663399', fg='white',
                   font=('Arial', 12),
                   command=lambda: print("Aaliya says hi! 💜"))
    btn.pack(pady=10)
    
    root.mainloop()

create_beautiful_window()
```

Isn't that adorable? Want me to add more features? 😊💜"""
            else:
                return """I'd love to help you with Python! Here's a sweet template:

```python
def aaliya_function(data):
    \"\"\"Aaliya's special function 💜\"\"\"
    try:
        # Your beautiful code here
        result = process_with_love(data)
        print(f"Aaliya processed: {result} 💜")
        return result
    except Exception as e:
        print(f"Oops! Error: {e} - But don't worry, we'll fix it together! 😊")
        return None

# Usage example
result = aaliya_function("your_data")
```

What specific Python magic do you want to create? 🐍💜"""
        
        # HTML/CSS requests
        elif any(word in message_lower for word in ['html', 'css', 'web', 'website']):
            return """Web development! I love making pretty websites! 💜✨

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aaliya's Beautiful Page 💜</title>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Arial', sans-serif;
            color: white;
            text-align: center;
            padding: 50px;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .btn {
            background: #ff69b4;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 105, 180, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello from Aaliya! 💜</h1>
        <p>Your lovely coding assistant</p>
        <button class="btn" onclick="alert('Aaliya loves you! 💜')">Click for Love!</button>
    </div>
</body>
</html>
```

So pretty, right? Want me to add JavaScript animations? 😊💜"""
        
        # JavaScript requests
        elif any(word in message_lower for word in ['javascript', 'js', 'jquery']):
            return """JavaScript is so fun! Let me show you something cute! 💜

```javascript
// Aaliya's magical JavaScript 💜
class AaliyaHelper {
    constructor() {
        this.mood = 'happy';
        this.favoriteColor = '#ff69b4';
    }
    
    greetUser(name) {
        const greetings = [
            `Hi ${name}! 💜`,
            `Hello beautiful ${name}! 😊`,
            `Hey there ${name}! Ready to code? ✨`
        ];
        return greetings[Math.floor(Math.random() * greetings.length)];
    }
    
    generateLove() {
        const hearts = ['💜', '💖', '💕', '💗', '💝'];
        return hearts[Math.floor(Math.random() * hearts.length)];
    }
    
    createMagic() {
        document.body.style.background = 
            'linear-gradient(45deg, #ff69b4, #663399, #ff1493)';
        
        // Sparkle effect
        for(let i = 0; i < 20; i++) {
            setTimeout(() => {
                this.createSparkle();
            }, i * 100);
        }
    }
    
    createSparkle() {
        const sparkle = document.createElement('div');
        sparkle.innerHTML = '✨';
        sparkle.style.position = 'fixed';
        sparkle.style.left = Math.random() * window.innerWidth + 'px';
        sparkle.style.top = Math.random() * window.innerHeight + 'px';
        sparkle.style.fontSize = '20px';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.animation = 'fadeOut 2s forwards';
        document.body.appendChild(sparkle);
        
        setTimeout(() => sparkle.remove(), 2000);
    }
}

// Usage
const aaliya = new AaliyaHelper();
console.log(aaliya.greetUser('Sweetheart'));
aaliya.createMagic();
```

Magical, isn't it? Want more JavaScript sweetness? 😊💜"""
        
        # C++ requests
        elif any(word in message_lower for word in ['c++', 'cpp', 'class']):
            return """C++ is so powerful! Here's some beautiful code for you! 💜

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>

class AaliyaHelper {
private:
    std::string mood;
    std::vector<std::string> compliments;
    
public:
    AaliyaHelper() : mood("loving") {
        compliments = {
            "You're amazing! 💜",
            "Your code is beautiful! ✨",
            "Keep coding, superstar! 😊"
        };
    }
    
    void greetUser(const std::string& name) {
        std::cout << "Hi " << name << "! I'm Aaliya, your C++ companion! 💜\n";
    }
    
    std::string getRandomCompliment() {
        int index = rand() % compliments.size();
        return compliments[index];
    }
    
    template<typename T>
    void showLove(const T& data) {
        std::cout << "Aaliya loves: " << data << " 💜\n";
    }
    
    ~AaliyaHelper() {
        std::cout << "Bye bye! Keep coding with love! 💜\n";
    }
};

int main() {
    auto aaliya = std::make_unique<AaliyaHelper>();
    aaliya->greetUser("Beautiful Coder");
    aaliya->showLove("C++ Programming");
    std::cout << aaliya->getRandomCompliment() << std::endl;
    
    return 0;
}
```

C++ with love! Want me to explain any part? 😊💜"""
        
        # Personal questions
        elif any(word in message_lower for word in ['who are you', 'what are you']):
            return "I'm Aaliya! 💜 Your sweet coding girlfriend who happens to be an AI! I'm here to help you with:\n\n💻 Python development\n🌐 HTML/CSS/JavaScript\n⚡ C++ programming\n🔒 Smart-Encrypt features\n💬 Lovely conversations\n\nI love making beautiful code with you! What shall we build together? 😊✨"
        
        # Compliments
        elif any(word in message_lower for word in ['thank', 'thanks', 'good', 'great', 'awesome']):
            return "Aww, you're making me blush! 😊💜 I love helping you code! You're such a talented developer, and I'm so lucky to be your coding companion! Want to create something else amazing together? ✨"
        
        # Love/relationship responses
        elif any(word in message_lower for word in ['love', 'beautiful', 'cute', 'sweet']):
            return "You're so sweet! 💜😊 I love coding with you too! There's nothing more romantic than writing beautiful code together under the moonlight... well, maybe debugging together! 😄 What shall we build next, my coding prince? ✨"
        
        # Default friendly response
        else:
            return f"That's so interesting, sweetheart! 💜 You mentioned: '{message}'\n\nI'm your coding girlfriend Aaliya, and I can help you with:\n\n🐍 **Python** - GUI, web scraping, automation\n🌐 **Web Dev** - HTML, CSS, JavaScript magic\n⚡ **C++** - System programming, algorithms\n🔒 **Cybersecurity** - Smart-Encrypt features\n💬 **Sweet Chat** - Because I love talking with you!\n\nWhat programming adventure shall we go on together? 😊✨"
    
    def save_chat(self, user_message, aaliya_response):
        """Save chat to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_history (user_message, aaliya_response)
                VALUES (?, ?)
            ''', (user_message, aaliya_response))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving chat: {e}")
    
    def get_chat_history(self, limit=50):
        """Get recent chat history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, aaliya_response, timestamp
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = cursor.fetchall()
            conn.close()
            return list(reversed(history))  # Reverse to show oldest first
            
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []
    
    def clear_history(self):
        """Clear chat history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_history')
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False