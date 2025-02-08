#!/usr/bin/env python3
import os
import shutil
import yaml
from difflib import SequenceMatcher
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import time
import sys

# Load environment variables
env_path = Path('.env')
if not env_path.exists():
    print("Error: .env file not found")
    sys.exit(1)

# Force reload environment variables
os.environ.clear()
load_dotenv(override=True)

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

print(f"Debug - API Key found: {api_key[:10]}...{api_key[-5:]}")  # Print partial key for debugging
print(f"Debug - .env file content:")
with open('.env', 'r') as f:
    print(f.read())

try:
    client = OpenAI(api_key=api_key)
    # Test the API key with a simple request
    client.models.list()
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")
    print(f"Debug - Full error: {e}")
    sys.exit(1)

def calculate_similarity(text1, text2):
    """Calculate text similarity using SequenceMatcher."""
    return SequenceMatcher(None, text1, text2).ratio()

def get_category_from_gpt(content):
    """Use GPT-3.5 to categorize the assistant based on its content."""
    try:
        # Parse YAML content first to get meaningful text
        try:
            yaml_content = yaml.safe_load(content)
            # Extract relevant fields for categorization
            description = yaml_content.get('description', '')
            name = yaml_content.get('name', '')
            prompt = yaml_content.get('prompt', '')
            content_for_gpt = f"Name: {name}\nDescription: {description}\nPrompt: {prompt}"
        except yaml.YAMLError:
            content_for_gpt = content

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a classifier that categorizes AI assistants into one of these categories: ai-llm, business, career, character, coding-and-dev, data-utilities, entertainment, food-and-drink, for-home, for-work, fun-ideas, general-models, general-utilities, geopolitics, geospecific, graphics, ideators, legal, mental-health, pranks, preparedness, productivity, randomisers, research, shopping, software-specific, sustainability, technology, travel, voice-tools, writing. Respond with ONLY the category name, nothing else."},
                {"role": "user", "content": f"Categorize this assistant:\n{content}"}
            ],
            temperature=0,
            max_tokens=50
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error getting category from GPT: {e}")
        return None

def find_duplicate(file_path, assistants_dir):
    """Check if a similar file exists in the assistants directory."""
    try:
        with open(str(file_path), 'r', encoding='utf-8') as f:
            new_content = f.read()
    except Exception as e:
        print(f"Error reading pipeline file: {e}")
        return None
    
    for root, _, files in os.walk(str(assistants_dir)):
        for file in files:
            if file.endswith('.yml'):
                existing_path = os.path.join(root, file)
                try:
                    with open(existing_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                    
                    similarity = calculate_similarity(new_content, existing_content)
                    if similarity >= 0.8:  # 80% similarity threshold
                        return existing_path
                except Exception as e:
                    print(f"Error reading file {existing_path}: {e}")
                    continue
    return None

def process_pipeline():
    """Process all YAML files in the pipeline directory."""
    pipeline_dir = Path('pipeline')
    assistants_dir = Path('assistants')
    
    if not pipeline_dir.exists():
        print("Pipeline directory not found")
        return
    
    yaml_files = list(pipeline_dir.glob('*.yml'))
    if not yaml_files:
        print("No YAML files found in pipeline directory")
        return
    
    print(f"Found {len(yaml_files)} files to process")
    
    for file_path in yaml_files:
        print(f"\nProcessing {file_path.name}...")
        
        # Check for duplicates
        duplicate = find_duplicate(file_path, assistants_dir)
        if duplicate:
            print(f"Found duplicate: {duplicate}")
            print(f"Removing {file_path.name} from pipeline")
            os.remove(file_path)
            continue
        
        # Get category from GPT
        try:
            with open(str(file_path), 'r', encoding='utf-8') as f:
                content = f.read()
            
            category = get_category_from_gpt(content)
            if not category:
                print(f"Could not determine category for {file_path.name}")
                continue
        except Exception as e:
            print(f"Error reading file {file_path.name}: {e}")
            continue
        
        # Create category directory if it doesn't exist
        category_dir = assistants_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Move file to appropriate category
        try:
            destination = category_dir / file_path.name
            shutil.move(str(file_path), str(destination))
            print(f"Moved {file_path.name} to {category}")
        except Exception as e:
            print(f"Error moving file {file_path.name}: {e}")
            continue
        
        # Add small delay to avoid rate limiting
        time.sleep(0.5)
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    print("Starting assistant configuration processor...")
    process_pipeline()
