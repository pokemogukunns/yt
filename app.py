from flask import Flask, render_template, request
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
        # YouTubeのHTMLを取得
        response = requests.get(youtube_url)
        if response.status_code != 200:
            return f"エラー: YouTubeページの取得に失敗しました (ステータスコード: {response.status_code})"

        html_content = response.text

        # "url"部分を抽出
        url_match = re.search(r'"itag":136,"url":"(https://[^"]+)"', html_content)
        if not url_match:
            return "URLが見つかりませんでした"

        raw_url = url_match.group(1)

        # エスケープ文字 (\u0026 など) をデコード
        decoded_url = raw_url.encode('utf-8').decode('unicode_escape')

        # 必要ならクエリ部分をデコード
        full_url = urllib.parse.unquote(decoded_url)

        return f"<h2>抽出されたURL:</h2><p><a href='{full_url}' target='_blank'>{full_url}</a></p>"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
