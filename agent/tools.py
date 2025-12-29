from langchain_core.tools import tool
from duckduckgo_search import DDGS
import os
import requests

@tool
def web_search(query: str):
    """Search the web for general information."""
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        return "\n".join([f"{r['title']} - {r['href']}\n{r['body']}" for r in results])
    except Exception as e:
        return f"Error searching web: {e}"

@tool
def search_yelp(term: str, location: str):
    """Search Yelp for businesses. Requires term (e.g. 'pizza') and location (e.g. 'San Francisco')."""
    api_key = os.getenv("YELP_API_KEY")
    if not api_key:
        return "Error: Yelp API key not configured."
    
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"term": term, "location": location, "limit": 5}
    
    try:
        response = requests.get("https://api.yelp.com/v3/businesses/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for business in data.get("businesses", []):
            name = business.get("name")
            rating = business.get("rating")
            url = business.get("url")
            results.append(f"{name} ({rating} stars) - {url}")
            
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Error searching Yelp: {e}"

@tool
def scrape_page(url: str):
    """Scrape the text content of a specific URL."""
    # Simple scraping using requests + beautifulsoup (or langchain loader)
    # Using AsyncHtmlLoader for better handling if needed, but requests is simpler for sync tool
    # Let's use a simple requests + bs4 approach for robustness in this tool
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:2000] + "..." if len(text) > 2000 else text
    except Exception as e:
        return f"Error scraping page: {e}"

def get_tools():
    return [web_search, search_yelp, scrape_page]
