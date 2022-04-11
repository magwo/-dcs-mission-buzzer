from datetime import datetime
import os
from buzzer import Buzzer
from carrier_relocator import CarrierRelocator
from loggin_util import print_bold
import dcs
import json
import argparse
from pathlib import Path
from map_limiter import MapLimiter

from track_drawer import TrackDrawer

version = "1.4.0"
print_bold(f"DCS Mission Buzzer v{version} by Mags")

parser = argparse.ArgumentParser(description='"Buzzes" a DCS miz file with region-like and season-like random weather - temperature, winds, clouds, pressure and more. Will also relocate carriers to be moving with correct wind-over-deck.')
parser.add_argument('--clearweather', dest='clearweather', action='store_true', default=False,
                    help='Whether to generate random but clear weather')
parser.add_argument('--forcenight', dest='forcenight', action='store_true', default=False,
                    help='Whether to set start time to night time')
parser.add_argument('--weatherreport', dest='weatherreport', action='store_true', default=False,
                    help='Whether to generate weather report file')
parser.add_argument('--limitmap', dest='limitmap', action='store_true', default=False,
                    help='Whether to limit F10 map to see no units')
parser.add_argument('input_filename', type=str, help='Input miz file path')
parser.add_argument('output_filename', nargs='?', type=str, default=None, help='Output miz file path. If omitted, a dry run will be performed')

args = parser.parse_args()

m = dcs.Mission()
print("Attempting to load mission file", args.input_filename)
m.load_file(args.input_filename)
print("Loaded mission file", args.input_filename)

with open("settings.json", "r") as f:
    json_content = f.read()
    settings = json.loads(json_content)
    buzzer = Buzzer()
    result = buzzer.buzz(m, settings, clearweather=args.clearweather, force_night=args.forcenight)

if args.limitmap:
    map_limiter = MapLimiter(m)
    map_limiter.limit_map()

if settings.get("relocate_carrier_groups", False):
    relocator = CarrierRelocator(m, result.conditions.weather.wind.at_0m, settings)
    relocator.relocate_carrier_groups()

if settings.get("draw_tanker_tracks", True):
    track_drawer = TrackDrawer(m, settings)
    track_drawer.draw_tracks()

out_filename = args.output_filename

if out_filename:
    print("Attempting to save to {}...".format(out_filename))
    m.save(out_filename)
    print("Saved to {}".format(out_filename))
else:
    print("Dry run was completed")

if settings.get("write_result_json") and args.weatherreport:
    filename = f"{result.theater}{datetime.now().date().isoformat()}.json"
    file_path = Path(settings.get("result_json_path"), filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as result_file:
        json.dump(result.toDict(), result_file, ensure_ascii=False, indent=4)
