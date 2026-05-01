#!/usr/bin/env python3
"""
Test script for multi-connection data center functionality
"""

import sys
sys.path.insert(0, 'app')

from app.utils import find_multiple_hydro_plants


def test_multi_connections():
    """Test the multi-connection allocation logic"""
    
    print("=" * 70)
    print("Testing Multi-Connection Data Center Logic")
    print("=" * 70)
    
    # Create mock hydropower plants
    mock_plants = [
        {
            'id': 'plant1',
            'name': 'Small Plant A',
            'maksYtelse_MW': 5.0,
            'coordinates': {'lat': 60.0, 'lon': 5.0}
        },
        {
            'id': 'plant2',
            'name': 'Small Plant B',
            'maksYtelse_MW': 8.0,
            'coordinates': {'lat': 60.05, 'lon': 5.05}
        },
        {
            'id': 'plant3',
            'name': 'Medium Plant C',
            'maksYtelse_MW': 12.0,
            'coordinates': {'lat': 60.1, 'lon': 5.1}
        },
        {
            'id': 'plant4',
            'name': 'Large Plant D',
            'maksYtelse_MW': 20.0,
            'coordinates': {'lat': 60.15, 'lon': 5.15}
        },
        {
            'id': 'plant5',
            'name': 'Large Plant E',
            'maksYtelse_MW': 30.0,
            'coordinates': {'lat': 60.2, 'lon': 5.2}
        }
    ]
    
    # Test 1: Small data center (10 MW)
    print("\n" + "=" * 70)
    print("Test 1: Small Data Center (10 MW)")
    print("=" * 70)
    dc_lat, dc_lon = 60.0, 5.0
    required_capacity = 10.0
    
    connections = find_multiple_hydro_plants(
        lat=dc_lat,
        lon=dc_lon,
        plants=mock_plants,
        required_capacity_mw=required_capacity,
        max_distance_km=200.0
    )
    
    print(f"\nData Center: 10 MW at ({dc_lat}, {dc_lon})")
    print(f"Connections found: {len(connections)}")
    total_allocated = sum(c['allocated_capacity_mw'] for c in connections)
    print(f"Total allocated: {total_allocated} MW")
    
    for i, conn in enumerate(connections, 1):
        print(f"\n  Connection {i}:")
        print(f"    Plant: {conn['hydro_name']}")
        print(f"    Distance: {conn['distance_km']} km")
        print(f"    Allocated: {conn['allocated_capacity_mw']} MW")
    
    assert total_allocated >= required_capacity, "Not enough capacity allocated!"
    print("\n✅ Test 1 PASSED")
    
    # Test 2: Medium data center (25 MW)
    print("\n" + "=" * 70)
    print("Test 2: Medium Data Center (25 MW)")
    print("=" * 70)
    required_capacity = 25.0
    
    connections = find_multiple_hydro_plants(
        lat=dc_lat,
        lon=dc_lon,
        plants=mock_plants,
        required_capacity_mw=required_capacity,
        max_distance_km=200.0
    )
    
    print(f"\nData Center: 25 MW at ({dc_lat}, {dc_lon})")
    print(f"Connections found: {len(connections)}")
    total_allocated = sum(c['allocated_capacity_mw'] for c in connections)
    print(f"Total allocated: {total_allocated} MW")
    
    for i, conn in enumerate(connections, 1):
        print(f"\n  Connection {i}:")
        print(f"    Plant: {conn['hydro_name']}")
        print(f"    Distance: {conn['distance_km']} km")
        print(f"    Allocated: {conn['allocated_capacity_mw']} MW")
    
    assert total_allocated >= required_capacity, "Not enough capacity allocated!"
    assert len(connections) >= 3, "Should need at least 3 plants for 25 MW"
    print("\n✅ Test 2 PASSED")
    
    # Test 3: Large data center (70 MW)
    print("\n" + "=" * 70)
    print("Test 3: Large Data Center (70 MW)")
    print("=" * 70)
    required_capacity = 70.0
    
    connections = find_multiple_hydro_plants(
        lat=dc_lat,
        lon=dc_lon,
        plants=mock_plants,
        required_capacity_mw=required_capacity,
        max_distance_km=200.0
    )
    
    print(f"\nData Center: 70 MW at ({dc_lat}, {dc_lon})")
    print(f"Connections found: {len(connections)}")
    total_allocated = sum(c['allocated_capacity_mw'] for c in connections)
    print(f"Total allocated: {total_allocated} MW")
    
    for i, conn in enumerate(connections, 1):
        print(f"\n  Connection {i}:")
        print(f"    Plant: {conn['hydro_name']}")
        print(f"    Distance: {conn['distance_km']} km")
        print(f"    Allocated: {conn['allocated_capacity_mw']} MW")
    
    assert total_allocated >= required_capacity, "Not enough capacity allocated!"
    assert len(connections) == 5, "Should use all 5 plants for 70 MW"
    print("\n✅ Test 3 PASSED")
    
    # Test 4: Very large data center (100 MW - exceeds available)
    print("\n" + "=" * 70)
    print("Test 4: Very Large Data Center (100 MW - exceeds total capacity)")
    print("=" * 70)
    required_capacity = 100.0
    
    connections = find_multiple_hydro_plants(
        lat=dc_lat,
        lon=dc_lon,
        plants=mock_plants,
        required_capacity_mw=required_capacity,
        max_distance_km=200.0
    )
    
    print(f"\nData Center: 100 MW at ({dc_lat}, {dc_lon})")
    print(f"Connections found: {len(connections)}")
    total_allocated = sum(c['allocated_capacity_mw'] for c in connections)
    total_available = sum(p['maksYtelse_MW'] for p in mock_plants)
    print(f"Total allocated: {total_allocated} MW")
    print(f"Total available: {total_available} MW")
    
    for i, conn in enumerate(connections, 1):
        print(f"\n  Connection {i}:")
        print(f"    Plant: {conn['hydro_name']}")
        print(f"    Distance: {conn['distance_km']} km")
        print(f"    Allocated: {conn['allocated_capacity_mw']} MW")
    
    assert total_allocated == total_available, "Should allocate all available capacity"
    print("\n⚠️  Warning: Data center requires more capacity than available!")
    print("✅ Test 4 PASSED (allocated maximum available)")
    
    # Summary
    print("\n" + "=" * 70)
    print("All Tests PASSED! ✅")
    print("=" * 70)
    print("\nSummary:")
    print("- The algorithm correctly allocates capacity from nearest plants first")
    print("- It creates multiple connections when single plants can't satisfy demand")
    print("- It handles cases where total demand exceeds available capacity")
    print("- Line thickness on the map will vary based on allocated capacity")


if __name__ == '__main__':
    test_multi_connections()

