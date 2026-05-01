# Multi-Connection Data Center Implementation

## Overview
This implementation allows data centers to connect to multiple hydropower plants when their energy consumption exceeds what a single nearby plant can provide.

## Problem Statement
Previously, when a data center was added via right-click, it would only connect to the nearest hydropower plant with a single line, regardless of whether that plant could actually satisfy the data center's power requirements. For example, a 70MW data center would still only connect to a nearby 5MW plant.

## Solution
The system now:
1. Calculates the data center's power requirements
2. Finds multiple nearby hydropower plants (within 200km)
3. Allocates capacity from the nearest plants first
4. Creates connections to as many plants as needed to meet the demand
5. Displays multiple lines on the map, with line thickness proportional to allocated capacity

## Implementation Details

### Backend Changes

#### 1. Models (`backend/app/models.py`)
- Added `HydroConnection` model to represent individual connections:
  - `hydro_id`: ID of the connected plant
  - `hydro_name`: Name of the connected plant
  - `distance_km`: Distance to the plant
  - `allocated_capacity_mw`: How much capacity is allocated from this plant

- Updated `DataCenter` model:
  - Added `hydro_connections: List[HydroConnection]` field
  - Kept legacy fields for backward compatibility

#### 2. Utilities (`backend/app/utils.py`)
- Added `find_multiple_hydro_plants()` function:
  - Takes: location (lat, lon), required capacity, max search distance
  - Returns: List of connections with allocated capacities
  - Algorithm:
    1. Finds all plants within max_distance_km (default 200km)
    2. Sorts by distance (nearest first)
    3. Allocates capacity from each plant until requirement is met
    4. If a plant has 5MW and 10MW is still needed, it allocates all 5MW and moves to next plant

#### 3. API Endpoint (`backend/app/main.py`)
- Updated `POST /api/data-centers` endpoint:
  - Now calls `find_multiple_hydro_plants()` instead of `find_nearest_hydro_plant()`
  - Stores multiple connections in the database
  - Logs total allocated capacity vs required capacity
  - Maintains backward compatibility with legacy fields

### Frontend Changes

#### 1. Types (`frontend/src/types.ts`)
- Added `HydroConnection` interface matching backend model
- Updated `DataCenter` interface to include `hydro_connections` array
- Kept legacy fields for backward compatibility

#### 2. Map Component (`frontend/src/components/Map.tsx`)
- Updated `connectionLinesGeoJSON` useMemo:
  - Iterates through each data center's `hydro_connections` array
  - Creates a separate line for each connection
  - Includes allocated capacity in line properties
  - Falls back to legacy single connection if `hydro_connections` is not available

- Enhanced line rendering:
  - Line width varies based on allocated capacity:
    - 0 MW → 2px
    - 10 MW → 3px
    - 50 MW → 5px
    - 100+ MW → 7px
  - Purple color (#8b5cf6) for all connections
  - 80% opacity for subtle appearance

- Updated Data Center Popup:
  - Shows count of connected plants
  - Lists all connections with allocated capacity and distance
  - Scrollable list if many connections
  - Falls back to legacy display if no connections array

## Example Scenarios

### Scenario 1: Small Data Center (5MW)
- Location: Near a 10MW hydroplant
- Result: Single connection to the 10MW plant
- Display: One purple line (2-3px width)

### Scenario 2: Medium Data Center (25MW)
- Location: Near a 10MW plant and a 20MW plant
- Result: 
  - Connection 1: 10MW from nearest plant (10km away)
  - Connection 2: 15MW from second plant (25km away)
- Display: Two purple lines of different thickness

### Scenario 3: Large Data Center (70MW)
- Location: Near multiple small plants (5MW, 8MW, 12MW, 20MW, 30MW)
- Result:
  - Connection 1: 5MW from plant 1
  - Connection 2: 8MW from plant 2
  - Connection 3: 12MW from plant 3
  - Connection 4: 20MW from plant 4
  - Connection 5: 25MW from plant 5 (only uses 25 of its 30MW)
- Display: Five purple lines radiating from the data center, varying in thickness

## Visual Enhancements

The implementation includes several visual features:
1. **Multiple Lines**: Each connection is drawn as a separate line
2. **Variable Thickness**: Thicker lines indicate higher capacity allocation
3. **Color Coding**: Purple (#8b5cf6) consistently identifies data center connections
4. **Interactive Popup**: Click a data center to see all connections with details
5. **Legend**: Shows data center icon and connection line style

## Database Compatibility

The implementation maintains backward compatibility:
- New data centers store both `hydro_connections` array and legacy fields
- Old data centers without `hydro_connections` will still display correctly
- Frontend gracefully handles both data formats

## Configuration

The multi-connection algorithm can be tuned by modifying:
- `max_distance_km` in `find_multiple_hydro_plants()` (default: 200km)
- Line width interpolation values in Map component
- Line color and opacity in Map component

## Testing

To test the implementation:
1. Start the backend server
2. Start the frontend application
3. Right-click on the map to add a data center
4. Set a high capacity (e.g., 70MW)
5. Observe multiple purple lines connecting to nearby hydroplants
6. Click the data center marker to see all connections in the popup
7. Notice that thicker lines represent higher capacity allocations

## Future Enhancements

Potential improvements:
- Add capacity utilization visualization for hydroplants
- Show warning if total allocated capacity < required capacity
- Allow manual connection selection/editing
- Display aggregate capacity by power zone
- Add connection cost/distance optimization
- Consider both existing and under-construction plants for connections

