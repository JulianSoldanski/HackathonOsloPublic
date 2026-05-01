import math
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    radius = 6371.0
    
    return radius * c


def filter_plants_by_distance(
    plants: list,
    center_lat: float,
    center_lon: float,
    radius_km: float
) -> list:
    """
    Filter plants by actual geodesic distance and add distance field
    
    Args:
        plants: List of plant dicts
        center_lat, center_lon: Center point
        radius_km: Search radius in km
    
    Returns:
        Filtered plants with distance_km field added
    """
    filtered = []
    
    for plant in plants:
        coords = plant["coordinates"]
        distance = haversine_distance(
            center_lat, center_lon,
            coords["lat"], coords["lon"]
        )
        
        if distance <= radius_km:
            plant["distance_km"] = round(distance, 2)
            filtered.append(plant)
    
    # Sort by distance
    filtered.sort(key=lambda p: p["distance_km"])
    
    return filtered


def get_power_zone_for_location(lat: float, lon: float) -> str:
    """
    Determine power zone (NO1-NO5) for a location
    
    Rough approximation based on coordinates:
    - NO1: Oslo/Eastern Norway (east of ~10°E, south of ~62°N)
    - NO2: Kristiansand/Southern Norway (south of ~59°N, west of ~8°E)
    - NO3: Trondheim/Central Norway (between ~62°N and ~67°N)
    - NO4: Tromsø/Northern Norway (north of ~67°N)
    - NO5: Bergen/Western Norway (west of ~8°E, between ~59°N and ~62°N)
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Zone ID (NO1-NO5)
    """
    # Northern Norway
    if lat >= 67:
        return "NO4"
    
    # Central Norway
    if lat >= 62:
        return "NO3"
    
    # Western Norway
    if lat >= 59 and lon < 8:
        return "NO5"
    
    # Southern Norway
    if lat < 59:
        return "NO2"
    
    # Eastern Norway (default)
    return "NO1"


def calculate_grid_constraint(
    zone_headroom_mw: float,
    local_capacity_mw: float
) -> Tuple[str, str, str]:
    """
    Calculate grid constraint status based on headroom and local capacity
    
    Args:
        zone_headroom_mw: Available headroom in power zone
        local_capacity_mw: Local installed capacity
    
    Returns:
        Tuple of (status, description, color)
    """
    # More nuanced thresholds for better color distribution
    # Excellent: High headroom AND high local capacity
    if zone_headroom_mw > 300 and local_capacity_mw > 100:
        return (
            "excellent",
            "Excellent grid capacity and abundant local generation",
            "blue"
        )
    # Good: Decent headroom AND decent local capacity (raised threshold)
    elif zone_headroom_mw > 150 and local_capacity_mw > 80:
        return (
            "ok",
            "Good grid capacity and local generation available",
            "green"
        )
    # Limited: Moderate headroom OR moderate local capacity
    elif zone_headroom_mw > 100 or local_capacity_mw > 40:
        return (
            "limited",
            "Moderate grid capacity, connection possible with planning",
            "orange"
        )
    # Challenging: Low headroom AND low local capacity
    elif zone_headroom_mw > 50 or local_capacity_mw > 5:
        return (
            "challenging",
            "Limited grid capacity, significant planning required",
            "yellow"
        )
    # Blocked: Very low headroom and minimal local capacity
    else:
        return (
            "blocked",
            "Insufficient grid capacity or local generation",
            "red"
        )


def find_nearest_hydro_plant(
    lat: float,
    lon: float,
    plants: list
) -> dict:
    """
    Find the nearest hydropower plant to given coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        plants: List of plant dicts
    
    Returns:
        Dictionary with plant ID, name, and distance in km
        or None if no plants available
    """
    if not plants:
        return None
    
    nearest = None
    min_distance = float('inf')
    
    for plant in plants:
        coords = plant["coordinates"]
        distance = haversine_distance(lat, lon, coords["lat"], coords["lon"])
        
        if distance < min_distance:
            min_distance = distance
            nearest = plant
    
    if nearest:
        return {
            "id": nearest["id"],
            "name": nearest["name"],
            "distance_km": round(min_distance, 2)
        }
    
    return None


def find_multiple_hydro_plants(
    lat: float,
    lon: float,
    plants: list,
    required_capacity_mw: float,
    max_distance_km: float = 200.0
) -> list:
    """
    Find multiple hydropower plants to satisfy the required capacity.
    Plants are selected by proximity until the capacity requirement is met.
    
    Args:
        lat: Latitude of data center
        lon: Longitude of data center
        plants: List of available plant dicts
        required_capacity_mw: Required capacity in MW
        max_distance_km: Maximum distance to search (default: 200 km)
    
    Returns:
        List of dicts with plant info and allocated capacity:
        [
            {
                "id": plant_id,
                "name": plant_name,
                "distance_km": distance,
                "allocated_capacity_mw": allocated
            },
            ...
        ]
    """
    if not plants or required_capacity_mw <= 0:
        return []
    
    # Calculate distances and filter by max distance
    plants_with_distance = []
    for plant in plants:
        coords = plant["coordinates"]
        distance = haversine_distance(lat, lon, coords["lat"], coords["lon"])
        
        if distance <= max_distance_km:
            plants_with_distance.append({
                "plant": plant,
                "distance": distance
            })
    
    # Sort by distance (nearest first)
    plants_with_distance.sort(key=lambda p: p["distance"])
    
    # Allocate capacity from nearest plants
    connections = []
    remaining_capacity = required_capacity_mw
    
    for item in plants_with_distance:
        if remaining_capacity <= 0:
            break
        
        plant = item["plant"]
        distance = item["distance"]
        plant_capacity = plant["maksYtelse_MW"]
        
        # Allocate as much as this plant can provide
        allocated = min(plant_capacity, remaining_capacity)
        
        connections.append({
            "hydro_id": plant["id"],
            "hydro_name": plant["name"],
            "distance_km": round(distance, 2),
            "allocated_capacity_mw": round(allocated, 2),
            "plant_total_capacity_mw": round(plant_capacity, 2)
        })
        
        remaining_capacity -= allocated
    
    return connections

