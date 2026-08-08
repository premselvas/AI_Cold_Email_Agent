import trafilatura
import requests
from bs4 import BeautifulSoup

class JobDescriptionParser:
    """Class to parse job descriptions from URLs or text."""
    
    @staticmethod
    def parse_url(url: str) -> str:
        """Extract main text from job posting URL."""
        if not url:
            return ""
            
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text:
                    return text.strip()
                    
            # Fallback to requests + BeautifulSoup
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Remove scripts and styles
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.extract()
                text = soup.get_text(separator='\n')
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                return '\n'.join(chunk for chunk in chunks if chunk)
                
            return ""
        except Exception:
            return ""

def extract_job_description(url):
    """Backward compatibility function."""
    return JobDescriptionParser.parse_url(url)