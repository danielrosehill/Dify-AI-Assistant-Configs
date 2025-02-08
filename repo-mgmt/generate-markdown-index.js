#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { existsSync } from 'fs';
import yaml from 'yaml';

const GITHUB_BASE_URL = 'https://github.com/danielrosehill/My-AI-Assistant-Library/blob/main';

// Helper to extract a description from pre_prompt if app.description is empty
function extractDescriptionFromPrePrompt(prePrompt) {
  if (!prePrompt) return '';
  // Take first sentence or first 150 characters
  const firstSentence = prePrompt.split(/[.!?](\s|$)/)[0];
  return firstSentence.length > 150 ? firstSentence.substring(0, 147) + '...' : firstSentence;
}

async function getAssistantInfo(filePath) {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    const config = yaml.parse(content);
    
    let description = config.app?.description || '';
    if (!description && config.model_config?.pre_prompt) {
      description = extractDescriptionFromPrePrompt(config.model_config.pre_prompt);
    }
    
    return {
      title: config.app?.name || path.basename(filePath, '.yml'),
      description,
      icon: config.app?.icon || ''
    };
  } catch (error) {
    console.error(`Error parsing ${filePath}:`, error);
    return {
      title: path.basename(filePath, '.yml'),
      description: '',
      icon: ''
    };
  }
}

async function getAllAssistantPaths(dir, basePath = '') {
  const assistants = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relativePath = basePath ? `${basePath}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      const subDirAssistants = await getAllAssistantPaths(fullPath, relativePath);
      assistants.push(...subDirAssistants);
    } else if (entry.name.endsWith('.yml')) {
      const urlPath = relativePath.split('/').map(segment => encodeURIComponent(segment)).join('/');
      const stats = await fs.stat(fullPath);
      const info = await getAssistantInfo(fullPath);
      
      assistants.push({
        ...info,
        category: basePath.split('/')[0] || 'Uncategorized',
        subCategory: basePath.split('/')[1] || '',
        githubUrl: `${GITHUB_BASE_URL}/assistants/${urlPath}`,
        lastModified: stats.mtime
      });
    }
  }

  return assistants;
}

function formatCategory(category) {
  return category
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Generates a complete markdown index of all assistants.
 * This function is safe to run multiple times as it:
 * 1. Completely regenerates index.md from scratch each time
 * 2. Processes each YAML file exactly once
 * 3. Uses deterministic grouping and sorting
 * 
 * The pre-commit hook runs this automatically on git push.
 */
async function generateMarkdownIndex() {
  try {
    // Get all assistant configurations
    const assistants = await getAllAssistantPaths('assistants');
    
    // Group by category
    const categorized = assistants.reduce((acc, assistant) => {
      const category = assistant.category;
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(assistant);
      return acc;
    }, {});

    // Generate markdown content
    let markdown = '# AI Assistant Library Index\n\n';
    markdown += `*Last updated: ${new Date().toISOString()}*\n\n`;
    markdown += `Total assistants: ${assistants.length}\n\n`;

    // Sort categories alphabetically
    const sortedCategories = Object.keys(categorized).sort();

    for (const category of sortedCategories) {
      markdown += `## ${formatCategory(category)}\n\n`;
      
      // Sort assistants within category by last modified
      categorized[category].sort((a, b) => b.lastModified - a.lastModified);

      for (const assistant of categorized[category]) {
        const title = assistant.icon ? `${assistant.title} ${assistant.icon}` : assistant.title;
        markdown += `### ${title}\n`;
        if (assistant.description) {
          markdown += `${assistant.description}\n\n`;
        }
        markdown += `[![Open Assistant](https://img.shields.io/badge/Open_Assistant-2ea44f?style=for-the-badge)](${assistant.githubUrl})\n\n`;
      }
    }

    // Write to index.md at repo root
    await fs.writeFile('index.md', markdown);

    console.log('Successfully generated markdown index');
    console.log(`Total assistants indexed: ${assistants.length}`);
  } catch (error) {
    console.error('Error generating markdown index:', error);
    process.exit(1);
  }
}

generateMarkdownIndex();
