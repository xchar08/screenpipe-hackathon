import pyautogui
import keyboard
import os
import subprocess
import re

def execute_command(action, **kwargs):
    if action == "click":
        pos = kwargs.get("position")
        if pos:
            pyautogui.click(pos[0], pos[1])
            print(f"Clicked at {pos}.")
    elif action == "right_click":
        pos = kwargs.get("position")
        if pos:
            pyautogui.rightClick(pos[0], pos[1])
            print(f"Right-clicked at {pos}.")
    elif action == "copy":
        keyboard.send("ctrl+c")
        print("Copy executed.")
    elif action == "paste":
        keyboard.send("ctrl+v")
        print("Paste executed.")
    elif action == "type":
        text = kwargs.get("text", "")
        keyboard.write(text)
        print(f"Typed: {text}")
    elif action == "create_file":
        command = kwargs.get("command", "")
        match = re.search(r'file\s+of\s+type\s+(\w+)\s+in\s+([\w\s/\\]+)', command.lower())
        if match:
            file_type = match.group(1)
            directory = match.group(2).strip()
            filename = f"new_file.{file_type}"
            full_path = os.path.join(directory, filename)
            os.makedirs(directory, exist_ok=True)
            with open(full_path, "w") as f:
                if file_type == "py":
                    f.write("# Python file created by Toph\n")
                else:
                    f.write("New file created by Toph.\n")
            print(f"Created file: {full_path}")
        else:
            print("Could not parse file creation command.")
    elif action == "create_project":
        command = kwargs.get("command", "")
        match = re.search(r'project\s+of\s+type\s+(\w+)\s+in\s+([\w\s/\\]+)', command.lower())
        if match:
            project_type = match.group(1)
            directory = match.group(2).strip()
            project_dir = os.path.join(directory, f"new_{project_type}_project")
            os.makedirs(project_dir, exist_ok=True)
            if project_type == "python":
                with open(os.path.join(project_dir, "main.py"), "w") as f:
                    f.write("# Main Python file for new project\n")
            print(f"Created project at: {project_dir}")
        else:
            print("Could not parse project creation command.")
    else:
        print("Unknown command action:", action)
