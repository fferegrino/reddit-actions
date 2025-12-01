"""Executor for applying actions to saved Reddit submissions."""

import os

import praw
from praw.models import Submission

from action import Action


class ActionExecutor:
    """
    Execute actions on saved Reddit submissions.

    Connects to Reddit using PRAW, retrieves saved submissions, and applies
    a list of actions to each submission. Can optionally delete submissions
    after actions are successfully executed.
    """

    def __init__(
        self,
        actions: list[Action],
        max_submissions: int | None = None,
        dry_run: bool = False,
    ):
        """
        Initialize the ActionExecutor with actions and configuration.

        Sets up Reddit connection using credentials from environment variables:
        REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD.

        Args:
            actions: List of Action instances to execute on each submission.
            max_submissions: Optional limit on the number of saved submissions
                to process. If None, processes all saved submissions.
            dry_run: If True, simulates execution without making changes.

        """
        self.actions = actions
        self.submissions_to_delete = {}
        self.max_submissions = max_submissions
        self.dry_run = dry_run
        self.reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
        )

    def execute(self) -> None:
        """
        Execute all actions on saved Reddit submissions.

        Iterates through the user's saved submissions, applies each action,
        and deletes submissions that were marked for deletion after successful
        execution (unless in dry-run mode).
        """
        saved = self.reddit.user.me().saved(limit=self.max_submissions)
        for submission in saved:
            if not isinstance(submission, Submission):
                continue
            for action in self.actions:
                did_execute = action.execute(submission)
                if did_execute and action.delete_after_execution:
                    self.submissions_to_delete[submission.id] = submission

        if self.dry_run:
            print(f"Would delete {len(self.submissions_to_delete)} submissions")
            return
        for submission in self.submissions_to_delete.values():
            submission.delete()
