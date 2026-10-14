#!/usr/bin/env python3
"""
scripts/telegram_bot_listener.py - Telegram Bot Listener for TILCOR
Receives prompts from admin 7546610030 via bot <BOT_TOKEN olib tashlandi>,
downloads any attached files, logs the prompt, sends acknowledgment, and exits so
the agent can execute the task and report back.
"""
import os
import sys
import time
import json
import urllib.request
import urllib.parse

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BOT_TOKEN = os.environ.get('TILCOR_BOT_TOKEN', '')
ADMIN_IDS = {7546610030, 946220712}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING_DIR = os.path.join(BASE_DIR, "staging")
DOWNLOADS_DIR = r"C:\Users\user\Downloads\Telegram Desktop"

os.makedirs(STAGING_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

OFFSET_FILE = os.path.join(STAGING_DIR, "tg_last_offset.txt")
PROMPT_FILE = os.path.join(STAGING_DIR, "telegram_prompt.json")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # Split if text > 4000
    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': chunk
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                pass
        except Exception as e:
            print(f"[!] Error sending message to {chat_id}: {e}")

def send_document(chat_id, file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    import subprocess
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-F", f"chat_id={chat_id}",
        "-F", f"document=@{file_path}",
        "-F", f"caption={caption}"
    ]
    subprocess.run(cmd, capture_output=True)

def download_file(file_id, dest_filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    
    file_path = res['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    dest_path = os.path.join(DOWNLOADS_DIR, dest_filename)
    urllib.request.urlretrieve(download_url, dest_path)
    print(f"[*] Fayl yuklab olindi: {dest_path}")
    return dest_path

def get_last_offset():
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_last_offset(offset):
    with open(OFFSET_FILE, 'w') as f:
        f.write(str(offset))

def listen_for_prompt(timeout_seconds=300):
    print(f"[*] Telegram bot tinglanmoqda... (Ruxsat etilgan adminlar: {ADMIN_IDS})")
    last_offset = get_last_offset()
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_offset}&timeout=20"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"[!] Xatolik: {e}")
            time.sleep(2)
            continue
            
        for update in data.get('result', []):
            update_id = update['update_id']
            last_offset = update_id + 1
            save_last_offset(last_offset)
            
            msg = update.get('message') or update.get('edited_message')
            if not msg:
                continue
                
            sender = msg.get('from', {})
            sender_id = sender.get('id')
            
            if sender_id not in ADMIN_IDS:
                print(f"[!] Begona foydalanuvchi ({sender_id}). E'tibor berilmadi.")
                continue
                
            text = msg.get('text', '')
            caption = msg.get('caption', '')
            doc = msg.get('document')

            if text.strip() == '/start':
                print(f"[+] Admin {sender_id} botni ishga tushirdi (/start).")
                send_message(sender_id, "Assalomu alaykum! TILCOR tizimi boshqaruv boti bilan aloqa o‘rnatildi. Siz muvaffaqiyatli ulandingiz! Endi istalgan topshiriq / prompt yoki faylni yuborishingiz mumkin.")
                continue
                
            prompt_content = text or caption or ""
            downloaded_doc_path = None
            
            if doc:
                f_id = doc.get('file_id')
                f_name = doc.get('file_name', 'attachment.dat')
                downloaded_doc_path = download_file(f_id, f_name)
                # If markdown or text file, read content
                if f_name.endswith(('.md', '.txt', '.json', '.py')):
                    try:
                        with open(downloaded_doc_path, 'r', encoding='utf-8') as df:
                            doc_text = df.read()
                        prompt_content = f"{prompt_content}\n\n[FILE: {f_name}]\n{doc_text}".strip()
                    except Exception as e:
                        print(f"[!] Fayl o'qishda xatolik: {e}")
                        prompt_content = f"{prompt_content}\n[Fayl saqlandi: {downloaded_doc_path}]".strip()
            
            if prompt_content or downloaded_doc_path:
                print("\n" + "="*60)
                print(f"[+] Yangi prompt qabul qilindi (Admin: {sender_id}):")
                print(prompt_content[:300] + ("..." if len(prompt_content) > 300 else ""))
                print("="*60)
                
                # Acknowledge to admin
                ack_msg = "✅ Topshiriq qabul qilindi. Jarayon boshlandi..."
                send_message(sender_id, ack_msg)
                
                # Save prompt data
                prompt_data = {
                    "timestamp": time.time(),
                    "sender_id": sender_id,
                    "sender_name": f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip(),
                    "prompt_text": prompt_content,
                    "file_path": downloaded_doc_path,
                    "update_id": update_id
                }
                with open(PROMPT_FILE, 'w', encoding='utf-8') as pf:
                    json.dump(prompt_data, pf, ensure_ascii=False, indent=2)
                    
                return prompt_data

                
        time.sleep(1)
        
    print("[*] Kutish vaqti tugadi (yangi xabar yo'q).")
    return None

if __name__ == '__main__':
    prompt = listen_for_prompt(timeout_seconds=int(sys.argv[1]) if len(sys.argv) > 1 else 120)
    if prompt:
        sys.exit(0)
    else:
        sys.exit(1)
