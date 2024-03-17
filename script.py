import os
import json
import random
import pyttsx3
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, request, jsonify, render_template
from flask.wrappers import Response
from ping import ping
from response import recognize_human_voice_analyze, recognize_ai_voice_analyze
import regex as re
import asyncio
import datetime

url = "http://127.0.0.1:8080"
Model_version = "openai-whisper-large-v3-1"
openai_Model_ID = "azureml://registries/azureml/models/openai-whisper-large-v3/versions/1"
Endpoint_URL = "https://project-codeiam-iam.eastus2.inference.ml.azure.com/score"
Swagger_URL = "https://project-codeiam-iam.eastus2.inference.ml.azure.com/swagger.json"
service_endpoint_key = "nGaqiz6lHpbPIvfmCM4gtWdAclggH4Xj"
SUBSCRIPTION_KEY = "7e23ef5547644534b78b21fc8c15aa7b"
REGION = "eastus2"
path_to_audio_file_or_audio_stream = "sentinels-main/testuser.wav"
now = datetime.datetime.now()

app = Flask(__name__)
app.secret_key = "super secret key"

# Initialize the text-to-speech engine
engine = pyttsx3.init()
ai_number = 0

# Initialize the speech config for Azure Open AI speech service
speech_config = speechsdk.SpeechConfig(subscription=SUBSCRIPTION_KEY, region=REGION)

@app.route('/')
def index():
    return render_template('generate.html')

@app.route('/ping')
def index_ping():
    return ping(url)

# Function to generate a random number for AI-generated voice
def generate_random_number():
    return random.randint(1, 10000)

# Function to generate AI-generated voice using Azure Open AI speech service
def ai_voice(number):
    engine.setProperty('rate', 200)
    engine.say(f"Your number is {number}")
    engine.runAndWait()

# Function to recognize human voice using Azure Open AI speech service
async def recognize_human_voice():
    audio_input = speechsdk.AudioConfig(filename=path_to_audio_file_or_audio_stream)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
        return None

# Function to recognize AI-generated voice using Azure Open AI speech service
async def recognize_ai_voice():
    audio_input = speechsdk.AudioConfig(filename=path_to_audio_file_or_audio_stream)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_synthesizer.speak_text_async("This is an AI-generated voice.")

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("AI-generated voice recognized")
        return result.audio_data
    else:
        print("AI-generated voice not recognized")
        return None

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    # Generate a random number for AI-generated voice
    ai_number = generate_random_number()

    # Generate AI-generated voice using Azure Open AI speech service
    ai_voice(ai_number)
    print(ai_number)

    return render_template('generate.html')


@app.route('/voice/analyze', methods=['GET', 'POST'])
def voiceanalyze():
    try:
        if request.method == 'POST':
            file = request.files[path_to_audio_file_or_audio_stream]
            content_type = file.content_type
            if content_type != "audio/wav":
                raise Response(response=json.dumps({"message": "Invalid file type. Please upload a .wav file."}), status=400, mimetype="application/json")

            # Check if the uploaded file is a valid .wav file
            if not file.filename.endswith('.wav'):
                raise Response(response=json.dumps({"message": "Invalid file type. Please upload a .wav file."}), status=400, mimetype="application/json")

            # Read the uploaded file
            file_data = file.read()
            if len(file_data) == 0:
                raise Response(response=json.dumps({"message": "No data received"}), status=400, mimetype="application/json")

            # Recognize human voice
            human_voice = asyncio.run(recognize_human_voice_analyze(file_data))
            if human_voice is None:
                raise Response(response=json.dumps({"message": "No speech recognized"}), status=400, mimetype="application/json")

            # Recognize AI-generated voice
            ai_voice = asyncio.run(recognize_ai_voice_analyze(file_data))
            voice_type = "human"
            if ai_voice is not None:
                voice_type = "ai"

            # Calculate confidence scores
            ai_probability = 5
            human_probability = 95
            if voice_type == "ai":
                ai_probability = 95
                human_probability = 5

            # Calculate emotional tone and background noise level
            emotional_tone = "N/A"
            background_noise_level = "N/A"

            # Return the JSON response
            response = {
                "status": "success",
                "analysis": {
                    "detectedVoice": True,
                    "voiceType": voice_type,
                    "confidenceScore": {
                        "aiProbability": ai_probability,
                        "humanProbability": human_probability
                    },
                    "additionalInfo": {
                        "emotionalTone": emotional_tone,
                        "backgroundNoiseLevel": background_noise_level
                    }
                },
                "responseTime": 200
            }
            return jsonify(response)
    except Exception as e:
        error_message = str(e)
        return jsonify({"error": error_message,
                        "dateTime": now.strftime("%Y-%m-%d %H:%M:%S")
                        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
