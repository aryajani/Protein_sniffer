import re
import requests
from urllib.parse import urlparse, parse_qs, unquote
from deets import API_KEY

def extract_place_id_from_url(google_maps_url):
    """Tries to extract place_id directly from the URL using regex."""
    match = re.search(r'!1s([a-zA-Z0-9_-]+)!', google_maps_url)
    return match.group(1) if match else None

def extract_name_from_url(google_maps_url):
    """Extracts the restaurant name from the Google Maps URL."""
    parsed_url = urlparse(google_maps_url)
    path_parts = parsed_url.path.split("/")
    
    for part in path_parts:
        if "+" in part:  # Restaurant name is encoded with '+' instead of spaces
            return unquote(part.replace("+", " "))
    
    return None

def get_place_id_from_api(api_key, query):
    """Uses Google Places API to get place_id from restaurant name or coordinates."""
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data.get("status") == "OK":
        return data["candidates"][0]["place_id"]
    else:
        return None

def get_menu_images(api_key, place_id):
    """Fetches menu images using the Google Places API."""
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "photos",
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if "photos" in data.get("result", {}):
        photo_refs = [photo["photo_reference"] for photo in data["result"]["photos"]]
        image_urls = [f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photo_reference={ref}&key={api_key}" for ref in photo_refs]
        return image_urls
    else:
        return ["No menu images found."]

# 🔹 Example Usage
google_maps_url = "https://www.google.com/maps/place/Vaibhav+Cafe/@19.1177851,72.810114,14z/data=!3m1!5s0x3be7c9cd999f2c13:0x62ae4d3ba4476159!4m10!1m2!2m1!1sRestaurants!3m6!1s0x3be7c9d2647c7265:0x94a596afb2b0a359!8m2!3d19.1177874!4d72.8482205!15sCgtSZXN0YXVyYW50c1oNIgtyZXN0YXVyYW50c5IBF3NvdXRoX2luZGlhbl9yZXN0YXVyYW504AEA!16s%2Fg%2F11c5xcgh61"

# Try extracting place_id directly
place_id = None

if not place_id:
    # If extraction fails, try getting it via the restaurant name
    restaurant_name = extract_name_from_url(google_maps_url)
    if restaurant_name:
        print("Extracted Restaurant Name:", restaurant_name)
        place_id = get_place_id_from_api(API_KEY, restaurant_name)

if place_id:
    print("Extracted Place ID:", place_id)
    menu_images = get_menu_images(API_KEY, place_id)
    print("Menu Images:", menu_images)
else:
    print("Could not extract Place ID.")
