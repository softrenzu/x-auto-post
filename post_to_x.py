#!/usr/bin/env python3
import os
import datetime
import requests
from requests_oauthlib import OAuth1

# ====== 設定 ======
WP_BASE_URL = "https://staytokyo.xyz"  # あなたのWPサイト
WP_API_URL = f"{WP_BASE_URL}/wp-json/wp/v2/posts"

# ====== X 認証 ======
auth = OAuth1(
    os.environ["X_API_KEY"],
    os.environ["X_API_SECRET"],
    os.environ["X_ACCESS_TOKEN"],
    os.environ["X_ACCESS_TOKEN_SECRET"],
    signature_type="AUTH_HEADER",
)


def get_latest_post_text() -> str:
    """WordPressの最新記事1件を取得してツイート文にする"""
    r = requests.get(WP_API_URL, params={"per_page": 1})
    r.raise_for_status()
    posts = r.json()
    if not posts:
        return "（お知らせ）まだ公開済みの記事がありません。"

    post = posts[0]
    title = post.get("title", {}).get("rendered", "").strip()
    link = post.get("link", "").strip()

    if not title or not link:
        return "新しい記事を公開しました。"

    base = f"[WP最新記事] {title} {link}"

    # 280文字制限を超えないように調整
    if len(base) <= 260:
        return base

    max_title_len = 260 - len("[WP最新記事] ") - len(link) - 1
    short_title = title[:max_title_len] + "…"
    return f"[最新記事] {short_title} {link}"


def main():
    tweet_text = get_latest_post_text()

    # 重複禁止のため、テスト用にタイムスタンプを末尾に付ける
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tweet_text = f"{tweet_text} ({now})"

    print("===== 実際に投稿するテキスト =====")
    print(tweet_text)
    print("================================")

    url = "https://api.x.com/2/tweets"
    payload = {"text": tweet_text}
    r = requests.post(url, json=payload, auth=auth)

    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    main()

