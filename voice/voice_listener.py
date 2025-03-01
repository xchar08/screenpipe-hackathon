import time
import speech_recognition as sr
from rapidfuzz import fuzz
import re

TARGET_WAKE_WORD = "Hey Jarvis"
WAKE_THRESHOLD = 60  # Adjust threshold for minor deviations


class VoiceListener:
    def __init__(self, main_window):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.main_window = main_window

    def is_wake_word(self, transcript):
        transcript_lower = transcript.lower()
        # First, require that the exact consecutive phrase "hey jarvis" is present.
        pattern = r'\bhey\s+jarvis\b'
        if re.search(pattern, transcript_lower) is None:
            return False
    # Then, use fuzzy matching for an extra layer of tolerance.
        score = fuzz.partial_ratio(transcript_lower, TARGET_WAKE_WORD)
        return score >= WAKE_THRESHOLD

    def listen_for_wake_word(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            transcript = self.recognizer.recognize_google(audio)
            if self.is_wake_word(transcript):
                return True
        except sr.UnknownValueError:
            pass
        return False

    def listen_for_command(self):
        with self.microphone as source:
            self.recognizer.pause_threshold = 2
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None

    def start_listening(self):
        while True:
            if self.listen_for_wake_word():
                print("Wake word detected!")
                self.main_window.startGlowSignal.emit()
                command = self.listen_for_command()
                if command:
                    print("Command received:", command)
                    self.main_window.commandReceived.emit(command)
                self.main_window.stopGlowSignal.emit()
            time.sleep(0.5)