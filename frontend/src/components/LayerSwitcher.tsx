import { useState } from 'react';
import { Layers, Map as MapIcon, CloudRain, Thermometer, Wind } from 'lucide-react';

export type MapLayer = 'default' | 'temperature' | 'precipitation' | 'satellite';

interface LayerSwitcherProps {
  currentLayer: MapLayer;
  onLayerChange: (layer: MapLayer) => void;
}

export default function LayerSwitcher({ currentLayer, onLayerChange }: LayerSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);

  const layers: { id: MapLayer; name: string; icon: JSX.Element; description: string }[] = [
    {
      id: 'default',
      name: 'Default',
      icon: <MapIcon size={18} />,
      description: 'Standard map view'
    },
    {
      id: 'temperature',
      name: 'Temperature',
      icon: <Thermometer size={18} />,
      description: 'Temperature overlay'
    },
    {
      id: 'precipitation',
      name: 'Elevation',
      icon: <CloudRain size={18} />,
      description: 'Terrain elevation colors'
    },
    {
      id: 'satellite',
      name: 'Satellite',
      icon: <Wind size={18} />,
      description: 'Satellite imagery'
    }
  ];

  const currentLayerInfo = layers.find(l => l.id === currentLayer) || layers[0];

  return (
    <div className="absolute top-4 left-4 z-10">
      {/* Main button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 hover:shadow-xl transition-all flex items-center gap-3 border border-gray-200 dark:border-gray-700"
        title="Change map layer"
      >
        <Layers size={26} className="text-gray-800 dark:text-gray-200" />
        <span className="text-xl font-medium text-gray-800 dark:text-gray-200">
          {currentLayerInfo.name}
        </span>
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu */}
          <div className="absolute top-full left-0 mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden min-w-[320px]">
            {layers.map((layer) => (
              <button
                key={layer.id}
                onClick={() => {
                  onLayerChange(layer.id);
                  setIsOpen(false);
                }}
                className={`w-full px-5 py-4 flex items-start gap-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                  currentLayer === layer.id
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-600'
                    : ''
                }`}
              >
                <div className={`mt-1 ${
                  currentLayer === layer.id
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-300'
                }`}>
                  {layer.icon}
                </div>
                <div className="flex-1 text-left">
                  <div className={`font-medium text-xl ${
                    currentLayer === layer.id
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {layer.name}
                  </div>
                  <div className="text-lg text-gray-600 dark:text-gray-300 mt-1">
                    {layer.description}
                  </div>
                </div>
                {currentLayer === layer.id && (
                  <div className="w-3 h-3 bg-blue-600 rounded-full mt-2" />
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

