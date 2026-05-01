# Google Custom Search Engine Setup Guide

## Why You Need This

The AI Plant Analysis feature requires a **Google Custom Search Engine (CSE)** to search the web for power plant information. Without it, the feature will fall back to predefined Norwegian energy sources (NVE, Kraftmagasinet), which still work but won't provide comprehensive search results.

## Step-by-Step Setup Instructions

### Step 1: Go to Programmable Search Engine Console

1. Visit: https://programmablesearchengine.google.com/
2. Sign in with your Google account (the same one associated with your API key)

### Step 2: Create a New Search Engine

1. Click the **"Add"** button (or "Create Search Engine" if it's your first one)
2. You'll see a form with several options

### Step 3: Configure Your Search Engine

Fill in the form as follows:

**Search engine name:**
```
Norway Hydropower Plants Search
```
(or any name you prefer)

**What to search:**
- Select **"Search the entire web"**
- This is important! Don't select "Search only these sites"

**Search settings (optional but recommended):**
- Language: English and Norwegian
- Region: Norway
- SafeSearch: Off

### Step 4: Create and Get Your ID

1. Click **"Create"** button
2. You'll be taken to your new search engine's overview page
3. Look for **"Search engine ID"** or **"Engine ID"**
4. It will look something like: `017576662512468239146:omuauf_lfve`
5. **Copy this ID** - you'll need it in the next step

### Step 5: Update the Code

1. Open the file: `Hackathon2/backend/app/plant_analyzer.py`
2. Find line 38 (around there):
   ```python
   cx_id = "YOUR_SEARCH_ENGINE_ID_HERE"
   ```
3. Replace `YOUR_SEARCH_ENGINE_ID_HERE` with your actual Search Engine ID:
   ```python
   cx_id = "017576662512468239146:omuauf_lfve"  # Replace with YOUR actual ID
   ```
4. Save the file

### Step 6: Restart Your Backend Server

```bash
cd Hackathon2/backend
# Stop the server (Ctrl+C) and restart it
uvicorn app.main:app --reload
```

## Verification

To verify it's working:

1. Go to your app
2. Click on a power plant under construction with no deadline
3. Click "Analyze Plant with AI"
4. Check the backend logs - you should see:
   ```
   INFO: Found 3 search results for [Plant Name]
   ```

If you see:
```
ERROR: Google Custom Search Engine ID not configured!
ERROR: Using fallback sources instead
```

Then the CSE ID is not set correctly. Double-check step 5.

## Alternative: Using Fallback Sources

If you don't want to set up Google Custom Search, the system automatically falls back to:

1. **NVE Search** - Norwegian Water Resources and Energy Directorate
2. **NVE Konsesjonssaker** - Construction permits database
3. **Kraftmagasinet** - Norwegian hydropower news

These sources are curated for Norwegian hydropower projects and will still provide useful information, though they may be less comprehensive than a full Google search.

## Troubleshooting

### "Invalid API key" error
- Verify your Google API key has the **Custom Search API** enabled
- Go to: https://console.cloud.google.com/apis/api/customsearch.googleapis.com
- Make sure it's enabled for your project

### "Quota exceeded" error
- Free tier: 100 queries per day
- Check usage: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
- Consider upgrading if you need more queries

### CSE not found
- Make sure you copied the correct Search Engine ID (not the API key)
- The ID format should be like: `abc123:xyz789`
- Verify the search engine exists in your console

### Still showing "No search results found"
- Check backend logs for specific error messages
- Verify the Custom Search API is enabled in your Google Cloud Console
- Make sure you're using the same Google account for API key and CSE
- Try testing the API directly: 
  ```
  https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_CSE_ID&q=test
  ```

## Cost Information

**Free Tier:**
- 100 queries per day
- Perfect for testing and small deployments

**Paid Tier (if needed):**
- $5 per 1000 additional queries
- Up to 10,000 queries per day

For most use cases, the free tier is sufficient!

## Video Tutorial

For a visual guide, watch: https://www.youtube.com/results?search_query=google+custom+search+engine+tutorial

## Support

If you encounter issues:
1. Check the backend logs for error messages
2. Verify all steps above were followed
3. Test your CSE directly in the Programmable Search Engine console
4. Make sure the Custom Search API is enabled in Google Cloud Console

## Quick Reference

- **Create CSE**: https://programmablesearchengine.google.com/
- **API Console**: https://console.cloud.google.com/apis/api/customsearch.googleapis.com
- **Quota Check**: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
- **Code File**: `Hackathon2/backend/app/plant_analyzer.py` (line 38)

