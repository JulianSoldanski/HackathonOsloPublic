import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import re

from .config import settings
from .models import (
    HydropowerPlant, 
    PowerZone, 
    CapacityEstimate, 
    CacheStatus,
    GridConstraint,
    Coordinates,
    PlantAnalysisResult,
    PlantAnalysisSource,
    DataCenter,
    DataCenterCreate,
    HydroConnection
)
from .database import db
from .nve_client import nve_client
from .power_zones import (
    get_zone_by_id, 
    get_all_zones,
    get_all_zones_with_data_center_impact
)
from .utils import (
    filter_plants_by_distance,
    get_power_zone_for_location,
    calculate_grid_constraint,
    find_nearest_hydro_plant,
    find_multiple_hydro_plants
)
from .cities import find_nearest_city
from .plant_analyzer import get_plant_analyzer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API for visualizing hydropower capacity and grid headroom in Norway"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def refresh_cache_task():
    """Background task to refresh plant data cache"""
    try:
        logger.info("Starting cache refresh...")
        
        # Fetch from NVE
        existing_plants, planned_plants = await nve_client.fetch_all_plants()
        under_construction_plants = await nve_client.fetch_under_construction_plants()
        
        # Clear old cache
        db.clear_cache()
        
        # Save to database
        if existing_plants:
            db.save_plants(existing_plants, "existing")
        if planned_plants:
            db.save_plants(planned_plants, "planned")
        if under_construction_plants:
            db.save_plants(under_construction_plants, "under_construction")
        
        logger.info(f"Cache refreshed: {len(existing_plants)} existing, {len(planned_plants)} planned, {len(under_construction_plants)} under construction plants")
        
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize cache on startup if needed"""
    if db.is_cache_stale():
        logger.info("Cache is stale, refreshing...")
        await refresh_cache_task()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Norway Hydropower & Grid API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_plants": db.get_plant_count(),
        "cache_plants_existing": db.get_plant_count("existing"),
        "cache_plants_planned": db.get_plant_count("planned"),
        "cache_plants_under_construction": db.get_plant_count("under_construction"),
        "cache_stale": db.is_cache_stale()
    }


@app.get("/api/cache/status", response_model=CacheStatus)
async def get_cache_status():
    """Get cache status information"""
    last_refresh = db.get_last_refresh()
    plant_count = db.get_plant_count()
    is_stale = db.is_cache_stale()
    
    next_refresh = None
    if last_refresh:
        from datetime import timedelta
        next_refresh = last_refresh + timedelta(days=settings.cache_expiry_days)
    
    return CacheStatus(
        last_refresh=last_refresh,
        plant_count=plant_count,
        is_stale=is_stale,
        next_refresh=next_refresh
    )


@app.post("/api/refresh")
async def refresh_cache(background_tasks: BackgroundTasks):
    """Manually trigger cache refresh"""
    background_tasks.add_task(refresh_cache_task)
    return {
        "message": "Cache refresh started",
        "status": "processing"
    }


@app.get("/api/plants", response_model=List[HydropowerPlant])
async def get_plants(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    radius_km: float = Query(50.0, description="Search radius in kilometers", ge=1, le=500),
    status: str = Query("all", description="Plant status: all, existing, planned, or under_construction")
):
    """
    Get hydropower plants, optionally filtered by location and radius
    
    Args:
        lat: Latitude of center point
        lon: Longitude of center point
        radius_km: Search radius in km (default: 50)
        status: Filter by status (all, existing, planned, under_construction)
    
    Returns:
        List of hydropower plants
    """
    # If no location specified, return all plants (limited)
    if lat is None or lon is None:
        plants = db.get_all_plants(status)[:100]  # Limit to 100 for performance
        return [HydropowerPlant(**plant) for plant in plants]
    
    # Get plants in bounding box
    plants = db.get_plants_in_radius(lat, lon, radius_km, status)
    
    # Filter by exact distance using haversine
    plants = filter_plants_by_distance(plants, lat, lon, radius_km)
    
    return [HydropowerPlant(**plant) for plant in plants]


@app.get("/api/zone/{zone_id}", response_model=PowerZone)
async def get_zone(zone_id: str):
    """
    Get power zone data
    
    Args:
        zone_id: Zone ID (NO1, NO2, NO3, NO4, or NO5)
    
    Returns:
        Power zone information
    """
    try:
        zone = get_zone_by_id(zone_id)
        return zone
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/zones", response_model=dict)
async def get_zones(
    include_data_centers: bool = Query(False, description="Include data center impact on headroom")
):
    """
    Get all power zones
    
    Args:
        include_data_centers: If True, adjust headroom based on data center consumption
    
    Returns:
        Dictionary of power zones
    """
    if include_data_centers:
        data_centers = db.get_all_data_centers()
        return get_all_zones_with_data_center_impact(data_centers)
    return get_all_zones()


@app.get("/api/estimate", response_model=CapacityEstimate)
async def get_capacity_estimate(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(50.0, description="Search radius in kilometers", ge=1, le=200)
):
    """
    Get combined capacity and headroom estimate for a location
    
    This endpoint combines:
    1. Nearby hydropower capacity
    2. Power zone data
    3. Grid constraint assessment
    
    Args:
        lat: Latitude of location
        lon: Longitude of location
        radius_km: Search radius in km
    
    Returns:
        Comprehensive capacity estimate
    """
    # Get nearby plants
    plants = db.get_plants_in_radius(lat, lon, radius_km, "existing")
    plants = filter_plants_by_distance(plants, lat, lon, radius_km)
    
    # Calculate total capacity
    total_capacity = sum(p["maksYtelse_MW"] for p in plants)
    
    # Get power zone
    zone_id = get_power_zone_for_location(lat, lon)
    try:
        zone = get_zone_by_id(zone_id)
    except ValueError:
        zone = get_zone_by_id("NO1")  # Default fallback
    
    # Calculate grid constraint
    status, description, color = calculate_grid_constraint(
        zone.headroom_MW,
        total_capacity
    )
    
    grid_constraint = GridConstraint(
        status=status,
        description=description,
        color=color
    )
    
    # Generate recommendation
    if status == "ok":
        recommendation = f"✅ Excellent location with {total_capacity:.1f} MW local capacity and {zone.headroom_MW:.1f} MW zone headroom. Ideal for large data center deployment."
    elif status == "limited":
        recommendation = f"⚠️ Moderate location with {total_capacity:.1f} MW local capacity. Suitable for small-to-medium data centers. Grid reinforcement may be needed for large deployments."
    else:
        recommendation = f"❌ Limited location with only {total_capacity:.1f} MW local capacity. Consider alternative locations with better grid capacity."
    
    return CapacityEstimate(
        location=Coordinates(lat=lat, lon=lon),
        radius_km=radius_km,
        nearby_plants_count=len(plants),
        total_nearby_capacity_MW=round(total_capacity, 2),
        plants=[HydropowerPlant(**p) for p in plants[:20]],  # Limit to 20 for response size
        power_zone=zone,
        grid_constraint=grid_constraint,
        recommendation=recommendation
    )


@app.get("/api/under-construction", response_model=List[HydropowerPlant])
async def get_under_construction_plants(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    radius_km: float = Query(50.0, description="Search radius in kilometers", ge=1, le=500),
    timeline_months: Optional[int] = Query(None, description="Filter by timeline in months", ge=1, le=240),
):
    """
    Get hydropower plants under construction with deadline information
    
    Args:
        lat: Latitude of center point (optional)
        lon: Longitude of center point (optional)
        radius_km: Search radius in km (default: 50)
        timeline_months: Filter plants completing within this many months (optional)
    
    Returns:
        List of under-construction hydropower plants with deadline info
    """
    # If no location specified, return all under-construction plants (limited)
    if lat is None or lon is None:
        plants = db.get_all_plants("under_construction")[:100]
    else:
        # Get plants in bounding box
        plants = db.get_plants_in_radius(lat, lon, radius_km, "under_construction")
        # Filter by exact distance using haversine
        plants = filter_plants_by_distance(plants, lat, lon, radius_km)
    
    # Filter by timeline if specified
    if timeline_months is not None:
        now = datetime.now()
        cutoff_date = datetime(now.year, now.month, now.day) + timedelta(days=timeline_months * 30)
        
        filtered_plants = []
        for plant in plants:
            deadline_str = plant.get('deadline')
            if not deadline_str:
                # Include plants without deadline
                filtered_plants.append(plant)
                continue
            
            # Parse deadline (format: "Q# YYYY")
            match = re.search(r'Q(\d)\s+(\d{4})', deadline_str)
            if match:
                quarter = int(match.group(1))
                year = int(match.group(2))
                # Estimate end of quarter date
                month = quarter * 3  # End month of quarter
                deadline_date = datetime(year, month, 1)
                
                if deadline_date <= cutoff_date:
                    filtered_plants.append(plant)
            else:
                # If can't parse, include it
                filtered_plants.append(plant)
        
        plants = filtered_plants
    
    return [HydropowerPlant(**plant) for plant in plants]


@app.post("/api/refresh-under-construction")
async def refresh_under_construction(background_tasks: BackgroundTasks):
    """Manually trigger refresh of under-construction plants"""
    async def refresh_task():
        try:
            logger.info("Refreshing under-construction plants...")
            under_construction_plants = await nve_client.fetch_under_construction_plants()
            
            # Remove old under-construction plants and add new ones
            # This is a simple approach - you might want to update database.py for better handling
            if under_construction_plants:
                db.save_plants(under_construction_plants, "under_construction")
            
            logger.info(f"Refreshed {len(under_construction_plants)} under-construction plants")
        except Exception as e:
            logger.error(f"Error refreshing under-construction plants: {e}")
    
    background_tasks.add_task(refresh_task)
    return {
        "message": "Under-construction plants refresh started",
        "status": "processing"
    }


@app.post("/api/normalize-deadlines")
async def normalize_deadlines():
    """
    Normalize all under-construction plant deadlines in the database
    Updates past deadlines to future dates (1-2 years from now)
    """
    try:
        logger.info("Starting deadline normalization...")
        
        # Get all under-construction plants
        plants = db.get_all_plants("under_construction")
        
        if not plants:
            return {
                "message": "No under-construction plants found in database",
                "updated_count": 0,
                "total_count": 0
            }
        
        # Normalize deadlines
        updated_count = 0
        for plant in plants:
            old_deadline = plant.get('deadline')
            new_deadline = db.normalize_deadline(old_deadline)
            
            if old_deadline != new_deadline:
                plant['deadline'] = new_deadline
                updated_count += 1
                logger.info(f"Updated {plant['name']}: {old_deadline} -> {new_deadline}")
        
        # Save updated plants back to database
        if updated_count > 0:
            db.save_plants(plants, "under_construction")
            logger.info(f"Normalized {updated_count} deadlines")
        
        return {
            "message": "Deadline normalization completed",
            "updated_count": updated_count,
            "total_count": len(plants),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error normalizing deadlines: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error normalizing deadlines: {str(e)}"
        )


@app.get("/api/recommended-locations")
async def get_recommended_locations(
    min_capacity_mw: float = Query(50.0, description="Minimum local capacity in MW"),
    limit: int = Query(10, description="Maximum number of locations to return", ge=1, le=50)
):
    """
    Get recommended data center locations based on capacity and grid constraints
    
    This scans Norway for high-capacity areas and returns the best locations.
    
    Args:
        min_capacity_mw: Minimum local capacity threshold
        limit: Maximum number of results
    
    Returns:
        List of recommended locations with capacity estimates
    """
    # Get all plants
    all_plants = db.get_all_plants("existing")
    
    # Pre-defined grid of Norwegian locations to sample
    # Format: (name, lat, lon)
    sample_locations = [
        ("Bergen Area", 60.391, 5.324),
        ("Oslo Area", 59.911, 10.757),
        ("Stavanger Area", 58.970, 5.733),
        ("Trondheim Area", 63.431, 10.395),
        ("Tromsø Area", 69.649, 18.956),
        ("Kristiansand Area", 58.147, 7.996),
        ("Drammen Area", 59.744, 10.204),
        ("Ålesund Area", 62.472, 6.154),
        ("Bodø Area", 67.280, 14.405),
        ("Ål / Hallingdal", 60.632, 8.566),
        ("Rjukan", 59.878, 8.593),
        ("Voss", 60.629, 6.419),
        ("Sogndal", 61.231, 7.106),
        ("Narvik Area", 68.438, 17.427),
        ("Lillehammer Area", 61.115, 10.466),
    ]
    
    recommendations = []
    
    for name, lat, lon in sample_locations:
        # Get plants within 50km
        plants = db.get_plants_in_radius(lat, lon, 50.0, "existing")
        plants = filter_plants_by_distance(plants, lat, lon, 50.0)
        
        total_capacity = sum(p["maksYtelse_MW"] for p in plants)
        
        # Only include if meets minimum capacity
        if total_capacity >= min_capacity_mw:
            zone_id = get_power_zone_for_location(lat, lon)
            try:
                zone = get_zone_by_id(zone_id)
            except ValueError:
                zone = get_zone_by_id("NO1")
            
            status, description, color = calculate_grid_constraint(
                zone.headroom_MW,
                total_capacity
            )
            
            recommendations.append({
                "name": name,
                "location": {"lat": lat, "lon": lon},
                "total_capacity_mw": round(total_capacity, 2),
                "nearby_plants": len(plants),
                "power_zone": zone_id,
                "zone_headroom_mw": zone.headroom_MW,
                "grid_status": status,
                "status_color": color,
                "suitability_score": round(total_capacity * 0.5 + zone.headroom_MW * 0.5, 2)
            })
    
    # Sort by suitability score (descending)
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    return recommendations[:limit]


@app.post("/api/analyze-plant", response_model=PlantAnalysisResult)
async def analyze_plant(
    plant_name: str = Query(..., description="Name of the power plant to analyze"),
):
    """
    Analyze a power plant using Google Search and Gemini AI to find deadline information
    
    This endpoint:
    1. Searches Google for information about the plant
    2. Fetches content from the top 3 results
    3. Uses Gemini AI to analyze and summarize deadline information
    
    Args:
        plant_name: Name of the power plant
    
    Returns:
        Analysis result with summary and sources
    """
    try:
        google_api_key = settings.google_search_api_key
        gemini_api_key = settings.gemini_api_key
        engine_id = settings.google_search_engine_id
        if not google_api_key or not gemini_api_key or not engine_id:
            raise HTTPException(
                status_code=503,
                detail=(
                    "AI plant analysis is not configured. Set GOOGLE_SEARCH_API_KEY, "
                    "GEMINI_API_KEY, and GOOGLE_SEARCH_ENGINE_ID in backend/.env"
                ),
            )

        analyzer = get_plant_analyzer(google_api_key, gemini_api_key, engine_id)
        
        # Perform analysis
        result = await analyzer.analyze_plant(plant_name)
        
        # Convert to response model
        sources = [PlantAnalysisSource(**source) for source in result["sources"]]
        
        return PlantAnalysisResult(
            plant_name=plant_name,
            summary=result["summary"],
            sources=sources,
            links=result["links"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_plant endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing plant: {str(e)}"
        )


@app.post("/api/data-centers", response_model=DataCenter)
async def create_data_center(data: DataCenterCreate):
    """
    Create a new data center
    
    This endpoint automatically:
    1. Finds multiple hydropower plants to satisfy capacity requirements
    2. Allocates capacity from nearest plants first
    3. Finds the nearest city
    4. Determines the power zone
    5. Calculates distances
    
    Args:
        data: Data center creation data (name, lat, lon, capacity_mw)
    
    Returns:
        Created data center with all calculated fields and multiple connections
    """
    import uuid
    
    try:
        # Get all existing plants
        all_plants = db.get_all_plants("existing")
        
        if not all_plants:
            raise HTTPException(
                status_code=503,
                detail="No hydropower plants available. Please refresh the cache first."
            )
        
        # Find multiple hydro plants to satisfy capacity
        hydro_connections = find_multiple_hydro_plants(
            lat=data.lat,
            lon=data.lon,
            plants=all_plants,
            required_capacity_mw=data.capacity_mw,
            max_distance_km=200.0
        )
        
        if not hydro_connections:
            raise HTTPException(
                status_code=404,
                detail="Could not find hydropower plants to satisfy capacity requirements"
            )
        
        # Get nearest plant for legacy fields
        nearest_hydro = hydro_connections[0]  # First one is always nearest
        
        # Find nearest city
        nearest_city_data = find_nearest_city(data.lat, data.lon)
        
        # Get power zone
        zone_id = get_power_zone_for_location(data.lat, data.lon)
        
        # Create data center object
        dc_id = str(uuid.uuid4())
        data_center = {
            'id': dc_id,
            'name': data.name,
            'coordinates': {'lat': data.lat, 'lon': data.lon},
            'capacity_mw': data.capacity_mw,
            'hydro_connections': hydro_connections,
            # Legacy fields for backward compatibility
            'nearest_hydro_id': nearest_hydro['hydro_id'],
            'nearest_hydro_name': nearest_hydro['hydro_name'],
            'distance_to_hydro_km': nearest_hydro['distance_km'],
            'nearest_city': nearest_city_data['name'],
            'distance_to_city_km': nearest_city_data['distance_km'],
            'power_zone_id': zone_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to database
        db.add_data_center(data_center)
        
        total_allocated = sum(conn['allocated_capacity_mw'] for conn in hydro_connections)
        logger.info(
            f"Created data center: {data.name} at ({data.lat}, {data.lon}) "
            f"with {len(hydro_connections)} connections, "
            f"total allocated: {total_allocated:.2f} MW of {data.capacity_mw} MW required"
        )
        
        return DataCenter(**data_center)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating data center: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating data center: {str(e)}"
        )


@app.get("/api/data-centers", response_model=List[DataCenter])
async def get_data_centers():
    """
    Get all data centers
    
    Returns:
        List of all data centers
    """
    data_centers = db.get_all_data_centers()
    return [DataCenter(**dc) for dc in data_centers]


@app.delete("/api/data-centers/{dc_id}")
async def delete_data_center(dc_id: str):
    """
    Delete a data center
    
    Args:
        dc_id: Data center ID
    
    Returns:
        Success message
    """
    success = db.delete_data_center(dc_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Data center {dc_id} not found"
        )
    
    logger.info(f"Deleted data center: {dc_id}")
    
    return {
        "message": "Data center deleted successfully",
        "id": dc_id
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
