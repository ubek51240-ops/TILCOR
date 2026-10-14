import json
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from search_engine import execute_unified_search

def main():
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
        collocations = json.load(f)
    with open('data/dictionary.json', 'r', encoding='utf-8') as f:
        dictionary = json.load(f)

    test_queries = ['og‘ir uyqu', 'heavy sleep', 'javob bermoq', 'dasturxon solmoq', 'yurak', 'heart', 'qaror bermoq']
    for q in test_queries:
        res = execute_unified_search(q, corpus, collocations, dictionary)
        print(f"\n==========================================")
        print(f"QUERY: '{q}' (Lang: {res['selected_lang']}, Multi: {res['is_collocation_query']})")
        print(f"Summary: {res['summary']}")
        ms = res['muqobil_summary']
        s1 = ms.get('source_1_confirmed', [])
        print(f"Source 1 Confirmed ({len(s1)} items):")
        for it in s1:
            print(f"  - '{it['equivalent']}' ({it['count']} marta, sahifalar: {it['pages']}, shakli: {it['form']})")
        s2 = ms.get('source_2_ai_proposal', [])
        print(f"Source 2 AI-taklif ({len(s2)} items):")
        for it in s2[:3]:
            print(f"  - '{it['equivalent']}' ({it['count']} marta, sahifalar: {it['pages']})")
        s3 = ms.get('source_3_dictionary', [])
        print(f"Source 3 Dictionary ({len(s3)} items):")
        for it in s3:
            print(f"  - '{it['equivalent'][:40]}...' | {it.get('dictionary_source')}")
        if ms.get('source_1_empty'):
            print(f"Empty state: {ms.get('empty_message')}")
        print(f"Top Sentence Card:")
        if res['corpus_sentences']:
            top_s = res['corpus_sentences'][0]
            print(f"  ID: {top_s['id']} | RankWeight: {top_s.get('ranking_weight')} | Status: {top_s['target_status_label']}")
            print(f"  Source: {top_s['source_label']}")
            print(f"  Target: {top_s['target_label']}")

if __name__ == '__main__':
    main()
