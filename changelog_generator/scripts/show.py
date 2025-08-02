from pathlib import PosixPath as Path

from changelog_generator import ChangelogGenerator

project_root = Path(__name__).parent.parent.absolute()


def main():
    """Main entry point for the changelog generator."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate CHANGELOG.rst from git history')
    parser.add_argument(
        "--output",
        "-o",
        default=f"{project_root / 'CHANGELOG.md'}",
        help="Output file name (default: CHANGELOG.md)",
    )
    parser.add_argument(
        "--max-commits",
        "-m",
        type=int,
        default=50,
        help="Maximum number of commits to process (default: 50)",
    )
    parser.add_argument(
        "--project-root",
        "-p",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Create generator and generate changel
    generator = ChangelogGenerator(args.project_root)
    generator.generate_changelog(args.output, args.max_commits)


if __name__ == "__main__":
    exit(main())
