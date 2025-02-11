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
    
    if counts_file.exists():
        with open(counts_file) as f:
            data = json.load(f)
            counts = data['counts']
            
            # Check if we already have today's entry
            if not any(c['date'] == today for c in counts):
                # Keep only last 30 days
                if len(counts) >= 30:
                    counts = counts[-29:]
                counts.append({'date': today, 'count': count})
                data['counts'] = counts
                data['lastUpdated'] = today
                
                with open(counts_file, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
    else:
        # Create initial file
        data = {
            'counts': [{'date': today, 'count': count}],
            'lastUpdated': today
        }
        with open(counts_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    return False

def update_chart():
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
                    'ticks': {'stepSize': 1}
                }
            },
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Assistant Library Growth Over Time'
                }
            }
        }
    }
    
    chart_url = f'https://quickchart.io/chart?c={urllib.parse.quote(json.dumps(chart_config))}'
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Update badge count
    content = re.sub(
        r'Configurations-\d+-green',
        f'Configurations-{values[-1]}-green',
        content
    )
    
    # Update chart URL
    content = re.sub(
        r'!\[Assistant Growth\]\(https://quickchart\.io/chart\?c=.*?\)',
        f'![Assistant Growth]({chart_url})',
        content
    )
    
    with open('README.md', 'w') as f:
        f.write(content)

def count_assistants():
    """Count all YAML files in the assistants directory."""
    assistants_dir = Path('assistants')
    count = 0
    for path in assistants_dir.rglob('*.yml'):
        count += 1
    return count

if __name__ == '__main__':
    # Get current count by scanning assistants directory
    current_count = count_assistants()
    
    # Update counts file if needed
    if update_counts(current_count):
        # Update chart and badge in README
        update_chart()