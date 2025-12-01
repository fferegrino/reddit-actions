"""Base action class for filtering and executing operations on Reddit submissions."""

from collections.abc import Callable, Iterable
from datetime import datetime, timedelta

from praw.models import Submission


class Action:
    """
    Base class for defining actions to perform on Reddit submissions.

    An Action filters Reddit submissions based on configurable criteria and
    executes a custom function on matching submissions. Filters include
    subreddit names, post age, post type (self-post vs link), and URL presence.
    """

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        action: Callable[[Submission], bool | None],
        *,
        subreddits: Iterable[str] | None = None,
        max_age_days: int | None = None,
        min_age_days: int | None = None,
        is_self_post: bool | None = None,
        has_url: bool | None = None,
        dry_run: bool = False,
        delete_after_execution: bool = False,
    ):
        """
        Initialize an Action with filtering criteria and execution behavior.

        Args:
            name: Identifier for this action.
            action: Callable that takes a Submission and returns a boolean
                indicating success, or None to indicate default success.
            subreddits: Optional set of subreddit names (case-insensitive) to
                filter submissions. If None, all subreddits are included.
            max_age_days: Optional maximum age in days for submissions.
                Older submissions are excluded.
            min_age_days: Optional minimum age in days for submissions.
                Newer submissions are excluded.
            is_self_post: Optional filter for self-posts (True) or link posts
                (False). If None, both types are included.
            has_url: Optional filter for posts with URLs (True) or without
                (False). If None, both types are included.
            dry_run: If True, print what would be executed without actually
                executing the action.
            delete_after_execution: If True, mark the submission for deletion
                after successful execution.

        """
        self.name = name
        self.subreddits = set(subreddits) if subreddits is not None else None
        self.max_age_days = max_age_days
        self.min_age_days = min_age_days
        self.is_self_post = is_self_post
        self.has_url = has_url
        self.dry_run = dry_run
        self.delete_after_execution = delete_after_execution
        self.action = action

    def _should_execute(self, submission: Submission) -> bool:
        """
        Check if the action should be executed on the given submission.

        Evaluates all configured filters (subreddit, age, post type, URL)
        against the submission.

        Args:
            submission: The Reddit submission to evaluate.

        Returns:
            True if all filters pass and the action should execute,
            False otherwise.

        """
        if self.subreddits is not None and submission.subreddit.display_name.lower() not in self.subreddits:
            return False
        if self.max_age_days is not None and submission.created_utc < datetime.now() - timedelta(
            days=self.max_age_days
        ):
            return False
        if self.min_age_days is not None and submission.created_utc > datetime.now() - timedelta(
            days=self.min_age_days
        ):
            return False
        if self.is_self_post is not None and submission.is_self != self.is_self_post:
            return False
        if self.has_url is not None and (submission.url is None or submission.url == ""):  # noqa: SIM103
            return False
        return True

    def execute(self, submission: Submission) -> bool:
        """
        Execute the action on a submission if it passes all filters.

        Checks if the submission matches the configured filters, then either
        executes the action (or simulates it in dry-run mode).

        Args:
            submission: The Reddit submission to process.

        Returns:
            Boolean indicating whether the action was executed successfully,
            or None/False if execution was skipped or failed.

        """
        if not self._should_execute(submission):
            return False
        if self.dry_run:
            print(f"Would execute action {self.name} on submission: {submission.title}")
            return False
        result = self.action(submission)
        if result is not None:
            return result
        return True
