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

        # ytInitialPlayerResponseを抽出
        match = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', html_content)
        if not match:
            return "ytInitialPlayerResponseが見つかりませんでした"

        yt_initial_data = json.loads(match.group(1))

        # 全フォーマットを取得して表示
        streaming_data = yt_initial_data.get('streamingData', {})
        formats = streaming_data.get('formats', []) + streaming_data.get('adaptiveFormats', [])

        if not formats:
            return "利用可能なフォーマットが見つかりませんでした"

        # 利用可能なすべてのURLを表示
        all_urls = []
        for fmt in formats:
            itag = fmt.get('itag')
            url = fmt.get('url', "URLがありません")
            all_urls.append(f"itag: {itag} -> URL: {url}")

        return f"<h2>利用可能なフォーマットとURL:</h2><pre>{'<br>'.join(all_urls)}</pre>"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
