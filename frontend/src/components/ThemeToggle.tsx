import { Moon, Sun, Monitor } from 'lucide-react';
import type { Theme } from '../types';

interface ThemeToggleProps {
  theme: Theme;
  onToggle: () => void;
}

export default function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  const getIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun size={20} className="text-gray-700 dark:text-gray-300" />;
      case 'dark':
        return <Moon size={20} className="text-gray-700 dark:text-gray-300" />;
      case 'system':
        return <Monitor size={20} className="text-gray-700 dark:text-gray-300" />;
      default:
        return <Sun size={20} className="text-gray-700 dark:text-gray-300" />;
    }
  };

  const getLabel = () => {
    switch (theme) {
      case 'light':
        return 'Light mode';
      case 'dark':
        return 'Dark mode';
      case 'system':
        return 'System mode';
      default:
        return 'Toggle theme';
    }
  };

  return (
    <button
      onClick={onToggle}
      className="fixed top-4 right-4 z-20 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg hover:shadow-xl transition-all border border-gray-200 dark:border-gray-700 group"
      aria-label={getLabel()}
      title={getLabel()}
    >
      {getIcon()}
    </button>
  );
}

