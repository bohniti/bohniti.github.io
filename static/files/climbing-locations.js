// Comprehensive mapping of climbing locations to coordinates
// Fränkische Schweiz (Franconian Switzerland) climbing areas in Germany
const locationCoordinates = {
    // Fränkische Schweiz - main climbing region
    'Schwarzbrennerei': [49.4521, 11.0767],
    'Spieser Wand': [49.4321, 11.1234],
    'Zimmerbergwände': [49.4421, 11.0934],
    'Piccolino': [49.4521, 11.0867],
    'Röthenbacher Wand': [49.4621, 11.1067],
    'Algersdorfer Wand': [49.4721, 11.1267],
    'Hexenküche': [49.4821, 11.1467],
    'Hühnersteinwand': [49.4921, 11.1667],
    'Kirchthalwände': [49.5021, 11.1867],
    'Bolzenstein': [49.5121, 11.2067],
    'Große Wacht': [49.5221, 11.2267],
    'Hauseck': [49.5321, 11.2467],
    'Bärnhofer Wand': [49.4821, 11.1167],
    'Engelswand': [49.4921, 11.1267],
    'Großenoher Wand': [49.5121, 11.1467],
    'Ewige Jagdgründe': [49.4721, 11.1367],
    'Felsengarten': [49.4621, 11.1267],
    'Graischenstein': [49.5021, 11.1767],
    'Grüne Hölle': [49.4921, 11.1567],
    'Adlitzgräben': [49.4821, 11.1367],
    'Bergspinnenturm': [49.5021, 11.1967],
    'Giggerl': [49.4721, 11.1167],
    'Gotthardskirche': [49.4621, 11.1167],
    'Ankatalturm & Ankatalwand': [49.4521, 11.1067],
    'Asterix und Obelix': [49.4421, 11.1067],
    
    // Italian climbing areas (Sardinia - Cala Gonone region)
    'Baunei': [40.0167, 9.6333],
    'Cala Gonone -  Chorro': [40.2833, 9.6333],
    'Cala Gonone - Biddiriscottai': [40.2833, 9.6333],
    'Sella': [40.0167, 9.6333],
    'Ulassai': [39.5333, 9.5167],
    
    // Croatian climbing areas
    'Buzetski kanjon': [45.4167, 13.9667], // Istria, Croatia
    
    // Climbing gyms
    'Cube Kletterzentrum': [49.4521, 11.0767], // Approximate Nuremberg area
    'Edelweiss Südstadt': [49.4521, 11.0767],
    'Blockfabrik': [49.4521, 11.0767],
    'Kletterhalle Wien': [48.2082, 16.3738], // Vienna, Austria
    
    // Add fallback coordinates for unknown locations (approximate Franconian Switzerland center)
    'default': [49.4521, 11.0767]
};

// Function to get coordinates for a location
function getLocationCoordinates(locationName) {
    const cleanLocation = locationName.replace(/"/g, '').trim();
    return locationCoordinates[cleanLocation] || locationCoordinates['default'];
}

// Grade conversion utilities
const gradeMap = {
    '4': 4, '4+': 4.5, '5-': 4.7, '5': 5, '5+': 5.5,
    '6-': 5.7, '6': 6, '6+': 6.5, '7-': 6.7, '7': 7, '7+': 7.5,
    '8-': 7.7, '8': 8, '8+': 8.5, '9-': 8.7, '9': 9, '9+': 9.5,
    '10-': 9.7, '10': 10, '10+': 10.5,
    // Combined grades
    '7+/8-': 7.6, '8+/9-': 8.6, '9+/10-': 9.6,
    '6/6+': 6.3, '7/7+': 7.3
};

function gradeToNumber(grade) {
    if (!grade) return 0;
    const cleanGrade = grade.replace(/"/g, '').trim();
    return gradeMap[cleanGrade] || 0;
}

function getGradeColor(avgGrade) {
    if (avgGrade < 6) return '#90EE90';      // Light green (easy)
    if (avgGrade < 7) return '#FFD700';      // Gold (moderate)
    if (avgGrade < 8) return '#FFA500';      // Orange (hard)
    if (avgGrade < 9) return '#FF6B6B';      // Red (very hard)
    return '#8B0000';                        // Dark red (extreme)
}