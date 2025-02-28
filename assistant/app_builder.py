import os
import subprocess
from apis.cerebras_api import generate_code as generate_cerebras_code
from apis.nebius_api import generate_response as generate_nebius_response
from PyQt5.QtWidgets import QMessageBox, QApplication

def create_application(app_type: str, target_directory: str) -> bool:
    """
    Generate a full application of the given type using code generation,
    then create the corresponding folders and files.
    """
    prompt = f"Generate full {app_type} application code including folder structure, necessary files, and configurations."
    code = generate_cerebras_code(prompt)
    if not code:
        code = generate_nebius_response(prompt)
    if not code:
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
            # In this simple example, write the generated code to a main file.
            main_file = os.path.join(target_directory, "main.py")
            with open(main_file, "w") as f:
                f.write(code)
            print(f"Application created at {target_directory}.")
            return True
        except Exception as e:
            print("Error creating application:", e)
            return False
    else:
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
            # Optionally, show git diff or similar here.
            result = subprocess.run(["vercel", "--prod"], cwd=target_directory, capture_output=True, text=True)
            if result.returncode == 0:
                print("Deployment successful:\n", result.stdout)
                return True
            else:
                print("Deployment failed:\n", result.stderr)
                return False
        except Exception as e:
            print("Error during deployment:", e)
            return False
    else:
        print("Deployment cancelled.")
        return False
