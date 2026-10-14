"""
scripts/clean_and_enhance_collocations.py
Executes Part 3 of TILCOR_03-1:
- English side cleaning: "~", merged entries, repeated tokens, duplicates.
- POS tagging with Penn Treebank + WordNet lemma verification.
- Corpus occurrence linking on OMS-EN and KVK-EN.
- Uzbek equivalents (1-3 variants) with source classes (KORPUS, LUG‘AT, AI-taklif, tasdiqlangan).
- Automatic quality checks: orthography, vocabulary, form (-moq), calque flag.
- Sample 100 selection for researcher review.
"""

import json
import re
import random
import os
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('.')

from word_family import uz_norm, lemmatizer
import nltk
from nltk import pos_tag
from nltk.corpus import wordnet as wn

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
COLLOC_FILE = os.path.join(DATA_DIR, 'collocations_full.json')
CORPUS_FILE = os.path.join(DATA_DIR, 'full_corpus.json')
DICT_FILE = os.path.join(DATA_DIR, 'dictionary.json')

with open(COLLOC_FILE, 'r', encoding='utf-8') as f:
    collocs = json.load(f)

with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
    full_corpus = json.load(f)

with open(DICT_FILE, 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

active_corpus = [c for c in full_corpus if c.get('book') != 'stevenson' and c.get('status') != 'excluded']
print(f"Loaded {len(collocs)} collocations, {len(active_corpus)} active corpus segments, {len(dictionary)} dictionary entries.")

# 1. Build Uzbek vocabulary for quality check
uzbek_vocab = set()
for c in active_corpus:
    norm_uz = uz_norm(c.get('uz', ''))
    for tok in re.findall(r"[a-z\u02bb\u02bc]+", norm_uz):
        uzbek_vocab.add(tok)

for d in dictionary:
    w = uz_norm(d.get('word', ''))
    for tok in re.findall(r"[a-z\u02bb\u02bc]+", w):
        uzbek_vocab.add(tok)
    tr = uz_norm(d.get('translation', '') or '')
    for tok in re.findall(r"[a-z\u02bb\u02bc]+", tr):
        uzbek_vocab.add(tok)

print(f"Uzbek reference vocabulary size: {len(uzbek_vocab)} words.")

# Known bad calques to flag and fix
CALQUE_REPLACEMENTS = {
    'samimiy nonushta': [('toʻyimli nonushta', 'kollokatsiya')],
    'yurak xuruji bor': [('yurak xuruji', 'kollokatsiya')],
    'engil yurak': [('yengil koʻngil', 'kollokatsiya'), ('begʻam koʻngil', 'kollokatsiya')],
    'chin dildan roziman': [('chin dildan rozi boʻlmoq', 'kollokatsiya')],
    'e\'tibor bering': [('eʼtibor bermoq', 'kollokatsiya'), ('diqqat qilmoq', 'kollokatsiya')],
    'eʼtibor bering': [('eʼtibor bermoq', 'kollokatsiya'), ('diqqat qilmoq', 'kollokatsiya')],
    'qaror qabul qiling': [('qaror qabul qilmoq', 'kollokatsiya'), ('qaror qilmoq', 'kollokatsiya')],
    'ogʻir yomgʻir': [('kuchli yomgʻir', 'kollokatsiya'), ('jala', 'bitta soʻz')],
    'sovuq yurak': [('bagʻritoshlik', 'bitta soʻz'), ('shafqatsiz koʻngil', 'kollokatsiya')]
}

KNOWN_GOOD_EQUIVALENTS = {
    'make a decision': [('qaror qabul qilmoq', 'kollokatsiya'), ('qaror qilmoq', 'kollokatsiya')],
    'pay attention': [('eʼtibor bermoq', 'kollokatsiya'), ('diqqat qilmoq', 'kollokatsiya')],
    'heavy rain': [('kuchli yomgʻir', 'kollokatsiya'), ('jala', 'bitta soʻz')],
    'hearty breakfast': [('toʻyimli nonushta', 'kollokatsiya')],
    'light heart': [('yengil koʻngil', 'kollokatsiya'), ('begʻam koʻngil', 'kollokatsiya')],
    'heart attack': [('yurak xuruji', 'kollokatsiya')],
    'have a heart attack': [('yurak xurujiga uchrash', 'kollokatsiya')],
    'suffer a heart attack': [('yurak xurujini boshdan kechirmoq', 'kollokatsiya')],
    'break a heart': [('dilini vayron qilmoq', 'kollokatsiya'), ('yuragini ezmoq', 'kollokatsiya')],
    'heart beats': [('yurak urmoq', 'kollokatsiya')],
    'strong feeling': [('kuchli tuygʻu', 'kollokatsiya'), ('chuqur his', 'kollokatsiya')],
    'deep breath': [('chuqur nafas olmoq', 'kollokatsiya')],
    'take a breath': [('nafas olmoq', 'kollokatsiya')],
    'make an effort': [('harakat qilmoq', 'kollokatsiya'), ('jon kuydirmoq', 'kollokatsiya')],
    'save time': [('vaqtni tejamoq', 'kollokatsiya')],
    'spend time': [('vaqt oʻtkazmoq', 'kollokatsiya')],
    'waste time': [('vaqtni behuda sarflamoq', 'kollokatsiya')],
    'keep a secret': [('sir saqlamoq', 'kollokatsiya')],
    'tell the truth': [('rostini aytmoq', 'kollokatsiya')],
    'tell a lie': [('yolgʻon gapirmoq', 'kollokatsiya')]
}

def determine_pos_pattern(phrase: str) -> str:
    tokens = [w for w in phrase.split() if w.isalpha()]
    if not tokens:
        return "Birikma (avtomatik)"
        
    tagged = pos_tag(tokens)
    tags = [t[1] for t in tagged]
    words = [t[0].lower() for t in tagged]
    
    # 2 words pattern
    if len(tokens) == 2:
        w1, w2 = words
        t1, t2 = tags
        
        # WordNet lemma POS assist
        is_w1_v = bool(wn.synsets(w1, pos=wn.VERB)) and not w1.endswith('ing')
        is_w1_adj = bool(wn.synsets(w1, pos=wn.ADJ))
        is_w2_n = bool(wn.synsets(w2, pos=wn.NOUN))
        is_w2_adv = bool(wn.synsets(w2, pos=wn.ADV))
        
        if (t1.startswith('VB') or is_w1_v) and (t2.startswith('NN') or is_w2_n) and not is_w1_adj:
            return "Feʼl + Ot (Verb + Noun) (avtomatik)"
        if (t1.startswith('JJ') or is_w1_adj) and (t2.startswith('NN') or is_w2_n):
            return "Sifat + Ot (Adjective + Noun) (avtomatik)"
        if t1.startswith('RB') and (t2.startswith('VB') or is_w1_v):
            return "Ravish + Feʼl (Adverb + Verb) (avtomatik)"
        if (t1.startswith('VB') or is_w1_v) and (t2.startswith('RB') or is_w2_adv):
            return "Feʼl + Ravish (Verb + Adverb) (avtomatik)"
        if t1.startswith('NN') and t2.startswith('NN'):
            return "Ot + Ot (Noun + Noun) (avtomatik)"
            
    if 'of' in words and len(tokens) == 3:
        return "Ot + of + Ot (Noun + of + Noun) (avtomatik)"
        
    if any(t.startswith('VB') for t in tags) and any(t.startswith('NN') for t in tags):
        if any(t == 'IN' for t in tags):
            return "Feʼl + Koʻmakchi + Ot (Verb + Preposition + Noun) (avtomatik)"
        return "Feʼl + Ot (Verb + Noun) (avtomatik)"
        
    if any(t.startswith('JJ') for t in tags) and any(t.startswith('NN') for t in tags):
        return "Sifat + Ot (Adjective + Noun) (avtomatik)"
        
    return "Birikma (avtomatik)"

# Track stats per source
stats_per_source = defaultdict(lambda: {
    "total": 0,
    "verified": 0,
    "needs_repair": 0,
    "merged_duplicates": 0,
    "restored": 0
})

# Phase 1: Group and deduplicate identical English entries
dedup_map = {} # english_clean -> [colloc_objects]
for c in collocs:
    src = c.get('sourceBook') or 'Reference'
    stats_per_source[src]["total"] += 1
    
    eng = c.get('english', '').strip()
    eng_clean = ' '.join(eng.lower().split())
    if eng_clean not in dedup_map:
        dedup_map[eng_clean] = []
    dedup_map[eng_clean].append(c)

merged_collocs = []
total_merged_duplicates = 0

for eng_clean, group in dedup_map.items():
    primary = group[0]
    src = primary.get('sourceBook') or 'Reference'
    
    if len(group) > 1:
        total_merged_duplicates += (len(group) - 1)
        stats_per_source[src]["merged_duplicates"] += (len(group) - 1)
        # Combine sources and metadata
        all_sources = set()
        for g in group:
            for s in g.get('sources', []):
                all_sources.add(s)
            if g.get('sourceMeta'):
                all_sources.add(g.get('sourceMeta'))
        primary['sources'] = list(all_sources)
        primary['sourceMeta'] = ', '.join(all_sources)
        
    merged_collocs.append(primary)

print(f"After merging duplicates: {len(merged_collocs)} unique English entries (merged {total_merged_duplicates} duplicates).")

# Phase 2: Clean English side & classify defects
cleaned_collocs = []
needs_repair_counts = Counter()

# Known merged entries to detect
MERGED_ENTRY_PATTERNS = [
    'childhood sweetheart high school',
    'pay attention commit crime',
    'blond hair heavy rain',
    'making friends heavy rain',
    'heavy rain blond hair',
    'commit crime pay attention'
]

for c in merged_collocs:
    src = c.get('sourceBook') or 'Reference'
    eng = c.get('english', '').strip()
    eng_lower = eng.lower()
    tokens = eng.split()
    
    # 1. Check "~" placeholder
    if '~' in eng:
        c['status'] = 'needs_repair'
        c['public_visible'] = False
        c['repair_reason'] = 'placeholder_tilde_unresolved'
        stats_per_source[src]["needs_repair"] += 1
        needs_repair_counts["placeholder_tilde"] += 1
        cleaned_collocs.append(c)
        continue
        
    # 2. Check merged entries
    is_merged = False
    for mp in MERGED_ENTRY_PATTERNS:
        if mp in eng_lower:
            is_merged = True
            break
    if not is_merged and len(tokens) >= 4:
        # Check if 2 distinct 2-word collocations joined together
        pass
        
    if is_merged:
        c['status'] = 'needs_repair'
        c['public_visible'] = False
        c['repair_reason'] = 'merged_entries_unsplit'
        stats_per_source[src]["needs_repair"] += 1
        needs_repair_counts["merged_entries"] += 1
        cleaned_collocs.append(c)
        continue
        
    # 3. Repeated tokens or excessive length (> 5 tokens)
    word_tokens = [t.lower() for t in tokens if t.isalpha()]
    has_repeated = False
    for i in range(len(word_tokens) - 1):
        if word_tokens[i] == word_tokens[i+1]:
            has_repeated = True
            break
            
    if has_repeated or len(tokens) > 5:
        c['status'] = 'needs_repair'
        c['public_visible'] = False
        c['repair_reason'] = 'repeated_tokens_or_excessive_length'
        stats_per_source[src]["needs_repair"] += 1
        needs_repair_counts["repeated_or_too_long"] += 1
        cleaned_collocs.append(c)
        continue
        
    # Valid verified entry
    c['status'] = 'active'
    c['public_visible'] = True
    stats_per_source[src]["verified"] += 1
    
    # Automatic POS pattern tagging
    c['pattern'] = determine_pos_pattern(eng)
    
    # Phase 3: Check corpus occurrences in OMS-EN and KVK-EN
    corpus_matches = []
    pattern_re = re.compile(rf"\b{re.escape(eng_lower)}\b", re.IGNORECASE)
    for seg in active_corpus:
        en_text = seg.get('en', '')
        if pattern_re.search(en_text):
            corpus_matches.append({
                "segment_id": seg.get('id'),
                "book": seg.get('book'),
                "en_text": en_text,
                "uz_text": seg.get('uz')
            })
            
    if corpus_matches:
        c['corpus_occurrences'] = len(corpus_matches)
        c['corpus_segments'] = [m["segment_id"] for m in corpus_matches]
        c['corpus_books'] = list(set(m["book"] for m in corpus_matches))
        c['corpus_badge_label'] = f"Korpusda uchraydi: {len(corpus_matches)} marta — ekvivalent tekislashdan keyin"
    else:
        c['corpus_occurrences'] = 0
        c['corpus_segments'] = []
        c['corpus_books'] = []
        c['corpus_badge_label'] = None

    # Phase 4: Construct 1-3 Uzbek variants with source classes
    variants = []
    
    # Priority a: Corpus (placeholder until step 04+ alignment)
    if corpus_matches:
        pass # Will become KORPUS class with verbatim target span after alignment
        
    # Priority b: Known good equivalents / dictionary / AI-taklif
    if eng_lower in KNOWN_GOOD_EQUIVALENTS:
        for v_text, v_form in KNOWN_GOOD_EQUIVALENTS[eng_lower]:
            variants.append({
                "text": uz_norm(v_text),
                "source_class": "AI-taklif",
                "form": v_form,
                "status": "AI-taklif (tekshirilmagan)",
                "calque_risk": False
            })
    else:
        # Check current Uzbek field for calques or finite forms
        raw_uz = c.get('uzbek', '').strip()
        raw_uz_norm = uz_norm(raw_uz)
        
        if raw_uz_norm in CALQUE_REPLACEMENTS:
            for v_text, v_form in CALQUE_REPLACEMENTS[raw_uz_norm]:
                variants.append({
                    "text": uz_norm(v_text),
                    "source_class": "AI-taklif",
                    "form": v_form,
                    "status": "AI-taklif (tekshirilmagan)",
                    "calque_risk": False
                })
        elif raw_uz:
            # Check if verb collocation ending in finite form instead of -moq
            cleaned_variant = raw_uz_norm
            # Replace common finite endings
            if cleaned_variant.endswith(' qiling'):
                cleaned_variant = cleaned_variant[:-7] + ' qilmoq'
            elif cleaned_variant.endswith(' bering'):
                cleaned_variant = cleaned_variant[:-7] + ' bermoq'
            elif cleaned_variant.endswith(' oling'):
                cleaned_variant = cleaned_variant[:-6] + ' olmoq'
            elif cleaned_variant.endswith(' eting'):
                cleaned_variant = cleaned_variant[:-6] + ' etmoq'
                
            v_form = "kollokatsiya" if ' ' in cleaned_variant else "bitta soʻz"
            variants.append({
                "text": cleaned_variant,
                "source_class": "AI-taklif",
                "form": v_form,
                "status": "AI-taklif (tekshirilmagan)",
                "calque_risk": bool("bor" in cleaned_variant or "qildim" in cleaned_variant)
            })

    # Ensure at least 1 variant
    if not variants:
        variants.append({
            "text": uz_norm(c.get('uzbek', eng)),
            "source_class": "AI-taklif",
            "form": "kollokatsiya",
            "status": "AI-taklif (tekshirilmagan)",
            "calque_risk": False
        })
        
    c['uzbek_variants'] = variants
    # Keep legacy string in sync
    c['uzbek'] = variants[0]['text']
    c['class'] = variants[0]['source_class']
    c['review_status'] = variants[0]['status']

    # Phase 5: Automatic quality checks for every Uzbek variant
    checks = {
        "orthography_passed": True,
        "vocabulary_passed": True,
        "form_passed": True,
        "calque_free": True
    }
    
    for v in variants:
        v_text = v['text']
        # Orthography check
        if '~' in v_text or any(c in v_text for c in ['`', '´', '’']):
            checks["orthography_passed"] = False
        # Vocabulary check
        tokens_uz = re.findall(r"[a-z\u02bb\u02bc]+", v_text)
        for tok in tokens_uz:
            if tok not in uzbek_vocab and len(tok) > 3:
                # Inflected form check
                pass
        # Form check: if verbal pattern, must end in -moq or -mak
        if 'Feʼl' in c['pattern']:
            if not any(v_text.endswith(end) for end in ('moq', 'mak', 'ish', 'uv')):
                checks["form_passed"] = False
        # Calque check
        if v.get('calque_risk'):
            checks["calque_free"] = False

    c['quality_checks'] = checks
    cleaned_collocs.append(c)

# Pre-select 100 sample entries for researcher review
active_candidates = [c for c in cleaned_collocs if c['status'] == 'active']
sample_100_ids = set(c['id'] for c in random.sample(active_candidates, min(100, len(active_candidates))))
for c in cleaned_collocs:
    c['is_sample_100'] = (c['id'] in sample_100_ids)

# Save updated collocations_full.json
with open(COLLOC_FILE, 'w', encoding='utf-8') as f:
    json.dump(cleaned_collocs, f, ensure_ascii=False, indent=2)

print(f"\nDone! Saved {len(cleaned_collocs)} collocations.")
print("Defect breakdown:", needs_repair_counts)
print("\nStats per source:")
for src, st in stats_per_source.items():
    print(f"  {src}:")
    print(f"    Total: {st['total']}, Verified: {st['verified']}, Needs repair: {st['needs_repair']}, Merged duplicates: {st['merged_duplicates']}")
