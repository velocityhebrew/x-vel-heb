"""
Twitter/X Upload Script

Uploads videos to Twitter/X using the current X platform endpoints.
- Media upload: API v1.1 (upload.twitter.com)
- Posting:      API v2 on https://api.x.com (the current X host)

Requirements:
- X Developer App (OAuth 1.0a user token)
- TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
"""

import os
import sys
import time
import tweepy
import requests
from pathlib import Path
from dotenv import load_dotenv
from tweepy.auth import OAuth1UserHandler

# Configure UTF-8 encoding for console output (Windows fix)
if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Load environment variables
load_dotenv()

# Current X platform host for v2 writes
X_HOST = "https://api.x.com"

# tweepy hardcodes api.twitter.com in BaseClient.request and rejects both
# `host` and `base_url`. Patch the method so v2 writes hit the current
# X host (api.x.com), which is required for posting.
def _x_request(self, method, route, params=None, json=None, user_auth=False):
    host = X_HOST
    headers = {"User-Agent": self.user_agent}
    auth = None
    if user_auth:
        auth = OAuth1UserHandler(
            self.consumer_key, self.consumer_secret,
            self.access_token, self.access_token_secret
        )
        auth = auth.apply_auth()
    else:
        headers["Authorization"] = f"Bearer {self.bearer_token}"

    with self.session.request(
        method, host + route, params=params, json=json,
        headers=headers, auth=auth
    ) as response:
        if response.status_code == 401:
            raise tweepy.errors.Unauthorized(response)
        if response.status_code == 403:
            raise tweepy.errors.Forbidden(response)
        if response.status_code == 429:
            raise tweepy.errors.TooManyRequests(response)
        if response.status_code >= 500:
            raise tweepy.errors.TwitterServerError(response)
        if not 200 <= response.status_code < 300:
            raise tweepy.errors.HTTPException(response)
        return response

tweepy.client.BaseClient.request = _x_request


def upload_to_twitter(video_path, caption):
    """Upload video to X using API v1.1 (media) + v2 (post) on api.x.com."""

    api_key = os.getenv('TWITTER_API_KEY', '').strip()
    api_secret = os.getenv('TWITTER_API_SECRET', '').strip()
    access_token = os.getenv('TWITTER_ACCESS_TOKEN', '').strip()
    access_secret = os.getenv('TWITTER_ACCESS_SECRET', '').strip()

    if not all([api_key, api_secret, access_token, access_secret]):
        raise ValueError("[twitter] Missing Twitter credentials in .env")

    print("[twitter] [info] Uploading to X...")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"[twitter] [error] Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[twitter] Video size: {file_size_mb:.2f} MB")

    try:
        # 1. Authenticate V1 (Media Upload)
        print("[twitter] Authenticating with API v1.1 (media upload)...")
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api_v1 = tweepy.API(auth)

        # 2. Authenticate V2 (Posting) on the current X host (api.x.com)
        print("[twitter] Authenticating with API v2 on api.x.com (posting)...")
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        # 3. Upload Video (Chunked)
        print("[twitter] Uploading video (chunked)...")
        media = api_v1.media_upload(
            filename=str(video_path_obj),
            media_category='tweet_video',
            chunked=True
        )
        print(f"[twitter] [success] Video uploaded! Media ID: {media.media_id}")

        # 4. Wait for video processing to complete before attaching
        print("[twitter] Waiting for video processing to complete...")
        deadline = time.time() + 300
        while time.time() < deadline:
            status = api_v1.get_media_upload_status(media.media_id)
            pinfo = getattr(status, 'processing_info', None)
            if not pinfo:
                break
            state = pinfo.get('state')
            if state == 'succeeded':
                print("[twitter] Video processing succeeded.")
                break
            if state == 'failed':
                raise RuntimeError(f"[twitter] [error] Media processing failed: {pinfo}")
            check_after = pinfo.get('check_after_secs', 5)
            time.sleep(check_after)
        else:
            raise RuntimeError("[twitter] [error] Media processing timed out")

        # 5. Post Tweet (text + video)
        print("[twitter] Posting tweet...")
        tweet_text = caption[:280]

        response = client.create_tweet(
            text=tweet_text,
            media_ids=[media.media_id]
        )

        tweet_id = response.data['id']
        tweet_url = f"https://x.com/i/web/status/{tweet_id}"

        print(f"[twitter] [success] Posted to X!")
        print(f"[twitter] URL: {tweet_url}")

        return {'id': tweet_id, 'url': tweet_url, 'platform': 'twitter'}

    except tweepy.errors.Unauthorized as e:
        print(f"[twitter] [error] Authentication failed: {e}")
        raise
    except tweepy.errors.Forbidden as e:
        print(f"[twitter] [error] Permission denied: {e}")
        raise
    except tweepy.errors.TooManyRequests as e:
        print(f"[twitter] [error] Rate limit exceeded: {e}")
        raise
    except Exception as e:
        print(f"[twitter] [error] Unexpected error: {e}")
        raise


if __name__ == '__main__':
    # Test block
    video_file = Path('final_video.mp4')
    if video_file.exists():
        upload_to_twitter(video_file, "Test Upload #XAPI")
    else:
        print("[twitter] No test video found.")
