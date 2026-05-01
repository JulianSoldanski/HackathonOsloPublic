# Setup Guide

## Prerequisites

1. **Docker & Docker Compose** (recommended for easiest setup)
   - [Install Docker Desktop](https://www.docker.com/products/docker-desktop)

2. **For Local Development:**
   - Node.js 18+ and npm
   - Python 3.11+
   - Git

3. **Mapbox Account** (free tier is sufficient)
   - Sign up at [mapbox.com](https://mapbox.com)
   - Get your access token from [account page](https://account.mapbox.com/access-tokens/)

---

## Quick Start with Docker (Recommended)

### 1. Clone and Setup

```bash
cd Hackathon2
```

### 2. Configure Frontend Environment

Create `frontend/.env` file:

```bash
cat > frontend/.env << EOF
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=YOUR_MAPBOX_TOKEN_HERE
EOF
```

**Important:** Replace `YOUR_MAPBOX_TOKEN_HERE` with your actual Mapbox token!

### 3. Start the Application

```bash
docker-compose up --build
```

This will:
- Build both backend and frontend containers
- Start the backend API on port 8000
- Start the frontend dev server on port 5173
- Create a persistent SQLite database volume

### 4. Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)

### 5. First Time Setup

The application will automatically:
1. Fetch hydropower plant data from NVE on first startup
2. Cache the data locally in SQLite
3. Refresh data weekly automatically

This initial fetch may take 1-2 minutes. Check the backend logs:

```bash
docker-compose logs -f backend
```

---

## Local Development Setup

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file with Mapbox token
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
echo "VITE_MAPBOX_TOKEN=your_token_here" >> .env

# Run dev server
npm run dev
```

---

## Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=sqlite:///./data/hydropower.db
CACHE_EXPIRY_DAYS=7
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=pk.your_token_here
```

---

## Troubleshooting

### "No Mapbox Token" Error

Make sure you've set `VITE_MAPBOX_TOKEN` in `frontend/.env` and restarted the dev server.

### Backend Not Fetching Data

Check backend logs for errors:
```bash
docker-compose logs backend
```

Common issues:
- Network connectivity to NVE API
- Database permissions
- Port 8000 already in use

### Frontend Can't Connect to Backend

1. Check if backend is running: http://localhost:8000/api/health
2. Verify CORS settings if accessing from different origin
3. Check `VITE_API_BASE_URL` in frontend/.env

### Docker Issues

```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build

# View logs
docker-compose logs -f

# Check container status
docker-compose ps
```

---

## Data Refresh

The application automatically refreshes NVE data every 7 days. To manually trigger a refresh:

```bash
curl -X POST http://localhost:8000/api/refresh
```

Or use the Swagger UI at http://localhost:8000/docs

---

## Production Deployment

### Docker Compose for Production

1. Update `docker-compose.yml` to use production builds
2. Set proper CORS origins in backend
3. Use environment-specific `.env` files
4. Consider using PostgreSQL instead of SQLite
5. Add nginx reverse proxy
6. Enable HTTPS with Let's Encrypt

### Environment-Specific Configuration

```bash
# Production
docker-compose -f docker-compose.prod.yml up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d
```

---

## API Usage Examples

### Get Plants Near Location

```bash
curl "http://localhost:8000/api/plants?lat=60.391&lon=5.324&radius_km=50"
```

### Get Capacity Estimate

```bash
curl "http://localhost:8000/api/estimate?lat=60.391&lon=5.324&radius_km=50"
```

### Get Power Zone Data

```bash
curl "http://localhost:8000/api/zone/NO5"
```

---

## Development Tips

### Hot Reload

Both frontend and backend support hot reload in development mode:
- **Backend:** Changes to `.py` files automatically reload the server
- **Frontend:** Changes to `.tsx/.ts` files trigger instant HMR

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation where you can test all endpoints.

### Debug Mode

Enable debug logging in backend:

```env
LOG_LEVEL=DEBUG
```

### VS Code Setup

Install recommended extensions:
- Python
- TypeScript Vue Plugin (Volar)
- Tailwind CSS IntelliSense
- ESLint

---

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review the API docs: http://localhost:8000/docs
3. Verify environment variables are set correctly

