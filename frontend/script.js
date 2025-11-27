let recognition;
let isListening = false;

// Check browser support
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        console.log("Using webkitSpeechRecognition");
    } else if ('SpeechRecognition' in window) {
        recognition = new SpeechRecognition();
        console.log("Using SpeechRecognition");
    } else {
        alert("Speech recognition not supported in this browser. Use Chrome or Edge.");
        return false;
    }
    
    // Configure recognition - more sensitive settings
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    // Event handlers
    recognition.onstart = function() {
        console.log("Speech recognition started");
        document.getElementById('status').textContent = '🎤 Listening... Speak now!';
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        isListening = true;
    };
    
    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript;
        console.log("✅ Command received:", command);
        console.log("Confidence:", event.results[0][0].confidence);
        document.getElementById('command-text').textContent = command;
        document.getElementById('status').textContent = '⏳ Processing command...';
        sendCommandToBackend(command);
    };
    
    recognition.onend = function() {
        console.log("Speech recognition ended");
        document.getElementById('status').textContent = 'Ready to listen...';
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        isListening = false;
    };
    
    recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);
        
        if (event.error === 'no-speech') {
            document.getElementById('status').textContent = '🔇 No speech detected. Click Start and speak again!';
        } else if (event.error === 'not-allowed') {
            document.getElementById('status').textContent = '❌ Microphone blocked! Allow microphone access.';
            alert('Please allow microphone access in browser settings!');
        } else if (event.error === 'audio-capture') {
            document.getElementById('status').textContent = '❌ No microphone found!';
        } else {
            document.getElementById('status').textContent = 'Error: ' + event.error;
        }
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        isListening = false;
    };
    
    return true;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("Page loaded, initializing...");
    
    if (!initializeSpeechRecognition()) {
        document.getElementById('status').textContent = 'Speech recognition not supported';
        return;
    }
    
    // Button events
    document.getElementById('startBtn').addEventListener('click', function() {
        console.log("Start button clicked");
        if (recognition && !isListening) {
            try {
                recognition.start();
            } catch (error) {
                console.error("Error starting recognition:", error);
                document.getElementById('status').textContent = 'Error starting microphone';
            }
        }
    });
    
    document.getElementById('stopBtn').addEventListener('click', function() {
        console.log("Stop button clicked");
        if (recognition && isListening) {
            recognition.stop();
        }
    });
});

// Send command to backend
async function sendCommandToBackend(command) {
    try {
        console.log("Sending command to backend:", command);
        
        const response = await fetch('http://127.0.0.1:5000/api/voice-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Backend response:", data);
        
        if (data.success) {
            // Show AI analysis if available
            let responseText = data.response;
            if (data.ai_analysis) {
                responseText = `🤖 AI Understanding: ${data.ai_analysis.description}\n\n${responseText}`;
            }
            document.getElementById('response-text').textContent = responseText;
            document.getElementById('status').textContent = '✅ Command processed successfully!';
        } else {
            document.getElementById('response-text').textContent = 'Error: ' + data.error;
            document.getElementById('status').textContent = '❌ Command failed';
        }
        
    } catch (error) {
        console.error("Backend communication error:", error);
        document.getElementById('response-text').textContent = 'Connection Error: ' + error.message;
        document.getElementById('status').textContent = '❌ Backend connection failed';
    }
}