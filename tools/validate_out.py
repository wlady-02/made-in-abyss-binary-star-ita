#!/usr/bin/env python3
"""Valida un lotto tradotto translation/work/<nome>.out.json contro il suo .in.json,
senza toccare translation/it/.

  validate_out.py <nome>    es. validate_out.py MIA1002
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr

name = sys.argv[1]
d = tr.load(); lim = tr.limits(d)
inp = json.load(open(os.path.join(tr.WORK, name + '.in.json'), encoding='utf-8'))
out = json.load(open(os.path.join(tr.WORK, name + '.out.json'), encoding='utf-8'))
idx = {f"{e['ns']}|{e['key']}": e for e in d}
miss = [x['id'] for x in inp if not out.get(x['id'])]
extra = [k for k in out if k not in idx]
bad = 0
for k, v in out.items():
    if k in idx:
        e = dict(idx[k]); e['it'] = v
        for p in tr.problems(e, lim):
            bad += 1; print(k, p)
print(f'{name}: mancanti {len(miss)} {miss[:5]} | id sconosciuti {len(extra)} | problemi {bad}')
sys.exit(1 if miss or extra or bad else 0)
