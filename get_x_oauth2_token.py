#!/usr/bin/env python3
import os
import base64
import hashlib
import secrets
import urllib.parse
import requests
import json

CLIENT_ID = os.environ["X_CLIENT_ID"]
CLIENT_SECRET = os.environ["X_CLIENT_SECRET"]
REDIRECT_URI = os.environ["X_REDIRECT_URI"]

# ユーザーに付与してもらう権限
SCOPES = "tweet.read tweet.write users.read offline.access"

def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

def main():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": "staytokyo_state",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = "https://twitter.com/i/oauth2/authorize?" + urllib.parse.urlencode(params)

    print("1) このURLをブラウザで開いて、X にログイン・許可してください:\n")
    print(auth_url)
    print("\n2) 許可後にブラウザが遷移した先の URL 全体をコピーして、ここに貼って Enter:")
    redirect_url = input("> ").strip()

    # URL から code を取り出す
    parsed = urllib.parse.urlparse(redirect_url)
    query = urllib.parse.parse_qs(parsed.query)
    code = query.get("code", [None])[0]
    state = query.get("state", [None])[0]

    if not code:
        raise SystemExit("code がURLに含まれていません。貼り付けたURLを確認してください。")
    if state != "staytokyo_state":
        raise SystemExit("state が一致しません。セキュリティのため中止します。")

    # 認可コードをアクセストークンに交換
    token_url = "https://api.x.com/2/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # client_id:client_secret を Base64
    basic = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii")
    ).decode("ascii")
    headers["Authorization"] = f"Basic {basic}"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    r = requests.post(token_url, headers=headers, data=data)
    print("Status:", r.status_code)
    print("Response:", r.text)

    r.raise_for_status()
    tokens = r.json()
    # access_token / refresh_token / expires_in などが返る
    with open("x_oauth2_tokens.json", "w") as f:
        json.dump(tokens, f, indent=2)

    print("\n✅ x_oauth2_tokens.json に保存しました。")

if __name__ == "__main__":
    main()

