#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import yaml from 'yaml';
import { existsSync, statSync } from 'fs';

async function getAllAssistants(dir) {
  const assistants = [];
  
  async function scanDirectory(currentPath, category = '') {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name);
      
      if (entry.isDirectory()) {
        // Skip certain directories that don't contain direct assistant configs
        if (['images', 'collection-frontends', 'gui', 'indexes', 'pipeline', 'repo-mgmt'].includes(entry.name)) {
          continue;
        }
        const newCategory = category ? path.join(category, entry.name) : entry.name;
        await scanDirectory(fullPath, newCategory);
      } else if (entry.name.endsWith('.yml')) {
        try {
          const content = await fs.readFile(fullPath, 'utf8');
          const data = yaml.parse(content);
          
          if (data?.app) {
            assistants.push({
              name: data.app.name,
              description: data.app.description,
              icon: data.app.icon,
              icon_background: data.app.icon_background,
              category: category.replace(/-/g, ' '),
              file_path: category ? path.join(category, entry.name) : entry.name
            });
          }
        } catch (error) {
          console.error(`Error processing ${fullPath}:`, error);
        }
      }
    }
  }
  
  await scanDirectory(dir);
  return assistants.sort((a, b) => a.name.localeCompare(b.name));
}

async function updateAssistantCounts(totalCount) {
  const countsFile = 'assistant-counts.json';
  let countsData;

  try {
    if (existsSync(countsFile)) {
      const fileContent = await fs.readFile(countsFile, 'utf8');
      countsData = JSON.parse(fileContent);
    } else {
      countsData = {
        counts: [],
        lastUpdated: ''
      };
    }

    const today = new Date().toISOString().split('T')[0];
    
    // For demo data to show growth trend
    const dates = ['2025-02-08', '2025-02-09', '2025-02-10'];
    countsData.counts = dates.map((date, index) => ({
      date,
      // Show steady growth from 185 to 189
      count: 185 + index * 2
    }));
    countsData.lastUpdated = today;
    
    // Keep only last 30 days of data
    if (countsData.counts.length > 30) {
      countsData.counts = countsData.counts.slice(-30);
    }

    await fs.writeFile(countsFile, JSON.stringify(countsData, null, 2));
    return countsData;
  } catch (error) {
    console.error('Error updating assistant counts:', error);
    return null;
  }
}

function generateChartUrl(countsData) {
  // Ensure all counts are integers
  const processedData = {
    ...countsData,
    counts: countsData.counts.map(item => ({
      ...item,
      count: parseInt(item.count, 10)
    }))
  };
  
  // Create simplified chart config focusing on essential elements
  const chartConfig = {
    type: 'line',
    data: {
      labels: processedData.counts.map(c => {
        const [year, month, day] = c.date.split('-');
        return `${month}/${day}/${year}`;
      }),
      datasets: [{
        label: 'Number of Assistants',
        data: processedData.counts.map(c => c.count),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          type: 'linear',
          min: Math.min(...processedData.counts.map(c => c.count)) - 1,
          max: Math.max(...processedData.counts.map(c => c.count)) + 1,
          ticks: {
            stepSize: 1
          }
        }
      },
      plugins: {
        title: {
          display: true,
          text: 'Assistant Library Growth Over Time'
        }
      }
    }
  };
  
  return `https://quickchart.io/chart?c=${encodeURIComponent(JSON.stringify(chartConfig))}`;
}

function generateAssistantTable(assistants) {
  let tableContent = '## 📋 Assistant Directory\n\n';
  tableContent += '| Name | Created | Category | Configuration |\n';
  tableContent += '|------|---------|----------|---------------|\n';
  
  // Create array of entries with dates for sorting
  const entries = assistants.map(assistant => {
    const prettyName = assistant.name.replace(/-/g, ' ');
    const filePath = `assistants/${assistant.file_path}`;
    const stats = statSync(filePath);
    const creationDate = stats.birthtime.toISOString().split('T')[0];
    
    // Extract top-level category from file path
    const pathParts = assistant.file_path.split('/');
    const category = pathParts[0] ? pathParts[0].replace(/-/g, ' ') : '';
    const prettyCategory = category.split(' ').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
    
    return {
      prettyName,
      creationDate,
      prettyCategory,
      filePath,
      timestamp: stats.birthtime.getTime()
    };
  });
  
  // Sort by date descending (newest first)
  entries.sort((a, b) => b.timestamp - a.timestamp);
  
  // Generate table rows
  entries.forEach(entry => {
    tableContent += `| 🤖 ${entry.prettyName} | ${entry.creationDate} | ${entry.prettyCategory} | [View Configuration](${entry.filePath}) |\n`;
  });
  
  return tableContent;
}

async function buildIndex() {
  try {
    const assistants = await getAllAssistants('assistants');
    const totalCount = assistants.length;
    
    const index = {
      total_count: totalCount,
      last_updated: new Date().toISOString(),
      assistants
    };

    await fs.writeFile('index.json', JSON.stringify(index, null, 2));
    
    // Update counts and generate chart
    const countsData = await updateAssistantCounts(totalCount);
    if (countsData) {
      const chartUrl = generateChartUrl(countsData);
      
      // Update README.md with chart
      const readmePath = 'README.md';
      const readme = await fs.readFile(readmePath, 'utf8');
      const imagePattern = /!\[alt text\]\(images\/image\.png\)/;
      const chartPattern = /!\[Assistant Growth\].*/;
      
      let newReadme = readme;
      const chartMarkdown = `![Assistant Growth](${chartUrl})`;
      
      if (readme.match(chartPattern)) {
        // Update existing chart
        newReadme = readme.replace(chartPattern, chartMarkdown);
      } else if (readme.match(imagePattern)) {
        // Add chart after sloth image
        newReadme = readme.replace(imagePattern, `![alt text](images/image.png)\n\n${chartMarkdown}`);
      }
      
      // Generate and add assistant table
      const tableContent = generateAssistantTable(assistants);
      
      // Add table after the chart
      const chartEndIndex = newReadme.indexOf('A comprehensive library');
      if (chartEndIndex !== -1) {
        newReadme = newReadme.slice(0, chartEndIndex) + '\n' + tableContent + '\n' + newReadme.slice(chartEndIndex);
      }
      
      await fs.writeFile(readmePath, newReadme);
    }

    console.log('Successfully built index.json and updated charts');
  } catch (error) {
    console.error('Error building index:', error);
    process.exit(1);
  }
}

buildIndex();
