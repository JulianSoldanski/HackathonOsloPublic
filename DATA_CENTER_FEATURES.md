# Data Center Features Documentation

## Overview

This document describes the new data center planning features added to the Norway Hydropower Visualizer. These features allow users to place data centers on the map, automatically connect them to the nearest hydropower plants, and visualize the impact on power zone capacity.

---

## ✨ New Features

### 1. Right-Click to Add Data Centers

**How to use:**
- Right-click anywhere on the map
- A modal will appear with the coordinates pre-filled
- Enter a name for the data center (e.g., "Oslo DC-1")
- Specify the estimated capacity in MW (1-1000 MW)
- Click "Create Data Center"

**What happens automatically:**
- System finds the nearest hydropower plant
- Calculates distance to the nearest hydro plant
- Identifies the nearest Norwegian city
- Determines the power zone (NO1-NO5)
- Creates a visual connection line on the map

### 2. Data Center Markers

**Visual Representation:**
- Purple square markers with server icon
- Located at the exact coordinates where you right-clicked
- Hover to see basic info (name, capacity)
- Click for detailed information popup

**Popup Information:**
- Data center name and capacity
- Connected hydropower plant name
- Distance to hydro plant
- Nearest city and distance
- Power zone assignment
- Delete button

### 3. Connection Lines

**Visual Features:**
- Purple dashed lines connecting data centers to their nearest hydro plants
- Automatically drawn when data center is created
- Shows the power supply relationship
- Updates when data centers are added or removed

### 4. Power Zone Capacity Bubbles

**Location:** Top-right corner of the map

**What they show:**
- All 5 Norwegian power zones (NO1-NO5)
- Real-time available capacity in MW
- Color-coded status indicators:
  - 🟢 Green: Excellent (>300 MW)
  - 🔵 Blue: Good (150-300 MW)
  - 🟡 Yellow: Moderate (100-150 MW)
  - 🟠 Orange: Limited (50-100 MW)
  - 🔴 Red: Critical (<50 MW)

**Dynamic Updates:**
- Capacity automatically reduces when data centers are added
- Updates in real-time as you add/remove data centers
- Shows impact of data center consumption on zone headroom

**Detailed Stats:**
- Total generation capacity
- Current consumption
- Export volumes
- Available headroom (after data center consumption)

### 5. Interactive Legend

**Updates dynamically:**
- Shows data center icon when data centers exist
- Displays connection line indicator
- Includes "Right-click map to add" hint
- Maintains existing hydropower plant legend

---

## 🔧 Backend Implementation

### New API Endpoints

#### `POST /api/data-centers`
Create a new data center.

**Request Body:**
```json
{
  "name": "Oslo DC-1",
  "lat": 59.911,
  "lon": 10.757,
  "capacity_mw": 50.0
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Oslo DC-1",
  "coordinates": {"lat": 59.911, "lon": 10.757},
  "capacity_mw": 50.0,
  "nearest_hydro_id": "plant_id",
  "nearest_hydro_name": "Aura kraftverk",
  "distance_to_hydro_km": 12.5,
  "nearest_city": "Oslo",
  "distance_to_city_km": 2.3,
  "power_zone_id": "NO1",
  "created_at": "2025-10-12T10:30:00"
}
```

#### `GET /api/data-centers`
Get all data centers.

#### `DELETE /api/data-centers/{id}`
Delete a data center by ID.

#### `GET /api/zones?include_data_centers=true`
Get power zones with adjusted headroom based on data center consumption.

### New Database Table

**`data_centers` table:**
- `id`: Unique identifier
- `name`: Data center name
- `lat`, `lon`: Geographic coordinates
- `capacity_mw`: Power consumption in MW
- `nearest_hydro_id`: ID of nearest hydro plant
- `nearest_hydro_name`: Name of nearest hydro plant
- `distance_to_hydro_km`: Distance to hydro plant
- `nearest_city`: Name of nearest city
- `distance_to_city_km`: Distance to city
- `power_zone_id`: Power zone (NO1-NO5)
- `created_at`: Creation timestamp

### Norwegian Cities Database

**New file:** `backend/app/cities.py`

Contains coordinates for 50+ Norwegian cities and towns, including:
- Major cities (Oslo, Bergen, Trondheim, Stavanger, Tromsø)
- Regional centers (Ålesund, Bodø, Kristiansand)
- Smaller towns (Rjukan, Voss, Sogndal)
- Mountain/hydropower regions (Ål, Geilo, Odda)

**Function:** `find_nearest_city(lat, lon)`
- Uses Haversine distance calculation
- Returns nearest city name and distance in km

### Utility Functions

**`find_nearest_hydro_plant(lat, lon, plants)`**
- Searches all existing plants
- Finds closest plant using Haversine distance
- Returns plant ID, name, and distance

**`get_zone_with_data_center_impact(zone_id, data_centers)`**
- Calculates total data center consumption in zone
- Adjusts zone headroom accordingly
- Returns updated PowerZone object

---

## 🎨 Frontend Implementation

### New Components

#### `AddDataCenterModal.tsx`
- Modal dialog for creating data centers
- Shows selected coordinates
- Form validation (name required, capacity 1-1000 MW)
- Error handling and loading states
- Dark mode support

#### `ZoneBubbles.tsx`
- Displays all power zones in cards
- Color-coded capacity indicators
- Progress bars for available capacity
- Detailed statistics (generation, consumption, export)
- Auto-refreshes when data centers change
- Status legend included

### Updated Components

#### `Map.tsx`
**New features:**
- Right-click handler (`onContextMenu`)
- Data center markers (purple squares with server icon)
- Connection lines (purple dashed lines)
- Data center popup with details and delete button
- Updated legend with data center indicators

#### `App.tsx`
**State management:**
- `dataCenters` state array
- `zoneRefreshTrigger` counter for force-refreshing zones
- Auto-loads data centers on startup
- Refresh handlers for add/delete operations

### State Flow

```
1. User right-clicks map
   ↓
2. Coordinates captured, modal opens
   ↓
3. User enters name and capacity
   ↓
4. POST /api/data-centers
   ↓
5. Backend calculates nearest hydro and city
   ↓
6. Data center saved to database
   ↓
7. Frontend refreshes data center list
   ↓
8. Map updates: marker appears, line drawn
   ↓
9. Zone bubbles refresh with new capacity
```

---

## 📊 Use Cases

### Scenario 1: Planning a New Data Center
1. Search for a location (e.g., Bergen)
2. View nearby hydropower capacity
3. Check power zone headroom
4. Right-click to place potential data center
5. See immediate impact on zone capacity
6. Try multiple locations to compare

### Scenario 2: Capacity Planning
1. Add multiple data centers to a region
2. Watch zone capacity decrease in real-time
3. Identify zones approaching capacity limits
4. Plan distribution across multiple zones

### Scenario 3: Site Analysis
1. Place data center at desired location
2. View automatically calculated information:
   - Which hydro plant will supply power
   - How far is the nearest grid connection
   - Which city is closest for logistics
   - What power zone governs the location
3. Use this info for feasibility assessment

---

## 🎯 Key Benefits

1. **Automatic Calculations:** No manual research needed for nearest hydro plant or city
2. **Visual Feedback:** See power connections and capacity impact immediately
3. **Real-Time Updates:** Zone capacity updates as you add data centers
4. **Easy Experimentation:** Try different locations, delete and recreate
5. **Informed Decisions:** All relevant data in one place

---

## 🔍 Technical Details

### Distance Calculations
- Uses Haversine formula for accurate geodesic distances
- Accounts for Earth's curvature
- Provides km precision to 2 decimal places

### Power Zone Mapping
Based on approximate geographic boundaries:
- **NO1** (Oslo): Eastern Norway, east of 10°E, south of 62°N
- **NO2** (Kristiansand): Southern Norway, south of 59°N, west of 8°E
- **NO3** (Trondheim): Central Norway, between 62°N and 67°N
- **NO4** (Tromsø): Northern Norway, north of 67°N
- **NO5** (Bergen): Western Norway, west of 8°E, between 59°N and 62°N

### Capacity Impact Calculation
```
Adjusted Headroom = Original Zone Headroom - Sum(Data Center Capacities in Zone)
```

Example:
- NO5 original headroom: 500 MW
- Data centers in NO5: 50 MW + 30 MW + 20 MW = 100 MW
- Adjusted headroom: 500 - 100 = 400 MW

---

## 🚀 Getting Started

### Prerequisites
All features work out-of-the-box with the existing setup. No additional configuration needed.

### Quick Test
1. Start the application: `docker-compose up` or `./start.sh`
2. Wait for the map to load
3. Right-click anywhere on the map
4. Fill in the form and create a data center
5. Watch the zone bubbles update

### Example Locations to Try
- **Oslo area:** 59.911, 10.757 (high density, NO1)
- **Bergen area:** 60.391, 5.324 (coastal, NO5)
- **Trondheim area:** 63.431, 10.395 (central, NO3)
- **Rjukan:** 59.878, 8.593 (hydropower region, NO2)

---

## 🐛 Troubleshooting

### Data center not appearing
- Check browser console for errors
- Ensure backend is running on port 8000
- Try refreshing the page

### Connection lines not showing
- Verify that the nearest hydro plant is visible on the map
- Check that you're in "Show All Plants" or "Existing Plants Only" mode
- Zoom out to see the connection if plants are far apart

### Zone capacity not updating
- The zone bubbles refresh automatically when data centers are added/deleted
- If stuck, try deleting and re-adding the data center
- Check that `include_data_centers=true` is being passed to zones API

### Cannot right-click
- Make sure you're clicking on the map itself, not on markers or UI elements
- Some browsers may intercept right-clicks - try a different browser
- Check that the map has fully loaded

---

## 📈 Future Enhancements

Potential additions for future versions:

1. **Edit Data Centers:** Modify capacity without deleting
2. **Data Center Types:** Different categories (edge, hyperscale, colocation)
3. **Cost Analysis:** Estimate connection costs based on distance
4. **Multiple Hydro Connections:** Connect to 2+ plants for redundancy
5. **Power Lines:** Show actual grid infrastructure
6. **Historical Tracking:** Track capacity changes over time
7. **Export Features:** Generate PDF reports of data center plans
8. **Collaboration:** Share data center plans with team members
9. **Optimization:** AI-powered optimal placement suggestions
10. **Import/Export:** Save and load data center configurations

---

## 📝 Summary

The new data center features provide a complete solution for planning data center locations in Norway with automatic power supply analysis. By combining real-time capacity visualization, automatic calculations, and interactive map features, users can make informed decisions about data center placement while understanding the impact on the power grid.

**Key Innovation:** Right-click simplicity meets sophisticated backend automation - no forms to fill out beforehand, just point and click where you want to evaluate a location, and the system does the rest.

---

## 🎉 Enjoy Planning Your Data Centers!

Start exploring the map, try different locations, and see how data centers impact the power grid in real-time. The system is designed to make complex infrastructure planning simple and visual.

Happy planning! 🌊⚡

