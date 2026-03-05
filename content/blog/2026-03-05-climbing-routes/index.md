---
title: "My Climbing Adventures: Routes, Maps & Grades"
date: 2026-03-05T10:00:00Z
draft: false
---

A visual journey through my climbing adventures, mapping out the routes I've conquered and analyzing the difficulty progression over the years.

## Route Locations

<div id="climbing-map" style="height: 500px; width: 100%; margin: 20px 0;"></div>

## Difficulty Distribution

<div id="difficulty-chart" style="height: 400px; width: 100%; margin: 20px 0;"></div>

## Grade Progression Over Time

<div id="progression-chart" style="height: 400px; width: 100%; margin: 20px 0;"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<script>
// Initialize the map with a view that shows both European climbing areas
const map = L.map('climbing-map').setView([45.0, 10.0], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// French Grade conversion utilities
const frenchGradeMap = {
    // French sport climbing grades
    '1a': 1.0, '1b': 1.3, '1c': 1.7, '2a': 2.0, '2b': 2.3, '2c': 2.7, 
    '3a': 3.0, '3b': 3.3, '3c': 3.7, '4a': 4.0, '4b': 4.3, '4c': 4.7,
    '5a': 5.0, '5b': 5.3, '5c': 5.7, '6a': 6.0, '6a+': 6.2, '6b': 6.3, '6b+': 6.5, '6c': 6.7, '6c+': 7.0,
    '7a': 7.3, '7a+': 7.5, '7b': 7.7, '7b+': 8.0, '7c': 8.3, '7c+': 8.5,
    '8a': 8.7, '8a+': 9.0, '8b': 9.3, '8b+': 9.5, '8c': 9.7, '8c+': 10.0,
    '9a': 10.3, '9a+': 10.5, '9b': 10.7, '9b+': 11.0, '9c': 11.3, '9c+': 11.5,
    '10a': 12.0, '10b': 12.3, '10c': 12.7,
    
    // Some variations
    '5a+': 5.2, '5b+': 5.5, '5c+': 5.8,
    
    // Combined grades (from converted data)
    '7a+': 7.5, // This handles the bulk conversion result
    
    // Aid grades
    '6b+/A1': 6.5, '7a/A1': 7.3, '7b/A1': 7.7,
    
    // Handle some edge cases that might remain
    'Grade me <3': 6.0, // Handle quirky grade entries
    
    // Fallback for any unconverted grades
    '4': 4, '4+': 4.5, '5-': 4.7, '5': 5, '5+': 5.5,
    '6-': 5.7, '6': 6, '6+': 6.5, '7-': 6.7, '7': 7, '7+': 7.5,
    '8-': 7.7, '8': 8, '8+': 8.5, '9-': 8.7, '9': 9, '9+': 9.5
};

function gradeToNumber(grade) {
    if (!grade) return 0;
    const cleanGrade = grade.replace(/"/g, '').trim();
    
    // Handle aid climbing notation
    if (cleanGrade.includes('/A')) {
        const baseGrade = cleanGrade.split('/')[0];
        return frenchGradeMap[baseGrade] || 0;
    }
    
    return frenchGradeMap[cleanGrade] || 0;
}

// Function to convert numerical grade back to French grade name
function numberToFrenchGrade(num) {
    // Find the closest French grade
    let closestGrade = '4a';
    let closestDiff = Math.abs(frenchGradeMap['4a'] - num);
    
    for (const [grade, value] of Object.entries(frenchGradeMap)) {
        const diff = Math.abs(value - num);
        if (diff < closestDiff) {
            closestDiff = diff;
            closestGrade = grade;
        }
    }
    
    return closestGrade;
}

function getGradeColor(avgGrade) {
    if (avgGrade < 4) return '#E8F5E8';      // Very light green (beginner)
    if (avgGrade < 5) return '#90EE90';      // Light green (easy)
    if (avgGrade < 6) return '#98FB98';      // Pale green (moderate)
    if (avgGrade < 7) return '#FFD700';      // Gold (intermediate)
    if (avgGrade < 8) return '#FFA500';      // Orange (hard)
    if (avgGrade < 9) return '#FF6B6B';      // Red (very hard)
    if (avgGrade < 10) return '#DC143C';     // Crimson (extreme)
    return '#8B0000';                        // Dark red (elite)
}

// CSV parsing function
function parseCSV(text) {
    const lines = text.split('\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
    
    const routes = [];
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            // Simple CSV parsing - handle quoted fields
            const values = [];
            let current = '';
            let inQuotes = false;
            
            for (let j = 0; j < lines[i].length; j++) {
                const char = lines[i][j];
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    values.push(current.trim());
                    current = '';
                } else {
                    current += char;
                }
            }
            values.push(current.trim()); // Don't forget the last value
            
            const route = {};
            headers.forEach((header, index) => {
                route[header] = values[index] ? values[index].replace(/"/g, '').trim() : '';
            });
            
            // Use new field names and check for valid data
            if (route.location && route.grade && route.location !== 'location') {
                routes.push(route);
            }
        }
    }
    
    return routes;
}

// Load and process climbing data
async function loadClimbingData() {
    try {
        // Try multiple possible paths for the CSV file
        const possiblePaths = [
            '/files/dataset.csv',
            './files/dataset.csv',
            '../../../static/files/dataset.csv'
        ];
        
        let response;
        let csvText;
        let successPath;
        
        for (const path of possiblePaths) {
            try {
                console.log(`Trying to fetch: ${path}`);
                response = await fetch(path);
                if (response.ok) {
                    csvText = await response.text();
                    successPath = path;
                    console.log(`Successfully loaded CSV from: ${path}`);
                    break;
                }
            } catch (err) {
                console.log(`Failed to fetch from ${path}: ${err.message}`);
            }
        }
        
        if (!csvText) {
            throw new Error('Could not load CSV from any path');
        }
        
        console.log('CSV loaded, first 200 chars:', csvText.substring(0, 200));
        
        const routes = parseCSV(csvText);
        console.log('Parsed routes:', routes.length);
        console.log('First route:', routes[0]);
        console.log('Routes with coordinates:', routes.filter(r => r.latitude && r.longitude).length);
        
        return routes;
    } catch (error) {
        console.error('Error loading climbing data:', error);
        return [];
    }
}

// Add markers to map
function addRouteMarkers(routes) {
    const locationCounts = {};
    
    routes.forEach(route => {
        const location = route.location;
        if (location && route.latitude && route.longitude) {
            if (!locationCounts[location]) {
                locationCounts[location] = [];
            }
            locationCounts[location].push(route);
        }
    });
    
    Object.keys(locationCounts).forEach(location => {
        const routeList = locationCounts[location];
        const firstRoute = routeList[0];
        const coords = [parseFloat(firstRoute.latitude), parseFloat(firstRoute.longitude)];
        const routeCount = routeList.length;
        const grades = routeList.map(r => r.grade).filter(g => g).join(', ');
        const avgGrade = routeList
            .map(r => gradeToNumber(r.grade))
            .filter(g => g > 0)
            .reduce((sum, grade, _, arr) => sum + grade / arr.length, 0);
        
        // Color based on data source
        const sources = [...new Set(routeList.map(r => r.source))];
        let borderColor = '#000';
        if (sources.includes('mountain_project') && sources.includes('vertical_life')) {
            borderColor = '#8B4513'; // Brown for mixed
        } else if (sources.includes('mountain_project')) {
            borderColor = '#FF0000'; // Red for Mountain Project
        } else {
            borderColor = '#0000FF'; // Blue for Vertical Life
        }
        
        const marker = L.circleMarker(coords, {
            radius: Math.max(8, Math.sqrt(routeCount) * 4),
            fillColor: getGradeColor(avgGrade),
            color: borderColor,
            weight: 3,
            opacity: 1,
            fillOpacity: 0.7
        }).addTo(map);
        
        marker.bindPopup(`
            <b>${location}</b><br>
            Routes: ${routeCount}<br>
            Sources: ${sources.join(', ')}<br>
            Average Grade: ${avgGrade > 0 ? avgGrade.toFixed(1) : 'N/A'}<br>
            Grades: ${grades.length > 50 ? grades.substring(0, 50) + '...' : grades}
        `);
    });
}

// Create difficulty distribution chart
function createDifficultyChart(routes) {
    const gradeCounts = {};
    routes.forEach(route => {
        const grade = route.grade;
        if (grade && grade.trim()) {
            gradeCounts[grade] = (gradeCounts[grade] || 0) + 1;
        }
    });
    
    const grades = Object.keys(gradeCounts)
        .filter(grade => gradeToNumber(grade) > 0)
        .sort((a, b) => gradeToNumber(a) - gradeToNumber(b));
    const counts = grades.map(grade => gradeCounts[grade]);
    
    const trace = {
        x: grades,
        y: counts,
        type: 'bar',
        marker: {
            color: grades.map(grade => getGradeColor(gradeToNumber(grade)))
        }
    };
    
    const layout = {
        title: 'Distribution of Climbing Grades',
        xaxis: { 
            title: 'Grade',
            tickangle: -45
        },
        yaxis: { title: 'Number of Routes' },
        margin: { b: 100 }
    };
    
    Plotly.newPlot('difficulty-chart', [trace], layout);
}

// Create progression chart
function createProgressionChart(routes) {
    const routesByYear = {};
    routes.forEach(route => {
        if (route.date && route.grade) {
            const year = new Date(route.date).getFullYear();
            const grade = gradeToNumber(route.grade);
            if (year && grade > 0) {
                if (!routesByYear[year]) routesByYear[year] = [];
                routesByYear[year].push(grade);
            }
        }
    });
    
    const years = Object.keys(routesByYear).sort();
    const maxGrades = years.map(year => Math.max(...routesByYear[year]));
    const avgGrades = years.map(year => {
        const grades = routesByYear[year];
        return grades.reduce((sum, grade) => sum + grade, 0) / grades.length;
    });
    const routeCounts = years.map(year => routesByYear[year].length);
    
    const trace1 = {
        x: years,
        y: maxGrades,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Hardest Grade',
        line: { color: '#FF6B6B', width: 3 },
        marker: { size: 8 }
    };
    
    const trace2 = {
        x: years,
        y: avgGrades,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Average Grade',
        line: { color: '#4CAF50', width: 3 },
        marker: { size: 8 }
    };
    
    const trace3 = {
        x: years,
        y: routeCounts,
        type: 'bar',
        name: 'Routes Climbed',
        yaxis: 'y2',
        opacity: 0.3,
        marker: { color: '#FFA500' }
    };
    
    const layout = {
        title: 'Climbing Grade Progression Over Time',
        xaxis: { title: 'Year' },
        yaxis: { 
            title: 'Grade (numerical)',
            side: 'left'
        },
        yaxis2: {
            title: 'Number of Routes',
            side: 'right',
            overlaying: 'y'
        }
    };
    
    Plotly.newPlot('progression-chart', [trace1, trace2, trace3], layout);
}

// Initialize everything
console.log('Starting to load climbing data...');
loadClimbingData().then(routes => {
    console.log('Routes loaded, length:', routes.length);
    console.log('Routes type:', typeof routes);
    console.log('Routes is array?', Array.isArray(routes));
    
    if (routes.length > 0) {
        console.log(`Successfully loaded ${routes.length} climbing routes`);
        console.log('Sample route:', routes[0]);
        
        // Add summary statistics to the page
        const totalRoutes = routes.length;
        const uniqueLocations = [...new Set(routes.map(r => r.location).filter(l => l))].length;
        const gradeRange = routes
            .map(r => gradeToNumber(r.grade))
            .filter(g => g > 0);
        const minGradeNum = gradeRange.length > 0 ? Math.min(...gradeRange) : 0;
        const maxGradeNum = gradeRange.length > 0 ? Math.max(...gradeRange) : 0;
        const minGradeFrench = numberToFrenchGrade(minGradeNum);
        const maxGradeFrench = numberToFrenchGrade(maxGradeNum);
        const sources = [...new Set(routes.map(r => r.source).filter(s => s))];
        const routesWithCoords = routes.filter(r => r.latitude && r.longitude).length;
        
        console.log('Statistics:', { totalRoutes, uniqueLocations, routesWithCoords, sources });
        
        // Add stats to the page
        const statsDiv = document.createElement('div');
        statsDiv.style.cssText = 'background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px;';
        statsDiv.innerHTML = `
            <h3>Climbing Statistics</h3>
            <p><strong>Total Routes:</strong> ${totalRoutes}</p>
            <p><strong>Data Sources:</strong> ${sources.join(', ')}</p>
            <p><strong>Unique Locations:</strong> ${uniqueLocations}</p>
            <p><strong>Routes with GPS:</strong> ${routesWithCoords}/${totalRoutes}</p>
            <p><strong>Grade Range:</strong> ${minGradeFrench} - ${maxGradeFrench}</p>
            <p><strong>Years Covered:</strong> ${routes.length > 0 ? Math.min(...routes.map(r => new Date(r.date).getFullYear())) + ' - ' + Math.max(...routes.map(r => new Date(r.date).getFullYear())) : 'N/A'}</p>
        `;
        
        // Insert stats after the intro paragraph  
        const mapContainer = document.getElementById('climbing-map');
        if (mapContainer && mapContainer.parentElement) {
            mapContainer.parentElement.insertBefore(statsDiv, mapContainer);
        }
        
        // Initialize visualizations
        console.log('Adding route markers...');
        addRouteMarkers(routes);
        
        console.log('Creating charts...');
        createDifficultyChart(routes);
        createProgressionChart(routes);
        
        // Fit map to show all markers
        const bounds = L.latLngBounds();
        let coordCount = 0;
        routes.forEach(route => {
            if (route.latitude && route.longitude && !isNaN(parseFloat(route.latitude)) && !isNaN(parseFloat(route.longitude))) {
                bounds.extend([parseFloat(route.latitude), parseFloat(route.longitude)]);
                coordCount++;
            }
        });
        
        console.log(`Valid coordinates found: ${coordCount}`);
        
        if (bounds.isValid() && coordCount > 0) {
            console.log('Fitting map bounds');
            map.fitBounds(bounds, { padding: [20, 20] });
        } else {
            console.warn('No valid bounds to fit map to');
        }
    } else {
        console.error('No climbing data loaded - routes array is empty');
        
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'background: #ffe6e6; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #ff9999;';
        errorDiv.innerHTML = `
            <h3>Error Loading Data</h3>
            <p>Unable to load climbing route data. Please check the console for details.</p>
        `;
        
        const mapContainer = document.getElementById('climbing-map');
        if (mapContainer && mapContainer.parentElement) {
            mapContainer.parentElement.insertBefore(errorDiv, mapContainer);
        }
    }
}).catch(error => {
    console.error('Failed to load climbing data:', error);
    
    // Show error message to user
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'background: #ffe6e6; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #ff9999;';
    errorDiv.innerHTML = `
        <h3>Error Loading Data</h3>
        <p>Failed to load climbing route data: ${error.message}</p>
        <p>Please check the console for more details.</p>
    `;
    
    const mapContainer = document.getElementById('climbing-map');
    if (mapContainer && mapContainer.parentElement) {
        mapContainer.parentElement.insertBefore(errorDiv, mapContainer);
    }
});
</script>

## About the Data

This climbing log represents my personal climbing journey, merging data from multiple sources to create a comprehensive view of my climbing activities from 2017 onwards.

### Data Sources

**Vertical Life**: European climbing data (404 routes)
- Primarily from Fränkische Schweiz (Franconian Switzerland), Germany
- Some international European destinations (Italy, Croatia, Austria)
- UIAA/European grading system

**Mountain Project**: North American climbing data (12 routes)
- Routes from Squamish, British Columbia, Canada
- YDS (Yosemite Decimal System) grading converted to European equivalent

### Route Information

- **Route Types**: Sport climbing, traditional climbing, bouldering, and gym routes
- **Locations**: 93 unique climbing areas across multiple countries
- **Grading System**: **Unified French scale** (3a-10c with + modifiers)
  - European numerical → French (e.g., 7+ → 7a+, 6 → 6b+)
  - YDS → French (e.g., 5.10d → 6c+, 5.7 → 5c)
  - UIAA → French (e.g., VII → 7a, VI+ → 6c)
- **Climbing Styles**: Various ascent styles including onsight, redpoint, flash, and fell/hung

### Map Legend

- **Blue markers**: Vertical Life data only
- **Red markers**: Mountain Project data only  
- **Brown markers**: Mixed data from both sources
- **Marker size**: Proportional to number of routes climbed
- **Marker color**: Based on average difficulty of routes at that location

### Geolocation Data

Coordinates were obtained through:
- Manual mapping for well-known climbing areas
- OpenStreetMap Nominatim geocoding API for other locations
- GPS coordinates are included for 386 out of 416 routes (93% coverage)

*Location positioning is accurate to the general climbing area, though some specific crags may not be precisely positioned.*