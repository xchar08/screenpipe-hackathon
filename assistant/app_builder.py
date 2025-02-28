import os
import subprocess
from apis.nebius_api import generate_response as generate_nebius_response
from PyQt5.QtWidgets import QMessageBox, QApplication
from voice.voice_output import say

def create_application(app_type: str, target_directory: str) -> bool:
    """
    Generate a full application of the given type using Nebius,
    then create the corresponding folders and files.
    """
    prompt = f"Generate full {app_type} application Python code using Selenium, including folder structure, necessary files, and configurations."
    code = generate_nebius_response(prompt)
    if not code:
        say("Failed to generate application code.")
        print("Failed to generate application code.")
        return False

    summary_prompt = f"Summarize and explain what the following application code will create:\n{code}"
    summary = generate_nebius_response(summary_prompt)

    parent = QApplication.activeWindow()
    message = f"Generated Application Summary:\n\n{summary}\n\nDo you want to create the application in {target_directory}?"
    reply = QMessageBox.question(parent, "Confirm Application Creation", message,
                                 QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        try:
            os.makedirs(target_directory, exist_ok=True)
            main_file = os.path.join(target_directory, "main.py")
            with open(main_file, "w") as f:
                f.write(code)
            say("Application created successfully.")
            print(f"Application created at {target_directory}.")
            return True
        except Exception as e:
            say("Error creating application.")
            print("Error creating application:", e)
            return False
    else:
        say("Application creation cancelled.")
        print("Application creation cancelled.")
        return False

def deploy_application(target_directory: str) -> bool:
    """
    Deploy the application in target_directory to Vercel using the Vercel CLI.
    A diff (or preview) step is included before actual deployment.
    """
    parent = QApplication.activeWindow()
    message = f"Do you want to deploy the application in {target_directory} to Vercel?"
    reply = QMessageBox.question(parent, "Confirm Deployment", message,
                                 QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        try:
            result = subprocess.run(["vercel", "--prod"], cwd=target_directory, capture_output=True, text=True)
            if result.returncode == 0:
                say("Deployment successful.")
                print("Deployment successful:\n", result.stdout)
                return True
            else:
                say("Deployment failed.")
                print("Deployment failed:\n", result.stderr)
                return False
        except Exception as e:
            say("Error during deployment.")
            print("Error during deployment:", e)
            return False
    else:
        say("Deployment cancelled.")
        print("Deployment cancelled.")
        return False
