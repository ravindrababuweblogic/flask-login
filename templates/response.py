import azure.cognitiveservices.speech as speechsdk
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Request
import json
import re
import io
import asyncio

SUBSCRIPTION_KEY = "7e23ef5547644534b78b21fc8c15aa7b"
REGION = "eastus2"
speech_config = speechsdk.SpeechConfig(subscription=SUBSCRIPTION_KEY, region=REGION)

async def recognize_human_voice_analyze(audio_data):
    audio_data_stream = speechsdk.AudioDataStream(audio_data)
    audio_config = speechsdk.AudioConfig(stream=audio_data_stream)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)
    result = speech_recognizer.recognize_once_async().get()
    audio_data_stream.close()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        raise HTTPException(status_code=400, detail="No speech recognized")

async def recognize_ai_voice_analyze(audio_data):
    audio_data_stream = speechsdk.AudioDataStream(audio_data)
    audio_config = speechsdk.AudioConfig(stream=audio_data_stream)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config, audio_config)
    result = speech_synthesizer.speak_text_async("This is an AI-generated voice.").get()
    audio_data_stream.close()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
    else:
        raise HTTPException(status_code=400, detail="AI voice recognition failed")
