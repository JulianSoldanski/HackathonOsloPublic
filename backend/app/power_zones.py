from datetime import datetime
from .models import PowerZone


# Mock power zone data - in production, this would come from Statnett API
# Values are approximations for demonstration with more realistic variation
POWER_ZONES = {
    "NO1": PowerZone(
        id="NO1",
        name="Oslo / Øst-Norge",
        total_generation_MW=8500,
        consumption_MW=7800,
        export_MW=400,
        headroom_MW=300,  # Good headroom
        last_updated=datetime.now()
    ),
    "NO2": PowerZone(
        id="NO2",
        name="Kristiansand / Sør-Norge",
        total_generation_MW=4200,
        consumption_MW=4000,  # Higher consumption
        export_MW=100,        # Lower export
        headroom_MW=100,      # Limited headroom
        last_updated=datetime.now()
    ),
    "NO3": PowerZone(
        id="NO3",
        name="Trondheim / Midt-Norge",
        total_generation_MW=6800,
        consumption_MW=5200,
        export_MW=1200,
        headroom_MW=400,      # Excellent headroom
        last_updated=datetime.now()
    ),
    "NO4": PowerZone(
        id="NO4",
        name="Tromsø / Nord-Norge",
        total_generation_MW=3200,
        consumption_MW=3000,  # Higher consumption
        export_MW=100,        # Lower export
        headroom_MW=100,      # Limited headroom
        last_updated=datetime.now()
    ),
    "NO5": PowerZone(
        id="NO5",
        name="Bergen / Vest-Norge",
        total_generation_MW=9500,
        consumption_MW=7200,
        export_MW=1800,
        headroom_MW=500,      # Excellent headroom
        last_updated=datetime.now()
    )
}


def get_zone_by_id(zone_id: str) -> PowerZone:
    """Get power zone by ID"""
    zone = POWER_ZONES.get(zone_id.upper())
    if not zone:
        raise ValueError(f"Invalid zone ID: {zone_id}")
    return zone


def get_all_zones() -> dict:
    """Get all power zones"""
    return POWER_ZONES


def get_zone_with_data_center_impact(zone_id: str, data_centers: list) -> PowerZone:
    """
    Get power zone with adjusted headroom based on data center consumption
    
    Args:
        zone_id: Zone ID (NO1-NO5)
        data_centers: List of data centers
    
    Returns:
        PowerZone with adjusted headroom
    """
    zone = get_zone_by_id(zone_id)
    
    # Calculate total data center consumption in this zone
    dc_consumption = sum(
        dc.get('capacity_mw', 0)
        for dc in data_centers
        if dc.get('power_zone_id') == zone_id
    )
    
    # Adjust headroom
    adjusted_headroom = zone.headroom_MW - dc_consumption
    
    # Create new zone with adjusted values
    return PowerZone(
        id=zone.id,
        name=zone.name,
        total_generation_MW=zone.total_generation_MW,
        consumption_MW=zone.consumption_MW + dc_consumption,
        export_MW=zone.export_MW,
        headroom_MW=max(0, adjusted_headroom),  # Don't go negative
        last_updated=datetime.now()
    )


def get_all_zones_with_data_center_impact(data_centers: list) -> dict:
    """
    Get all power zones with adjusted headroom based on data center consumption
    
    Args:
        data_centers: List of data centers
    
    Returns:
        Dictionary of zones with adjusted headroom
    """
    zones = {}
    for zone_id in POWER_ZONES.keys():
        zones[zone_id] = get_zone_with_data_center_impact(zone_id, data_centers)
    return zones

