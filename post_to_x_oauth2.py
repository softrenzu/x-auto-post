#!/usr/bin/env python3
import json
import os
import time
import base64
import requests

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "x_oauth2_tokens.json")
CLIENT_ID = os.environ["X_CLIENT_ID"]
CLIENT_SECRET = os.environ["X_CLIENT_SECRET"]

def load_tokens():
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

def refresh_token_if_needed(tokens):
    # 超ざっくり：expires_in が 2時間程度なので、期限近そうならリフレッシュ
    # （厳密にやるなら expires_at を保存する）
    # ここでは常にリフレッシュしてもOKなくらいの頻度なので、単純化
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        return tokens  # そもそも無いなら何もしない

    token_url = "https://api.x.com/2/oauth2/token"
    basic = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii")
    ).decode("ascii")

    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Basic {basic}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    r = requests.post(token_url, headers=headers, data=data)
    if r.status_code != 200:
        print("⚠ トークンリフレッシュ失敗:", r.status_code, r.text)
        return tokens

    new_tokens = r.json()
    save_tokens(new_tokens)
    return new_tokens

def main():
    tokens = load_tokens()
    tokens = refresh_token_if_needed(tokens)
    access_token = tokens["access_token"]

    tweet_text = "OAuth2 + PKCE からのテスト投稿です（さくらVPS）"

    url = "https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": tweet_text}

    r = requests.post(url, headers=headers, json=payload)
    print(r.status_code)
    print(r.text)

if __name__ == "__main__":
    main()

