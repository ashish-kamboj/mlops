#!/usr/bin/env python3
"""
Sync repository files to Databricks workspace.
This script uploads new and modified files to the Databricks workspace.
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path


def get_changed_files(branch):
    """
    Get list of changed files between commits.
    For push events, compare with previous commit.
    """
    try:
        # Get changed files in the current push
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception as e:
        print(f"Error getting changed files: {e}")
    
    return []


def get_all_files(source_dir, exclude_patterns=None):
    """
    Get all files in the repository excluding certain patterns.
    """
    if exclude_patterns is None:
        exclude_patterns = ['.git', '.github', '.gitignore', '__pycache__', 
                          '.pytest_cache', '.DS_Store', '*.pyc', '.eggs']
    
    all_files = []
    for root, dirs, files in os.walk(source_dir):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
        
        for file in files:
            # Skip excluded file patterns
            if any(pattern in file for pattern in exclude_patterns):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, source_dir)
            all_files.append(rel_path)
    
    return all_files


def upload_file(source_path, target_path, databricks_path):
    """
    Upload a single file to Databricks using databricks-cli.
    """
    try:
        # Ensure target directory exists
        subprocess.run(
            ['databricks', 'workspace', 'mkdirs', target_path],
            check=False,
            capture_output=True
        )
        
        # Upload file
        cmd = ['databricks', 'workspace', 'import', source_path, databricks_path, '--language', 'AUTO', '--format', 'AUTO']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Uploaded: {databricks_path}")
            return True
        else:
            print(f"✗ Failed to upload: {databricks_path}")
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Exception uploading {databricks_path}: {e}")
        return False


def sync_files(source_dir, target_path, branch):
    """
    Sync files to Databricks workspace.
    """
    print(f"Starting sync from {source_dir} to {target_path}")
    print(f"Branch: {branch}")
    
    all_files = get_all_files(source_dir)
    print(f"Total files to sync: {len(all_files)}")
    
    successful = 0
    failed = 0
    
    for rel_path in all_files:
        source_file = os.path.join(source_dir, rel_path)
        
        # Convert Windows path separators to forward slashes
        rel_path_unix = rel_path.replace(os.sep, '/')
        
        # Construct target path in Databricks
        databricks_target = f"{target_path}/{rel_path_unix}"
        
        if upload_file(source_file, os.path.dirname(databricks_target), databricks_target):
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Sync Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {successful + failed}")
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description='Sync files to Databricks workspace')
    parser.add_argument('--source-dir', default='.', help='Source directory')
    parser.add_argument('--target-path', required=True, help='Target Databricks workspace path')
    parser.add_argument('--branch', required=True, help='Git branch name')
    
    args = parser.parse_args()
    
    success = sync_files(args.source_dir, args.target_path, args.branch)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()