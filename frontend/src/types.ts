export interface Coordinates {
  lat: number;
  lon: number;
}

export interface HydropowerPlant {
  id: string;
  name: string;
  maksYtelse_MW: number;
  type: 'Mikro' | 'Mini' | 'Stor';
  year?: number;
  kommune?: string;
  fylke?: string;
  owner?: string;
  coordinates: Coordinates;
  status: 'existing' | 'planned' | 'under_construction';
  distance_km?: number;
  kdbNr?: number;
  deadline?: string;
  deadline_scraped?: boolean;
}

export interface PowerZone {
  id: string;
  name: string;
  total_generation_MW: number;
  consumption_MW: number;
  export_MW: number;
  headroom_MW: number;
  last_updated: string;
}

export interface GridConstraint {
  status: 'ok' | 'limited' | 'blocked';
  description: string;
  color: 'green' | 'orange' | 'red';
}

export interface CapacityEstimate {
  location: Coordinates;
  radius_km: number;
  nearby_plants_count: number;
  total_nearby_capacity_MW: number;
  plants: HydropowerPlant[];
  power_zone: PowerZone;
  grid_constraint: GridConstraint;
  recommendation: string;
}

export interface RecommendedLocation {
  name: string;
  location: Coordinates;
  total_capacity_mw: number;
  nearby_plants: number;
  power_zone: string;
  zone_headroom_mw: number;
  grid_status: 'excellent' | 'ok' | 'limited' | 'challenging' | 'blocked';
  status_color: 'blue' | 'green' | 'orange' | 'yellow' | 'red';
  suitability_score: number;
}

export type Theme = 'light' | 'dark' | 'system';

export interface ViewState {
  longitude: number;
  latitude: number;
  zoom: number;
}

export interface PlantAnalysisSource {
  title: string;
  url: string;
  snippet: string;
}

export interface PlantAnalysisResult {
  plant_name: string;
  summary: string;
  sources: PlantAnalysisSource[];
  links: string[];
}

export interface HydroConnection {
  hydro_id: string;
  hydro_name: string;
  distance_km: number;
  allocated_capacity_mw: number;
}

export interface DataCenter {
  id: string;
  name: string;
  coordinates: Coordinates;
  capacity_mw: number;
  hydro_connections: HydroConnection[];
  // Legacy fields for backward compatibility
  nearest_hydro_id: string;
  nearest_hydro_name: string;
  distance_to_hydro_km: number;
  nearest_city: string;
  distance_to_city_km: number;
  power_zone_id: string;
  created_at: string;
}

export interface DataCenterCreate {
  name: string;
  lat: number;
  lon: number;
  capacity_mw: number;
}

