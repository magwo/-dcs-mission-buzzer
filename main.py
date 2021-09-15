from buzzer import Buzzer
from loggin_util import print_bold, print_warning
import dcs
import sys
import json
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

version = "1.0.0"
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
    buzzer.buzz(m, settings)

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
