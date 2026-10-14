import os
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("189.74.100.111", username=os.environ.get('TILCOR_VPS_USER', 'root'), password=os.environ['TILCOR_VPS_PASSWORD'], timeout=15)

# Check python version and nltk
stdin, stdout, stderr = client.exec_command("python3 -c 'import nltk; print(nltk.__version__)'")
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print("NLTK version:", out)
if err:
    print("NLTK err:", err)

# Check wordnet data
stdin, stdout, stderr = client.exec_command("python3 -c 'import nltk; nltk.download(\"wordnet\"); nltk.download(\"omw-1.4\")'")
print("Download:", stdout.read().decode('utf-8'))

client.close()
