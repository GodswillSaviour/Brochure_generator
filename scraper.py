from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

# Standard headers to fetch a website and avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    cleaned of scripts/styles and truncated to a sensible limit.
    """
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input", "nav", "footer"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
        
    return (title + "\n\n" + text)[:2_000]


def fetch_website_links(url):
    """
    Finds anchor tags on the page, converts relative links to absolute URLs,
    and returns a structured dictionary of links.
    """
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        absolute_url = urljoin(url, href)
        
        # Only keep valid HTTP/HTTPS links
        if absolute_url.startswith("http"):
            link_text = link.get_text(strip=True) or "External Link"
            links.append({"type": link_text[:30], "url": absolute_url})
            
    # Deduplicate by URL and limit to the first 5 links to prevent token overload
    unique_links = list({v['url']: v for v in links}.values())[:5]
    return {"links": unique_links}


def fetch_page_and_all_relevant_links(url):
    """
    Scrapes the main landing page plus its relevant sub-links,
    combining them into a single Markdown-formatted string.
    """
    parts = []
    
    # 1. Fetch main landing page content
    contents = fetch_website_contents(url)
    parts.append(f"## Landing Page:\n\n{contents}\n\n## Relevant Links:\n")
    
    # 2. Fetch sub-links and their contents
    try:
        relevant_links = fetch_website_links(url)
        for link in relevant_links.get('links', []):
            parts.append(f"\n\n### Link: {link['type']}\n")
            sub_content = fetch_website_contents(link["url"])
            parts.append(sub_content)
    except Exception as e:
        parts.append(f"\n[Error fetching sub-links: {e}]")
        
    return "".join(parts)