"""Norwegian cities and major towns with coordinates"""

# Major cities and towns in Norway with their coordinates
# This list includes cities and larger towns that data centers might be near
NORWEGIAN_CITIES = [
    # Major cities
    {"name": "Oslo", "lat": 59.911, "lon": 10.757},
    {"name": "Bergen", "lat": 60.391, "lon": 5.324},
    {"name": "Trondheim", "lat": 63.431, "lon": 10.395},
    {"name": "Stavanger", "lat": 58.970, "lon": 5.733},
    {"name": "Tromsø", "lat": 69.649, "lon": 18.956},
    {"name": "Drammen", "lat": 59.744, "lon": 10.204},
    {"name": "Fredrikstad", "lat": 59.213, "lon": 10.936},
    {"name": "Kristiansand", "lat": 58.147, "lon": 7.996},
    {"name": "Sandnes", "lat": 58.852, "lon": 5.736},
    {"name": "Tønsberg", "lat": 59.267, "lon": 10.408},
    
    # Important regional centers
    {"name": "Ålesund", "lat": 62.472, "lon": 6.154},
    {"name": "Sarpsborg", "lat": 59.283, "lon": 11.108},
    {"name": "Skien", "lat": 59.209, "lon": 9.608},
    {"name": "Haugesund", "lat": 59.414, "lon": 5.268},
    {"name": "Sandefjord", "lat": 59.131, "lon": 10.216},
    {"name": "Bodø", "lat": 67.280, "lon": 14.405},
    {"name": "Arendal", "lat": 58.461, "lon": 8.772},
    {"name": "Moss", "lat": 59.436, "lon": 10.657},
    {"name": "Porsgrunn", "lat": 59.140, "lon": 9.656},
    {"name": "Lillehammer", "lat": 61.115, "lon": 10.466},
    
    # Additional towns
    {"name": "Hamar", "lat": 60.795, "lon": 11.068},
    {"name": "Larvik", "lat": 59.052, "lon": 10.035},
    {"name": "Halden", "lat": 59.134, "lon": 11.387},
    {"name": "Askøy", "lat": 60.467, "lon": 5.083},
    {"name": "Molde", "lat": 62.737, "lon": 7.159},
    {"name": "Kongsberg", "lat": 59.669, "lon": 9.651},
    {"name": "Harstad", "lat": 68.798, "lon": 16.541},
    {"name": "Horten", "lat": 59.417, "lon": 10.483},
    {"name": "Gjøvik", "lat": 60.796, "lon": 10.691},
    {"name": "Mo i Rana", "lat": 66.313, "lon": 14.143},
    
    # Smaller but notable towns
    {"name": "Narvik", "lat": 68.438, "lon": 17.427},
    {"name": "Alta", "lat": 69.969, "lon": 23.272},
    {"name": "Kristiansund", "lat": 63.111, "lon": 7.728},
    {"name": "Elverum", "lat": 60.881, "lon": 11.562},
    {"name": "Steinkjer", "lat": 64.015, "lon": 11.495},
    {"name": "Grimstad", "lat": 58.340, "lon": 8.593},
    {"name": "Mandal", "lat": 58.029, "lon": 7.455},
    {"name": "Voss", "lat": 60.629, "lon": 6.419},
    {"name": "Sogndal", "lat": 61.231, "lon": 7.106},
    {"name": "Rjukan", "lat": 59.878, "lon": 8.593},
    
    # Mountain/hydropower regions
    {"name": "Ål", "lat": 60.632, "lon": 8.566},
    {"name": "Geilo", "lat": 60.534, "lon": 8.206},
    {"name": "Odda", "lat": 60.067, "lon": 6.545},
    {"name": "Røros", "lat": 62.575, "lon": 11.381},
    {"name": "Lom", "lat": 61.836, "lon": 8.568},
    {"name": "Notodden", "lat": 59.560, "lon": 9.257},
    {"name": "Hønefoss", "lat": 60.168, "lon": 10.256},
    {"name": "Førde", "lat": 61.452, "lon": 5.857},
    {"name": "Brumunddal", "lat": 60.879, "lon": 10.942},
    {"name": "Levanger", "lat": 63.746, "lon": 11.301},
]


def get_all_cities():
    """Get all Norwegian cities"""
    return NORWEGIAN_CITIES


def find_nearest_city(lat: float, lon: float):
    """
    Find the nearest city to given coordinates using simple Euclidean distance
    (Good enough approximation for finding nearest city name)
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dictionary with city name and distance in km
    """
    from .utils import haversine_distance
    
    nearest = None
    min_distance = float('inf')
    
    for city in NORWEGIAN_CITIES:
        distance = haversine_distance(lat, lon, city["lat"], city["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest = city
    
    return {
        "name": nearest["name"],
        "distance_km": round(min_distance, 2)
    }

