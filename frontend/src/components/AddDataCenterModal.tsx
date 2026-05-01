import { useState } from 'react';
import { X } from 'lucide-react';
import type { DataCenterCreate } from '../types';

interface AddDataCenterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: DataCenterCreate) => Promise<void>;
  initialLat: number;
  initialLon: number;
}

export default function AddDataCenterModal({
  isOpen,
  onClose,
  onSubmit,
  initialLat,
  initialLon,
}: AddDataCenterModalProps) {
  const [name, setName] = useState('');
  const [capacityMW, setCapacityMW] = useState('10');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const capacity = parseFloat(capacityMW);
      if (isNaN(capacity) || capacity < 1 || capacity > 1000) {
        setError('Capacity must be between 1 and 1000 MW');
        setIsSubmitting(false);
        return;
      }

      await onSubmit({
        name: name.trim(),
        lat: initialLat,
        lon: initialLon,
        capacity_mw: capacity,
      });

      // Reset form and close
      setName('');
      setCapacityMW('10');
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create data center');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setName('');
      setCapacityMW('10');
      setError(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-3xl font-semibold text-gray-900 dark:text-white">
            Add Data Center
          </h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-white"
          >
            <X className="w-7 h-7" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="px-8 py-6 space-y-6">
          {/* Location Display */}
          <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg">
            <p className="text-xl text-blue-800 dark:text-blue-200 font-medium mb-2">
              Selected Location
            </p>
            <p className="text-lg text-blue-700 dark:text-blue-300">
              Lat: {initialLat.toFixed(4)}, Lon: {initialLon.toFixed(4)}
            </p>
          </div>

          {/* Name Input */}
          <div>
            <label htmlFor="dc-name" className="block text-xl font-medium text-gray-800 dark:text-gray-200 mb-2">
              Data Center Name *
            </label>
            <input
              id="dc-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Oslo DC-1"
              required
              disabled={isSubmitting}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-xl
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          {/* Capacity Input */}
          <div>
            <label htmlFor="dc-capacity" className="block text-xl font-medium text-gray-800 dark:text-gray-200 mb-2">
              Estimated Capacity (MW) *
            </label>
            <input
              id="dc-capacity"
              type="number"
              value={capacityMW}
              onChange={(e) => setCapacityMW(e.target.value)}
              min="1"
              max="1000"
              step="0.1"
              required
              disabled={isSubmitting}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-xl
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <p className="text-lg text-gray-600 dark:text-gray-300 mt-2">
              Typical range: 5-100 MW for medium-sized data centers
            </p>
          </div>

          {/* Info Box */}
          <div className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
            <p className="text-lg text-gray-700 dark:text-gray-300">
              <strong>Auto-calculated:</strong> The system will automatically find the nearest hydropower plant, 
              nearest city, and power zone for this location.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-xl text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Buttons */}
          <div className="flex space-x-4 pt-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1 px-5 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-xl
                       text-gray-800 dark:text-gray-200 font-medium
                       hover:bg-gray-50 dark:hover:bg-gray-700
                       disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              className="flex-1 px-5 py-3 bg-blue-600 text-white rounded-lg font-medium text-xl
                       hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Creating...' : 'Create Data Center'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

