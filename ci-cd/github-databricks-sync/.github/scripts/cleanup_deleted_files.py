#!/usr/bin/env python3
"""
Clean up deleted files from Databricks workspace.
This script removes files from Databricks that have been deleted from the repository.
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path


def get_deleted_files(branch):
    """
    Get list of deleted files between commits.
    """
    try:
        # Get deleted files in the current push
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=D', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return [f for f in files if f]  # Filter out empty strings
    except Exception as e:
        print(f"Error getting deleted files: {e}")
    
    return []


def delete_file_from_databricks(databricks_path):
    """
    Delete a file from Databricks workspace.
    """
    try:
        cmd = ['databricks', 'workspace', 'rm', databricks_path, '--recursive']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Deleted: {databricks_path}")
            return True
        else:
            print(f"✗ Failed to delete: {databricks_path}")
            if "does not exist" not in result.stderr:
                print(f"  Error: {result.stderr}")
            return True  # Return true even if file doesn't exist
    except Exception as e:
        print(f"✗ Exception deleting {databricks_path}: {e}")
        return False


def cleanup_deleted_files(target_path, branch):
    """
    Remove deleted files from Databricks workspace.
    """
    print(f"Checking for deleted files in branch: {branch}")
    print(f"Target workspace path: {target_path}")
    
    deleted_files = get_deleted_files(branch)
    
    if not deleted_files:
        print("No deleted files detected.")
        return True
    
    print(f"Found {len(deleted_files)} deleted file(s)")
    
    successful = 0
    failed = 0
    
    for rel_path in deleted_files:
        # Convert Windows path separators to forward slashes
        rel_path_unix = rel_path.replace(os.sep, '/')
        
        # Construct target path in Databricks
        databricks_target = f"{target_path}/{rel_path_unix}"
        
        if delete_file_from_databricks(databricks_target):
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Cleanup Summary:")
    print(f"  Successful deletions: {successful}")
    print(f"  Failed deletions: {failed}")
    print(f"  Total processed: {successful + failed}")
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description='Clean up deleted files from Databricks')
    parser.add_argument('--target-path', required=True, help='Target Databricks workspace path')
    parser.add_argument('--branch', required=True, help='Git branch name')
    
    args = parser.parse_args()
    
    success = cleanup_deleted_files(args.target_path, args.branch)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()