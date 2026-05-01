import type { HydropowerPlant } from './types';

export const getPlantColor = (plant: HydropowerPlant): string => {
  if (plant.status === 'planned') {
    return '#cbd5e1'; // Lighter gray for planned (more visible)
  }
  
  switch (plant.type) {
    case 'Mikro':
      return '#10b981'; // Brighter green
    case 'Mini':
      return '#fb923c'; // Brighter orange
    case 'Stor':
      return '#f87171'; // Brighter red
    default:
      return '#94a3b8'; // Gray
  }
};

export const getPlantSize = (capacity_mw: number): number => {
  // Increased sizes by 2x for better visibility
  if (capacity_mw < 1) return 12;
  if (capacity_mw < 10) return 16;
  if (capacity_mw < 50) return 20;
  if (capacity_mw < 100) return 24;
  return 28;
};

export const formatNumber = (num: number, decimals: number = 1): string => {
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

export const getGridConstraintColor = (status: string): string => {
  switch (status) {
    case 'excellent':
      return 'bg-blue-500';
    case 'ok':
      return 'bg-green-500';
    case 'limited':
      return 'bg-orange-500';
    case 'challenging':
      return 'bg-yellow-500';
    case 'blocked':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
};

export const getZoneColor = (zoneId: string): string => {
  const colors: Record<string, string> = {
    'NO1': '#3b82f6', // Blue
    'NO2': '#10b981', // Green
    'NO3': '#f59e0b', // Orange
    'NO4': '#ef4444', // Red
    'NO5': '#8b5cf6', // Purple
  };
  return colors[zoneId] || '#6b7280';
};

// Norway center coordinates - adjusted for better full country view
export const NORWAY_CENTER: [number, number] = [10.7522, 64.5]; // Moved north to show more of Norway
export const NORWAY_ZOOM = 5.5; // Slightly zoomed out to show entire country

