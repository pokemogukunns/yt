from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/home')
def home():
    return '''
        <h1>ストリームURL取得ツール</h1>
        <form method="post" action="/get_stream">
            <label for="youtube_url">YouTubeのURLを入力:</label><br>
            <input type="text" id="youtube_url" name="youtube_url" size="50" placeholder="https://www.youtube.com/watch?v=example"><br><br>
            <button type="submit">ストリームURL取得</button>
        </form>
    '''

@app.route('/get_stream', methods=['POST'])
def get_stream():
    youtube_url = request.form.get('youtube_url')

    if not youtube_url:
        return "URLを入力してください"

    try:
        # yt-dlpを使用してストリームURLを解析
        ydl_opts = {
            'quiet': True,
            'format': 'best',  # 必要に応じて品質を選択
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)

        # 各フォーマットのストリームURLを収集
        formats = info_dict.get('formats', [])
        stream_urls = [
            {
                'format': f.get('format_note', 'N/A'),
                'url': f.get('url')
            }
            for f in formats if f.get('url')
        ]

        # 結果をJSON形式で返す
        return jsonify({
            'title': info_dict.get('title', 'タイトル不明'),
            'stream_urls': stream_urls
        })

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
