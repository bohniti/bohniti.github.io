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

// Grade conversion utilities
const gradeMap = {
    '4': 4, '4+': 4.5, '5-': 4.7, '5': 5, '5+': 5.5,
    '6-': 5.7, '6': 6, '6+': 6.5, '7-': 6.7, '7': 7, '7+': 7.5,
    '8-': 7.7, '8': 8, '8+': 8.5, '9-': 8.7, '9': 9, '9+': 9.5,
    '10-': 9.7, '10': 10, '10+': 10.5,
    // Combined grades
    '7+/8-': 7.6, '8+/9-': 8.6, '9+/10-': 9.6,
    '6/6+': 6.3, '7/7+': 7.3, '7/A': 7.0
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
        const response = await fetch('/files/dataset.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
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
loadClimbingData().then(routes => {
    console.log('Routes loaded, length:', routes.length);
    
    if (routes.length > 0) {
        console.log(`Successfully loaded ${routes.length} climbing routes`);
        console.log('Sample route:', routes[0]);
        
        // Add summary statistics to the page
        const totalRoutes = routes.length;
        const uniqueLocations = [...new Set(routes.map(r => r.location).filter(l => l))].length;
        const gradeRange = routes
            .map(r => gradeToNumber(r.grade))
            .filter(g => g > 0);
        const minGrade = gradeRange.length > 0 ? Math.min(...gradeRange) : 0;
        const maxGrade = gradeRange.length > 0 ? Math.max(...gradeRange) : 0;
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
            <p><strong>Grade Range:</strong> ${minGrade > 0 ? minGrade.toFixed(1) + ' - ' + maxGrade.toFixed(1) : 'N/A'}</p>
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
- **Grading Systems**: Unified to European-style grades (converted from YDS where applicable)
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