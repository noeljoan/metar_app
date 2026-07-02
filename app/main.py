# app/main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import threading
import time
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

try:
    from .utils.file_util import (
        read_zip_contents,
        fetch_online_metar_by_country,
        fetch_online_metar_single,
    )
    from .models.metar import parse_metar, metar_to_dict
except ImportError:
    # Einfache Fallback-Funktionen, falls die Module nicht gefunden werden
    def read_zip_contents(filepath):
        return [
            "METAR EDDF 011200Z 24010KT 9999 FEW030 15/08 Q1013=",
            "METAR EDDF 011300Z 25012KT 9000 -RA SCT025 14/09 Q1012=",
        ]

    def fetch_online_metar_by_country(country_prefix):
        return []

    def fetch_online_metar_single(station_id):
        return []

    def parse_metar(raw_str):
        return raw_str

    def metar_to_dict(parsed_obj):
        parts = parsed_obj.split()
        station = parts[1] if len(parts) > 1 else "UNKN"
        return {
            "station": station, "time": datetime.now().strftime("%H:%M"),
            "wind": "12 KT", "temp": 15.0, "pressure": 1013.0, "visibility": 9999.0,
            "clouds": "keine Angabe", "trend": "", "remarks": "",
        }


class METARViewer(tk.Tk):
    # Spalten der Daten-Tabelle inkl. individueller Breite
    TABLE_COLUMNS = {
        "station": 90,
        "time": 70,
        "wind": 90,
        "temp": 70,
        "pressure": 80,
        "visibility": 90,
        "clouds": 160,
        "trend": 70,
        "remarks": 260,
    }

    def __init__(self):
        super().__init__()
        self.title("METAR-Desktop V1.2 - (c) 2026 Noel Joan ")
        self.geometry("1200x900")

        self.data = []
        self.ml_model = None
        self.scaler = None
        self.model_trained = False
        self.simulation_running = False

        self.setup_ui()

    def setup_ui(self):
        # Top Button Bar / Steuerung
        btn_frame = ttk.LabelFrame(self, text=" Datenquelle wählen ")
        btn_frame.pack(fill="x", padx=10, pady=5)

        # Lokale Dateien laden
        ttk.Button(btn_frame, text="ZIP-Datei laden", command=self.load_zip_file).pack(
            side="left", padx=5, pady=5
        )

        # Trennlinie für Optik
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10, pady=5)

        # Online Live-Daten nach Land
        ttk.Label(btn_frame, text="Land wählen:").pack(side="left", padx=5)

        self.country_box = ttk.Combobox(btn_frame, state="readonly", width=18)
        self.country_box["values"] = (
            "Deutschland (ED)",
            "Mexiko (MM)",
            "USA (K)",
            "Österreich (LO)",
            "Schweiz (LS)",
            "Großbritannien (EG)",
            "Frankreich (LF)",
            "Spanien (LE)",
            "Italien (LI)",
            "Niederlande (EH)",
            "Belgien (EB)",
        )
        self.country_box.current(0)  # Standardwert: Deutschland
        self.country_box.pack(side="left", padx=5)

        ttk.Button(
            btn_frame, text="Live-Daten laden", command=self.load_online_country_data
        ).pack(side="left", padx=5)

        # Einzelne Station live abrufen
        single_frame = ttk.LabelFrame(self, text=" Einzelne Station live abrufen ")
        single_frame.pack(fill="x", padx=10, pady=(0, 5))

        ttk.Label(single_frame, text="Flughafen-ICAO (z.B. EDMA):").pack(
            side="left", padx=5, pady=5
        )
        self.station_entry = ttk.Entry(single_frame, width=15)
        self.station_entry.insert(0, "EDMA")
        self.station_entry.pack(side="left", padx=5, pady=5)
        self.station_entry.bind("<Return>", lambda event: self.load_single_station())

        ttk.Button(
            single_frame, text="Wetter laden", command=self.load_single_station
        ).pack(side="left", padx=5, pady=5)

        # Funktionen & Simulation
        ttk.Button(
            btn_frame, text="Simulation starten", command=self.toggle_simulation
        ).pack(side="right", padx=5, pady=5)
        ttk.Button(
            btn_frame, text="KI-Modell trainieren", command=self.train_prediction_model
        ).pack(side="right", padx=5, pady=5)

        # Notebook für Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # TAB 1: Tabelle
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Daten-Tabelle")

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=tuple(self.TABLE_COLUMNS.keys()),
            show="headings",
        )
        for col, width in self.TABLE_COLUMNS.items():
            self.tree.heading(col, text=col.title())
            anchor = "w" if col == "remarks" else "center"
            self.tree.column(col, width=width, anchor=anchor)

        v_scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # TAB 2: Visualisierung (Matplotlib)
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Visualisierung")

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Temperatur- & Luftdruckverlauf")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # TAB 3: KI-Vorhersage
        self.ml_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ml_frame, text="KI-Vorhersage")

        ttk.Label(
            self.ml_frame,
            text="Aktuelle Stations-Parameter eingeben für Sichtweiten-Vorhersage:",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

        self.input_temp = self.create_input_field(self.ml_frame, "Temperatur (°C):", "15")
        self.input_press = self.create_input_field(self.ml_frame, "Luftdruck (hPa):", "1013")

        ttk.Button(
            self.ml_frame, text="Sichtweite vorhersagen", command=self.predict_visibility
        ).pack(pady=15)
        self.lbl_prediction = ttk.Label(
            self.ml_frame, text="Vorhersage: Noch kein Modell trainiert", font=("Arial", 12)
        )
        self.lbl_prediction.pack(pady=5)

    def create_input_field(self, parent, label_text, default_val):
        frame = ttk.Frame(parent)
        frame.pack(pady=5, fill="x", padx=100)
        ttk.Label(frame, text=label_text, width=20).pack(side="left")
        entry = ttk.Entry(frame)
        entry.insert(0, default_val)
        entry.pack(side="right", expand=True, fill="x")
        return entry

    def _add_reports_to_table(self, raw_reports):
        self.data.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for report in raw_reports:
            parsed = parse_metar(report)
            data_dict = metar_to_dict(parsed)
            self.data.append(data_dict)

            self.tree.insert(
                "", "end",
                values=tuple(data_dict.get(col, "") for col in self.TABLE_COLUMNS),
            )

        self.update_charts()

    def load_zip_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip")])
        if not file_path:
            return

        try:
            raw_reports = read_zip_contents(file_path)
            self._add_reports_to_table(raw_reports)
            messagebox.showinfo("Erfolg", f"{len(raw_reports)} METAR-Berichte erfolgreich geladen!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht gelesen werden:\n{str(e)}")

    def load_online_country_data(self):
        selected_text = self.country_box.get()
        start_idx = selected_text.find("(") + 1
        end_idx = selected_text.find(")")
        country_prefix = selected_text[start_idx:end_idx]

        self.title(f"METAR-Desktop - Lade Live-Daten für {country_prefix}...")

        try:
            raw_reports = fetch_online_metar_by_country(country_prefix)

            if not raw_reports:
                messagebox.showwarning(
                    "Keine Daten",
                    f"Für das Länderkürzel '{country_prefix}' wurden aktuell keine METAR-Daten gefunden.",
                )
                return

            self._add_reports_to_table(raw_reports)
            messagebox.showinfo("Erfolg", f"Erfolgreich {len(raw_reports)} Live-METARs geladen!")

        except Exception as e:
            messagebox.showerror("Online-Fehler", f"Live-Daten konnten nicht abgerufen werden:\n{str(e)}")
        finally:
            self.title("METAR-Desktop")

    def load_single_station(self):
        station_id = self.station_entry.get().strip().upper()

        self.title(f"METAR-Desktop - Lade Live-Daten für {station_id}...")

        try:
            raw_reports = fetch_online_metar_single(station_id)

            if not raw_reports:
                messagebox.showwarning(
                    "Keine Daten",
                    f"Für die Station '{station_id}' wurde aktuell kein METAR gefunden.",
                )
                return

            self._add_reports_to_table(raw_reports)
            messagebox.showinfo("Erfolg", f"Wetterdaten für {station_id} geladen!")

        except ValueError as e:
            messagebox.showerror("Eingabefehler", str(e))
        except Exception as e:
            messagebox.showerror("Online-Fehler", f"Live-Daten konnten nicht abgerufen werden:\n{str(e)}")
        finally:
            self.title("METAR-Desktop")

    def update_charts(self):
        if not self.data:
            return
        df = pd.DataFrame(self.data)
        self.ax.clear()

        self.ax.plot(
            df["station"], df["temp"], marker="o", color="orange",
            linestyle="None", label="Temperatur (°C)",
        )

        self.ax.set_ylabel("Grad Celsius")
        self.ax.set_xlabel("Flughafen-Station")
        self.ax.set_title("Aktuelle Temperaturen nach Station")
        self.ax.legend(loc="upper left")
        self.ax.grid(True, linestyle="--", alpha=0.6)

        # Verhindert, dass Stationsnamen am Rand abgeschnitten werden
        self.fig.tight_layout()

        self.canvas.draw()

    def toggle_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
            return

        self.simulation_running = True
        threading.Thread(target=self.run_realtime_simulation, daemon=True).start()

    def run_realtime_simulation(self):
        # Simuliert eingehende Live-Wetterdaten im Sekundentakt
        station_names = ["EDDF", "EDDM", "EDDH", "EDDL"]
        cloud_options = ["CAVOK", "FEW030", "SCT025", "BKN020CB", "OVC080", "SKC"]
        while self.simulation_running:
            mock_dict = {
                "station": np.random.choice(station_names),
                "time": datetime.now().strftime("%H:%M:%S"),
                "wind": f"{np.random.randint(5, 25)} KT",
                "temp": round(np.random.uniform(5, 25), 1),
                "pressure": round(np.random.uniform(990, 1030), 1),
                "visibility": float(np.random.choice([9999, 5000, 3000, 800])),
                "clouds": np.random.choice(cloud_options),
                "trend": np.random.choice(["", "", "NOSIG"]),
                "remarks": "",
            }
            self.data.append(mock_dict)

            # UI-Änderungen sicher aus dem Thread übergeben
            self.after(0, lambda d=mock_dict: self.tree.insert(
                "", 0,
                values=tuple(d.get(col, "") for col in self.TABLE_COLUMNS),
            ))
            self.after(0, self.update_charts)
            time.sleep(1.5)

    def train_prediction_model(self):
        # Falls keine echten Daten da sind, erzeugen wir synthetische Trainingsdaten
        if len(self.data) < 10:
            messagebox.showwarning("Wenig Daten", "Generiere künstliche Daten für das KI-Modell-Training...")
            X = np.random.rand(100, 2) * [20, 40] + [5, 990]  # Temp, Pressure
            y = X[:, 0] * 300 + X[:, 1] * 2 + np.random.randn(100) * 500  # Sichtweite
        else:
            df = pd.DataFrame(self.data)
            X = df[["temp", "pressure"]].values
            y = df["visibility"].values

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.ml_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.ml_model.fit(X_scaled, y)
        self.model_trained = True

        messagebox.showinfo("KI-Modell", "Random-Forest-Modell erfolgreich trainiert!")

    def predict_visibility(self):
        if not self.model_trained:
            messagebox.showerror("Fehler", "Bitte trainiere zuerst das KI-Modell!")
            return
        try:
            t = float(self.input_temp.get())
            p = float(self.input_press.get())

            features = np.array([[t, p]])
            features_scaled = self.scaler.transform(features)
            prediction = self.ml_model.predict(features_scaled)[0]

            self.lbl_prediction.config(text=f"Vorhergesagte Sichtweite: {round(prediction, 1)} Meter")
        except ValueError:
            messagebox.showerror("Eingabefehler", "Bitte gültige Zahlenwerte eintragen.")
