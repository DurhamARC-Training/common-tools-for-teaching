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

### Usage

```bash
# Process a single notebook:
python common-tools/generate_student_version.py --source path/to/source_notebook.ipynb --target path/to/output_notebook.ipynb

# Process all notebooks in a folder:
python common-tools/generate_student_version.py --source path/to/source_folder --target path/to/output_folder

# Show verbose processing information:
python common-tools/generate_student_version.py --source notebook.ipynb --target student_notebook.ipynb --verbose
```

### Command-line Options

- `--source`, `-s`: Source notebook file or folder containing notebooks (required)
- `--target`, `-t`: Target notebook file or folder where processed notebooks will be saved (required)
- `--verbose`, `-v`: Display detailed processing information
- `--help`, `-h`: Show help message

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
3. Click on the Property Inspector icon (ⓘ) in the right sidebar, or click on the two cogwheels on the top right
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
6. Be sure to confirm the change by clicking on the green checkmark
7. Save the notebook

### Examples

**Example 1:** Create a student version of a single notebook
```bash
python common-tools/generate_student_version.py --source instructor_notebook.ipynb --target student_notebook.ipynb
```

**Example 2:** Process all notebooks in a course folder
```bash
python common-tools/generate_student_version.py --source Filled_Course/ --target Student_Course/
```

**Example 3:** Get detailed information about the processing
```bash
python common-tools/generate_student_version.py --source complex_notebook.ipynb --target student_version.ipynb --verbose
```

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
