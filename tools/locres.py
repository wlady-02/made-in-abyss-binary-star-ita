#!/usr/bin/env python3
"""Lettura/scrittura dei file UE4 .locres v2 (Optimized_CRC32).

Il round trip e' identico byte per byte sui file del gioco.
  locres.py dump <Game.locres>   -> elenco ns|chiave e testo
"""
import json, struct, sys

MAGIC = bytes.fromhex('0e147475674a03fc4a15909dc3377f1b')


def rstr(b, p):
    n = struct.unpack_from('<i', b, p)[0]; p += 4
    if n >= 0:
        return b[p:p + max(n - 1, 0)].decode('latin-1'), p + n
    return b[p:p - 2 * n - 2].decode('utf-16-le'), p - 2 * n


def wstr(s):
    if not s:
        return struct.pack("<i", 1) + b"\0"
    try:
        e = s.encode('ascii') + b'\0'; return struct.pack('<i', len(e)) + e
    except UnicodeEncodeError:
        e = s.encode('utf-16-le') + b'\0\0'; return struct.pack('<i', -(len(e) // 2)) + e


def read(src):
    """src: percorso del file oppure il suo contenuto in bytes."""
    b = src if isinstance(src, bytes) else open(src, 'rb').read()
    assert b[:16] == MAGIC and b[16] == 2, 'formato locres non supportato'
    soff, total, nns = struct.unpack_from('<qII', b, 17); p = 33
    q = soff; nstr = struct.unpack_from('<i', b, q)[0]; q += 4
    strings = []
    for _ in range(nstr):
        s, q = rstr(b, q); q += 4  # refcount
        strings.append(s)
    out = []
    for _ in range(nns):
        nsh = struct.unpack_from('<I', b, p)[0]; ns, p = rstr(b, p + 4)
        nk = struct.unpack_from('<I', b, p)[0]; p += 4
        for _ in range(nk):
            kh = struct.unpack_from('<I', b, p)[0]; key, p = rstr(b, p + 4)
            sh, si = struct.unpack_from('<Ii', b, p); p += 8
            out.append(dict(ns=ns, nsh=nsh, key=key, kh=kh, sh=sh, text=strings[si]))
    return out


def write(path, entries):
    strings, sidx = [], {}
    body = b''
    groups = {}
    for e in entries:
        groups.setdefault((e['nsh'], e['ns']), []).append(e)
    for (nsh, ns), es in groups.items():
        body += struct.pack('<I', nsh) + wstr(ns) + struct.pack('<I', len(es))
        for e in es:
            t = e['text']
            if t not in sidx:
                sidx[t] = len(strings); strings.append([t, 0])
            strings[sidx[t]][1] += 1
            body += struct.pack('<I', e['kh']) + wstr(e['key']) + struct.pack('<Ii', e['sh'], sidx[t])
    head_len = 16 + 1 + 8 + 4 + 4
    sarr = struct.pack('<i', len(strings)) + b''.join(wstr(s) + struct.pack('<i', c) for s, c in strings)
    hdr = MAGIC + struct.pack('<BqII', 2, head_len + len(body), len(entries), len(groups))
    open(path, 'wb').write(hdr + body + sarr)


if __name__ == '__main__':
    # locres.py dump <Game.locres> : stampa ns|chiave<TAB>testo (per ispezione)
    for e in read(sys.argv[2] if sys.argv[1] == 'dump' else sys.argv[1]):
        print(f"{e['ns']}|{e['key']}\t{e['text']!r}")
