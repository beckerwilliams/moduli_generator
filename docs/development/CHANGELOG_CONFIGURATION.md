# ChangelogGenerator Configuration Guide

This guide explains how to control the number of dates and commits that appear in your generated changelog.

## Overview

The `ChangelogGenerator` class provides flexible options for controlling how much history to include in your changelog.
The primary control mechanism is the `max_commits` parameter.

## Basic Usage

```python
from changelog_generator import ChangelogGenerator

# Create a generator instance
generator = ChangelogGenerator()

# Generate changelog with default settings (50 commits)
generator.generate_changelog()
```

## Controlling Output Size

### Generate FEWER dates (shorter changelog)

```python
# Generate changelog with only the last 5 commits
generator.generate_changelog(max_commits=5)

# Generate changelog with only the last 10 commits  
generator.generate_changelog(max_commits=10)

# Generate changelog with only the last 20 commits
generator.generate_changelog(max_commits=20)
```

### Generate MORE dates (longer changelog)

```python
# Generate changelog with the last 100 commits
generator.generate_changelog(max_commits=100)

# Generate changelog with the last 200 commits
generator.generate_changelog(max_commits=200)

# Generate changelog with all available commits
generator.generate_changelog(max_commits=1000)
```

## Parameters

### `max_commits` (int, optional)

- **Default**: 50
- **Description**: Maximum number of recent commits to include in the changelog
- **Effect**: More commits = more dates in the changelog (assuming commits span multiple dates)

### `output_file` (str, optional)

- **Default**: "CHANGELOG.md"
- **Description**: Name of the output changelog file
- **Example**: `generator.generate_changelog(output_file="MY_CHANGELOG.md")`

## How It Works

1. **Commit Retrieval**: The generator fetches the specified number of recent commits from git history
2. **Date Grouping**: Commits are automatically grouped by their commit date
3. **Deduplication**: Duplicate commit messages are automatically removed
4. **Categorization**: Commits are categorized (Features, Bug Fixes, etc.) based on their content

## Examples by Use Case

### Quick Summary (Recent Changes Only)

```python
# Perfect for release notes or recent updates
generator.generate_changelog(
    output_file="RECENT_CHANGES.md",
    max_commits=15
)
```

### Comprehensive History

```python
# Perfect for full project documentation
generator.generate_changelog(
    output_file="FULL_HISTORY.md",
    max_commits=500
)
```

### Monthly Report

```python
# Approximately 30-60 commits depending on activity
generator.generate_changelog(
    output_file="MONTHLY_CHANGELOG.md",
    max_commits=60
)
```

## Expected Output Sizes

Based on typical commit patterns:

| max_commits  | Typical Date Sections | File Size (approx) | Use Case              |
|--------------|-----------------------|--------------------|-----------------------|
| 5-10         | 2-4 dates             | 500-1000 bytes     | Quick summary         |
| 20-30        | 5-10 dates            | 1-3 KB             | Sprint/milestone      |
| 50 (default) | 10-20 dates           | 3-5 KB             | Standard changelog    |
| 100+         | 20-40 dates           | 5-10 KB            | Comprehensive history |

## Tips

1. **Start Small**: Begin with a small `max_commits` value and increase as needed
2. **Regular Updates**: For ongoing projects, use smaller values (10-30) for regular updates
3. **Documentation**: For project documentation, use larger values (100+) for comprehensive history
4. **Performance**: Very large values (1000+) may take longer to process but won't significantly impact file size if
   your project has fewer total commits

## Command Line Usage

You can also run the generator directly:

```bash
# Generate with default settings
python -c "from changelog_generator import ChangelogGenerator; ChangelogGenerator().generate_changelog()"

# Generate with custom commit count
python -c "from changelog_generator import ChangelogGenerator; ChangelogGenerator().generate_changelog(max_commits=25)"
```

## Demo Script

Run the included demonstration script to see different output sizes:

```bash
python demo_changelog_options.py
```

This will generate three different changelog files showing the impact of different `max_commits` values.