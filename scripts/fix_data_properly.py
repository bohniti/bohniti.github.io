#!/usr/bin/env python3
"""
Properly fix the dataset without corrupting structure
"""

import csv

def fix_dataset_properly():
    """Fix grade issues while preserving CSV structure"""
    
    input_file = '/Users/timo/Development/bohniti.github.io/static/files/dataset.csv'
    
    print("Reading dataset for proper cleaning...")
    
    routes = []
    fixes_applied = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Check for problematic entries
            comment = row.get('comment', '').lower()
            grade = row.get('grade', '')
            route_name = row.get('route_name', '')
            
            # Skip the problematic route mentioned as wrong
            if 'not my grade' in comment and 'wrong route' in comment:
                fixes_applied.append(f"Removed: {route_name} - marked as incorrect in comment")
                continue
                
            # Fix unrealistic 8a+ grades (downgrade to 7c+)
            if grade == '8a+':
                fixes_applied.append(f"Downgraded: {route_name} from 8a+ to 7c+")
                row['grade'] = '7c+'
                row['grade_uiaa'] = '7c+'
                row['grade_french'] = '7c+'
                
            # Fix inflated 8a gym grades (downgrade to 7c)  
            elif grade == '8a' and 'GYM' in row.get('route_type', ''):
                fixes_applied.append(f"Downgraded gym route: {route_name} from 8a to 7c")
                row['grade'] = '7c'
                row['grade_uiaa'] = '7c'
                row['grade_french'] = '7c'
            
            routes.append(row)
    
    # Write the cleaned data
    fieldnames = ['source', 'date', 'route_name', 'location', 'sector', 'area', 'country', 
                 'grade', 'grade_uiaa', 'grade_original', 'style', 'route_type', 'height', 
                 'comment', 'tries', 'url', 'stars', 'latitude', 'longitude']
    
    with open(input_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(routes)
    
    print(f"\nApplied {len(fixes_applied)} fixes:")
    for fix in fixes_applied:
        print(f"- {fix}")
    
    print(f"\nDataset now contains {len(routes)} routes")
    
    # Check grade range
    grades = [r['grade'] for r in routes if r['grade']]
    grade_counts = {}
    for grade in grades:
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    sorted_grades = sorted(grade_counts.items(), key=lambda x: x[1], reverse=True)
    print(f"\nTop 10 grades:")
    for grade, count in sorted_grades[:10]:
        print(f"  {grade}: {count} routes")
    
    # Find realistic range
    unique_grades = list(grade_counts.keys())
    if unique_grades:
        print(f"\nGrade range: {min(unique_grades)} to {max(unique_grades)}")
    
    return len(routes)

if __name__ == "__main__":
    count = fix_dataset_properly()
    print(f"\n✅ Dataset properly cleaned with {count} routes")