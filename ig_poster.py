import os
import json
import requests
from datetime import datetime, timezone, timedelta

# 設定
SCHEDULE_FILE = "schedule.json"
IG_ACCESS_TOKEN = os.environ.get('IG_ACCESS_TOKEN')
IG_USER_ID = os.environ.get('IG_USER_ID')

# JST(日本時間)の現在時刻
JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)

def post_to_instagram_reels(video_url, caption):
    print(f"📸 Instagramリールへの投稿処理を開始します... URL: {video_url}")
    upload_url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    payload = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'access_token': IG_ACCESS_TOKEN
    }
    try:
        res = requests.post(upload_url, data=payload)
        result = res.json()
        if 'id' not in result:
            print("❌ Instagram動画送信エラー:", result)
            return False
        
        creation_id = result['id']
        print(f"✅ Metaサーバーが動画を受付しました (ID: {creation_id})")

        import time
        status_url = f"https://graph.facebook.com/v20.0/{creation_id}"
        print("⏳ Instagram側の動画処理を待機中 (約30秒〜)...")
        for _ in range(30):
            time.sleep(10)
            status_res = requests.get(status_url, params={'fields': 'status_code', 'access_token': IG_ACCESS_TOKEN})
            status = status_res.json().get('status_code')
            if status == 'FINISHED':
                print("✅ Instagram側の動画準備が完了しました！")
                break
            elif status == 'ERROR':
                print("❌ Instagram側で動画処理エラーが発生しました。")
                return False

        publish_url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
        publish_payload = {'creation_id': creation_id, 'access_token': IG_ACCESS_TOKEN}
        publish_res = requests.post(publish_url, data=publish_payload)
        
        if 'id' in publish_res.json():
            print("🎉 Instagramリールの投稿が完全に成功しました！")
            return True
        else:
            print("❌ Instagram公開エラー:", publish_res.json())
            return False
    except Exception as e:
        print(f"❌ Instagram投稿中にシステムエラー: {e}")
        return False

def main():
    if not os.path.exists(SCHEDULE_FILE):
        print("スケジュールファイルがありません。")
        return
        
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
        try:
            schedule = json.load(f)
        except json.JSONDecodeError:
            schedule = []
            
    updated = False
    
    for item in schedule:
        if item.get('status') != 'pending':
            continue # すでに投稿済みのものはスキップ
            
        post_time_str = item.get('post_time')
        # 日本時間として読み込む
        post_time = datetime.strptime(post_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=JST)
        
        if now >= post_time:
            print(f"⏰ 投稿時間です！ タイトル: {item.get('caption')}")
            success = post_to_instagram_reels(item['video_url'], item['caption'])
            
            if success:
                item['status'] = 'posted' # 投稿済みに変更
                updated = True
            else:
                print("⚠️ 投稿に失敗しました。次回再試行します。")
                
    if updated:
        # スケジュール表を上書き保存
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=4)
        print("📝 スケジュール表を「投稿済み」に更新しました。")

if __name__ == "__main__":
    main()
