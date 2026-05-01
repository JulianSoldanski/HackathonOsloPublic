# How to Update Under-Construction Plants Data

## Overview
The system loads under-construction plants from a local JSON file first, then falls back to the NVE API if the file doesn't exist.

## Updating the Local Data File

### Location
The data file should be placed at:
```
backend/data/data.json
```

### Format
The file should contain a direct response from the NVE ArcGIS API:

```json
{
  "displayFieldName": "objektType",
  "fieldAliases": { ... },
  "geometryType": "esriGeometryPoint",
  "spatialReference": { "wkid": 25833, "latestWkid": 25833 },
  "fields": [ ... ],
  "features": [
    {
      "attributes": {
        "OBJECTID": 1676,
        "vannkraftverkNavn": "Plant Name",
        "maksYtelse_MW": 2.7,
        "status": "U",
        "kdbNr": 5849,
        "kommuneNavn": "Municipality",
        "fylke": "County",
        ...
      },
      "geometry": {
        "x": 13406.375,
        "y": 6695794.582
      }
    }
  ]
}
```

### How to Get Fresh Data

#### Method 1: Direct API Query
```bash
curl "https://nve.geodataonline.no/arcgis/rest/services/Vannkraft1/MapServer/8/query?where=status=%27U%27&outFields=*&returnGeometry=true&f=json" > backend/data/data.json
```

#### Method 2: Using Browser
1. Go to: https://nve.geodataonline.no/arcgis/rest/services/Vannkraft1/MapServer/8/query
2. Fill in the form:
   - **Where**: `status='U'`
   - **Out Fields**: `*`
   - **Return Geometry**: `true`
   - **Format**: `JSON`
3. Click "Query (GET)"
4. Copy the response and save to `backend/data/data.json`

#### Method 3: Using Python Script
```python
import requests
import json

url = "https://nve.geodataonline.no/arcgis/rest/services/Vannkraft1/MapServer/8/query"
params = {
    "where": "status='U'",
    "outFields": "*",
    "returnGeometry": "true",
    "f": "json"
}

response = requests.get(url, params=params)
data = response.json()

with open("backend/data/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Saved {len(data.get('features', []))} plants to data.json")
```

## When to Update

You should update the data file when:
1. **Regular maintenance**: Monthly or quarterly updates
2. **After major changes**: When you know new plants have been added to NVE database
3. **Before important demos**: To ensure latest data is available
4. **When API is slow/unreliable**: Pre-download data for better performance

## Verifying the Update

After updating the file, restart the backend and check the logs:

```bash
INFO: Loading under-construction plants from local file: /path/to/backend/data/data.json
INFO: Loaded 60 under-construction plants from local file
INFO: Fetched 60 under-construction plants
```

You should see:
1. Message about loading from local file
2. Number of plants loaded
3. Then the system proceeds to scrape deadlines

## Troubleshooting

### File Not Found
If you see: `Falling back to NVE API...`
- Check that the file exists at `backend/data/data.json`
- Verify the path is correct relative to the backend directory

### Invalid JSON
If loading fails with error:
- Validate your JSON at https://jsonlint.com/
- Ensure proper encoding (UTF-8)
- Check for trailing commas

### No Plants Loaded
If you see `Loaded 0 under-construction plants`:
- Verify the JSON has a "features" array
- Check that features have the correct structure
- Ensure status='U' plants are in the file

## Automatic Fallback

If the local file:
- Doesn't exist
- Is corrupted
- Fails to load

The system will automatically fall back to querying the NVE API directly. This ensures the application always works, even without the pre-downloaded data file.

## Performance Considerations

### With Local File
- **Load time**: < 1 second
- **Network dependency**: None
- **Rate limiting**: Not applicable

### With API Query
- **Load time**: 5-15 seconds (depends on NVE API)
- **Network dependency**: Requires internet connection
- **Rate limiting**: Subject to NVE's limits

**Recommendation**: Always maintain an updated local file for production deployments.

## Example: Complete Update Process

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create data directory if it doesn't exist
mkdir -p data

# 3. Download fresh data
curl "https://nve.geodataonline.no/arcgis/rest/services/Vannkraft1/MapServer/8/query?where=status=%27U%27&outFields=*&returnGeometry=true&f=json" > data/data.json

# 4. Verify the file
cat data/data.json | jq '.features | length'
# Should output: 60 (or current number of under-construction plants)

# 5. Restart the application
# If using Docker:
docker-compose restart backend

# If running locally:
# Kill the uvicorn process and restart:
uvicorn app.main:app --reload
```

## Notes

- The system still scrapes deadlines from the NVE website for each plant
- Updating the JSON file only updates the plant list, not the deadlines
- Deadlines are always fetched fresh on each search to ensure accuracy
- Consider setting up a cron job to update the file regularly

