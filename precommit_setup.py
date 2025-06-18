#!/usr/bin/env python3
"""
Setup script to install a pre-commit hook for generating student versions of notebooks.
This script installs the hook with paths from notebook_settings.json or command line arguments.
"""

import os
import json
import argparse
import stat
from pathlib import Path

def get_default_settings():
    """Read settings from notebook_settings.json if available."""
    try:
        # Get the repository root directory
        import subprocess
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], 
            universal_newlines=True
        ).strip()
        
        settings_path = Path(repo_root) / "notebook_settings.json"
        
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            return settings
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Note: Could not load default settings: {e}")
    
    return {}

def setup_precommit_hook(source_path, target_path, verbose=False, additional_args=None):
    """
    Configure and install the pre-commit hook with the specified paths.
    
    Args:
        source_path (str): Path to source notebooks or directory
        target_path (str): Path where student notebooks will be saved
        verbose (bool): Whether to enable verbose output in the hook
        additional_args (str): Additional arguments to pass to the script
    """
    # Get the repository root directory
    try:
        import subprocess
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], 
            universal_newlines=True
        ).strip()
    except subprocess.CalledProcessError:
        print("Error: Not a git repository.")
        return False
    
    # Paths
    submodule_dir = Path(repo_root) / "common-tools"
    submodule_dir = submodule_dir if submodule_dir.exists() else Path(repo_root) / "common"
    hooks_dir = Path(repo_root) / ".git" / "hooks"
    template_path = submodule_dir / "pre-commit-template.sh"
    hook_path = hooks_dir / "pre-commit"
    
    # Verify the submodule exists
    if not submodule_dir.exists():
        print(f"Error: Submodule directory '{submodule_dir}' not found.")
        print("Make sure you have added the common-tools submodule to your repository.")
        return False
    
    # Verify the template exists
    if not template_path.exists():
        print(f"Error: Pre-commit template '{template_path}' not found.")
        return False
    
    # Create hooks directory if it doesn't exist
    hooks_dir.mkdir(exist_ok=True, parents=True)
    
    # Read the template
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace placeholders with actual values
    verbose_flag = "--verbose" if verbose else ""
    additional_args = additional_args or ""
    
    hook_content = template_content.replace("__SOURCE_PATH__", source_path)
    hook_content = hook_content.replace("__TARGET_PATH__", target_path)
    hook_content = hook_content.replace("__VERBOSE__", verbose_flag)
    hook_content = hook_content.replace("__ADDITIONAL_ARGS__", additional_args)
    
    # Write the configured hook
    with open(hook_path, 'w') as f:
        f.write(hook_content)
    
    # Make the hook executable
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print(f"Pre-commit hook installed at: {hook_path}")
    print(f"Source path: {source_path}")
    print(f"Target path: {target_path}")
    if verbose:
        print("Verbose mode: enabled")
    if additional_args:
        print(f"Additional arguments: {additional_args}")
    
    return True

def main():
    # Get default settings
    defaults = get_default_settings()
    
    parser = argparse.ArgumentParser(
        description="Setup a pre-commit hook for generating student versions of notebooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup using settings from notebook_settings.json (if present):
  python setup_precommit_hook.py

  # Override settings with command line arguments:
  python setup_precommit_hook.py --source Custom_Course/ --target Custom_Student/
        """
    )
    
    parser.add_argument(
        "--source", "-s", 
        default=defaults.get("source_path"),
        help="Source notebook file or folder containing notebooks"
    )
    
    parser.add_argument(
        "--target", "-t", 
        default=defaults.get("target_path"),
        help="Target notebook file or folder where student notebooks will be saved"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        default=defaults.get("verbose", False),
        help="Enable verbose output in the hook"
    )
    
    parser.add_argument(
        "--args", "-a", 
        default=defaults.get("additional_args", ""),
        help="Additional arguments to pass to the script"
    )
    
    args = parser.parse_args()
    
    # Check if required arguments are missing
    if args.source is None:
        parser.error("source path is required (either in notebook_settings.json or as --source argument)")
    
    if args.target is None:
        parser.error("target path is required (either in notebook_settings.json or as --target argument)")
    
    setup_precommit_hook(args.source, args.target, args.verbose, args.args)

if __name__ == "__main__":
    main()
