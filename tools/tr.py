#!/usr/bin/env python3
"""Gestione della traduzione.

I testi italiani sono in translation/it/<namespace>.json come {"<chiave>": "testo"}
(il namespace vuoto dell'interfaccia e' nel file _root.json).
Il testo originale (inglese + giapponese di riferimento) NON e' nel repository:
`tr.py sources` lo estrae dal gioco installato in build/cache/source.json.

  tr.py sources              -> estrae i testi originali dal gioco (serve una volta)
  tr.py status               -> avanzamento per namespace
  tr.py check [ns...]        -> controlla segnaposto, codici @, larghezza e numero di righe
  tr.py batch <ns> [ns...]   -> translation/work/<nome>.in.json da tradurre (en + ja + limiti)
  tr.py apply <file.json>    -> applica un file {"<ns>|<chiave>": "italiano"} a translation/it/
  tr.py missing              -> chiavi del gioco senza traduzione (es. dopo un aggiornamento)
"""
import collections, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import locres

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IT_DIR = os.path.join(ROOT, 'translation', 'it')
WORK = os.path.join(ROOT, 'translation', 'work')
SOURCE = os.path.join(ROOT, 'build', 'cache', 'source.json')
TOKEN = re.compile(r'\{[^}]*\}|@[0-9A-F]{2}|<[^>]*>|%[sd]')
NL = '\r\n'


def ns_file(ns):
    return os.path.join(IT_DIR, (ns or '_root') + '.json')


def extract_sources():
    import gamefiles
    en = locres.read(gamefiles.read_file(gamefiles.locres_path('en')))
    ja = {(e['ns'], e['key']): e['text'] for e in locres.read(gamefiles.read_file(gamefiles.locres_path('ja')))}
    src = [dict(ns=e['ns'], key=e['key'], src=e['text'], ja=ja.get((e['ns'], e['key']), '')) for e in en]
    os.makedirs(os.path.dirname(SOURCE), exist_ok=True)
    json.dump(src, open(SOURCE, 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(src), 'stringhe originali estratte in', SOURCE)


def load_translations():
    tr = {}
    for name in sorted(os.listdir(IT_DIR)):
        if name.endswith('.json'):
            ns = '' if name == '_root.json' else name[:-5]
            for k, v in json.load(open(os.path.join(IT_DIR, name), encoding='utf-8')).items():
                tr[(ns, k)] = v
    return tr


def load():
    """Lista di {ns, key, src, ja, it} nell'ordine del Game.locres inglese."""
    if not os.path.exists(SOURCE):
        extract_sources()
    tr = load_translations()
    d = json.load(open(SOURCE, encoding='utf-8'))
    for e in d:
        e['it'] = tr.get((e['ns'], e['key']), '')
    return d


def apply(path):
    new = json.load(open(path, encoding='utf-8'))
    known = {(e['ns'], e['key']) for e in load()}
    by_ns = collections.defaultdict(dict)
    bad = []
    for k, v in new.items():
        ns, key = k.split('|', 1)
        if (ns, key) not in known:
            bad.append(k)
        elif v:
            by_ns[ns][key] = v
    for ns, items in by_ns.items():
        f = ns_file(ns)
        cur = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {}
        cur.update(items)
        json.dump(dict(sorted(cur.items())), open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        open(f, 'a', encoding='utf-8').write('\n')
    print(sum(len(x) for x in by_ns.values()), 'applicate', f'(id sconosciuti: {bad[:5]})' if bad else '')


def limits(d):
    """Larghezza e righe massime per namespace, ricavate dall'inglese."""
    w, n = collections.defaultdict(list), collections.defaultdict(int)
    for e in d:
        g = 'MIA' if e['ns'].startswith('MIA') else e['ns']
        lines = e['src'].split(NL)
        w[g] += [len(x.rstrip()) for x in lines]
        n[g] = max(n[g], len(lines))
    out = {}
    for g, v in w.items():
        v.sort()
        out[g] = (max(v[int(len(v) * .98)], 20), n[g])
    out['MIA'] = (56, 3)  # riquadro dei dialoghi
    return out


def limit_for(lim, e):
    g = 'MIA' if e['ns'].startswith('MIA') else e['ns']
    width, maxl = lim[g]
    src_lines = e['src'].split(NL)
    if e['ns'] == 'DT_ItemInfomation' and e['key'].endswith('_Name'):
        # nel riquadro descrizione il nome condivide la riga con il peso ("350g"):
        # oltre 25 caratteri i due testi si sovrappongono (verificato in gioco)
        return 25, 1
    if len(src_lines) == 1 and not e['ns'].startswith('MIA'):
        # etichette/nomi su una riga: niente a capo, max +40% di lunghezza
        return max(len(e['src']) * 14 // 10 + 4, 12), 1
    return max(width, max(len(x.rstrip()) for x in src_lines)), maxl


def problems(e, lim):
    it = e['it']; p = []
    if collections.Counter(TOKEN.findall(it)) != collections.Counter(TOKEN.findall(e['src'])):
        p.append('segnaposto/codici diversi: %s vs %s' % (TOKEN.findall(e['src']), TOKEN.findall(it)))
    if '\n' in it.replace(NL, '') or '\r' in it.replace(NL, ''):
        p.append('a capo non in formato \\r\\n')
    width, maxl = limit_for(lim, e)
    lines = it.split(NL)
    if len(lines) > maxl:
        p.append(f'{len(lines)} righe (max {maxl})')
    for x in lines:
        if len(TOKEN.sub('', x).rstrip()) > width:
            p.append(f'riga di {len(x)} car. (max {width}): {x!r}')
    return p


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'sources':
        return extract_sources()
    if cmd in ('apply', 'merge'):
        return apply(args[0])
    d = load(); lim = limits(d)
    if cmd == 'batch':
        os.makedirs(WORK, exist_ok=True)
        items = []
        for e in d:
            if e['ns'] in args:
                width, maxl = limit_for(lim, e)
                items.append({'id': f"{e['ns']}|{e['key']}", 'en': e['src'], 'ja': e['ja'],
                              'max_chars_per_line': width, 'max_lines': maxl})
        items.sort(key=lambda x: x['id'])
        name = (args[0] or '_root') if len(args) == 1 else f'{args[0] or "_root"}+{len(args) - 1}'
        path = os.path.join(WORK, name + '.in.json')
        json.dump(items, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(path, len(items), 'stringhe')
    elif cmd == 'check':
        bad = 0
        for e in d:
            if e['it'] and (not args or e['ns'] in args):
                for p in problems(e, lim):
                    bad += 1; print(f"{e['ns']}|{e['key']}: {p}")
        print('problemi:', bad); sys.exit(1 if bad else 0)
    elif cmd == 'status':
        c, t = collections.Counter(), collections.Counter()
        for e in d:
            c[e['ns']] += 1; t[e['ns']] += bool(e['it'])
        for ns in sorted(c, key=lambda x: (x.startswith('MIA'), x)):
            print(f'{t[ns]:5}/{c[ns]:<5} {ns or "(UI)"}')
        print(f'TOTALE {sum(t.values())}/{sum(c.values())}')
    elif cmd == 'missing':
        miss = [f"{e['ns']}|{e['key']}" for e in d if not e['it']]
        print('\n'.join(miss)); print(len(miss), 'senza traduzione', file=sys.stderr)


if __name__ == '__main__':
    main()
