from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Coordinates(BaseModel):
    """Geographic coordinates"""
    lat: float
    lon: float


class HydropowerPlant(BaseModel):
    """Hydropower plant data model"""
    id: str
    name: str
    maksYtelse_MW: float = Field(..., description="Maximum capacity in MW")
    type: str = Field(..., description="Plant type: Mikro, Mini, Stor")
    year: Optional[int] = Field(None, description="Year commissioned")
    kommune: Optional[str] = Field(None, description="Municipality")
    fylke: Optional[str] = Field(None, description="County")
    owner: Optional[str] = Field(None, description="Owner/operator")
    coordinates: Coordinates
    status: str = Field(default="existing", description="Status: existing, planned, or under_construction")
    distance_km: Optional[float] = Field(None, description="Distance from query point")
    kdbNr: Optional[int] = Field(None, description="KDB number for under-construction plants")
    deadline: Optional[str] = Field(None, description="Construction deadline for under-construction plants")
    deadline_scraped: Optional[bool] = Field(None, description="Whether deadline was successfully scraped")


class PowerZone(BaseModel):
    """Norwegian power zone data (NO1-NO5)"""
    id: str = Field(..., description="Zone ID: NO1, NO2, NO3, NO4, or NO5")
    name: str
    total_generation_MW: float
    consumption_MW: float
    export_MW: float
    headroom_MW: float = Field(..., description="Available capacity (generation - consumption - export)")
    last_updated: datetime


class GridConstraint(BaseModel):
    """Grid constraint status"""
    status: str = Field(..., description="Status: ok, limited, or blocked")
    description: str
    color: str = Field(..., description="Color code: green, orange, or red")


class CapacityEstimate(BaseModel):
    """Combined capacity and headroom estimate for a location"""
    location: Coordinates
    radius_km: float
    nearby_plants_count: int
    total_nearby_capacity_MW: float
    plants: List[HydropowerPlant]
    power_zone: PowerZone
    grid_constraint: GridConstraint
    recommendation: str


class PlantsQueryParams(BaseModel):
    """Query parameters for plants endpoint"""
    lat: float
    lon: float
    radius_km: float = 50.0
    plant_type: Optional[str] = None
    status: str = "all"  # all, existing, planned


class CacheStatus(BaseModel):
    """Cache status information"""
    last_refresh: Optional[datetime]
    plant_count: int
    is_stale: bool
    next_refresh: Optional[datetime]


class PlantAnalysisSource(BaseModel):
    """Source information for plant analysis"""
    title: str
    url: str
    snippet: str


class PlantAnalysisResult(BaseModel):
    """Result of plant analysis with LLM"""
    plant_name: str
    summary: str = Field(..., description="50-100 word summary from LLM")
    sources: List[PlantAnalysisSource]
    links: List[str]


class HydroConnection(BaseModel):
    """Connection between data center and hydropower plant"""
    hydro_id: str
    hydro_name: str
    distance_km: float
    allocated_capacity_mw: float = Field(..., description="How much capacity is allocated from this plant")


class DataCenter(BaseModel):
    """Data center model"""
    id: str
    name: str
    coordinates: Coordinates
    capacity_mw: float = Field(..., description="Estimated capacity/consumption in MW")
    hydro_connections: List[HydroConnection] = Field(..., description="List of connected hydropower plants")
    # Keep legacy fields for backward compatibility
    nearest_hydro_id: str = Field(..., description="ID of nearest hydropower plant (legacy)")
    nearest_hydro_name: str = Field(..., description="Name of nearest hydropower plant (legacy)")
    distance_to_hydro_km: float = Field(..., description="Distance to nearest hydro (legacy)")
    nearest_city: str
    distance_to_city_km: float
    power_zone_id: str
    created_at: datetime


class DataCenterCreate(BaseModel):
    """Model for creating a data center"""
    name: str
    lat: float
    lon: float
    capacity_mw: float = Field(..., ge=1, le=1000, description="Estimated capacity in MW")

