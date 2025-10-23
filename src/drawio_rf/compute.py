from .reader import read_drawio
from .processor import build_df
from .writer import write_drawio
import os
import sys
import json
import glob
import warnings
import tkinter as tk
from tkinter import filedialog

# load all json files from db folder
BASE_DIR =  os.path.dirname(os.path.abspath(__file__))

JSON = os.path.join(BASE_DIR, '..', '..', "db", "*.json")

json_files = glob.glob(JSON)
component_db = {}
for j in json_files:
    with open(j, "r") as f:
        data = json.load(f)
        for key, value in data.items():
            if key in component_db:
                warnings.warn(f"Duplicate key '{key}' found in file '{j}'. Overwriting.")
            component_db[key] = value

def compute_drawio(drawio, json=component_db, outpath=None):
    blocks = read_drawio(drawio)
    df_circuit = build_df(blocks, json)
    return write_drawio(df_circuit, drawio, outpath)

def choose_file_and_run():
    # If no file path was passed as argument, open a file dialog
    file_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not file_path:
        root = tk.Tk()
        root.withdraw()  # Hide the main Tk window

        file_path = filedialog.askopenfilename(
            title="Select Draw.io XML file",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if not file_path:
            print("No file selected.")
            return

    compute_drawio(file_path)
