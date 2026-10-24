#!/usr/bin/env python3
"""Costruisce la patch italiana dal gioco installato + translation/it/.

  python3 tools/build.py              -> build/MadeInAbyss-BSFD-ITA_99_P.pak
  python3 tools/build.py install      -> build + copia nella cartella Paks del gioco
  python3 tools/build.py uninstall    -> rimuove la patch dal gioco
  python3 tools/build.py release v0.9.0-beta  -> build/MadeInAbyss-BSFD-ITA-<versione>.zip (pak + LEGGIMI.txt)

Opzioni (variabili d'ambiente):
  GAME_DIR=...   cartella del gioco, se non trovata automaticamente
  SLOTS=en       culture in cui scrivere l'italiano: en (default) sostituisce l'inglese;
                 zh-Hant / zh-Hans usano lo slot cinese (si attiva dalla lingua di Steam)
                 e mettono il font inglese al posto di quello cinese, che non ha le lettere accentate.
"""
import os, shutil, sys, tempfile, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamefiles, locres, pakutil, tr

OUT = os.path.join(tr.ROOT, 'build', gamefiles.MOD_PAK)


def build():
    slots = os.environ.get('SLOTS', 'en').split()
    translations = tr.load_translations()
    entries = locres.read(gamefiles.read_file(gamefiles.locres_path('en')))
    done = 0
    for e in entries:
        it = translations.get((e['ns'], e['key']))
        if it:
            e['text'] = it; done += 1
    print(f'{done}/{len(entries)} stringhe tradotte')
    stage = tempfile.mkdtemp(prefix='mia-ita-')
    try:
        for slot in slots:
            dst = os.path.join(stage, gamefiles.locres_path(slot))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            locres.write(dst, entries)
            if slot != 'en':
                font = os.path.join(stage, gamefiles.font_path(slot))
                os.makedirs(os.path.dirname(font), exist_ok=True)
                open(font, 'wb').write(gamefiles.read_file(gamefiles.font_path('en')))
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        pakutil.create(OUT, stage)
    finally:
        shutil.rmtree(stage)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    target = os.path.join(gamefiles.paks_dir(), gamefiles.MOD_PAK)
    if cmd == 'uninstall':
        if os.path.exists(target):
            os.remove(target); print('rimossa', target)
        else:
            print('patch non installata')
        sys.exit()
    build()
    if cmd == 'release':
        version = sys.argv[2]
        readme = open(os.path.join(tr.ROOT, 'release', 'LEGGIMI.txt'), encoding='utf-8').read()
        zpath = os.path.join(tr.ROOT, 'build', f'MadeInAbyss-BSFD-ITA-{version}.zip')
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(OUT, gamefiles.MOD_PAK)
            z.writestr('LEGGIMI.txt', readme.replace('{VERSION}', version).replace('\n', '\r\n'))
        print('creato', zpath)
    if cmd == 'install':
        shutil.copyfile(OUT, target); print('installata in', target)
