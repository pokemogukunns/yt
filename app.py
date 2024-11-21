from flask import Flask, render_template, request, redirect, url_for, session
import json
import re
import urllib.parse
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle

# Flaskのインスタンス作成
app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッションを保持するために秘密鍵が必要
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ローカルでの認証には必要

# YouTube APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# GoogleのクライアントIDとクライアントシークレットが含まれるJSONファイル
CLIENT_SECRET_FILE = 'YOUR_CLIENT_SECRET_FILE.json'
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# トークンファイルの保存場所
CREDENTIALS_FILE = 'credentials.pickle'


# OAuth認証フロー
def get_credentials():
    credentials = None
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


# YouTube APIにアクセスする関数
def get_youtube_data():
    credentials = get_credentials()
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    request = youtube.channels().list(part="snippet", mine=True)
    response = request.execute()
    return response


# ホームページ（ログインページ）
@app.route('/home')
def home():
    credentials = get_credentials()
    if credentials:
        return redirect(url_for('extract'))
    return '''
        <h1>YouTube URL解析ツール</h1>
        <a href="/login">Googleでログイン</a>
    '''


# Googleでの認証
@app.route('/login')
def login():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)


# Google OAuth認証後のリダイレクトURL
@app.route('/oauth2callback')
def oauth2callback():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    with open(CREDENTIALS_FILE, 'wb') as token:
        pickle.dump(credentials, token)

    return redirect(url_for('extract'))


# YouTubeデータを取得（解析）
@app.route('/extract', methods=['GET', 'POST'])
def extract():
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        if not youtube_url:
            return "URLを入力してください"

        try:
            response = requests.get(youtube_url)
            if response.status_code != 200:
                return f"エラー: YouTubeページの取得に失敗しました (ステータスコード: {response.status_code})"

            html_content = response.text
            match = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', html_content)
            if not match:
                return "ytInitialPlayerResponseが見つかりませんでした"

            yt_initial_data = json.loads(match.group(1))
            return f"<h2>ytInitialPlayerResponse の内容:</h2><pre>{json.dumps(yt_initial_data, indent=4)}</pre>"
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"
    return '''
        <h1>YouTube URL解析ツール</h1>
        <form method="post">
            <label for="youtube_url">YouTubeのURLを入力:</label><br>
            <input type="text" id="youtube_url" name="youtube_url" size="50" placeholder="https://www.youtube.com/watch?v=example"><br><br>
            <button type="submit">解析</button>
        </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
