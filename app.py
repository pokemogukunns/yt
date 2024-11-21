from flask import Flask, request, render_template_string
import requests
import re
import json

app = Flask(__name__)

# ホームページ: URL入力フォームを表示
@app.route('/home', methods=['GET'])
def home():
    return '''
        <h1>YouTube URL解析ツール</h1>
        <form method="post" action="/extract">
            <label for="youtube_url">YouTubeのURLを入力:</label><br>
            <input type="text" id="youtube_url" name="youtube_url" size="50" placeholder="https://www.youtube.com/watch?v=example"><br><br>
            <button type="submit">解析</button>
        </form>
    '''

# YouTube URLを解析して結果を表示
@app.route('/extract', methods=['POST'])
def extract():
    youtube_url = request.form.get('youtube_url')  # フォームからURLを取得
    
    if not youtube_url:
        return "URLを入力してください"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # YouTubeページを取得
        response = requests.get(youtube_url, headers=headers)
        if response.status_code != 200:
            return f"エラー: YouTubeページの取得に失敗しました (ステータスコード: {response.status_code})"
        
        # HTMLから ytInitialPlayerResponse を抽出
        html_content = response.text
        match = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', html_content)
        if not match:
            return "ytInitialPlayerResponseが見つかりませんでした"

        # JSONデータを整形して表示
        yt_initial_data = json.loads(match.group(1))
        return f"<h2>解析結果:</h2><pre>{json.dumps(yt_initial_data, indent=4)}</pre>"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
