import os
import time
import requests

# GitHubに登録した鍵を読み込む
ACCESS_TOKEN = os.environ['IG_ACCESS_TOKEN']
USER_ID = os.environ['IG_USER_ID']

def post_instagram_reel(video_url, caption):
    print("1. Metaのサーバーに動画を送信中...")
    upload_url = f"https://graph.facebook.com/v20.0/{USER_ID}/media"
    payload = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    }
    response = requests.post(upload_url, data=payload)
    result = response.json()
    
    if 'id' not in result:
        print("❌ エラー発生:", result)
        return
        
    creation_id = result['id']
    print(f"✅ 受付完了 (ID: {creation_id})")

    # 処理完了まで少し待機
    print("2. 処理完了を待機中...")
    status_url = f"https://graph.facebook.com/v20.0/{creation_id}"
    while True:
        time.sleep(10)
        status_res = requests.get(status_url, params={'fields': 'status_code', 'access_token': ACCESS_TOKEN})
        status = status_res.json().get('status_code')
        if status == 'FINISHED':
            print("✅ 準備OK！")
            break
        elif status == 'ERROR':
            print("❌ エラーが発生しました。")
            return

    # 公開実行
    print("3. Instagramへ公開中...")
    publish_url = f"https://graph.facebook.com/v20.0/{USER_ID}/media_publish"
    publish_payload = {
        'creation_id': creation_id,
        'access_token': ACCESS_TOKEN
    }
    publish_res = requests.post(publish_url, data=publish_payload)
    
    if 'id' in publish_res.json():
        print("🎉 投稿成功しました！")
    else:
        print("❌ 公開失敗:", publish_res.json())

if __name__ == "__main__":
    # テスト用の動画URLとキャプション
    TEST_VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"
    CAPTION = "自動投稿のテストです🚀"
    post_instagram_reel(TEST_VIDEO_URL, CAPTION)
