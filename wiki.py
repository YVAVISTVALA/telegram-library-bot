import requests

API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

def get_reading_order(query):
    title = query.replace(" ", "_")
    r = requests.get(API + title, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json()
    text = data.get("extract")
    if not text:
        return None

    return text[:1200]
