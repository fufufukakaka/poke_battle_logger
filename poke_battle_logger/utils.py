from datetime import datetime
from typing import Optional

from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search


def publish_date(watch_html: str) -> Optional[datetime]:
    """https://github.com/pytube/pytube/issues/1269

    Extract publish date
    :param str watch_html:
        The html contents of the watch page.
    :rtype: str
    :returns:
        Publish date of the video.
    """
    # Check if isLiveBroadcast to get Correct UTC Publish Date +00:00
    try:
        result = regex_search(
            r"(?<=itemprop=\"startDate\" content=\")\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            watch_html,
            group=0,
        )
        return datetime.strptime(result, "%Y-%m-%dT%H:%M:%S")
    except RegexMatchError:
        try:
            result = regex_search(
                r"(?<=itemprop=\"datePublished\" content=\")", watch_html, group=0
            )
            return datetime.strptime(result, "%Y-%m-%d")
        except RegexMatchError:
            return None


def get_youtube_url_with_timestamp(video_url: str, battle_started_at: datetime) -> str:
    yt = YouTube(video_url)
    video_started_at = publish_date(yt.watch_html)
    if video_started_at is None:
        return video_url
    timestamp = battle_started_at - video_started_at
    youtube_url_with_timestamp = f"{video_url}&t={timestamp}"
    return youtube_url_with_timestamp
