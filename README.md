# Common tools for preparing teaching materials

This repository contains various scripts that can help maintain teaching materials, such as Python courses. To use them, you must add this repository as a Git submodule, for example:
```bash
git submodule add https://github.com/DurhamARC-Training/common-tools-for-teaching.git common-tools
```

## generate_student_version.py

`generate_student_version.py` is a script that processes Jupyter notebooks for teaching purposes by:

1. Removing all code outputs
2. Removing unnecessary notebook metadata
3. Removing cell execution counts
4. Removing cells with slideshow slide type "notes" or "skip"
5. Making markdown cells non-editable to preserve instructions
6. Modifying code cells with "remove_code" metadata according to specified rules

### Installation

No special installation is required other than having Python installed. The script uses only standard library modules.

# Pre-commit Hook Integration

The script can be set up to run automatically as a git pre-commit hook, generating student versions whenever you commit changes to your instructor notebooks.
Notice that the precommit hook will fail if you used `"after:#Comment"` and `#Comment` does not exist in that cell.

## Standard Configuration

Each repository should include a `notebook_settings.json` file in the root directory with standardized paths, for example:

```json
{
  "source_path": "Filled_Course/",
  "target_path": "Course/",
  "verbose": false,
  "additional_args": ""
}
```

This ensures all contributors use the same source and target paths, preventing accidental mixing of instructor and student content or the generation of multiple student
folders or notebooks.

## Setup

After adding the common-tools submodule to your repository, you can set up the pre-commit hook:

```bash
# Using settings from notebook_settings.json
python common-tools/precommit_setup.py

# Or with custom paths (only use if necessary, a settings json should always be preferred)
python common-tools/precommit_setup.py --source Custom_Path/ --target Custom_Target/
```

## How It Works

Once installed, the pre-commit hook will:

1. Detect if any notebook files have been changed in your commit
2. If the source path is a directory, process all notebooks in that directory
3. If the source path is a specific file, process only that file if it has changed
4. Automatically add the generated student notebooks to your commit

## Setting Up a New Repository

For a new teaching repository:

1. Add the common-tools submodule:
   ```bash
   git submodule add https://github.com/DurhamARC-Training/common-tools-for-teaching.git common-tools
   ```

2. Create a `notebook_settings.json` file in the repository root with your desired paths

3. Install the pre-commit hook:
   ```bash
   python common-tools/precommit_setup.py
   ```

4. Create your directory structure:
   ```bash
   mkdir -p Filled_Course Student_Course
   ```

## Updating Hook Configuration

To change the configuration, edit `notebook_settings.json` and then run the setup script again:

```bash
python common-tools/setup_precommit_hook.py
```

## Manual Triggering

```bash
# Process a single notebook:
python common-tools/generate_student_version.py --source path/to/source_notebook.ipynb --target path/to/output_notebook.ipynb

# Process all notebooks in a folder:
python common-tools/generate_student_version.py --source path/to/source_folder --target path/to/output_folder

# Show verbose processing information:
python common-tools/generate_student_version.py --source notebook.ipynb --target student_notebook.ipynb --verbose
```


### Working with "remove_code" Cell Metadata

The script supports three modes of code removal in cells with the "remove_code" metadata:

1. **Remove all non-comment code:**
   ```json
   "remove_code": "non-comments"
   ```
   This preserves only comments in the cell while removing all executable code.

2. **Remove code after a specific comment:**
   ```json
   "remove_code": "after:# Start removing here"
   ```
   This keeps all code up to the specified comment marker and removes non-comment code after it.
   Note that spaces after "after:" are automatically trimmed.

3. **Remove all content:**
   ```json
   "remove_code": "all"
   ```
   This removes all cell content, both comments and code, leaving only a newline.

### Setting Cell Metadata in JupyterLab

To set the "remove_code" attribute for a cell in JupyterLab:

1. Open the notebook in JupyterLab
2. Click on the cell you want to modify
3. Click on the two cogwheels on the top of the right sidebar
4. Go to "Advanced Tools" section 
5. Add the "remove_code" metadata with one of the supported values:
   ```json
   {
     "remove_code": "non-comments"
   }
   ```
   or
   ```json
   {
     "remove_code": "after:# Start removing here"
   }
   ```
   or
   ```json
   {
     "remove_code": "all"
   }
   ```
6. Be sure to confirm the change by clicking on the green checkmark. If there is no checkmark your JSON is invalid.
7. Save the notebook

### Notes

- Markdown cells are automatically made non-editable in the output notebook, ensuring that instructions and explanations cannot be modified by students
- Cells with slideshow slide type set to "notes" or "skip" are completely removed from the output notebook
- All code outputs and execution counts are removed to ensure a clean starting point for students
- The script preserves essential notebook metadata but removes unnecessary elements

### Troubleshooting

If you encounter an error message in a cell like:
```
# ERROR: Comment marker '# This marker' not found in cell
```

This means that the marker specified in the "remove_code" metadata couldn't be found in the cell. Double-check that the marker text exactly matches a comment in your cell.
