import os
# Set TESSDATA_PREFIX to the folder containing tessdata
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import pyautogui
import pytesseract
import asyncio
from googletrans import Translator

class TranslationThread(QThread):
    # Signal: original text, translated text
    translation_ready = pyqtSignal(str, str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.translator = Translator()

    def run(self):
        try:
            # Use asyncio.run to await the translation coroutine
            translation = asyncio.run(self.translator.translate(self.text, dest='en'))
            self.translation_ready.emit(self.text, translation.text)
        except Exception as e:
            self.translation_ready.emit(self.text, f"Translation error: {e}")

class LiveTranslationDialog(QDialog):
    def __init__(self, parent=None, update_interval=1000):
        super().__init__(parent)
        self.setWindowTitle("Live Translation")
        self.resize(400, 300)
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_translation)
        self.timer.start(update_interval)
        # Define a region around the current mouse cursor (200x100 pixels, centered)
        self.region = self.get_default_region()
        self.translation_thread = None

    def get_default_region(self):
        x, y = pyautogui.position()
        return (max(0, x - 100), max(0, y - 50), 200, 100)

    def update_translation(self):
        # Update region in case the cursor moved
        self.region = self.get_default_region()
        screenshot = pyautogui.screenshot(region=self.region)
        try:
            extracted_text = pytesseract.image_to_string(screenshot)
        except Exception as e:
            extracted_text = ""
            print("Error during OCR:", e)
        if extracted_text.strip():
            # If a previous translation is still running, skip this update
            if self.translation_thread is not None and self.translation_thread.isRunning():
                return
            self.translation_thread = TranslationThread(extracted_text)
            self.translation_thread.translation_ready.connect(self.on_translation_ready)
            self.translation_thread.start()
        else:
            self.text_edit.setPlainText("No text detected.")

    def on_translation_ready(self, original, translated):
        self.text_edit.setPlainText(f"Original:\n{original}\n\nTranslation:\n{translated}")

    def closeEvent(self, event):
        self.timer.stop()
        if self.translation_thread is not None:
            self.translation_thread.quit()
            self.translation_thread.wait()
        event.accept()
