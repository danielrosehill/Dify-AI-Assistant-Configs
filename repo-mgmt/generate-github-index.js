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
    // Use forward slashes for GitHub URLs
    const relativePath = basePath ? `${basePath}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      // Recursively process subdirectories
      const subDirAssistants = await getAllAssistantPaths(fullPath, relativePath);
      assistants.push(...subDirAssistants);
    } else if (entry.name.endsWith('.yml')) {
      // Process YAML files
      // Ensure forward slashes and proper URL encoding for each path segment
      const urlPath = relativePath.split('/').map(segment => encodeURIComponent(segment)).join('/');
      assistants.push({
        title: entry.name.replace('.yml', ''),
        githubUrl: `${GITHUB_BASE_URL}/assistants/${urlPath}`
      });
    }
  }

  return assistants;
}

async function buildGithubIndex() {
  try {
    // Create indexes directory if it doesn't exist
    const indexesDir = 'indexes';
    if (!existsSync(indexesDir)) {
      await fs.mkdir(indexesDir);
    }

    // Get all assistant configurations
    const assistants = await getAllAssistantPaths('assistants');
    
    // Create the index object
    const index = {
      total_count: assistants.length,
      last_updated: new Date().toISOString(),
      assistants: assistants.sort((a, b) => a.title.localeCompare(b.title))
    };

    // Write to github-index.json in the indexes directory
    // This overwrites any existing file, ensuring no duplicate data
    await fs.writeFile(
      path.join(indexesDir, 'github-index.json'), 
      JSON.stringify(index, null, 2)
    );

    console.log('Successfully generated GitHub index');
    console.log(`Total assistants indexed: ${assistants.length}`);
  } catch (error) {
    console.error('Error generating GitHub index:', error);
    process.exit(1);
  }
}

buildGithubIndex();
