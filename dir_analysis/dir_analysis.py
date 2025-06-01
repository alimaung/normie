#!/usr/bin/env python3
"""
Directory Index Creator - Simple and fast directory structure indexing
Creates a basic index of files and folders with verbose progress output
"""

import os
import sys
import time
import json
from datetime import datetime
import traceback

class DirectoryIndexer:
    def __init__(self, target_path, verbose=True):
        self.target_path = target_path
        self.verbose = verbose
        self.directory_tree = {}
        self.file_count = 0
        self.dir_count = 0
        self.errors = []
        
    def log(self, message, level="INFO"):
        """Verbose logging with timestamp"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [{level}] {message}")
    
    def analyze_directory(self, path, current_depth=0):
        """Recursively analyze directory structure"""
        try:
            path_str = str(path)
            
            # Check if path is accessible
            if not os.path.exists(path_str):
                self.log(f"Path not found: {path_str}", "ERROR")
                return
            
            # Log every folder being scanned
            indent = "  " * current_depth
            folder_name = os.path.basename(path_str) or path_str
            self.log(f"{indent}Scanning: {folder_name}")
            
            # Use scandir for better performance
            try:
                with os.scandir(path_str) as entries:
                    dir_contents = {'files': [], 'subdirs': {}}
                    
                    for entry in entries:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                self.process_file(entry, dir_contents)
                            elif entry.is_dir(follow_symlinks=False):
                                self.process_directory(entry, dir_contents, current_depth)
                        except (OSError, PermissionError) as e:
                            self.log(f"Error processing entry {entry.name}: {e}", "WARNING")
                            self.errors.append(f"{entry.path}: {str(e)}")
                            continue
                    
                    # Store directory structure
                    self.directory_tree[path_str] = dir_contents
                    
            except (OSError, PermissionError) as e:
                self.log(f"Cannot access directory {path_str}: {e}", "WARNING")
                self.errors.append(f"{path_str}: {str(e)}")
                
        except Exception as e:
            self.log(f"Unexpected error analyzing {path}: {e}", "ERROR")
            self.errors.append(f"{path}: {str(e)}")
    
    def process_file(self, entry, dir_contents):
        """Process a file entry"""
        try:
            self.file_count += 1
            
            # Add to directory contents
            dir_contents['files'].append(entry.name)
                
        except Exception as e:
            self.log(f"Error processing file {entry.name}: {e}", "WARNING")
            self.errors.append(f"{entry.path}: {str(e)}")
    
    def process_directory(self, entry, dir_contents, current_depth):
        """Process a directory entry"""
        try:
            self.dir_count += 1
            
            # Recursively analyze subdirectory
            self.analyze_directory(entry.path, current_depth + 1)
            
            # Add subdirectory to current directory contents
            if entry.path in self.directory_tree:
                dir_contents['subdirs'][entry.name] = self.directory_tree[entry.path]
                
        except Exception as e:
            self.log(f"Error processing directory {entry.name}: {e}", "WARNING")
            self.errors.append(f"{entry.path}: {str(e)}")
    
    def save_index_json(self, output_file="directory_index.json"):
        """Save directory index as JSON"""
        self.log(f"Saving JSON index to {output_file}")
        
        try:
            # Create a clean structure for JSON export
            root_name = os.path.basename(self.target_path) or "root"
            
            if self.target_path in self.directory_tree:
                json_data = {
                    "metadata": {
                        "target_path": self.target_path,
                        "scan_timestamp": datetime.now().isoformat(),
                        "total_files": self.file_count,
                        "total_directories": self.dir_count,
                        "errors_count": len(self.errors)
                    },
                    "structure": {
                        root_name: self.directory_tree[self.target_path]
                    }
                }
            else:
                json_data = {
                    "metadata": {
                        "target_path": self.target_path,
                        "scan_timestamp": datetime.now().isoformat(),
                        "total_files": self.file_count,
                        "total_directories": self.dir_count,
                        "errors_count": len(self.errors),
                        "error": "Root directory not accessible"
                    },
                    "structure": {}
                }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log(f"Error saving JSON index: {e}", "ERROR")
    
    def save_index_text(self, output_file="directory_index.txt"):
        """Save directory index as text"""
        self.log(f"Saving text index to {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("DIRECTORY INDEX\n")
                f.write("=" * 50 + "\n")
                f.write(f"Target: {self.target_path}\n")
                f.write(f"Scanned: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Files: {self.file_count:,} | Directories: {self.dir_count:,}\n")
                f.write("=" * 50 + "\n\n")
                
                def write_directory(name, contents, depth=0):
                    indent = "  " * depth
                    f.write(f"{indent}{name}/\n")
                    
                    # Write subdirectories first
                    for subdir_name, subdir_contents in sorted(contents.get('subdirs', {}).items()):
                        write_directory(subdir_name, subdir_contents, depth + 1)
                    
                    # Write files
                    for filename in sorted(contents.get('files', [])):
                        f.write(f"{indent}  {filename}\n")
                
                # Start with root directory
                root_name = os.path.basename(self.target_path) or "root"
                if self.target_path in self.directory_tree:
                    write_directory(root_name, self.directory_tree[self.target_path])
                else:
                    f.write("ERROR: Root directory not accessible\n")
                
        except Exception as e:
            self.log(f"Error saving text index: {e}", "ERROR")
    
    def run_analysis(self):
        """Run the directory indexing"""
        self.log("Starting directory indexing...")
        self.log(f"Target path: {self.target_path}")
        
        start_time = time.time()
        
        try:
            # Start analysis
            self.analyze_directory(self.target_path)
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.log(f"Indexing completed in {duration:.2f} seconds")
            self.log(f"Found {self.file_count:,} files and {self.dir_count:,} directories")
            
            if self.errors:
                self.log(f"Encountered {len(self.errors)} errors during scan", "WARNING")
            
            # Save indexes
            self.save_index_json()
            self.save_index_text()
            
            self.log("Index files saved successfully!")
            return True
            
        except KeyboardInterrupt:
            self.log("Indexing interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Fatal error during indexing: {e}", "ERROR")
            traceback.print_exc()
            return False

def main():
    """Main function"""
    target_path = r"\\Dehesdna-a009a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe"
    
    print("Directory Indexer v1.0")
    print("=" * 50)
    print(f"Target: {target_path}")
    print("=" * 50)
    
    indexer = DirectoryIndexer(target_path, verbose=True)
    success = indexer.run_analysis()
    
    if success:
        print("\nIndexing completed! Generated files:")
        print("  - directory_index.json (JSON format)")
        print("  - directory_index.txt (text format)")
    else:
        print("\nIndexing failed or was interrupted.")
        sys.exit(1)

if __name__ == "__main__":
    main()
