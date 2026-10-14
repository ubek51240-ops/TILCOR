import os
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("189.74.100.111", username=os.environ.get('TILCOR_VPS_USER', 'root'), password=os.environ['TILCOR_VPS_PASSWORD'], timeout=15)

print("[*] Installing nltk on VPS...")
stdin, stdout, stderr = client.exec_command("pip3 install nltk || apt-get update && apt-get install -y python3-nltk")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("[*] Downloading wordnet corpora...")
stdin, stdout, stderr = client.exec_command("python3 -c 'import nltk; nltk.download(\"wordnet\"); nltk.download(\"omw-1.4\")'")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("[*] Verifying nltk version on VPS...")
stdin, stdout, stderr = client.exec_command("python3 -c 'import nltk; from nltk.stem import WordNetLemmatizer, PorterStemmer; print(\"NLTK:\", nltk.__version__)'")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

client.close()
