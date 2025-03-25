"""
Entry point for the Scoundrel game.
"""
from .ui.tui import ScoundrelApp


def main():
    """Run the Scoundrel game."""
    app = ScoundrelApp()
    app.run()


if __name__ == "__main__":
    main()