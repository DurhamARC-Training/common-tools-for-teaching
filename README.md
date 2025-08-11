# Common tools for preparing teaching materials

This repository contains scripts for maintaining teaching materials for our python courses, particularly for converting instructor Jupyter notebooks into student versions. The main script `generate_student_version.py` processes notebooks by removing outputs, cleaning metadata, and selectively removing code based on cell metadata.

This ensures that we only need to edit one version of the course (called `source` here), which contains the completed code and the speaker notes. The work version (called `target` here), which we and the participants fill during the courses, is automatically generated (and should never be edited manually).

## Setup for Existing Repositories

If you're working with a repository that already uses these tools:

```bash
# Initialize and update the submodule
git submodule init
git submodule update

# Or pull with submodules in one command
git pull --recurse-submodules

# Install the pre-commit hook
python common-tools/precommit_setup.py
```

## Working with Cell Metadata

The script supports three modes of code removal using the "remove_code" cell metadata:

### 1. Remove all non-comment code
```json
"remove_code": "non-comments"
```
Preserves only comments while removing all executable code.

### 2. Remove code after a specific comment
```json
"remove_code": "after:# Start removing here"
```
Keeps all code up to the specified comment marker and removes non-comment code after it.

### 3. Remove all content
```json
"remove_code": "all"
```
Removes all cell content, leaving only a newline.

### Setting Cell Metadata in JupyterLab

1. Select the cell you want to modify
2. Click the cogwheels icon in the right sidebar
3. Go to "Advanced Tools" section
4. Add the "remove_code" metadata with your desired value
5. __Confirm the change__ by clicking the green checkmark (if that is missing, you have invalid JSON)
6. Save the notebook

## Troubleshooting

If you encounter an error message in a cell like:
```
# ERROR: Comment marker '# This marker' not found in cell
```

This means the marker specified in the "remove_code" metadata couldn't be found. Double-check that the marker text exactly matches a comment in your cell.

## Setting Up a New Repository

1. Add the common-tools submodule:
   ```bash
   git submodule add https://github.com/DurhamARC-Training/common-tools-for-teaching.git common-tools
   ```

2. Create a `notebook_settings.json` file in the repository root:
   ```json
   {
     "source_path": "Filled_Course/",
     "target_path": "Course/",
     "verbose": false,
     "additional_args": ""
   }
   ```
   **Note:** `source_path` and `target_path` can be either directories (as shown) or specific notebook files.

3. Install the pre-commit hook:
   ```bash
   python common-tools/precommit_setup.py
   ```

4. If you have used folders, create your directory structure:
   ```bash
   mkdir -p Filled_Course Course
   ```

## Pre-commit Hook Integration

The script automatically runs as a git pre-commit hook, generating student versions whenever you commit changes to instructor notebooks.

### How It Works

The pre-commit hook will:
1. Detect changed notebook files in your commit
2. Process notebooks according to your `notebook_settings.json` configuration
3. Automatically add generated student notebooks to your commit

**Note:** The precommit hook will fail if you use `"after:#Comment"` and `#Comment` does not exist in that cell.

### Updating Hook Configuration

To change settings, edit `notebook_settings.json` and run:
```bash
python common-tools/precommit_setup.py
```

## What the Script Does

The `generate_student_version.py` script processes notebooks by:

1. Removing all code outputs and execution counts
2. Removing unnecessary notebook metadata
3. Removing cells with slideshow slide type "notes" or "skip"
4. Making markdown cells non-editable to preserve instructions
5. Modifying code cells with "remove_code" metadata according to specified rules

## Manual Triggering
This should mainly be used for debugging; the pre-commit hook should be preferred.

```bash
# Process a single notebook:
python common-tools/generate_student_version.py --source path/to/source_notebook.ipynb --target path/to/output_notebook.ipynb

# Process all notebooks in a folder:
python common-tools/generate_student_version.py --source path/to/source_folder --target path/to/output_folder

# Show verbose processing information:
python common-tools/generate_student_version.py --source notebook.ipynb --target student_notebook.ipynb --verbose
```