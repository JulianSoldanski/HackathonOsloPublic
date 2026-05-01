import httpx
import logging
import math
import re
import json
import os
from typing import List, Dict, Any, Optional
from pyproj import Transformer
from bs4 import BeautifulSoup
from .config import settings

logger = logging.getLogger(__name__)


class NVEClient:
    """Client for NVE ArcGIS MapServer API"""
    
    def __init__(self):
        self.base_url = settings.nve_base_url
        self.timeout = 30.0
        
        # Initialize coordinate transformers for Norwegian coordinate systems
        # NVE data is typically in UTM Zone 33N (EPSG:32633) or ETRS89 (EPSG:25833)
        # We'll try both and see which works better
        try:
            # UTM Zone 33N (EPSG:32633) to WGS84 (EPSG:4326)
            self.utm33_to_wgs84 = Transformer.from_crs("EPSG:32633", "EPSG:4326", always_xy=True)
            # ETRS89 UTM Zone 33N (EPSG:25833) to WGS84 (EPSG:4326)  
            self.etrs89_to_wgs84 = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
            logger.info("Coordinate transformers initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize coordinate transformers: {e}")
            self.utm33_to_wgs84 = None
            self.etrs89_to_wgs84 = None
    
    def transform_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Transform coordinates from NVE coordinate system to WGS84
        
        Args:
            x: X coordinate from NVE
            y: Y coordinate from NVE
            
        Returns:
            Tuple of (longitude, latitude) in WGS84
        """
        if not self.utm33_to_wgs84 or not self.etrs89_to_wgs84:
            logger.warning("Coordinate transformers not available, using fallback")
            # Fallback to rough approximation if pyproj fails
            lon = (x - 500000) / (111320 * math.cos(math.radians(60))) + 15
            lat = (y - 6600000) / 111320 + 59.5
            return lon, lat
        
        try:
            # Try UTM Zone 33N first (most common for Norwegian data)
            try:
                lon, lat = self.utm33_to_wgs84.transform(x, y)
                logger.debug(f"Transformed using UTM33: ({x}, {y}) -> ({lon:.6f}, {lat:.6f})")
                return lon, lat
            except Exception as e:
                logger.debug(f"UTM33 transformation failed: {e}")
                
            # Try ETRS89 UTM Zone 33N as fallback
            try:
                lon, lat = self.etrs89_to_wgs84.transform(x, y)
                logger.debug(f"Transformed using ETRS89: ({x}, {y}) -> ({lon:.6f}, {lat:.6f})")
                return lon, lat
            except Exception as e:
                logger.debug(f"ETRS89 transformation failed: {e}")
                
            # If both fail, use rough approximation
            logger.warning(f"All coordinate transformations failed for ({x}, {y}), using fallback")
            lon = (x - 500000) / (111320 * math.cos(math.radians(60))) + 15
            lat = (y - 6600000) / 111320 + 59.5
            return lon, lat
            
        except Exception as e:
            logger.error(f"Coordinate transformation error: {e}")
            # Final fallback
            lon = (x - 500000) / (111320 * math.cos(math.radians(60))) + 15
            lat = (y - 6600000) / 111320 + 59.5
            return lon, lat
    
    async def fetch_layer(self, layer_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all features from a specific layer
        
        Args:
            layer_id: Layer ID (0 for existing plants, 8 for planned)
        
        Returns:
            List of plant features
        """
        url = f"{self.base_url}/{layer_id}/query"
        
        params = {
            "where": "1=1",  # Get all features
            "outFields": "*",
            "returnGeometry": "true",
            "f": "json",
            "resultOffset": 0,
            "resultRecordCount": 1000  # Fetch in batches
        }
        
        all_features = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "error" in data:
                        logger.error(f"NVE API error: {data['error']}")
                        break
                    
                    features = data.get("features", [])
                    if not features:
                        break
                    
                    all_features.extend(features)
                    
                    # Check if there are more results
                    if len(features) < params["resultRecordCount"]:
                        break
                    
                    # Fetch next batch
                    params["resultOffset"] += params["resultRecordCount"]
                    
                    logger.info(f"Fetched {len(all_features)} features from layer {layer_id}")
                    
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error fetching layer {layer_id}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error fetching layer {layer_id}: {e}")
                    break
        
        return all_features
    
    async def scrape_deadline_from_nve(self, kdb_nr: int) -> tuple[Optional[str], bool]:
        """
        Scrape construction deadline from NVE website
        
        Args:
            kdb_nr: KDB number of the plant
            
        Returns:
            Tuple of (deadline_text, success)
        """
        url = f"https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id={kdb_nr}&type=V-1"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Search for deadline text patterns
                # Looking for patterns like "Utsatt byggefrist. Ny frist er 19.12.2023"
                # or "Byggefrist" followed by a date
                # or extended deadline text like "OED vedtok 30.06.2023 å forlenge byggefrist for Gravdalen kraftverk med fem år, til 15.02.2025. Fristen for ferdigstillelse av anleggene forlenges til 15.02.2030."
                text_content = soup.get_text()
                
                # Pattern 1: "Fristen for ferdigstillelse av anleggene forlenges til DD.MM.YYYY" (most specific, highest priority)
                pattern1 = r'Fristen for ferdigstillelse av anleggene forlenges til\s*(\d{1,2}\.\d{1,2}\.\d{4})'
                match1 = re.search(pattern1, text_content, re.IGNORECASE)
                if match1:
                    deadline = match1.group(1)
                    logger.info(f"Scraped extended deadline for kdbNr {kdb_nr}: {deadline}")
                    return deadline, True
                
                # Pattern 2: "forlenge byggefrist ... til DD.MM.YYYY" - captures extended deadlines
                pattern2 = r'forlenge byggefrist[^.]*til\s*(\d{1,2}\.\d{1,2}\.\d{4})'
                matches2 = re.findall(pattern2, text_content, re.IGNORECASE)
                if matches2:
                    # If multiple dates found, return the latest one
                    from datetime import datetime
                    try:
                        dates = [datetime.strptime(d, '%d.%m.%Y') for d in matches2]
                        latest_date = max(dates)
                        deadline = latest_date.strftime('%d.%m.%Y')
                        logger.info(f"Scraped latest extended deadline for kdbNr {kdb_nr}: {deadline}")
                        return deadline, True
                    except:
                        # If date parsing fails, just use the last match
                        deadline = matches2[-1]
                        logger.info(f"Scraped extended deadline for kdbNr {kdb_nr}: {deadline}")
                        return deadline, True
                
                # Pattern 3: "Utsatt byggefrist. Ny frist er DD.MM.YYYY"
                pattern3 = r'Utsatt byggefrist\.?\s*Ny frist er\s*(\d{1,2}\.\d{1,2}\.\d{4})'
                match3 = re.search(pattern3, text_content, re.IGNORECASE)
                if match3:
                    deadline = match3.group(1)
                    logger.info(f"Scraped deadline for kdbNr {kdb_nr}: {deadline}")
                    return deadline, True
                
                # Pattern 4: "Byggefrist: DD.MM.YYYY" or "Byggefrist DD.MM.YYYY"
                pattern4 = r'Byggefrist[:\s]+(\d{1,2}\.\d{1,2}\.\d{4})'
                match4 = re.search(pattern4, text_content, re.IGNORECASE)
                if match4:
                    deadline = match4.group(1)
                    logger.info(f"Scraped deadline for kdbNr {kdb_nr}: {deadline}")
                    return deadline, True
                
                # Pattern 5: Just find any date near "frist" word
                pattern5 = r'(?:frist|deadline)[^\d]*(\d{1,2}\.\d{1,2}\.\d{4})'
                match5 = re.search(pattern5, text_content, re.IGNORECASE)
                if match5:
                    deadline = match5.group(1)
                    logger.info(f"Scraped deadline for kdbNr {kdb_nr}: {deadline}")
                    return deadline, True
                
                logger.warning(f"No deadline found for kdbNr {kdb_nr} at {url}")
                return None, False
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping deadline for kdbNr {kdb_nr}: {e}")
            return None, False
        except Exception as e:
            logger.error(f"Error scraping deadline for kdbNr {kdb_nr}: {e}")
            return None, False
    
    def parse_plant_feature(self, feature: Dict[str, Any], status: str = "existing") -> Dict[str, Any]:
        """
        Parse ArcGIS feature to our plant model
        
        Args:
            feature: Raw ArcGIS feature
            status: Plant status (existing, planned, or under_construction)
        
        Returns:
            Parsed plant dict
        """
        attrs = feature.get("attributes", {})
        geometry = feature.get("geometry", {})
        
        # Extract coordinates
        x = geometry.get("x")
        y = geometry.get("y")
        
        # Transform coordinates using pyproj for accurate conversion
        if x and y:
            try:
                lon, lat = self.transform_coordinates(x, y)
                logger.debug(f"Transformed plant coordinates: ({x}, {y}) -> ({lon:.6f}, {lat:.6f})")
                
                # Clamp to reasonable Norwegian bounds as sanity check
                lat = max(58.0, min(71.0, lat))
                lon = max(4.0, min(31.0, lon))
            except Exception as e:
                logger.error(f"Coordinate transformation failed for plant: {e}")
                lat = None
                lon = None
        else:
            lat = None
            lon = None
        
        # Handle different field names in ArcGIS API
        # Common field names: vannkraftverkNr, vannkraftverkNavn, maksYtelse_MW, etc.
        plant_id = str(attrs.get("vannkraftverkNr") or attrs.get("OBJECTID") or attrs.get("FID", "unknown"))
        name = attrs.get("vannkraftverkNavn") or attrs.get("NAVN") or attrs.get("NAME", "Unknown")
        
        # Capacity in MW
        capacity = float(attrs.get("maksYtelse_MW") or attrs.get("MAKSYTELSE") or attrs.get("MIDLYTELSE") or attrs.get("INSTALLERTYTELSE", 0))
        
        # Plant type classification
        if capacity < 1:
            plant_type = "Mikro"
        elif capacity < 10:
            plant_type = "Mini"
        else:
            plant_type = "Stor"
        
        # Additional fields
        year = attrs.get("idriftsattAar") or attrs.get("FERDIGAAR") or attrs.get("DRIFTSTART") or attrs.get("YEAR")
        kommune = attrs.get("kommuneNavn") or attrs.get("KOMMUNE") or attrs.get("KOMM")
        fylke = attrs.get("fylke") or attrs.get("FYLKE") or attrs.get("COUNTY")
        owner = attrs.get("vannkraftverkEier") or attrs.get("EIER") or attrs.get("OWNER")
        
        # Get kdbNr for under-construction plants
        kdb_nr = attrs.get("kdbNr")
        
        plant_data = {
            "id": plant_id,
            "name": name,
            "maksYtelse_MW": capacity,
            "type": plant_type,
            "year": int(year) if year else None,
            "kommune": kommune,
            "fylke": fylke,
            "owner": owner,
            "coordinates": {
                "lat": lat,
                "lon": lon
            },
            "status": status
        }
        
        # Add kdbNr for under-construction plants
        if status == "under_construction" and kdb_nr:
            plant_data["kdbNr"] = int(kdb_nr)
        
        return plant_data
    
    async def fetch_under_construction_plants(self) -> List[Dict[str, Any]]:
        """
        Fetch plants under construction (status='U') with deadline scraping
        First tries to load from local JSON file, then falls back to API
        
        Returns:
            List of under-construction plants with deadline information
        """
        logger.info("Fetching under-construction hydropower plants...")
        
        all_features = []
        
        # Try to load from local JSON file first
        json_path = os.path.join(os.path.dirname(__file__), "../data/data.json")
        json_path = os.path.abspath(json_path)  # Convert to absolute path
        
        logger.info(f"Looking for JSON file at: {json_path}")
        logger.info(f"File exists: {os.path.exists(json_path)}")
        
        if os.path.exists(json_path):
            try:
                logger.info(f"Loading under-construction plants from local file: {json_path}")
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_features = data.get("features", [])
                    logger.info(f"Loaded {len(all_features)} under-construction plants from local file")
            except Exception as e:
                logger.error(f"Error loading from JSON file: {e}", exc_info=True)
                logger.info("Falling back to NVE API...")
        else:
            logger.warning(f"JSON file not found at {json_path}, falling back to NVE API")
        
        # If no features loaded from file, try API
        if not all_features:
            logger.info("Fetching under-construction plants from NVE API...")
            url = f"{self.base_url}/8/query"
            
            params = {
                "where": "status='U'",
                "outFields": "*",
                "returnGeometry": "true",
                "f": "json",
                "resultOffset": 0,
                "resultRecordCount": 1000
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                while True:
                    try:
                        response = await client.get(url, params=params)
                        response.raise_for_status()
                        data = response.json()
                        
                        if "error" in data:
                            logger.error(f"NVE API error: {data['error']}")
                            break
                        
                        features = data.get("features", [])
                        if not features:
                            break
                        
                        all_features.extend(features)
                        
                        if len(features) < params["resultRecordCount"]:
                            break
                        
                        params["resultOffset"] += params["resultRecordCount"]
                        logger.info(f"Fetched {len(all_features)} under-construction features")
                        
                    except httpx.HTTPError as e:
                        logger.error(f"HTTP error fetching under-construction plants: {e}")
                        break
                    except Exception as e:
                        logger.error(f"Error fetching under-construction plants: {e}")
                        break
        
        # Parse plants and scrape deadlines
        plants = []
        for feature in all_features:
            plant = self.parse_plant_feature(feature, "under_construction")
            
            # Try to scrape deadline if kdbNr is available
            if plant.get("kdbNr"):
                try:
                    deadline, success = await self.scrape_deadline_from_nve(plant["kdbNr"])
                    plant["deadline"] = deadline
                    plant["deadline_scraped"] = success
                    
                    if not success:
                        logger.warning(f"Could not scrape deadline for plant {plant['name']} (kdbNr: {plant['kdbNr']})")
                except Exception as e:
                    logger.error(f"Error scraping deadline for plant {plant['name']}: {e}")
                    plant["deadline"] = None
                    plant["deadline_scraped"] = False
            else:
                plant["deadline"] = None
                plant["deadline_scraped"] = False
                logger.warning(f"No kdbNr for plant {plant['name']}, cannot scrape deadline")
            
            plants.append(plant)
        
        logger.info(f"Fetched {len(plants)} under-construction plants")
        return plants
    
    async def fetch_all_plants(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Fetch both existing and planned plants
        
        Returns:
            Tuple of (existing_plants, planned_plants)
        """
        logger.info("Fetching hydropower plants from NVE...")
        
        # Fetch layer 0 (existing plants)
        existing_features = await self.fetch_layer(0)
        existing_plants = [
            self.parse_plant_feature(f, "existing") 
            for f in existing_features
        ]
        
        # Fetch layer 8 (planned plants)
        planned_features = await self.fetch_layer(8)
        planned_plants = [
            self.parse_plant_feature(f, "planned") 
            for f in planned_features
        ]
        
        logger.info(f"Fetched {len(existing_plants)} existing and {len(planned_plants)} planned plants")
        
        return existing_plants, planned_plants


# Global client instance
nve_client = NVEClient()

