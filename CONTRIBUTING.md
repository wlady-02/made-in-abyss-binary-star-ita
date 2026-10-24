# Contribuire

Grazie per voler migliorare la traduzione! Il modo più semplice è **[aprire una issue](../../issues/new/choose)** con
l'errore trovato. Se invece vuoi correggere direttamente i file, questa guida spiega come funziona il progetto.

## Requisiti

- Python 3.8 o successivo (solo libreria standard).
- Il gioco installato da Steam: gli strumenti leggono da lì il testo originale, che **non** è nel repository.
  Se il gioco non viene trovato automaticamente, indica la cartella con `GAME_DIR`:
  ```bash
  GAME_DIR="/percorso/steamapps/common/MadeInAbyss-BSFD" python3 tools/tr.py sources
  ```

## Dove sono i testi

`translation/it/<namespace>.json` contiene, per ogni sezione del gioco, un oggetto `{"chiave": "testo italiano"}`.

| File | Contenuto |
|---|---|
| `_root.json` | interfaccia: menu, pulsanti, messaggi generici |
| `MIA1xxx.json` | dialoghi della storia *Hello Abyss* (Riko e Reg) |
| `MIA2xxx`–`MIA4xxx.json`, `MIA9xxx.json` | dialoghi di *Deep in Abyss*, eventi e missioni |
| `DT_ItemInfomation.json` | nomi e descrizioni degli oggetti |
| `DT_QuestInfomation.json` | missioni |
| `DT_MonsterInfomation.json`, `DT_PBProtistInfo.json` | creature e bestiario |
| `DT_PBCharaInfo.json`, `DT_CharaInfomation.json` | personaggi |
| `DT_Tutorial.json`, `DT_UIHelp.json`, `DT_OptionText.json`… | tutorial, aiuti, opzioni |

Per trovare una frase: `grep -rn "testo da cercare" translation/it/`.
Per vedere l'originale inglese e giapponese di una chiave, dopo `tools/tr.py sources`:
`grep -n '"key": "MIA1001_002"' -A3 build/cache/source.json`.

## Regole (obbligatorie)

Leggi [translation/glossario.md](translation/glossario.md). In breve:

- **Segnaposto** come `{NAME}`, `{TEU0}`, `{ITEM}`, `{0}`: vanno copiati identici, nello stesso numero.
- **Codici dei tasti** come `@1A`, `@0F`: vanno lasciati identici.
- **A capo**: nel file sono `\r\n`. I dialoghi hanno al massimo **3 righe da 56 caratteri**; le altre sezioni hanno
  limiti ricavati dal testo inglese.
- **Termini**: usa quelli del glossario. Se un termine cambia, cambialo ovunque e nel glossario.

Il controllo automatico verifica tutto questo:

```bash
python3 tools/tr.py check            # tutto
python3 tools/tr.py check MIA1004    # solo una sezione
```

## Provare una modifica in gioco

```bash
python3 tools/build.py install       # crea la patch e la copia nel gioco
python3 tools/build.py uninstall     # la rimuove
```

## Inviare la correzione

1. Fai un fork e crea un branch.
2. Modifica i file in `translation/it/`.
3. Esegui `python3 tools/tr.py check`: deve dire `problemi: 0`.
4. Apri una pull request spiegando cosa hai cambiato e perché (meglio se con uno screenshot).

**Non includere mai file del gioco** (`.pak`, `.locres`, `.uasset`, font, testi originali completi): il `.gitignore`
li esclude già.

## Tradurre testo nuovo (dopo un aggiornamento del gioco)

```bash
python3 tools/tr.py sources          # rilegge il testo dal gioco aggiornato
python3 tools/tr.py missing          # chiavi senza traduzione
python3 tools/tr.py batch MIA1004    # crea translation/work/MIA1004.in.json (en + ja + limiti)
# traduci in translation/work/MIA1004.out.json come {"<ns>|<chiave>": "italiano"}
python3 tools/validate_out.py MIA1004
python3 tools/tr.py apply translation/work/MIA1004.out.json
```

## Strumenti

| Script | Cosa fa |
|---|---|
| `tools/gamefiles.py` | trova il gioco (Steam su Linux/Windows o `GAME_DIR`) e legge i file dalle pak in ordine di priorità |
| `tools/pakutil.py` | legge, estrae e crea pak UE4.25 v9 (`list`, `extract`, `create`) |
| `tools/locres.py` | legge e scrive `Game.locres` v2 (`dump` per ispezionarlo) |
| `tools/tr.py` | estrazione dei testi, controlli, stato, lotti di traduzione |
| `tools/validate_out.py` | valida un lotto tradotto prima di applicarlo |
| `tools/build.py` | crea, installa e rimuove la patch |

---

## 🇬🇧 Contributing (short)

Report mistakes through [issues](../../issues/new/choose). To fix text directly, edit
`translation/it/<namespace>.json`, keep every `{placeholder}` and `@XX` code intact, respect the line limits
(dialogue: max 3 lines of 56 characters), run `python3 tools/tr.py check`, and open a pull request.
Never commit game files. The tools read the original text from your own installed copy of the game.
