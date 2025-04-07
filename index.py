import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

# PlaywrightでHTMLを取得する関数
def fetch_rendered_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)  # JavaScriptが完全に描画されるまで待つ
        html = page.content()  # ページの完全なHTMLを取得
        browser.close()
        return html

# 送信済みURLのリストを読み込む関数
def load_sent_urls():
    try:
        with open('sent_urls.txt', 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# 送信済みURLのリストを更新する関数
def update_sent_urls(new_urls):
    with open('sent_urls.txt', 'a') as file:
        for url in new_urls:
            file.write(url + "\n")

# 対象の投稿URLを探す関数（Playwrightを使用）
def find_target_posts():
    HOYOLAB_URL = "https://www.hoyolab.com/accountCenter/postList?id=178846223"
    
    # PlaywrightでページのHTMLを取得
    html = fetch_rendered_html(HOYOLAB_URL)
    
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html, 'html.parser')
    
    # 文字列「崩壊スターレイル」と「シリアルコード」を含む投稿を探す
    pattern = re.compile(r"(崩壊)?スターレイル.*コード")
    
    target_urls = []
    
    # 投稿の中の全てのテキストを探してチェック
    for text in soup.find_all(string=True):
        if pattern.search(text):
            parent_a = text.find_parent("a")
            if parent_a and parent_a.has_attr("href"):
                post_url = "https://www.hoyolab.com" + parent_a["href"]
                target_urls.append(post_url)
    
    return target_urls

# コンテンツから「自動入力リンク」を含むURLを抽出する関数
def find_autofill_links(post_url):
    # PlaywrightでコンテンツのHTMLを取得
    html = fetch_rendered_html(post_url)
    
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html, 'html.parser')
    
    # 「自動入力リンク」を含むリンクを探す
    autofill_links = []
    for a_tag in soup.find_all('a', string=re.compile("自動入力リンク")):
        if a_tag.has_attr("href"):
            autofill_links.append(a_tag["href"])
    
    return autofill_links

# Discordへの通知を送信する関数
def send_to_discord(webhook_url, message):
    data = {
        "content": message
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("通知が送信されました。")
    else:
        print(f"通知送信に失敗しました。ステータスコード: {response.status_code}")

# 実行するメイン関数
def main():
    # Webhook URL（DiscordのWebhook URLを設定）
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1358594210705440890/8jk0dE9FaGBk4o0kAFr-ce4IA6jswPtVt34OZ0dVoirApqlnfUZqEwsX1bkNinYF-T8r"
    
    # 送信済みURLを読み込む
    sent_urls = load_sent_urls()
    
    # 対象の投稿URLを取得（すべての該当URLを取得）
    target_urls = find_target_posts()
    
    # 送信する新しいURLをフィルタリング（過去に送信したものを除外）
    all_autofill_links = []
    
    for post_url in target_urls:
        # 各投稿の詳細ページから「自動入力リンク」を取得
        autofill_links = find_autofill_links(post_url)
        
        # 送信済みURLにない「自動入力リンク」だけをリストに追加
        new_autofill_links = [link for link in autofill_links if link not in sent_urls]
        all_autofill_links.extend(new_autofill_links)
    
    # 重複を排除するため、セットを使用してリンクを一意にする
    unique_autofill_links = list(set(all_autofill_links))
    
    if unique_autofill_links:
        # 自動入力リンクがあれば、改行区切りで通知
        message = "\n".join(unique_autofill_links)
        send_to_discord(DISCORD_WEBHOOK_URL, f"# <:icon:1315525679969992705> シリアルコード<:icon:1315525679969992705>\n{message}")
        
        # 送信済みURLリストを更新（「自動入力リンク」のURLを保存）
        update_sent_urls(unique_autofill_links)
    else:
        print("新しい自動入力リンクは見つかりませんでした。")

# スクリプトを実行
if __name__ == "__main__":
    main()
