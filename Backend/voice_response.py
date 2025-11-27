import pyttsx3
import threading

class VoiceResponse:
    """Text-to-Speech for voice responses"""
    
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Set voice (female voice if available)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
            
            self.enabled = True
        except Exception as e:
            print(f"Voice engine initialization failed: {e}")
            self.enabled = False
    
    def speak(self, text):
        """Speak the given text"""
        if not self.enabled:
            return
        
        try:
            # Clean text for speaking
            clean_text = self.clean_text_for_speech(text)
            
            # Speak in separate thread to not block
            thread = threading.Thread(target=self._speak_thread, args=(clean_text,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"Speech error: {e}")
    
    def _speak_thread(self, text):
        """Internal method to speak in thread"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech thread error: {e}")
    
    def clean_text_for_speech(self, text):
        """Clean text to make it more speech-friendly"""
        # Remove special characters
        clean = text.replace('✅', 'Success.')
        clean = clean.replace('❌', 'Error.')
        clean = clean.replace('⚠️', 'Warning.')
        clean = clean.replace('ℹ️', 'Info.')
        clean = clean.replace('🤖', '')
        clean = clean.replace('\n', '. ')
        
        # Shorten long outputs
        lines = clean.split('.')
        if len(lines) > 5:
            # Only speak summary
            summary = '. '.join(lines[:3])
            return summary + ". Check screen for full details."
        
        return clean
    
    def generate_summary(self, command_result):
        """Generate a concise summary for voice"""
        result_lower = command_result.lower()
        
        # Count items
        if 'running' in result_lower:
            count = result_lower.count('running')
            return f"Found {count} running items"
        
        elif 'error' in result_lower:
            return "Command failed with an error"
        
        elif 'no resources' in result_lower:
            return "No resources found"
        
        elif 'success' in result_lower:
            return "Command executed successfully"
        
        else:
            return "Command completed"
