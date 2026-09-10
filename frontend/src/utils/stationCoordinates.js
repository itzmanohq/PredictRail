/**
 * PredictRail Station Coordinates Database
 * Accurate Real Geographic Coordinates (Latitude & Longitude) for Indian Railways Stations
 */

export const STATION_COORDINATES = {
  // Demo Journey: Dibrugarh -> Guwahati -> Kolkata -> New Delhi
  'DBRG': { name: 'Dibrugarh', lat: 27.4636, lon: 94.9353, state: 'Assam' },
  'DBRT': { name: 'Dibrugarh Town', lat: 27.4855, lon: 94.9213, state: 'Assam' },
  'GHY': { name: 'Guwahati', lat: 26.1826, lon: 91.7519, state: 'Assam' },
  'KYQ': { name: 'Kamakhya', lat: 26.1554, lon: 91.7061, state: 'Assam' },
  'RNY': { name: 'Rangiya Jn', lat: 26.4385, lon: 91.6247, state: 'Assam' },
  'NBQ': { name: 'New Bongaigaon', lat: 26.5053, lon: 90.5484, state: 'Assam' },
  'KOJ': { name: 'Kokrajhar', lat: 26.4026, lon: 90.2743, state: 'Assam' },
  'NOQ': { name: 'New Alipurduar', lat: 26.4912, lon: 89.5492, state: 'West Bengal' },
  'NCB': { name: 'New Cooch Behar', lat: 26.3406, lon: 89.4674, state: 'West Bengal' },
  'NJP': { name: 'New Jalpaiguri', lat: 26.6853, lon: 88.4414, state: 'West Bengal' },
  'KNE': { name: 'Kishanganj', lat: 26.0967, lon: 87.9472, state: 'Bihar' },
  'BOE': { name: 'Barsoi Jn', lat: 25.6811, lon: 87.8932, state: 'Bihar' },
  'KIR': { name: 'Katihar Jn', lat: 25.5414, lon: 87.5707, state: 'Bihar' },
  'MLDT': { name: 'Malda Town', lat: 25.0116, lon: 88.1362, state: 'West Bengal' },
  'NFK': { name: 'New Farakka Jn', lat: 24.7932, lon: 87.9048, state: 'West Bengal' },
  'BHP': { name: 'Bolpur Shantiniketan', lat: 23.6693, lon: 87.6974, state: 'West Bengal' },
  'BWN': { name: 'Barddhaman Jn', lat: 23.2389, lon: 87.8637, state: 'West Bengal' },
  'HWH': { name: 'Howrah Jn (Kolkata)', lat: 22.5841, lon: 88.3410, state: 'West Bengal' },
  'KOAA': { name: 'Kolkata', lat: 22.6025, lon: 88.3775, state: 'West Bengal' },
  'SDAH': { name: 'Sealdah (Kolkata)', lat: 22.5670, lon: 88.3712, state: 'West Bengal' },
  'BJU': { name: 'Barauni Jn', lat: 25.4618, lon: 85.9887, state: 'Bihar' },
  'SPJ': { name: 'Samastipur Jn', lat: 25.8624, lon: 85.7812, state: 'Bihar' },
  'MFP': { name: 'Muzaffarpur Jn', lat: 26.1226, lon: 85.3906, state: 'Bihar' },
  'HJP': { name: 'Hajipur Jn', lat: 25.6858, lon: 85.2146, state: 'Bihar' },
  'SEE': { name: 'Sonpur Jn', lat: 25.7001, lon: 85.1804, state: 'Bihar' },
  'CPR': { name: 'Chhapra Jn', lat: 25.7796, lon: 84.7499, state: 'Bihar' },
  'SV': { name: 'Siwan Jn', lat: 26.2107, lon: 84.3593, state: 'Bihar' },
  'BTT': { name: 'Bhatni Jn', lat: 26.2483, lon: 83.9785, state: 'Uttar Pradesh' },
  'DEOS': { name: 'Deoria Sadar', lat: 26.5077, lon: 83.7820, state: 'Uttar Pradesh' },
  'GKP': { name: 'Gorakhpur Jn', lat: 26.7593, lon: 83.3815, state: 'Uttar Pradesh' },
  'BST': { name: 'Basti', lat: 26.7925, lon: 82.7483, state: 'Uttar Pradesh' },
  'GD': { name: 'Gonda Jn', lat: 27.1345, lon: 81.9610, state: 'Uttar Pradesh' },
  'LKO': { name: 'Lucknow Charbagh', lat: 26.8322, lon: 80.9238, state: 'Uttar Pradesh' },
  'LJN': { name: 'Lucknow Jn', lat: 26.8306, lon: 80.9198, state: 'Uttar Pradesh' },
  'BE': { name: 'Bareilly Jn', lat: 28.3398, lon: 79.4184, state: 'Uttar Pradesh' },
  'MB': { name: 'Moradabad Jn', lat: 28.8386, lon: 78.7733, state: 'Uttar Pradesh' },
  'GZB': { name: 'Ghaziabad Jn', lat: 28.6678, lon: 77.4414, state: 'Uttar Pradesh' },
  'NDLS': { name: 'New Delhi', lat: 28.6423, lon: 77.2200, state: 'Delhi' },
  'DLI': { name: 'Old Delhi Jn', lat: 28.6608, lon: 77.2274, state: 'Delhi' },
  'NZM': { name: 'Hazrat Nizamuddin', lat: 28.5888, lon: 77.2534, state: 'Delhi' },
  'ANVT': { name: 'Anand Vihar Terminal', lat: 28.6508, lon: 77.3153, state: 'Delhi' },

  // Eastern & Central Trunk Corridor (Patna, DDU, Varanasi, Kanpur, Prayagraj)
  'PNBE': { name: 'Patna Jn', lat: 25.6022, lon: 85.1376, state: 'Bihar' },
  'PPTA': { name: 'Patliputra Jn', lat: 25.6370, lon: 85.0970, state: 'Bihar' },
  'DNR': { name: 'Danapur', lat: 25.5898, lon: 85.0450, state: 'Bihar' },
  'ARA': { name: 'Ara Jn', lat: 25.5562, lon: 84.6644, state: 'Bihar' },
  'BXR': { name: 'Buxar', lat: 25.5756, lon: 83.9777, state: 'Bihar' },
  'DDU': { name: 'Pt. Deen Dayal Upadhyaya Jn (Mughalsarai)', lat: 25.2818, lon: 83.1189, state: 'Uttar Pradesh' },
  'MGS': { name: 'Mughal Sarai Jn', lat: 25.2781, lon: 83.1193, state: 'Uttar Pradesh' },
  'BSB': { name: 'Varanasi Jn', lat: 25.3268, lon: 82.9863, state: 'Uttar Pradesh' },
  'BSBS': { name: 'Banaras (Manduadih)', lat: 25.3090, lon: 82.9644, state: 'Uttar Pradesh' },
  'PRYJ': { name: 'Prayagraj Jn (Allahabad)', lat: 25.4484, lon: 81.8340, state: 'Uttar Pradesh' },
  'ALD': { name: 'Allahabad Jn', lat: 25.4484, lon: 81.8340, state: 'Uttar Pradesh' },
  'CNB': { name: 'Kanpur Central', lat: 26.4547, lon: 80.3507, state: 'Uttar Pradesh' },
  'ETW': { name: 'Etawah Jn', lat: 26.7725, lon: 79.0270, state: 'Uttar Pradesh' },
  'TDL': { name: 'Tundla Jn', lat: 27.2078, lon: 78.2389, state: 'Uttar Pradesh' },
  'ALJN': { name: 'Aligarh Jn', lat: 27.8936, lon: 78.0772, state: 'Uttar Pradesh' },
  'AGC': { name: 'Agra Cantt', lat: 27.1578, lon: 77.9906, state: 'Uttar Pradesh' },
  'GWL': { name: 'Gwalior Jn', lat: 26.2163, lon: 78.1884, state: 'Madhya Pradesh' },
  'VGLJ': { name: 'V Lakshmibai Jhansi Jn', lat: 25.4484, lon: 78.5685, state: 'Madhya Pradesh' },
  'JHS': { name: 'Jhansi Jn', lat: 25.4484, lon: 78.5685, state: 'Madhya Pradesh' },
  'BINA': { name: 'Bina Jn', lat: 24.1756, lon: 78.1842, state: 'Madhya Pradesh' },
  'BPL': { name: 'Bhopal Jn', lat: 23.2678, lon: 77.4124, state: 'Madhya Pradesh' },
  'RKMP': { name: 'Rani Kamlapati (Habibganj)', lat: 23.2185, lon: 77.4370, state: 'Madhya Pradesh' },
  'ET': { name: 'Itarsi Jn', lat: 22.6122, lon: 77.7618, state: 'Madhya Pradesh' },
  'NGP': { name: 'Nagpur Jn', lat: 21.1524, lon: 79.0882, state: 'Maharashtra' },

  // Southern Corridor (Chennai - Madurai - Pandian Express)
  'MS': { name: 'Chennai Egmore', lat: 13.0827, lon: 80.2612, state: 'Tamil Nadu' },
  'MAS': { name: 'MGR Chennai Central', lat: 13.0827, lon: 80.2755, state: 'Tamil Nadu' },
  'MBM': { name: 'Mambalam', lat: 13.0336, lon: 80.2289, state: 'Tamil Nadu' },
  'TBM': { name: 'Tambaram', lat: 12.9260, lon: 80.1192, state: 'Tamil Nadu' },
  'CGL': { name: 'Chengalpattu Jn', lat: 12.6931, lon: 79.9774, state: 'Tamil Nadu' },
  'VM': { name: 'Villupuram Jn', lat: 11.9398, lon: 79.4975, state: 'Tamil Nadu' },
  'VRI': { name: 'Vriddhachalam Jn', lat: 11.5178, lon: 79.3308, state: 'Tamil Nadu' },
  'ALU': { name: 'Ariyalur', lat: 11.1396, lon: 79.0734, state: 'Tamil Nadu' },
  'SRGM': { name: 'Srirangam', lat: 10.8654, lon: 78.6948, state: 'Tamil Nadu' },
  'TPJ': { name: 'Tiruchchirappalli Jn', lat: 10.7937, lon: 78.6836, state: 'Tamil Nadu' },
  'MPA': { name: 'Manaparai', lat: 10.6083, lon: 78.4239, state: 'Tamil Nadu' },
  'DG': { name: 'Dindigul Jn', lat: 10.3624, lon: 77.9695, state: 'Tamil Nadu' },
  'ABI': { name: 'Ambaturai', lat: 10.2589, lon: 77.9304, state: 'Tamil Nadu' },
  'KQN': { name: 'Kodaikanal Road', lat: 10.1802, lon: 77.8932, state: 'Tamil Nadu' },
  'SDN': { name: 'Sholavandan', lat: 10.0215, lon: 77.9620, state: 'Tamil Nadu' },
  'MDU': { name: 'Madurai Jn', lat: 9.9189, lon: 78.1124, state: 'Tamil Nadu' },
  'TEN': { name: 'Tirunelveli Jn', lat: 8.7139, lon: 77.7567, state: 'Tamil Nadu' },
  'CAPE': { name: 'Kanniyakumari', lat: 8.0883, lon: 77.5385, state: 'Tamil Nadu' },
  'CBE': { name: 'Coimbatore Jn', lat: 11.0018, lon: 76.9628, state: 'Tamil Nadu' },
  'SBC': { name: 'KSR Bengaluru', lat: 12.9784, lon: 77.5683, state: 'Karnataka' },
  'YPR': { name: 'Yesvantpur Jn', lat: 13.0238, lon: 77.5501, state: 'Karnataka' },
  'SMVB': { name: 'SMVT Bengaluru', lat: 12.9984, lon: 77.6582, state: 'Karnataka' },
  'BZA': { name: 'Vijayawada Jn', lat: 16.5186, lon: 80.6200, state: 'Andhra Pradesh' },
  'SC': { name: 'Secunderabad Jn', lat: 17.4338, lon: 78.5015, state: 'Telangana' },
  'HYB': { name: 'Hyderabad Deccan', lat: 17.3920, lon: 78.4674, state: 'Telangana' },

  // Western Corridor (Mumbai - Ahmedabad - Surat - Vadodara)
  'CSMT': { name: 'Mumbai CSMT', lat: 18.9401, lon: 72.8353, state: 'Maharashtra' },
  'CSTM': { name: 'Mumbai CSMT', lat: 18.9401, lon: 72.8353, state: 'Maharashtra' },
  'MMCT': { name: 'Mumbai Central', lat: 18.9696, lon: 72.8193, state: 'Maharashtra' },
  'BDTS': { name: 'Bandra Terminus', lat: 19.0624, lon: 72.8406, state: 'Maharashtra' },
  'LTT': { name: 'Lokmanya Tilak Terminus', lat: 19.0699, lon: 72.8906, state: 'Maharashtra' },
  'KYN': { name: 'Kalyan Jn', lat: 19.2372, lon: 73.1306, state: 'Maharashtra' },
  'PUNE': { name: 'Pune Jn', lat: 18.5284, lon: 73.8744, state: 'Maharashtra' },
  'ST': { name: 'Surat', lat: 21.2049, lon: 72.8406, state: 'Gujarat' },
  'BRC': { name: 'Vadodara Jn', lat: 22.3106, lon: 73.1812, state: 'Gujarat' },
  'ADI': { name: 'Ahmedabad Jn', lat: 23.0225, lon: 72.6006, state: 'Gujarat' },
  'RTM': { name: 'Ratlam Jn', lat: 23.3364, lon: 75.0370, state: 'Madhya Pradesh' },
  'KOTA': { name: 'Kota Jn', lat: 25.2185, lon: 75.8648, state: 'Rajasthan' },
  'SWM': { name: 'Sawai Madhopur Jn', lat: 25.9984, lon: 76.3685, state: 'Rajasthan' },
  'JP': { name: 'Jaipur Jn', lat: 26.9196, lon: 75.7878, state: 'Rajasthan' },
  'AII': { name: 'Ajmer Jn', lat: 26.4524, lon: 74.6385, state: 'Rajasthan' }
};

/**
 * Resolves accurate geographic coordinates for a given station code.
 * Falls back to case-insensitive lookup or alias resolution.
 * 
 * @param {string} stationCode Indian Railways station code (e.g. 'DBRG', 'GHY', 'HWH', 'NDLS')
 * @returns {{ lat: number, lon: number, name?: string } | null}
 */
export function getStationCoordinates(stationCode) {
  if (!stationCode) return null;
  const code = String(stationCode).trim().toUpperCase();
  const entry = STATION_COORDINATES[code];
  if (entry && entry.lat != null && entry.lon != null) {
    return {
      lat: entry.lat,
      lon: entry.lon,
      name: entry.name || code
    };
  }
  return null;
}

/**
 * Returns complete geographic coordinates for a stop object,
 * using stop.latitude/longitude if valid, or falling back to the station database.
 * 
 * @param {Object} stop Station stop object
 * @returns {[number, number] | null} [latitude, longitude]
 */
export function resolveStopCoordinates(stop) {
  if (!stop) return null;
  
  if (stop.latitude != null && stop.longitude != null && !isNaN(stop.latitude) && !isNaN(stop.longitude)) {
    return [Number(stop.latitude), Number(stop.longitude)];
  }
  
  const code = stop.station_code || stop.stationCode || stop.code;
  const lookup = getStationCoordinates(code);
  if (lookup) {
    return [lookup.lat, lookup.lon];
  }
  
  return null;
}
