import os
import shutil
import datetime

timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = os.path.join('backups', f'backup_step03_{timestamp}')
os.makedirs(backup_dir, exist_ok=True)

items = ['index.html', 'server.py', 'search_engine.py', 'word_family.py', 'PROJECT_CONTEXT.md', 'METHODS.md', 'js', 'data', 'css']
for item in items:
    if os.path.exists(item):
        dst = os.path.join(backup_dir, item)
        if os.path.isdir(item):
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)

print(f"[*] Backup created successfully at: {backup_dir}")
