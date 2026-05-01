import { useState, useEffect } from 'react';
import { Search, MapPin, Zap, TrendingUp, AlertCircle, Factory, Loader2, X, Construction } from 'lucide-react';
import type { HydropowerPlant, CapacityEstimate, RecommendedLocation } from '../types';
import { formatNumber, getGridConstraintColor } from '../utils';
import type { PlantViewMode } from '../App';

interface SidebarProps {
  estimate: CapacityEstimate | null;
  selectedPlant: HydropowerPlant | null;
  onSearch: (lat: number, lon: number, radius: number) => void;
  onClose: () => void;
  loading: boolean;
  recommendedLocations: RecommendedLocation[];
  onShowRecommendations: (minCapacity?: number) => void;
  onLocationClick: (location: RecommendedLocation) => void;
  plantViewMode: PlantViewMode;
  onPlantViewModeChange: (mode: PlantViewMode) => void;
  underConstructionPlants: HydropowerPlant[];
  timelineMonths: number;
  onTimelineChange: (months: number) => void;
}

export default function Sidebar({ 
  estimate, 
  selectedPlant, 
  onSearch, 
  onClose, 
  loading,
  recommendedLocations,
  onShowRecommendations,
  onLocationClick,
  plantViewMode,
  onPlantViewModeChange,
  underConstructionPlants,
  timelineMonths,
  onTimelineChange
}: SidebarProps) {
  const [searchLat, setSearchLat] = useState('60.391');
  const [searchLon, setSearchLon] = useState('5.324');
  const [searchRadius, setSearchRadius] = useState('50');
  const [dataCenterSize, setDataCenterSize] = useState('');
  const [filterLoading, setFilterLoading] = useState(false);

  const handleSearch = () => {
    const lat = parseFloat(searchLat);
    const lon = parseFloat(searchLon);
    const radius = parseFloat(searchRadius);

    if (!isNaN(lat) && !isNaN(lon) && !isNaN(radius)) {
      onSearch(lat, lon, radius);
    }
  };

  const handleFilterByCapacity = () => {
    const capacity = parseFloat(dataCenterSize);
    if (!isNaN(capacity) && capacity > 0) {
      setFilterLoading(true);
      // Call the recommendations function with the capacity requirement
      onShowRecommendations(capacity);
      setFilterLoading(false);
    }
  };

  // Quick search presets
  const presets = [
    { name: 'Bergen', lat: 60.391, lon: 5.324 },
    { name: 'Oslo', lat: 59.911, lon: 10.757 },
    { name: 'Trondheim', lat: 63.431, lon: 10.395 },
    { name: 'Tromsø', lat: 69.649, lon: 18.956 },
    { name: 'Ål', lat: 60.632, lon: 8.566 },
  ];

  return (
    <div className="w-full md:w-96 h-full bg-white dark:bg-gray-900 shadow-xl overflow-y-auto custom-scrollbar flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-900 z-10">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Norway Power Grid
        </h1>
      </div>

      {/* Quick Actions */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="space-y-4">

          {/* Data Center Size Input */}
          <div>
            <label htmlFor="dc-size" className="block text-xl font-medium text-gray-800 dark:text-gray-200 mb-3">
              Data Center Capacity (MW)
            </label>
            <input
              id="dc-size"
              type="number"
              min="1"
              step="1"
              value={dataCenterSize}
              onChange={(e) => setDataCenterSize(e.target.value)}
              placeholder="e.g., 50"
              className="w-full px-4 py-3 text-lg border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Timeline Slider */}
          <div>
            <label className="block text-xl font-medium text-gray-800 dark:text-gray-200 mb-3">
              Server Build Plan Timeline
            </label>
            <div className="space-y-3">
              <input
                type="range"
                min="6"
                max="120"
                value={timelineMonths}
                onChange={(e) => onTimelineChange(parseInt(e.target.value))}
                className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-lg text-gray-700 dark:text-gray-300">
                <span>6 months</span>
                <span className="font-semibold text-blue-600 dark:text-blue-400">
                  {timelineMonths < 12 
                    ? `${timelineMonths} months` 
                    : `${(timelineMonths / 12).toFixed(1)} years`}
                </span>
                <span>10 years</span>
              </div>
              <p className="text-lg text-gray-600 dark:text-gray-300 italic">
                Shows plants completing within selected timeline
              </p>
            </div>
          </div>

          {/* Filter Button */}
          <button
            onClick={handleFilterByCapacity}
            disabled={!dataCenterSize || filterLoading}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white text-lg font-semibold rounded-lg transition-all shadow-md flex items-center justify-center gap-2"
          >
            {filterLoading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Filtering...
              </>
            ) : (
              <>
                <Search size={20} />
                Filter Suitable Locations
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recommended Locations */}
      {recommendedLocations.length > 0 && (
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
          <h3 className="font-semibold text-xl mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <MapPin size={22} className="text-blue-600 dark:text-blue-400" />
            Suitable Locations ({recommendedLocations.length})
          </h3>
          {dataCenterSize && (
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
              Based on {dataCenterSize} MW capacity requirement
            </p>
          )}
          <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
            {recommendedLocations.map((location, index) => (
              <button
                key={index}
                onClick={() => onLocationClick(location)}
                className="w-full text-left bg-white dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600 transition-all shadow-sm hover:shadow-md"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="font-semibold text-lg text-gray-900 dark:text-white">
                    {location.name}
                  </div>
                  <div className={`px-2 py-1 text-sm rounded ${
                    location.status_color === 'blue' || location.status_color === 'green' 
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                      : location.status_color === 'orange' || location.status_color === 'yellow'
                      ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                      : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                  }`}>
                    Score: {location.suitability_score}
                  </div>
                </div>
                <div className="space-y-1 text-base text-gray-700 dark:text-gray-300">
                  <div className="flex justify-between">
                    <span>Available Capacity:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {location.total_capacity_mw.toFixed(1)} MW
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Nearby Plants:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {location.nearby_plants}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Power Zone:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {location.power_zone}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Zone Headroom:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {location.zone_headroom_mw.toFixed(0)} MW
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {estimate && !loading && (
        <div className="flex-1 p-6 space-y-6">
          {/* Grid Constraint Status */}
          <div className={`p-5 rounded-lg ${
            estimate.grid_constraint.status === 'ok' 
              ? 'bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800'
              : estimate.grid_constraint.status === 'limited'
              ? 'bg-orange-50 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-800'
              : 'bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800'
          }`}>
            <div className="flex items-start gap-4">
              <div className={`mt-1 w-4 h-4 rounded-full ${getGridConstraintColor(estimate.grid_constraint.status)}`} />
              <div className="flex-1">
                <h3 className="font-semibold text-xl mb-2 text-gray-900 dark:text-white">
                  {estimate.grid_constraint.status.toUpperCase()} - Grid Status
                </h3>
                <p className="text-xl text-gray-800 dark:text-gray-200">
                  {estimate.grid_constraint.description}
                </p>
              </div>
            </div>
          </div>

          {/* Capacity Summary */}
          <div className="grid grid-cols-2 gap-5">
            <div className="bg-gray-50 dark:bg-gray-800 p-5 rounded-lg">
              <div className="flex items-center gap-2 mb-3 text-gray-700 dark:text-gray-300">
                <Zap size={20} />
                <span className="text-lg font-medium">Local Capacity</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {formatNumber(estimate.total_nearby_capacity_MW, 0)}
                <span className="text-xl font-normal text-gray-600 dark:text-gray-400 ml-1">MW</span>
              </div>
              <div className="text-lg text-gray-700 dark:text-gray-300 mt-2">
                {estimate.nearby_plants_count} plants
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-800 p-5 rounded-lg">
              <div className="flex items-center gap-2 mb-3 text-gray-700 dark:text-gray-300">
                <TrendingUp size={20} />
                <span className="text-lg font-medium">Zone Headroom</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {formatNumber(estimate.power_zone.headroom_MW, 0)}
                <span className="text-xl font-normal text-gray-600 dark:text-gray-400 ml-1">MW</span>
              </div>
              <div className="text-lg text-gray-700 dark:text-gray-300 mt-2">
                {estimate.power_zone.name}
              </div>
            </div>
          </div>

          {/* Power Zone Details */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-5">
            <h3 className="font-semibold text-xl mb-4 text-gray-900 dark:text-white flex items-center gap-2">
              <Factory size={20} />
              Power Zone: {estimate.power_zone.id}
            </h3>
            <div className="space-y-3 text-lg">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">Generation:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {formatNumber(estimate.power_zone.total_generation_MW, 0)} MW
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">Consumption:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {formatNumber(estimate.power_zone.consumption_MW, 0)} MW
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">Export:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {formatNumber(estimate.power_zone.export_MW, 0)} MW
                </span>
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-5">
            <h3 className="font-semibold text-xl mb-3 text-gray-900 dark:text-white flex items-center gap-2">
              <AlertCircle size={20} />
              Recommendation
            </h3>
            <p className="text-xl text-gray-800 dark:text-gray-200">
              {estimate.recommendation}
            </p>
          </div>

          {/* Nearby Plants List */}
          {estimate.plants.length > 0 && (
            <div>
              <h3 className="font-semibold text-xl mb-4 text-gray-900 dark:text-white">
                Nearby Plants (Top {estimate.plants.length})
              </h3>
              <div className="space-y-3">
                {estimate.plants.slice(0, 10).map((plant) => (
                  <div
                    key={plant.id}
                    className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg text-lg"
                  >
                    <div className="font-medium text-gray-900 dark:text-white">{plant.name}</div>
                    <div className="flex justify-between mt-2 text-lg text-gray-700 dark:text-gray-300">
                      <span>{plant.maksYtelse_MW.toFixed(1)} MW</span>
                      <span>{plant.distance_km?.toFixed(1)} km away</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Selected Plant Details */}
      {selectedPlant && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-800">
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-semibold text-xl text-gray-900 dark:text-white flex items-center gap-2">
              Plant Details
              {selectedPlant.status === 'under_construction' && (
                <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-lg rounded-full">
                  Under Construction
                </span>
              )}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
            >
              <X size={26} />
            </button>
          </div>
          <div className="space-y-3 text-lg">
            <div>
              <span className="text-gray-700 dark:text-gray-300">Name:</span>
              <div className="font-medium text-gray-900 dark:text-white">{selectedPlant.name}</div>
            </div>
            <div>
              <span className="text-gray-700 dark:text-gray-300">Capacity:</span>
              <div className="font-medium text-gray-900 dark:text-white">
                {selectedPlant.maksYtelse_MW.toFixed(2)} MW
              </div>
            </div>
            <div>
              <span className="text-gray-700 dark:text-gray-300">Type:</span>
              <div className="font-medium text-gray-900 dark:text-white">{selectedPlant.type}</div>
            </div>
            {selectedPlant.status === 'under_construction' && selectedPlant.deadline && (
              <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                <span className="text-gray-700 dark:text-gray-300">Construction Deadline:</span>
                <div className="font-semibold text-yellow-600 dark:text-yellow-300 text-xl">
                  {selectedPlant.deadline}
                </div>
                {selectedPlant.kdbNr && (
                  <a
                    href={`https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id=${selectedPlant.kdbNr}&type=V-1`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-lg text-blue-600 dark:text-blue-400 hover:underline mt-2 block"
                  >
                    View on NVE website →
                  </a>
                )}
              </div>
            )}
            {selectedPlant.year && (
              <div>
                <span className="text-gray-700 dark:text-gray-300">Year:</span>
                <div className="font-medium text-gray-900 dark:text-white">{selectedPlant.year}</div>
              </div>
            )}
            {selectedPlant.owner && (
              <div>
                <span className="text-gray-700 dark:text-gray-300">Owner:</span>
                <div className="font-medium text-gray-900 dark:text-white">{selectedPlant.owner}</div>
              </div>
            )}
            {selectedPlant.kommune && (
              <div>
                <span className="text-gray-700 dark:text-gray-300">Municipality:</span>
                <div className="font-medium text-gray-900 dark:text-white">{selectedPlant.kommune}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && !estimate && (
        <div className="p-6 space-y-4">
          <div className="h-24 skeleton rounded-lg"></div>
          <div className="h-32 skeleton rounded-lg"></div>
          <div className="h-48 skeleton rounded-lg"></div>
        </div>
      )}
    </div>
  );
}

