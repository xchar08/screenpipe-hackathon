import re
import sys
import time
from assistant.commands import (
    execute_command, open_app, open_url, close_app, close_url,
    play_audio, pause_audio, search_term, handle_copy_text_command
)
from apis.screenpipe_api import get_object_position
from apis.nebius_api import generate_response as generate_nebius_response
from PyQt5.QtWidgets import QMessageBox, QApplication
from voice.voice_output import say
import pyautogui
import speech_recognition as sr

class Assistant:
    def __init__(self):
        self.command_history = []
        self.pending_context = None

    def process_command(self, command: str):
        self.command_history.append(command)
        # Support command chaining separated by " and "
        sub_commands = re.split(r'\s+and\s+', command)
        for sub in sub_commands:
            sub = sub.strip()
            if sub:
                self.execute(sub)

    def execute(self, command: str):
        command_lower = command.lower()
        if "screen position of" in command_lower:
            # Use Screenpipe to report the position of an object.
            object_name = command_lower.split("screen position of")[-1].strip()
            coords = get_object_position(object_name)
            if coords:
                msg = f"Screen position of '{object_name}': {coords}"
                print(msg)
                say(msg)
            else:
                msg = f"Could not find '{object_name}' on screen."
                print(msg)
                say(msg)
        elif command_lower.startswith("click on"):
            object_name = command_lower.replace("click on", "").strip()
            coords = self.get_click_coordinates(object_name)
            if coords:
                execute_command("click", position=coords)
                say(f"Clicked on {object_name}")
            else:
                say(f"Could not determine where to click for {object_name}")
                print(f"Could not determine coordinates for {object_name}")
        elif command_lower.startswith("right click on"):
            object_name = command_lower.replace("right click on", "").strip()
            coords = get_object_position(object_name)
            if coords:
                execute_command("right_click", position=coords)
                say(f"Right clicked on {object_name}")
            else:
                say(f"Object {object_name} not found for right-click")
                print(f"Object '{object_name}' not found for right-click")
        elif command_lower.startswith("copy text"):
            handle_copy_text_command(command)
        elif command_lower.startswith("copy"):
            execute_command("copy")
            say("Copied to clipboard.")
        elif command_lower.startswith("paste"):
            execute_command("paste")
            say("Pasted from clipboard.")
        elif command_lower.startswith("type in"):
            # "type in" command: listen for your speech and gradually type it out.
            prompt = command[len("type in"):].strip()
            self.type_in(prompt)
        elif command_lower.startswith("type generate"):
            # "type generate" command: use Nebius to generate text then type it gradually.
            prompt = command[len("type generate"):].strip()
            self.type_generate(prompt)
        elif command_lower.startswith("type"):
            # Fall back: if just "type" is said, type the remainder instantly.
            text = command[command_lower.find("type") + len("type"):].strip()
            execute_command("type", text=text)
            say(f"Typed: {text}")
        elif command_lower.startswith("create file"):
            execute_command("create_file", command=command)
        elif command_lower.startswith("create project"):
            execute_command("create_project", command=command)
        elif command_lower.startswith("open app"):
            app_name = command_lower.replace("open app", "").strip()
            open_app(app_name)
            say(f"Opening app {app_name}")
        elif command_lower.startswith("open url"):
            query = command_lower.replace("open url", "").strip()
            open_url(query)
            say(f"Opening URL for query: {query}")
        elif command_lower.startswith("close app"):
            app_name = command_lower.replace("close app", "").strip()
            close_app(app_name)
            say(f"Closing app {app_name}")
        elif command_lower.startswith("close url"):
            query = command_lower.replace("close url", "").strip()
            close_url(query)
            say(f"Closing URL for query: {query}")
        elif command_lower.startswith("play audio"):
            play_audio()
            say("Playing audio.")
        elif command_lower.startswith("pause audio"):
            pause_audio()
            say("Pausing audio.")
        elif command_lower.startswith("search"):
            term = command_lower.replace("search", "").strip()
            search_term(term)
            say(f"Searching for {term}.")
        elif command_lower.startswith("live translate near my cursor"):
            from ui.live_translation_dialog import LiveTranslationDialog
            dialog = LiveTranslationDialog()
            dialog.exec_()
        elif command_lower.startswith("hey jarivs, let's talk"):
            self.conversational_mode()
        elif command_lower.startswith("shutdown"):
            self.shutdown()
        elif command_lower.startswith("answer this") or command_lower.startswith("answer me"):
            # Extract the question after "answer this" or "answer me"
            question = command.split("answer", 1)[1].strip()
            prompt = f"Answer the following question in a cute and friendly tone: {question}"
            answer = generate_nebius_response(prompt)
            if answer:
                say(answer)
                print("Answer:", answer)
            else:
                say("Sorry, I couldn't understand your question.")
                print("Could not generate an answer for:", question)
        else:
            # For ambiguous commands, first say we couldn't understand, then attempt code generation.
            say("I couldn't understand that command. Attempting to generate code for: " + command)
            print("Ambiguous command; attempting to generate code for:", command)
            prompt = (
                f"Generate Python code that uses Selenium to perform the following task: {command}.\n"
                "The code should be self-contained and include only the code with no explanations."
            )
            code_snippet = generate_nebius_response(prompt)
            if code_snippet:
                self.confirm_and_execute_generated_code(code_snippet)
            else:
                say("Sorry, I couldn't generate code for that command.")
                print("Nebius returned no code; unable to process the command:", command)

    def get_click_coordinates(self, item: str) -> tuple:
        """
        Uses Screenpipe's API exclusively to determine the coordinates
        for clicking on a specified UI element.
        """
        coords = get_object_position(item)
        return coords

    def conversational_mode(self):
        """
        Enters conversational mode. Miso will respond to your questions with a cute personality.
        The conversation continues until you say "ok, that's enough talking".
        """
        say("Sure, let's talk! You can ask me anything. Say 'ok, that's enough talking' when you're done.")
        while True:
            user_input = self.listen_for_speech("I'm listening...")
            if user_input:
                if "ok, that's enough talking" in user_input.lower():
                    say("Alright, I'll stop talking now!")
                    break
                prompt = f"Answer the following question in a friendly, conversational, and cute tone: {user_input}"
                answer = generate_nebius_response(prompt)
                if answer:
                    say(answer)
                    print("Conversational answer:", answer)
                else:
                    say("I couldn't understand that, please try again.")
            else:
                say("I didn't catch that, please speak again.")

    def type_in(self, prompt: str):
        """
        Listens for your speech and then gradually types it.
        If prompt text is provided, it will type that text.
        Otherwise, it listens for your spoken words.
        """
        if not prompt:
            # Listen for speech
            typed_text = self.listen_for_speech("What would you like me to type?")
        else:
            typed_text = prompt
        if typed_text:
            say("Typing your text.")
            for char in typed_text:
                pyautogui.typewrite(char)
                time.sleep(0.05)  # Adjust delay for gradual typing
        else:
            say("I didn't catch anything to type.")

    def type_generate(self, prompt: str):
        """
        Uses Nebius to generate text based on your prompt, then gradually types it.
        """
        say("Generating text, please wait.")
        generated_text = generate_nebius_response(prompt)
        if generated_text:
            say("Typing generated text.")
            for char in generated_text:
                pyautogui.typewrite(char)
                time.sleep(0.05)
        else:
            say("I couldn't generate text for that prompt.")

    def listen_for_speech(self, prompt: str = "") -> str:
        """
        Listens for a full spoken response and returns it as text.
        """
        if prompt:
            say(prompt)
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            try:
                print("Listening for speech...")
                audio = r.listen(source)
                response = r.recognize_google(audio)
                print("Speech recognized:", response)
                return response
            except Exception as e:
                print("Speech recognition error:", e)
                return ""

    def shutdown(self):
        """
        Plays a shutdown sound and exits the application.
        """
        say("Shutting down. Goodbye!")
        try:
            from playsound import playsound
            playsound("shutdown.mp3")
        except Exception as e:
            print("Error playing shutdown sound:", e)
        QApplication.quit()
        sys.exit(0)

    def confirm_and_execute_generated_code(self, code_snippet: str):
        """
        Uses Nebius to produce a summary of the generated code, then shows a popup
        asking the user to confirm whether to execute the code.
        The code is written to a temporary file and executed using subprocess.
        """
        summary_prompt = f"Summarize and explain what the following code will do:\n{code_snippet}"
        summary = generate_nebius_response(summary_prompt)
        parent = QApplication.activeWindow()
        message = f"Generated Code Summary:\n\n{summary}\n\nDo you want to execute this code?"
        reply = QMessageBox.question(parent, "Confirm Execution", message,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                import tempfile
                import subprocess
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                    temp_file.write(code_snippet)
                    temp_path = temp_file.name
                subprocess.Popen(["python", temp_path])
                say("Executing generated code.")
                print("Executed generated code successfully from:", temp_path)
            except Exception as e:
                say("Error executing generated code.")
                print("Error executing generated code:", e)
        else:
            say("Cancelled executing generated code.")
            print("Execution of generated code cancelled.")
