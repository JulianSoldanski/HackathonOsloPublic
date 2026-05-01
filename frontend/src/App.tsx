import { useState, useEffect } from 'react';
import MapComponent from './components/Map';
import Sidebar from './components/Sidebar';
import ThemeToggle from './components/ThemeToggle';
import ZoneBubbles from './components/ZoneBubbles';
import { getCapacityEstimate, getRecommendedLocations, getUnderConstructionPlants, getDataCenters } from './api';
import type { HydropowerPlant, CapacityEstimate, Theme, RecommendedLocation, DataCenter } from './types';

export type PlantViewMode = 'existing' | 'under_construction' | 'both';

function App() {
  const [theme, setTheme] = useState<Theme>('light');
  const [estimate, setEstimate] = useState<CapacityEstimate | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<HydropowerPlant | null>(null);
  const [searchCenter, setSearchCenter] = useState<[number, number] | undefined>();
  const [searchRadius, setSearchRadius] = useState<number | undefined>();
  const [loading, setLoading] = useState(false);
  const [recommendedLocations, setRecommendedLocations] = useState<RecommendedLocation[]>([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [plantViewMode, setPlantViewMode] = useState<PlantViewMode>('both');
  const [underConstructionPlants, setUnderConstructionPlants] = useState<HydropowerPlant[]>([]);
  const [timelineMonths, setTimelineMonths] = useState<number>(24); // Default 2 years
  const [dataCenters, setDataCenters] = useState<DataCenter[]>([]);
  const [zoneRefreshTrigger, setZoneRefreshTrigger] = useState(0);

  // Initialize theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      setTheme('system'); // Default to system mode
    }
  }, []);

  // Apply theme to document and handle system theme detection
  useEffect(() => {
    const applyTheme = () => {
      let effectiveTheme: 'light' | 'dark';
      
      if (theme === 'system') {
        effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      } else {
        effectiveTheme = theme;
      }
      
      if (effectiveTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    };

    applyTheme();
    localStorage.setItem('theme', theme);

    // Listen for system theme changes when in system mode
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', applyTheme);
      return () => mediaQuery.removeEventListener('change', applyTheme);
    }
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme(prev => {
      switch (prev) {
        case 'light':
          return 'dark';
        case 'dark':
          return 'system';
        case 'system':
          return 'light';
        default:
          return 'light';
      }
    });
  };

  const handleSearch = async (lat: number, lon: number, radius: number) => {
    setLoading(true);
    setSelectedPlant(null);
    
    try {
      const result = await getCapacityEstimate(lat, lon, radius);
      setEstimate(result);
      setSearchCenter([lon, lat]);
      setSearchRadius(radius);
      
      // Fetch under-construction plants for the same location with timeline filter
      const underConstruction = await getUnderConstructionPlants(lat, lon, radius, timelineMonths);
      setUnderConstructionPlants(underConstruction);
      console.log('Fetched under-construction plants:', underConstruction);
    } catch (error) {
      console.error('Error fetching estimate:', error);
      alert('Failed to fetch data. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handlePlantViewModeChange = (mode: PlantViewMode) => {
    setPlantViewMode(mode);
  };

  const handleTimelineChange = (months: number) => {
    setTimelineMonths(months);
  };

  // Refetch under-construction plants when timeline changes
  useEffect(() => {
    const refetchUnderConstructionPlants = async () => {
      if (searchCenter && searchRadius) {
        try {
          const underConstruction = await getUnderConstructionPlants(
            searchCenter[1], // lat
            searchCenter[0], // lon
            searchRadius,
            timelineMonths
          );
          setUnderConstructionPlants(underConstruction);
          console.log('Refetched under-construction plants for new timeline:', underConstruction.length);
        } catch (error) {
          console.error('Error refetching under-construction plants:', error);
        }
      }
    };

    refetchUnderConstructionPlants();
  }, [timelineMonths, searchCenter, searchRadius]);

  // Auto-load recommended locations and data centers on startup
  useEffect(() => {
    const loadInitialRecommendations = async () => {
      try {
        const locations = await getRecommendedLocations(50, 15);
        setRecommendedLocations(locations);
        setShowRecommendations(true);
      } catch (error) {
        console.error('Error loading initial recommendations:', error);
      }
    };

    const loadDataCenters = async () => {
      try {
        const dcs = await getDataCenters();
        setDataCenters(dcs);
      } catch (error) {
        console.error('Error loading data centers:', error);
      }
    };

    loadInitialRecommendations();
    loadDataCenters();
  }, []);

  const handlePlantClick = (plant: HydropowerPlant) => {
    setSelectedPlant(plant);
  };

  const handleClosePlantDetails = () => {
    setSelectedPlant(null);
  };

  const handleShowRecommendations = async (minCapacity?: number) => {
    setLoading(true);
    try {
      const capacity = minCapacity || 50;
      const locations = await getRecommendedLocations(capacity, 15);
      setRecommendedLocations(locations);
      setShowRecommendations(true);
      setEstimate(null); // Clear single location estimate
      setSearchCenter(undefined);
      setSearchRadius(undefined);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      alert('Failed to fetch recommended locations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLocationClick = (location: RecommendedLocation) => {
    // Don't hide recommendations, just analyze the location
    handleSearch(location.location.lat, location.location.lon, 50);
  };

  const refreshDataCenters = async () => {
    try {
      const dcs = await getDataCenters();
      setDataCenters(dcs);
      setZoneRefreshTrigger(prev => prev + 1); // Trigger zone refresh
    } catch (error) {
      console.error('Error refreshing data centers:', error);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="relative z-10 flex-shrink-0">
        <Sidebar
          estimate={estimate}
          selectedPlant={selectedPlant}
          onSearch={handleSearch}
          onClose={handleClosePlantDetails}
          loading={loading}
          recommendedLocations={showRecommendations ? recommendedLocations : []}
          onShowRecommendations={handleShowRecommendations}
          onLocationClick={handleLocationClick}
          plantViewMode={plantViewMode}
          onPlantViewModeChange={handlePlantViewModeChange}
          underConstructionPlants={underConstructionPlants}
          timelineMonths={timelineMonths}
          onTimelineChange={handleTimelineChange}
        />
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        <MapComponent
          plants={estimate?.plants || []}
          underConstructionPlants={underConstructionPlants}
          selectedPlant={selectedPlant}
          onPlantClick={handlePlantClick}
          onClosePlant={handleClosePlantDetails}
          searchRadius={searchRadius}
          searchCenter={searchCenter}
          theme={theme}
          recommendedLocations={showRecommendations ? recommendedLocations : []}
          onRecommendedLocationClick={handleLocationClick}
          plantViewMode={plantViewMode}
          onPlantViewModeChange={handlePlantViewModeChange}
          timelineMonths={timelineMonths}
          dataCenters={dataCenters}
          onDataCenterAdded={refreshDataCenters}
          onDataCenterDeleted={refreshDataCenters}
        />
        
        {/* Zone Capacity Bubbles */}
        <ZoneBubbles 
          includeDataCenters={dataCenters.length > 0} 
          refreshTrigger={zoneRefreshTrigger}
        />
      </div>

      {/* Theme Toggle */}
      <ThemeToggle theme={theme} onToggle={handleToggleTheme} />

      {/* Info Banner */}
      {!estimate && !loading && recommendedLocations.length === 0 && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-20 bg-blue-600 text-white px-8 py-4 rounded-lg shadow-lg max-w-lg text-center">
          <p className="text-xl font-medium">
            Loading recommended data center locations across Norway...
          </p>
        </div>
      )}
    </div>
  );
}

export default App;

