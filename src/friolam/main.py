"""CLI entry point for Friolam."""

from friolam import __version__


def get_status_message() -> str:
    """Return a human-readable status line for the project."""
    return f"Friolam is set up and running (v{__version__})."


def main() -> None:
    """Run the Friolam CLI."""
    print(get_status_message())


if __name__ == "__main__":
    main()
