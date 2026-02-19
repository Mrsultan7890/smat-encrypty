"""Audio Visual Feedback System for Smart-Encrypt"""
import tkinter as tk
import numpy as np
import threading
import time
import random
import math
from typing import Dict, List

try:
    import simpleaudio as sa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Check for system audio commands
import subprocess
import shutil

SYSTEM_AUDIO_AVAILABLE = any([
    shutil.which('paplay'),
    shutil.which('aplay'),
    shutil.which('speaker-test'),
    shutil.which('beep')
])

class AudioVisualFeedback:
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.sample_rate = 22050
        self.enabled = True
        print(f'AudioVisualFeedback initialized - enabled: {self.enabled}')
        self.visual_effects = True
        self.haptic_enabled = False
        self.volume = 0.5
        
    def play_sound_effect(self, effect_type: str):
        """Play various sound effects"""
        print(f'play_sound_effect called: {effect_type}, enabled: {self.enabled}')
        if not self.enabled:
            return
        
        def generate_and_play():
            try:
                if AUDIO_AVAILABLE:
                    # Use simpleaudio if available
                    if effect_type == "click":
                        audio = self.generate_click_sound()
                    elif effect_type == "success":
                        audio = self.generate_success_sound()
                    elif effect_type == "error":
                        audio = self.generate_error_sound()
                    elif effect_type == "notification":
                        audio = self.generate_notification_sound()
                    elif effect_type == "typing":
                        audio = self.generate_typing_sound()
                    elif effect_type == "unlock":
                        audio = self.generate_unlock_sound()
                    elif effect_type == "lock":
                        audio = self.generate_lock_sound()
                    else:
                        return
                    
                    # Apply volume
                    audio = (audio * self.volume * 32767).astype(np.int16)
                    
                    # Play audio
                    play_obj = sa.play_buffer(audio, 1, 2, self.sample_rate)
                    play_obj.wait_done()
                
                elif SYSTEM_AUDIO_AVAILABLE:
                    # Use system audio commands as fallback
                    self._play_system_sound(effect_type)
                    
            except Exception:
                pass
        
        threading.Thread(target=generate_and_play, daemon=True).start()
    
    def generate_click_sound(self) -> np.ndarray:
        """Generate button click sound"""
        duration = 0.05
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Sharp click with quick decay
        frequency = 800
        audio = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 50)
        
        return audio
    
    def generate_success_sound(self) -> np.ndarray:
        """Generate success notification sound"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Rising chord progression
        freq1 = 440  # A4
        freq2 = 554  # C#5
        freq3 = 659  # E5
        
        audio = (np.sin(2 * np.pi * freq1 * t) + 
                np.sin(2 * np.pi * freq2 * t) + 
                np.sin(2 * np.pi * freq3 * t)) / 3
        
        # Fade out
        fade_samples = int(0.1 * self.sample_rate)
        audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return audio
    
    def generate_error_sound(self) -> np.ndarray:
        """Generate error alert sound"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Dissonant low frequency buzz
        freq1 = 200
        freq2 = 150
        
        audio = (np.sin(2 * np.pi * freq1 * t) + 
                np.sin(2 * np.pi * freq2 * t)) / 2
        
        # Add some noise for harshness
        noise = np.random.normal(0, 0.1, len(t))
        audio = audio * 0.8 + noise * 0.2
        
        return audio
    
    def generate_notification_sound(self) -> np.ndarray:
        """Generate gentle notification sound"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Soft bell-like tone
        frequency = 880
        audio = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 3)
        
        # Add harmonics
        audio += 0.3 * np.sin(2 * np.pi * frequency * 2 * t) * np.exp(-t * 5)
        
        return audio
    
    def generate_typing_sound(self) -> np.ndarray:
        """Generate subtle typing sound"""
        duration = 0.02
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Quick mechanical click
        frequency = random.randint(600, 1000)
        audio = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 100)
        
        return audio
    
    def generate_unlock_sound(self) -> np.ndarray:
        """Generate unlock success sound"""
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Ascending melody
        frequencies = [330, 440, 550, 660]
        audio = np.zeros_like(t)
        
        segment_length = len(t) // len(frequencies)
        for i, freq in enumerate(frequencies):
            start_idx = i * segment_length
            end_idx = min((i + 1) * segment_length, len(t))
            segment_t = t[start_idx:end_idx] - t[start_idx]
            
            tone = np.sin(2 * np.pi * freq * segment_t)
            envelope = np.exp(-segment_t * 2)
            audio[start_idx:end_idx] = tone * envelope
        
        return audio
    
    def generate_lock_sound(self) -> np.ndarray:
        """Generate lock sound"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Descending tone
        start_freq = 440
        end_freq = 220
        frequency = start_freq + (end_freq - start_freq) * t / duration
        
        audio = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 2)
        
        return audio
    
    def create_visual_effect(self, widget, effect_type: str):
        """Create visual feedback effects"""
        if not self.visual_effects:
            return
        
        if effect_type == "flash":
            self.flash_effect(widget)
        elif effect_type == "pulse":
            self.pulse_effect(widget)
        elif effect_type == "shake":
            self.shake_effect(widget)
        elif effect_type == "glow":
            self.glow_effect(widget)
        elif effect_type == "ripple":
            self.ripple_effect(widget)
    
    def flash_effect(self, widget):
        """Flash widget background"""
        try:
            original_bg = widget.cget('bg')
            flash_color = '#ffffff'
            
            def flash_sequence():
                for _ in range(3):
                    if widget.winfo_exists():
                        widget.configure(bg=flash_color)
                        widget.update()
                        time.sleep(0.05)
                        widget.configure(bg=original_bg)
                        widget.update()
                        time.sleep(0.05)
            
            threading.Thread(target=flash_sequence, daemon=True).start()
        except:
            pass
    
    def pulse_effect(self, widget):
        """Pulse widget size"""
        try:
            original_font = widget.cget('font')
            
            def pulse_sequence():
                for scale in [1.1, 1.2, 1.1, 1.0]:
                    if widget.winfo_exists():
                        if isinstance(original_font, tuple):
                            new_size = int(original_font[1] * scale)
                            new_font = (original_font[0], new_size, original_font[2])
                        else:
                            new_font = original_font
                        
                        widget.configure(font=new_font)
                        widget.update()
                        time.sleep(0.1)
            
            threading.Thread(target=pulse_sequence, daemon=True).start()
        except:
            pass
    
    def shake_effect(self, widget):
        """Shake widget position"""
        try:
            original_x = widget.winfo_x()
            original_y = widget.winfo_y()
            
            def shake_sequence():
                for _ in range(5):
                    if widget.winfo_exists():
                        offset_x = random.randint(-3, 3)
                        offset_y = random.randint(-3, 3)
                        widget.place(x=original_x + offset_x, y=original_y + offset_y)
                        widget.update()
                        time.sleep(0.05)
                
                if widget.winfo_exists():
                    widget.place(x=original_x, y=original_y)
            
            threading.Thread(target=shake_sequence, daemon=True).start()
        except:
            pass
    
    def glow_effect(self, widget):
        """Create glow effect around widget"""
        try:
            original_relief = widget.cget('relief')
            original_bd = widget.cget('bd')
            
            def glow_sequence():
                colors = ['#00ff41', '#40ff80', '#80ffbf', '#40ff80', '#00ff41']
                for color in colors:
                    if widget.winfo_exists():
                        widget.configure(relief='solid', bd=2, highlightbackground=color)
                        widget.update()
                        time.sleep(0.1)
                
                if widget.winfo_exists():
                    widget.configure(relief=original_relief, bd=original_bd)
            
            threading.Thread(target=glow_sequence, daemon=True).start()
        except:
            pass
    
    def ripple_effect(self, widget):
        """Create ripple effect (for canvas widgets)"""
        if not isinstance(widget, tk.Canvas):
            return
        
        try:
            center_x = widget.winfo_width() // 2
            center_y = widget.winfo_height() // 2
            
            def ripple_sequence():
                ripple_id = None
                for radius in range(10, 100, 10):
                    if widget.winfo_exists():
                        if ripple_id:
                            widget.delete(ripple_id)
                        
                        ripple_id = widget.create_oval(
                            center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            outline='#00ff41', width=2
                        )
                        widget.update()
                        time.sleep(0.05)
                
                if widget.winfo_exists() and ripple_id:
                    widget.delete(ripple_id)
            
            threading.Thread(target=ripple_sequence, daemon=True).start()
        except:
            pass
    
    def create_audio_visualizer(self, canvas: tk.Canvas, x: int, y: int, width: int = 200, height: int = 100):
        """Create realistic audio spectrum visualizer with frequency analysis"""
        if not canvas:
            return
        
        def animate_visualizer():
            bars = 32  # More bars for better resolution
            bar_width = width // bars
            
            # Frequency bands (Hz)
            freq_bands = np.logspace(1, 4, bars)  # 10Hz to 10kHz
            
            # Initialize amplitude history for smoothing
            amplitude_history = [[] for _ in range(bars)]
            max_history = 10
            
            while canvas.winfo_exists():
                try:
                    canvas.delete("visualizer")
                    
                    for i in range(bars):
                        # Simulate frequency response with some realism
                        base_freq = freq_bands[i]
                        
                        # Generate amplitude based on frequency characteristics
                        if base_freq < 100:  # Sub-bass
                            amplitude = random.uniform(0.1, 0.4) * height
                        elif base_freq < 500:  # Bass
                            amplitude = random.uniform(0.2, 0.7) * height
                        elif base_freq < 2000:  # Midrange
                            amplitude = random.uniform(0.3, 0.9) * height
                        elif base_freq < 8000:  # Treble
                            amplitude = random.uniform(0.1, 0.6) * height
                        else:  # High treble
                            amplitude = random.uniform(0.05, 0.3) * height
                        
                        # Add some randomness and decay
                        amplitude *= random.uniform(0.7, 1.3)
                        
                        # Smooth amplitude using history
                        amplitude_history[i].append(amplitude)
                        if len(amplitude_history[i]) > max_history:
                            amplitude_history[i].pop(0)
                        
                        smooth_amplitude = sum(amplitude_history[i]) / len(amplitude_history[i])
                        
                        bar_x = x + i * bar_width
                        bar_y = y + height - smooth_amplitude
                        
                        # Color based on frequency and amplitude
                        if base_freq < 200:
                            color = f'#{int(255 * smooth_amplitude / height):02x}0040'  # Red for bass
                        elif base_freq < 2000:
                            color = f'#{int(255 * smooth_amplitude / height):02x}{int(255 * smooth_amplitude / height):02x}00'  # Yellow for mid
                        else:
                            color = f'00{int(255 * smooth_amplitude / height):02x}41'  # Green for treble
                        
                        # Draw bar with gradient effect
                        canvas.create_rectangle(
                            bar_x, bar_y, bar_x + bar_width - 1, y + height,
                            fill=color, outline='', tags="visualizer"
                        )
                        
                        # Add peak indicator
                        if smooth_amplitude > height * 0.8:
                            canvas.create_rectangle(
                                bar_x, bar_y - 3, bar_x + bar_width - 1, bar_y,
                                fill='#ffffff', outline='', tags="visualizer"
                            )
                    
                    canvas.update()
                    time.sleep(0.05)  # Faster update for smoother animation
                    
                except tk.TclError:
                    break  # Canvas destroyed
                except Exception:
                    continue
        
        threading.Thread(target=animate_visualizer, daemon=True).start()
    
    def text_to_speech(self, text: str):
        """Enhanced text-to-speech with multiple fallbacks"""
        if not self.enabled or len(text) > 100:  # Limit text length
            return
        
        def speak():
            try:
                # Clean text for TTS
                clean_text = ''.join(c for c in text if c.isalnum() or c.isspace())[:50]
                
                # Try espeak first (most common on Linux)
                if shutil.which('espeak'):
                    try:
                        subprocess.run(['espeak', '-s', '150', '-v', 'en', clean_text], 
                                     check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                        return
                    except:
                        pass
                
                # Try festival
                if shutil.which('festival'):
                    try:
                        process = subprocess.Popen(['festival', '--tts'], 
                                                 stdin=subprocess.PIPE, 
                                                 stdout=subprocess.DEVNULL, 
                                                 stderr=subprocess.DEVNULL)
                        process.communicate(input=clean_text.encode(), timeout=5)
                        return
                    except:
                        pass
                
                # Try macOS say command
                if shutil.which('say'):
                    try:
                        subprocess.run(['say', clean_text], check=True,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                        return
                    except:
                        pass
                
                # Try spd-say (speech-dispatcher)
                if shutil.which('spd-say'):
                    try:
                        subprocess.run(['spd-say', clean_text], check=True,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                        return
                    except:
                        pass
                
                # Fallback: Generate beep pattern for text
                self._text_to_beeps(clean_text)
                
            except Exception:
                pass
        
        threading.Thread(target=speak, daemon=True).start()
    
    def _text_to_beeps(self, text: str):
        """Convert text to morse-like beep patterns"""
        try:
            # Simple text to beep conversion
            for char in text.lower():
                if char.isalpha():
                    # Different frequencies for different letters
                    freq = 400 + (ord(char) - ord('a')) * 20
                    self._generate_beep(freq, 0.1)
                    time.sleep(0.05)
                elif char.isspace():
                    time.sleep(0.2)
        except:
            pass
    
    def _generate_beep(self, frequency: int, duration: float):
        """Generate a simple beep tone"""
        try:
            if AUDIO_AVAILABLE:
                t = np.linspace(0, duration, int(self.sample_rate * duration))
                tone = np.sin(2 * np.pi * frequency * t) * 0.3
                audio = (tone * 32767).astype(np.int16)
                play_obj = sa.play_buffer(audio, 1, 2, self.sample_rate)
                play_obj.wait_done()
            elif SYSTEM_AUDIO_AVAILABLE:
                self._play_system_beep(frequency, duration)
        except:
            pass
    
    def _play_system_sound(self, effect_type: str):
        """Play sound using system commands"""
        try:
            if effect_type == "click":
                self._play_system_beep(800, 0.05)
            elif effect_type == "success":
                # Play ascending tones
                for freq in [440, 554, 659]:
                    self._play_system_beep(freq, 0.1)
                    time.sleep(0.05)
            elif effect_type == "error":
                self._play_system_beep(200, 0.4)
            elif effect_type == "notification":
                self._play_system_beep(880, 0.2)
            elif effect_type == "unlock":
                for freq in [330, 440, 550, 660]:
                    self._play_system_beep(freq, 0.15)
                    time.sleep(0.05)
            elif effect_type == "lock":
                for freq in [440, 220]:
                    self._play_system_beep(freq, 0.2)
                    time.sleep(0.1)
        except:
            pass
    
    def _play_system_beep(self, frequency: int, duration: float):
        """Play beep using system commands"""
        try:
            duration_ms = int(duration * 1000)
            print(f'Playing beep: {frequency}Hz for {duration_ms}ms')
            
            # Try different system audio commands
            if shutil.which('beep'):
                result = subprocess.run(['beep', '-f', str(frequency), '-l', str(duration_ms)], 
                             capture_output=True, timeout=2)
                print(f'beep command result: {result.returncode}')
            elif shutil.which('speaker-test'):
                result = subprocess.run(['speaker-test', '-t', 'sine', '-f', str(frequency), '-l', '1'], 
                             capture_output=True, timeout=2)
                print(f'speaker-test result: {result.returncode}')
            elif shutil.which('aplay'):
                # Generate simple wav and play with aplay
                self._generate_and_play_beep_aplay(frequency, duration)
            else:
                # Fallback: print bell character multiple times
                print('\a' * 3, end='', flush=True)
                print(f'Audio fallback: terminal bell for {frequency}Hz')
        except Exception as e:
            # Ultimate fallback: print bell
            print('\a', end='', flush=True)
            print(f'Audio error: {e}')
    
    def _generate_and_play_beep_aplay(self, frequency: int, duration: float):
        """Generate beep and play with aplay directly"""
        try:
            import tempfile
            import wave
            
            # Generate tone
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = np.sin(2 * np.pi * frequency * t) * 0.3
            audio = (audio * 32767).astype(np.int16)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio.tobytes())
                
                # Play with aplay
                if shutil.which('aplay'):
                    result = subprocess.run(['aplay', temp_file.name], 
                                         capture_output=True, timeout=5)
                    print(f'aplay result: {result.returncode}')
                    if result.stderr:
                        print(f'aplay error: {result.stderr.decode()}')
                
                # Clean up
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
        except Exception as e:
            print(f'aplay generation error: {e}')
    
    def haptic_feedback(self, pattern: str = "short"):
        """Simulate haptic feedback"""
        if not self.haptic_enabled:
            return
        
        # Visual haptic simulation (screen flash)
        if pattern == "short":
            self.screen_flash(duration=0.05)
        elif pattern == "long":
            self.screen_flash(duration=0.2)
        elif pattern == "double":
            self.screen_flash(duration=0.05)
            time.sleep(0.1)
            self.screen_flash(duration=0.05)
    
    def screen_flash(self, duration: float = 0.1):
        """Flash entire screen for haptic feedback"""
        try:
            flash_window = tk.Toplevel(self.parent)
            flash_window.attributes('-fullscreen', True)
            flash_window.attributes('-alpha', 0.3)
            flash_window.configure(bg='white')
            flash_window.overrideredirect(True)
            
            def remove_flash():
                time.sleep(duration)
                if flash_window.winfo_exists():
                    flash_window.destroy()
            
            threading.Thread(target=remove_flash, daemon=True).start()
        except:
            pass
    
    def set_volume(self, volume: float):
        """Set audio volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_enabled(self, enabled: bool):
        """Enable/disable audio feedback"""
        self.enabled = enabled
    
    def set_visual_effects(self, enabled: bool):
        """Enable/disable visual effects"""
        self.visual_effects = enabled
    
    def set_haptic_feedback(self, enabled: bool):
        """Enable/disable haptic feedback"""
        self.haptic_enabled = enabled