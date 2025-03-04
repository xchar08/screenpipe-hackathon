import os
import requests

# Adjust these URLs based on your Screenpipe service configuration.
SCREENPIPE_API_URL = "http://localhost:3030/search"
SCREENPIPE_OCR_URL = "http://localhost:3030/ocr"  # Example OCR endpoint

def get_object_position(object_name: str):
    params = {
        "q": object_name,
        "content_type": "ocr",
        "limit": 1
    }
    try:
        response = requests.get(SCREENPIPE_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("pagination", {}).get("total", 0) > 0:
                item = data["data"][0]
                # Assume coordinates are provided in the "coordinates" field.
                return item.get("coordinates", None)
            else:
                return None
        else:
            print("Screenpipe API error:", response.text)
            return None
    except Exception as e:
        print("Error calling Screenpipe API:", e)
        return None

def get_ocr_text(query: str):
    """
    Queries Screenpipe's OCR endpoint to retrieve text.
    If query is empty or "everything you see", returns all OCR text.
    """
    params = {
        "q": query,
        "content_type": "ocr"
    }
    try:
        response = requests.get(SCREENPIPE_OCR_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            texts = [item.get("text", "") for item in data.get("data", [])]
            return "\n".join(texts).strip()
        else:
            print("Screenpipe OCR API error:", response.text)
            return ""
    except Exception as e:
        print("Error calling Screenpipe OCR API:", e)
        return ""
