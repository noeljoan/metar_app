# app/utils/file_util.py
import urllib.request
import json
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def read_zip_contents(zip_path: Path = None) -> list[str]:
    if zip_path is None:
        zip_path = DATA_DIR / "metar.zip"
    else:
        zip_path = Path(zip_path)

    if not zip_path.is_file():
        raise FileNotFoundError(f"ZIP-Datei nicht gefunden: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as z:
        txt_files = [f for f in z.namelist() if f.endswith(".txt")]
        lines = []
        for t in txt_files:
            with z.open(t) as fh:
                lines.extend(
                    [ln.decode("utf-8-sig").strip() for ln in fh.readlines() if ln.strip()]
                )
        return lines


def _query_metar_api(station_string: str) -> list[str]:
    """Fragt die aviationweather.gov-API für eine Kommaliste von ICAO-Codes ab."""
    url = f"https://aviationweather.gov/api/data/metar?ids={station_string}&format=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 204:
                return []
            json_data = json.loads(response.read().decode("utf-8"))

        raw_reports = []
        if isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, dict) and "rawOb" in item:
                    raw_reports.append(item["rawOb"])
        return raw_reports
    except Exception as e:
        raise RuntimeError(f"API-Fehler: {str(e)}")


def fetch_online_metar_by_country(country_prefix: str) -> list[str]:
    prefix = country_prefix.strip()

    station_map = {
        # USA — grosse Drehkreuze quer über den Kontinent
        "K": "KJFK,KLAX,KORD,KATL,KDFW,KSFO,KDEN,KSEA,KMIA,KBOS,KIAH,KLAS,KPHX,KMCO,KEWR",
        # Deutschland — alle grösseren Verkehrsflughäfen
        "ED": "EDDF,EDMA,EDDM,EDDH,EDDL,EDDK,EDDS,EDDB,EDDW,EDDN,EDDV,EDDP,EDDC,EDDR",
        # Schweiz
        "LS": "LSZH,LSGG,LSGC,LFSB,LSZB,LSZS,LSZA",
        # Österreich
        "LO": "LOWW,LOWS,LOWG,LOWI,LOWL,LOWK",
        # Grossbritannien
        "EG": "EGLL,EGKK,EGSS,EGCC,EGGD,EGPH,EGPF,EGBB,EGGW",
        # Frankreich
        "LF": "LFPG,LFPO,LFLL,LFMN,LFBO,LFRS,LFST,LFBD,LFMK",
        # Spanien
        "LE": "LEMD,LEBL,LEPA,LEAL,LEZL,LEMG,LEVC",
        # Italien
        "LI": "LIRF,LIML,LIPE,LIME,LIRN,LICJ",
        # Niederlande
        "EH": "EHAM,EHRD,EHEH,EHGG",
        # Belgien
        "EB": "EBBR,EBLG,EBAW,EBCI",
        # Mexiko
        "MM": "MMMX,MMUN,MMGL,MMMY,MMTJ,MMPR,MMSD,MMAA,MMTO,MMPB",
    }
    station_string = station_map.get(prefix)

    if station_string is None:
        raise ValueError(f"Unbekanntes Länderkürzel: '{prefix}'")

    return _query_metar_api(station_string)


def fetch_online_metar_single(station_id: str) -> list[str]:
    """Fragt die aktuelle METAR-Meldung für einen einzelnen ICAO-Code ab (z.B. 'EDMA')."""
    station_id = station_id.strip().upper()

    if not station_id:
        raise ValueError("Bitte einen ICAO-Code eingeben (z.B. EDMA).")
    if not (len(station_id) == 4 and station_id.isalpha()):
        raise ValueError(f"'{station_id}' ist kein gültiger ICAO-Code (4 Buchstaben, z.B. EDMA).")

    return _query_metar_api(station_id)
