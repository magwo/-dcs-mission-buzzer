from datetime import datetime
import os
from buzzer import Buzzer
from carrier_relocator import CarrierRelocator
from loggin_util import print_bold, print_warning
import dcs
import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

version = "1.2.0"
print_bold(f"DCS Mission Buzzer v{version} by Mags")

in_filename = sys.argv[1] if len(sys.argv) > 1 else None
if not in_filename:
    print_bold("Select mission file")
    in_filename = filedialog.askopenfilename(title="Select mission file", filetypes=[('Mission files', '.miz')])

if not in_filename:
    sys.exit(1)

m = dcs.Mission()
print("Attempting to load mission file", in_filename)
m.load_file(in_filename)
print("Loaded mission file", in_filename)

with open('settings.json', "r") as f:
    json_content = f.read()
    settings = json.loads(json_content)
    buzzer = Buzzer()
    result = buzzer.buzz(m, settings)

    if settings.get("relocate_carrier_groups", False):
        relocator = CarrierRelocator(m, result.conditions.weather.wind.at_0m, settings)
        relocator.relocate_carrier_groups()

    if settings.get("write_result_json"):
        filename = f"{result.theater}{datetime.now().date().isoformat()}.json"
        file_path = Path(settings.get("result_json_path"), filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as result_file:
            json.dump(result.toDict(), result_file, ensure_ascii=False, indent=4)

out_filename = sys.argv[2] if len(sys.argv) > 2 else None
if not out_filename:
    print_bold("Select file to save mission as")
    out_filename = filedialog.asksaveasfilename(title="Save mission as", filetypes=[('Mission files', '.miz')], initialfile=in_filename)

if out_filename:
    print("Attempting to save to {}...".format(out_filename))
    m.save(out_filename)
    print("Saved to {}".format(out_filename))
else:
    print("Dry run was completed")
