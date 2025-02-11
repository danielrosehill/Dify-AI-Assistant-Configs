import os
import datetime
import subprocess

def get_assistant_data(assistant_path):
    """Extracts assistant data from the file path."""
    assistant_name = os.path.basename(assistant_path).replace(".yml", "").replace("_", " ").strip()
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(assistant_path)).strftime('%Y-%m-%d')
    return assistant_name, creation_date

def generate_markdown_row(assistant_name, creation_date, file_path):
    """Generates a markdown table row for the assistant."""
    # Encode file path for URLs
    encoded_path = file_path.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    repo_url = f"https://github.com/danielrosehill/My-AI-Assistant-Library/blob/main/{encoded_path}"
    # Create shields.io badge with link
    badge_url = "https://img.shields.io/badge/Config-Open-blue"
    prettified_name = assistant_name.replace(".yml", "").replace("_", " ").strip()
    return f"| 🤖 {prettified_name} | {creation_date} | [![Open Config]({badge_url})]({repo_url}) |\n"

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
        assistant_name, creation_date = get_assistant_data(file_path)
        markdown_row = generate_markdown_row(assistant_name, creation_date, file_path)
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
        if line == index_start_marker:
            start_index = i
        elif line == index_end_marker:
            end_index = i

    if start_index == -1 or end_index == -1:
        print("Index markers not found in README.md. Please add them.")
        return

    # Remove existing table rows between the markers
    del readme_content[start_index + 1:end_index]

    # Insert the new markdown table between the markers
    table_header = [
        "| Assistant Name | Creation Date | URL |\n",
        "|---|---|---|\n",
    ]
    # Remove any duplicate entries
    seen = set()
    unique_rows = []
    for row in markdown_table:
        # Extract assistant name from the first column (index 1 after split)
        # Format is "| 🤖 Name | Date | URL |"
        assistant_name = row.split("|")[1].replace("🤖", "").strip()
        if assistant_name not in seen:
            seen.add(assistant_name)
            unique_rows.append(row)

    readme_content = (
        readme_content[: start_index + 1]
        + table_header
        + unique_rows
        + readme_content[end_index:]
    )

    with open(readme_path, "w") as f:
        f.writelines(readme_content)

    print("Assistant index in README.md updated successfully.")

if __name__ == "__main__":
    main()