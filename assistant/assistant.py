import re
from assistant.commands import execute_command
from apis.screenpipe_api import get_object_position
from apis.cerebras_api import generate_code as generate_cerebras_code
from apis.nebius_api import generate_response as generate_nebius_response
from PyQt5.QtWidgets import QMessageBox, QApplication

class Assistant:
    def __init__(self):
        self.command_history = []
        self.pending_context = None

    def process_command(self, command: str):
        self.command_history.append(command)
        # Support command chaining using " and "
        sub_commands = re.split(r'\s+and\s+', command)
        for sub in sub_commands:
            sub = sub.strip()
            if sub:
                self.execute(sub)

    def execute(self, command: str):
        command_lower = command.lower()
        if "screen position of" in command_lower:
            object_name = command_lower.split("screen position of")[-1].strip()
            pos = get_object_position(object_name)
            if pos:
                print(f"Screen position of '{object_name}': {pos}")
            else:
                print(f"Could not find '{object_name}' on screen.")
        elif command_lower.startswith("click on"):
            object_name = command_lower.replace("click on", "").strip()
            pos = get_object_position(object_name)
            if pos:
                execute_command("click", position=pos)
            else:
                print(f"Object '{object_name}' not found for click.")
        elif command_lower.startswith("right click on"):
            object_name = command_lower.replace("right click on", "").strip()
            pos = get_object_position(object_name)
            if pos:
                execute_command("right_click", position=pos)
            else:
                print(f"Object '{object_name}' not found for right-click.")
        elif command_lower.startswith("copy"):
            execute_command("copy")
        elif command_lower.startswith("paste"):
            execute_command("paste")
        elif command_lower.startswith("type"):
            text = command[command_lower.find("type") + len("type"):].strip()
            execute_command("type", text=text)
        elif command_lower.startswith("create file"):
            execute_command("create_file", command=command)
        elif command_lower.startswith("create project"):
            execute_command("create_project", command=command)
        elif command_lower.startswith("create application"):
            # Example: "create application of type nextjs in /path/to/app"
            match = re.search(r'create application of type (\w+)\s+in\s+([\w\s/\\:]+)', command_lower)
            if match:
                app_type = match.group(1)
                target_directory = match.group(2).strip()
                from assistant.app_builder import create_application
                create_application(app_type, target_directory)
            else:
                print("Could not parse application creation command.")
        elif command_lower.startswith("deploy application"):
            # Example: "deploy application in /path/to/app"
            match = re.search(r'deploy application in\s+([\w\s/\\:]+)', command_lower)
            if match:
                target_directory = match.group(1).strip()
                from assistant.app_builder import deploy_application
                deploy_application(target_directory)
            else:
                print("Could not parse deployment command.")
        else:
            # Unclear commands are delegated for on-the-fly code generation.
            print("Delegating command to Cerebras for code generation...")
            code_snippet = generate_cerebras_code(command)
            if code_snippet:
                self.confirm_and_execute_generated_code(code_snippet)
            else:
                print("Cerebras returned no code; trying Nebius...")
                response = generate_nebius_response(command)
                if response:
                    print("Nebius response:\n", response)
                else:
                    print("Unable to process the command:", command)

    def confirm_and_execute_generated_code(self, code_snippet: str):
        """
        Uses Nebius to generate a summary of the generated code, then shows a popup
        asking the user to confirm whether to execute the code.
        """
        summary_prompt = f"Summarize and explain what the following code will do:\n{code_snippet}"
        summary = generate_nebius_response(summary_prompt)
        parent = QApplication.activeWindow()
        message = f"Generated Code Summary:\n\n{summary}\n\nDo you want to execute this code?"
        reply = QMessageBox.question(parent, "Confirm Execution", message,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                exec(code_snippet, globals())
                print("Executed generated code successfully.")
            except Exception as e:
                print("Error executing generated code:", e)
        else:
            print("Execution of generated code cancelled.")
