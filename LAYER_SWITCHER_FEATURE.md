# Map Layer Switcher Feature

## ✅ What's New

Added a layer switcher button in the **top-left corner** of the map that allows you to view different data overlays for analysis.

---

## 🗺️ Available Layers

### 1. **Default** (Standard Map)
- Clean street map view
- Shows roads, cities, and geographic features
- Best for general navigation and location selection

### 2. **Temperature** 🌡️
- Real-time temperature overlay from OpenWeatherMap
- Color gradient showing temperature variations across Norway
- **Legend:**
  - Blue = Cold (-40°C to 0°C)
  - Green/Yellow = Moderate (0°C to +20°C)
  - Red = Warm (+20°C to +40°C)
- **Use Case:** Identify regions with optimal temperatures for data center cooling

### 3. **Precipitation** 🌧️
- Real-time precipitation/rainfall overlay
- Shows rain intensity across the region
- **Legend:**
  - Transparent = No precipitation
  - Light Blue = Light rain
  - Dark Blue = Heavy rain
- **Use Case:** Assess water availability for hydropower generation

### 4. **Satellite** 🛰️
- Satellite imagery view
- Shows actual terrain, forests, water bodies
- **Use Case:** Visual assessment of geographic features and infrastructure accessibility

---

## 🎯 How to Use

1. **Open the map** in your application
2. **Look for the Layers button** in the top-left corner (shows current layer name)
3. **Click the button** to open the layer menu
4. **Select a layer**:
   - Click on any layer option (Default, Temperature, Precipitation, Satellite)
   - The map updates instantly
5. **View the legend** in the bottom-right corner (shows what colors mean)

---

## 📊 Features

### Smart Layer Switching
- Instant layer changes without reloading
- Smooth transitions between layers
- All hydropower plants and data centers remain visible on all layers

### Visual Indicators
- ✓ Checkmark shows currently active layer
- Blue highlight on selected layer
- Layer icons for easy identification

### Adaptive Styling
- Automatically adjusts base map style for better overlay visibility
- Dark/light mode support
- High-contrast overlays for readability

### Interactive Legend
- Dynamic legend updates based on selected layer
- Shows temperature/precipitation scales
- Appears automatically when relevant layer is active

---

## 🔧 Technical Details

### Data Sources
- **Temperature & Precipitation:** OpenWeatherMap API tiles
- **Satellite:** Mapbox Satellite Streets style
- **Base Maps:** Mapbox Streets/Dark styles

### Implementation
- **Component:** `LayerSwitcher.tsx` - Standalone layer control component
- **Integration:** Added to `Map.tsx` with state management
- **Overlay:** Uses Mapbox GL raster layers for weather data
- **Styling:** TailwindCSS with responsive design

### API Usage
- Temperature tiles: `https://tile.openweathermap.org/map/temp_new/`
- Precipitation tiles: `https://tile.openweathermap.org/map/precipitation_new/`
- Opacity set to 60% for overlay visibility

---

## 💡 Use Cases for Data Center Planning

### Temperature Layer
- **Find cool regions:** Areas with lower average temperatures reduce cooling costs
- **Seasonal variations:** Identify regions with stable temperatures year-round
- **Climate zones:** Compare different geographic zones

### Precipitation Layer
- **Water availability:** More precipitation = more water for hydropower
- **Risk assessment:** Heavy rainfall areas may have flooding risks
- **Hydropower potential:** Correlate precipitation with plant locations

### Satellite Layer
- **Terrain analysis:** Assess accessibility for infrastructure development
- **Land use:** Identify available land for construction
- **Proximity to resources:** Visual check of nearby water sources and power lines

---

## 🎨 UI/UX Design

### Button Location
- **Top-left corner** - Easy to find, doesn't block important controls
- Above the map, outside the sidebar
- Consistent positioning across all screens

### Visual Design
- Clean white card with shadow
- Icon + text label for clarity
- Dropdown menu with full descriptions
- Hover effects for interactivity

### Accessibility
- Large click targets
- Clear visual feedback
- Keyboard-friendly (can be enhanced)
- Color-blind friendly gradients

---

## 📱 Responsive Design

- Works on desktop and tablet
- Touch-friendly button size
- Dropdown adapts to screen size
- Legends remain readable on smaller screens

---

## 🚀 Future Enhancements (Optional)

### Additional Layers
- [ ] Wind speed overlay
- [ ] Snow cover data
- [ ] Elevation/terrain contours
- [ ] Power grid infrastructure
- [ ] Fiber optic network availability
- [ ] Population density heatmap

### Advanced Features
- [ ] Time slider for historical temperature data
- [ ] Compare two layers side-by-side
- [ ] Custom layer opacity control
- [ ] Save favorite layer preferences
- [ ] Export layer data as image

### Data Sources
- [ ] Integrate with Norwegian Meteorological Institute
- [ ] Real-time weather updates
- [ ] Historical climate data trends
- [ ] Predictive climate models

---

## 📝 Files Created/Modified

### New Files
- `frontend/src/components/LayerSwitcher.tsx` - Layer control component

### Modified Files
- `frontend/src/components/Map.tsx`:
  - Added LayerSwitcher import and component
  - Added layer state management
  - Added map style switching logic
  - Added OpenWeatherMap tile overlays
  - Added temperature/precipitation legends

---

## 🎓 How It Works

1. **User clicks layer button** → Opens dropdown menu
2. **User selects layer** → Updates `currentLayer` state
3. **Map style changes** → Mapbox applies new base style
4. **Overlay loads** (if needed) → Temperature/precipitation tiles appear
5. **Legend updates** → Shows relevant color scale
6. **All markers remain** → Power plants and data centers stay visible

---

## ✨ Benefits

### For Analysis
- Multi-dimensional data visualization
- Better understanding of environmental factors
- Data-driven decision making for site selection

### For User Experience
- Intuitive, single-click layer switching
- Non-intrusive design
- Professional, polished interface
- Educational (learn about temperature patterns)

### For Development
- Modular component design
- Easy to add more layers
- Clean state management
- Well-documented code

---

## 🎉 Ready to Use!

The layer switcher is fully implemented and ready to use. Just:
1. Start your frontend application
2. Look for the "Layers" button in the top-left
3. Click and explore different views!

**Enjoy exploring Norway's climate data alongside hydropower infrastructure!** 🌍⚡

