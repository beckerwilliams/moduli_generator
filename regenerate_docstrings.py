#!/usr/bin/env python3
"""
Script to regenerate docstrings from Sphinx format to Google format.
This script processes all Python files in the project and converts docstrings
from Sphinx-style (:param:, :type:, :return:, :rtype:) to Google-style format.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DocstringConverter:
    """Converts Sphinx-style docstrings to Google-style format."""
    
    def __init__(self):
        self.sphinx_param_pattern = re.compile(r':param\s+(\w+):\s*(.*?)(?=\n\s*:|\n\s*$|\Z)', re.DOTALL)
        self.sphinx_type_pattern = re.compile(r':type\s+(\w+):\s*(.*?)(?=\n\s*:|\n\s*$|\Z)', re.DOTALL)
        self.sphinx_return_pattern = re.compile(r':return:\s*(.*?)(?=\n\s*:|\n\s*$|\Z)', re.DOTALL)
        self.sphinx_rtype_pattern = re.compile(r':rtype:\s*(.*?)(?=\n\s*:|\n\s*$|\Z)', re.DOTALL)
        self.sphinx_raises_pattern = re.compile(r':raises?\s+(\w+):\s*(.*?)(?=\n\s*:|\n\s*$|\Z)', re.DOTALL)
        
    def convert_docstring(self, docstring: str) -> str:
        """Convert a Sphinx-style docstring to Google format.
        
        Args:
            docstring: The original Sphinx-style docstring.
            
        Returns:
            The converted Google-style docstring.
        """
        if not docstring or not self._has_sphinx_tags(docstring):
            return docstring
            
        lines = docstring.split('\n')
        
        # Extract the main description (everything before first :param:, :type:, etc.)
        description_lines = []
        sphinx_section_start = None
        
        for i, line in enumerate(lines):
            if re.match(r'\s*:(param|type|return|rtype|raises?)(\s|:)', line):
                sphinx_section_start = i
                break
            description_lines.append(line)
        
        # Clean up description
        description = '\n'.join(description_lines).strip()
        
        # Extract parameters, types, return info, and raises info
        sphinx_section = '\n'.join(lines[sphinx_section_start:]) if sphinx_section_start else ""
        
        params = self._extract_params(sphinx_section)
        types = self._extract_types(sphinx_section)
        return_info = self._extract_return(sphinx_section)
        rtype_info = self._extract_rtype(sphinx_section)
        raises_info = self._extract_raises(sphinx_section)
        
        # Build Google-style docstring
        google_parts = []
        
        if description:
            google_parts.append(description)
        
        # Add Args section
        if params or types:
            google_parts.append("")
            google_parts.append("Args:")
            
            # Combine params with their types
            param_names = set(params.keys()) | set(types.keys())
            for param_name in sorted(param_names):
                param_desc = params.get(param_name, "").strip()
                param_type = types.get(param_name, "").strip()
                
                if param_type and param_desc:
                    google_parts.append(f"    {param_name} ({param_type}): {param_desc}")
                elif param_desc:
                    google_parts.append(f"    {param_name}: {param_desc}")
                elif param_type:
                    google_parts.append(f"    {param_name} ({param_type}): Parameter description.")
        
        # Add Returns section
        if return_info or rtype_info:
            google_parts.append("")
            google_parts.append("Returns:")
            
            return_desc = return_info.strip() if return_info else "Return value."
            return_type = rtype_info.strip() if rtype_info else ""
            
            if return_type and return_desc:
                google_parts.append(f"    {return_type}: {return_desc}")
            elif return_desc:
                google_parts.append(f"    {return_desc}")
        
        # Add Raises section
        if raises_info:
            google_parts.append("")
            google_parts.append("Raises:")
            for exception_type, exception_desc in raises_info.items():
                google_parts.append(f"    {exception_type}: {exception_desc.strip()}")
        
        return '\n'.join(google_parts)
    
    def _has_sphinx_tags(self, docstring: str) -> bool:
        """Check if docstring contains Sphinx-style tags."""
        return bool(re.search(r':(param|type|return|rtype|raises?)(\s|:)', docstring))
    
    def _extract_params(self, text: str) -> Dict[str, str]:
        """Extract parameter descriptions from Sphinx docstring."""
        params = {}
        for match in self.sphinx_param_pattern.finditer(text):
            param_name = match.group(1)
            param_desc = match.group(2).strip().replace('\n', ' ')
            params[param_name] = param_desc
        return params
    
    def _extract_types(self, text: str) -> Dict[str, str]:
        """Extract parameter types from Sphinx docstring."""
        types = {}
        for match in self.sphinx_type_pattern.finditer(text):
            param_name = match.group(1)
            param_type = match.group(2).strip().replace('\n', ' ')
            types[param_name] = param_type
        return types
    
    def _extract_return(self, text: str) -> Optional[str]:
        """Extract return description from Sphinx docstring."""
        match = self.sphinx_return_pattern.search(text)
        return match.group(1).strip().replace('\n', ' ') if match else None
    
    def _extract_rtype(self, text: str) -> Optional[str]:
        """Extract return type from Sphinx docstring."""
        match = self.sphinx_rtype_pattern.search(text)
        return match.group(1).strip().replace('\n', ' ') if match else None
    
    def _extract_raises(self, text: str) -> Dict[str, str]:
        """Extract raises information from Sphinx docstring."""
        raises = {}
        for match in self.sphinx_raises_pattern.finditer(text):
            exception_type = match.group(1)
            exception_desc = match.group(2).strip().replace('\n', ' ')
            raises[exception_type] = exception_desc
        return raises


class FileProcessor:
    """Processes Python files to convert docstrings."""
    
    def __init__(self):
        self.converter = DocstringConverter()
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single Python file to convert its docstrings.
        
        Args:
            file_path: Path to the Python file to process.
            
        Returns:
            True if the file was modified, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST to find docstrings
            tree = ast.parse(content)
            
            # Find all docstring locations
            docstring_locations = self._find_docstrings(tree, content)
            
            if not docstring_locations:
                return False
            
            # Process docstrings from end to beginning to maintain line numbers
            modified = False
            for start_line, end_line, original_docstring in reversed(docstring_locations):
                converted = self.converter.convert_docstring(original_docstring)
                
                if converted != original_docstring:
                    content = self._replace_docstring_in_content(
                        content, start_line, end_line, converted
                    )
                    modified = True
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated docstrings in: {file_path}")
            
            return modified
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def _find_docstrings(self, tree: ast.AST, content: str) -> List[Tuple[int, int, str]]:
        """Find all docstrings in the AST with their line positions.
        
        Args:
            tree: The AST of the Python file.
            content: The original file content.
            
        Returns:
            List of tuples (start_line, end_line, docstring_content).
        """
        docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                docstring_node = ast.get_docstring(node, clean=False)
                if docstring_node:
                    # Find the actual string node
                    if isinstance(node, ast.Module):
                        # Module docstring is the first statement
                        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                            string_node = node.body[0].value
                        else:
                            continue
                    else:
                        # Function/class docstring is the first statement in the body
                        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                            string_node = node.body[0].value
                        else:
                            continue
                    
                    start_line = string_node.lineno
                    end_line = string_node.end_lineno if hasattr(string_node, 'end_lineno') else start_line
                    
                    docstrings.append((start_line, end_line, docstring_node))
        
        return docstrings
    
    def _replace_docstring_in_content(self, content: str, start_line: int, end_line: int, new_docstring: str) -> str:
        """Replace a docstring in the file content.
        
        Args:
            content: The original file content.
            start_line: Starting line number of the docstring (1-based).
            end_line: Ending line number of the docstring (1-based).
            new_docstring: The new docstring content.
            
        Returns:
            The updated file content.
        """
        lines = content.split('\n')
        
        # Find the indentation of the original docstring
        docstring_line = lines[start_line - 1]
        indent_match = re.match(r'^(\s*)', docstring_line)
        indent = indent_match.group(1) if indent_match else ''
        
        # Format the new docstring with proper indentation
        new_lines = new_docstring.split('\n')
        formatted_lines = [indent + '"""']
        
        for line in new_lines:
            if line.strip():
                # Preserve existing indentation within the docstring content
                if line.startswith('    '):  # Args/Returns section items
                    formatted_lines.append(indent + line)
                else:  # Main description lines
                    formatted_lines.append(indent + line)
            else:
                formatted_lines.append('')
        
        formatted_lines.append(indent + '"""')
        
        # Replace the lines
        result_lines = lines[:start_line-1] + formatted_lines + lines[end_line:]
        return '\n'.join(result_lines)


def main():
    """Main function to process all Python files in the project."""
    project_root = Path(__file__).parent
    processor = FileProcessor()
    
    # Find Python files only in main project packages, exclude virtual env and external files
    main_packages = ['moduli_generator', 'config', 'db', 'changelog_generator', 'test']
    python_files = []
    
    # Add root level Python files
    for py_file in project_root.glob('*.py'):
        if py_file.name != 'regenerate_docstrings.py':
            python_files.append(py_file)
    
    # Add files from main packages
    for package in main_packages:
        package_path = project_root / package
        if package_path.exists():
            python_files.extend(package_path.glob('**/*.py'))
    
    print(f"Found {len(python_files)} Python files to process")
    
    modified_count = 0
    for file_path in python_files:
        if processor.process_file(file_path):
            modified_count += 1
    
    print(f"\nCompleted! Modified {modified_count} files.")


if __name__ == '__main__':
    main()