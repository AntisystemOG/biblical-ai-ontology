import speech_recognition as sr  
import pyttsx3  
import whisper  
import pyaudio  
import os  
import subprocess  
import time  
  
# Config  
WAKE_WORD = "hey spock"  
WHISPER_MODEL = "base"  # small/medium/large for accuracy vs speed  
OPENCLAW_SESSION = "default"  # Adjust if needed  
  
# Initialize  
recognizer = sr.Recognizer()  
engine = pyttsx3.init()  
model = whisper.load_model(WHISPER_MODEL)  
  
def speak(text):  
    engine.say(text)  
    engine.runAndWait()  
  
def listen_for_wake_word():  
    with sr.Microphone() as source:  
        print("Listening for wake word...")  
        audio = recognizer.listen(source)  
    try:  
        text = recognizer.recognize_google(audio).lower()  
        if WAKE_WORD in text:  
            speak("Yes?")  
            return True  
    except:  
        pass  
    return False  
  
def record_message():  
    with sr.Microphone() as source:  
        print("Speak your message...")  
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)  
    # Save to temp file  
    with open("temp.wav", "wb") as f:  
        f.write(audio.get_wav_data())  
    return "temp.wav"  
  
def transcribe_audio(file_path):  
    result = model.transcribe(file_path)  
    os.remove(file_path)  
    return result["text"]  
  
def send_to_spock(message):  
    # Use openclaw CLI to send message (adjust command as needed)  
    cmd = f'openclaw message send --session {OPENCLAW_SESSION} --text "{message}"'  
    response = subprocess.getoutput(cmd)  
    # Parse response (assuming it returns Spock's reply)  
    return response  # Adjust parsing if needed  
  
# Main loop  
while True:  
    if listen_for_wake_word():  
        audio_file = record_message()  
        transcription = transcribe_audio(audio_file)  
        print(f"You said: {transcription}")  
        response = send_to_spock(transcription)  
        print(f"Spock: {response}")  
        speak(response)  
    time.sleep(1)  
