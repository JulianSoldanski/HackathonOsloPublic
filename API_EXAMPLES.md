# API Examples

This document provides practical examples for using the Hydropower Visualizer API.

## Base URL

- **Local Development:** `http://localhost:8000/api`
- **Production:** Update with your deployment URL

---

## Authentication

Currently, no authentication is required. For production deployments, consider adding OAuth2 or API keys.

---

## Endpoints

### 1. Health Check

Check if the API is running and view cache status.

**Request:**
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-11T10:30:00.000Z",
  "cache_plants": 1523,
  "cache_stale": false
}
```

---

### 2. Get All Plants (Limited)

Retrieve up to 100 hydropower plants without location filtering.

**Request:**
```bash
curl "http://localhost:8000/api/plants"
```

**Response:**
```json
[
  {
    "id": "12345",
    "name": "Granvin Kraftverk",
    "maksYtelse_MW": 45.5,
    "type": "Stor",
    "year": 1968,
    "kommune": "Granvin",
    "fylke": "Vestland",
    "owner": "BKK AS",
    "coordinates": {
      "lat": 60.5333,
      "lon": 6.7167
    },
    "status": "existing"
  }
]
```

---

### 3. Get Plants Near Location

Find hydropower plants within a radius of a specific location.

**Request:**
```bash
# Bergen area, 50km radius
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&radius_km=50"

# Oslo area, 30km radius
curl "http://localhost:8000/api/plants?lat=59.911&lon=10.757&radius_km=30"

# Only existing plants
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&radius_km=50&status=existing"

# Only planned plants
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&radius_km=50&status=planned"
```

**Response:**
```json
[
  {
    "id": "12345",
    "name": "Granvin Kraftverk",
    "maksYtelse_MW": 45.5,
    "type": "Stor",
    "year": 1968,
    "kommune": "Granvin",
    "fylke": "Vestland",
    "owner": "BKK AS",
    "coordinates": {
      "lat": 60.5333,
      "lon": 6.7167
    },
    "status": "existing",
    "distance_km": 23.4
  }
]
```

---

### 4. Get Power Zone Data

Retrieve information about a specific power zone (NO1-NO5).

**Request:**
```bash
# Bergen area (NO5)
curl "http://localhost:8000/api/zone/NO5"

# Oslo area (NO1)
curl "http://localhost:8000/api/zone/NO1"
```

**Response:**
```json
{
  "id": "NO5",
  "name": "Bergen / Vest-Norge",
  "total_generation_MW": 9500,
  "consumption_MW": 7200,
  "export_MW": 1800,
  "headroom_MW": 500,
  "last_updated": "2025-10-11T10:30:00.000Z"
}
```

---

### 5. Get All Power Zones

Retrieve data for all Norwegian power zones.

**Request:**
```bash
curl "http://localhost:8000/api/zones"
```

**Response:**
```json
{
  "NO1": {
    "id": "NO1",
    "name": "Oslo / Øst-Norge",
    "total_generation_MW": 8500,
    "consumption_MW": 7800,
    "export_MW": 400,
    "headroom_MW": 300,
    "last_updated": "2025-10-11T10:30:00.000Z"
  },
  "NO2": { ... },
  "NO3": { ... },
  "NO4": { ... },
  "NO5": { ... }
}
```

---

### 6. Get Capacity Estimate

Get a comprehensive analysis for a location including nearby capacity, power zone data, and recommendations.

**Request:**
```bash
# Bergen area
curl "http://localhost:8000/api/estimate?lat=60.391&lon=5.324&radius_km=50"

# Ål (common data center location)
curl "http://localhost:8000/api/estimate?lat=60.632&lon=8.566&radius_km=50"

# Custom radius
curl "http://localhost:8000/api/estimate?lat=60.391&lon=5.324&radius_km=100"
```

**Response:**
```json
{
  "location": {
    "lat": 60.391,
    "lon": 5.324
  },
  "radius_km": 50,
  "nearby_plants_count": 23,
  "total_nearby_capacity_MW": 567.8,
  "plants": [
    {
      "id": "12345",
      "name": "Granvin Kraftverk",
      "maksYtelse_MW": 45.5,
      "type": "Stor",
      "year": 1968,
      "kommune": "Granvin",
      "fylke": "Vestland",
      "owner": "BKK AS",
      "coordinates": {
        "lat": 60.5333,
        "lon": 6.7167
      },
      "status": "existing",
      "distance_km": 23.4
    }
  ],
  "power_zone": {
    "id": "NO5",
    "name": "Bergen / Vest-Norge",
    "total_generation_MW": 9500,
    "consumption_MW": 7200,
    "export_MW": 1800,
    "headroom_MW": 500,
    "last_updated": "2025-10-11T10:30:00.000Z"
  },
  "grid_constraint": {
    "status": "ok",
    "description": "Good grid capacity and local generation available",
    "color": "green"
  },
  "recommendation": "Excellent location with 567.8 MW local capacity and 500.0 MW zone headroom. Suitable for large data center deployment."
}
```

---

### 7. Refresh Cache

Manually trigger a refresh of the cached hydropower data from NVE.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/refresh"
```

**Response:**
```json
{
  "message": "Cache refresh started",
  "status": "processing"
}
```

**Note:** This is an asynchronous operation. The refresh happens in the background.

---

### 8. Get Cache Status

Check the current cache status and last refresh time.

**Request:**
```bash
curl "http://localhost:8000/api/cache/status"
```

**Response:**
```json
{
  "last_refresh": "2025-10-11T03:00:00.000Z",
  "plant_count": 1523,
  "is_stale": false,
  "next_refresh": "2025-10-18T03:00:00.000Z"
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Invalid zone ID: NO6"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "radius_km"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently, no rate limiting is enforced. For production:
- Consider implementing rate limiting (e.g., 100 requests/minute per IP)
- Use Redis for distributed rate limiting

---

## Query Parameters Summary

### `/api/plants`
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| lat | float | No | - | Latitude of center point |
| lon | float | No | - | Longitude of center point |
| radius_km | float | No | 50.0 | Search radius in km (1-500) |
| status | string | No | "all" | Filter: "all", "existing", "planned" |

### `/api/estimate`
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| lat | float | Yes | - | Latitude of location |
| lon | float | Yes | - | Longitude of location |
| radius_km | float | No | 50.0 | Search radius in km (1-200) |

---

## Integration Examples

### Python

```python
import requests

API_BASE = "http://localhost:8000/api"

# Get capacity estimate
response = requests.get(f"{API_BASE}/estimate", params={
    "lat": 60.391,
    "lon": 5.324,
    "radius_km": 50
})

data = response.json()
print(f"Total capacity: {data['total_nearby_capacity_MW']} MW")
print(f"Recommendation: {data['recommendation']}")
```

### JavaScript/TypeScript

```typescript
const API_BASE = "http://localhost:8000/api";

async function getEstimate(lat: number, lon: number, radius: number) {
  const response = await fetch(
    `${API_BASE}/estimate?lat=${lat}&lon=${lon}&radius_km=${radius}`
  );
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const data = await response.json();
  console.log(`Total capacity: ${data.total_nearby_capacity_MW} MW`);
  return data;
}

// Usage
getEstimate(60.391, 5.324, 50);
```

### cURL Script

```bash
#!/bin/bash

API_BASE="http://localhost:8000/api"
LAT=60.391
LON=5.324
RADIUS=50

echo "Analyzing location: $LAT, $LON"

# Get estimate
RESPONSE=$(curl -s "$API_BASE/estimate?lat=$LAT&lon=$LON&radius_km=$RADIUS")

# Parse with jq
CAPACITY=$(echo $RESPONSE | jq -r '.total_nearby_capacity_MW')
STATUS=$(echo $RESPONSE | jq -r '.grid_constraint.status')

echo "Capacity: $CAPACITY MW"
echo "Status: $STATUS"
```

---

## Testing with Swagger UI

Visit http://localhost:8000/docs for an interactive API documentation interface where you can:
- Test all endpoints directly in the browser
- View request/response schemas
- Download OpenAPI specification

---

## Common Use Cases

### 1. Find Best Location for Data Center

```bash
# Compare multiple locations
for location in "60.391,5.324" "59.911,10.757" "63.431,10.395"; do
  IFS=',' read lat lon <<< "$location"
  curl -s "http://localhost:8000/api/estimate?lat=$lat&lon=$lon" | \
    jq -r '"\(.location.lat),\(.location.lon): \(.total_nearby_capacity_MW) MW"'
done
```

### 2. Export Plant Data to CSV

```bash
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&radius_km=100" | \
  jq -r '.[] | [.name, .maksYtelse_MW, .type, .kommune] | @csv'
```

### 3. Monitor Cache Status

```bash
# Check if refresh needed
curl -s "http://localhost:8000/api/cache/status" | jq '.is_stale'

# If stale, trigger refresh
if [ "$(curl -s http://localhost:8000/api/cache/status | jq -r '.is_stale')" = "true" ]; then
  curl -X POST "http://localhost:8000/api/refresh"
  echo "Cache refresh triggered"
fi
```

---

## Performance Tips

1. **Reduce Radius:** Smaller radius = faster queries
2. **Filter Status:** Use `status=existing` to exclude planned plants
3. **Cache Results:** Client-side caching for repeated queries
4. **Batch Requests:** Use `/api/zones` instead of multiple `/api/zone/{id}` calls

