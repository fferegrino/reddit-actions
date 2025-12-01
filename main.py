"""Main entry point for the Reddit actions application."""

from dotenv import load_dotenv

from action_executor import ActionExecutor
from instapaper_action import InstapaperAction

load_dotenv()


def main():
    """Initialize actions and execute them on saved Reddit submissions."""
    actions = [InstapaperAction()]
    action_executor = ActionExecutor(actions)
    action_executor.execute()


if __name__ == "__main__":
    main()
