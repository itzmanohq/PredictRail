/**
 * Geographic calculation utilities for PredictRail
 */

/**
 * Calculates great-circle distance between two GPS points in kilometers using Haversine formula.
 * @param {number} lat1 Latitude of point 1
 * @param {number} lon1 Longitude of point 1
 * @param {number} lat2 Latitude of point 2
 * @param {number} lon2 Longitude of point 2
 * @returns {number} Distance in kilometers
 */
export function calculateHaversineDistanceKm(lat1, lon1, lat2, lon2) {
  if (lat1 == null || lon1 == null || lat2 == null || lon2 == null) {
    return Infinity;
  }

  const R = 6371; // Earth radius in kilometers
  const toRad = (deg) => (deg * Math.PI) / 180;

  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const phi1 = toRad(lat1);
  const phi2 = toRad(lat2);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(phi1) * Math.cos(phi2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Filters a list of active network trains to only those within a specified radius
 * of the center coordinates.
 * 
 * @param {Array} trains List of network train objects
 * @param {number} centerLat Latitude of the selected train / center
 * @param {number} centerLon Longitude of the selected train / center
 * @param {number} radiusKm Maximum distance in kilometers (default: 150 km)
 * @param {string|number} excludeTrainNumber Train number of the selected train to exclude
 * @returns {Array} List of nearby trains within the radius, sorted by distance ascending
 */
export function filterNearbyTrains(trains = [], centerLat, centerLon, radiusKm = 150, excludeTrainNumber = null) {
  if (!centerLat || !centerLon || !Array.isArray(trains)) {
    return [];
  }

  const exclude = excludeTrainNumber ? String(excludeTrainNumber).trim().replace(/^0+/, '') : null;

  const nearby = [];

  for (const train of trains) {
    const tNo = String(train.train_number || '').trim().replace(/^0+/, '');
    if (exclude && tNo === exclude) {
      continue;
    }

    const lat = train.latitude;
    const lon = train.longitude;

    if (lat == null || lon == null || isNaN(lat) || isNaN(lon)) {
      continue;
    }

    const dist = calculateHaversineDistanceKm(centerLat, centerLon, lat, lon);
    if (dist <= radiusKm) {
      nearby.push({
        ...train,
        distance_km: Math.round(dist * 10) / 10
      });
    }
  }

  return nearby.sort((a, b) => a.distance_km - b.distance_km);
}
