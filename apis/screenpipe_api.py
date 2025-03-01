import requests

SCREENPIPE_API_URL = "http://localhost:3030/search"

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
                # Assume that Screenpipe returns coordinates in the "coordinates" field.
                # Adjust as necessary based on your API response.
                return item.get("coordinates", (100, 100))
            else:
                return None
        else:
            print("Screenpipe API error:", response.text)
            return None
    except Exception as e:
        print("Error calling Screenpipe API:", e)
        return None
import requests

SCREENPIPE_API_URL = "http://localhost:3030/search"

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
                # Assume that Screenpipe returns coordinates in the "coordinates" field.
                # Adjust as necessary based on your API response.
                return item.get("coordinates", (100, 100))
            else:
                return None
        else:
            print("Screenpipe API error:", response.text)
            return None
    except Exception as e:
        print("Error calling Screenpipe API:", e)
        return None
