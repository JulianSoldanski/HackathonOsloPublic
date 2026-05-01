import json
import sqlite3
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from .config import settings


class Database:
    """SQLite database handler for caching hydropower data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = settings.database_url.replace("sqlite:///", "")
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Plants cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plants (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    capacity_mw REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create spatial index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_plants_location 
                ON plants(lat, lon)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_plants_status 
                ON plants(status)
            """)
            
            # Cache metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Data centers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_centers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    capacity_mw REAL NOT NULL,
                    hydro_connections TEXT,
                    nearest_hydro_id TEXT NOT NULL,
                    nearest_hydro_name TEXT NOT NULL,
                    distance_to_hydro_km REAL NOT NULL,
                    nearest_city TEXT NOT NULL,
                    distance_to_city_km REAL NOT NULL,
                    power_zone_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_data_centers_location 
                ON data_centers(lat, lon)
            """)
            
            # Migrate existing data centers: add hydro_connections column if it doesn't exist
            try:
                cursor.execute("SELECT hydro_connections FROM data_centers LIMIT 1")
            except sqlite3.OperationalError:
                # Column doesn't exist, add it
                cursor.execute("ALTER TABLE data_centers ADD COLUMN hydro_connections TEXT")
            
            conn.commit()
    
    def save_plants(self, plants: List[Dict[str, Any]], status: str = "existing"):
        """Save plants to cache"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for plant in plants:
                cursor.execute("""
                    INSERT OR REPLACE INTO plants (id, data, lat, lon, capacity_mw, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    plant['id'],
                    json.dumps(plant),
                    plant['coordinates']['lat'],
                    plant['coordinates']['lon'],
                    plant['maksYtelse_MW'],
                    status
                ))
            
            # Update last refresh timestamp
            cursor.execute("""
                INSERT OR REPLACE INTO cache_metadata (key, value, updated_at)
                VALUES ('last_refresh', ?, CURRENT_TIMESTAMP)
            """, (datetime.now().isoformat(),))
            
            conn.commit()
    
    def get_plants_in_radius(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float,
        status: str = "all"
    ) -> List[Dict[str, Any]]:
        """Get plants within radius using simple bounding box"""
        # Rough conversion: 1 degree ≈ 111 km at equator (less at high latitudes)
        # For Norway (around 60°N), 1 degree longitude ≈ 55 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / 55.0  # Adjusted for Norway's latitude
        
        query = """
            SELECT data FROM plants
            WHERE lat BETWEEN ? AND ?
            AND lon BETWEEN ? AND ?
        """
        params = [
            lat - lat_delta,
            lat + lat_delta,
            lon - lon_delta,
            lon + lon_delta
        ]
        
        if status != "all":
            query += " AND status = ?"
            params.append(status)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            plants = []
            for row in cursor.fetchall():
                plants.append(json.loads(row[0]))
            
            return plants
    
    def normalize_deadline(self, deadline_str: Optional[str]) -> Optional[str]:
        """
        Normalize deadline dates - if in the past, add years to make it future
        Uses hash of plant name for consistent year offset (not random)
        
        Args:
            deadline_str: Original deadline string (can be "DD.MM.YYYY" or "Q# YYYY" format)
            
        Returns:
            Normalized deadline string in "Q# YYYY" format
        """
        if not deadline_str:
            return None
            
        current_year = datetime.now().year
        current_date = datetime.now()
        
        # Try to parse Norwegian date format (DD.MM.YYYY)
        if '.' in deadline_str:
            try:
                parts = deadline_str.split('.')
                if len(parts) == 3:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    
                    deadline_date = datetime(year, month, day)
                    
                    # If deadline is in the past, add 2-4 years to make it future
                    if deadline_date < current_date:
                        # Calculate how many years to add to make it future
                        years_past = current_year - year
                        # Add enough years to be 2-4 years in future
                        new_year = current_year + max(2, (years_past % 3) + 2)
                        # Convert to quarter format
                        quarter = ((month - 1) // 3) + 1
                        return f"Q{quarter} {new_year}"
                    else:
                        # Convert existing future date to quarter format
                        quarter = ((month - 1) // 3) + 1
                        return f"Q{quarter} {year}"
            except (ValueError, IndexError):
                pass
        
        # Try to parse quarter format (Q# YYYY or Q# /YYYY)
        quarter_match = re.search(r'Q(\d)\s*/?\s*(\d{4})', deadline_str)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            
            # Estimate date from quarter (use middle month of quarter)
            month = (quarter - 1) * 3 + 2  # Q1->Feb, Q2->May, Q3->Aug, Q4->Nov
            deadline_date = datetime(year, month, 1)
            
            # If deadline is in the past, add 2-4 years to make it future
            if deadline_date < current_date:
                # Calculate how many years to add
                years_past = current_year - year
                # Add enough years to be 2-4 years in future
                new_year = current_year + max(2, (years_past % 3) + 2)
                return f"Q{quarter} {new_year}"
            else:
                return f"Q{quarter} {year}"
        
        # If we can't parse, return as-is
        return deadline_str
    
    def get_all_plants(self, status: str = "all") -> List[Dict[str, Any]]:
        """Get all plants from cache"""
        query = "SELECT data FROM plants"
        params = []
        
        if status != "all":
            query += " WHERE status = ?"
            params.append(status)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            plants = []
            for row in cursor.fetchall():
                plants.append(json.loads(row[0]))
            
            return plants
    
    def get_last_refresh(self) -> Optional[datetime]:
        """Get last cache refresh timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM cache_metadata WHERE key = 'last_refresh'
            """)
            
            row = cursor.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
            return None
    
    def is_cache_stale(self) -> bool:
        """Check if cache needs refresh"""
        last_refresh = self.get_last_refresh()
        if not last_refresh:
            return True
        
        expiry = timedelta(days=settings.cache_expiry_days)
        return datetime.now() - last_refresh > expiry
    
    def get_plant_count(self, status: str = "all") -> int:
        """Get total number of cached plants, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status == "all":
                cursor.execute("SELECT COUNT(*) FROM plants")
            else:
                cursor.execute("SELECT COUNT(*) FROM plants WHERE status = ?", (status,))
            
            return cursor.fetchone()[0]
    
    def clear_cache(self):
        """Clear all cached plants"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plants")
            cursor.execute("DELETE FROM cache_metadata WHERE key = 'last_refresh'")
            conn.commit()
    
    def add_data_center(self, data_center: Dict[str, Any]):
        """Add a data center to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Serialize hydro_connections to JSON if present
            hydro_connections_json = None
            if 'hydro_connections' in data_center and data_center['hydro_connections']:
                hydro_connections_json = json.dumps(data_center['hydro_connections'])
            
            cursor.execute("""
                INSERT INTO data_centers (
                    id, name, lat, lon, capacity_mw, hydro_connections,
                    nearest_hydro_id, nearest_hydro_name, distance_to_hydro_km,
                    nearest_city, distance_to_city_km, power_zone_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_center['id'],
                data_center['name'],
                data_center['coordinates']['lat'],
                data_center['coordinates']['lon'],
                data_center['capacity_mw'],
                hydro_connections_json,
                data_center['nearest_hydro_id'],
                data_center['nearest_hydro_name'],
                data_center['distance_to_hydro_km'],
                data_center['nearest_city'],
                data_center['distance_to_city_km'],
                data_center['power_zone_id'],
                data_center['created_at']
            ))
            conn.commit()
    
    def get_all_data_centers(self) -> List[Dict[str, Any]]:
        """Get all data centers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, lat, lon, capacity_mw, hydro_connections,
                       nearest_hydro_id, nearest_hydro_name, distance_to_hydro_km,
                       nearest_city, distance_to_city_km, power_zone_id, created_at
                FROM data_centers
            """)
            
            data_centers = []
            for row in cursor.fetchall():
                # Parse hydro_connections from JSON if present
                hydro_connections = []
                if row[5]:  # hydro_connections column
                    try:
                        hydro_connections = json.loads(row[5])
                    except (json.JSONDecodeError, TypeError):
                        # If parsing fails, create a single connection from legacy fields
                        hydro_connections = [{
                            'hydro_id': row[6],  # nearest_hydro_id
                            'hydro_name': row[7],  # nearest_hydro_name
                            'distance_km': row[8],  # distance_to_hydro_km
                            'allocated_capacity_mw': row[4]  # capacity_mw
                        }]
                
                # If no connections but we have legacy data, create a single connection
                if not hydro_connections and row[6]:  # nearest_hydro_id exists
                    hydro_connections = [{
                        'hydro_id': row[6],
                        'hydro_name': row[7],
                        'distance_km': row[8],
                        'allocated_capacity_mw': row[4]
                    }]
                
                data_centers.append({
                    'id': row[0],
                    'name': row[1],
                    'coordinates': {'lat': row[2], 'lon': row[3]},
                    'capacity_mw': row[4],
                    'hydro_connections': hydro_connections,
                    'nearest_hydro_id': row[6],
                    'nearest_hydro_name': row[7],
                    'distance_to_hydro_km': row[8],
                    'nearest_city': row[9],
                    'distance_to_city_km': row[10],
                    'power_zone_id': row[11],
                    'created_at': row[12]
                })
            
            return data_centers
    
    def delete_data_center(self, dc_id: str) -> bool:
        """Delete a data center by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM data_centers WHERE id = ?", (dc_id,))
            conn.commit()
            return cursor.rowcount > 0


# Global database instance
db = Database()

