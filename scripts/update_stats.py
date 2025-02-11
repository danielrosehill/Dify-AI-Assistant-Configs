#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def update_counts(count):
    today = datetime.now().strftime('%Y-%m-%d')
    counts_file = Path('assistant-counts.json')
    
    print(f"Updating counts for {today} with count: {count}")
    
    if counts_file.exists():
        print(f"Reading existing counts from {counts_file}")
        with open(counts_file) as f:
            data = json.load(f)
            counts = data['counts']
            
            # Remove today's entry if it exists
            counts = [c for c in counts if c['date'] != today]
            print("Removed any existing entry for today")
            
            # Keep only last 30 days
            if len(counts) >= 30:
                print("Trimming to last 30 days")
                counts = counts[-29:]
            
            # Add new entry for today
            counts.append({'date': today, 'count': count})
            data['counts'] = counts
            data['lastUpdated'] = today
            
            print(f"Writing updated counts to {counts_file}")
            with open(counts_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
    else:
        print(f"Creating new counts file at {counts_file}")
        # Create initial file
        data = {
            'counts': [{'date': today, 'count': count}],
            'lastUpdated': today
        }
        with open(counts_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True

def update_chart():
    print("Updating chart")
    with open('assistant-counts.json') as f:
        data = json.load(f)
    
    counts = data['counts']
    labels = [d['date'][5:].replace('-', '/') for d in counts]
    values = [d['count'] for d in counts]
    min_y = min(values) - 1
    max_y = max(values) + 1
    
    # Create the chart
    plt.figure(figsize=(10, 6))
    plt.plot(labels, values, marker='o', color='#4BC0C0', linewidth=2, markersize=6)
    
    # Customize the chart
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlabel('Date')
    plt.ylabel('Number of Assistants')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Set y-axis limits and ticks
    plt.ylim(min_y, max_y)
    plt.yticks(range(min_y, max_y + 1))
    
    # Add padding to prevent label cutoff
    plt.tight_layout()
    
    # Save the chart
    chart_path = 'images/assistant-growth.png'
    print(f"Saving chart to {chart_path}")
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Update README.md with new badge count and chart
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Update badge count
    content = re.sub(
        r'Configurations-\d+-green',
        f'Configurations-{values[-1]}-green',
        content
    )
    print(f"Updated badge count to {values[-1]}")
    
    # Update chart image - use a more specific pattern
    content = re.sub(
        r'!\[Assistant Growth\]\([^)]+\)(?:\%[^)]*\))?',
        f'![Assistant Growth](images/assistant-growth.png)',
        content
    )
    print("Updated chart reference in README.md")
    
    with open('README.md', 'w') as f:
        f.write(content)

def count_assistants():
    """Count all YAML files in the assistants directory."""
    assistants_dir = Path('assistants')
    count = 0
    for path in assistants_dir.rglob('*.yml'):
        count += 1
    print(f"Found {count} assistant YAML files")
    return count

if __name__ == '__main__':
    print("Starting update_stats.py")
    # Get current count by scanning assistants directory
    current_count = count_assistants()
    
    # Always update counts and chart
    update_counts(current_count)
    update_chart()
    print("Stats update completed")