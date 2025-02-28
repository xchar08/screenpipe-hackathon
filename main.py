import sys
import threading
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from voice.voice_listener import VoiceListener

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Start the voice listener in a separate thread.
    voice_listener = VoiceListener(window)
    threading.Thread(target=voice_listener.start_listening, daemon=True).start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
