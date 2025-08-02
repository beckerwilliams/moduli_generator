#!/usr/bin/env python3
"""
Demonstration script showing how to control the number of dates/commits
in the ChangelogGenerator output.

This script shows different ways to generate changelogs with MORE or LESS dates.
"""
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from changelog_generator import ChangelogGenerator


def demo_different_commit_counts():
    """Demonstrate generating changelogs with different numbers of commits."""

    print("=" * 60)
    print("ChangelogGenerator: Controlling Output Dates/Commits")
    print("=" * 60)
    print()

    generator = ChangelogGenerator()

    # Example 1: Generate changelog with FEWER dates (last 10 commits)
    print("1. Generating changelog with FEWER dates (max_commits=10):")
    print("-" * 50)
    generator.generate_changelog(output_file="CHANGELOG_SHORT.md", max_commits=10)
    print()

    # Example 2: Generate changelog with MORE dates (last 100 commits)
    print("2. Generating changelog with MORE dates (max_commits=100):")
    print("-" * 50)
    generator.generate_changelog(output_file="CHANGELOG_LONG.md", max_commits=100)
    print()

    # Example 3: Generate changelog with ALL commits (no limit)
    print("3. Generating changelog with ALL commits (max_commits=1000):")
    print("-" * 50)
    generator.generate_changelog(output_file="CHANGELOG_ALL.md", max_commits=1000)
    print()

    # Show file sizes for comparison
    print("Generated files comparison:")
    print("-" * 30)

    files = [
        ("CHANGELOG_SHORT.md", "10 commits"),
        ("CHANGELOG_LONG.md", "100 commits"),
        ("CHANGELOG_ALL.md", "1000 commits"),
    ]

    for filename, description in files:
        filepath = Path(filename)
        if filepath.exists():
            size = filepath.stat().st_size
            with open(filepath, "r") as f:
                lines = len(f.readlines())
            print(
                f"  {filename:<20} ({description:<12}): {size:>5} bytes, {lines:>3} lines"
            )
        else:
            print(f"  {filename:<20} ({description:<12}): File not found")

    print()
    print("Usage Examples:")
    print("=" * 40)
    print("from changelog_generator import ChangelogGenerator")
    print()
    print("# Create generator instance")
    print("generator = ChangelogGenerator()")
    print()
    print("# Generate with FEWER dates (last 5 commits)")
    print("generator.generate_changelog(max_commits=5)")
    print()
    print("# Generate with MORE dates (last 200 commits)")
    print("generator.generate_changelog(max_commits=200)")
    print()
    print("# Generate with custom output filename")
    print("generator.generate_changelog(output_file='MY_CHANGELOG.md', max_commits=25)")
    print()


def cleanup_demo_files():
    """Clean up the demo files created."""
    demo_files = ["CHANGELOG_SHORT.md", "CHANGELOG_LONG.md", "CHANGELOG_ALL.md"]

    print("Cleaning up demo files...")
    for filename in demo_files:
        filepath = Path(filename)
        if filepath.exists():
            filepath.unlink()
            print(f"  Removed {filename}")
    print("Cleanup complete.")


if __name__ == "__main__":
    try:
        demo_different_commit_counts()

        # Ask user if they want to keep the demo files
        response = input("\nKeep demo files? (y/N): ").strip().lower()
        if response not in ["y", "yes"]:
            cleanup_demo_files()

    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
        cleanup_demo_files()
    except Exception as e:
        print(f"Error during demo: {e}")
        cleanup_demo_files()
        sys.exit(1)
