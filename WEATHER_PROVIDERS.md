# Weather Data Providers - Free Alternatives

## ✅ Currently Using

### Precipitation: RainViewer
- **URL:** `https://tilecache.rainviewer.com/v2/radar/0/{z}/{x}/{y}/256/1_1.png`
- **API Key:** ❌ None needed!
- **Coverage:** Global
- **Data:** Real-time precipitation radar
- **Update:** Every 10 minutes
- **Status:** ✅ Working now!

### Temperature: Placeholder
- Currently using radar data (not ideal for temperature)
- See alternatives below

---

## 🌡️ Better Temperature Providers

### 1. **Windy.com** (Recommended for Europe/Norway)
```
Temperature: https://ims.windy.com/ol/3.3.0/img/temp/{z}/{x}/{y}.jpg
Wind: https://ims.windy.com/ol/3.3.0/img/wind/{z}/{x}/{y}.jpg
```
- ✅ No API key
- ✅ Excellent coverage for Europe
- ✅ High quality data
- ✅ Updates frequently
- **Best for Norway!**

### 2. **OpenWeatherMap** (Free Tier)
```
Temperature: https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=YOUR_KEY
Precipitation: https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=YOUR_KEY
```
- ⚠️ Requires API key (free to get)
- ✅ 1,000,000 calls/month free
- ✅ Tile layers unlimited
- Sign up: https://openweathermap.org/api

### 3. **Meteomatics** (Professional)
```
https://api.meteomatics.com/...
```
- ⚠️ Requires API key
- Professional-grade data
- Good for Norway
- Limited free tier

---

## 🗺️ Other Useful Layers

### Terrain/Elevation
```
OpenTopoMap: https://tile.opentopomap.org/{z}/{x}/{y}.png
```
- ✅ No API key
- Shows elevation contours
- Useful for hydropower site analysis

### Wind Speed
```
Windy.com: https://ims.windy.com/ol/3.3.0/img/wind/{z}/{x}/{y}.jpg
```
- ✅ No API key
- Real-time wind data
- Useful for wind+hydro hybrid sites

### Cloud Cover
```
Sentinel Hub: https://services.sentinel-hub.com/...
```
- ⚠️ Requires registration
- Satellite cloud data
- Free tier available

### Ocean Currents (For Coastal Sites)
```
NOAA: https://tileservice.charts.noaa.gov/tiles/...
```
- ✅ No API key
- Marine data
- Useful for offshore analysis

---

## 🚀 How to Switch Providers

### Quick Switch (Edit Map.tsx)

**For Windy.com Temperature:**
```typescript
{currentLayer === 'temperature' && (
  <Source
    id="temperature-tiles"
    type="raster"
    tiles={['https://ims.windy.com/ol/3.3.0/img/temp/{z}/{x}/{y}.jpg']}
    tileSize={256}
  >
    <Layer
      id="temperature-layer"
      type="raster"
      paint={{ 'raster-opacity': 0.5 }}
    />
  </Source>
)}
```

**For OpenWeatherMap (with key):**
```typescript
tiles={[
  `https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${YOUR_KEY}`
]}
```

---

## 📊 Comparison Table

| Provider | Temperature | Precipitation | API Key | Norway Coverage | Quality |
|----------|-------------|---------------|---------|-----------------|---------|
| **RainViewer** | ❌ | ✅ | ❌ No | ⭐⭐⭐⭐ | Good |
| **Windy.com** | ✅ | ✅ | ❌ No | ⭐⭐⭐⭐⭐ | Excellent |
| **OpenWeatherMap** | ✅ | ✅ | ✅ Free | ⭐⭐⭐⭐ | Good |
| **OpenTopoMap** | ❌ | ❌ | ❌ No | ⭐⭐⭐⭐⭐ | Excellent |
| **Meteomatics** | ✅ | ✅ | ✅ Paid | ⭐⭐⭐⭐⭐ | Professional |

---

## 💡 Recommendations

### For Your Use Case (Norway Hydropower):

1. **Precipitation:** Keep RainViewer ✅ (works now!)
2. **Temperature:** Switch to Windy.com (no key needed, better for Norway)
3. **Terrain:** Add OpenTopoMap layer (useful for site analysis)
4. **Wind:** Consider adding Windy.com wind layer

### Code to Add Windy Temperature:

Replace the temperature layer in `Map.tsx`:

```typescript
{/* Temperature Overlay Layer - Using Windy.com */}
{currentLayer === 'temperature' && (
  <Source
    id="temperature-tiles"
    type="raster"
    tiles={['https://ims.windy.com/ol/3.3.0/img/temp/{z}/{x}/{y}.jpg']}
    tileSize={256}
  >
    <Layer
      id="temperature-layer"
      type="raster"
      paint={{ 'raster-opacity': 0.6 }}
    />
  </Source>
)}
```

---

## 🎯 Quick Setup

### Current Working Setup (No Changes Needed):
- ✅ Precipitation works now (RainViewer)
- ✅ Satellite works (Mapbox)
- ⚠️ Temperature needs better provider

### Recommended Change:
1. Replace temperature URL with Windy.com
2. Test by selecting "Temperature" layer
3. Enjoy free, high-quality weather data!

---

## 📚 Resources

- **RainViewer API:** https://www.rainviewer.com/api.html
- **Windy API:** https://api.windy.com/
- **OpenWeatherMap:** https://openweathermap.org/api
- **Mapbox Styles:** https://docs.mapbox.com/api/maps/styles/

---

## ✨ Bonus Ideas

### Add More Layers:
- Solar radiation (for solar+hydro hybrid)
- Snow cover (affects hydropower)
- Soil moisture (affects runoff)
- River flow data (direct hydropower impact)

All available from various free sources!

