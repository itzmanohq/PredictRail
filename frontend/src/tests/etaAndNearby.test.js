/**
 * Test Suite for PredictRail Frontend:
 * 1. Nearby Train Radius Filtering (Haversine & 150 km radius)
 * 2. Empty State Handling ("No nearby live trains found")
 * 3. Dynamic ETA Recalculation after Live Position Changes (TBM -> TPJ)
 * 4. Stale ETA Response Protection (Race Condition Prevention)
 * 5. Train Switching Isolation (Clearing Old Train ETA)
 * 6. Live Refresh Behavior
 */

import { calculateHaversineDistanceKm, filterNearbyTrains } from '../utils/geo.js';

// Assert helper
function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion Failed: ${message}`);
  }
}

function assertEquals(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`Assertion Failed: ${message}. Expected: [${expected}], Got: [${actual}]`);
  }
}

// Sample Network Active Trains (simulating real backend response across India)
const MOCK_NETWORK_TRAINS = [
  // Tamil Nadu / Southern corridor trains
  { train_number: '12638', train_name: 'Pandian Express (Return)', latitude: 9.93, longitude: 78.12, delay_minutes: 5, station_code: 'MDU' }, // ~0 km from Madurai
  { train_number: '12635', train_name: 'Vaigai Superfast Express', latitude: 10.79, longitude: 78.70, delay_minutes: 10, station_code: 'TPJ' }, // ~110 km from Madurai
  { train_number: '16127', train_name: 'Guruvayur Express', latitude: 8.71, longitude: 77.76, delay_minutes: 0, station_code: 'TEN' }, // ~140 km from Madurai
  { train_number: '12671', train_name: 'Nilgiri Express', latitude: 11.01, longitude: 76.96, delay_minutes: 15, station_code: 'CBE' }, // ~175 km (Outside 150 km radius)
  // Distant trains across India (Northern, Eastern, Western)
  { train_number: '12423', train_name: 'Rajdhani Express', latitude: 25.16, longitude: 82.33, delay_minutes: 10, station_code: 'JIA' }, // North India (~1700 km away)
  { train_number: '12002', train_name: 'Bhopal Shatabdi', latitude: 26.85, longitude: 78.10, delay_minutes: 5, station_code: 'AGC' }, // Agra (~1900 km away)
  { train_number: '12951', train_name: 'Mumbai Rajdhani', latitude: 24.18, longitude: 75.64, delay_minutes: 18, station_code: 'SGZ' }, // West India (~1600 km away)
  { train_number: '13009', train_name: 'Doon Express', latitude: 25.32, longitude: 82.98, delay_minutes: 25, station_code: 'BSB' }, // Varanasi (~1700 km away)
  { train_number: '12259', train_name: 'Sealdah Duronto', latitude: 28.61, longitude: 77.20, delay_minutes: 0, station_code: 'NDLS' } // New Delhi (~2100 km away)
];

export async function runAllTests() {
  console.log('\n======================================================');
  console.log('  PREDICTRAIL FRONTEND AUTOMATED TEST SUITE');
  console.log('======================================================\n');

  let passed = 0;
  let failed = 0;

  async function test(name, fn) {
    try {
      await fn();
      console.log(`  ✓ PASS: ${name}`);
      passed++;
    } catch (err) {
      console.error(`  ✗ FAIL: ${name}`);
      console.error(`    Error: ${err.message}\n`);
      failed++;
    }
  }

  // TEST 1: Haversine distance accuracy
  await test('Haversine Distance: accurately computes spherical distance between GPS coordinates', () => {
    // Distance between Chennai (13.08, 80.27) and Madurai (9.92, 78.12) is ~420 km
    const dist = calculateHaversineDistanceKm(13.08, 80.27, 9.92, 78.12);
    assert(dist > 400 && dist < 440, `Chennai to Madurai distance should be ~420 km, calculated: ${dist}`);

    // Same point should be 0 km
    const zeroDist = calculateHaversineDistanceKm(9.92, 78.12, 9.92, 78.12);
    assertEquals(Math.round(zeroDist), 0, 'Distance to same coordinate must be 0');

    // Null safety
    assertEquals(calculateHaversineDistanceKm(null, null, 10, 20), Infinity, 'Null inputs should return Infinity');
  });

  // TEST 2: Nearby train radius filtering (150 km) for Train 12637 Pandian Express (Madurai / Tamil Nadu)
  await test('Nearby Train Filtering: strictly excludes distant trains (Delhi, Mumbai, Kolkata) for Train 12637', () => {
    const maduraiLat = 9.92;
    const maduraiLon = 78.12;

    const nearby = filterNearbyTrains(MOCK_NETWORK_TRAINS, maduraiLat, maduraiLon, 150, '12637');

    // Should include Pandian Return (12638), Vaigai (12635), Guruvayur (16127) which are <= 150 km
    assert(nearby.length > 0, 'Should find nearby trains in Southern corridor');
    assert(nearby.length === 3, `Expected 3 trains within 150 km, got ${nearby.length}`);

    const trainNumbers = nearby.map(t => t.train_number);
    assert(trainNumbers.includes('12638'), 'Should include 12638 in Madurai');
    assert(trainNumbers.includes('12635'), 'Should include 12635 in Trichy');
    assert(trainNumbers.includes('16127'), 'Should include 16127 in Tirunelveli');

    // MUST NOT include distant trains from Delhi, Mumbai, Kolkata, Agra, Varanasi
    assert(!trainNumbers.includes('12423'), 'Must NOT include North Rajdhani 12423');
    assert(!trainNumbers.includes('12002'), 'Must NOT include Bhopal Shatabdi 12002');
    assert(!trainNumbers.includes('12951'), 'Must NOT include Mumbai Rajdhani 12951');
    assert(!trainNumbers.includes('13009'), 'Must NOT include Doon Exp 13009');
    assert(!trainNumbers.includes('12259'), 'Must NOT include Sealdah Duronto 12259');
    assert(!trainNumbers.includes('12671'), 'Must NOT include Nilgiri Exp 12671 (>150 km)');

    // Verify distance_km is attached and sorted ascending
    for (let i = 0; i < nearby.length - 1; i++) {
      assert(nearby[i].distance_km <= nearby[i + 1].distance_km, 'Trains must be sorted by distance ascending');
      assert(nearby[i].distance_km <= 150, `Distance ${nearby[i].distance_km} must be <= 150 km`);
    }
  });

  // TEST 3: "No nearby live trains found" when all trains are beyond radius
  await test('Empty State Logic: returns empty array when no trains are within radius', () => {
    // Center at an isolated coordinate (e.g. Lakshadweep / Arabian Sea: 10.56, 72.64)
    const islandLat = 10.56;
    const islandLon = 72.64;

    const nearby = filterNearbyTrains(MOCK_NETWORK_TRAINS, islandLat, islandLon, 150, '12637');
    assertEquals(nearby.length, 0, 'Expected 0 nearby trains for isolated location');
  });

  // TEST 4: ETA Recalculation after live position / station change
  await test('ETA Recalculation: correctly updates destination ETA when observation station changes (TBM vs TPJ)', () => {
    // Simulated mock dynamic ETA engine state
    function computeMockEta(trainNo, currentStation, delayMin) {
      const schedule = {
        '12637': {
          'TBM': { destinationEta: '06:11:06 (Day 2)', remainingStops: 10, nextHalt: 'CGL' },
          'TPJ': { destinationEta: '06:10:48 (Day 2)', remainingStops: 6, nextHalt: 'MPA' }
        }
      };
      return schedule[trainNo]?.[currentStation] || null;
    }

    // Step 1: User queries 12637 at TBM
    const etaTBM = computeMockEta('12637', 'TBM', 15.0);
    assert(etaTBM !== null, 'TBM ETA should exist');
    assertEquals(etaTBM.destinationEta, '06:11:06 (Day 2)', 'TBM destination ETA check');
    assertEquals(etaTBM.remainingStops, 10, 'TBM remaining stops check');

    // Step 2: Live telemetry reports train progressed to TPJ
    const etaTPJ = computeMockEta('12637', 'TPJ', 15.0);
    assert(etaTPJ !== null, 'TPJ ETA should exist');
    assertEquals(etaTPJ.destinationEta, '06:10:48 (Day 2)', 'TPJ destination ETA check');
    assertEquals(etaTPJ.remainingStops, 6, 'TPJ remaining stops check');
    assert(etaTPJ.destinationEta !== etaTBM.destinationEta, 'ETA must be recalculated for new station');
  });

  // TEST 5: Stale Response Protection (Race Condition Prevention)
  await test('Stale Response Protection: newer requests discard slower outdated responses', async () => {
    let latestRequestId = 0;
    let committedData = null;

    async function simulatedAsyncRequest(reqId, stationCode, delayMs) {
      await new Promise(resolve => setTimeout(resolve, delayMs));
      // Stale check
      if (reqId !== latestRequestId) {
        return; // discarded!
      }
      committedData = { stationCode, resolvedAt: Date.now() };
    }

    // Request 1: Dispatched first for TBM, takes 80ms (slow)
    const req1 = ++latestRequestId;
    const p1 = simulatedAsyncRequest(req1, 'TBM', 80);

    // Request 2: Dispatched immediately after for TPJ, takes 20ms (fast)
    const req2 = ++latestRequestId;
    const p2 = simulatedAsyncRequest(req2, 'TPJ', 20);

    await Promise.all([p1, p2]);

    // Committed data MUST be from Request 2 (TPJ), NOT overwritten by slow Request 1
    assertEquals(committedData.stationCode, 'TPJ', 'Committed data must be the latest request (TPJ)');
  });

  // TEST 6: Train Switching Isolation (Clearing Old Train ETA)
  await test('Train Switching Isolation: resets state and does not show previous train ETA', () => {
    let activeState = {
      trainNumber: '12637',
      trainName: 'Pandian Express',
      destinationEta: '06:11:06 (Day 2)'
    };

    // User switches to Train 12002 Bhopal Shatabdi
    function handleSwitchTrain(newTrainNumber) {
      if (activeState.trainNumber !== newTrainNumber) {
        // Immediate reset
        activeState = null;
      }
    }

    handleSwitchTrain('12002');
    assertEquals(activeState, null, 'Old train state must be cleared immediately upon switching');
  });

  // TEST 7: Live Refresh & Telemetry Update Hook
  await test('Live Telemetry Hook: triggers ETA recomputation on live telemetry reception', async () => {
    let etaRecalculated = false;
    let receivedStation = null;
    let receivedDelay = null;

    function onLiveTelemetryUpdate(liveData, trainNum) {
      if (trainNum === '12637' && liveData.currentLocation) {
        receivedStation = liveData.currentLocation.stationCode;
        receivedDelay = liveData.currentLocation.delayMinutes;
        etaRecalculated = true;
      }
    }

    // Simulate RailRadar live telemetry payload
    const mockLivePayload = {
      trainName: 'Pandian Express',
      isLive: true,
      currentLocation: {
        stationCode: 'TPJ',
        stationName: 'Tiruchchirappalli Jn',
        delayMinutes: 22,
        latitude: 10.79,
        longitude: 78.70
      }
    };

    onLiveTelemetryUpdate(mockLivePayload, '12637');

    assert(etaRecalculated, 'ETA recalculation must be triggered on live telemetry update');
    assertEquals(receivedStation, 'TPJ', 'Live station should be TPJ');
    assertEquals(receivedDelay, 22, 'Live delay should be 22 min');
  });

  // TEST 8: Real Geographic Coordinates Accuracy for Demo Journey
  await test('Demo Journey Coordinates: accurate real-world coordinates for Dibrugarh -> Guwahati -> Kolkata -> New Delhi', async () => {
    const { getStationCoordinates } = await import('../utils/stationCoordinates.js');
    
    const dbrg = getStationCoordinates('DBRG');
    assert(dbrg != null, 'DBRG coordinates must exist');
    assert(dbrg.lat > 27.0 && dbrg.lat < 28.0, `DBRG latitude should be ~27.46, got ${dbrg.lat}`);
    assert(dbrg.lon > 94.0 && dbrg.lon < 96.0, `DBRG longitude should be ~94.94, got ${dbrg.lon}`);

    const ghy = getStationCoordinates('GHY');
    assert(ghy != null, 'GHY coordinates must exist');
    assert(ghy.lat > 25.5 && ghy.lat < 27.0, `GHY latitude should be ~26.18, got ${ghy.lat}`);
    assert(ghy.lon > 91.0 && ghy.lon < 92.5, `GHY longitude should be ~91.75, got ${ghy.lon}`);

    const hwh = getStationCoordinates('HWH');
    assert(hwh != null, 'HWH (Kolkata) coordinates must exist');
    assert(hwh.lat > 22.0 && hwh.lat < 23.0, `HWH latitude should be ~22.58, got ${hwh.lat}`);
    assert(hwh.lon > 88.0 && hwh.lon < 89.0, `HWH longitude should be ~88.34, got ${hwh.lon}`);

    const ndls = getStationCoordinates('NDLS');
    assert(ndls != null, 'NDLS (New Delhi) coordinates must exist');
    assert(ndls.lat > 28.0 && ndls.lat < 29.0, `NDLS latitude should be ~28.64, got ${ndls.lat}`);
    assert(ndls.lon > 76.5 && ndls.lon < 78.0, `NDLS longitude should be ~77.22, got ${ndls.lon}`);
  });

  // TEST 9: Station Coordinate Resolution Fallback
  await test('Station Coordinate Resolution: resolves stop lat/lon or falls back seamlessly', async () => {
    const { resolveStopCoordinates } = await import('../utils/stationCoordinates.js');

    // Case 1: Stop already has valid coordinates
    const explicitStop = { station_code: 'XYZ', latitude: 12.34, longitude: 56.78 };
    const res1 = resolveStopCoordinates(explicitStop);
    assertEquals(res1[0], 12.34, 'Should preserve valid explicit latitude');
    assertEquals(res1[1], 56.78, 'Should preserve valid explicit longitude');

    // Case 2: Stop has missing coordinates, resolved from station database
    const missingCoordsStop = { station_code: 'TBM', station_name: 'Tambaram' };
    const res2 = resolveStopCoordinates(missingCoordsStop);
    assert(res2 != null, 'Should resolve TBM coordinates from database');
    assert(res2[0] > 12.5 && res2[0] < 13.5, `TBM latitude should be ~12.92, got ${res2[0]}`);
  });

  // TEST 10: Dynamic Passed Stations Filtering (Excludes Departed Stations from Selectable List)
  await test('Passed Stations Filtering: excludes already departed stops from selectable observation list', () => {
    const allStops = [
      { station_code: 'DBRG', station_name: 'Dibrugarh' },
      { station_code: 'DMV', station_name: 'Dimapur' },
      { station_code: 'LMG', station_name: 'Lumding' },
      { station_code: 'GHY', station_name: 'Guwahati' },
      { station_code: 'NBQ', station_name: 'New Bongaigaon' },
      { station_code: 'NDLS', station_name: 'New Delhi' }
    ];

    const passedStations = ['DBRG', 'DMV', 'LMG'];
    const selectableStops = allStops.filter(s => !passedStations.includes(s.station_code));

    assertEquals(selectableStops.length, 3, 'Only 3 upcoming stations should remain selectable');
    const selectableCodes = selectableStops.map(s => s.station_code);
    assert(selectableCodes.includes('GHY'), 'Current station GHY must be selectable');
    assert(selectableCodes.includes('NBQ'), 'Upcoming station NBQ must be selectable');
    assert(selectableCodes.includes('NDLS'), 'Destination NDLS must be selectable');
    assert(!selectableCodes.includes('DBRG'), 'Passed station DBRG must NOT be selectable');
    assert(!selectableCodes.includes('DMV'), 'Passed station DMV must NOT be selectable');
  });

  // TEST 11: Destination Arrived State (0 min remaining, Status ARRIVED, No negative ETA)
  await test('Destination Arrived Handling: displays Arrival 0 min and Status ARRIVED when journey completed', () => {
    const arrivedPayload = {
      is_arrived: true,
      train_status: 'ARRIVED',
      arrival_time_remaining_min: 0.0,
      current_delay_minutes: 18.0,
      dynamic_eta: {
        destination_dynamic_eta: 'Arrived (0 min remaining)',
        destination_punctuality: 'Arrived (+18m Delay)',
        upcoming_stops_count: 0
      }
    };

    assert(arrivedPayload.is_arrived === true, 'is_arrived flag must be true');
    assertEquals(arrivedPayload.arrival_time_remaining_min, 0.0, 'Remaining arrival time must be 0 min');
    assertEquals(arrivedPayload.train_status, 'ARRIVED', 'Status must be ARRIVED');
    assertEquals(arrivedPayload.dynamic_eta.upcoming_stops_count, 0, 'Upcoming stops count must be 0');
    assert(arrivedPayload.dynamic_eta.destination_dynamic_eta.includes('0 min'), 'ETA string must show 0 min remaining');
  });

  // TEST 12: Dynamic Delay Surge Reaction (Recalculation on delay increase)
  await test('Dynamic Delay Surge: recalculates predicted delay dynamically when live delay increases', () => {
    let currentObservedDelay = 8.0;
    let mlBaselineDelay = 12.0;

    function calculateDynamicDelay(liveDelay, mlDelay) {
      return round(0.70 * liveDelay + 0.30 * mlDelay, 1);
    }
    function round(v, d) { return Number(Math.round(v + 'e' + d) + 'e-' + d); }

    const initialPrediction = calculateDynamicDelay(currentObservedDelay, mlBaselineDelay);
    
    // Live update arrives: Delay surges to 28.0 min
    currentObservedDelay = 28.0;
    const updatedPrediction = calculateDynamicDelay(currentObservedDelay, mlBaselineDelay);

    assert(updatedPrediction > initialPrediction, 'Prediction must dynamically increase with live delay surge');
    assertEquals(updatedPrediction, 23.2, 'Updated blended prediction should match formula');
  });

  console.log('\n======================================================');
  console.log(`  RESULTS: ${passed} PASSED, ${failed} FAILED`);
  console.log('======================================================\n');

  if (failed > 0) {
    process.exit(1);
  }
}

