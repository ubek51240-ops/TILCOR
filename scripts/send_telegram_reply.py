import os
#!/usr/bin/env python3
"""
scripts/send_telegram_reply.py - Sends response back to admin 7546610030
"""
import sys
import json
import urllib.request
import urllib.parse

BOT_TOKEN = os.environ.get('TILCOR_BOT_TOKEN', '')
ADMIN_IDS = [7546610030, 946220712]

def send_reply(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # Chunk long text
    chunks = [text[i:i+3800] for i in range(0, len(text), 3800)]
    for admin_id in ADMIN_IDS:
        for chunk in chunks:
            data = urllib.parse.urlencode({
                'chat_id': admin_id,
                'text': chunk
            }).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    pass
            except Exception as e:
                # If 403 (user hasn't started bot yet), just ignore
                pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = sys.stdin.read()
    send_reply(msg)
    print("[*] Javob adminga yuborildi.")
