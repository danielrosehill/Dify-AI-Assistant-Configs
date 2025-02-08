# Create Github assistant index

Generate a script that does the following:

- The 'assistants' folder in the repository contains a list of various confrigurations for AI assistants. Each one is provided as a .yml file. They are organised into folders (and subfolders) for organisation. The script should have recursive logic to find all of them.

The purpose of the script would be to:

- Generate an update a JSON to be stored in the 'indexes' folder. 

The JSON file should contain, for each assistant

- Its prettified title. The file extension (.yml) should be removed so that it's easier to read.
- The public Github URL for the configuration. For example: https://github.com/danielrosehill/My-AI-Assistant-Library/blob/main/assistants/data-utilities/Open%20Access%20Data%20Finder.yml
