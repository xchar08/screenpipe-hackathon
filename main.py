import sys
import threading
import platform
from PyQt5.QtWidgets import QApplication
from assistant.assistant import Assistant
from voice.voice_listener import VoiceListener

def play_startup_sound():
    if platform.system() == "Windows":
        try:
            import winsound
            winsound.PlaySound("startup.wav", winsound.SND_FILENAME)
        except Exception as e:
            print("Error playing startup sound with winsound:", e)
    else:
        try:
            from playsound import playsound
            playsound("startup.wav")
        except Exception as e:
            print("Error playing startup sound with playsound:", e)

def main():
    app = QApplication(sys.argv)
    
    # Play startup sound
    play_startup_sound()
    
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    # Start voice listener in a separate thread.
    voice_listener = VoiceListener(window)
    threading.Thread(target=voice_listener.start_listening, daemon=True).start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
