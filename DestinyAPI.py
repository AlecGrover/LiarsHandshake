import requests
import urllib.parse
from config import API_KEY

BUNGIE = "https://www.bungie.net"
PLATFORM = "/Platform/"
HEADERS = {"X-API-KEY": API_KEY}


def search_for_user(user):
    url_safe_user = urllib.parse.quote(user)
    url = BUNGIE + PLATFORM + "Destiny2/SearchDestinyPlayer/-1/" + url_safe_user + "/"
    with requests.get(url, stream=True, headers=HEADERS) as r:
        data = r.json()
        return data["Response"]
