# PyCharm Configuration for MkDocs

This guide explains how to reconfigure PyCharm after converting from Sphinx to MkDocs with Markdown documentation.

## Changes Made

### 1. Run Configurations

- **Removed**: `Sphinx Task in Sphinx.xml` - old Sphinx build configuration
- **Added**: `MkDocs Serve.xml` - serves documentation locally at http://127.0.0.1:8000
- **Added**: `MkDocs Build.xml` - builds static documentation to `site/` directory

### 2. Module Configuration (.idea/moduli_generator.iml)

- **Removed**: `ReSTService` component that forced `.txt` files to be treated as reStructuredText
- **Kept**: Excluded folders including `site/` (mkdocs output directory)

## Additional PyCharm Settings to Configure

### 1. File Associations

1. Go to **File → Settings** (or **PyCharm → Preferences** on macOS)
2. Navigate to **Editor → File Types**
3. Ensure **Markdown** file type includes:
    - `*.md`
    - `*.markdown`
    - `*.mdown`

### 2. Markdown Preview Settings

1. Go to **Languages & Frameworks → Markdown**
2. Configure preview settings:
    - **Preview browser**: Choose your preferred browser
    - **Default layout**: Editor and Preview or Preview Only
    - Enable **Use Grazie in Markdown files** for grammar checking

### 3. Live Templates for Markdown

1. Go to **Editor → Live Templates**
2. Create custom templates for common mkdocs patterns:
    - `adm` → `!!! note "Title"\n    Content`
    - `code` → `\`\`\`python\n$SELECTION$\n\`\`\``

### 4. Plugin Recommendations

Install these plugins from **File → Settings → Plugins**:

- **Markdown Navigator Enhanced** - Advanced Markdown editing
- **PlantUML Integration** - For diagrams in documentation
- **Grazie** - Grammar and spell checking

### 5. Project Structure

Ensure these directories are properly configured:

- `docs/` - Source documentation (should be marked as Sources Root if needed)
- `site/` - Build output (already excluded)

## Using the New Configuration

### Serving Documentation Locally

1. Select **MkDocs Serve** from the run configurations dropdown
2. Click the green play button
3. Open http://127.0.0.1:8000 in your browser
4. Documentation will auto-reload when you edit `.md` files

### Building Documentation

1. Select **MkDocs Build** from the run configurations dropdown
2. Click the green play button
3. Static site will be generated in the `site/` directory

### Editing Markdown Files

- PyCharm now treats `.md` files as Markdown instead of plain text
- Use the split editor view to see live preview while editing
- Syntax highlighting and code completion work for embedded code blocks

## Troubleshooting

### If Markdown files don't show preview:

1. Right-click on a `.md` file
2. Select **Open With → Markdown Editor**
3. Check that Markdown plugin is enabled

### If mkdocs commands don't work:

1. Ensure mkdocs is installed in your project environment
2. Check that the Python interpreter is correctly configured
3. Verify `mkdocs.yml` is in the project root

### For better mkdocstrings support:

1. Install the **Python Docstring Generator** plugin
2. Configure docstring format to **Google** or **NumPy** style
3. Use proper type hints for better API documentation generation

## Next Steps

1. Test the new run configurations
2. Configure Markdown preview settings to your preference
3. Install recommended plugins
4. Set up live templates for common documentation patterns
5. Consider setting up a Git hook to build docs on commit

Your PyCharm environment is now configured for MkDocs development!