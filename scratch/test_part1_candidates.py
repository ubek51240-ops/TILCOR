import json
import re
from collections import Counter, defaultdict
from word_family import uz_norm, match_uzbek_word_family, match_english_word_family

# Load corpus
corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))
dictionary = json.load(open('data/dictionary.json', encoding='utf-8'))

print(f"Corpus: {len(corpus)}, Dictionary: {len(dictionary)}")
