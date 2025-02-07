#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import yaml from 'yaml';

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

async function buildIndex() {
  try {
    const assistants = await getAllAssistants('assistants');
    const index = {
      total_count: assistants.length,
      last_updated: new Date().toISOString(),
      assistants
    };

    await fs.writeFile('index.json', JSON.stringify(index, null, 2));
    console.log('Successfully built index.json');
  } catch (error) {
    console.error('Error building index:', error);
    process.exit(1);
  }
}

buildIndex();
