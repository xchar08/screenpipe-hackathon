import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech rate as needed.
engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

def say(text: str):
    engine.say(text)
    engine.runAndWait()
