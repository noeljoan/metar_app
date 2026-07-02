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
| 📊 **Tabelle & Diagramm** | Geparste Daten in sortierbarer Treeview-Tabelle + Matplotlib-Chart |
| 🔴 **Live-Simulation** | Erzeugt alle 1,5 s einen zufälligen Live-Datensatz in einem Hintergrund-Thread |
| 🤖 **KI-Vorhersage** | Random-Forest-Modell sagt die Sichtweite aus Temperatur & Luftdruck voraus |

## 🖼️ Aufbau der Oberfläche

```
┌──────────────────────────────────────────────────────────────┐
│  Datenquelle wählen                                           │
│  [ZIP-Datei laden] | Land: [Deutschland ▾] [Live-Daten laden] │
│                                    [Simulation] [KI trainieren]│
├──────────────────────────────────────────────────────────────┤
│  Einzelne Station live abrufen                                │
│  Flughafen-ICAO (z.B. EDMA): [EDMA____] [Wetter laden]        │
├──────────────────────────────────────────────────────────────┤
│  ┌ Daten-Tabelle ┐ ┌ Visualisierung ┐ ┌ KI-Vorhersage ┐       │
│  │  Station-Tabelle mit Wind/Temp/Druck/Sicht          │      │
│  └───────────────────────────────────────────────────  ┘      │
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

## ✅ Getestet

Die App wurde tatsächlich (headless via Xvfb) end-to-end getestet:

- [x] ZIP-Import → Tabelle → Chart-Update
- [x] METAR-Parsing (US- und EU-Sichtweitenformat)
- [x] Live-Abruf einzelner Station (inkl. Validierung & Fehlerfälle)
- [x] KI-Modell-Training + Vorhersage
- [x] Live-Simulation im echten `mainloop()`

## ⚠️ Bekannte Einschränkung

Die Live-Abfragen (`fetch_online_metar_by_country`,
`fetch_online_metar_single`) rufen `aviationweather.gov` auf — das
funktioniert nur mit Internetzugang. Ohne Verbindung erscheint eine klare
Fehlermeldung im Dialog statt eines Absturzes.

## 📝 Lizenz

Dieses Projekt kann frei für eigene Zwecke genutzt und angepasst werden.

---

<div align="center">
Made with 🐍 &nbsp;+&nbsp; ☁️ &nbsp;+&nbsp; ✈️
</div>
