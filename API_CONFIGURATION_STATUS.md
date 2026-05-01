# API Configuration Status

## AI plant analysis (`/api/analyze-plant`)
2
Credentials are **not** stored in the repository. Configure them in `backend/.env` (see `backend/.env.example`):

| Variable | Purpose |
|----------|---------|
| `GOOGLE_SEARCH_API_KEY` | Google Custom Search JSON API key |
| `GEMINI_API_KEY` | Google AI Studio / Gemini API key |
| `GOOGLE_SEARCH_ENGINE_ID` | Programmable Search Engine ID (`cx`) |

The backend loads these via `backend/app/config.py` (`Settings`). If any are missing, the endpoint returns **503** with a short explanation.

### One-time Google Cloud

- Enable **Generative Language API**: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com  
- Enable **Custom Search API** and create a Programmable Search Engine as in `GOOGLE_CUSTOM_SEARCH_SETUP.md`.

### Test Custom Search (replace placeholders)

```bash
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_GOOGLE_SEARCH_API_KEY&cx=YOUR_SEARCH_ENGINE_ID&q=Budal+kraftverk+Norway"
```

### Test in the app

1. Set the three variables in `backend/.env` and restart the backend.  
2. Open the app → under-construction plants → **Analyze Plant with AI**.

---

## Related docs

- `QUICK_START_AI_ANALYSIS.md` — quick setup  
- `AI_PLANT_ANALYSIS_FEATURE.md` — feature overview  
- `GOOGLE_CUSTOM_SEARCH_SETUP.md` — Custom Search Engine  
- `ARCHITECTURE.md` — system overview  

---

## Quotas (unchanged)

- **Custom Search**: free tier limits per Google Cloud project.  
- **Gemini**: see current Google AI pricing and quotas for the model you use (`gemini-2.0-flash-exp` in `plant_analyzer.py`).
