import requests
from bs4 import BeautifulSoup

# 定数
HOYOLAB_URL = "https://www.hoyolab.com/accountCenter/postList?id=178846223"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1358594210705440890/8jk0dE9FaGBk4o0kAFr-ce4IA6jswPtVt34OZ0dVoirApqlnfUZqEwsX1bkNinYF-T8r"  # ←実際のURLに置き換えてね

headers = {
    "User-Agent": "Mozilla/5.0"
}

def find_target_post():
    response = requests.get(HOYOLAB_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for a_tag in soup.find_all("a", href=True):
        text = a_tag.get_text()
        if "崩壊スターレイル" in text and "シリアルコード" in text:
            return "https://www.hoyolab.com" + a_tag["href"]
    return None

def extract_auto_fill_link(post_url):
    response = requests.get(post_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for a_tag in soup.find_all("a", href=True):
        if "自動入力リンク" in a_tag.get_text():
            return a_tag["href"]
    return None

def send_to_discord(link):
    data = {"content": f"新しいコード入力リンクが見つかりました！\n{link}"}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    response.raise_for_status()

def main():
    post_url = find_target_post()
    if not post_url:
        print("対象の投稿が見つかりませんでした。")
        return
    link = extract_auto_fill_link(post_url)
    if not link:
        print("自動入力リンクが見つかりませんでした。")
        return
    send_to_discord(link)
    print("リンクを送信しました:", link)

if __name__ == "__main__":
    main()
