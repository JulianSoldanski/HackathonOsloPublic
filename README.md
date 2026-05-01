# Norway Hydropower & Grid Headroom Visualizer

A full-stack web application for visualizing available hydropower capacity and grid headroom in Norway to assess potential sites for new data centers.







https://github.com/user-attachments/assets/5ead2946-19e6-4793-b362-8430c3b90ca1

https://github.com/user-attachments/assets/210ec7e0-6363-4618-a905-6c69489cf89f


## Features

- **Interactive Map**: Visualize hydropower plants across Norway with MapboxGL
- **Real-time Data**: Fetch data from NVE's Vannkraft1 MapServer (ArcGIS REST API)
- **Zone Analysis**: View power zone data (NO1-NO5) with generation, consumption, and headroom
- **Location Search**: Find potential data center sites and calculate nearby capacity
- **Grid Assessment**: Estimate energy headroom and grid constraints
- **Dark/Light Theme**: Modern UI with TailwindCSS

## Stack

- **Backend**: Python FastAPI
- **Frontend**: React + TypeScript + MapboxGL
- **Database**: SQLite (development)
- **Deployment**: Docker

## Project Structure

```
Hackathon2/
├── backend/          # FastAPI application
├── frontend/         # React TypeScript app
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

```bash
# One-time: env files are loaded by Compose (not committed). Copy examples and fill in values:
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit frontend/.env — set VITE_MAPBOX_TOKEN. Optionally set backend AI keys (see backend/.env.example).

# Or use ./start.sh — it creates .env files and starts Compose.

# Start all services
docker compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /api/plants` - Get hydropower plants within radius
  - Query params: `lat`, `lon`, `radius_km` (optional)
- `GET /api/zone/{zone_id}` - Get power zone data (NO1-NO5)
- `GET /api/estimate` - Get combined capacity and headroom estimate
  - Query params: `lat`, `lon`
- `GET /api/refresh` - Manually refresh cached data (admin)

## Data Sources

- **NVE Vannkraft1 MapServer**: https://nve.geodataonline.no/arcgis/rest/services/Vannkraft1/MapServer
  - Layer 0: Existing hydropower plants
  - Layer 8: Planned/under construction plants
- **Power Zones**: NO1 (Oslo), NO2 (Kristiansand), NO3 (Trondheim), NO4 (Tromsø), NO5 (Bergen)

## Environment Variables

Create `.env` files in backend and frontend directories:

### Backend `.env`

See `backend/.env.example`. Core settings:

```
DATABASE_URL=sqlite:///./data/hydropower.db
CACHE_EXPIRY_DAYS=7
LOG_LEVEL=INFO
```

Optional (AI plant analysis): `GOOGLE_SEARCH_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID`.

### Frontend `.env`

See `frontend/.env.example`. You need a Mapbox public token for the map. Optional: `VITE_OPENWEATHER_API_KEY` for the temperature overlay.

## License

MIT

