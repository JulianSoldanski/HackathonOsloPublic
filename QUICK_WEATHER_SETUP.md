# ⚡ Quick Weather Layer Setup (2 Minutes)

## The Reality

**Unfortunately, free weather tile providers without API keys are rare** because:
- Weather data is expensive to collect
- Most providers require authentication
- Free public tiles get abused and shut down

## ✅ Best Solution: OpenWeatherMap (FREE)

### Super Quick Setup:

**1. Get API Key (2 minutes):**
```bash
# Open this URL:
https://openweathermap.org/price

# Click "Get API key" under "Free" plan
# Sign up (takes 1 minute)
# Copy your API key
```

**2. Add to Your Project:**
```bash
cd Hackathon2/frontend
echo "VITE_OPENWEATHER_API_KEY=YOUR_KEY_HERE" >> .env
```

**3. Update Map.tsx:**

Replace lines 303-327 with this working code:

```typescript
{/* Temperature Overlay Layer */}
{currentLayer === 'temperature' && (
  <Source
    id="temperature-tiles"
    type="raster"
    tiles={[
      `https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${import.meta.env.VITE_OPENWEATHER_API_KEY}`
    ]}
    tileSize={256}
  >
    <Layer
      id="temperature-layer"
      type="raster"
      paint={{ 'raster-opacity': 0.6 }}
    />
  </Source>
)}

{/* Precipitation Overlay Layer */}
{currentLayer === 'precipitation' && (
  <Source
    id="precipitation-tiles"
    type="raster"
    tiles={[
      `https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${import.meta.env.VITE_OPENWEATHER_API_KEY}`
    ]}
    tileSize={256}
  >
    <Layer
      id="precipitation-layer"
      type="raster"
      paint={{ 'raster-opacity': 0.6 }}
    />
  </Source>
)}
```

**4. Restart and Test:**
```bash
npm run dev
```

Done! ✅ Both layers will work.

---

## 🎯 Why OpenWeatherMap?

- ✅ **FREE** - 1,000,000 API calls/month
- ✅ **Tile layers unlimited** - Perfect for this use case!
- ✅ **No credit card required**
- ✅ **Good coverage for Norway**
- ✅ **Takes 2 minutes to setup**

---

## 🚀 Alternative: Use Satellite Only

If you don't want to sign up, **Satellite layer works perfectly** without any API key:

1. Click "Layers" button
2. Select "Satellite"
3. See real terrain imagery

This is actually very useful for:
- Checking terrain accessibility
- Seeing water bodies
- Assessing forest coverage
- Visual site analysis

---

## 📊 What You Get (Free Tier)

| Feature | Limit |
|---------|-------|
| API Calls | 1,000,000/month |
| Tile Requests | ♾️ Unlimited |
| Historical Data | 5 days |
| Forecasts | 5 days |
| Updates | Every 10 min |

**Perfect for your use case!** 🎉

---

## 🐛 Troubleshooting

### "Still not working after adding key"
1. Make sure you restarted the frontend (`npm run dev`)
2. Check .env file has no typos
3. Wait 10-15 minutes for new API keys to activate
4. Check browser console for errors

### "API key not found"
Make sure your .env file looks like this:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=pk.your_mapbox_token
VITE_OPENWEATHER_API_KEY=your_openweather_key
```

### "Tiles loading slowly"
- This is normal for first load
- Tiles are cached after first view
- Zoom out for faster loading

---

## 💡 Summary

**Honest answer:** You need an API key for weather data. But:
- ✅ It's FREE
- ✅ Takes 2 minutes
- ✅ Works great for Norway
- ✅ No credit card needed

**Or just use Satellite layer** - works immediately, no setup! 🛰️

