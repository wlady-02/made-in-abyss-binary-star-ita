# Made in Abyss: Binary Star Falling into Darkness: Traduzione italiana (amatoriale)

**Patch di traduzione italiana non ufficiale** per *Made in Abyss: Binary Star Falling into Darkness* (PC / Steam).
Traduce tutti i testi del gioco: dialoghi, menu, oggetti, missioni, bestiario, tutorial.

> 🇬🇧 *Unofficial Italian fan translation of Made in Abyss: Binary Star Falling into Darkness (PC/Steam).
> [English summary below](#english).*

| | |
|---|---|
| **Stato** | Beta: 7487/7487 stringhe tradotte, revisione in corso |
| **Versione del gioco** | Steam, build 10136809 (ottobre 2026) |
| **Piattaforme** | Windows, Linux (Proton), Steam Deck |
| **Voci** | Restano originali (giapponese o inglese): la patch traduce i testi e i sottotitoli |

**[⬇️ Scarica l'ultima versione](../../releases/latest)** · disponibile anche su **[Nexus Mods](https://www.nexusmods.com/madeinabyssbinarystarfallingintodarkness/mods/26)** · [discussione su Steam](https://steamcommunity.com/app/1324340/discussions/0/573804739774403109/)

---

## ⚠️ Da sapere prima di installare

- **È una traduzione amatoriale e gratuita**, non affiliata in alcun modo con gli sviluppatori o gli editori del gioco.
- **È stata realizzata con un'intelligenza artificiale**: [Claude](https://www.anthropic.com/claude) di Anthropic
  (modello Claude Opus 5.5), con un glossario comune, il testo giapponese originale come riferimento e controlli
  automatici su formato e lunghezza delle righe. Il progetto è coordinato e testato da [wlady-02](https://github.com/wlady-02).
- **Non è ancora stata rivista per intero da un essere umano.** Menu e prologo sono stati verificati in gioco, il resto
  no: aspettati qualche frase poco naturale, un termine incoerente o un testo che sfora dal riquadro.
  **Le segnalazioni sono benvenute**: vedi [Segnalare un errore](#segnalare-un-errore).

## Installazione

1. Scarica `MadeInAbyss-BSFD-ITA-<versione>.zip` dalla pagina **[Releases](../../releases/latest)** (oppure da [Nexus Mods](https://www.nexusmods.com/madeinabyssbinarystarfallingintodarkness/mods/26)) ed estrailo.
2. Apri la cartella del gioco: in Steam, **tasto destro sul gioco → Gestisci → Sfoglia i file locali**.
3. Entra in `MadeInAbyss-BSFD` → `Content` → `Paks`.
4. Copia lì il file **`MadeInAbyss-BSFD-ITA_99_P.pak`**, accanto ai file `.pak` del gioco (non sostituisce nulla).
5. Avvia il gioco con **la lingua del testo su Inglese**: nelle opzioni del gioco "Text Language: English" e, in Steam,
   lingua del gioco Inglese. La patch prende il posto dell'inglese.

Percorsi tipici della cartella `Paks`:

| Sistema | Percorso |
|---|---|
| Windows | `C:\Program Files (x86)\Steam\steamapps\common\MadeInAbyss-BSFD\MadeInAbyss-BSFD\Content\Paks` |
| Linux | `~/.steam/steam/steamapps/common/MadeInAbyss-BSFD/MadeInAbyss-BSFD/Content/Paks` |
| Steam Deck | come Linux, dalla **modalità desktop** (Dolphin) |

Su Linux e Steam Deck non serve nessuna configurazione di Proton: è un normale file del gioco.

### Disinstallazione

Cancella `MadeInAbyss-BSFD-ITA_99_P.pak` dalla cartella `Paks`. Il gioco torna in inglese.
I salvataggi non vengono toccati: puoi installare e disinstallare la patch quando vuoi.

### Dopo un aggiornamento del gioco

La patch è fatta per la build indicata sopra. Se un aggiornamento di Steam cambia dei testi, quelli modificati
resterebbero coperti dalla versione tradotta più vecchia. In caso di problemi dopo un aggiornamento, disinstalla
la patch e controlla se è uscita una nuova versione qui.

## Domande frequenti

**Nelle opzioni la lingua si chiama ancora "English". È normale?**
Sì. Il gioco ha solo giapponese e inglese, e il menu delle lingue è nel codice compilato: non si può aggiungere una voce
"Italiano" in modo pulito. Per questo l'italiano prende il posto dell'inglese.

**Alcune scritte sono ancora in inglese.**
I testi disegnati dentro le immagini (alcuni titoli e loghi) non fanno parte dei file di testo e restano in inglese.
Se invece trovi una frase normale non tradotta, segnalala.

**Funziona con la versione Switch o PS4?**
No, solo con la versione PC di Steam.

**Steam "Verifica integrità dei file" rimuove la patch?**
No, la patch è un file in più e Steam non lo tocca. Per toglierla va cancellata a mano.

## Segnalare un errore

Apri una **[segnalazione (issue)](../../issues/new/choose)** indicando:
- dove compare il testo (scena, menu, nome dell'oggetto o della missione…);
- il testo attuale e, se vuoi, come lo correggeresti;
- se possibile uno screenshot (soprattutto per i testi che escono dal riquadro).

Le correzioni vengono raccolte e pubblicate in nuove versioni.

## Per chi vuole contribuire o ricompilare la patch

Il repository contiene **solo il lavoro originale** del progetto: i testi italiani (`translation/it/`), il glossario e gli
strumenti in Python. **Non contiene nessun file del gioco**: il testo originale viene letto dalla copia del gioco
installata sul tuo computer al momento della compilazione.

Serve Python 3.8 o successivo, nient'altro:

```bash
python3 tools/tr.py sources        # legge i testi originali dal gioco installato
python3 tools/tr.py check          # controlla segnaposto, codici dei tasti, lunghezza delle righe
python3 tools/build.py install     # crea la patch e la copia nel gioco
```

Tutti i dettagli, dal formato dei file alle regole di traduzione e al flusso di lavoro, sono in [CONTRIBUTING.md](CONTRIBUTING.md).

### Struttura

```
translation/it/            testi italiani, un file per sezione ({"chiave": "testo"})
translation/glossario.md   regole di stile, tu/lei, termini fissi
translation/termini_nuovi.md  termini scelti durante la traduzione
tools/                     estrazione dal gioco, controlli, compilazione della patch
```

## Dettagli tecnici

- Gioco in **Unreal Engine 4.25**. I testi stanno in `Content/Localization/Game/<lingua>/Game.locres` (formato v2),
  dentro pak v9 non cifrate e non compresse.
- La patch è una pak aggiuntiva con priorità più alta (`_99_P`) che contiene solo il `Game.locres` inglese con i testi
  in italiano. I file originali del gioco non vengono modificati.
- Gli strumenti (`tools/pakutil.py`, `tools/locres.py`) sono scritti da zero. Leggono e riscrivono pak e locres in
  modo identico byte per byte agli originali, e non serve nessun programma esterno.

## Crediti e licenza

- **Traduzione**: Claude (Anthropic), modello Claude Opus 5.5.
- **Coordinamento, test e pubblicazione**: [wlady-02](https://github.com/wlady-02).
- Codice degli strumenti: licenza [MIT](LICENSE). Testi tradotti: liberamente utilizzabili per scopi **non commerciali**
  (vedi [LICENSE](LICENSE)).

*Made in Abyss* è un'opera di Akihito Tsukushi. *Made in Abyss: Binary Star Falling into Darkness* e tutti i marchi
collegati appartengono ai rispettivi proprietari, tra cui Spike Chunsoft e CHIME. Questo progetto non è affiliato né
approvato da loro e non distribuisce file del gioco. Se sei un titolare dei diritti e vuoi che il progetto venga
rimosso, apri una issue: verrà rimosso.

---

<a id="english"></a>
## 🇬🇧 English

**Unofficial Italian fan translation (traduzione italiana) of *Made in Abyss: Binary Star Falling into Darkness*
for PC / Steam.** It translates all in-game text into Italian: dialogue, menus, items, quests, bestiary and tutorials.
Voices stay in Japanese or English.

- **Status:** beta. All 7,487 strings are translated, and human review is ongoing.
- **Made with AI:** translated by [Claude](https://www.anthropic.com/claude) (Anthropic, Claude Opus 5.5), using a
  shared glossary, the original Japanese script as reference, and automated checks for placeholders and line length.
  Coordinated and tested by [wlady-02](https://github.com/wlady-02). It has **not** yet been fully proofread by a human.
- **Game version:** Steam build 10136809. Works on Windows, Linux (Proton) and Steam Deck.

### Install

1. Download the zip from **[Releases](../../releases/latest)** or [Nexus Mods](https://www.nexusmods.com/madeinabyssbinarystarfallingintodarkness/mods/26).
2. In Steam: *right-click the game → Manage → Browse local files*, then open `MadeInAbyss-BSFD/Content/Paks`.
3. Copy `MadeInAbyss-BSFD-ITA_99_P.pak` there. It is an extra file and replaces nothing.
4. Play with the text language set to **English**. The patch replaces the English text with Italian.

To uninstall, delete the `.pak` file.

### Build from source

The repository contains only the Italian text and Python tools. **No game files are included**: the original text
is read from your own installed copy of the game when you build.

```bash
python3 tools/tr.py sources && python3 tools/build.py install
```

Not affiliated with or endorsed by Spike Chunsoft, CHIME or the Made in Abyss rights holders. Non-commercial fan project.
