#!/usr/bin/env python3
"""
Changelog Generator for the moduli_generator project

This script generates a CHANGELOG.rst file from git commit history,
organizing commits by date in reStructuredText format.
"""
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import toml

__all__ = ["ChangelogGenerator"]


def _categorize_commit(message):
    """Categorize commit based on message content."""
    message_lower = message.lower()

    # Define categories and their keywords
    categories = {
        "Database Improvements": [
            "database",
            "db",
            "mariadb",
            "connector",
            "sql",
            "schema",
            "transactional",
            "parameterized",
        ],
        "Bug Fixes": ["fix", "fixed", "bug", "error", "issue", "correct"],
        "Features": [
            "add",
            "added",
            "new",
            "feature",
            "implement",
            "create",
            "created",
        ],
        "Refactoring": [
            "refactor",
            "refactored",
            "restructure",
            "reorganize",
            "cleanup",
        ],
        "Documentation": ["docs", "documentation", "readme", "comment", "docstring"],
        "Configuration": [
            "config",
            "configuration",
            "settings",
            "default",
            "constants",
        ],
        "Testing": ["test", "testing", "tests", "successful", "complete"],
        "Performance": ["performance", "optimize", "speed", "efficiency"],
        "Security": ["security", "secure", "vulnerability", "auth"],
    }

    # Check for category keywords
    for category, keywords in categories.items():
        if any(keyword in message_lower for keyword in keywords):
            return category

    # Check for specific patterns
    if "checkpoint" in message_lower or "milestone" in message_lower:
        return "Milestones"

    if "production" in message_lower or "release" in message_lower:
        return "Releases"

    return "General"


class ChangelogGenerator:
    """
    Generates changelog files for a project by extracting and parsing commit history
    from a Git repository. It also integrates project metadata from a pyproject.toml file
    if available. The changelog includes grouped commits by date and categorizes them
    for better readability.

    Detailed description of the class, its purpose, and usage.

    Attributes:
        project_root (Path): The root directory of the project used for locating
            metadata and Git operations.
        project_info (dict): Metadata of the project parsed from the pyproject.toml file,
            including details like the project name, version, description, and authors.
    """

    def __init__(self, project_root=None):
        """
        Initializes the class with a given project root directory and loads related
                project information. If no project root is provided, it defaults to the
                current working directory.

        Args:
            project_root (str or None): The root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.project_info = self._load_project_info()

    def _load_project_info(self):
        """Load project information from pyproject.toml."""
        try:
            pyproject_path = self.project_root / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "r") as f:
                    data = toml.load(f)
                    return data.get("tool", {}).get("poetry", {})
        except Exception as e:
            print(f"Warning: Could not load pyproject.toml: {e}")

        return {}

    def _get_git_commits(self, max_commits=50):
        """Get git commit history with dates and messages."""
        try:
            # Get a commit log with format: hash|date|author|message
            cmd = [
                "git",
                "log",
                f"--max-count={max_commits}",
                "--pretty=format:%H|%ad|%an <%ae>|%s",
                "--date=short",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode != 0:
                raise RuntimeError(f"Git command failed: {result.stderr}")

            # The following cleans up 'asterisk' cruft I've created in my Changelog Records
            # cleanup = re.sub(r'\*\*\*', '**', result.stdout.strip().split('\n'))
            #
            # r2 = result.stdout.strip().split('\n')
            return re.sub(r"\*\*\*", "**", result.stdout).strip().split("\n")

        except Exception as e:
            print(f"Error getting git commits: {e}")
            return []

    @staticmethod
    def _parse_commit_line(line):
        """Parse a single commit line into components."""
        try:
            parts = line.split("|", 3)
            if len(parts) != 4:
                return None

            hash_id, date_str, author, message = parts

            # Parse date
            commit_date = datetime.strptime(date_str, "%Y-%m-%d")

            return {
                "hash": hash_id,
                "date": commit_date,
                "author": author,
                "message": message.strip(),
            }
        except Exception as e:
            print(f"Error parsing commit line '{line}': {e}")
            return None

    @staticmethod
    def _format_commit_message(message):
        """Format commit message for changelog."""
        # Remove common prefixes and clean up
        message = re.sub(r"^(feat|fix|docs|style|refactor|test|chore):\s*", "", message)

        # Capitalize the first letter
        if message:
            message = message[0].upper() + message[1:]

        # Remove trailing periods and normalize
        message = message.rstrip(".")

        return message

    @staticmethod
    def _group_commits_by_date(commits):
        """Group commits by date."""
        grouped = defaultdict(list)

        for commit in commits:
            if commit:  # Skip None commits
                date_key = commit["date"].strftime("%Y-%m-%d")
                grouped[date_key].append(commit)

        return grouped

    def _generate_markdown_header(self):
        """Generate the Markdown header section."""
        header = [
            "# Changelog",
            "",
            "This document tracks the changes made to the moduli_generator project.",
            "",
        ]

        # Add version info if available
        if self.project_info.get("version"):
            header.append(f"## Version {self.project_info['version']}")
            header.append("")
            (Path.cwd() / "config" / "__version__.py").write_text(
                f"version = '{self.project_info['version']}'\n"
            )

        return header

    def _generate_date_section(self, date_str, commits):
        """Generate a Markdown section for a specific date."""
        section = []

        # Convert date string to readable format
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")

        section.append(f"## {formatted_date}")
        section.append("")

        # Group commits by category
        categorized = defaultdict(list)
        for commit in commits:
            category = _categorize_commit(commit["message"])
            categorized[category].append(commit)

        # Add commits by category
        for category in sorted(categorized.keys()):
            category_commits = categorized[category]

            if len(category_commits) == 1:
                # Single commit - format as a bullet point with category
                commit = category_commits[0]
                formatted_msg = self._format_commit_message(commit["message"])
                section.append(f"* **{category}**: {formatted_msg}")
            else:
                # Multiple commits - create a subsection
                section.append(f"**{category}**:")
                section.append("")
                for commit in category_commits:
                    formatted_msg = self._format_commit_message(commit["message"])
                    section.append(f"  * {formatted_msg}")
                section.append("")

        section.append("")
        return section

    def _generate_project_info_section(self):
        """Generate project information section."""
        section = ["## Project Information", ""]

        info = self.project_info
        if info.get("name"):
            section.append(f"* **Project**: {info['name']}")
        if info.get("version"):
            section.append(f"* **Version**: {info['version']}")
        if info.get("description"):
            section.append(f"* **Description**: {info['description']}")
        if info.get("authors"):
            authors = info["authors"]
            if isinstance(authors, list):
                section.append(f"* **Author**: {authors[0]}")
            else:
                section.append(f"* **Author**: {authors}")

        # Add URLs if available
        urls = info.get("urls", {})
        if urls.get("Repository"):
            section.append(f"* **Repository**: {urls['Repository']}")
        if urls.get("Homepage"):
            section.append(f"* **Homepage**: {urls['Homepage']}")

        section.append("* **License**: See docs/license.md")
        section.append("")

        return section

    def generate_changelog(self, output_file="CHANGELOG.md", max_commits=50) -> None:
        """
        Generates a changelog file based on git commit history and saves it to the
                specified output file. The changelog is formatted in reStructuredText (RST)
                format and includes grouped commit entries by date in descending order.

        Args:
            max_commits (int, optional): The maximum number of recent commits to include in the             changelog, with a default value of 50.
            output_file (str, optional): The name of the output changelog file with the default value "CHANGELOG.rst".

        Returns:
            None: None
        """
        print("Generating changelog...")

        # Get git commits
        commit_lines = self._get_git_commits(max_commits)
        if not commit_lines:
            print("No git commits found.")
            return

        # Parse commits
        commits = []
        for line in commit_lines:
            if line.strip():
                commit = self._parse_commit_line(line)
                if commit:
                    commits.append(commit)

        if not commits:
            print("No valid commits found.")
            return

        print(f"Found {len(commits)} commits")

        # Remove duplicate commits based on message content
        # Keep the most recent commit for each unique message
        seen_messages = {}
        deduplicated_commits = []

        for commit in commits:
            message = commit["message"]
            if message not in seen_messages:
                seen_messages[message] = commit
                deduplicated_commits.append(commit)
            else:
                # Keep the more recent commit (earlier in the list since git log is reverse chronological)
                existing_commit = seen_messages[message]
                if commit["date"] > existing_commit["date"]:
                    # Replace the existing commit with the more recent one
                    seen_messages[message] = commit
                    # Remove the old commit and add the new one
                    deduplicated_commits = [
                        c for c in deduplicated_commits if c["message"] != message
                    ]
                    deduplicated_commits.append(commit)

        duplicates_removed = len(commits) - len(deduplicated_commits)
        if duplicates_removed > 0:
            print(f"Removed {duplicates_removed} duplicate commit entries")

        commits = deduplicated_commits

        # Group by date
        grouped_commits = self._group_commits_by_date(commits)

        # Generate changelog content
        changelog_lines = []

        # Add header
        changelog_lines.extend(self._generate_markdown_header())

        # Add date sections (most recent first)
        for date_str in sorted(grouped_commits.keys(), reverse=True):
            date_commits = grouped_commits[date_str]
            changelog_lines.extend(self._generate_date_section(date_str, date_commits))

        # Add the project info section
        changelog_lines.extend(self._generate_project_info_section())

        # Write to a file
        output_path = self.project_root / output_file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(changelog_lines))

            print(f"Changelog written to {output_path}")
            print(
                f"Generated {len(grouped_commits)} date sections from {len(commits)} commits"
            )

        except Exception as e:
            print(f"Error writing changelog: {e}")
