#!/usr/bin/env python3
"""Minimal reader/writer for UE4.25 .pak (v9, no compression, no encryption).

  pakutil.py list    <pak> [filter]
  pakutil.py extract <pak> <outdir> <filter...>   (substring of the path)
  pakutil.py create  <out.pak> <srcdir> [mount]   (mount default ../../../)
"""
import hashlib, os, struct, sys

MAGIC = 0x5A6F12E1


def read_fstring(b, p):
    n = struct.unpack_from('<i', b, p)[0]; p += 4
    if n == 0:
        return '', p
    if n > 0:
        s = b[p:p + n - 1].decode('latin-1'); return s, p + n
    n = -n
    s = b[p:p + 2 * n - 2].decode('utf-16-le'); return s, p + 2 * n


def write_fstring(s):
    try:
        e = s.encode('ascii') + b'\0'; return struct.pack('<i', len(e)) + e
    except UnicodeEncodeError:
        e = s.encode('utf-16-le') + b'\0\0'; return struct.pack('<i', -(len(e) // 2)) + e


def read_footer(f):
    f.seek(0, 2); size = f.tell()
    f.seek(max(0, size - 512)); tail = f.read()
    i = tail.rfind(struct.pack('<I', MAGIC))
    enc_index = tail[i - 1]
    magic, ver, off, isz = struct.unpack_from('<IiQQ', tail, i)
    return ver, off, isz, enc_index


def read_entry(b, p, ver):
    off, size, usize, comp = struct.unpack_from('<qqqI', b, p); p += 28
    sha = b[p:p + 20]; p += 20
    blocks = []
    if comp:
        n = struct.unpack_from('<i', b, p)[0]; p += 4
        for _ in range(n):
            blocks.append(struct.unpack_from('<qq', b, p)); p += 16
    flags, bsize = struct.unpack_from('<BI', b, p); p += 5
    return dict(offset=off, size=size, usize=usize, comp=comp, sha=sha,
                blocks=blocks, flags=flags, bsize=bsize), p


def entry_bytes(offset, data):
    return (struct.pack('<qqqI', offset, len(data), len(data), 0)
            + hashlib.sha1(data).digest() + struct.pack('<BI', 0, 0))


def read_index(path):
    with open(path, 'rb') as f:
        ver, off, isz, enc = read_footer(f)
        if enc:
            sys.exit('index cifrato: serve la chiave AES')
        f.seek(off); b = f.read(isz)
    mount, p = read_fstring(b, 0)
    n = struct.unpack_from('<i', b, p)[0]; p += 4
    entries = []
    for _ in range(n):
        name, p = read_fstring(b, p)
        e, p = read_entry(b, p, ver)
        e['name'] = name; entries.append(e)
    return ver, mount, entries


def extract(pak, outdir, filters):
    ver, mount, entries = read_index(pak)
    with open(pak, 'rb') as f:
        for e in entries:
            if filters and not any(x in e['name'] for x in filters):
                continue
            if e['comp'] or e['flags'] & 1:
                print('SKIP (compresso/cifrato):', e['name']); continue
            f.seek(e['offset']); hdr = f.read(53)
            f.seek(e['offset'] + 53); data = f.read(e['size'])
            if hashlib.sha1(data).digest() != e['sha']:
                print('WARN sha1 mismatch:', e['name'])
            dst = os.path.join(outdir, e['name'])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'wb').write(data)
            print(e['name'], len(data))


def create(out, src, mount='../../../'):
    files = sorted(os.path.relpath(os.path.join(r, n), src).replace(os.sep, '/')
                   for r, _, ns in os.walk(src) for n in ns)
    index = b''
    with open(out, 'wb') as f:
        for name in files:
            data = open(os.path.join(src, name), 'rb').read()
            off = f.tell()
            f.write(entry_bytes(0, data)); f.write(data)
            index += write_fstring(name) + entry_bytes(off, data)
        index = write_fstring(mount) + struct.pack('<i', len(files)) + index
        ioff = f.tell(); f.write(index)
        f.write(b'\0' * 16 + b'\0')  # key guid, index non cifrato
        f.write(struct.pack('<IiQQ', MAGIC, 9, ioff, len(index)))
        f.write(hashlib.sha1(index).digest())
        f.write(b'\0')               # bFrozenIndex
        f.write(b'\0' * 32 * 5)      # nessun metodo di compressione
    print('creato', out, len(files), 'file')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list':
        ver, mount, entries = read_index(sys.argv[2])
        flt = sys.argv[3] if len(sys.argv) > 3 else ''
        print('version', ver, 'mount', mount, 'entries', len(entries), file=sys.stderr)
        for e in entries:
            if flt in e['name']:
                print(e['name'], e['size'], 'comp=%d flags=%d' % (e['comp'], e['flags']))
    elif cmd == 'extract':
        extract(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == 'create':
        create(*sys.argv[2:])
