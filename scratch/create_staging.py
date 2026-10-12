import os, shutil

staging_dir = 'staging'
os.makedirs(staging_dir, exist_ok=True)

files_to_copy = [
    'index.html', 'server.py', 'app_streamlit.py', 'README.md',
    'extract_corpus.py', 'extract_80k_dict.py', 'test_extract.py',
    'extract_and_translate_collocations.py', 'merge_literary_collocs.py',
    'export_collocations_list.py', 'enrich_corpus_and_collocations.py',
    'export_to_sqlite.py'
]

dirs_to_copy = ['css', 'js', 'data', 'docs']

for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy2(f, os.path.join(staging_dir, f))

for d in dirs_to_copy:
    dst_d = os.path.join(staging_dir, d)
    if os.path.exists(dst_d):
        shutil.rmtree(dst_d)
    shutil.copytree(d, dst_d)

print(f"STAGING copy successfully created at '{staging_dir}'.")
