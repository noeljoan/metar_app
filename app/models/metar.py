# app/models/metar.py
import re
from datetime import datetime


def parse_metar(raw_str: str) -> dict:
    clean_str = raw_str.strip().rstrip("=")
    parts = clean_str.split()

    data = {
        "station": "UNKN",
        "time": "00:00",
        "wind": "00000KT",
        "temp": 0.0,
        "pressure": 1013.2,
        "visibility": 9999.0
    }

    if not parts:
        return data

    # Überspringe das Wort "METAR", wenn es am Anfang steht
    if parts[0] == "METAR" and len(parts) > 1:
        data["station"] = parts[1]
    else:
        data["station"] = parts[0]

    # Reguläre Ausdrücke für die verschiedenen METAR-Felder
    time_pattern = re.compile(r"^\d{6}Z$")               # z.B. 011951Z
    wind_pattern = re.compile(r"^\d{5}(G\d{2})?KT$")      # z.B. 18015KT
    vis_sm_pattern = re.compile(r"^(\d+)SM$")             # z.B. 10SM (US-Format)
    vis_m_pattern = re.compile(r"^(\d{4})$")              # z.B. 9999 / 0800 (EU-Format, Meter)
    temp_pattern = re.compile(r"^(M?\d{2})/(M?\d{2})$")   # z.B. 28/16
    press_alt_pattern = re.compile(r"^A(\d{4})$")         # z.B. A3005 (inHg)
    press_qnh_pattern = re.compile(r"^Q(\d{4})$")         # z.B. Q1013 (hPa)

    for part in parts:
        if time_pattern.match(part):
            data["time"] = f"{part[2:4]}:{part[4:6]}"

        elif wind_pattern.match(part):
            data["wind"] = part

        elif vis_sm_pattern.match(part):
            match = vis_sm_pattern.match(part)
            miles = int(match.group(1))
            data["visibility"] = float(miles * 1609.34)

        elif temp_pattern.match(part):
            match = temp_pattern.match(part)
            t_str = match.group(1)
            temp = -int(t_str[1:]) if t_str.startswith("M") else int(t_str)
            data["temp"] = float(temp)

        elif press_alt_pattern.match(part):
            match = press_alt_pattern.match(part)
            alt_val = int(match.group(1)) / 100.0
            data["pressure"] = round(alt_val * 33.8639, 1)

        elif press_qnh_pattern.match(part):
            match = press_qnh_pattern.match(part)
            data["pressure"] = float(match.group(1))

        elif vis_m_pattern.match(part):
            # EU-Format: 4-stellige Sichtweite in Metern (z.B. 9999 = 10km+, 0800 = 800m)
            data["visibility"] = float(int(part))

    return data


def metar_to_dict(parsed_obj: dict) -> dict:
    """
    Reicht das geparste Dictionary direkt weiter (stellt die Kompatibilität mit
    main.py her).
    """
    return parsed_obj
