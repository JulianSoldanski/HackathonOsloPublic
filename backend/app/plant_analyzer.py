import logging
import httpx
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PlantAnalyzer:
    """Analyzes power plants using Google Search and Gemini AI"""
    
    def __init__(self, google_api_key: str, gemini_api_key: str, google_search_engine_id: str):
        self.google_api_key = google_api_key
        self.gemini_api_key = gemini_api_key
        self.google_search_engine_id = google_search_engine_id
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"
        # Updated to use the latest Gemini model
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    async def search_plant_info(self, plant_name: str) -> List[Dict[str, str]]:
        """
        Search for plant information using Google Custom Search API
        
        Args:
            plant_name: Name of the power plant
            
        Returns:
            List of search results with title, link, and snippet
        """
        try:
            # Clean plant name - remove everything after " - " (space-hyphen-space)
            clean_name = plant_name.split(' - ')[0].strip()
            
            cx_id = self.google_search_engine_id
            
            params = {
                "key": self.google_api_key,
                "cx": cx_id,
                "q": clean_name,
                "num": 3
            }
            
            logger.info(f"Searching Google for: {clean_name}")
            logger.info(f"Search params: cx={cx_id}, q={params['q']}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.google_search_url, params=params)
                
                logger.info(f"Google Search API response status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                results = []
                items = data.get("items", [])
                logger.info(f"Google returned {len(items)} items")
                
                for item in items[:3]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
                
                logger.info(f"Successfully got {len(results)} Google search results for {clean_name}")
                return results
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Google Search API: {e.response.status_code}")
            logger.error(f"Response: {e.response.text[:500]}")
            logger.error(f"Using fallback sources instead")
        except Exception as e:
            logger.error(f"Error searching for plant info: {type(e).__name__}: {e}")
            logger.error(f"Using fallback sources instead")
        
        # Return curated Norwegian energy sources as fallback
        plant_encoded = clean_name.replace(' ', '+')
        return [
            {
                "title": f"NVE Search - {clean_name}",
                "link": f"https://www.nve.no/search/?query={plant_encoded}",
                "snippet": f"Search Norwegian Water Resources and Energy Directorate for information about {clean_name} construction and deadlines"
            },
            {
                "title": f"NVE Konsesjonssaker - {clean_name}",
                "link": f"https://www.nve.no/konsesjon/konsesjonssaker/?query={plant_encoded}",
                "snippet": f"Construction permits and consession information for {clean_name} from NVE"
            },
            {
                "title": f"Kraftmagasinet News - {clean_name}",
                "link": f"https://kraftmagasinet.no/?s={plant_encoded}",
                "snippet": f"Norwegian hydropower industry news about {clean_name} project updates"
            }
        ]
    
    async def fetch_page_content(self, url: str) -> str:
        """
        Fetch and extract text content from a webpage
        
        Args:
            url: URL to fetch
            
        Returns:
            Extracted text content
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                response.raise_for_status()
                
                # Parse HTML and extract text
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator='\n', strip=True)
                
                # Clean up text (limit to first 5000 characters)
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                text = '\n'.join(lines)[:5000]
                
                return text
                
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
            return ""
    
    async def analyze_with_gemini(self, plant_name: str, sources: List[Dict[str, str]], contents: List[str]) -> str:
        """
        Analyze plant information using Gemini AI
        
        Args:
            plant_name: Name of the power plant
            sources: List of source information (title, link, snippet)
            contents: List of webpage contents
            
        Returns:
            Summary from Gemini (50-100 words)
        """
        try:
            # Prepare context for Gemini
            context = f"Power Plant: {plant_name}\n\n"
            
            has_content = False
            for i, (source, content) in enumerate(zip(sources, contents), 1):
                context += f"Source {i}: {source['title']}\n"
                context += f"URL: {source['link']}\n"
                
                # Include content if available, otherwise use snippet
                if content and len(content) > 100:
                    context += f"Content:\n{content[:2000]}\n\n"
                    has_content = True
                else:
                    context += f"Snippet: {source.get('snippet', 'No content available')}\n\n"
            
            # Prepare prompt based on available information
            if has_content:
                prompt = f"""You are analyzing information about a hydropower plant construction project in Norway.

{context}

Based on the above sources, provide a summary (50-100 words) that answers:
1. Is there a construction deadline or expected completion date mentioned?
2. If yes, what is the deadline/date?
3. If no, clearly state that the deadline information is not available in these sources.

Keep the summary concise, factual, and focused on the deadline/completion date information."""
            else:
                prompt = f"""You are analyzing search results about a hydropower plant construction project in Norway.

{context}

Based on the available snippets above, provide a brief summary (50-75 words) about:
1. Whether any deadline or completion date information is mentioned in the snippets
2. If yes, what information is available
3. If no, suggest that the user should visit the provided source links for detailed information

Note: Full content is not available, so base your summary only on the snippets provided."""

            # Call Gemini API
            request_body = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 200,
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.gemini_api_url}?key={self.gemini_api_key}",
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 404:
                    logger.error("Gemini API returned 404. The API endpoint or model name may be incorrect.")
                    logger.error("Make sure the Generative Language API is enabled in your Google Cloud Console")
                    return "Unable to access Gemini AI. Please check that the Generative Language API is enabled for your API key. Visit: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com"
                
                if response.status_code == 403:
                    logger.error("Gemini API returned 403. The API key may be invalid or the API is not enabled.")
                    return "Unable to access Gemini AI. Please verify your API key and ensure the Generative Language API is enabled."
                
                response.raise_for_status()
                
                result = response.json()
                
                # Extract text from response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        text = candidate["content"]["parts"][0].get("text", "")
                        logger.info(f"Generated summary for {plant_name}: {len(text)} characters")
                        return text
                
                return "Unable to generate summary from the available sources."
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Gemini API: {e.response.status_code} - {e.response.text}")
            return f"Unable to access Gemini AI (HTTP {e.response.status_code}). Please check API configuration."
        except Exception as e:
            logger.error(f"Error analyzing with Gemini: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def analyze_plant(self, plant_name: str) -> Dict[str, any]:
        """
        Complete analysis workflow for a power plant
        
        Args:
            plant_name: Name of the power plant
            
        Returns:
            Dictionary with summary, sources, and links
        """
        try:
            # Clean plant name - remove everything after " - " (space-hyphen-space)
            clean_name = plant_name.split(' - ')[0].strip()
            
            # Step 1: Search for information
            logger.info(f"Starting analysis for plant: {clean_name}")
            search_results = await self.search_plant_info(clean_name)
            
            if not search_results:
                return {
                    "summary": "No search results found for this power plant. Unable to provide deadline information.",
                    "sources": [],
                    "links": []
                }
            
            logger.info(f"Found {len(search_results)} sources for {clean_name}")
            
            # Step 2: Fetch content from search results
            contents = []
            successful_fetches = 0
            for result in search_results:
                content = await self.fetch_page_content(result["link"])
                contents.append(content)
                if content and len(content) > 100:
                    successful_fetches += 1
            
            logger.info(f"Successfully fetched content from {successful_fetches}/{len(search_results)} sources")
            
            # Step 3: Analyze with Gemini
            summary = await self.analyze_with_gemini(clean_name, search_results, contents)
            
            # Step 4: Return results
            return {
                "summary": summary,
                "sources": [
                    {
                        "title": r["title"],
                        "url": r["link"],
                        "snippet": r["snippet"]
                    }
                    for r in search_results
                ],
                "links": [r["link"] for r in search_results]
            }
            
        except Exception as e:
            logger.error(f"Error in plant analysis: {e}")
            # Return a helpful fallback even on error
            # Clean plant name first
            clean_name = plant_name.split(' - ')[0].strip()
            plant_encoded = clean_name.replace(' ', '+')
            return {
                "summary": f"Unable to complete automated analysis for {clean_name}. Please check the provided Norwegian energy authority sources below for construction timeline and deadline information. These sources typically contain the most up-to-date information about hydropower projects in Norway.",
                "sources": [
                    {
                        "title": f"NVE Search - {clean_name}",
                        "url": f"https://www.nve.no/search/?query={plant_encoded}",
                        "snippet": "Norwegian Water Resources and Energy Directorate search"
                    },
                    {
                        "title": f"NVE Konsesjonssaker - {clean_name}",
                        "url": f"https://www.nve.no/konsesjon/konsesjonssaker/?query={plant_encoded}",
                        "snippet": "Construction permits and consession information"
                    }
                ],
                "links": [
                    f"https://www.nve.no/search/?query={plant_encoded}",
                    f"https://www.nve.no/konsesjon/konsesjonssaker/?query={plant_encoded}"
                ]
            }


def get_plant_analyzer(
    google_api_key: str, gemini_api_key: str, google_search_engine_id: str
) -> PlantAnalyzer:
    """Create a plant analyzer (no global singleton — keys may change via env)."""
    return PlantAnalyzer(google_api_key, gemini_api_key, google_search_engine_id)