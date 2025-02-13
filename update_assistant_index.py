import os
import datetime
import subprocess
import yaml
from scripts.update_stats import count_assistants

def get_assistant_data(assistant_path):
    """Extracts assistant data from the file path and YAML content."""
    assistant_name = os.path.basename(assistant_path).replace(".yml", "").replace("_", " ").strip()
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(assistant_path)).strftime('%Y-%m-%d')
    return assistant_name, creation_date, ""
# Repository configuration
REPO_NAME = "danielrosehill/My-AI-Assistant-Library"
REPO_URL = f"https://github.com/{REPO_NAME}"
RAW_URL_BASE = f"https://raw.githubusercontent.com/{REPO_NAME}/main"

def generate_markdown_row(assistant_name, creation_date, file_path, description=""):
    """Generates a simplified markdown list item for the assistant."""
    # Encode file path for URLs
    encoded_path = file_path.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    repo_url = f"{REPO_URL}/blob/main/{encoded_path}"
    raw_url = f"{RAW_URL_BASE}/{encoded_path}"
    # Create shields.io badges with links
    view_badge_url = "https://img.shields.io/badge/Config-Open-blue"
    download_badge_url = "https://img.shields.io/badge/Download-DSL-green"
    prettified_name = assistant_name.replace(".yml", "").replace("_", " ").strip()

    badge_links = f"[![Open Config]({view_badge_url})]({repo_url}) [![Download DSL]({download_badge_url})]({raw_url})"

    # Create the list item with bold name and badges
    return f"- 🤖 **{prettified_name}** {badge_links} ({creation_date})\n"

def main():
    """Main function to update the assistant index in README.md."""
    assistants_dir = "assistants"
    assistant_files = []
    for root, _, files in os.walk(assistants_dir):
        for file in files:
            if file.endswith(".yml"):
                assistant_files.append(os.path.join(root, file))

    # Sort assistants by creation date in reverse chronological order
    assistant_files.sort(key=os.path.getctime, reverse=True)

    markdown_list = []
    for file_path in assistant_files:
        assistant_name, creation_date, _ = get_assistant_data(file_path)
        markdown_list.append(generate_markdown_row(assistant_name, creation_date, file_path))

    # Update the README.md file with the generated markdown list.
    readme_path = "README.md"
    with open(readme_path, "r") as f:
        readme_content = f.readlines()
        
    # Update the badge URLs
    for i, line in enumerate(readme_content):
        if "Last%20Updated" in line:
            readme_content[i] = f'[![Last Updated](https://img.shields.io/badge/Last%20Updated-February%202025-blue)]({REPO_URL})\n'
        elif "Configurations" in line:
            assistant_count, _ = count_assistants()
            readme_content[i] = f'[![Configurations](https://img.shields.io/badge/Configurations-{assistant_count}-green)]({REPO_URL}/tree/main/assistants)\n'

    # Find the index start and end markers in the README
    index_start_marker = "<!-- ASSISTANT_INDEX_START -->\n"
    index_end_marker = "<!-- ASSISTANT_INDEX_END -->\n"
    start_index = -1
    end_index = -1

    for i, line in enumerate(readme_content):
        if line == index_start_marker and start_index == -1:  # Only take first occurrence
            start_index = i
        elif line == index_end_marker and end_index == -1:  # Only take first occurrence
            end_index = i

    # Find or create the section for the assistant index
    if start_index == -1:
        # Find a good spot to insert the index (after the usage section)
        for i, line in enumerate(readme_content):
            if "## 🚀 Usage Options" in line:
                # Skip past the usage section to find the next section
                while i < len(readme_content) and not line.startswith("##"):
                    i += 1
                    if i < len(readme_content):
                        line = readme_content[i]
                start_index = i - 1
                break
        
        if start_index == -1:
            # If no good spot found, add to end of file before author section
            for i, line in enumerate(readme_content):
                if "## Author" in line:
                    start_index = i - 1
                    break
            if start_index == -1:
                start_index = len(readme_content) - 1
        
        # Insert a newline and the start marker
        readme_content.insert(start_index + 1, "\n")
        readme_content.insert(start_index + 2, index_start_marker)
        start_index += 2

    # Find or create end marker position
    if end_index == -1:
        end_index = start_index + 1
        while end_index < len(readme_content):
            if readme_content[end_index].startswith("##"):
                break
            end_index += 1
        readme_content.insert(end_index, index_end_marker)

    # Remove any existing content between markers
    del readme_content[start_index + 1:end_index]

    # Insert the new markdown list between the markers
    list_header = []

    # Remove any duplicate start markers
    readme_content = [line for line in readme_content if line != index_start_marker or readme_content.index(line) == start_index]

    # Remove any duplicate entries
    seen = set()
    unique_items = []
    for item in markdown_list:
        assistant_name = item.split("🤖")[1].split(" ")[1]
        if assistant_name not in seen:
            seen.add(assistant_name)
            unique_items.append(item)

    # Insert the new content
    readme_content = (
        readme_content[:start_index + 1]
        + unique_items
        + [index_end_marker]
        + readme_content[end_index + 1:]
    )

    with open(readme_path, "w") as f:
        f.writelines(readme_content)

    print("Assistant index in README.md updated successfully.")

if __name__ == "__main__":
    main()