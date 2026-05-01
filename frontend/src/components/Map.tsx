import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import Map, { Marker, Layer, Source, NavigationControl, Popup } from 'react-map-gl';
import type { MapRef } from 'react-map-gl';
import { Zap, Star, X, Construction, Brain, Loader2, AlertCircle, Search, Server, Trash2, ExternalLink } from 'lucide-react';
import type { HydropowerPlant, ViewState, RecommendedLocation, PlantAnalysisResult, DataCenter, DataCenterCreate } from '../types';
import { getPlantColor, getPlantSize, NORWAY_CENTER, NORWAY_ZOOM, getGridConstraintColor } from '../utils';
import type { PlantViewMode } from '../App';
import { analyzePlant, createDataCenter, deleteDataCenter } from '../api';
import AddDataCenterModal from './AddDataCenterModal';
import LayerSwitcher, { type MapLayer } from './LayerSwitcher';

interface MapComponentProps {
  plants: HydropowerPlant[];
  underConstructionPlants: HydropowerPlant[];
  selectedPlant: HydropowerPlant | null;
  onPlantClick: (plant: HydropowerPlant) => void;
  onClosePlant: () => void;
  searchRadius?: number;
  searchCenter?: [number, number];
  theme: 'light' | 'dark';
  recommendedLocations: RecommendedLocation[];
  onRecommendedLocationClick: (location: RecommendedLocation) => void;
  plantViewMode: PlantViewMode;
  onPlantViewModeChange: (mode: PlantViewMode) => void;
  timelineMonths: number;
  dataCenters: DataCenter[];
  onDataCenterAdded: () => void;
  onDataCenterDeleted: () => void;
}

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

export default function MapComponent({
  plants,
  underConstructionPlants,
  selectedPlant,
  onPlantClick,
  onClosePlant,
  searchRadius,
  searchCenter,
  theme,
  recommendedLocations,
  onRecommendedLocationClick,
  plantViewMode,
  onPlantViewModeChange,
  timelineMonths,
  dataCenters,
  onDataCenterAdded,
  onDataCenterDeleted
}: MapComponentProps) {
  const mapRef = useRef<MapRef>(null);
  const [viewState, setViewState] = useState<ViewState>({
    longitude: NORWAY_CENTER[0],
    latitude: NORWAY_CENTER[1],
    zoom: NORWAY_ZOOM
  });
  const [analysisResult, setAnalysisResult] = useState<PlantAnalysisResult | null>(null);
  const [analyzingPlant, setAnalyzingPlant] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [rightClickCoords, setRightClickCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [showAddDCModal, setShowAddDCModal] = useState(false);
  const [selectedDataCenter, setSelectedDataCenter] = useState<DataCenter | null>(null);
  const [currentLayer, setCurrentLayer] = useState<MapLayer>('default');

  // Filter plants based on view mode (timeline filtering now done in backend)
  const visiblePlants = useMemo(() => {
    if (plantViewMode === 'existing') {
      return plants;
    } else if (plantViewMode === 'under_construction') {
      return underConstructionPlants;
    } else {
      // both
      return [...plants, ...underConstructionPlants];
    }
  }, [plants, underConstructionPlants, plantViewMode]);

  // Update view when search center changes
  useEffect(() => {
    if (searchCenter && mapRef.current) {
      mapRef.current.flyTo({
        center: searchCenter,
        zoom: 7, // Reduced zoom to keep more of Norway visible
        duration: 2000
      });
    }
  }, [searchCenter]);

  const handleMarkerClick = useCallback((plant: HydropowerPlant) => {
    onPlantClick(plant);
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [plant.coordinates.lon, plant.coordinates.lat],
        zoom: 8, // Reduced zoom to keep more context
        duration: 1500
      });
    }
  }, [onPlantClick]);

  const handleAnalyzePlant = async () => {
    if (!selectedPlant) return;
    
    setAnalyzingPlant(true);
    try {
      const result = await analyzePlant(selectedPlant.name);
      setAnalysisResult(result);
      setShowAnalysisModal(true);
    } catch (error) {
      console.error('Error analyzing plant:', error);
      alert('Failed to analyze plant. Please try again.');
    } finally {
      setAnalyzingPlant(false);
    }
  };

  const isDeadlineInPast = (deadline?: string): boolean => {
    if (!deadline) return false;
    
    // Parse Norwegian date format (DD.MM.YYYY)
    const parts = deadline.split('.');
    if (parts.length !== 3) return false;
    
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // JS months are 0-indexed
    const year = parseInt(parts[2], 10);
    
    const deadlineDate = new Date(year, month, day);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return deadlineDate < today;
  };

  const handleMapRightClick = useCallback((e: any) => {
    const { lngLat } = e;
    setRightClickCoords({
      lat: lngLat.lat,
      lon: lngLat.lng
    });
    setShowAddDCModal(true);
  }, []);

  const handleAddDataCenter = async (data: DataCenterCreate) => {
    try {
      await createDataCenter(data);
      await onDataCenterAdded();
      setShowAddDCModal(false);
      setRightClickCoords(null);
    } catch (error) {
      console.error('Error creating data center:', error);
      throw error; // Let modal handle the error
    }
  };

  const handleDeleteDataCenter = async (dc: DataCenter) => {
    if (confirm(`Delete data center "${dc.name}"?`)) {
      try {
        await deleteDataCenter(dc.id);
        await onDataCenterDeleted();
        setSelectedDataCenter(null);
      } catch (error) {
        console.error('Error deleting data center:', error);
        alert('Failed to delete data center');
      }
    }
  };

  // Create connection lines GeoJSON between data centers and hydro plants
  const connectionLinesGeoJSON = useMemo(() => {
    if (dataCenters.length === 0) return null;

    const allPlants = [...plants, ...underConstructionPlants];
    const features: any[] = [];

    // For each data center, create a line to each connected hydro plant
    dataCenters.forEach(dc => {
      // Use the new hydro_connections array if available
      if (dc.hydro_connections && dc.hydro_connections.length > 0) {
        dc.hydro_connections.forEach(connection => {
          const hydroPlant = allPlants.find(p => p.id === connection.hydro_id);
          
          if (hydroPlant) {
            features.push({
              type: 'Feature' as const,
              properties: {
                dc_name: dc.name,
                hydro_name: connection.hydro_name,
                allocated_capacity: connection.allocated_capacity_mw,
                distance_km: connection.distance_km
              },
              geometry: {
                type: 'LineString' as const,
                coordinates: [
                  [dc.coordinates.lon, dc.coordinates.lat],
                  [hydroPlant.coordinates.lon, hydroPlant.coordinates.lat]
                ]
              }
            });
          }
        });
      } else {
        // Fallback to legacy single connection for backward compatibility
        const hydroPlant = allPlants.find(p => p.id === dc.nearest_hydro_id);
        
        if (hydroPlant) {
          features.push({
            type: 'Feature' as const,
            properties: {
              dc_name: dc.name,
              hydro_name: dc.nearest_hydro_name,
              allocated_capacity: dc.capacity_mw,
              distance_km: dc.distance_to_hydro_km
            },
            geometry: {
              type: 'LineString' as const,
              coordinates: [
                [dc.coordinates.lon, dc.coordinates.lat],
                [hydroPlant.coordinates.lon, hydroPlant.coordinates.lat]
              ]
            }
          });
        }
      }
    });

    return {
      type: 'FeatureCollection' as const,
      features
    };
  }, [dataCenters, plants, underConstructionPlants]);

  // Create circle GeoJSON for search radius
  const radiusGeoJSON = searchCenter && searchRadius ? {
    type: 'FeatureCollection' as const,
    features: [{
      type: 'Feature' as const,
      properties: {},
      geometry: {
        type: 'Point' as const,
        coordinates: searchCenter
      }
    }]
  } : null;

  // Map style based on current layer and theme
  const getMapStyle = () => {
    // Different styles for different layers
    if (currentLayer === 'satellite') {
      return 'mapbox://styles/mapbox/satellite-streets-v12';
    }
    
    // For temperature and precipitation, we'll use overlay layers
    // So use a simple base style
    if (currentLayer === 'temperature' || currentLayer === 'precipitation') {
      return theme === 'dark'
        ? 'mapbox://styles/mapbox/dark-v10'
        : 'mapbox://styles/mapbox/light-v10';
    }
    
    // Default style
    return theme === 'dark' 
      ? 'mapbox://styles/mapbox/dark-v10'
      : 'mapbox://styles/mapbox/streets-v11';
  };

  const mapStyle = getMapStyle();

  // Check if Mapbox token is available
  if (!MAPBOX_TOKEN || MAPBOX_TOKEN === 'pk.your_token_here') {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-center p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Mapbox Token Required
          </h3>
          <p className="text-gray-700 dark:text-gray-200 mb-4 text-xl">
            Please set a valid Mapbox token in frontend/.env
          </p>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Get a free token at <a href="https://mapbox.com" target="_blank" className="text-blue-600 dark:text-blue-400 hover:underline">mapbox.com</a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      {/* Layer Switcher */}
      <LayerSwitcher currentLayer={currentLayer} onLayerChange={setCurrentLayer} />

      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        onContextMenu={handleMapRightClick}
        mapStyle={mapStyle}
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        attributionControl={false}
      >
        <NavigationControl position="top-right" />

        {/* Temperature Overlay - Using OpenWeatherMap */}
        {currentLayer === 'temperature' && (
          <Source
            id="temperature-tiles"
            type="raster"
            tiles={[
              // Get free API key at: https://openweathermap.org/api
              // Add to frontend/.env: VITE_OPENWEATHER_API_KEY=your_key
              `https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${import.meta.env.VITE_OPENWEATHER_API_KEY ?? ''}`
            ]}
            tileSize={256}
          >
            <Layer
              id="temperature-layer"
              type="raster"
              paint={{
                'raster-opacity': 0.6
              }}
            />
          </Source>
        )}

        {/* Precipitation/Terrain Overlay - Using MapTiler Terrain RGB (shows elevation with colors) */}
        {currentLayer === 'precipitation' && (
          <Source
            id="terrain-rgb-tiles"
            type="raster"
            tiles={[
              `https://api.maptiler.com/tiles/terrain-rgb/{z}/{x}/{y}.png?key=xV0hMP1B1Nk0uxQp8YpJ`
            ]}
            tileSize={256}
          >
            <Layer
              id="terrain-rgb-layer"
              type="raster"
              paint={{
                'raster-opacity': 0.4
              }}
            />
          </Source>
        )}

        {/* Connection lines between data centers and hydro plants */}
        {connectionLinesGeoJSON && (
          <Source id="dc-connections" type="geojson" data={connectionLinesGeoJSON}>
            <Layer
              id="dc-connection-lines"
              type="line"
              paint={{
                'line-color': '#8b5cf6',
                'line-width': [
                  'interpolate',
                  ['linear'],
                  ['get', 'allocated_capacity'],
                  0, 2,    // 0 MW = 2px width
                  10, 3,   // 10 MW = 3px width
                  50, 5,   // 50 MW = 5px width
                  100, 7   // 100+ MW = 7px width
                ],
                'line-opacity': 0.8
              }}
            />
          </Source>
        )}

        {/* Search radius circle */}
        {radiusGeoJSON && (
          <>
            <Source id="search-radius" type="geojson" data={radiusGeoJSON}>
              <Layer
                id="radius-circle"
                type="circle"
                paint={{
                  'circle-radius': {
                    stops: [
                      [0, 0],
                      [20, searchRadius! * 1000 * 0.0075] // Approximate conversion
                    ],
                    base: 2
                  },
                  'circle-color': '#3b82f6',
                  'circle-opacity': 0.1,
                  'circle-stroke-width': 2,
                  'circle-stroke-color': '#3b82f6',
                  'circle-stroke-opacity': 0.5
                }}
              />
            </Source>
            
            {/* Center marker */}
            <Marker
              longitude={searchCenter[0]}
              latitude={searchCenter[1]}
              anchor="center"
            >
              <div className="w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow-lg" />
            </Marker>
          </>
        )}

        {/* Recommended location markers */}
        {recommendedLocations.map((location, index) => (
          <Marker
            key={`recommended-${location.name}-${index}`}
            longitude={location.location.lon}
            latitude={location.location.lat}
            anchor="center"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              onRecommendedLocationClick(location);
            }}
          >
            <div className="cursor-pointer transition-all hover:scale-125 group">
              <div className="relative">
                {/* Star icon with color based on grid status */}
                <div className={`w-10 h-10 rounded-full shadow-xl border-3 border-white flex items-center justify-center ${
                  location.grid_status === 'excellent' ? 'bg-blue-500' :
                  location.grid_status === 'ok' ? 'bg-green-500' :
                  location.grid_status === 'limited' ? 'bg-orange-500' :
                  location.grid_status === 'challenging' ? 'bg-yellow-500' : 'bg-red-500'
                }`}>
                  <Star className="text-white fill-white" size={24} />
                </div>
                
                {/* Rank badge */}
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-600 text-white text-xs font-bold rounded-full flex items-center justify-center border-2 border-white">
                  {index + 1}
                </div>
              </div>
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                <div className="bg-gray-900 dark:bg-gray-800 text-white text-lg rounded py-3 px-4 whitespace-nowrap shadow-xl border border-gray-700">
                  <div className="font-semibold mb-1 text-xl">{location.name}</div>
                  <div className="text-lg">{location.total_capacity_mw.toFixed(0)} MW capacity</div>
                  <div className="text-gray-200 dark:text-gray-300 text-base">Click to analyze</div>
                </div>
              </div>
            </div>
          </Marker>
        ))}

        {/* Plant markers */}
        {visiblePlants.map((plant) => (
          <Marker
            key={`${plant.id}-${plant.status}`}
            longitude={plant.coordinates.lon}
            latitude={plant.coordinates.lat}
            anchor="center"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              handleMarkerClick(plant);
            }}
          >
            <div
              className={`cursor-pointer transition-all hover:scale-125 group ${
                selectedPlant?.id === plant.id ? 'scale-150 z-10' : ''
              }`}
              style={{
                width: plant.status === 'under_construction' ? getPlantSize(plant.maksYtelse_MW) * 2.1 : getPlantSize(plant.maksYtelse_MW) * 1.4,
                height: plant.status === 'under_construction' ? getPlantSize(plant.maksYtelse_MW) * 2.1 : getPlantSize(plant.maksYtelse_MW) * 1.4,
              }}
            >
              <div
                className="w-full h-full rounded-full shadow-xl border-3 border-white flex items-center justify-center relative"
                style={{ 
                  backgroundColor: plant.status === 'under_construction' ? '#fbbf24' : getPlantColor(plant),
                  boxShadow: plant.status === 'under_construction' ? '0 0 20px rgba(251, 191, 36, 0.6)' : undefined
                }}
              >
                {plant.status === 'under_construction' ? (
                  <Construction className="text-white drop-shadow-md" size={getPlantSize(plant.maksYtelse_MW) * 0.9} />
                ) : (
                  <Zap className="text-white drop-shadow-md" size={getPlantSize(plant.maksYtelse_MW) * 0.6} />
                )}
              </div>
              
              {/* Tooltip on hover */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                <div className="bg-gray-900 dark:bg-gray-800 text-white text-lg rounded py-2 px-3 whitespace-nowrap border border-gray-700">
                  <div className="font-semibold text-xl">{plant.name}</div>
                  <div className="text-lg">{plant.maksYtelse_MW.toFixed(1)} MW</div>
                  {plant.status === 'under_construction' && (
                    <div className="text-yellow-300 dark:text-yellow-200 text-lg">Under Construction</div>
                  )}
                  {plant.status === 'under_construction' && plant.deadline && (
                    <div className="text-yellow-300 dark:text-yellow-200 text-base">Deadline: {plant.deadline}</div>
                  )}
                </div>
              </div>
            </div>
          </Marker>
        ))}

        {/* Data Center markers */}
        {dataCenters.map((dc) => (
          <Marker
            key={dc.id}
            longitude={dc.coordinates.lon}
            latitude={dc.coordinates.lat}
            anchor="center"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              setSelectedDataCenter(dc);
            }}
          >
            <div className="cursor-pointer transition-all hover:scale-125 group">
              <div className="w-11 h-11 bg-purple-600 rounded-lg shadow-xl border-2 border-white flex items-center justify-center">
                <Server className="text-white" size={25} />
              </div>
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                <div className="bg-gray-900 dark:bg-gray-800 text-white text-lg rounded py-2 px-3 whitespace-nowrap border border-gray-700">
                  <div className="font-semibold text-xl">{dc.name}</div>
                  <div className="text-lg">{dc.capacity_mw} MW</div>
                  <div className="text-purple-300 dark:text-purple-200 text-lg">Data Center</div>
                </div>
              </div>
            </div>
          </Marker>
        ))}

        {/* Popup for selected plant */}
        {selectedPlant && (
          <Popup
            longitude={selectedPlant.coordinates.lon}
            latitude={selectedPlant.coordinates.lat}
            anchor="bottom"
            onClose={onClosePlant}
            closeButton={false}
            maxWidth="480px"
          >
            <div className="p-5 min-w-[420px]">
              {/* Header with close button */}
              <div className="flex justify-between items-start mb-3 pb-3 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white text-2xl">Plant Details</h3>
                  {selectedPlant.status === 'under_construction' && (
                    <span className="inline-block mt-2 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-lg rounded-full">
                      Under Construction
                    </span>
                  )}
                </div>
                <button
                  onClick={onClosePlant}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white transition-colors"
                >
                  <X size={26} />
                </button>
              </div>
              
              {/* Plant details */}
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Name</span>
                  <div className="font-medium text-gray-900 dark:text-white text-xl">{selectedPlant.name}</div>
                </div>
                
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Capacity</span>
                  <div className="font-medium text-gray-900 dark:text-white">
                    <span className="text-2xl font-bold">{selectedPlant.maksYtelse_MW.toFixed(2)}</span> <span className="text-xl">MW</span>
                  </div>
                </div>
                
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Type</span>
                  <div className="font-medium text-gray-900 dark:text-white text-xl">{selectedPlant.type}</div>
                </div>
                
                {selectedPlant.status === 'under_construction' && selectedPlant.deadline && (
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-gray-600 dark:text-gray-300 text-lg">Construction Deadline</span>
                    <div className="font-semibold text-yellow-600 dark:text-yellow-300 text-xl">
                      {selectedPlant.deadline}
                    </div>
                    {selectedPlant.kdbNr && (
                      <a
                        href={`https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id=${selectedPlant.kdbNr}&type=V-1`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lg text-blue-600 dark:text-blue-400 hover:underline mt-2 flex items-center gap-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        View on NVE website <ExternalLink size={18} />
                      </a>
                    )}
                  </div>
                )}
                
                {selectedPlant.status === 'under_construction' && (
                  <div className="pt-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAnalyzePlant();
                      }}
                      disabled={analyzingPlant}
                      className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white text-xl font-medium rounded-md transition-all flex items-center justify-center gap-2 shadow-md"
                    >
                      {analyzingPlant ? (
                        <>
                          <Loader2 size={20} className="animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Brain size={20} />
                          Analyze with AI
                        </>
                      )}
                    </button>
                    <p className="text-lg text-gray-600 dark:text-gray-300 mt-2 text-center">
                      Search for latest deadline info
                    </p>
                  </div>
                )}
                
                {selectedPlant.distance_km !== undefined && (
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-gray-600 dark:text-gray-300 text-lg">Distance</span>
                    <div className="font-medium text-gray-900 dark:text-white text-xl">
                      {selectedPlant.distance_km.toFixed(2)} km
                    </div>
                  </div>
                )}
                
                {selectedPlant.owner && (
                  <div>
                    <span className="text-gray-600 dark:text-gray-300 text-lg">Owner</span>
                    <div className="font-medium text-gray-900 dark:text-white text-xl">{selectedPlant.owner}</div>
                  </div>
                )}
                
                {selectedPlant.kommune && (
                  <div>
                    <span className="text-gray-600 dark:text-gray-300 text-lg">Municipality</span>
                    <div className="font-medium text-gray-900 dark:text-white text-xl">{selectedPlant.kommune}</div>
                  </div>
                )}
              </div>
            </div>
          </Popup>
        )}

        {/* Popup for selected data center */}
        {selectedDataCenter && (
          <Popup
            longitude={selectedDataCenter.coordinates.lon}
            latitude={selectedDataCenter.coordinates.lat}
            anchor="bottom"
            onClose={() => setSelectedDataCenter(null)}
            closeButton={false}
            maxWidth="420px"
          >
            <div className="p-5 min-w-[380px]">
              <div className="flex justify-between items-start mb-3 pb-3 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-white text-2xl flex items-center gap-2">
                  <Server size={26} className="text-purple-600" />
                  Data Center
                </h3>
                <button
                  onClick={() => setSelectedDataCenter(null)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white transition-colors"
                >
                  <X size={26} />
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Name</span>
                  <div className="font-medium text-gray-900 dark:text-white text-xl">{selectedDataCenter.name}</div>
                </div>
                
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Capacity</span>
                  <div className="font-medium text-gray-900 dark:text-white">
                    <span className="text-2xl font-bold">{selectedDataCenter.capacity_mw}</span> <span className="text-xl">MW</span>
                  </div>
                </div>
                
                <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                  <span className="text-gray-600 dark:text-gray-300 text-lg mb-2 block">
                    Connected Plants ({selectedDataCenter.hydro_connections?.length || 1})
                  </span>
                  <div className="space-y-3 max-h-40 overflow-y-auto">
                    {selectedDataCenter.hydro_connections && selectedDataCenter.hydro_connections.length > 0 ? (
                      selectedDataCenter.hydro_connections.map((conn, idx) => (
                        <div key={idx} className="bg-purple-50 dark:bg-purple-900/30 p-3 rounded text-lg">
                          <div className="font-medium text-purple-700 dark:text-purple-300">
                            {conn.hydro_name}
                          </div>
                          <div className="text-gray-700 dark:text-gray-300 mt-1">
                            {conn.allocated_capacity_mw} MW • {conn.distance_km} km away
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="bg-purple-50 dark:bg-purple-900/30 p-3 rounded text-lg">
                        <div className="font-medium text-purple-700 dark:text-purple-300">
                          {selectedDataCenter.nearest_hydro_name}
                        </div>
                        <div className="text-gray-700 dark:text-gray-300 mt-1">
                          {selectedDataCenter.distance_to_hydro_km} km away
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Nearest City</span>
                  <div className="font-medium text-gray-900 dark:text-white text-xl">
                    {selectedDataCenter.nearest_city}
                  </div>
                  <div className="text-lg text-gray-600 dark:text-gray-300">
                    {selectedDataCenter.distance_to_city_km} km away
                  </div>
                </div>
                
                <div>
                  <span className="text-gray-600 dark:text-gray-300 text-lg">Power Zone</span>
                  <div className="font-medium text-gray-900 dark:text-white text-xl">
                    {selectedDataCenter.power_zone_id}
                  </div>
                </div>
                
                <button
                  onClick={() => handleDeleteDataCenter(selectedDataCenter)}
                  className="w-full mt-3 px-4 py-3 bg-red-600 hover:bg-red-700 text-white text-xl font-medium rounded transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 size={20} />
                  Delete Data Center
                </button>
              </div>
            </div>
          </Popup>
        )}
      </Map>

      {/* Plant View Mode Control Panel - Top Right */}
      <div className="absolute top-4 right-4 bg-white dark:bg-gray-800 p-5 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold text-xl mb-4 text-gray-900 dark:text-white flex items-center gap-2">
          <Construction size={24} />
          Plant View Options
        </h3>
        <div className="flex flex-col gap-3">
          <button
            onClick={() => onPlantViewModeChange('existing')}
            className={`px-5 py-3 text-xl font-medium rounded-md transition-all ${
              plantViewMode === 'existing'
                ? 'bg-green-600 text-white shadow-lg scale-105'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <div className="flex items-center gap-2">
              <Zap size={20} />
              Existing Plants Only
            </div>
          </button>
          <button
            onClick={() => onPlantViewModeChange('under_construction')}
            className={`px-5 py-3 text-xl font-medium rounded-md transition-all ${
              plantViewMode === 'under_construction'
                ? 'bg-yellow-500 text-white shadow-lg scale-105'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <div className="flex items-center gap-2">
              <Construction size={20} />
              Under Construction
            </div>
          </button>
          <button
            onClick={() => onPlantViewModeChange('both')}
            className={`px-5 py-3 text-xl font-medium rounded-md transition-all ${
              plantViewMode === 'both'
                ? 'bg-blue-600 text-white shadow-lg scale-105'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <div className="flex items-center gap-2">
              <Zap size={18} />
              <Construction size={18} />
              Show All Plants
            </div>
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white dark:bg-gray-800 p-5 rounded-lg shadow-lg max-w-md">
        <h3 className="font-semibold text-xl mb-3 text-gray-900 dark:text-white">Legend</h3>
        
        {recommendedLocations.length > 0 && (
          <>
            <div className="mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-1">
                <Star className="text-green-500 fill-green-500" size={18} />
                <span className="text-gray-800 dark:text-gray-200 text-lg font-medium">Recommended Sites</span>
              </div>
            </div>
          </>
        )}
        
        <div className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Hydropower Plants:</div>
        <div className="space-y-2 text-lg mb-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full shadow-md" style={{ backgroundColor: '#10b981' }}></div>
            <span className="text-gray-800 dark:text-gray-200">Mikro (&lt;1 MW)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full shadow-md" style={{ backgroundColor: '#fb923c' }}></div>
            <span className="text-gray-800 dark:text-gray-200">Mini (1-10 MW)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full shadow-md" style={{ backgroundColor: '#f87171' }}></div>
            <span className="text-gray-800 dark:text-gray-200">Stor (&gt;10 MW)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full shadow-md" style={{ backgroundColor: '#fbbf24', boxShadow: '0 0 10px rgba(251, 191, 36, 0.6)' }}></div>
            <span className="text-gray-800 dark:text-gray-200">Under Construction</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full shadow-md" style={{ backgroundColor: '#cbd5e1' }}></div>
            <span className="text-gray-800 dark:text-gray-200">Planned</span>
          </div>
        </div>
        
        {dataCenters.length > 0 && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Data Centers:</div>
            <div className="space-y-2 text-lg">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 bg-purple-600 rounded-lg shadow-md flex items-center justify-center">
                  <Server size={14} className="text-white" />
                </div>
                <span className="text-gray-800 dark:text-gray-200">Data Center</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-0.5 border-t-2 border-dashed border-purple-600"></div>
                <span className="text-gray-800 dark:text-gray-200">Connection</span>
              </div>
            </div>
            <div className="mt-3 p-3 bg-purple-50 dark:bg-purple-900/30 rounded text-lg text-purple-800 dark:text-purple-200">
              Right-click map to add
            </div>
          </div>
        )}

        {/* Temperature Layer Legend */}
        {currentLayer === 'temperature' && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Temperature:</div>
            <div className="flex items-center gap-1 mb-2">
              <div className="flex-1 h-4 rounded" style={{
                background: 'linear-gradient(to right, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000)'
              }}></div>
            </div>
            <div className="flex justify-between text-base text-gray-700 dark:text-gray-300">
              <span>-40°C</span>
              <span>0°C</span>
              <span>+40°C</span>
            </div>
            <p className="text-base text-gray-600 dark:text-gray-300 mt-2 italic">
              OpenWeatherMap data
            </p>
          </div>
        )}

        {/* Elevation Layer Legend */}
        {currentLayer === 'precipitation' && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Elevation:</div>
            <div className="flex items-center gap-1 mb-2">
              <div className="flex-1 h-4 rounded" style={{
                background: 'linear-gradient(to right, #2E8B57, #FFD700, #8B4513, #FFFFFF)'
              }}></div>
            </div>
            <div className="flex justify-between text-base text-gray-700 dark:text-gray-300">
              <span>Sea Level</span>
              <span>Hills</span>
              <span>High</span>
            </div>
            <p className="text-base text-gray-600 dark:text-gray-300 mt-2 italic">
              Useful for hydropower site analysis
            </p>
          </div>
        )}
      </div>

      {/* Analysis Modal */}
      {showAnalysisModal && analysisResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-8 flex justify-between items-start z-10">
              <div>
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                  <Brain size={30} className="text-purple-600" />
                  AI Analysis Results
                </h3>
                <p className="text-xl text-gray-700 dark:text-gray-300 mt-2">{analysisResult.plant_name}</p>
              </div>
              <button
                onClick={() => setShowAnalysisModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-white transition-colors"
              >
                <X size={30} />
              </button>
            </div>
            
            <div className="p-8 space-y-8">
              {/* Summary */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/30 dark:to-blue-900/30 p-5 rounded-lg border border-purple-200 dark:border-purple-700">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2 text-2xl">
                  <AlertCircle size={24} />
                  Summary
                </h4>
                <p className="text-gray-800 dark:text-gray-200 text-xl leading-relaxed">
                  {analysisResult.summary}
                </p>
              </div>

              {/* Sources */}
              {analysisResult.sources.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2 text-2xl">
                    <Search size={24} />
                    Sources Analyzed
                  </h4>
                  <div className="space-y-4">
                    {analysisResult.sources.map((source, index) => (
                      <div key={index} className="bg-gray-50 dark:bg-gray-700/50 p-5 rounded-lg border border-gray-200 dark:border-gray-600">
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-2 text-xl"
                        >
                          {source.title}
                          <span className="text-lg">↗</span>
                        </a>
                        <p className="text-lg text-gray-700 dark:text-gray-300 mt-2 break-all">
                          {source.url}
                        </p>
                        {source.snippet && (
                          <p className="text-xl text-gray-700 dark:text-gray-200 mt-3">
                            {source.snippet}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex gap-4 pt-5 border-t border-gray-200 dark:border-gray-700">
                {analysisResult.links.map((link, index) => (
                  <a
                    key={index}
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white text-xl font-medium rounded-md transition-colors text-center"
                  >
                    Open Source {index + 1}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Data Center Modal */}
      {showAddDCModal && rightClickCoords && (
        <AddDataCenterModal
          isOpen={showAddDCModal}
          onClose={() => {
            setShowAddDCModal(false);
            setRightClickCoords(null);
          }}
          onSubmit={handleAddDataCenter}
          initialLat={rightClickCoords.lat}
          initialLon={rightClickCoords.lon}
        />
      )}
    </div>
  );
}


