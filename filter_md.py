#!/usr/bin/env python3

"""
Usage example:
    python filter_md.py Basics_filled.md Basics.md
"""

import sys

def remove_solutions(input_file, output_file,
                     start_marker="<!-- #solution -->",
                     end_marker="<!-- #endsolution -->"):
    in_block = False
    is_comment = False
    lines_to_keep = []

    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            # Detect start of solution block
            if start_marker in line:
                in_block = True

            if in_block:
                # Remove leading and trailing whitespace
                stripped_line = line.strip()

                # Set the comment flag if the line starts with '#' or "```"
                if stripped_line.startswith('#') or stripped_line.startswith('```') or stripped_line.startswith('<!--'):
                    is_comment = True
            
            # Detect end of solution block
            if end_marker in line:
                in_block = False

            # If not in solution block, keep the line
            if not in_block or (in_block and is_comment):
                lines_to_keep.append(line)

            # Reset the comment flag after each line
            is_comment = False

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.writelines(lines_to_keep)

    # Print the file we created/modified (per the instructions)
    print(f"# Created/Modified files after removing solutions:\n{output_file}")


def remove_section(input_file, output_file, section_type="skip"):
    """Remove sections marked as skip or notes from markdown files.
    
    Args:
        input_file (str): Path to input file
        output_file (str): Path to output file
        section_type (str): Type of section to remove ("skip" or "notes")
    """
    start_marker = f'<!-- #region slideshow={{"slide_type": "{section_type}"}} -->'
    end_marker = '<!-- #endregion -->'
    
    in_block = False
    is_comment = False
    lines_to_keep = []

    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            # Detect start of section block
            if start_marker in line:
                in_block = True

            if in_block:
                # Remove leading and trailing whitespace
                stripped_line = line.strip()

                # Set the comment flag if the line starts with '#' or "```"
                if stripped_line.startswith('```') or stripped_line.startswith('<!--'):
                    is_comment = True
            
            # Detect end of section block
            if end_marker in line:
                in_block = False

            # If not in section block, keep the line
            if not in_block or (in_block and is_comment):
                lines_to_keep.append(line)

            # Reset the comment flag after each line
            is_comment = False

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.writelines(lines_to_keep)

    # Print the file we created/modified
    print(f"# Created/Modified files after removing {section_type} section:\n{output_file}")
    
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python filter_md.py <input.md> <output.md>")
        sys.exit(1)

    input_md = sys.argv[1]
    output_md = sys.argv[2]

    remove_solutions(input_md, output_md)
    remove_section(output_md, output_md, section_type="skip")
    remove_section(output_md, output_md, section_type="notes")
    