import pyautogui
import keyboard
import os
import subprocess
import webbrowser
import re
import platform
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from PyQt5.QtWidgets import QMessageBox, QApplication
from voice.voice_output import say
import speech_recognition as sr

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
                    f.write("# Python file created by Hey Miso\n")
                else:
                    f.write("New file created by Hey Miso.\n")
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

def open_app(app_name: str):
    try:
        if platform.system() == "Windows":
            subprocess.Popen(app_name)
        else:
            subprocess.Popen(["open", "-a", app_name])
        print(f"Opened app: {app_name}")
    except Exception as e:
        print("Error opening app:", e)

def open_url(query: str):
    """
    Use BeautifulSoup to webscrape the first search result for the query.
    It queries DuckDuckGo’s HTML interface and extracts the first result.
    If the URL is a DuckDuckGo redirect, it extracts the actual URL from the 'uddg' parameter.
    """
    query = query.strip()
    search_url = "https://html.duckduckgo.com/html/?q=" + re.sub(r'\s+', '+', query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        first_result = soup.find("a", class_="result__a")
        if first_result and first_result.get("href"):
            url = first_result.get("href")
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "uddg" in qs:
                url = qs["uddg"][0]
        else:
            url_candidate = query.replace(" ", "")
            url = f"https://www.{url_candidate}.com"
        webbrowser.open(url)
        print(f"Opened URL: {url}")
    except Exception as e:
        print("Error opening URL:", e)

def close_app(app_name: str):
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["taskkill", "/IM", f"{app_name}.exe", "/F"])
        else:
            subprocess.Popen(["pkill", app_name])
        print(f"Closed app: {app_name}")
    except Exception as e:
        print("Error closing app:", e)

def close_url(query: str):
    """
    Closes the active browser tab by simulating the 'Ctrl+W' (or 'Cmd+W' on macOS) keystroke.
    Assumes the target browser tab is active.
    """
    print(f"Attempting to close browser tab for query: {query}")
    try:
        if platform.system() == "Darwin":
            keyboard.send("command+w")
        else:
            keyboard.send("ctrl+w")
        print("Closed active browser tab.")
    except Exception as e:
        print("Error closing URL:", e)

def play_audio():
    try:
        keyboard.send("play/pause media")
        print("Toggled audio playback (play).")
    except Exception as e:
        print("Error playing audio:", e)

def pause_audio():
    try:
        keyboard.send("play/pause media")
        print("Toggled audio playback (pause).")
    except Exception as e:
        print("Error pausing audio:", e)

def listen_for_yes_no():
    """
    Listens until the user stops speaking and returns True if 'yes' is in the response,
    False if 'no' is in the response, or None if unrecognized.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            print("Listening for yes/no response...")
            audio = r.listen(source, phrase_time_limit=3)
            response = r.recognize_google(audio).lower()
            print("Voice response received:", response)
            if "yes" in response:
                return True
            elif "no" in response:
                return False
            else:
                return None
        except Exception as e:
            print("Voice recognition error:", e)
            return None

def get_confirmation(prompt: str):
    """
    First, try to get a yes/no answer from voice input (listening until silence).
    If no valid voice response is received, fall back to a popup dialog.
    """
    say(prompt)
    voice_response = listen_for_yes_no()
    if voice_response is not None:
        return voice_response
    else:
        reply = QMessageBox.question(
            QApplication.activeWindow(),
            "Confirm",
            prompt,
            QMessageBox.Yes | QMessageBox.No
        )
        return True if reply == QMessageBox.Yes else False

def search_term(term: str):
    """
    Searches the term using DuckDuckGo and interactively goes through results.
    For each result, it asks:
      - Would you like me to read the result title?
      - Would you like me to open this result?
    This uses voice input (if available) or a popup for confirmation.
    """
    term = term.strip()
    search_url = "https://html.duckduckgo.com/html/?q=" + re.sub(r'\s+', '+', term)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a")
        num_results = len(results)
        msg = f"{num_results} items found for '{term}'."
        print(msg)
        say(msg)
        if num_results == 0:
            return
        for i, result in enumerate(results, start=1):
            title = result.get_text().strip()
            url = result.get("href")
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "uddg" in qs:
                url = qs["uddg"][0]
            prompt_read = f"Result {i}: {title}. Would you like me to read this result?"
            if get_confirmation(prompt_read):
                say(title)
            prompt_open = f"Result {i}: {title}. Would you like me to open this result?"
            if get_confirmation(prompt_open):
                webbrowser.open(url)
                print(f"Opened URL: {url}")
            prompt_continue = "Would you like me to check the next result?"
            if not get_confirmation(prompt_continue):
                break
    except Exception as e:
        print("Error performing search:", e)
