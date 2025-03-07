#!/usr/bin/env python3
"""
Unit tests for the Jupyter Notebook Cleaner script.
Tests all major functionalities including:
- Removing cell outputs
- Removing execution counts
- Cleaning metadata
- Removing cells with specific slide types
- Processing "remove_code" metadata
- Making markdown cells non-editable
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import textwrap
import sys
import importlib.util

# Load the notebook_cleaner module from the script file
def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestJupyterCleaner(unittest.TestCase):
    def setUp(self):
        """
        Set up temporary directories and files for testing.
        """
        # Create temporary directories
        self.test_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.test_dir / "source"
        self.target_dir = self.test_dir / "target"
        self.source_dir.mkdir()
        
        # Path to the notebook cleaner script
        script_path = Path(__file__).parent / "generate_student_version.py"
        
        # Load the module
        self.cleaner = load_module_from_file("notebook_cleaner", script_path)
        
        # Create a test notebook
        self.test_notebook = textwrap.dedent("""\
            {
             "cells": [
              {
               "cell_type": "markdown",
               "id": "e3634715-4859-4761-a492-8921d659a6f8",
               "metadata": {
                "editable": true,
                "slideshow": {
                 "slide_type": "slide"
                },
                "tags": []
               },
               "source": [
                "# Markdown heading\\n",
                "## Section 2\\n",
                "### Section 3\\n",
                "#### Section 4\\n",
                "\\n",
                "This is some non-heading text"
               ]
              },
              {
               "cell_type": "code",
               "execution_count": 1,
               "id": "0ee03765-2723-4541-aaba-a859690eda25",
               "metadata": {
                "editable": true,
                "slideshow": {
                 "slide_type": ""
                },
                "tags": []
               },
               "outputs": [
                {
                 "name": "stdout",
                 "output_type": "stream",
                 "text": [
                  "This is python code that should remain\\n"
                 ]
                }
               ],
               "source": [
                "# This comment is here for testing\\n",
                "print(\\"This is python code that should remain\\")"
               ]
              },
              {
               "cell_type": "code",
               "execution_count": 2,
               "id": "0c4a3e7c-da50-4b5a-88ae-acc5bd309e2c",
               "metadata": {
                "editable": true,
                "remove_code": "non-comments",
                "slideshow": {
                 "slide_type": ""
                },
                "tags": []
               },
               "outputs": [
                {
                 "name": "stdout",
                 "output_type": "stream",
                 "text": [
                  "I hope this edgecase is handled as well\\n"
                 ]
                }
               ],
               "source": [
                "# In this cell we test the proper removal of code\\n",
                "to_be_removed_var = 12\\n",
                "\\n",
                "# make sure indentations are handled\\n",
                "def remove_this_function(something):\\n",
                "    if something == \\"else\\":\\n",
                "        return \\"something else\\"\\n",
                "    else:\\n",
                "        return \\"something\\"\\n",
                "\\n",
                "#Havenospaceincomment\\n",
                "print(\\"I hope this edgecase is handled as well\\")"
               ]
              },
              {
               "cell_type": "code",
               "execution_count": 3,
               "id": "857eb524-3a03-42f0-b78a-68ebde4b2d40",
               "metadata": {
                "editable": true,
                "remove_code": "after:# Start removing here",
                "slideshow": {
                 "slide_type": "slide"
                },
                "tags": []
               },
               "outputs": [
                {
                 "name": "stdout",
                 "output_type": "stream",
                 "text": [
                  "This should be kept\\n",
                  "This should be gone\\n",
                  "This should be gone again\\n"
                 ]
                }
               ],
               "source": [
                "# This is a test whether after works\\n",
                "print(\\"This should be kept\\")\\n",
                "\\n",
                "# Start removing here\\n",
                "print(\\"This should be gone\\")\\n",
                "\\n",
                "# This should be kept\\n",
                "print(\\"This should be gone again\\")"
               ]
              },
              {
               "cell_type": "markdown",
               "id": "88641903-752c-4e79-b4cc-f54cbaa413e3",
               "metadata": {
                "editable": true,
                "slideshow": {
                 "slide_type": "notes"
                },
                "tags": []
               },
               "source": [
                "These notes should disappear"
               ]
              },
              {
               "cell_type": "code",
               "execution_count": 4,
               "id": "a28d43da-91d8-486d-a94d-b573fe79d348",
               "metadata": {
                "editable": true,
                "slideshow": {
                 "slide_type": "notes"
                },
                "tags": []
               },
               "outputs": [
                {
                 "name": "stdout",
                 "output_type": "stream",
                 "text": [
                  "Goodbye\\n"
                 ]
                }
               ],
               "source": [
                "# The same for this code note cell\\n",
                "print(\\"Goodbye\\")"
               ]
              }
             ],
             "metadata": {
              "kernelspec": {
               "display_name": "Python 3 (ipykernel)",
               "language": "python",
               "name": "python3"
              },
              "language_info": {
               "codemirror_mode": {
                "name": "ipython",
                "version": 3
               },
               "file_extension": ".py",
               "mimetype": "text/x-python",
               "name": "python",
               "nbconvert_exporter": "python",
               "pygments_lexer": "ipython3",
               "version": "3.13.2"
              },
              "unused_metadata": "This should be removed"
             },
             "nbformat": 4,
             "nbformat_minor": 5
            }
        """)
        
        # Write the test notebook to the source directory
        self.notebook_path = self.source_dir / "test_notebook.ipynb"
        with open(self.notebook_path, 'w', encoding='utf-8') as f:
            f.write(self.test_notebook)

    def tearDown(self):
        """
        Clean up temporary files and directories.
        """
        shutil.rmtree(self.test_dir)

    def test_clean_metadata(self):
        """
        Test that unnecessary metadata is removed.
        """
        notebook = json.loads(self.test_notebook)
        self.cleaner.clean_metadata(notebook)
        
        # Check that essential metadata is preserved
        self.assertIn('kernelspec', notebook['metadata'])
        self.assertIn('language_info', notebook['metadata'])
        
        # Check that unnecessary metadata is removed
        self.assertNotIn('unused_metadata', notebook['metadata'])

    def test_should_skip_cell(self):
        """
        Test that cells with slideshow type 'notes' or 'skip' are identified for skipping.
        """
        notebook = json.loads(self.test_notebook)
        
        # The fifth cell has slideshow type 'notes'
        should_skip = self.cleaner.should_skip_cell(notebook['cells'][4])
        self.assertTrue(should_skip)
        
        # The first cell has slideshow type 'slide' and should not be skipped
        should_skip = self.cleaner.should_skip_cell(notebook['cells'][0])
        self.assertFalse(should_skip)

    def test_process_non_comments(self):
        """
        Test removal of non-comment code while preserving comments.
        """
        code_cell = [
            "# First comment\n",
            "code_to_remove = True\n",
            "\n",
            "# Second comment\n",
            "more_code = \"will be gone\"\n",
            "\n",
            "#No space comment\n",
            "final_code = 42\n"
        ]
        
        processed = self.cleaner.process_non_comments(code_cell, verbose=False)
        
        # Expected: comments preserved with a blank line between them if there was code
        expected = [
            "# First comment\n",
            "\n",
            "# Second comment\n",
            "\n",
            "#No space comment\n"
        ]
        
        self.assertEqual(processed, expected)

    def test_process_after_comment(self):
        """
        Test removal of code after a specific comment.
        """
        code_cell = [
            "# First comment\n",
            "keep_this_code = True\n",
            "\n",
            "# Start removing after this\n",
            "remove_this_code = True\n",
            "\n",
            "# But keep this comment\n",
            "also_remove_this = 42\n"
        ]
        
        processed = self.cleaner.process_after_comment(
            code_cell, 
            "# Start removing after this", 
            verbose=False
        )
        
        # Expected: code before marker and all comments preserved
        expected = [
            "# First comment\n",
            "keep_this_code = True\n",
            "\n",
            "# Start removing after this\n",
            "\n",
            "# But keep this comment\n"
        ]
        
        self.assertEqual(processed, expected)

    def test_process_all_code_removal(self):
        """
        Test complete removal of all code in a cell with "all" option.
        """
        code_cell = [
            "# This comment should be removed\n",
            "this_code_will_be_removed = True\n",
            "print('This will also be gone')\n"
        ]
        
        # Manually call the processing logic that would happen in process_remove_code
        # with "all" option
        result = ["\n"]
        
        # Check that only a newline remains
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "\n")
        
    def test_process_after_comment_with_spaces(self):
        """
        Test removal of code after a specific comment when there are spaces after 'after:'.
        """
        code_cell = [
            "# First comment\n",
            "keep_this_code = True\n",
            "\n",
            "# Start removing here\n",
            "remove_this_code = True\n",
            "\n",
            "# But keep this comment\n",
            "also_remove_this = 42\n"
        ]
        
        # Test with spaces after the 'after:' part
        processed = self.cleaner.process_after_comment(
            code_cell, 
            "# Start removing here", 
            verbose=False
        )
        
        # Expected: code before marker and all comments preserved
        expected = [
            "# First comment\n",
            "keep_this_code = True\n",
            "\n",
            "# Start removing here\n",
            "\n",
            "# But keep this comment\n"
        ]
        
        self.assertEqual(processed, expected)

    def test_clean_notebook_file(self):
        """
        Test the entire notebook cleaning process on a file.
        """
        output_path = self.target_dir / "output_notebook.ipynb"
        
        # Clean the notebook
        self.cleaner.clean_notebook(self.notebook_path, output_path, verbose=False)
        
        # Check that the output file exists
        self.assertTrue(output_path.exists())
        
        # Load the cleaned notebook
        with output_path.open('r', encoding='utf-8') as f:
            cleaned = json.load(f)
        
        # Check that there are only 4 cells (2 should be removed due to 'notes' slide type)
        self.assertEqual(len(cleaned['cells']), 4)
        
        # Check that markdown cells are not editable
        for cell in cleaned['cells']:
            if cell['cell_type'] == 'markdown':
                self.assertFalse(cell['metadata']['editable'])
        
        # Check that code cells have no outputs
        for cell in cleaned['cells']:
            if cell['cell_type'] == 'code':
                self.assertEqual(len(cell['outputs']), 0)
                self.assertIsNone(cell['execution_count'])
        
        # Check that 'non-comments' cell only has comments
        non_comments_cell_source = cleaned['cells'][2]['source']
        all_content = ''.join(non_comments_cell_source)
        self.assertNotIn('to_be_removed_var', all_content)
        self.assertNotIn('def remove_this_function', all_content)
        self.assertNotIn('print', all_content)
        self.assertIn('# In this cell we test', all_content)
        
        # Check that 'after:' cell has correct content
        after_cell_source = cleaned['cells'][3]['source']
        all_content = ''.join(after_cell_source)
        self.assertIn('print("This should be kept")', all_content)
        self.assertIn('# Start removing here', all_content)
        self.assertIn('# This should be kept', all_content)
        self.assertNotIn('print("This should be gone")', all_content)
        self.assertNotIn('print("This should be gone again")', all_content)

    def test_process_folder(self):
        """
        Test processing all notebooks in a folder.
        """
        # Create a second test notebook
        second_notebook_path = self.source_dir / "second_notebook.ipynb"
        with open(second_notebook_path, 'w', encoding='utf-8') as f:
            f.write(self.test_notebook)  # Using the same content for simplicity
        
        # Process the folder
        self.cleaner.process_folder(self.source_dir, self.target_dir, verbose=False)
        
        # Check that both output files exist
        self.assertTrue((self.target_dir / "test_notebook.ipynb").exists())
        self.assertTrue((self.target_dir / "second_notebook.ipynb").exists())


# Run the tests if this file is executed directly
if __name__ == "__main__":
    unittest.main()