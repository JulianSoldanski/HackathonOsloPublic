# Weather Layers Setup Guide

## Why Are the Layers Empty?

The temperature and precipitation layers require an **OpenWeatherMap API key** to display data. The placeholder key in the code doesn't work.

---

## ✅ Solution: Get Free API Key (5 minutes)

### Step 1: Sign Up for OpenWeatherMap

1. Visit: **https://openweathermap.org/api**
2. Click **"Sign Up"** button (top right)
3. Fill in the form (it's FREE!)
4. **Verify your email** (check your inbox)
5. **Wait 10-15 minutes** for API activation (grab a coffee! ☕)

### Step 2: Get Your API Key

1. Log in to OpenWeatherMap
2. Go to: **https://home.openweathermap.org/api_keys**
3. You'll see your default API key
4. **Copy it** (looks like: `abc123def456...`)

### Step 3: Add API Key to Your Project

Edit `Hackathon2/frontend/.env` and add:

```bash
VITE_OPENWEATHER_API_KEY=paste_your_key_here
```

Example:
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=pk.eyJ1IjoieW91cnRva2VuIn0...
VITE_OPENWEATHER_API_KEY=abc123def456789xyz
```

### Step 4: Restart Frontend

```bash
cd Hackathon2/frontend
npm run dev
```

### Step 5: Test It!

1. Open http://localhost:5173
2. Click the **"Layers"** button (top-left)
3. Select **"Temperature"**
4. You should see colorful temperature overlay! 🌡️

---

## 🎯 What You'll See

### Temperature Layer
- **Blue** = Cold regions (below 0°C)
- **Green** = Cool regions (0-10°C)
- **Yellow** = Moderate regions (10-20°C)
- **Orange** = Warm regions (20-30°C)
- **Red** = Hot regions (above 30°C)

### Precipitation Layer
- **Transparent** = No rain
- **Light blue** = Light rain
- **Dark blue** = Heavy rain
- **Purple** = Very heavy rain

---

## 📊 API Limits (Free Tier)

- **60 calls/minute**
- **1,000,000 calls/month**
- Tile layers don't count towards limits (unlimited!)
- Perfect for this application ✅

---

## 🐛 Troubleshooting

### "Layers still empty after adding key"

**Solution 1:** Make sure you restarted the frontend
```bash
# Press Ctrl+C to stop
cd Hackathon2/frontend
npm run dev
```

**Solution 2:** Check your .env file format
```bash
# Should be exactly like this (no quotes, no spaces around =)
VITE_OPENWEATHER_API_KEY=your_key_here
```

**Solution 3:** Wait for API activation
- New API keys take 10-15 minutes to activate
- Check https://home.openweathermap.org/api_keys
- Status should show "Active"

### "Invalid API key" error

- Double-check you copied the entire key
- Make sure there are no extra spaces
- Try generating a new API key

### Layers load but look weird

- This is normal! Weather data updates periodically
- Some areas might have no data (shows as transparent)
- Zoom in/out to see different detail levels

---

## 🌍 Alternative: No API Key Needed

If you can't get an API key right now, you can use **Satellite layer** which works immediately:

1. Click "Layers" button
2. Select "Satellite"
3. See actual satellite imagery of Norway!

---

## 💡 Tips

### Best Time to View Temperature Data
- Temperature data is most interesting during:
  - Winter (see cold vs warm regions)
  - Summer (temperature variations)
  - Morning/evening (temperature changes)

### Using Weather Data for Analysis
1. **Cool regions** = Lower data center cooling costs
2. **High precipitation** = More water for hydropower
3. **Satellite view** = Check terrain accessibility

---

## 📝 Quick Command Reference

```bash
# Add API key to .env
cd Hackathon2/frontend
echo "VITE_OPENWEATHER_API_KEY=your_key" >> .env

# Edit .env file
nano .env
# or
code .env

# Restart frontend
npm run dev

# Check if key is loaded (in browser console)
console.log(import.meta.env.VITE_OPENWEATHER_API_KEY)
```

---

## 🎉 All Set!

Once you add your API key and restart:
- ✅ Temperature layer will show colorful temperature data
- ✅ Precipitation layer will show rainfall
- ✅ Satellite layer works immediately (no key needed)
- ✅ All layers update automatically

**Enjoy exploring weather data across Norway!** 🌦️🌡️

