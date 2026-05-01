# Under-Construction Power Plants Feature

## Overview
This feature adds support for visualizing power plants under construction with deadline information scraped from NVE's website.

## What's Been Added

### Backend Changes

#### 1. Web Scraping Capability (`nve_client.py`)
- Added `scrape_deadline_from_nve()` method to extract construction deadlines from NVE website
- Scrapes from: `https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id={kdbNr}&type=V-1`
- Searches for deadline patterns like "Utsatt byggefrist. Ny frist er 19.12.2023"
- Handles errors gracefully - shows plants even if scraping fails
- Logs all scraping attempts to console for debugging

#### 2. Under-Construction Plant Fetching (`nve_client.py`)
- Added `fetch_under_construction_plants()` method
- Fetches plants with `status='U'` from NVE API layer 8
- Automatically scrapes deadlines for each plant using their kdbNr
- Returns plants with deadline information attached

#### 3. API Endpoints (`main.py`)
- **GET `/api/under-construction`**: Get under-construction plants (with optional location filtering)
- **POST `/api/refresh-under-construction`**: Manually trigger refresh of under-construction plants
- Updated **GET `/api/plants`**: Now supports `status=under_construction` parameter
- Updated cache refresh to automatically fetch and store under-construction plants

#### 4. Data Models (`models.py`)
Added new fields to `HydropowerPlant`:
- `kdbNr`: KDB number for linking to NVE website
- `deadline`: Construction deadline (string)
- `deadline_scraped`: Boolean indicating if deadline was successfully scraped
- Updated `status` field to include `'under_construction'` option

#### 5. Dependencies (`requirements.txt`)
Added:
- `beautifulsoup4==4.12.2`: For HTML parsing
- `lxml==4.9.3`: For faster HTML parsing

### Frontend Changes

#### 1. TypeScript Types (`types.ts`)
- Updated `HydropowerPlant` interface with new fields
- Added support for `'under_construction'` status

#### 2. API Client (`api.ts`)
- Added `getUnderConstructionPlants()`: Fetch under-construction plants
- Added `refreshUnderConstructionPlants()`: Trigger refresh

#### 3. App State Management (`App.tsx`)
- Added `PlantViewMode` type: `'existing' | 'under_construction' | 'both'`
- Added state for under-construction plants
- Fetches under-construction plants automatically when searching
- Passes view mode and plants to child components

#### 4. Toggle Buttons (`Sidebar.tsx`)
Added three-button toggle:
- **Existing Only**: Shows only existing power plants (green button)
- **Under Constr.**: Shows only under-construction plants (yellow button)
- **Show Both**: Shows both types (blue button, default)

Shows count of under-construction plants found.

#### 5. Map Visualization (`Map.tsx`)
- **Yellow markers** with construction icon for under-construction plants
- Filters visible plants based on selected view mode
- Hover tooltip shows deadline if available
- Map popup displays deadline information with link to NVE website
- Updated legend to include under-construction plants (yellow)

#### 6. Plant Details Display (`Sidebar.tsx`)
When clicking an under-construction plant:
- Shows "Under Construction" badge
- Displays construction deadline (if available)
- Provides link to NVE website for more details
- Shows "Not available" if deadline couldn't be scraped

## How It Works

### Backend Flow
1. User searches for a location
2. Backend loads under-construction plants:
   - **First**: Tries to load from `backend/data/data.json` (if exists)
   - **Fallback**: Fetches from NVE API with query `status='U'`
3. For each plant, backend:
   - Gets the kdbNr (KDB number)
   - Visits NVE website: `https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id={kdbNr}&type=V-1`
   - Scrapes the page for deadline information
   - Logs success/failure to console
   - Attaches deadline to plant data (or null if not found)
4. Returns plants with deadline information to frontend

### Data Source Priority
1. **Local JSON file** (`backend/data/data.json`) - Loaded first if present
2. **NVE API** - Used as fallback if JSON file doesn't exist or fails to load

This approach ensures:
- Faster loading from local file
- No dependency on NVE API availability
- Ability to work with pre-downloaded data
- Automatic fallback to live API if needed

### Frontend Flow
1. User searches for a location
2. App fetches both existing and under-construction plants
3. User can toggle between views using buttons in sidebar
4. Map shows appropriate markers:
   - Lightning icon (colored by type) for existing plants
   - Construction icon (yellow) for under-construction plants
5. Clicking a plant shows full details including deadline
6. Link to NVE website allows viewing full project details

## Usage Examples

### View Under-Construction Plants Only
1. Search for any location in Norway
2. Click "Under Constr." button in sidebar
3. Map now shows only yellow markers (under construction)

### View All Plants Together
1. Search for any location
2. Click "Show Both" button (default)
3. Map shows both existing (colored) and under-construction (yellow) plants

### View Plant Deadline
1. Click on any yellow marker
2. Popup or sidebar shows:
   - Plant name and capacity
   - "Under Construction" status
   - Construction deadline (if available)
   - Link to NVE website

## API Examples

### Get Under-Construction Plants
```bash
# All under-construction plants (limited to 100)
curl "http://localhost:8000/api/under-construction"

# Under-construction plants near Bergen (50km radius)
curl "http://localhost:8000/api/under-construction?lat=60.391&lon=5.324&radius_km=50"
```

### Get All Plants Including Under-Construction
```bash
# Get all types of plants
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&status=all"

# Get only under-construction plants
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&status=under_construction"
```

### Response Format
```json
{
  "id": "12345",
  "name": "Example Kraftverk",
  "maksYtelse_MW": 5.2,
  "type": "Mini",
  "status": "under_construction",
  "kdbNr": 6299,
  "deadline": "19.12.2023",
  "deadline_scraped": true,
  "coordinates": {
    "lat": 60.5,
    "lon": 5.5
  }
}
```

## Console Output
The backend logs web scraping activity:
- `INFO: Scraped deadline for kdbNr 6299: 19.12.2023` (success)
- `WARNING: No deadline found for kdbNr 6299 at https://...` (not found)
- `ERROR: HTTP error scraping deadline for kdbNr 6299: ...` (error)

Check the backend console to see scraping results for each plant.

## Error Handling
- If web scraping fails, plants are still shown
- `deadline` field will be `null`
- `deadline_scraped` will be `false`
- User can still click link to view NVE website manually
- All errors are logged to console for debugging

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Running
The feature works automatically when you start the application. On first search, the backend will:
1. Fetch under-construction plants from NVE
2. Scrape deadlines for each plant (you'll see console output)
3. Cache the results
4. Return data to frontend

## Notes
- Deadline scraping may take a few seconds per plant
- Results are cached to avoid repeated scraping
- Some plants may not have deadline information on NVE website
- The scraper looks for Norwegian text patterns like "Utsatt byggefrist" and "Ny frist er"
- Yellow color (#facc15) is used for under-construction plants to distinguish them

## Future Improvements
- Add deadline sorting and filtering
- Show countdown to deadline
- Add notifications for approaching deadlines
- Cache scraped deadlines in database
- Add retry logic for failed scrapes
- Support for more deadline text patterns

