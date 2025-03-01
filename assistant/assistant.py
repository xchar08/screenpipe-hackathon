import re
from assistant.commands import (
    execute_command, open_app, open_url, close_app, close_url,
    play_audio, pause_audio, search_term, handle_copy_text_command
)
from apis.screenpipe_api import get_object_position
from apis.nebius_api import generate_response as generate_nebius_response
from PyQt5.QtWidgets import QMessageBox, QApplication
from voice.voice_output import say

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
            # Handle commands like "copy text everything you see" or "copy text in my search bar"
            handle_copy_text_command(command)
        elif command_lower.startswith("copy"):
            execute_command("copy")
            say("Copied to clipboard.")
        elif command_lower.startswith("paste"):
            execute_command("paste")
            say("Pasted from clipboard.")
        elif command_lower.startswith("type"):
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
        elif command_lower.startswith("what do you see"):
            self.what_do_you_see()
        else:
            # For ambiguous commands, delegate to Nebius for code generation.
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

    def what_do_you_see(self):
        """
        Uses Screenpipe's OCR to return the text it sees on screen.
        """
        from apis.screenpipe_api import get_ocr_text
        text = get_ocr_text("everything you see")
        if text:
            say(f"I see: {text}")
            print("OCR text:", text)
        else:
            say("I couldn't detect any text on screen.")
            print("No OCR text found.")

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
