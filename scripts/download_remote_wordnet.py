import os
import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('189.74.100.111', username=os.environ.get('TILCOR_VPS_USER', 'root'), password=os.environ['TILCOR_VPS_PASSWORD'], timeout=15)

stdin, stdout, stderr = client.exec_command("python3 -c \"import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')\"")
print("Download:", stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = client.exec_command("python3 -c \"import nltk; from nltk.stem import WordNetLemmatizer; lem = WordNetLemmatizer(); print('NLTK OK:', nltk.__version__, lem.lemmatize('hearts'))\"")
print("Verification:", stdout.read().decode('utf-8', errors='replace'))

client.close()
