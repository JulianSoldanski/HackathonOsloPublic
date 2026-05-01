# AI Plant Analysis Feature

## Overview
This feature adds AI-powered deadline analysis for hydropower plants under construction. When a plant's deadline is in the past or not available, users can click an "Analyze Plant with AI" button to get updated information.

## How It Works

### Frontend Flow
1. **Condition Check**: When displaying a plant under construction:
   - If the deadline exists and is in the future → Show the deadline
   - If the deadline is missing or in the past → Show "Analyze Plant with AI" button

2. **Analysis Trigger**: When the user clicks the button:
   - Frontend calls `/api/analyze-plant` endpoint with the plant name
   - Shows a loading indicator while analyzing
   - Displays results in a beautiful modal dialog

3. **Results Display**: The modal shows:
   - AI-generated summary (50-100 words)
   - List of sources analyzed with links
   - Quick action buttons to open each source

### Backend Flow
1. **Google Search**: Uses Google Custom Search API to find 3 relevant links
   - Searches for: `{plant_name} kraftverk Norway deadline bygge`
   - Returns top 3 results with titles, URLs, and snippets

2. **Content Extraction**: For each link:
   - Fetches the webpage
   - Extracts clean text content using BeautifulSoup
   - Limits content to 5000 characters per page

3. **AI Analysis**: Uses Gemini AI to:
   - Analyze all collected content
   - Identify deadline/completion date information
   - Generate a concise 50-100 word summary
   - Explicitly state if no deadline information is found

## Setup Requirements

### 1. Google Custom Search Engine

Create a Programmable Search Engine and JSON API key in Google Cloud, then set in `backend/.env`:

- `GOOGLE_SEARCH_API_KEY`
- `GOOGLE_SEARCH_ENGINE_ID`

See `GOOGLE_CUSTOM_SEARCH_SETUP.md` for step-by-step instructions.

### 2. Gemini API setup

Set `GEMINI_API_KEY` in `backend/.env` (same file as above).

**Important**: Enable the **Generative Language API** for your Google Cloud project:
1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Click "Enable" if it's not already enabled
3. This is required for the Gemini AI to work

**Model Used**: The code now uses `gemini-2.0-flash-exp` (latest experimental model with improved capabilities), which replaced the deprecated `gemini-pro` model.

All keys are read from environment variables via `backend/.env` (see `backend/.env.example`).

### 3. Backend Dependencies
Install the new required package:
```bash
cd Hackathon2/backend
pip install -r requirements.txt
```

New dependency added:
- `google-api-python-client==2.108.0`

## API Endpoint

### POST `/api/analyze-plant`

**Query Parameters:**
- `plant_name` (required): Name of the power plant to analyze

**Response:**
```json
{
  "plant_name": "Example Kraftverk",
  "summary": "Based on available sources, the construction deadline for Example Kraftverk has been extended to Q4 2025. The project faced delays due to environmental assessments...",
  "sources": [
    {
      "title": "Example Kraftverk Construction Update",
      "url": "https://example.com/article",
      "snippet": "The deadline has been moved..."
    }
  ],
  "links": [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
  ]
}
```

## Files Modified

### Backend
- `backend/app/plant_analyzer.py` (NEW) - Core analysis logic
- `backend/app/main.py` - Added `/api/analyze-plant` endpoint
- `backend/app/models.py` - Added `PlantAnalysisResult` and `PlantAnalysisSource` models
- `backend/requirements.txt` - Added google-api-python-client

### Frontend
- `frontend/src/api.ts` - Added `analyzePlant()` function
- `frontend/src/types.ts` - Added analysis result types
- `frontend/src/components/Sidebar.tsx` - Added analyze button and modal
- `frontend/src/components/Map.tsx` - Added analyze button and modal

## Usage

### For Users
1. Navigate to the map or sidebar
2. Click on a power plant under construction
3. If the deadline is past or unavailable, you'll see an "Analyze Plant with AI" button
4. Click the button to start analysis
5. View the AI-generated summary and sources in the modal
6. Click on any source link to read more details

### For Developers
```typescript
// In your component
import { analyzePlant } from '../api';

const handleAnalyze = async () => {
  const result = await analyzePlant(plantName);
  console.log(result.summary);
  console.log(result.sources);
};
```

## Error Handling & Fallbacks

The feature is designed to be resilient:

### Automatic Fallbacks
1. **Google CSE Not Configured**: 
   - Automatically uses curated Norwegian energy sources
   - NVE (Norwegian Water Resources and Energy Directorate)
   - NVE Konsesjonssaker (construction permits)
   - Kraftmagasinet (industry news)

2. **Page Fetch Failures**: 
   - Uses search result snippets instead
   - Gemini AI analyzes available snippets
   - Provides helpful guidance to check sources

3. **Gemini API Issues**: 
   - Returns informative error message
   - Still displays all source links
   - Users can manually check sources

4. **Complete Failure**: 
   - Provides Norwegian energy authority sources
   - Clear instructions for manual search
   - Never shows empty results

### Logging
All operations are logged to backend console:
```
INFO: Starting analysis for plant: Budal II kraftverk
INFO: Found 3 sources for Budal II kraftverk
INFO: Successfully fetched content from 2/3 sources
INFO: Generated summary for Budal II kraftverk: 85 characters
```

## Future Improvements

1. **Caching**: Cache analysis results to avoid repeated API calls
2. **Custom Search Engine**: Configure CSE to prioritize Norwegian energy sites
3. **Language Support**: Add Norwegian language prompts for better results
4. **Source Validation**: Verify source credibility and recency
5. **Deadline Extraction**: Use structured data extraction for better accuracy
6. **Rate Limiting**: Add rate limiting to prevent API quota exhaustion
7. **Background Jobs**: Move analysis to background tasks for better UX

## Limitations

1. **API Quotas**: Google Search API has daily limits (100 queries/day on free tier)
2. **Accuracy**: AI summary depends on quality of search results
3. **Language**: Some Norwegian content may not be well-analyzed
4. **Paywall Content**: Cannot access content behind paywalls
5. **Search Engine ID**: Requires manual setup of Google CSE

## Testing

To test the feature:
1. Find a plant with a past deadline (e.g., deadline before today)
2. Or find a plant with no deadline information
3. Click the "Analyze Plant with AI" button
4. Verify the modal appears with analysis results
5. Check that source links are clickable and valid

## Troubleshooting

**Issue**: "Error 404 Not Found" from Gemini API
- ✅ **FIXED**: Updated to use `gemini-1.5-flash` model
- Make sure the Generative Language API is enabled: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
- Verify your Gemini API key is valid
- Restart the backend server after making changes

**Issue**: "No search results found"
- Google Custom Search Engine ID is not configured (see GOOGLE_CUSTOM_SEARCH_SETUP.md)
- The system will fall back to Norwegian energy sources (NVE, Kraftmagasinet)
- This is expected behavior if CSE is not set up

**Issue**: "Failed to analyze plant"
- Check backend logs for specific error messages
- Verify both API keys are valid
- Ensure internet connectivity
- Check API quotas haven't been exceeded

**Issue**: Analysis returns fallback sources (NVE, Kraftmagasinet)
- This is normal if Google Custom Search Engine is not configured
- See GOOGLE_CUSTOM_SEARCH_SETUP.md to set up comprehensive search
- Fallback sources still provide useful information

**Issue**: Analysis takes too long (>30 seconds)
- Reduce timeout values in `plant_analyzer.py`
- Consider implementing background processing
- Check your internet connection and API response times
- Some Norwegian websites may be slow to respond

