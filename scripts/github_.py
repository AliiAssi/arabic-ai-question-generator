#!/usr/bin/env python3
"""
GitHub README Context Generator

This script extracts repository information and code structure from a GitHub
repository to assist in README file generation. It creates a comprehensive
context file that can be used for manual README creation.

Usage:
    python readme_context_generator.py <github_repo_url> [--token YOUR_TOKEN]

Requirements:
    - requests library: pip install requests
    - GitHub personal access token (optional but recommended for higher rate limits)
"""

import re
import sys
import json
import argparse
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional
import requests
from pathlib import Path


class GitHubRepoAnalyzer:
    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub repository analyzer.
        
        Args:
            token: GitHub personal access token for API authentication
        """
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
        
        # File extensions to analyze for code
        self.code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.r', '.m', '.pl', '.sh', '.ps1', '.sql'
        }
        
        # Documentation and config files to include
        self.doc_extensions = {
            '.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.toml',
            '.cfg', '.ini', '.xml', '.dockerfile'
        }
        
        # Directories to skip (package managers, dependencies, build outputs)
        self.skip_directories = {
            'node_modules', 'npm', 'venv', 'env', '.env', 'virtualenv',
            'vendor', 'composer', 'packages', 'bower_components',
            '__pycache__', '.pytest_cache', 'build', 'dist', 'target',
            'bin', 'obj', 'out', '.gradle', '.mvn', 'cmake-build-debug',
            'cmake-build-release', '.idea', '.vscode', '.vs', 'Pods',
            'carthage', 'deps', '_build', 'ebin', 'rel', 'cover',
            'logs', 'tmp', 'temp', '.tmp', '.cache', '.next', '.nuxt',
            'public', 'static', 'assets', 'resources', 'storage',
            '.git', '.svn', '.hg', '.bzr'
        }

    def parse_repo_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub repository URL to extract owner and repo name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        parsed = urlparse(url)
        if parsed.netloc not in ['github.com', 'www.github.com']:
            raise ValueError("URL must be a GitHub repository URL")
        
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL format")
        
        owner, repo = path_parts[0], path_parts[1]
        # Remove .git suffix if present
        if repo.endswith('.git'):
            repo = repo[:-4]
        
        return owner, repo

    def get_repo_info(self, owner: str, repo: str) -> Dict:
        """Get basic repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary containing repository information
        """
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def should_skip_directory(self, path: str) -> bool:
        """Check if a directory should be skipped based on common patterns.
        
        Args:
            path: Directory path to check
            
        Returns:
            True if directory should be skipped
        """
        path_parts = path.lower().split('/')
        
        # Check if any part of the path matches skip directories
        for part in path_parts:
            if part in self.skip_directories:
                return True
            
            # Additional patterns to skip
            if (part.startswith('.') and len(part) > 1 and 
                part not in ['.github', '.gitignore', '.env.example']):
                return True
            
            # Skip test directories that are too deep
            if part in ['test', 'tests', '__tests__', 'spec', 'specs'] and len(path_parts) > 2:
                return True
        
        return False

    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get repository contents recursively.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within the repository
            
        Returns:
            List of file/directory information
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = self.session.get(url)
        
        if response.status_code == 404:
            return []
        
        response.raise_for_status()
        contents = response.json()
        
        all_files = []
        for item in contents:
            if item['type'] == 'file':
                all_files.append(item)
            elif item['type'] == 'dir':
                # Check if we should skip this directory
                if self.should_skip_directory(item['path']):
                    print(f"Skipping directory: {item['path']}")
                    continue
                
                # Recursively get directory contents
                subdir_files = self.get_repo_contents(owner, repo, item['path'])
                all_files.extend(subdir_files)
        
        return all_files

    def get_file_content(self, download_url: str) -> str:
        """Download file content from GitHub.
        
        Args:
            download_url: Direct download URL for the file
            
        Returns:
            File content as string
        """
        response = self.session.get(download_url)
        response.raise_for_status()
        
        # Try to decode as UTF-8, fallback to latin1 if that fails
        try:
            return response.content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return response.content.decode('latin1')
            except UnicodeDecodeError:
                return f"[Binary file - cannot display content]"

    def extract_python_functions(self, content: str) -> List[Dict]:
        """Extract Python functions and their docstrings.
        
        Args:
            content: Python file content
            
        Returns:
            List of dictionaries containing function information
        """
        functions = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for function definitions
            if line.startswith('def ') or line.startswith('async def '):
                func_match = re.match(r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\):', line)
                if func_match:
                    func_name = func_match.group(1)
                    func_line = i + 1
                    
                    # Look for docstring
                    docstring = ""
                    j = i + 1
                    
                    # Skip empty lines
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    # Check for docstring
                    if j < len(lines):
                        doc_line = lines[j].strip()
                        if doc_line.startswith('"""') or doc_line.startswith("'''"):
                            quote_type = '"""' if doc_line.startswith('"""') else "'''"
                            
                            if doc_line.count(quote_type) >= 2:
                                # Single line docstring
                                docstring = doc_line.strip(quote_type).strip()
                            else:
                                # Multi-line docstring
                                docstring_lines = [doc_line.strip(quote_type)]
                                j += 1
                                while j < len(lines):
                                    if quote_type in lines[j]:
                                        docstring_lines.append(lines[j].split(quote_type)[0])
                                        break
                                    docstring_lines.append(lines[j])
                                    j += 1
                                docstring = '\n'.join(docstring_lines).strip()
                    
                    functions.append({
                        'name': func_name,
                        'line': func_line,
                        'docstring': docstring,
                        'signature': line
                    })
            
            i += 1
        
        return functions

    def extract_javascript_functions(self, content: str) -> List[Dict]:
        """Extract JavaScript/TypeScript functions and their comments.
        
        Args:
            content: JavaScript/TypeScript file content
            
        Returns:
            List of dictionaries containing function information
        """
        functions = []
        lines = content.split('\n')
        
        # Patterns for different function types
        patterns = [
            r'function\s+(\w+)\s*\(',  # function name()
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\s*\([^)]*\)\s*=>\s*{',  # const name = () => {
            r'let\s+(\w+)\s*=\s*(?:async\s+)?\s*\([^)]*\)\s*=>\s*{',     # let name = () => {
            r'var\s+(\w+)\s*=\s*(?:async\s+)?\s*\([^)]*\)\s*=>\s*{',     # var name = () => {
            r'(\w+)\s*:\s*(?:async\s+)?\s*function\s*\(',                # name: function(
            r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*{',                       # async name() {
        ]
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            for pattern in patterns:
                match = re.search(pattern, line_stripped)
                if match:
                    func_name = match.group(1)
                    
                    # Look for preceding comment
                    comment = ""
                    j = i - 1
                    comment_lines = []
                    
                    # Collect preceding comments
                    while j >= 0:
                        prev_line = lines[j].strip()
                        if prev_line.startswith('//') or prev_line.startswith('*') or prev_line.startswith('/*'):
                            comment_lines.insert(0, prev_line.lstrip('/*').rstrip('*/').strip())
                            j -= 1
                        elif not prev_line:
                            j -= 1
                        else:
                            break
                    
                    if comment_lines:
                        comment = '\n'.join(comment_lines)
                    
                    functions.append({
                        'name': func_name,
                        'line': i + 1,
                        'comment': comment,
                        'signature': line_stripped
                    })
                    break
        
        return functions

    def extract_functions_from_file(self, file_path: str, content: str) -> List[Dict]:
        """Extract functions from a file based on its extension.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of dictionaries containing function information
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            return self.extract_python_functions(content)
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            return self.extract_javascript_functions(content)
        else:
            # For other languages, do a simple regex search for function-like patterns
            functions = []
            lines = content.split('\n')
            
            # Generic patterns that might match functions in various languages
            patterns = [
                r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',  # Java/C#
                r'func\s+(\w+)\s*\(',  # Go/Swift
                r'fn\s+(\w+)\s*\(',    # Rust
                r'def\s+(\w+)\s*\(',   # Ruby (similar to Python)
            ]
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                for pattern in patterns:
                    match = re.search(pattern, line_stripped)
                    if match:
                        functions.append({
                            'name': match.group(1),
                            'line': i + 1,
                            'signature': line_stripped,
                            'comment': ''
                        })
                        break
            
            return functions

    def analyze_repository(self, repo_url: str) -> Dict:
        """Analyze a GitHub repository and extract all relevant information.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary containing repository analysis
        """
        owner, repo = self.parse_repo_url(repo_url)
        
        print(f"Analyzing repository: {owner}/{repo}")
        
        # Get repository information
        repo_info = self.get_repo_info(owner, repo)
        
        # Get all files
        all_files = self.get_repo_contents(owner, repo)
        
        analysis = {
            'repository': {
                'name': repo_info['name'],
                'full_name': repo_info['full_name'],
                'description': repo_info.get('description', ''),
                'language': repo_info.get('language', ''),
                'topics': repo_info.get('topics', []),
                'stars': repo_info['stargazers_count'],
                'forks': repo_info['forks_count'],
                'license': repo_info.get('license', {}).get('name', 'Not specified') if repo_info.get('license') else 'Not specified',
                'url': repo_info['html_url']
            },
            'files': {
                'code_files': [],
                'documentation_files': [],
                'other_files': []
            },
            'structure': {
                'total_files': len(all_files),
                'directories': set(),
                'file_types': {}
            }
        }
        
        # Process each file
        skipped_files = 0
        for file_info in all_files:
            file_path = file_info['path']
            file_ext = Path(file_path).suffix.lower()
            
            # Skip files in directories we want to ignore
            if self.should_skip_directory(file_path):
                skipped_files += 1
                continue
            
            # Track directory structure (only for non-skipped files)
            if '/' in file_path:
                directory = '/'.join(file_path.split('/')[:-1])
                if not self.should_skip_directory(directory):
                    analysis['structure']['directories'].add(directory)
            
            # Track file types
            if file_ext:
                analysis['structure']['file_types'][file_ext] = analysis['structure']['file_types'].get(file_ext, 0) + 1
            
            # Process based on file type
            if file_ext in self.code_extensions:
                print(f"Processing code file: {file_path}")
                try:
                    content = self.get_file_content(file_info['download_url'])
                    functions = self.extract_functions_from_file(file_path, content)
                    
                    analysis['files']['code_files'].append({
                        'path': file_path,
                        'size': file_info['size'],
                        'functions': functions,
                        'lines_of_code': len(content.split('\n'))
                    })
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    analysis['files']['code_files'].append({
                        'path': file_path,
                        'size': file_info['size'],
                        'functions': [],
                        'error': str(e)
                    })
            
            elif file_ext in self.doc_extensions or file_path.lower() in ['readme', 'license', 'changelog', 'contributing']:
                analysis['files']['documentation_files'].append({
                    'path': file_path,
                    'size': file_info['size']
                })
            
            else:
                analysis['files']['other_files'].append({
                    'path': file_path,
                    'size': file_info['size']
                })
        
        # Convert directories set to sorted list
        analysis['structure']['directories'] = sorted(list(analysis['structure']['directories']))
        analysis['structure']['skipped_files'] = skipped_files
        
        print(f"Processed {len(all_files) - skipped_files} files, skipped {skipped_files} files")
        
        return analysis

    def generate_context_file(self, analysis: Dict, output_file: str):
        """Generate a context file for README creation.
        
        Args:
            analysis: Repository analysis dictionary
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# GitHub Repository Analysis - README Context\n")
            f.write("=" * 60 + "\n\n")
            
            # Repository Information
            repo = analysis['repository']
            f.write("## Repository Information\n")
            f.write("-" * 30 + "\n")
            f.write(f"Name: {repo['name']}\n")
            f.write(f"Full Name: {repo['full_name']}\n")
            f.write(f"Description: {repo['description']}\n")
            f.write(f"Primary Language: {repo['language']}\n")
            f.write(f"Topics: {', '.join(repo['topics'])}\n")
            f.write(f"Stars: {repo['stars']}\n")
            f.write(f"Forks: {repo['forks']}\n")
            f.write(f"License: {repo['license']}\n")
            f.write(f"URL: {repo['url']}\n\n")
            
            # Project Structure
            structure = analysis['structure']
            f.write("## Project Structure\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Files: {structure['total_files']}\n")
            f.write(f"Files Processed: {structure['total_files'] - structure.get('skipped_files', 0)}\n")
            f.write(f"Files Skipped: {structure.get('skipped_files', 0)} (dependencies/build artifacts)\n")
            f.write(f"Directories: {len(structure['directories'])}\n\n")
            
            if structure['directories']:
                f.write("### Directory Structure:\n")
                for directory in structure['directories']:
                    f.write(f"  - {directory}/\n")
                f.write("\n")
            
            f.write("### File Types Distribution:\n")
            for ext, count in sorted(structure['file_types'].items()):
                f.write(f"  {ext}: {count} files\n")
            f.write("\n")
            
            # Code Files Analysis
            f.write("## Code Files Analysis\n")
            f.write("-" * 30 + "\n")
            
            code_files = analysis['files']['code_files']
            if code_files:
                f.write(f"Total code files: {len(code_files)}\n\n")
                
                for file_info in code_files:
                    f.write(f"### File: {file_info['path']}\n")
                    f.write(f"Size: {file_info['size']} bytes\n")
                    
                    if 'lines_of_code' in file_info:
                        f.write(f"Lines of code: {file_info['lines_of_code']}\n")
                    
                    if 'error' in file_info:
                        f.write(f"Error: {file_info['error']}\n\n")
                        continue
                    
                    functions = file_info['functions']
                    if functions:
                        f.write(f"Functions found: {len(functions)}\n\n")
                        
                        for func in functions:
                            f.write(f"#### Function: {func['name']} (Line {func['line']})\n")
                            f.write(f"Signature: {func['signature']}\n")
                            
                            # Handle different comment/docstring fields
                            doc = func.get('docstring', '') or func.get('comment', '')
                            if doc:
                                f.write("Documentation:\n")
                                for doc_line in doc.split('\n'):
                                    f.write(f"  {doc_line}\n")
                            f.write("\n")
                    else:
                        f.write("No functions found.\n\n")
                    
                    f.write("-" * 40 + "\n\n")
            else:
                f.write("No code files found.\n\n")
            
            # Documentation Files
            doc_files = analysis['files']['documentation_files']
            if doc_files:
                f.write("## Documentation Files\n")
                f.write("-" * 30 + "\n")
                for doc_file in doc_files:
                    f.write(f"- {doc_file['path']} ({doc_file['size']} bytes)\n")
                f.write("\n")
            
            # Other Files
            other_files = analysis['files']['other_files']
            if other_files:
                f.write("## Other Files\n")
                f.write("-" * 30 + "\n")
                for other_file in other_files:
                    f.write(f"- {other_file['path']} ({other_file['size']} bytes)\n")
                f.write("\n")
            
            # README Suggestions
            f.write("## README Content Suggestions\n")
            f.write("-" * 30 + "\n")
            f.write("Based on the analysis above, consider including the following sections in your README:\n\n")
            f.write("1. **Project Title and Description**\n")
            f.write(f"   - Use: {repo['name']}\n")
            f.write(f"   - Description: {repo['description']}\n\n")
            
            if repo['language']:
                f.write("2. **Technology Stack**\n")
                f.write(f"   - Primary language: {repo['language']}\n")
                if structure['file_types']:
                    f.write("   - File types suggest additional technologies:\n")
                    for ext in sorted(structure['file_types'].keys()):
                        f.write(f"     - {ext}\n")
                f.write("\n")
            
            f.write("3. **Installation & Setup**\n")
            f.write("   - Based on project structure and file types\n\n")
            
            if any(len(f['functions']) > 0 for f in code_files):
                f.write("4. **Usage Examples**\n")
                f.write("   - Highlight main functions found in the analysis\n\n")
            
            f.write("5. **Project Structure**\n")
            f.write("   - Use the directory structure provided above\n\n")
            
            if repo['license'] != 'Not specified':
                f.write("6. **License**\n")
                f.write(f"   - {repo['license']}\n\n")
            
            f.write("7. **Contributing**\n")
            f.write("   - Guidelines for contributors\n\n")


def main():
    parser = argparse.ArgumentParser(description='Generate README context from GitHub repository')
    parser.add_argument('repo_url', help='GitHub repository URL')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--output', '-o', default='readme_context.txt', help='Output file name')
    
    args = parser.parse_args()
    
    try:
        analyzer = GitHubRepoAnalyzer(token=args.token)
        analysis = analyzer.analyze_repository(args.repo_url)
        analyzer.generate_context_file(analysis, args.output)
        
        print(f"\nAnalysis complete! Context file saved as: {args.output}")
        print(f"Repository: {analysis['repository']['full_name']}")
        print(f"Total files analyzed: {analysis['structure']['total_files']}")
        print(f"Code files: {len(analysis['files']['code_files'])}")
        
        # Count total functions
        total_functions = sum(len(f['functions']) for f in analysis['files']['code_files'])
        print(f"Functions found: {total_functions}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()