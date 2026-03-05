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
<script src="/files/climbing-locations.js"></script>

<script>
// Initialize the map with a view that shows both European climbing areas
const map = L.map('climbing-map').setView([45.0, 10.0], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// CSV parsing function
function parseCSV(text) {
    const lines = text.split('\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));
    
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
                route[header] = values[index] ? values[index].replace(/"/g, '') : '';
            });
            
            if (route.location_name && route.difficulty && route.location_name !== 'location_name') {
                routes.push(route);
            }
        }
    }
    
    return routes;
}

// Load and process climbing data
async function loadClimbingData() {
    try {
        const response = await fetch('/files/climbing-data.csv');
        const csvText = await response.text();
        return parseCSV(csvText);
    } catch (error) {
        console.error('Error loading climbing data:', error);
        return [];
    }
}

// Add markers to map
function addRouteMarkers(routes) {
    const locationCounts = {};
    
    routes.forEach(route => {
        const location = route.location_name;
        if (!locationCounts[location]) {
            locationCounts[location] = [];
        }
        locationCounts[location].push(route);
    });
    
    Object.keys(locationCounts).forEach(location => {
        const coords = getLocationCoordinates(location);
        const routeCount = locationCounts[location].length;
        const grades = locationCounts[location].map(r => r.difficulty).filter(g => g).join(', ');
        const avgGrade = locationCounts[location]
            .map(r => gradeToNumber(r.difficulty))
            .filter(g => g > 0)
            .reduce((sum, grade, _, arr) => sum + grade / arr.length, 0);
        
        const marker = L.circleMarker(coords, {
            radius: Math.max(8, Math.sqrt(routeCount) * 4),
            fillColor: getGradeColor(avgGrade),
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.7
        }).addTo(map);
        
        marker.bindPopup(`
            <b>${location}</b><br>
            Routes: ${routeCount}<br>
            Average Grade: ${avgGrade.toFixed(1)}<br>
            Grades: ${grades.length > 50 ? grades.substring(0, 50) + '...' : grades}
        `);
    });
}

// Create difficulty distribution chart
function createDifficultyChart(routes) {
    const gradeCounts = {};
    routes.forEach(route => {
        const grade = route.difficulty;
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
        if (route.date && route.difficulty) {
            const year = new Date(route.date).getFullYear();
            const grade = gradeToNumber(route.difficulty);
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
    if (routes.length > 0) {
        console.log(`Loaded ${routes.length} climbing routes`);
        
        // Add summary statistics to the page
        const totalRoutes = routes.length;
        const uniqueLocations = [...new Set(routes.map(r => r.location_name))].length;
        const gradeRange = routes
            .map(r => gradeToNumber(r.difficulty))
            .filter(g => g > 0);
        const minGrade = Math.min(...gradeRange);
        const maxGrade = Math.max(...gradeRange);
        
        // Add stats to the page
        const statsDiv = document.createElement('div');
        statsDiv.style.cssText = 'background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px;';
        statsDiv.innerHTML = `
            <h3>Climbing Statistics</h3>
            <p><strong>Total Routes:</strong> ${totalRoutes}</p>
            <p><strong>Unique Locations:</strong> ${uniqueLocations}</p>
            <p><strong>Grade Range:</strong> ${minGrade.toFixed(1)} - ${maxGrade.toFixed(1)}</p>
            <p><strong>Years Covered:</strong> ${Math.min(...routes.map(r => new Date(r.date).getFullYear()))} - ${Math.max(...routes.map(r => new Date(r.date).getFullYear()))}</p>
        `;
        
        // Insert stats after the intro paragraph
        const firstChart = document.getElementById('climbing-map').parentElement;
        firstChart.insertBefore(statsDiv, firstChart.firstChild);
        
        // Initialize visualizations
        addRouteMarkers(routes);
        createDifficultyChart(routes);
        createProgressionChart(routes);
        
        // Fit map to show all markers
        const bounds = L.latLngBounds();
        routes.forEach(route => {
            const coords = getLocationCoordinates(route.location_name);
            bounds.extend(coords);
        });
        if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [20, 20] });
        }
    } else {
        console.error('No climbing data loaded');
    }
});
</script>

## About the Data

This climbing log represents my personal climbing journey, tracking routes from 2017 onwards. The data includes:

- **Route Types**: Sport climbing, traditional climbing, and bouldering
- **Locations**: Primarily in the Fränkische Schweiz (Franconian Switzerland) region of Germany, with some international destinations
- **Difficulty Grades**: Using the UIAA scale common in European climbing
- **Climbing Styles**: Various ascent styles including onsight (OS), redpoint (RP), and flash attempts

### Geolocation Notes

For the geolocations, since Vertical Life doesn't provide a public API, I've used:
- Manual coordinate mapping for known climbing areas
- OpenStreetMap data for major climbing locations
- Approximate positioning for visualization purposes

*Some climbing areas may not be precisely positioned, but locations are accurate to the general region.*