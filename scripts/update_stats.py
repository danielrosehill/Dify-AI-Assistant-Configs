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

def update_chart_and_readme(current_count, assistant_files):
    print("Updating chart and README")
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
    
    # Update README.md with new badge count, chart, and assistant list
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Update badge count
    content = re.sub(
        r'Configurations-\d+-green',
        f'Configurations-{current_count}-green',
        content
    )
    print(f"Updated badge count to {current_count}")
    
    # Update count in Key Features section
    content = re.sub(
        r'\*\*Extensive Collection\*\*: \d+\+',
        f'**Extensive Collection**: {current_count}+',
        content
    )
    print(f"Updated count in Key Features section to {current_count}+")
    
    # Update chart image - use a more specific pattern
    content = re.sub(
        r'!\[Assistant Growth\]\([^)]+\)(?:\%[^)]*\))?',
        f'![Assistant Growth](images/assistant-growth.png)',
        content
    )
    print("Updated chart reference in README.md")
    
    # Update assistant list
    assistant_list = generate_assistant_list(assistant_files)
    content = update_readme_assistants(content, assistant_list)
    print("Updated assistant list in README.md")
    
    with open('README.md', 'w') as f:
        f.write(content)

def count_assistants():
    """Count all YAML files in the assistants directory."""
    assistants_dir = Path('assistants')
    count = 0
    assistant_files = []
    for path in assistants_dir.rglob('*.yml'):
        count += 1
        assistant_files.append(path)
    print(f"Found {count} assistant YAML files")
    return count, assistant_files

def generate_assistant_list(assistant_files):
    """Generate the list of assistants for the README."""
    assistant_list = []
    for file in sorted(assistant_files):
        with open(file, 'r') as f:
            content = f.read()
            name_match = re.search(r'name:\s*(.+)', content)
            description_match = re.search(r'description:\s*(.+)', content)
            name = name_match.group(1) if name_match else file.stem
            description = description_match.group(1) if description_match else ""
            relative_path = file.relative_to(Path('assistants'))
            assistant_list.append(f"| 🤖 **{name}**<br><br>_{description}_ | {datetime.now().strftime('%Y-%m-%d')} | [![Open Config](https://img.shields.io/badge/Config-Open-blue)](https://github.com/danielrosehill/My-AI-Assistant-Library/blob/main/assistants/{relative_path}) | <a href=\"https://raw.githubusercontent.com/danielrosehill/My-AI-Assistant-Library/main/assistants/{relative_path}\" download>![Download DSL](https://img.shields.io/badge/Download-DSL-green)</a> |")
    return "\n".join(assistant_list)

def update_readme_assistants(content, assistant_list):
    """Update the list of assistants in the README."""
    start_marker = "<!-- ASSISTANT_INDEX_START -->"
    end_marker = "<!-- ASSISTANT_INDEX_END -->"
    table_header = "| Assistant | Last Updated | Config | Download |\n|-----------|--------------|---------|----------|\n"
    new_content = re.sub(
        f"{start_marker}.*?{end_marker}",
        f"{start_marker}\n{table_header}{assistant_list}\n{end_marker}",
        content,
        flags=re.DOTALL
    )
    return new_content

if __name__ == '__main__':
    print("Starting update_stats.py")
    # Get current count and list of assistant files
    current_count, assistant_files = count_assistants()
    
    # Update counts in JSON file
    update_counts(current_count)
    
    # Update chart and README (including badge count and assistant list)
    update_chart_and_readme(current_count, assistant_files)
    
    print("Stats update completed")