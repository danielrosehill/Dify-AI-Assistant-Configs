import os
import datetime
import subprocess
import yaml

def get_assistant_data(assistant_path):
    """Extracts assistant data from the file path and YAML content."""
    assistant_name = os.path.basename(assistant_path).replace(".yml", "").replace("_", " ").strip()
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(assistant_path)).strftime('%Y-%m-%d')
    description = ""
    
    try:
        with open(assistant_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
            if yaml_content and 'app' in yaml_content and 'description' in yaml_content['app']:
                # Get description and limit to 50 words
                full_description = yaml_content['app']['description']
                words = full_description.split()
                if len(words) > 50:
                    description = " ".join(words[:50]) + "..."
                else:
                    description = full_description
    except Exception as e:
        print(f"Warning: Could not read description from {assistant_path}: {e}")
    
    return assistant_name, creation_date, description

def generate_markdown_row(assistant_name, creation_date, file_path, description=""):
    """Generates a markdown table row for the assistant."""
    # Encode file path for URLs
    encoded_path = file_path.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    repo_url = f"https://github.com/danielrosehill/dify-assistant-configs/blob/main/{encoded_path}"
    raw_url = f"https://raw.githubusercontent.com/danielrosehill/dify-assistant-configs/main/{encoded_path}"
    # Create shields.io badges with links
    view_badge_url = "https://img.shields.io/badge/Config-Open-blue"
    download_badge_url = "https://img.shields.io/badge/Download-DSL-green"
    prettified_name = assistant_name.replace(".yml", "").replace("_", " ").strip()
    
    # Create the row with bold name and optional description in italics
    name_cell = f"🤖 **{prettified_name}**"
    if description:
        # Escape any asterisks in the description
        escaped_description = description.replace("*", "\\*")
        # Add empty line between title and description using double <br>
        name_cell += f"<br><br>_{escaped_description}_"
    
    return f"| {name_cell} | {creation_date} | [![Open Config]({view_badge_url})]({repo_url}) | <a href=\"{raw_url}\" download>![Download DSL]({download_badge_url})</a> |\n"

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

    markdown_table = []
    for file_path in assistant_files:
        assistant_name, creation_date, description = get_assistant_data(file_path)
        markdown_row = generate_markdown_row(assistant_name, creation_date, file_path, description)
        markdown_table.append(markdown_row)

    # Update the README.md file with the generated markdown table.
    readme_path = "README.md"
    with open(readme_path, "r") as f:
        readme_content = f.readlines()

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

    # Insert the new markdown table between the markers
    table_header = [
        "| Assistant Name & Description | Creation Date | URL | Download |\n",
        "|:--------------------------|:--------------|:---:|:---------:|\n",
    ]

    # Remove any duplicate start markers
    readme_content = [line for line in readme_content if line != index_start_marker or readme_content.index(line) == start_index]

    # Remove any duplicate entries
    seen = set()
    unique_rows = []
    for row in markdown_table:
        assistant_name = row.split("|")[1].replace("🤖", "").strip()
        if assistant_name not in seen:
            seen.add(assistant_name)
            unique_rows.append(row)

    # Insert the new content
    readme_content = (
        readme_content[:start_index + 1]
        + table_header
        + unique_rows
        + [index_end_marker]
        + readme_content[end_index + 1:]
    )

    with open(readme_path, "w") as f:
        f.writelines(readme_content)

    print("Assistant index in README.md updated successfully.")

if __name__ == "__main__":
    main()