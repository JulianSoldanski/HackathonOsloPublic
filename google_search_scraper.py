import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional

class GoogleSearchScraper:
    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize the Google Custom Search scraper.
        
        Args:
            api_key: Your Google API key
            search_engine_id: Your Custom Search Engine ID (cx)
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Perform a Google Custom Search and return the top results.
        
        Args:
            query: The search query
            num_results: Number of results to return (default: 3)
            
        Returns:
            List of dictionaries containing search results
        """
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results  # Request only the number we need
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            # Extract the relevant information from the response
            results = []
            if 'items' in data:
                for item in data['items'][:num_results]:  # Ensure we only take num_results
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'displayLink': item.get('displayLink', '')
                    })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error making search request: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error during search: {e}")
            return []
    
    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape the content from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            The text content of the page, or None if scraping fails
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text: remove extra whitespace and newlines
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error scraping {url}: {e}")
            return None
    
    def search_and_scrape(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Search Google and scrape the content from the top results.
        
        Args:
            query: The search query
            num_results: Number of results to scrape (default: 3)
            
        Returns:
            List of dictionaries containing search results with scraped content
        """
        # Get search results
        search_results = self.search(query, num_results)
        
        if not search_results:
            print("No search results found")
            return []
        
        # Scrape each URL
        for idx, result in enumerate(search_results):
            print(f"Scraping {idx + 1}/{len(search_results)}: {result['link']}")
            
            content = self.scrape_url(result['link'])
            
            if content:
                # Limit content length to avoid overwhelming the LLM
                result['content'] = content[:5000]  # Adjust this limit as needed
            else:
                result['content'] = result['snippet']  # Fallback to snippet
            
            # Be polite and don't hammer servers
            if idx < len(search_results) - 1:
                time.sleep(1)
        
        return search_results
    
    def prepare_llm_context(self, scraped_results: List[Dict], max_length: int = 10000) -> str:
        """
        Prepare the scraped content for sending to an LLM.
        
        Args:
            scraped_results: List of scraped results
            max_length: Maximum total length of the context
            
        Returns:
            Formatted text ready for LLM
        """
        context_parts = []
        current_length = 0
        
        for idx, result in enumerate(scraped_results, 1):
            title = result.get('title', 'Unknown')
            link = result.get('link', 'Unknown')
            content = result.get('content', '')
            
            # Calculate how much content we can include
            header = f"\n\n=== Source {idx}: {title} ===\nURL: {link}\n\n"
            header_length = len(header)
            
            available_space = max_length - current_length - header_length
            
            if available_space <= 0:
                break
            
            # Truncate content if needed
            content_to_add = content[:available_space] if len(content) > available_space else content
            
            context_parts.append(header + content_to_add)
            current_length += len(header) + len(content_to_add)
            
            if current_length >= max_length:
                break
        
        return ''.join(context_parts)


# Example usage
def main():
    import os
    API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    if not API_KEY or not SEARCH_ENGINE_ID:
        raise SystemExit(
            "Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in the environment."
        )
    
    # Initialize scraper
    scraper = GoogleSearchScraper(API_KEY, SEARCH_ENGINE_ID)
    
    # Search and scrape
    query = "plant disease identification"
    print(f"Searching for: {query}\n")
    
    results = scraper.search_and_scrape(query, num_results=3)
    
    # Prepare context for LLM
    llm_context = scraper.prepare_llm_context(results)
    
    print("\n" + "="*80)
    print("CONTEXT FOR LLM:")
    print("="*80)
    print(llm_context[:1000] + "...\n")  # Print first 1000 chars as preview
    
    print(f"\nTotal context length: {len(llm_context)} characters")
    print(f"\nScraped {len(results)} URLs successfully")
    
    # Now you can send llm_context to your LLM
    # Example: send_to_llm(llm_context, user_question)


if __name__ == "__main__":
    main()

