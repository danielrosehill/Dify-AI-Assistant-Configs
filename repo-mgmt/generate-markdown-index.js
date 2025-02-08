#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { existsSync } from 'fs';

const GITHUB_BASE_URL = 'https://github.com/danielrosehill/My-AI-Assistant-Library/blob/main';

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
      assistants.push({
        title: entry.name.replace('.yml', ''),
        githubUrl: `${GITHUB_BASE_URL}/assistants/${urlPath}`,
        lastModified: stats.mtime
      });
    }
  }

  return assistants;
}

async function generateMarkdownIndex() {
  try {
    // Get all assistant configurations with last modified times
    const assistants = await getAllAssistantPaths('assistants');
    
    // Sort by last modified time, most recent first
    assistants.sort((a, b) => b.lastModified - a.lastModified);

    // Generate markdown content
    let markdown = '# AI Assistant Library Index\n\n';
    markdown += `*Last updated: ${new Date().toISOString()}*\n\n`;
    markdown += `Total assistants: ${assistants.length}\n\n`;
    markdown += '## Assistants (Most Recently Added First)\n\n';

    // Add each assistant as a markdown link
    for (const assistant of assistants) {
      markdown += `- [${assistant.title}](${assistant.githubUrl})\n`;
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
