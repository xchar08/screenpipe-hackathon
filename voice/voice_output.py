import pyttsx3

engine = pyttsx3.init()
# Optionally customize voice properties:
engine.setProperty('rate', 150)  # speech rate
engine.setProperty('volume', 1.0)  # volume level (0.0 to 1.0)

def say(text: str):
    engine.say(text)
    engine.runAndWait()
