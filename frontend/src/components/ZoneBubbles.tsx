import { useEffect, useState } from 'react';
import { getZones } from '../api';
import type { PowerZone } from '../types';

interface ZoneBubblesProps {
  includeDataCenters: boolean;
  refreshTrigger?: number; // Increment this to force refresh
}

export default function ZoneBubbles({ includeDataCenters, refreshTrigger }: ZoneBubblesProps) {
  const [zones, setZones] = useState<Record<string, PowerZone>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const zonesData = await getZones(includeDataCenters);
        setZones(zonesData);
      } catch (error) {
        console.error('Error fetching zones:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, [includeDataCenters, refreshTrigger]);

  if (loading) {
    return (
      <div className="fixed top-4 right-4 z-10">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <p className="text-xl text-gray-600 dark:text-gray-300">Loading zones...</p>
        </div>
      </div>
    );
  }

  const getHeadroomColor = (headroom: number): string => {
    if (headroom > 300) return 'bg-green-500';
    if (headroom > 150) return 'bg-blue-500';
    if (headroom > 100) return 'bg-yellow-500';
    if (headroom > 50) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getHeadroomStatus = (headroom: number): string => {
    if (headroom > 300) return 'Excellent';
    if (headroom > 150) return 'Good';
    if (headroom > 100) return 'Moderate';
    if (headroom > 50) return 'Limited';
    return 'Critical';
  };

  const zoneArray = Object.values(zones);

  return (
    <div className="fixed top-64 right-4 z-10 space-y-3 max-w-sm">
      {/* Zone Bubbles */}
      <div className="space-y-3">
        {zoneArray.map((zone) => {
          const headroomColor = getHeadroomColor(zone.headroom_MW);

          return (
            <div
              key={zone.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${headroomColor}`} />
                  <span className="text-xl font-semibold text-gray-900 dark:text-white">
                    {zone.id}
                  </span>
                </div>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  {zone.headroom_MW.toFixed(0)} MW
                </span>
              </div>
              
              {/* Available Energy Bar */}
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${headroomColor} transition-all duration-500`}
                  style={{
                    width: `${Math.min(100, (zone.headroom_MW / 500) * 100)}%`
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

