# app/utils/gui_util.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def create_main_window(title="METAR-Viewer"):
    root = tk.Tk()
    root.title(title)
    root.geometry("800x600")
    return root


def add_treeview(parent):
    columns = ("station", "time", "wind", "temp", "pressure")
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.title())
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True)
    return tree


def show_error(msg, title="Fehler"):
    messagebox.showerror(title, msg)


def ask_directory(msg="Ordner mit METAR-Daten auswählen"):
    return filedialog.askdirectory(title=msg)
