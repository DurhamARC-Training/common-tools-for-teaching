#!/usr/bin/env python3

"""
Usage examples:
    # Process a single notebook
    python filter_notebook.py process instructor_notebook.ipynb student_notebook.ipynb
    
    # Process all notebooks in a folder
    python filter_notebook.py process-folder instructor_folder/ student_folder/
    
This script processes Jupyter notebooks with custom metadata tags to generate
student versions without solutions.

Cell metadata tags used:
- "remove_code": "non-comments"  # Remove code but keep comments in this cell
- "remove_code": "all"           # Remove entire solution (add placeholder)
- "remove_code": "none"          # Keep complete solution (for examples)
- "skip": true                   # Skip this cell entirely in student version
- "notes": true                  # Instructor notes to be removed from student version
"""

import sys
import json
import re
import argparse
import copy
import os
import shutil

# Default placeholders based on cell type
CODE_PLACEHOLDER = "# Your code here\n"
MARKDOWN_PLACEHOLDER = "**Your answer here**\n"

def sanitize_notebook_metadata(notebook):
    """
    Sanitize notebook metadata to prevent unnecessary Git changes,
    while preserving slideshow/presentation metadata.
    
    Args:
        notebook: The notebook object to sanitize
        
    Returns:
        The sanitized notebook object
    """
    # List of metadata fields to remove from notebook-level metadata
    notebook_metadata_to_remove = [
        'widgets',
        'varInspector',
        'notebookname',
        'celltoolbar',
        'collapsed',
        'scrolled'
    ]
    
    # Fields to preserve for presentation features
    notebook_metadata_to_preserve = [
        'kernelspec',
        'language_info',
        'rise',  # RISE presentation extension
        'livereveal',  # Another presentation extension
        'slideshow',  # Jupyter slideshow metadata
        'jupyter-deck'  # Jupyter Deck metadata
    ]
    
    # Remove volatile metadata from notebook, but preserve presentation metadata
    if 'metadata' in notebook:
        new_metadata = {}
        # First, copy all preserved fields that exist
        for field in notebook_metadata_to_preserve:
            if field in notebook['metadata']:
                new_metadata[field] = notebook['metadata'][field]
        
        # Then, copy any fields not in the removal list
        for field in notebook['metadata']:
            if field not in notebook_metadata_to_remove and field not in notebook_metadata_to_preserve:
                new_metadata[field] = notebook['metadata'][field]
        
        notebook['metadata'] = new_metadata
    
    # Sanitize cell-level metadata
    for cell in notebook.get('cells', []):
        # Essential fields to preserve
        essential_fields = [
            'remove_code', 
            'skip', 
            'notes',
            'slideshow',  # Slideshow metadata for presentations
            'slide_type'  # Slide type for presentations
        ]
        
        if 'metadata' in cell:
            # Create a new metadata dict with only the essential fields
            new_metadata = {}
            for field in essential_fields:
                if field in cell['metadata']:
                    new_metadata[field] = cell['metadata'][field]
            
            # Also preserve any jupyter-deck related metadata
            for field in cell['metadata']:
                if field.startswith('jupyter-deck') or field.startswith('rise'):
                    new_metadata[field] = cell['metadata'][field]
            
            # Replace the cell metadata with the sanitized version
            cell['metadata'] = new_metadata
    
    return notebook

def process_notebook(input_file, output_file):
    """
    Process a Jupyter notebook, filtering solutions based on metadata tags.
    
    Args:
        input_file (str): Path to input notebook (instructor version)
        output_file (str): Path to output notebook (student version)
    """
    # Read the notebook file
    with open(input_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Create a copy of the notebook to modify
    student_notebook = copy.deepcopy(notebook)
    filtered_cells = []
    
    # Process each cell
    for cell in student_notebook['cells']:
        # Check for cells to skip entirely
        if cell.get('metadata', {}).get('skip', False):
            continue
            
        # Check for instructor notes
        if cell.get('metadata', {}).get('notes', False):
            continue
            
        # Clear all outputs regardless of cell type
        if 'outputs' in cell:
            cell['outputs'] = []
            
        # Set execution_count to null for all code cells
        if 'execution_count' in cell:
            cell['execution_count'] = None
            
        # Process cells with remove_code property
        if 'remove_code' in cell.get('metadata', {}):
            remove_code = cell['metadata']['remove_code']
            
            # Handle different remove_code types
            if remove_code == 'none':
                # Keep the entire solution
                pass
            elif remove_code == 'all':
                # Replace the entire cell with a placeholder
                if cell['cell_type'] == 'code':
                    cell['source'] = [CODE_PLACEHOLDER]
                else:
                    cell['source'] = [MARKDOWN_PLACEHOLDER]
            elif remove_code == 'non-comments':
                # Keep only comments and blank lines
                if cell['cell_type'] == 'code':
                    new_source = []
                    for line in cell['source']:
                        if line.strip().startswith('#') or not line.strip():
                            new_source.append(line)
                    # Add placeholder if needed
                    if not new_source:
                        new_source = [CODE_PLACEHOLDER]
                    cell['source'] = new_source
                else:
                    # For markdown cells, just add the placeholder
                    cell['source'] = [MARKDOWN_PLACEHOLDER]
        
        # Add cell to filtered list
        filtered_cells.append(cell)
    
    # Update the notebook with filtered cells
    student_notebook['cells'] = filtered_cells
    
    # Sanitize notebook metadata to prevent unnecessary Git changes
    student_notebook = sanitize_notebook_metadata(student_notebook)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    # Write the filtered notebook
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(student_notebook, f, indent=1)
        
    print(f"Created student version: {output_file}")

def process_folder(input_folder, output_folder):
    """
    Process all notebooks in a folder, generating student versions.
    
    Args:
        input_folder (str): Path to input folder containing instructor notebooks
        output_folder (str): Path to output folder for student notebooks
    """
    # Check if input folder exists
    if not os.path.isdir(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Keep track of processed files
    processed_files = 0
    
    # Process each .ipynb file in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.ipynb'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)
            
            process_notebook(input_file, output_file)
            processed_files += 1
    
    # Copy any non-notebook files to the output folder
    for filename in os.listdir(input_folder):
        if not filename.endswith('.ipynb'):
            src = os.path.join(input_folder, filename)
            dst = os.path.join(output_folder, filename)
            
            # Skip directories (process them separately if needed)
            if os.path.isdir(src):
                continue
                
            shutil.copy2(src, dst)
            print(f"Copied file: {dst}")
    
    print(f"Processed {processed_files} notebooks from {input_folder} to {output_folder}")

def add_code_removal_metadata(input_file, output_file):
    """
    Utility function to help add remove_code metadata to cells containing solution markers.
    This helps migrate from comment-based to metadata-based approach.
    
    Args:
        input_file (str): Path to input notebook
        output_file (str): Path to output notebook with metadata added
    """
    # Read the notebook file
    with open(input_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells_updated = 0
    
    for cell in notebook['cells']:
        source = ''.join(cell['source'])
        
        # Look for solution markers in code or markdown
        if "# Solution" in source or "<!-- #solution -->" in source:
            if 'metadata' not in cell:
                cell['metadata'] = {}
            
            # Try to determine remove_code value based on content
            if "# KEEP ALL" in source or "<!-- KEEP ALL -->" in source:
                cell['metadata']['remove_code'] = 'none'
            elif "# HIDE ALL" in source or "<!-- HIDE ALL -->" in source:
                cell['metadata']['remove_code'] = 'all'
            else:
                cell['metadata']['remove_code'] = 'non-comments'
                
            cells_updated += 1
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    # Write the updated notebook
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)
        
    print(f"Added metadata to {cells_updated} cells in: {output_file}")

def add_metadata_folder(input_folder, output_folder):
    """
    Add remove_code metadata to all notebooks in a folder.
    
    Args:
        input_folder (str): Path to input folder containing notebooks
        output_folder (str): Path to output folder for updated notebooks
    """
    # Check if input folder exists
    if not os.path.isdir(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Keep track of processed files
    processed_files = 0
    
    # Process each .ipynb file in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.ipynb'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)
            
            add_code_removal_metadata(input_file, output_file)
            processed_files += 1
    
    # Copy any non-notebook files to the output folder
    for filename in os.listdir(input_folder):
        if not filename.endswith('.ipynb'):
            src = os.path.join(input_folder, filename)
            dst = os.path.join(output_folder, filename)
            
            # Skip directories
            if os.path.isdir(src):
                continue
                
            shutil.copy2(src, dst)
            print(f"Copied file: {dst}")
    
    print(f"Processed metadata for {processed_files} notebooks from {input_folder} to {output_folder}")

def main():
    parser = argparse.ArgumentParser(description="Process Jupyter notebooks with code removal metadata")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Process notebook command
    process_parser = subparsers.add_parser("process", help="Process notebook to create student version")
    process_parser.add_argument("input_file", help="Input notebook (instructor version)")
    process_parser.add_argument("output_file", help="Output notebook (student version)")
    
    # Process folder command
    process_folder_parser = subparsers.add_parser("process-folder", 
                                                 help="Process all notebooks in a folder")
    process_folder_parser.add_argument("input_folder", help="Input folder (instructor versions)")
    process_folder_parser.add_argument("output_folder", help="Output folder (student versions)")
    
    # Add metadata command
    add_metadata_parser = subparsers.add_parser("add-metadata", 
                                               help="Add code removal metadata to cells with solution markers")
    add_metadata_parser.add_argument("input_file", help="Input notebook")
    add_metadata_parser.add_argument("output_file", help="Output notebook with metadata added")
    
    # Add metadata to folder command
    add_metadata_folder_parser = subparsers.add_parser("add-metadata-folder",
                                                      help="Add code removal metadata to all notebooks in a folder")
    add_metadata_folder_parser.add_argument("input_folder", help="Input folder")
    add_metadata_folder_parser.add_argument("output_folder", help="Output folder for notebooks with metadata")
    
    args = parser.parse_args()
    
    if args.command == "process":
        process_notebook(args.input_file, args.output_file)
    elif args.command == "process-folder":
        process_folder(args.input_folder, args.output_folder)
    elif args.command == "add-metadata":
        add_code_removal_metadata(args.input_file, args.output_file)
    elif args.command == "add-metadata-folder":
        add_metadata_folder(args.input_folder, args.output_folder)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()