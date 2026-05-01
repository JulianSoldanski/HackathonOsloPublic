# Quick Start Guide: Multi-Connection Data Centers

## How It Works Now

### Adding a Data Center

1. **Right-click** anywhere on the map
2. A modal appears to create a new data center
3. Fill in:
   - **Name**: e.g., "Oslo Data Center"
   - **Capacity (MW)**: e.g., 70
4. Click **"Add Data Center"**

### What Happens Automatically

The system will:
1. ✅ Find all hydropower plants within 200km
2. ✅ Sort them by distance (nearest first)
3. ✅ Allocate capacity from each plant until your data center's needs are met
4. ✅ Draw purple lines from your data center to each connected plant
5. ✅ Make thicker lines for higher capacity allocations

### Visual Indicators

- **Purple Square Icon** 🟪: Your data center
- **Purple Lines**: Power connections to hydroplants
  - **Thin lines** (2-3px): Low capacity connections (0-10 MW)
  - **Medium lines** (3-5px): Medium capacity connections (10-50 MW)
  - **Thick lines** (5-7px): High capacity connections (50+ MW)

### Viewing Connection Details

1. **Click** on a data center (purple square)
2. A popup appears showing:
   - Data center name and total capacity
   - Number of connected plants
   - List of all connections with:
     - Plant name
     - Allocated capacity (MW)
     - Distance (km)
   - Nearest city information
   - Power zone

### Example Use Cases

#### Small Data Center (10 MW)
- **Location**: Near Bergen
- **Nearby plants**: 15 MW plant at 5km
- **Result**: 1 connection line
- **Allocation**: 10 MW from the 15 MW plant

#### Medium Data Center (50 MW)
- **Location**: Near Oslo
- **Nearby plants**: 
  - 20 MW at 8km
  - 25 MW at 15km
  - 30 MW at 22km
- **Result**: 3 connection lines
- **Allocation**: 
  - 20 MW from plant 1
  - 25 MW from plant 2
  - 5 MW from plant 3

#### Large Data Center (150 MW)
- **Location**: In a high-capacity area
- **Nearby plants**: Multiple plants of various sizes
- **Result**: 5-10+ connection lines radiating outward
- **Allocation**: Distributed across all available plants

### Tips

1. **Higher capacity** data centers will show more dramatic multi-line connections
2. **Remote locations** might not find enough plants within 200km
3. **Line thickness** helps you quickly see which plants provide the most power
4. **Zoom out** to see all connections for large data centers
5. **Click markers** to see exact allocation numbers

### Deleting a Data Center

1. Click on a data center
2. In the popup, click **"Delete Data Center"**
3. Confirm the deletion
4. All connection lines disappear

### Technical Details

- **Search radius**: 200 km (configurable in backend)
- **Allocation strategy**: Nearest-first (greedy algorithm)
- **Plant types**: Currently only uses existing plants (not under-construction)
- **Maximum connections**: No limit - uses as many plants as needed

## Testing the Feature

### Quick Test
```
1. Right-click near Bergen (60.391, 5.324)
2. Create "Test DC" with 70 MW capacity
3. Observe multiple purple lines connecting to nearby plants
4. Click the data center to see all connections
```

### Stress Test
```
1. Right-click in a high-capacity area (e.g., near Ål)
2. Create a large data center with 200 MW capacity
3. Watch as many lines are drawn to satisfy the demand
4. Check the popup to verify total allocation
```

## Troubleshooting

**No lines appear after creating data center**
- Check if there are plants visible on the map (toggle plant view)
- Verify the backend is running
- Check browser console for errors

**Only one line appears for large data center**
- Check if viewing "existing" plants (not just under-construction)
- Verify the backend has plant data (check `/api/health`)
- Try refreshing the cache

**Lines are too thin/thick**
- Line width scales with allocated capacity
- Very small allocations (< 5 MW) will appear thin
- Large allocations (> 50 MW) will appear thick

## Next Steps

- Try creating data centers in different locations
- Compare capacity allocations in different power zones
- Experiment with different capacity values
- Check how plant availability affects connections

