<div align="center">

# 🛫 METAR-Desktop

**Desktop-App zum Laden, Visualisieren und KI-gestützten Vorhersagen von Flughafen-Wetterdaten (METAR)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)](https://docs.python.org/3/library/tkinter.html)
[![scikit--learn](https://img.shields.io/badge/ML-scikit--learn-f7931e?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](#-lizenz)
[![Status](https://img.shields.io/badge/Status-funktionsfähig-brightgreen)](#-getestet)

</div>

---

## 📖 Überblick

METAR-Desktop importiert Flughafen-Wettermeldungen (**METAR**) — aus lokalen
ZIP-Dateien oder live von [aviationweather.gov](https://aviationweather.gov) —
parst sie, stellt sie tabellarisch und grafisch dar und sagt mithilfe eines
Random-Forest-Modells die Sichtweite auf Basis von Temperatur und Luftdruck
voraus.

## ✨ Funktionen

| Bereich | Beschreibung |
|---|---|
| 📦 **ZIP-Import** | METAR-Zeilen aus lokalen `.txt`-Dateien innerhalb einer ZIP-Datei einlesen |
| 🌍 **Live-Daten (Land)** | Aktuelle METARs für ganze Länder abrufen — 🇩🇪 🇲🇽 🇺🇸 🇦🇹 🇨🇭 🇬🇧 🇫🇷 🇪🇸 🇮🇹 🇳🇱 🇧🇪 (10-15 Flughäfen pro Land) |
| ✈️ **Live-Daten (Einzelstation)** | Beliebigen ICAO-Code eingeben (z. B. `EDMA`) und per Klick oder <kbd>Enter</kbd> abrufen |
| 📊 **Tabelle & Diagramm** | Geparste Daten in sortierbarer Treeview-Tabelle (inkl. Wolken, Trend, Remarks) + Matplotlib-Chart |
| 🔴 **Live-Simulation** | Erzeugt alle 1,5 s einen zufälligen Live-Datensatz in einem Hintergrund-Thread |
| 🤖 **KI-Vorhersage** | Random-Forest-Modell sagt die Sichtweite aus Temperatur & Luftdruck voraus |

## 🖼️ Aufbau der Oberfläche

```
┌──────────────────────────────────────────────────────────────┐
│  Datenquelle wählen                                          │
│  [ZIP-Datei laden] | Land: [Deutschland ▾] [Live-Daten laden]│
│                                  [Simulation] [KI trainieren]│
├──────────────────────────────────────────────────────────────┤
│  Einzelne Station live abrufen                               │
│  Flughafen-ICAO (z.B. EDMA): [EDMA____] [Wetter laden]       │
├──────────────────────────────────────────────────────────────┤
│  ┌ Daten-Tabelle ┐ ┌ Visualisierung ┐ ┌ KI-Vorhersage ┐      │
│  │  Station-Tabelle mit Wind/Temp/Druck/Sicht          │     │
│  └───────────────────────────────────────────────────  ┘     │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

```bash
# Projektordner öffnen
cd metar_app

# Virtuelle Umgebung (empfohlen)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

> **Hinweis:** `tkinter` ist bei den meisten Python-Installationen bereits
> enthalten. Falls nicht (z. B. manche Linux-Distributionen):
> ```bash
> sudo apt install python3-tk
> ```

## ▶️ Starten

```bash
python run.py
```

## 📁 Projektstruktur

```
metar_app/
├── run.py                      # Einstiegspunkt
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── main.py                 # Hauptfenster (METARViewer)
    ├── data/
    │   └── metar.zip           # Beispieldaten (4 METARs) zum Testen
    ├── utils/
    │   ├── __init__.py
    │   ├── file_util.py        # ZIP-Import + Live-Abfrage (aviationweather.gov)
    │   └── gui_util.py         # kleine Tk-Hilfsfunktionen
    └── models/
        ├── __init__.py
        └── metar.py            # METAR-Parser (US- & EU-Format)
```

## 🧠 Wie die KI-Vorhersage funktioniert

1. Vorhandene (oder synthetisch generierte, falls < 10 Datensätze) Werte für
   **Temperatur** und **Luftdruck** werden mit `StandardScaler` skaliert.
2. Ein `RandomForestRegressor` (50 Bäume) wird darauf trainiert, die
   **Sichtweite** vorherzusagen.
3. Im Tab *KI-Vorhersage* lassen sich eigene Werte eingeben, um eine
   Prognose zu erhalten.

> Das Modell ist eine Demonstration des ML-Workflows, keine
> meteorologisch validierte Vorhersage.

## 🌐 Unterstützte METAR-Formate

Der Parser (`app/models/metar.py`) erkennt sowohl das **US-Format**
(`10SM` → Statute Miles) als auch das **europäische Format**
(`9999` / `0800` → Meter), z. B.:

```
METAR EDDF 011200Z 24010KT 9999 FEW030 15/08 Q1013=
METAR KJFK 011200Z 24010KT 10SM FEW030 15/08 A3005=
```

Zusätzlich werden folgende Felder ausgewertet und in eigenen
Tabellenspalten angezeigt:

| Feld | Beispiel | Bedeutung |
|---|---|---|
| ☁️ **Wolken** | `BKN020CB, OVC080` | Bedeckungsgrad + Basishöhe (x100 ft), optional CB/TCU; `CAVOK`/`SKC`/`CLR`/`NSC`/`NCD` werden ebenfalls erkannt |
| 📈 **Trend** | `NOSIG` | Kurzfrist-Trend (`NOSIG`, `BECMG`, `TEMPO`) |
| 📝 **Remarks** | `8/96/ HZY OCNL DROPS BINOVC` | Freitext-Bemerkungen nach `RMK`, unverändert übernommen |

Beispiel-METAR mit allen Feldern:

```
METAR MMSM 020147Z 24005KT 7SM BKN020CB OVC080 13/12 A3034 NOSIG RMK 8/96/ HZY OCNL DROPS BINOVC
```

wird geparst zu:

```json
{
  "station": "MMSM", "time": "01:47", "wind": "24005KT",
  "temp": 13.0, "pressure": 1027.4, "visibility": 11265.38,
  "clouds": "BKN020CB, OVC080", "trend": "NOSIG",
  "remarks": "8/96/ HZY OCNL DROPS BINOVC"
}
```

## ✅ Getestet

Die App wurde tatsächlich (headless via Xvfb) end-to-end getestet:

- [x] ZIP-Import → Tabelle → Chart-Update
- [x] METAR-Parsing (US- und EU-Sichtweitenformat)
- [x] METAR-Parsing von Wolken, Trend (NOSIG/BECMG/TEMPO) und Remarks (RMK)
- [x] Live-Abruf einzelner Station (inkl. Validierung & Fehlerfälle)
- [x] KI-Modell-Training + Vorhersage
- [x] Live-Simulation im echten `mainloop()`

## ⚠️ Bekannte Einschränkung

Die Live-Abfragen (`fetch_online_metar_by_country`,
`fetch_online_metar_single`) rufen `aviationweather.gov` auf — das
funktioniert nur mit Internetzugang. Ohne Verbindung erscheint eine klare
Fehlermeldung im Dialog statt eines Absturzes.

## 📦 Standalone .exe erstellen (PyInstaller)

Damit die App auf einem Windows-Rechner läuft, ohne dass dort Python
installiert sein muss, lässt sie sich mit [PyInstaller](https://pyinstaller.org/)
zu einer einzigen `.exe`-Datei bündeln.

> **Wichtig:** Der Build muss **unter Windows** ausgeführt werden — eine
> unter Linux/Mac gebaute PyInstaller-Datei läuft nicht unter Windows
> (und umgekehrt). Am besten also auf dem Windows-Zielrechner selbst
> bauen (in derselben venv, in der `pip install -r requirements.txt`
> gelaufen ist).

### 1. PyInstaller installieren

```bash
pip install pyinstaller
```

### 2. Build ausführen

```bash
pyinstaller --noconfirm --onefile --windowed --name METAR-Desktop run.py
```

| Flag | Bedeutung |
|---|---|
| `--onefile` | Alles (inkl. matplotlib, pandas, scikit-learn) in **eine** `.exe`-Datei packen |
| `--windowed` | Kein Konsolenfenster im Hintergrund öffnen (reines GUI-Fenster) |
| `--name METAR-Desktop` | Name der erzeugten `.exe` |

Die fertige Datei liegt danach unter:

```
dist/METAR-Desktop.exe
```

Sie ist eigenständig lauffähig — kein `pip install`, keine Python-Installation
auf dem Zielrechner nötig.

### 3. Eigenes Icon (optional)

```bash
pyinstaller --noconfirm --onefile --windowed --name METAR-Desktop --icon=app.ico run.py
```
(`app.ico` muss im Projektordner liegen, Format `.ico`, z. B. via
[convertio.co](https://convertio.co/de/png-ico/) aus einem PNG erzeugt.)

### 4. Aufräumen

PyInstaller legt `build/`, `dist/` und eine `METAR-Desktop.spec`-Datei an.
Nur `dist/METAR-Desktop.exe` wird zum Weitergeben benötigt — `build/` und
die `.spec`-Datei können danach gelöscht werden (oder für den nächsten
Build behalten werden, dann geht ein erneuter Build etwas schneller).

> ✅ Ich habe den obigen Befehl (unter Linux, als Sanity-Check für die
> Parameter) tatsächlich durchlaufen lassen — Build und Start der
> erzeugten Datei liefen fehlerfrei durch, inkl. matplotlib-, pandas- und
> scikit-learn-Abhängigkeiten. Unter Windows erzeugt derselbe Befehl
> entsprechend eine `.exe` statt einer Linux-Binary.

## 📝 Lizenz

Dieses Projekt kann frei für eigene Zwecke genutzt und angepasst werden.

---

<div align="center">
Made with 🐍 &nbsp;+&nbsp; ☁️ &nbsp;+&nbsp; ✈️  &nbsp;+&nbsp; <BR>
(c) Copyright 2026 - Noel Joan    
</div>
