# Architecture Documentation

## System Overview

The Norway Hydropower Visualizer is a full-stack web application that helps assess potential data center locations by analyzing hydropower capacity and grid headroom.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + MapboxGL + TailwindCSS                │
│  - Interactive map visualization                             │
│  - Location search and analysis                              │
│  - Real-time data display                                    │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST API
                 │
┌────────────────▼────────────────────────────────────────────┐
│                         Backend                              │
│  FastAPI (Python)                                            │
│  - REST API endpoints                                        │
│  - Data caching and processing                               │
│  - Geospatial calculations                                   │
└────────────┬───────────────────┬──────────────────────────┘
             │                   │
             │                   │
┌────────────▼─────────┐  ┌─────▼──────────────────────────┐
│   SQLite Database    │  │  NVE ArcGIS MapServer          │
│   - Cached plants    │  │  - Hydropower plant data       │
│   - Metadata         │  │  - Real-time updates           │
└──────────────────────┘  └────────────────────────────────┘
```

---

## Backend Architecture

### Technology Stack

- **Framework:** FastAPI 0.104+
- **Database:** SQLite with spatial indexing
- **HTTP Client:** httpx for async API calls
- **Geospatial:** geopy for distance calculations
- **ASGI Server:** Uvicorn

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app & endpoints
│   ├── config.py         # Settings & configuration
│   ├── models.py         # Pydantic data models
│   ├── database.py       # SQLite operations
│   ├── nve_client.py     # NVE API integration
│   ├── power_zones.py    # Power zone data
│   └── utils.py          # Helper functions
├── data/                 # SQLite database (generated)
├── requirements.txt
├── Dockerfile
└── .env
```

### Key Components

#### 1. **API Layer** (`main.py`)

Handles HTTP requests and orchestrates business logic:

- `GET /api/plants` - Query hydropower plants
- `GET /api/zone/{id}` - Get power zone data
- `GET /api/estimate` - Calculate capacity estimate
- `POST /api/refresh` - Trigger data refresh

#### 2. **Data Layer** (`database.py`)

Manages persistent storage:

- SQLite database with spatial indexes
- Caching mechanism with TTL
- Efficient radius queries using bounding boxes
- Automatic stale data detection

#### 3. **External Integration** (`nve_client.py`)

Fetches data from NVE ArcGIS REST API:

- Async HTTP requests
- Pagination handling (1000 records per batch)
- Feature parsing and normalization
- Error handling and fallback to cache

#### 4. **Business Logic** (`utils.py`, `power_zones.py`)

Core calculations:

- Haversine distance for geodesic measurements
- Power zone determination by coordinates
- Grid constraint assessment
- Capacity aggregation

### Data Flow

```
1. User Request
   ↓
2. API Endpoint (FastAPI)
   ↓
3. Check Cache Status
   ↓
4. If stale → Fetch from NVE API → Update Database
   ↓
5. Query Database (spatial filtering)
   ↓
6. Calculate Distance (Haversine)
   ↓
7. Aggregate Capacity
   ↓
8. Assess Grid Constraint
   ↓
9. Return JSON Response
```

### Caching Strategy

- **Initial Load:** Fetch all plants on first startup
- **TTL:** 7 days (configurable)
- **Refresh:** Background task or manual trigger
- **Fallback:** Use stale cache if API fails

### Performance Optimizations

1. **Spatial Indexing:** SQLite indexes on lat/lon
2. **Bounding Box Pre-filter:** Reduce distance calculations
3. **Result Limiting:** Cap responses at reasonable sizes
4. **Async I/O:** Non-blocking external API calls

---

## Frontend Architecture

### Technology Stack

- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **Map Library:** Mapbox GL JS + react-map-gl
- **Styling:** TailwindCSS
- **HTTP Client:** Axios
- **Icons:** Lucide React

### Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Map.tsx           # MapboxGL wrapper
│   │   ├── Sidebar.tsx       # Search & results UI
│   │   └── ThemeToggle.tsx   # Dark/light mode
│   ├── App.tsx               # Main application
│   ├── main.tsx              # Entry point
│   ├── types.ts              # TypeScript types
│   ├── api.ts                # API client
│   ├── utils.ts              # Helper functions
│   └── index.css             # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── Dockerfile
```

### Component Architecture

```
App (State Management)
├── ThemeToggle (Theme Context)
├── Sidebar
│   ├── Search Form
│   ├── Capacity Summary
│   ├── Zone Details
│   ├── Plant List
│   └── Recommendation
└── Map
    ├── Mapbox GL Canvas
    ├── Plant Markers
    ├── Search Radius Circle
    ├── Navigation Controls
    └── Legend
```

### State Management

Using React hooks (useState, useEffect):

- **Theme:** Persisted to localStorage
- **Search State:** Lat/lon/radius
- **Results:** Capacity estimate data
- **Selected Plant:** Current plant details
- **Loading:** UI feedback state

### Data Flow

```
1. User Input (Search Form)
   ↓
2. State Update (useState)
   ↓
3. API Call (axios)
   ↓
4. Backend Processing
   ↓
5. Response → State Update
   ↓
6. Component Re-render
   ↓
7. Map & UI Update
```

### Map Visualization

#### Markers

- **Color-coded by type:**
  - Green: Mikro (<1 MW)
  - Orange: Mini (1-10 MW)
  - Red: Stor (>10 MW)
  - Gray: Planned

- **Size-coded by capacity:**
  - Larger circles = higher capacity
  - Hover tooltip with details
  - Click to select plant

#### Search Radius

- Blue circle overlay
- Center marker
- Fly-to animation on search

### Responsive Design

- **Desktop:** Side-by-side layout (sidebar + map)
- **Tablet:** Collapsible sidebar
- **Mobile:** Full-screen map with overlay

---

## API Contract

### Data Models

#### HydropowerPlant

```typescript
{
  id: string;
  name: string;
  maksYtelse_MW: number;
  type: 'Mikro' | 'Mini' | 'Stor';
  year?: number;
  kommune?: string;
  fylke?: string;
  owner?: string;
  coordinates: { lat: number; lon: number };
  status: 'existing' | 'planned';
  distance_km?: number;
}
```

#### PowerZone

```typescript
{
  id: 'NO1' | 'NO2' | 'NO3' | 'NO4' | 'NO5';
  name: string;
  total_generation_MW: number;
  consumption_MW: number;
  export_MW: number;
  headroom_MW: number;
  last_updated: string;
}
```

#### CapacityEstimate

```typescript
{
  location: { lat: number; lon: number };
  radius_km: number;
  nearby_plants_count: number;
  total_nearby_capacity_MW: number;
  plants: HydropowerPlant[];
  power_zone: PowerZone;
  grid_constraint: {
    status: 'ok' | 'limited' | 'blocked';
    description: string;
    color: 'green' | 'orange' | 'red';
  };
  recommendation: string;
}
```

---

## Security Considerations

### Backend

- CORS configured (restrict in production)
- No authentication (add OAuth2 for production)
- Input validation with Pydantic
- SQL injection protected (parameterized queries)
- Rate limiting (add in production)

### Frontend

- Environment variables for sensitive data
- No API keys in source code
- XSS protection via React
- HTTPS required in production

---

## Scalability

### Current Limitations

- SQLite: Single-writer, local file
- No horizontal scaling
- In-memory cache only

### Future Improvements

1. **Database:** PostgreSQL with PostGIS
2. **Caching:** Redis for distributed cache
3. **API:** Load balancer + multiple instances
4. **CDN:** Static assets on CloudFront/Cloudflare
5. **Real-time:** WebSocket for live updates

---

## Deployment

### Docker Compose (Current)

- Single-host deployment
- Development-friendly
- Easy local setup

### Production Options

1. **Cloud Run / App Engine:** Serverless containers
2. **Kubernetes:** Multi-container orchestration
3. **VM + Nginx:** Traditional server setup
4. **Vercel + Railway:** Frontend + Backend split

---

## Monitoring & Observability

### Recommended Tools

- **Logs:** ELK stack or CloudWatch
- **Metrics:** Prometheus + Grafana
- **Tracing:** Jaeger or Datadog
- **Uptime:** UptimeRobot or Pingdom

### Key Metrics

- API response time
- Cache hit rate
- NVE API success rate
- Database query performance
- Active users
- Map tile loads

---

## Future Enhancements

1. **Authentication:** User accounts and saved searches
2. **Historical Data:** Track capacity changes over time
3. **DSO Integration:** Real-time grid constraint data
4. **Export Features:** CSV/PDF reports
5. **Advanced Analytics:** ML-based site recommendations
6. **Notifications:** Alert users on capacity changes
7. **Mobile App:** Native iOS/Android

