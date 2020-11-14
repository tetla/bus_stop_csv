import json, os
from dotenv import load_dotenv
import requests

def geocoding(address: str):
    return "not supported"

def reverse_geocoding(lat: float, lng: float, key: str,language="ja", format="json"):
    url = f"https://maps.googleapis.com/maps/api/geocode/{format}"
    payload = {"latlng": f"{lat},{lng}", "key": key, "language": language}
    r = requests.get(url, params=payload)
    data = r.json()
    address = json.dumps(data["results"][0]["formatted_address"])
    # ユニコードのおまじない
    return address.encode().decode('unicode-escape')

if __name__ == "__main__":
    load_dotenv()
    key = os.environ["APIKEY"]
    address = reverse_geocoding(35.684,139.836,key)
    print(address)

