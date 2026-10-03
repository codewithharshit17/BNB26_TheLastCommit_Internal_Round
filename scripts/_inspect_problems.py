import json
from collections import Counter

data = json.load(open('engine/data/mcminer/problems_processed.json', encoding='utf-8'))
print('=== Field analysis ===')
print(f'Total problems: {len(data)}')

with_sol   = sum(1 for p in data if p.get('solutions'))
with_tests = sum(1 for p in data if p.get('unit_tests','').strip())
print(f'With solutions:   {with_sol}')
print(f'With unit_tests:  {with_tests}')

sources = Counter(p.get('source','') for p in data)
print(f'Sources: {dict(sources)}')

print('\n=== Sample problems ===')
samples = [p for p in data if p.get('solutions') and p.get('unit_tests','').strip()][:3]
for p in samples:
    print(f"id={p['id']} source={p['source']}")
    print(f"  title: {p['title']}")
    print(f"  solution[0]: {repr(p['solutions'][0][:80])}")
    print(f"  unit_tests:  {repr(p['unit_tests'][:80])}")
    print()

target_tags = ['indexing','index','range','string','list','assignment','arithmetic','division','operator']
print('=== Tag coverage for our families ===')
for tag in target_tags:
    count = sum(1 for p in data if tag in ' '.join(p.get('tags',[])).lower())
    print(f'  {tag}: {count} problems')

# FalconCode check (no public license per PRD)
falcon = sum(1 for p in data if 'falcon' in p.get('source','').lower())
print(f'\nFalconCode problems (exclude per PRD): {falcon}')
print('All others are usable (MBPP=CC-BY-4.0, rest permissive)')
