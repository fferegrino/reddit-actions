"""
Reddit API Integration

This module provides functions to interact with Reddit API using PRAW
(Python Reddit API Wrapper). It handles authentication, fetching saved
threads, and managing saved posts.

Configuration:
- Filters threads from specific subreddits
- Only processes self-posts (text posts, not links)
- Only processes threads older than TIME_OFFSET_IN_DAYS
"""

import datetime
import os

import praw
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User agent string for Reddit API (required by Reddit API rules)
USER_AGENT = "RedditActions/0.1 by fferegrino"

# Set of subreddit names to filter saved threads
SELECT_SUBREDDITS = {
}

# Minimum age of threads to process (in days)
# Threads must be older than this to be processed
TIME_OFFSET_IN_DAYS = 2

# Global Reddit client instance (singleton pattern)
_REDDIT_CLIENT = None


def get_reddit_client():
    """
    Get or create a Reddit API client instance (singleton pattern).

    Loads credentials from environment variables and creates a PRAW
    Reddit instance. Subsequent calls return the same instance.

    Environment Variables Required:
        REDDIT_CLIENT_ID: Reddit application client ID
        REDDIT_CLIENT_SECRET: Reddit application client secret
        REDDIT_USERNAME: Reddit username
        REDDIT_PASSWORD: Reddit password

    Returns:
        praw.Reddit: Authenticated Reddit client instance

    Raises:
        KeyError: If required environment variables are missing
    """
    global _REDDIT_CLIENT
    if _REDDIT_CLIENT is not None:
        return _REDDIT_CLIENT

    load_dotenv()

    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=USER_AGENT,
        username=os.environ["REDDIT_USERNAME"],
        password=os.environ["REDDIT_PASSWORD"],
    )

    return reddit


def get_thread_from_url(url):
    """
    Fetch a Reddit thread (submission) by its URL.

    Args:
        url: Full URL of the Reddit thread

    Returns:
        praw.models.Submission: The Reddit submission object
    """
    reddit = get_reddit_client()
    submission = reddit.submission(url=url)
    return submission


def remove_from_saved(url):
    """
    Remove a Reddit thread from the authenticated user's saved posts.

    Args:
        url: Full URL of the Reddit thread to unsave
    """
    print(f"Removing {url} from saved")
    reddit = get_reddit_client()
    submission = reddit.submission(url=url)
    submission.unsave()


def get_saved_threads_for_user():
    """
    Generator that yields saved Reddit threads matching filtering criteria.

    Filters threads based on:
    - Subreddit must be in SELECT_SUBREDDITS
    - Must be a self-post (text post, not a link)
    - Must be older than TIME_OFFSET_IN_DAYS

    Yields:
        praw.models.Submission: Reddit submission objects that match criteria

    Note:
        This is a generator function, so it yields items one at a time
        rather than returning a complete list. This is memory-efficient
        for large numbers of saved posts.
    """
    # Calculate cutoff timestamp (threads must be older than this)
    thread_cutoff = datetime.datetime.now() - datetime.timedelta(days=TIME_OFFSET_IN_DAYS)

    reddit = get_reddit_client()

    # Get all saved items (limit=None means get all)
    saved = reddit.user.me().saved(limit=None)

    # Filter and yield matching threads
    for item in saved:
        # Check if subreddit is in selected list and is a self-post
        subreddit_name = item.subreddit.display_name.lower()
        if subreddit_name in SELECT_SUBREDDITS and item.is_self:
            # Check if thread is old enough
            if item.created_utc < thread_cutoff.timestamp():
                yield item
            else:
                logger.info(f"Skipping thread: {item.title} because it is not old enough")
        else:
            logger.info(f"Skipping thread: {item.id} because {subreddit_name} is not in the selected subreddits")

    
