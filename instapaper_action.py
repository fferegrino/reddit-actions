"""Action implementation for saving Reddit submission URLs to Instapaper."""

import base64
import os
from collections.abc import Iterable
from urllib.parse import urlparse

import requests
from praw.models import Submission

from action import Action


class InstapaperAction(Action):
    """
    Save Reddit submission URLs to Instapaper.

    Filters for link posts (non-self posts) with URLs, excludes certain
    domains (image hosts, Reddit, YouTube), and saves matching URLs to
    Instapaper with metadata about the source subreddit and title.
    """

    def __init__(self, subreddits: Iterable[str] | None = None, dry_run: bool = False):
        """
        Initialize the InstapaperAction.

        Sets up Instapaper API authentication using credentials from
        environment variables: INSTAPAPER_USER, INSTAPAPER_PASS.

        Args:
            subreddits: Optional list of subreddit names to filter submissions.
                If None, processes submissions from all subreddits.
            dry_run: If True, simulates execution without saving to Instapaper.

        """
        super().__init__(
            name="instapaper",
            action=self.execute,
            delete_after_execution=True,
            subreddits=subreddits,
            is_self_post=False,
            has_url=True,
            dry_run=dry_run,
        )

        self.basic_auth = f"{os.environ['INSTAPAPER_USER']}:{os.environ['INSTAPAPER_PASS']}"
        self.basic_auth_encoded = base64.b64encode(self.basic_auth.encode()).decode()

        self.exclude_domains = [
            "i.redd.it",
            "imgur.com",
            "reddit.com",
            "v.redd.it",
            "www.reddit.com",
            "www.youtube.com",
            "youtu.be",
            "youtube.com",
        ]

    def execute(self, submission: Submission) -> bool:
        """
        Save the submission URL to Instapaper.

        Checks if the submission's domain is in the exclusion list, then
        sends the URL to Instapaper's API with metadata about the source
        subreddit and post title.

        Args:
            submission: The Reddit submission to save.

        Returns:
            True if successfully saved to Instapaper, False otherwise.

        """
        parsed_url = urlparse(submission.url)
        domain = parsed_url.netloc
        if domain in self.exclude_domains:
            return False
        print(submission.url)

        try:
            query_params = {
                "url": submission.url,
                "selection": f'From r/{submission.subreddit.display_name}: "{submission.title}"',
            }
            response = requests.get(
                "https://www.instapaper.com/api/add",
                headers={
                    "Authorization": f"Basic {self.basic_auth_encoded}",
                },
                params=query_params,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error adding to Instapaper: {e}")
            return False
        return True
