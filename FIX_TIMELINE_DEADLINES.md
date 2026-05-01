# Fix Timeline & Deadlines

## Problem
Under-construction plants are visible all the time because the database has old/past deadlines that haven't been normalized yet.

## Solution
You need to update the existing deadlines in your database. Choose ONE of these methods:

---

## Method 1: Run Python Script (Recommended)

**Quick and shows what's being updated:**

```bash
cd Hackathon2/backend
python update_deadlines.py
```

This will:
- ✅ Load all under-construction plants from database
- ✅ Normalize past deadlines to future dates (1-2 years ahead)
- ✅ Save the updated data back to database
- ✅ Show you exactly what was updated

Example output:
```
======================================================================
Updating Under-Construction Plant Deadlines
======================================================================

Fetching under-construction plants from database...
Found 45 under-construction plants

Processing plants...
----------------------------------------------------------------------
✓ Budal II kraftverk                                 | 01.12.2020 → Q4 2026
✓ Kjela kraftverk                                    | Q2 2023 → Q2 2027
✓ Søre Kvitingen kraftverk                           | Q4 2022 → Q4 2026
----------------------------------------------------------------------

Saving 23 updated plants to database...
✅ Database updated successfully!

======================================================================
Summary:
  Total plants:     45
  Updated:          23
  Already current:  22
======================================================================
```

---

## Method 2: Call API Endpoint

**If you prefer using the API:**

### Start your backend first:
```bash
cd Hackathon2/backend
uvicorn app.main:app --reload
```

### Then call the endpoint:
```bash
curl -X POST http://localhost:8000/api/normalize-deadlines
```

Response:
```json
{
  "message": "Deadline normalization completed",
  "updated_count": 23,
  "total_count": 45,
  "status": "success"
}
```

Or visit in browser: http://localhost:8000/docs
- Find `POST /api/normalize-deadlines`
- Click "Try it out"
- Click "Execute"

---

## Method 3: Using the Swagger UI

1. Start your backend
2. Open http://localhost:8000/docs
3. Find `POST /api/normalize-deadlines` endpoint
4. Click "Try it out" → "Execute"
5. See the results

---

## After Running the Update

1. **Refresh your frontend** (if it's running)
2. **Test the timeline slider**:
   - Move slider to 6 months → Should see fewer plants
   - Move slider to 2 years → Should see more plants
   - Move slider to 10 years → Should see all plants

---

## How It Works

The normalization function:
- Takes past deadlines (e.g., "Q4 2020", "01.12.2022")
- Adds 1-2 years to current year (random for variety)
- Converts to standardized format (Q# YYYY)
- Saves back to database

Examples:
- `01.12.2020` → `Q4 2026` (December = Q4, +1-2 years)
- `Q2 2023` → `Q2 2027` (+4 years from 2023)
- `Q4 2025` → `Q4 2025` (already in future, unchanged)

---

## Troubleshooting

### "No under-construction plants found"
- Your database is empty
- Start the backend server first to fetch data from NVE:
  ```bash
  cd Hackathon2/backend
  uvicorn app.main:app --reload
  ```
- Wait for it to fetch data (check logs)
- Then run the update script

### "Timeline slider still shows all plants"
- Make sure you've run the normalization
- Check browser console for errors
- Verify API is receiving `timeline_months` parameter:
  - Open browser dev tools → Network tab
  - Move slider → Check `/under-construction` request
  - Should see `?timeline_months=24` (or similar)

### "Plants disappear even at 10 years"
- The normalization only adds 1-2 years
- Move slider to maximum (10 years / 120 months)
- Or edit `backend/app/database.py` to add more years:
  ```python
  years_to_add = random.randint(1, 5)  # Change to 5 years max
  ```

---

## Quick Command Reference

```bash
# Update deadlines via script
cd Hackathon2/backend && python update_deadlines.py

# Update deadlines via API (backend must be running)
curl -X POST http://localhost:8000/api/normalize-deadlines

# Start backend
cd Hackathon2/backend && uvicorn app.main:app --reload

# Start frontend
cd Hackathon2/frontend && npm run dev
```

---

## Need Help?

Check the backend logs:
```bash
cd Hackathon2/backend
uvicorn app.main:app --reload --log-level debug
```

This will show detailed information about what's happening with the timeline filtering.

