from flask import Flask, render_template, request
import json
import re
import urllib.parse
import requests

app = Flask(__name__)

@app.route('/home')
def home():
    return '''
        <h1>YouTube URL解析ツール</h1>
        <form method="post" action="/extract">
            <label for="youtube_url">YouTubeのURLを入力:</label><br>
            <input type="text" id="youtube_url" name="youtube_url" size="50" placeholder="https://www.youtube.com/watch?v=example"><br><br>
            <button type="submit">解析</button>
        </form>
    '''

@app.route('/extract', methods=['POST'])
def extract():
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

        # デバッグ用にレスポンス全体を表示
        yt_initial_data = json.loads(match.group(1))
        return f"<h2>ytInitialPlayerResponse の内容:</h2><pre>{json.dumps(yt_initial_data, indent=4)}</pre>"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"



if __name__ == '__main__':
    app.run(debug=True)
