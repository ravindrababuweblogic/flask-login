import os
import random
import pyttsx3
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "super secret key"

# Initialize the text-to-speech engine
engine = pyttsx3.init()
ai_number = 0

# Initialize the speech config for Azure Open AI speech service
speech_config = speechsdk.SpeechConfig(subscription="7e23ef5547644534b78b21fc8c15aa7b", region="eastus2")


@app.route('/')
def index():
    return render_template('generate.html')


# Function to generate a random number for AI-generated voice
def generate_random_number():
    return random.randint(1, 10000)


# Function to generate AI-generated voice using Azure Open AI speech service
def ai_voice(number):
    engine.setProperty('rate', 200)
    engine.say(f"Your number is {number}")
    engine.runAndWait()


# Function to recognize human voice using Azure Open AI speech service
def recognize_human_voice():
    print("here")
    audio_input = speechsdk.AudioConfig(filename="path_to_audio_file_or_audio_stream")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
        return None


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    # Generate a random number for AI-generated voice
    ai_number = generate_random_number()

    # Generate AI-generated voice using Azure Open AI speech service
    ai_voice(ai_number)
    print(ai_number)

    return render_template('generate.html')


@app.route('/voicetest', methods=['GET', 'POST'])
def voicetest():
    # Recognize human voice using Azure Open AI speech service
    human_voice = recognize_human_voice()

    # Check if the recognized text matches the expected pattern and proceed accordingly


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
