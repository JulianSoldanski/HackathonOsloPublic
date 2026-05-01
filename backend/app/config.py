from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    api_title: str = "Norway Hydropower & Grid API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api"
    
    # Database
    database_url: str = "sqlite:///./data/hydropower.db"
    
    # Cache settings
    cache_expiry_days: int = 7
    
    # External APIs
    nve_base_url: str = "https://nve.geodataonline.no/arcgis/rest/services/Vannkraft1/MapServer"
    
    # Logging
    log_level: str = "INFO"

    # Optional: Google Custom Search + Gemini for /api/analyze-plant
    google_search_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

