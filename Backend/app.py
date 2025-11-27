from flask import Flask, request, jsonify
from flask_cors import CORS
from devops_executor import DevOpsExecutor
from ai_processor import AIProcessor
from voice_response import VoiceResponse
import json

app = Flask(__name__)
CORS(app)

# Initialize components
devops_executor = DevOpsExecutor()
ai_processor = AIProcessor()
voice_response = VoiceResponse()

@app.route('/')
def index():
    return "Voice DevOps Assistant is Running!"

@app.route('/api/voice-command', methods=['POST'])
def handle_voice_command():
    try:
        data = request.get_json()
        voice_command = data.get('command', '')
        
        print(f"\n{'='*50}")
        print(f"Received voice command: {voice_command}")
        
        # Step 1: AI Processing - Understand command
        ai_analysis = ai_processor.process_command(voice_command)
        print(f"AI Analysis: {ai_analysis['command_type']}")
        print(f"Description: {ai_analysis['description']}")
        
        # Step 2: Execute DevOps command
        response = devops_executor.execute_command(voice_command)
        
        # Step 3: Generate smart response
        smart_response = ai_processor.generate_smart_response(response, ai_analysis)
        
        # Step 4: Voice response
        voice_summary = voice_response.generate_summary(smart_response)
        voice_response.speak(voice_summary)
        
        print(f"Response sent to user")
        print(f"Voice: {voice_summary}")
        print(f"{'='*50}\n")
        
        return jsonify({
            'success': True,
            'response': smart_response,
            'command': voice_command,
            'ai_analysis': {
                'command_type': ai_analysis['command_type'],
                'description': ai_analysis['description'],
                'parameters': ai_analysis['parameters']
            }
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'voice-devops-assistant'})

if __name__ == '__main__':
    print("Starting Voice DevOps Assistant...")
    print("Server running on: http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)