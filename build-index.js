#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import yaml from 'yaml';
import { existsSync } from 'fs';

async function getAllAssistants(dir) {
  const assistants = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const category = entry.name;
      const files = await fs.readdir(fullPath);
      for (const file of files) {
        if (file.endsWith('.yml')) {
          const content = await fs.readFile(path.join(fullPath, file), 'utf8');
          const data = yaml.parse(content);
          
          if (data?.app) {
            assistants.push({
              name: data.app.name,
              description: data.app.description,
              icon: data.app.icon,
              icon_background: data.app.icon_background,
              category: category.replace(/-/g, ' '),
              file_path: path.join(category, file)
            });
          }
        }
      }
    }
  }

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
    
    // Only update once per day
    if (today !== countsData.lastUpdated) {
      countsData.counts.push({
        date: today,
        count: Math.round(totalCount)
      });
      countsData.lastUpdated = today;
      
      // Keep only last 30 days of data
      if (countsData.counts.length > 30) {
        countsData.counts = countsData.counts.slice(-30);
      }

      await fs.writeFile(countsFile, JSON.stringify(countsData, null, 2));
    }

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
      labels: processedData.counts.map(c => c.date.slice(5)),
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
      
      await fs.writeFile(readmePath, newReadme);
    }

    console.log('Successfully built index.json and updated charts');
  } catch (error) {
    console.error('Error building index:', error);
    process.exit(1);
  }
}

buildIndex();
