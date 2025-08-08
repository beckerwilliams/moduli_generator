# Moduli Generator Documentation System Diagram

```
+----------------------------------------------------+
|                 Documentation System                |
+----------------------------------------------------+
                           |
           +---------------+----------------+
           |                                |
+----------v-----------+      +------------v---------+
|    Source Files      |      |   Build Process      |
+----------------------+      +----------------------+
| - docs/*.md          |      | - MkDocs             |
| - docs/*.rst         |      | - mkdocstrings       |
| - Python docstrings  |      | - pydoc-markdown     |
| - Sample configs     |      | - start_docserver.sh |
+----------+-----------+      +------------+---------+
           |                                |
           |                                v
+----------v-----------+      +------------+---------+
|  Documentation Types |      |    Output Files      |
+----------------------+      +----------------------+
| - User guides        |      | - site/*.html        |
| - API reference      |      | - site/assets/       |
| - Installation guides|      | - site/javascript/   |
| - Database docs      |      | - site/sitemap.xml   |
| - Project management |      +----------------------+
+----------------------+

```

## Documentation Flow

1. **Source Files**:
    - Markdown files (*.md) in the docs/ directory
    - reStructuredText files (*.rst) in the docs/ directory
    - Python docstrings in the codebase
    - Sample configuration files

2. **Build Process**:
    - MkDocs (primary build system)
    - mkdocstrings plugin (processes Python docstrings)
    - pydoc-markdown (alternative docstring processor)
    - start_docserver.sh (local development server)

3. **Documentation Types**:
    - User guides (usage.md, etc.)
    - API reference (generated from docstrings)
    - Installation guides (command_line_installer.md)
    - Database documentation (DATABASE_INTEGRATION.rst, MARIADB.md)
    - Project management (REFACTORING_SUMMARY.md, project_improvement_recommendations.md)

4. **Output Files**:
    - HTML files in the site/ directory
    - Assets (CSS, images)
    - JavaScript files
    - Sitemap and other metadata

## Current Documentation Architecture

```
+-------------+     +-----------+     +------------+
| Source Code |---->| Docstrings|---->| API Docs   |
+-------------+     +-----------+     +------------+
                         |
                         v
+-------------+     +-----------+     +------------+
| Markdown &  |---->| MkDocs    |---->| Static Site|
| RST Files   |     | Build     |     |            |
+-------------+     +-----------+     +------------+
```

The documentation system uses a hybrid approach:

- Manual documentation files (.md, .rst) for user guides and project information
- Automated generation of API documentation from docstrings
- Two different tools (mkdocstrings and pydoc-markdown) for processing docstrings
- MkDocs for final site generation