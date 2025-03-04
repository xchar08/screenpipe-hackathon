# Toph – Your Voice-Controlled Assistant

Toph is a voice-controlled assistant that leverages screen context via Screenpipe, dynamic text generation via Nebius, and various OS integrations to help you interact with your computer hands-free. Toph can perform actions like clicking UI elements, copying text from the screen, opening applications and URLs, live translating text near your cursor, engaging in conversation, generating and typing code, and even creating GitHub repositories and deploying them to Vercel—all through voice commands.

## Features

- **Voice Activation:**  
  Use a wake word (e.g., "hey toph") to activate voice command processing.

- **Screen Interaction:**  
  Utilize Screenpipe’s OCR and object detection to click on UI elements and copy text from the screen.

- **Live Translation:**  
  Open a live translation dialog that continuously captures a region around your mouse cursor, performs OCR with Tesseract, and translates text to English.

- **Conversational Mode:**  
  Trigger conversational mode (e.g., "hey jarivs, let's talk") for a cute, friendly back-and-forth until you say "ok, that's enough talking."

- **Dynamic Code Generation & Typing:**  
  Toph uses Nebius to live-generate Python code for ambiguous commands, gradually types text based on your spoken commands, and even executes the code upon confirmation.

- **Repository Creation & Deployment:**  
  Toph can fully generate code for projects, create a GitHub repository, and deploy the project to Vercel using voice commands.

- **Gradual Typing:**  
  Commands like “type in” or “type generate” allow Toph to gradually type text (simulating natural typing) rather than printing it instantly.

- **Startup and Shutdown Sounds:**  
  Plays a startup sound on launch and a shutdown sound when you issue a shutdown command.

## Installation

### Prerequisites

- Python 3.8+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed on your system  
  (Ensure that the `TESSDATA_PREFIX` environment variable is set correctly to point to the tessdata folder)
- [Screenpipe](https://github.com/mediar-ai/screenpipe) installed and running (with OCR enabled)
- Nebius API access with a valid API key

### Clone the Repository

```bash
git clone https://github.com/yourusername/screenpipe-hackathon.git
cd screenpipe-hackathon
```

### Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

**requirements.txt** includes:

```txt
PyQt5
SpeechRecognition
pyaudio
pyautogui
keyboard
rapidfuzz
requests
python-dotenv
pyttsx3
beautifulsoup4
pytesseract
Pillow
googletrans==4.0.0-rc1
playsound
```

## Configuration

1. **Environment Variables:**  
   Create a `.env` file in the project root with your Nebius API key:

   ```env
   NEBIUS_API_KEY=your_actual_nebius_api_key
   ```

2. **Tesseract Data:**  
   In the `ui/live_translation_dialog.py` file, ensure that the `TESSDATA_PREFIX` is set to the folder containing your tessdata, for example:

   ```python
   os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
   ```

3. **Screenpipe Settings:**  
   Start Screenpipe via CLI with options (example):

   ```bash
   screenpipe --data-dir %LOCALAPPDATA%\screenpipe --ocr-engine windows-native --disable-telemetry
   ```

## Usage

Run the assistant by executing:

```bash
python main.py
```

### Example Commands

- **UI Interaction:**
  - "click on Microsoft Edge icon"  
    *Toph uses Screenpipe to locate and click on the specified icon.*

- **Copy Text:**
  - "copy text everything you see"  
    *Toph retrieves OCR text from the screen via Screenpipe.*

- **Live Translation:**
  - "live translate near my cursor"  
    *Opens a live translation dialog that captures text near the mouse, translates it to English, and displays it in real time.*

- **Conversational Mode:**
  - "hey jarivs, let's talk"  
    *Toph enters conversational mode, engaging in a friendly dialogue until you say "ok, that's enough talking."*

- **Dynamic Typing:**
  - "type in [your spoken text]"  
    *Toph listens and gradually types the dictated text.*
  - "type generate [prompt]"  
    *Toph uses Nebius to generate text based on your prompt and then gradually types it out.*

- **Answering Questions:**
  - "answer me who's a good boy"  
    *Toph answers in a cute, conversational tone.*

- **Repository & Deployment:**
  - "generate code for a nextjs app and create a repository"  
    *Toph live-generates code, creates a GitHub repository, and deploys the project to Vercel.*
  
- **Shutdown:**
  - "shutdown"  
    *Toph plays a shutdown sound and exits the application.*

## Contributing

Contributions are welcome! Please fork the repository and open a pull request with your improvements.

## License

This project is open source. See [LICENSE](LICENSE) for details.
