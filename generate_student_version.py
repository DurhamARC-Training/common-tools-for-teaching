#!/usr/bin/env python3
"""
Jupyter Notebook Cleaner

This script processes Jupyter notebooks by:
1. Removing all code outputs
2. Removing unnecessary notebook metadata
3. Removing cell execution counts
4. Removing cells with slideshow slide type "notes" or "skip"
5. Modifying code cells with "remove_code" metadata according to specified rules
6. Making markdown cells non-editable

Usage:
    Process a single notebook:
    python notebook_cleaner.py --source path/to/source_notebook.ipynb --target path/to/output_notebook.ipynb
    
    Process all notebooks in a folder:
    python notebook_cleaner.py --source path/to/source_folder --target path/to/output_folder
"""

import json
import sys
import re
import copy
import argparse
from pathlib import Path


def clean_notebook(source_path, target_path, verbose=False):
    """
    Process a Jupyter notebook according to specified cleaning rules.
    
    Args:
        source_path (Path): Path to the source notebook
        target_path (Path): Path where the cleaned notebook will be saved
        verbose (bool): Whether to display detailed processing information
    """
    if verbose:
        print(f"Processing: {source_path} -> {target_path}")
    
    try:
        with source_path.open('r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"Error loading notebook {source_path}: {e}")
        sys.exit(1)
    
    # Create a deep copy to avoid modifying the original while iterating
    cleaned_notebook = copy.deepcopy(notebook)
    
    # Clean notebook metadata
    clean_metadata(cleaned_notebook)
    if verbose:
        print("  Cleaned metadata")
    
    # Process cells
    original_cell_count = len(cleaned_notebook['cells'])
    cleaned_notebook['cells'] = process_cells(cleaned_notebook['cells'], verbose)
    final_cell_count = len(cleaned_notebook['cells'])
    
    if verbose:
        print(f"  Removed {original_cell_count - final_cell_count} cells")
    
    # Create parent directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the cleaned notebook
    try:
        with target_path.open('w', encoding='utf-8') as f:
            json.dump(cleaned_notebook, f, indent=1)
        print(f"Successfully created: {target_path}")
    except Exception as e:
        print(f"Error saving notebook {target_path}: {e}")
        sys.exit(1)


def clean_metadata(notebook):
    """
    Remove unnecessary metadata from the notebook.
    
    Args:
        notebook (dict): The notebook object
    """
    # Keep only essential metadata
    essential_keys = ['kernelspec', 'language_info', 'nbformat', 'nbformat_minor']
    if 'metadata' in notebook:
        cleaned_metadata = {k: notebook['metadata'][k] for k in essential_keys if k in notebook['metadata']}
        notebook['metadata'] = cleaned_metadata


def process_cells(cells, verbose=False):
    """
    Process all cells in the notebook according to the rules.
    
    Args:
        cells (list): List of cell dictionaries
        verbose (bool): Whether to display detailed processing information
        
    Returns:
        list: Processed cells
    """
    cleaned_cells = []
    removed_cells = 0
    processed_code_cells = 0
    markdown_cells_locked = 0
    
    for cell in cells:
        # Skip cells with slideshow slide type "notes" or "skip"
        if should_skip_cell(cell):
            removed_cells += 1
            if verbose:
                print(f"  Skipping cell with slide type: {cell['metadata'].get('slideshow', {}).get('slide_type', 'unknown')}")
            continue
        
        # Make markdown cells non-editable
        if cell['cell_type'] == 'markdown':
            if 'metadata' not in cell:
                cell['metadata'] = {}
            cell['metadata']['editable'] = False
            markdown_cells_locked += 1
        
        # Remove execution count for code cells
        if cell['cell_type'] == 'code':
            cell['execution_count'] = None
            
            # Remove outputs
            output_count = len(cell.get('outputs', []))
            cell['outputs'] = []
            
            if verbose and output_count > 0:
                print(f"  Removed {output_count} outputs from code cell")
            
            # Process "remove_code" metadata if present
            if 'metadata' in cell and 'remove_code' in cell['metadata']:
                process_remove_code(cell, verbose)
                processed_code_cells += 1
                
        # Add the processed cell to our list
        cleaned_cells.append(cell)
    
    if verbose:
        print(f"  Processed {processed_code_cells} code cells with 'remove_code' metadata")
        print(f"  Made {markdown_cells_locked} markdown cells non-editable")
        print(f"  Removed {removed_cells} cells with 'notes' or 'skip' slide type")
    
    return cleaned_cells


def should_skip_cell(cell):
    """
    Determine if a cell should be skipped based on slideshow metadata.
    
    Args:
        cell (dict): Cell dictionary
        
    Returns:
        bool: True if the cell should be skipped, False otherwise
    """
    if 'metadata' in cell and 'slideshow' in cell['metadata']:
        slide_type = cell['metadata']['slideshow'].get('slide_type', '')
        if slide_type in ['notes', 'skip']:
            return True
    return False


def process_remove_code(cell, verbose=False):
    """
    Process code cells with "remove_code" metadata.
    
    Args:
        cell (dict): Cell dictionary
        verbose (bool): Whether to display detailed processing information
    """
    remove_code_value = cell['metadata']['remove_code']
    
    # Handle source being either a string or a list of strings
    if isinstance(cell['source'], list):
        source_lines = cell['source']
    else:
        source_lines = cell['source'].splitlines()
    
    if verbose:
        print(f"  Processing code removal with mode: {remove_code_value}")
    
    if remove_code_value == "non-comments":
        cell['source'] = process_non_comments(source_lines, verbose)
    elif remove_code_value == "all":
        cell['source'] = ["\n"]
    elif remove_code_value.startswith("after:"):
        comment_marker = remove_code_value[6:].strip()  # Extract the comment after "after:"
        cell['source'] = process_after_comment(source_lines, comment_marker, verbose)
    else:
        if verbose:
            print(f"  Unknown remove_code value: {remove_code_value}, leaving cell unchanged")


def process_non_comments(source_lines, verbose=False):
    """
    Remove all non-comment code lines but preserve single newlines between comments.
    
    Args:
        source_lines (list): List of source code lines
        verbose (bool): Whether to display detailed processing information
        
    Returns:
        list: Processed source code as a list of lines
    """
    result = []
    prev_was_comment = False
    non_comment_lines_removed = 0
    
    for line in source_lines:
        stripped = line.strip()
        is_comment = stripped.startswith('#')
        
        if is_comment:
            # Add a newline between comments if needed
            if not prev_was_comment and len(result) > 0 and result[-1].strip():
                result.append('\n')
            result.append(line)
            prev_was_comment = True
        else:
            if stripped:  # Only count non-empty lines
                non_comment_lines_removed += 1
            prev_was_comment = False
    
    if verbose:
        print(f"  Removed {non_comment_lines_removed} non-comment lines")
    
    return result


def process_after_comment(source_lines, comment_marker, verbose=False):
    """
    Remove code lines (but not comments) after a specific comment.
    
    Args:
        source_lines (list): List of source code lines
        comment_marker (str): The marker comment after which code should be removed
        verbose (bool): Whether to display detailed processing information
        
    Returns:
        list: Processed source code as a list of lines
    """
    result = []
    remove_mode = False
    prev_was_comment = False
    non_comment_lines_removed = 0
    
    # Check if the comment marker appears exactly once
    comment_occurrences = 0
    for line in source_lines:
        if line.strip() == comment_marker:
            comment_occurrences += 1
    
    if comment_occurrences == 0:
        error_msg = f"ERROR: Comment marker '{comment_marker}' not found in cell"
        print(error_msg)
        error_line = f"# {error_msg}"
        return [error_line] + source_lines
    
    if comment_occurrences > 1:
        error_msg = f"ERROR: Comment marker '{comment_marker}' appears multiple times in cell"
        print(error_msg)
        error_line = f"# {error_msg}"
        return [error_line] + source_lines
    
    for line in source_lines:
        stripped = line.strip()
        is_comment = stripped.startswith('#')
        
        if not remove_mode:
            result.append(line)
            if stripped == comment_marker:
                remove_mode = True
                prev_was_comment = True
        else:
            if is_comment:
                # Add a newline between comments if needed
                if not prev_was_comment and len(result) > 0 and result[-1].strip():
                    result.append('\n')
                result.append(line)
                prev_was_comment = True
            else:
                if stripped:  # Only count non-empty lines
                    non_comment_lines_removed += 1
                prev_was_comment = False
    
    if verbose:
        print(f"  Removed {non_comment_lines_removed} non-comment lines after marker")
    
    return result


def process_folder(source_folder, target_folder, verbose=False):
    """
    Process all notebooks in the source folder and output them to the target folder.
    
    Args:
        source_folder (Path): Path to the source folder containing notebooks
        target_folder (Path): Path where the cleaned notebooks will be saved
        verbose (bool): Whether to display detailed processing information
    """
    # Create the target folder if it doesn't exist
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all Jupyter notebooks in the source folder
    notebook_paths = list(source_folder.glob("*.ipynb"))
    
    if not notebook_paths:
        print(f"No notebooks found in {source_folder}")
        return
    
    print(f"Found {len(notebook_paths)} notebooks to process.")
    
    for notebook_path in notebook_paths:
        # Get the target path with same filename
        target_path = target_folder / notebook_path.name
        
        if verbose:
            print(f"\nProcessing: {notebook_path.name}")
        
        clean_notebook(notebook_path, target_path, verbose)
    
    print(f"\nAll notebooks have been processed and saved to {target_folder}")


def main():
    """Main function to run the script with argparse."""
    parser = argparse.ArgumentParser(
        description="Process Jupyter notebooks to create student versions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a single notebook:
    python notebook_cleaner.py --source notebook.ipynb --target student_notebook.ipynb
    
  Process all notebooks in a folder:
    python notebook_cleaner.py --source notebooks_folder --target student_notebooks_folder
        """
    )
    
    parser.add_argument(
        "--source", "-s", 
        required=True,
        type=Path,
        help="Source notebook file or folder containing notebooks"
    )
    
    parser.add_argument(
        "--target", "-t", 
        required=True,
        type=Path,
        help="Target notebook file or folder where processed notebooks will be saved"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Display detailed processing information"
    )
    
    args = parser.parse_args()
    
    source_path = args.source
    target_path = args.target
    verbose = args.verbose
    
    # Determine if we're processing a single file or a folder
    if source_path.is_dir():
        if not target_path.is_dir() and target_path.exists():
            print(f"Error: {target_path} exists but is not a directory")
            sys.exit(1)
        process_folder(source_path, target_path, verbose)
    else:
        clean_notebook(source_path, target_path, verbose)


if __name__ == "__main__":
    main()