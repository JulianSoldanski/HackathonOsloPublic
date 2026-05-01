import axios from 'axios';
import type { HydropowerPlant, PowerZone, CapacityEstimate, RecommendedLocation, PlantAnalysisResult, DataCenter, DataCenterCreate } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const getPlants = async (
  lat?: number,
  lon?: number,
  radius_km: number = 50,
  status: string = 'all'
): Promise<HydropowerPlant[]> => {
  const params: any = { status };
  if (lat !== undefined && lon !== undefined) {
    params.lat = lat;
    params.lon = lon;
    params.radius_km = radius_km;
  }
  
  const response = await api.get<HydropowerPlant[]>('/plants', { params });
  return response.data;
};

export const getZone = async (zoneId: string): Promise<PowerZone> => {
  const response = await api.get<PowerZone>(`/zone/${zoneId}`);
  return response.data;
};

export const getZones = async (includeDataCenters: boolean = false): Promise<Record<string, PowerZone>> => {
  const response = await api.get<Record<string, PowerZone>>('/zones', {
    params: { include_data_centers: includeDataCenters }
  });
  return response.data;
};

export const getCapacityEstimate = async (
  lat: number,
  lon: number,
  radius_km: number = 50
): Promise<CapacityEstimate> => {
  const response = await api.get<CapacityEstimate>('/estimate', {
    params: { lat, lon, radius_km }
  });
  return response.data;
};

export const getRecommendedLocations = async (
  min_capacity_mw: number = 50,
  limit: number = 10
): Promise<RecommendedLocation[]> => {
  const response = await api.get<RecommendedLocation[]>('/recommended-locations', {
    params: { min_capacity_mw, limit }
  });
  return response.data;
};

export const refreshCache = async (): Promise<void> => {
  await api.post('/refresh');
};

export const getUnderConstructionPlants = async (
  lat?: number,
  lon?: number,
  radius_km: number = 50,
  timeline_months?: number
): Promise<HydropowerPlant[]> => {
  const params: any = {};
  if (lat !== undefined && lon !== undefined) {
    params.lat = lat;
    params.lon = lon;
    params.radius_km = radius_km;
  }
  if (timeline_months !== undefined) {
    params.timeline_months = timeline_months;
  }
  
  const response = await api.get<HydropowerPlant[]>('/under-construction', { params });
  return response.data;
};

export const refreshUnderConstructionPlants = async (): Promise<void> => {
  await api.post('/refresh-under-construction');
};

export const analyzePlant = async (plantName: string): Promise<PlantAnalysisResult> => {
  const response = await api.post<PlantAnalysisResult>('/analyze-plant', null, {
    params: { plant_name: plantName }
  });
  return response.data;
};

export const createDataCenter = async (data: DataCenterCreate): Promise<DataCenter> => {
  const response = await api.post<DataCenter>('/data-centers', data);
  return response.data;
};

export const getDataCenters = async (): Promise<DataCenter[]> => {
  const response = await api.get<DataCenter[]>('/data-centers');
  return response.data;
};

export const deleteDataCenter = async (id: string): Promise<void> => {
  await api.delete(`/data-centers/${id}`);
};

