#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def extract_folder_structure(root_path='../', output_file='../docs/project_structure.txt'):
    """
    Extract and display the folder structure of a project
    Excludes 'venv' folder and '__init__.py' files
    """
    
    # Convert to Path object for easier handling
    root_path = Path(root_path).resolve()
    
    # Files and folders to exclude
    exclude_folders = {
        'venv', '__pycache__', '.git', '.vscode', 
        'node_modules', '.pytest_cache', '.mypy_cache',
        'dist', 'build', '*.egg-info', 'scripts'
    }
    
    exclude_files = {
        '__init__.py', '.gitignore', '.env', 
        '*.pyc', '*.pyo', '*.pyd', '.DS_Store'
    }
    
    def should_exclude_folder(folder_name):
        """Check if folder should be excluded"""
        return any(
            folder_name == exclude or 
            folder_name.startswith('.') and exclude.startswith('.') or
            '*' in exclude and folder_name.endswith(exclude.replace('*', ''))
            for exclude in exclude_folders
        )
    
    def should_exclude_file(file_name):
        """Check if file should be excluded"""
        return any(
            file_name == exclude or
            ('*' in exclude and file_name.endswith(exclude.replace('*', '')))
            for exclude in exclude_files
        )
    
    def get_tree_structure(path, prefix="", is_last=True):
        """Recursively build tree structure"""
        tree_lines = []
        
        if path.is_dir():
            # Get directory name
            dir_name = path.name if path != root_path else path.name or "."
            
            # Add directory to tree
            if path != root_path:
                connector = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{connector}📁 {dir_name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
            else:
                tree_lines.append(f"📁 {dir_name}/")
                new_prefix = ""
            
            try:
                # Get all items in directory
                items = list(path.iterdir())
                
                # Separate folders and files
                folders = [item for item in items if item.is_dir() and not should_exclude_folder(item.name)]
                files = [item for item in items if item.is_file() and not should_exclude_file(item.name)]
                
                # Sort folders and files separately
                folders.sort(key=lambda x: x.name.lower())
                files.sort(key=lambda x: x.name.lower())
                
                all_items = folders + files
                
                # Process each item
                for i, item in enumerate(all_items):
                    is_last_item = (i == len(all_items) - 1)
                    
                    if item.is_dir():
                        # Recursively process subdirectory
                        tree_lines.extend(get_tree_structure(item, new_prefix, is_last_item))
                    else:
                        # Add file to tree
                        connector = "└── " if is_last_item else "├── "
                        file_icon = get_file_icon(item.name)
                        file_size = get_file_size(item)
                        tree_lines.append(f"{new_prefix}{connector}{file_icon} {item.name} {file_size}")
                        
            except PermissionError:
                tree_lines.append(f"{new_prefix}├── [Permission Denied]")
                
        return tree_lines
    
    def get_file_icon(filename):
        """Get appropriate icon for file type"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        icons = {
            'py': '🐍',
            'txt': '📄',
            'md': '📝',
            'json': '📋',
            'yml': '⚙️',
            'yaml': '⚙️',
            'html': '🌐',
            'css': '🎨',
            'js': '📜',
            'pdf': '📕',
            'png': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'gif': '🖼️',
            'svg': '🖼️',
            'ico': '🖼️',
        }
        
        return icons.get(extension, '📄')
    
    def get_file_size(file_path):
        """Get human readable file size"""
        try:
            size = file_path.stat().st_size
            if size < 1024:
                return f"({size}B)"
            elif size < 1024 * 1024:
                return f"({size/1024:.1f}KB)"
            else:
                return f"({size/(1024*1024):.1f}MB)"
        except:
            return ""
    
    def get_project_stats(path):
        """Get project statistics"""
        stats = {
            'total_files': 0,
            'total_folders': 0,
            'python_files': 0,
            'total_size': 0,
            'file_types': {}
        }
        
        for item in path.rglob('*'):
            try:
                if should_exclude_folder(item.parent.name):
                    continue
                    
                if item.is_file() and not should_exclude_file(item.name):
                    stats['total_files'] += 1
                    stats['total_size'] += item.stat().st_size
                    
                    if item.suffix.lower() == '.py':
                        stats['python_files'] += 1
                    
                    ext = item.suffix.lower()
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                    
                elif item.is_dir() and not should_exclude_folder(item.name):
                    stats['total_folders'] += 1
            except:
                continue
                
        return stats
    
    # Generate tree structure
    print("🔍 Extracting project structure...")
    tree_lines = get_tree_structure(root_path)
    
    # Get project statistics
    stats = get_project_stats(root_path)
    
    # Prepare output
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("📂 PROJECT FOLDER STRUCTURE")
    output_lines.append("=" * 60)
    output_lines.append("")
    
    # Add tree structure
    output_lines.extend(tree_lines)
    output_lines.append("")
    
    # Add statistics
    output_lines.append("=" * 60)
    output_lines.append("📊 PROJECT STATISTICS")
    output_lines.append("=" * 60)
    output_lines.append(f"📁 Total Folders: {stats['total_folders']}")
    output_lines.append(f"📄 Total Files: {stats['total_files']}")
    output_lines.append(f"🐍 Python Files: {stats['python_files']}")
    output_lines.append(f"💾 Total Size: {stats['total_size']/(1024*1024):.2f} MB")
    output_lines.append("")
    
    # File types breakdown
    if stats['file_types']:
        output_lines.append("📋 File Types:")
        for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            ext_display = ext if ext else "(no extension)"
            output_lines.append(f"   {ext_display}: {count} files")
    
    output_lines.append("")
    output_lines.append("=" * 60)
    output_lines.append(f"Generated from: {root_path}")
    output_lines.append("=" * 60)
    
    # Display output
    output_text = "\n".join(output_lines)
    print(output_text)
    
    # Save to file
    try:
        # Ensure the docs directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"\n✅ Structure saved to: {output_path.resolve()}")
    except Exception as e:
        print(f"\n❌ Error saving to file: {e}")
        print(f"   Attempted to save to: {Path(output_file).resolve()}")
    
    return output_text

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract project folder structure')
    parser.add_argument('path', nargs='?', default='../', help='Project path (default: parent directory ../)')
    parser.add_argument('-o', '--output', default='../docs/project_structure.txt', help='Output file name (default: ../docs/project_structure.txt)')
    parser.add_argument('--no-file', action='store_true', help='Display only, do not save to file')
    
    args = parser.parse_args()
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"❌ Error: Path '{args.path}' does not exist")
        sys.exit(1)
    
    # Extract structure
    if args.no_file:
        extract_folder_structure(args.path, None)
    else:
        extract_folder_structure(args.path, args.output)

if __name__ == "__main__":
    main()