#!/usr/bin/env python3
"""Trova l'installazione del gioco e legge i file dalle sue pak.

I file originali non sono nel repository: vengono letti ogni volta dal gioco
installato di chi compila, rispettando la priorita' delle pak (base < _0_P < ...).
La variabile d'ambiente GAME_DIR permette di indicare la cartella a mano.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pakutil

GAME_FOLDER = 'MadeInAbyss-BSFD'
MOD_PAK = 'MadeInAbyss-BSFD-ITA_99_P.pak'


def _steam_roots():
    home = os.path.expanduser('~')
    roots = [
        os.path.join(home, '.steam', 'steam'),
        os.path.join(home, '.steam', 'debian-installation'),
        os.path.join(home, '.local', 'share', 'Steam'),
        os.path.join(home, '.var', 'app', 'com.valvesoftware.Steam', '.local', 'share', 'Steam'),
        r'C:\Program Files (x86)\Steam',
        r'C:\Program Files\Steam',
    ]
    return [r for r in roots if os.path.isdir(r)]


def _libraries():
    libs = []
    for root in _steam_roots():
        libs.append(root)
        vdf = os.path.join(root, 'steamapps', 'libraryfolders.vdf')
        if os.path.isfile(vdf):
            for path in re.findall(r'"path"\s+"([^"]+)"', open(vdf, encoding='utf-8', errors='replace').read()):
                libs.append(path.replace('\\\\', '\\'))
    return libs


def game_dir():
    env = os.environ.get('GAME_DIR')
    if env:
        return env
    for lib in _libraries():
        cand = os.path.join(lib, 'steamapps', 'common', GAME_FOLDER)
        if os.path.isdir(os.path.join(cand, GAME_FOLDER, 'Content', 'Paks')):
            return cand
    sys.exit('Gioco non trovato. Indica la cartella con GAME_DIR=/percorso/MadeInAbyss-BSFD')


def paks_dir():
    return os.path.join(game_dir(), GAME_FOLDER, 'Content', 'Paks')


def _pak_order(name):
    """Priorita' come in UE4.25: pak normali prima, poi _P per numero di versione."""
    if not name.endswith('_P.pak'):
        return 0
    m = re.search(r'_(\d+)_P\.pak$', name)
    version = int(m.group(1)) + 1 if m and int(m.group(1)) >= 1 else 1
    return 100 * version


def official_paks():
    d = paks_dir()
    names = [n for n in os.listdir(d) if n.endswith('.pak') and n != MOD_PAK]
    return [os.path.join(d, n) for n in sorted(names, key=lambda n: (_pak_order(n), n))]


def read_file(internal_path):
    """Contenuto della versione piu' recente di un file interno alle pak ufficiali."""
    found = None
    for pak in official_paks():
        _, _, entries = pakutil.read_index(pak)
        for e in entries:
            if e['name'] == internal_path:
                found = (pak, e)
    if not found:
        sys.exit(f'{internal_path} non trovato nelle pak del gioco')
    pak, e = found
    with open(pak, 'rb') as f:
        f.seek(e['offset'] + 53)
        return f.read(e['size'])


def locres_path(culture):
    return f'{GAME_FOLDER}/Content/Localization/Game/{culture}/Game.locres'


def font_path(culture):
    return {
        'en': f'{GAME_FOLDER}/Content/MadeInAbyss/Font/en/FontFace_FOT-UDKakugo_LargePro-M.ufont',
        'zh-Hant': f'{GAME_FOLDER}/Content/MadeInAbyss/Font/zh-Hant/FontFace_DFT_R3.ufont',
        'zh-Hans': f'{GAME_FOLDER}/Content/MadeInAbyss/Font/zh-Hans/FontFace_DFGB_Y3.ufont',
    }[culture]
