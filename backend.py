"""
ChillBot ML Backend - Flask API for Railway
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import numpy as np

app = Flask(__name__)

# CORS Configuration for Vercel
ALLOWED_ORIGINS = os.environ.get(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:8000'
).split(',')
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# ============================================
# EMOTION DETECTION MODEL
# ============================================

class EmotionDetector:
    def __init__(self):
        self.emotion_keywords = {
            'anxiety': {
                'keywords': ['anxious', 'anxiety', 'panic', 'worried', 'nervous', 
                           'scared', 'fearful', 'terrified', 'restless', 'tense'],
                'phrases': ['can\'t breathe', 'racing heart', 'panic attack']
            },
            'depression': {
                'keywords': ['depressed', 'sad', 'hopeless', 'worthless', 'empty', 
                           'numb', 'lonely', 'isolated', 'crying', 'tired'],
                'phrases': ['no point', 'give up', 'nothing matters', 'can\'t go on']
            },
            'stress': {
                'keywords': ['stressed', 'overwhelmed', 'pressure', 'burnout', 
                           'exhausted', 'swamped', 'drowning', 'too much'],
                'phrases': ['can\'t handle', 'too much to do', 'breaking point']
            },
            'anger': {
                'keywords': ['angry', 'furious', 'mad', 'frustrated', 'irritated', 
                           'annoyed', 'rage', 'hate'],
                'phrases': ['so angry', 'pissed off', 'fed up']
            }
        }
        
        self.crisis_keywords = [
            'suicide', 'suicidal', 'kill myself', 'end my life', 'want to die',
            'better off dead', 'hurt myself', 'self harm', 'cut myself', 
            'overdose', 'no reason to live'
        ]
    
    def detect_crisis(self, text):
        text_lower = text.lower()
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                return True, keyword
        return False, None
    
    def detect_emotion(self, text):
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, data in self.emotion_keywords.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in text_lower:
                    score += 1
            for phrase in data['phrases']:
                if phrase in text_lower:
                    score += 2
            emotion_scores[emotion] = score
        
        if max(emotion_scores.values()) > 0:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[primary_emotion] / 3, 1.0)
            return primary_emotion, confidence
        
        return None, 0.0

# ============================================
# RESPONSE GENERATION
# ============================================

class ResponseGenerator:
    def __init__(self):
        self.responses = {
            'anxiety': [
                {
                    'message': "I hear that you're feeling anxious. Anxiety can be really challenging. Let's try a quick grounding technique together:\n\n🌟 5-4-3-2-1 Exercise:\n• Name 5 things you can see\n• 4 things you can touch\n• 3 things you can hear\n• 2 things you can smell\n• 1 thing you can taste\n\nWould you like to try this, or would you prefer to talk about what's making you anxious?",
                    'technique': '5-4-3-2-1 grounding'
                },
                {
                    'message': "Anxiety can feel overwhelming. Let's work on calming your nervous system:\n\n💨 Box Breathing:\n• Inhale for 4 counts\n• Hold for 4 counts\n• Exhale for 4 counts\n• Hold for 4 counts\n• Repeat 4 times\n\nThis activates your parasympathetic nervous system. Want to try it together?",
                    'technique': 'box breathing'
                }
            ],
            'depression': [
                {
                    'message': "Thank you for sharing that with me. Depression can make everything feel heavy. What you're feeling is valid, and you're not alone.\n\nWhen we're feeling down, even small actions can help. Would any of these feel doable right now?\n\n• Take a 5-minute walk outside\n• Listen to a favorite song\n• Reach out to someone you trust\n• Write down one small thing that went okay today\n\nNo pressure - what sounds manageable?",
                    'technique': 'behavioral activation'
                }
            ],
            'stress': [
                {
                    'message': "Feeling stressed and overwhelmed is tough. Let's work on bringing that pressure down:\n\n💨 4-7-8 Breathing:\n• Breathe in through your nose for 4 counts\n• Hold your breath for 7 counts\n• Exhale through your mouth for 8 counts\n• Repeat 3-4 times\n\nThis scientifically calms your nervous system. Ready to try?",
                    'technique': '4-7-8 breathing'
                }
            ],
            'anger': [
                {
                    'message': "I hear your frustration. Anger is a valid emotion, and it's telling you something important.\n\n🔥 Let's channel it constructively:\n• What specifically triggered this feeling?\n• What need of yours isn't being met?\n• What would help address the core issue?\n\nAnger often protects us from deeper feelings. Want to explore what's underneath?",
                    'technique': 'anger exploration'
                }
            ],
            'general': [
                {
                    'message': "I'm listening. It sounds like you're going through something important. Would you like to tell me more about what you're experiencing? Sometimes talking through things helps us see them more clearly.",
                    'technique': 'active listening'
                }
            ],
            'crisis': {
                'message': "I'm really concerned about what you're sharing. Your safety is the top priority. Please reach out to:\n\n🆘 National Suicide Prevention Lifeline: 988\n📞 Crisis Text Line: Text HOME to 741741\n🌐 International: https://findahelpline.com\n\nThese services are free, confidential, and available 24/7. Would you be willing to contact them right now? You don't have to face this alone.",
                'technique': 'crisis intervention'
            }
        }
    
    def generate_response(self, emotion, is_crisis):
        if is_crisis:
            return self.responses['crisis']
        if emotion and emotion in self.responses:
            import random
            return random.choice(self.responses[emotion])
        return self.responses['general'][0]

# ============================================
# MOOD TRACKING
# ============================================

class MoodTracker:
    def __init__(self):
        self.mood_history = []
    
    def log_mood(self, user_id, mood_score, emotion, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        entry = {
            'user_id': user_id,
            'mood_score': mood_score,
            'emotion': emotion,
            'timestamp': timestamp
        }
        self.mood_history.append(entry)
        return entry
    
    def get_mood_trend(self, user_id, days=7):
        user_moods = [m for m in self.mood_history if m['user_id'] == user_id]
        if len(user_moods) < 2:
            return {'trend': 'insufficient_data'}
        recent_moods = user_moods[-days:]
        scores = [m['mood_score'] for m in recent_moods]
        avg_mood = np.mean(scores)
        trend = 'stable'
        if len(scores) >= 3:
            if scores[-1] > scores[0]:
                trend = 'improving'
            elif scores[-1] < scores[0]:
                trend = 'declining'
        return {
            'average_mood': float(avg_mood),
            'trend': trend,
            'entries': len(recent_moods)
        }

# ============================================
# INITIALIZE
# ============================================

emotion_detector = EmotionDetector()
response_generator = ResponseGenerator()
mood_tracker = MoodTracker()

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'ChillBot ML Backend',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': ['/api/health', '/api/analyze', '/api/mood/log', '/api/mood/trend', '/api/resources']
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'ChillBot ML Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_message():
    data = request.get_json()
    message = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    is_crisis, crisis_keyword = emotion_detector.detect_crisis(message)
    emotion, confidence = emotion_detector.detect_emotion(message)
    response = response_generator.generate_response(emotion, is_crisis)
    
    return jsonify({
        'emotion': emotion,
        'confidence': float(confidence),
        'is_crisis': is_crisis,
        'crisis_keyword': crisis_keyword,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/mood/log', methods=['POST'])
def log_mood():
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous')
    mood_score = data.get('mood_score')
    emotion = data.get('emotion')
    
    if mood_score is None:
        return jsonify({'error': 'mood_score is required'}), 400
    
    entry = mood_tracker.log_mood(user_id, mood_score, emotion)
    return jsonify({'success': True, 'entry': entry})

@app.route('/api/mood/trend', methods=['GET'])
def get_mood_trend():
    user_id = request.args.get('user_id', 'anonymous')
    days = int(request.args.get('days', 7))
    trend = mood_tracker.get_mood_trend(user_id, days)
    return jsonify(trend)

@app.route('/api/resources', methods=['GET'])
def get_resources():
    resources = {
        'crisis_hotlines': [
            {'name': 'National Suicide Prevention Lifeline', 'number': '988', 'available': '24/7', 'country': 'USA'},
            {'name': 'Crisis Text Line', 'contact': 'Text HOME to 741741', 'available': '24/7', 'country': 'USA'},
            {'name': 'International', 'website': 'https://findahelpline.com', 'available': '24/7', 'country': 'International'}
        ]
    }
    return jsonify(resources)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🤖 ChillBot ML Backend Starting...")
    print("📊 Emotion Detection: Active")
    print("🚨 Crisis Detection: Active")
    print("💾 Mood Tracking: Active")
    print(f"\n🌐 Server running on http://0.0.0.0:{port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)