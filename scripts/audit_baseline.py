"""Capture the pre-change evidence from the immutable baseline Git revision."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '97b9413'
URL = 'https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv'

def git_text(path):
    return subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT).decode('utf-8-sig')

def capture():
    raw = (ROOT / 'data/cookie_cats.csv').read_bytes()
    reference = ROOT / 'outputs/upstream_reference.csv'
    if not reference.exists():
        reference.write_bytes(urllib.request.urlopen(URL, timeout=60).read())
    upstream = reference.read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode())))
    full = list(csv.DictReader(io.StringIO(upstream.decode())))
    claims = []
    for path in ['README.md', 'PROJECT_MASTER_REPORT.md']:
        for line_no, line in enumerate(git_text(path).splitlines(), 1):
            if re.search(r'\d', line):
                # Retain original evidence in Git; no obsolete promotional text in outputs.
                claims.append({'file': path, 'line': line_no,
                               'numeric_tokens': re.findall(r'[-+]?\d[\d,.]*(?:e-\d+)?', line)})
    old_segments = list(csv.DictReader(io.StringIO(git_text('data/player_segments.csv'))))
    result = {'baseline_commit': BASELINE, 'source_url': URL,
              'raw_sha256': hashlib.sha256(raw).hexdigest(),
              'source_sha256': hashlib.sha256(upstream).hexdigest(),
              'local_bytes': len(raw), 'source_bytes': len(upstream),
              'exact_byte_prefix': upstream.startswith(raw),
              'raw_rows': len(rows), 'complete_rows': sum(r['retention_7'] is not None for r in rows),
              'source_rows': len(full), 'source_max_rounds': max(int(r['sum_gamerounds']) for r in full),
              'local_max_rounds': max(int(r['sum_gamerounds']) for r in rows if r['sum_gamerounds']),
              'incomplete_row': rows[-1], 'legacy_numeric_claims': claims}
    groups = {}
    total_rounds = sum(int(r['sum_gamerounds']) for r in old_segments)
    for key in sorted({r['cluster_id'] for r in old_segments}):
        g = [r for r in old_segments if r['cluster_id'] == key]
        rounds = sorted(int(r['sum_gamerounds']) for r in g)
        n = len(g)
        groups[key] = {'n': n, 'size_share': n / len(old_segments),
                       'rounds_share': sum(rounds) / total_rounds,
                       'mean_rounds': sum(rounds) / n,
                       'median_rounds': (rounds[(n-1)//2] + rounds[n//2])/2,
                       'd1': sum(int(r['retention_1_int']) for r in g)/n,
                       'd7': sum(int(r['retention_7_int']) for r in g)/n}
    result['legacy_segments'] = groups
    (ROOT / 'outputs/audit_baseline.json').write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / 'outputs/metrics.json').write_text(json.dumps({'audit': result}, indent=2) + '\n')
    return result

if __name__ == '__main__':
    print(json.dumps({k:v for k,v in capture().items() if k not in ['legacy_numeric_claims','legacy_segments']}, indent=2))
