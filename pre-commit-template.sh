#!/bin/bash

# Pre-commit hook to automatically generate student notebooks
# This is a template file that will be populated with custom paths
# during setup and copied to .git/hooks/pre-commit

# Configuration variables (will be replaced during setup)
SOURCE_PATH="__SOURCE_PATH__"
TARGET_PATH="__TARGET_PATH__"
VERBOSE="__VERBOSE__"
ADDITIONAL_ARGS="__ADDITIONAL_ARGS__"

# Path to the submodule script
SCRIPT_PATH="$(git rev-parse --show-toplevel)/common-tools/generate_student_version.py"

# Exit if source path doesn't exist
if [ ! -e "$SOURCE_PATH" ]; then
    echo "Error: Source path '$SOURCE_PATH' does not exist!"
    exit 1
fi

# Create target directory if it's a directory and doesn't exist
if [[ "$TARGET_PATH" == */ && ! -d "$TARGET_PATH" ]]; then
    mkdir -p "$TARGET_PATH"
fi

# Check which files have been changed/added
changed_files=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.ipynb$' | grep -v "^$TARGET_PATH")

# If no notebook files were changed, exit successfully
if [ -z "$changed_files" ]; then
    echo "No notebook files changed, skipping student version generation."
    exit 0
fi

# Function to run the script and check for errors
run_script() {
    # Create a temporary file for output
    temp_output=$(mktemp)
    
    # Run the script and capture both stdout and stderr
    python "$SCRIPT_PATH" --source "$1" --target "$2" $VERBOSE $ADDITIONAL_ARGS 2>&1 | tee "$temp_output"
    
    # Check if the output contains ERROR messages
    if grep -q "ERROR:" "$temp_output"; then
        echo ""
        echo "❌ Errors detected during student notebook generation!"
        echo "Please fix the errors before committing."
        rm "$temp_output"
        return 1
    fi
    
    rm "$temp_output"
    return 0
}

# If SOURCE_PATH is a directory, filter changed files to only include those in the SOURCE_PATH
if [ -d "$SOURCE_PATH" ]; then
    source_path_pattern="^${SOURCE_PATH%/}/"
    filtered_files=$(echo "$changed_files" | grep -E "$source_path_pattern" || echo "")
    
    if [ -z "$filtered_files" ]; then
        echo "No notebook files changed in $SOURCE_PATH, skipping student version generation."
        exit 0
    fi
    
    # Run the script with the directory paths
    echo "Generating student versions for notebooks in $SOURCE_PATH → $TARGET_PATH"
    if ! run_script "$SOURCE_PATH" "$TARGET_PATH"; then
        exit 1
    fi
    
    # Add generated files to the commit
    if [ -d "$TARGET_PATH" ]; then
        git add "$TARGET_PATH"
    fi
else
    # SOURCE_PATH is a specific file, check if it's in the changed files
    if echo "$changed_files" | grep -q "^$SOURCE_PATH$"; then
        echo "Generating student version for $SOURCE_PATH → $TARGET_PATH"
        if ! run_script "$SOURCE_PATH" "$TARGET_PATH"; then
            exit 1
        fi
        
        # Add generated file to the commit
        git add "$TARGET_PATH"
    else
        echo "Source file $SOURCE_PATH was not changed, skipping student version generation."
    fi
fi

echo "✅ Student notebook generation completed successfully."
exit 0