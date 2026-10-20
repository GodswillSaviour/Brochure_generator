
import requests
from bs4 import BeautifulSoup


def fetch_website_contents(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return soup.get_text(separator=" ", strip=True)
