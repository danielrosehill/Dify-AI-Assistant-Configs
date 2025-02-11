#!/usr/bin/env python3
import json
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

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
    
    chart_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Number of Assistants',
                'data': values,
                'fill': False,
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            }]
        },
        'options': {
            'responsive': True,
            'scales': {
                'y': {
                    'type': 'linear',
                    'min': min_y,
                    'max': max_y,
                    'ticks': {
                        'stepSize': 1,
                        'font': {
                            'size': 12
                        }
                    }
                },
                'x': {
                    'ticks': {
                        'font': {
                            'size': 12
                        }
                    }
                }
            },
            'plugins': {
                'title': {
                    'display': False  # Removed title to clean up the chart
                },
                'legend': {
                    'display': False  # Hide the legend since we only have one dataset
                }
            },
            'layout': {
                'padding': {
                    'top': 10,
                    'right': 10,
                    'bottom': 10,
                    'left': 10
                }
            }
        }
    }
    
    chart_url = f'https://quickchart.io/chart?c={urllib.parse.quote(json.dumps(chart_config))}'
    print(f"Generated chart URL: {chart_url}")
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Update badge count
    content = re.sub(
        r'Configurations-\d+-green',
        f'Configurations-{values[-1]}-green',
        content
    )
    print(f"Updated badge count to {values[-1]}")
    
    # Update chart URL
    content = re.sub(
        r'!\[Assistant Growth\]\(https://quickchart\.io/chart\?c=.*?\)',
        f'![Assistant Growth]({chart_url})',
        content
    )
    print("Updated chart URL in README.md")
    
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