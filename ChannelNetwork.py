import logging
from typing import Optional, Generator, Set, Tuple, List, Dict
from collections import Counter
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_youtube_client(api_key: str):
    return build("youtube", "v3", developerKey=api_key)


def get_uploads_playlist_id(youtube, channel_id: str) -> Optional[str]:

    try:
        resp = youtube.channels().list(part="contentDetails", id=channel_id).execute()
        items = resp.get("items", [])
        if not items:
            logger.warning("No channel found for id=%s", channel_id)
            return None
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except HttpError as e:
        logger.error("YouTube API error while fetching channel contentDetails: %s", e)
        return None


def iterate_playlist_video_ids(youtube, playlist_id: str) -> Generator[str, None, None]:

    next_page_token = None
    while True:
        resp = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        ).execute()
        for item in resp.get("items", []):

            resource = item.get("snippet", {}).get("resourceId", {})
            video_id = resource.get("videoId")
            if video_id:
                yield video_id
        next_page_token = resp.get("nextPageToken")
        if not next_page_token:
            break


def commenter_has_public_subs(youtube, commenter_channel_id: str) -> bool:

    try:
        resp = youtube.subscriptions().list(
            part="id",
            channelId=commenter_channel_id,
            maxResults=1
        ).execute()
        return bool(resp.get("items"))
    except HttpError as e:
        logger.debug("Could not check subscriptions for %s: %s", commenter_channel_id, e)
        return False
    except Exception as e:
        logger.debug("Unexpected error checking subs for %s: %s", commenter_channel_id, e)
        return False


def collect_commenters_with_public_subs(
    youtube,
    uploads_playlist_id: str,
    max_commenters: int = 50
) -> Set[str]:

    commenters_with_public_subs: Set[str] = set()

    for video_id in iterate_playlist_video_ids(youtube, uploads_playlist_id):
        logger.info("Scanning comments for video: %s", video_id)

        comment_page_token = None
        while True:
            try:
                comments_resp = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=comment_page_token,
                ).execute()
            except HttpError as e:
                logger.warning("Skipping comments for video %s due to API error: %s", video_id, e)
                break
            except Exception as e:
                logger.warning("Unexpected error when fetching comments for %s: %s", video_id, e)
                break

            for thread in comments_resp.get("items", []):
                author_info = thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                author_channel_id_obj = author_info.get("authorChannelId", {})
                commenter_id = author_channel_id_obj.get("value")
                if not commenter_id:
                    continue

                
                if commenter_id in commenters_with_public_subs:
                    continue

                
                if commenter_has_public_subs(youtube, commenter_id):
                    commenters_with_public_subs.add(commenter_id)
                    logger.info("Found commenter with public subs: %s (total=%d)", commenter_id, len(commenters_with_public_subs))

                if len(commenters_with_public_subs) >= max_commenters:
                    logger.info("Reached max_commenters (%d).", max_commenters)
                    return commenters_with_public_subs

            comment_page_token = comments_resp.get("nextPageToken")
            if not comment_page_token:
                break

    logger.info("Collected %d commenters with public subscriptions.", len(commenters_with_public_subs))
    return commenters_with_public_subs


def get_subscriptions_for_commenter(
    youtube,
    commenter_channel_id: str,
    max_subscriptions: int = 50
) -> List[Tuple[str, str]]:

    results: List[Tuple[str, str]] = []
    page_token = None
    fetched = 0

    while True:
        try:
            resp = youtube.subscriptions().list(
                part="snippet",
                channelId=commenter_channel_id,
                maxResults=50,
                pageToken=page_token
            ).execute()
        except HttpError as e:
            logger.debug("Could not fetch subscriptions for %s: %s", commenter_channel_id, e)
            break
        except Exception as e:
            logger.debug("Unexpected error fetching subs for %s: %s", commenter_channel_id, e)
            break

        for item in resp.get("items", []):
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            sub_channel_id = resource.get("channelId")
            sub_title = snippet.get("title", "(unknown)")
            if sub_channel_id:
                results.append((sub_channel_id, sub_title))
                fetched += 1
                if fetched >= max_subscriptions:
                    break

        if fetched >= max_subscriptions:
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return results


def aggregate_subscriptions(
    youtube,
    commenters: Set[str],
    max_subscriptions_per_commenter: int = 50
) -> Counter:
    """
    Return a Counter mapping (channel_id, title) -> count across all commenters.
    """
    counter = Counter()
    total = len(commenters)
    for idx, commenter_id in enumerate(commenters, start=1):
        subs = get_subscriptions_for_commenter(youtube, commenter_id, max_subscriptions_per_commenter)
        for ch_id, title in subs:
            counter[(ch_id, title)] += 1
        logger.info("[%d/%d] Processed %d subscriptions for commenter %s", idx, total, len(subs), commenter_id)
    return counter


def format_top_subscriptions(counter: Counter, num_nodes: int = 10) -> List[Dict]:

    most_common = counter.most_common(num_nodes)
    return [
        {"channel_id": ch_id, "title": title, "count": count}
        for (ch_id, title), count in most_common
    ]


def most_common_subscriptions(
    api_key: str,
    channel_id: str,
    num_nodes: int = 10,
    max_commenters: int = 50,
    max_subscriptions: int = 50
) -> List[Dict]:

    youtube = build_youtube_client(api_key)

    uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)
    if not uploads_playlist_id:
        logger.error("Could not determine uploads playlist for channel %s", channel_id)
        return []

    commenters = collect_commenters_with_public_subs(youtube, uploads_playlist_id, max_commenters=max_commenters)
    if not commenters:
        logger.warning("No commenters with public subscriptions found.")
        return []

    counter = aggregate_subscriptions(youtube, commenters, max_subscriptions_per_commenter=max_subscriptions)
    return format_top_subscriptions(counter, num_nodes=num_nodes)


if __name__ == "__main__":

    api_key = os.environ.get("YT_API_KEY") # set your YouTube Data API key in environment variable: export YT_API_KEY="your_key_here"
    if not api_key:
        raise ValueError("Please set the YT_API_KEY environment variable")
    
    channel_id = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # MrBeast (example) 
    results = most_common_subscriptions(
        api_key=api_key,
        channel_id=channel_id,
        num_nodes=10,
        max_commenters=100,
        max_subscriptions=30
    )

    df = pd.DataFrame(results)

    print(df)




