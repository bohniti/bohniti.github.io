#!/usr/bin/env python3
"""
Convert to French grades properly without breaking CSV structure
"""

import csv

def convert_to_french_fixed():
    """Convert all grades to French maintaining CSV integrity"""
    
    # Grade conversion mappings
    def to_french(grade, source=''):
        """Convert any grade to French"""
        if not grade or grade.strip() == '':
            return '6a'  # Default
            
        grade = str(grade).strip()
        
        # Already French
        if any(x in grade for x in ['a', 'b', 'c']):
            return grade
            
        # European numerical to French
        mapping = {
            '3': '4a', '3+': '4b', '4-': '4c', '4': '5a', '4+': '5b',
            '5-': '5c', '5': '6a', '5+': '6a+', '6-': '6b', '6': '6b+', '6+': '6c',
            '7-': '6c+', '7': '7a', '7+': '7a+', '8-': '7b', '8': '7b+', '8+': '7c',
            '9-': '7c+', '9': '8a', '9+': '8a+',
            # Combined grades
            '7+/8-': '7a+', '8+/9-': '7c+', '6/6+': '6b+', '7/7+': '7a'
        }
        
        # YDS to French (for any remaining)
        yds_map = {
            '5.7': '5c', '5.8': '6a', '5.9': '6a+', '5.10a': '6b', '5.10b': '6b+',
            '5.10c': '6c', '5.10d': '6c+', '5.10-': '6b', '5.11a': '7a'
        }
        
        if grade in mapping:
            return mapping[grade]
        elif grade in yds_map:
            return yds_map[grade]
        elif grade in ['Grade me <3', 'DE', 'CA', 'HR', 'US']:
            return '6a'  # Default for invalid entries
        else:
            return grade  # Keep as is
    
    input_file = '/Users/timo/Development/bohniti.github.io/static/files/dataset.csv'
    
    print("Converting to French grades properly...")
    
    routes = []
    conversions = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Convert grade to French
            original_grade = row.get('grade', '')
            french_grade = to_french(original_grade)
            
            if french_grade != original_grade:
                conversions += 1
                print(f"Converting: {original_grade} → {french_grade}")
            
            # Update grade fields
            row['grade'] = french_grade
            if 'grade_uiaa' in row:
                row['grade_uiaa'] = french_grade  # Replace with French
            if 'grade_french' in row:
                row['grade_french'] = french_grade
            
            routes.append(row)
    
    # Write back with proper structure
    if routes:
        fieldnames = list(routes[0].keys())
        
        with open(input_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(routes)
    
    print(f"\nConverted {conversions} grades")
    print(f"Dataset contains {len(routes)} routes")
    
    # Check final distribution
    grade_counts = {}
    for route in routes:
        grade = route['grade']
        if grade:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    print(f"\nFrench Grade Distribution (top 10):")
    sorted_grades = sorted(grade_counts.items(), key=lambda x: x[1], reverse=True)
    for grade, count in sorted_grades[:10]:
        print(f"  {grade}: {count} routes")
    
    # Find range
    valid_grades = [g for g, _ in sorted_grades if g not in ['', 'null']]
    if valid_grades:
        print(f"\nGrade range: {min(valid_grades)} to {max(valid_grades)}")
    
    return len(routes)

if __name__ == "__main__":
    count = convert_to_french_fixed()
    print(f"\n✅ Successfully converted {count} routes to French grades")