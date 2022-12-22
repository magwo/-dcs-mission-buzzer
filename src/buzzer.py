from dataclasses import dataclass
import datetime
import random
from utils import Heading, Speed

from dcs.weather import Wind
from loggin_util import print_bold
from environmentgen import EnvironmentGenerator
from weather import Conditions, TimeOfDay
from seasonalconditions.seasonalconditions import SeasonalConditions
from dcs.mission import Mission
from dcs.terrain.terrain import Terrain
from dcs.terrain import (
    caucasus,
    nevada,
    normandy,
    persiangulf,
    syria,
    thechannel,
    marianaislands,
)


@dataclass(frozen=True)
class BuzzResult:
    theater: str
    date: str
    conditions: Conditions

    def toDict(self) -> dict:
        return {
            "theater": self.theater,
            "date": self.date,
            "time": self.conditions.start_time.time().isoformat(),
            "temperature_c": f"{self.conditions.weather.atmospheric.temperature_celsius:.0f}",
            "qnh_inches_hg": f"{self.conditions.weather.atmospheric.qnh.inches_hg:.2f}",
            "qnh_hecto_pascals": f"{self.conditions.weather.atmospheric.qnh.hecto_pascals:.1f}",
            "precipitation": self.conditions.weather.clouds.precipitation.name.replace(
                "_", ""
            )
            if self.conditions.weather.clouds
            else "None",
            "cloud_preset": self.conditions.weather.clouds.preset.ui_name
            if self.conditions.weather.clouds and self.conditions.weather.clouds.preset
            else "None",
            "cloud_base": str(self.conditions.weather.clouds.base)
            if self.conditions.weather.clouds
            else "-",
            "fog_visibility_meters": str(
                int(self.conditions.weather.fog.visibility.meters)
            )
            if self.conditions.weather.fog
            else "-",
            "fog_thickness": str(self.conditions.weather.fog.thickness)
            if self.conditions.weather.fog
            else "-",
            "wind_0m": self.wind_dict(self.conditions.weather.wind.at_0m),
            "wind_2000m": self.wind_dict(self.conditions.weather.wind.at_2000m),
            "wind_8000m": self.wind_dict(self.conditions.weather.wind.at_8000m),
        }

    def wind_dict(self, wind: Wind):
        return {
            "speed_mps": f"{wind.speed:.1f}",
            "speed_kts": f"{Speed.from_meters_per_second(wind.speed).knots:.0f}",
            "direction": str(int(wind.direction)),
            "direction_opposite": str(int(Heading(wind.direction).opposite.degrees)),
        }


class Buzzer:
    def buzz(self, m: Mission, settings: dict, clearweather=False, force_night=False) -> BuzzResult:
        if settings.get("random_seed_method") == "THEATER_AND_TODAYS_DATE":
            seed = f"{m.terrain.name}_{str(datetime.datetime.now().date())}"
            print("Seed is", seed)
            random.seed(seed)

        seasonal_conditions = Buzzer.get_seasonal_conditions(m.terrain)
        if settings.get("date_pick_method") == "COMPRESSED_SEASONS":
            date = Buzzer.get_compressed_date(
                settings.get("date_range").get("start"),
                settings.get("date_range").get("end"),
                datetime.datetime.now().date(),
                12
            )
        else:
            date = Buzzer.get_random_date(
                settings.get("date_range").get("start"),
                settings.get("date_range").get("end"),
            )
        if not force_night:
            day_time_chances = settings.get("day_time_chances")
        else:
            day_time_chances = {"Dawn": 0, "Day": 0, "Dusk": 0, "Night": 100}

        time_of_day = random.choices(
            list(day_time_chances.keys()), weights=list(day_time_chances.values())
        )[0]
        time_of_day = TimeOfDay[time_of_day]
        
        # Handle forced night wind - used to avoid ILS/RWY problems in DCS
        min_wind_dir = Heading.from_degrees(0)
        max_wind_dir = Heading.from_degrees(359)
        min_wind_speed = Speed.from_meters_per_second(0)
        if time_of_day == TimeOfDay.Night and settings.get("night_forced_wind") is not None:
            min_wind_dir = Heading.from_degrees(settings.get("night_forced_wind").get("min_direction_towards", 0))
            max_wind_dir = Heading.from_degrees(settings.get("night_forced_wind").get("max_direction_towards", 359))
            min_wind_speed = Speed.from_meters_per_second(settings.get("night_forced_wind").get("min_speed_mps", 0))

        print("Min wind dir", min_wind_dir)
        print("Max wind dir", max_wind_dir)
        print("Min wind spd", min_wind_speed)
        print("Time of day", time_of_day)
        conditions = Conditions.generate(seasonal_conditions, date, time_of_day, clearweather, min_wind_dir, max_wind_dir, min_wind_speed)

        print_bold("Conditions as follows!")
        print("Date and time:", conditions.start_time)
        print("Wind at 0m:", conditions.weather.wind.at_0m.__dict__)
        print("Wind at 2000m:", conditions.weather.wind.at_2000m.__dict__)
        print("Wind at 8000m:", conditions.weather.wind.at_8000m.__dict__)
        print("Clouds:", conditions.weather.clouds)
        if conditions.weather.clouds and conditions.weather.clouds.preset:
            print("Cloud preset:", conditions.weather.clouds.preset.__dict__)
        print("Fog:", conditions.weather.fog)
        print("Atmospheric:", conditions.weather.atmospheric)
        EnvironmentGenerator(m, conditions).generate()

        type_suffix = " clear weather" if clearweather else ""
        return BuzzResult(m.terrain.name + type_suffix, str(date.date()), conditions)

    @staticmethod
    def get_seasonal_conditions(terrain: Terrain) -> SeasonalConditions:
        if terrain.name == caucasus.Caucasus.__name__:
            from seasonalconditions.caucasus import CONDITIONS

            return CONDITIONS
        elif terrain.name == nevada.Nevada.__name__:
            from seasonalconditions.nevada import CONDITIONS

            return CONDITIONS
        elif terrain.name == normandy.Normandy.__name__:
            from seasonalconditions.normandy import CONDITIONS

            return CONDITIONS
        elif terrain.name == persiangulf.PersianGulf.__name__:
            from seasonalconditions.persiangulf import CONDITIONS

            return CONDITIONS
        elif terrain.name == syria.Syria.__name__:
            from seasonalconditions.syria import CONDITIONS

            return CONDITIONS
        elif terrain.name == thechannel.TheChannel.__name__:
            from seasonalconditions.thechannel import CONDITIONS

            return CONDITIONS
        elif terrain.name == marianaislands.MarianaIslands.__name__:
            from seasonalconditions.marianaislands import CONDITIONS

            return CONDITIONS
        raise ValueError(terrain)

    @staticmethod
    def get_random_date(start_date_iso: str, end_date_iso: str) -> datetime.datetime:
        def random_date(start, end):
            """Generate a random datetime between `start` and `end`"""
            return start + datetime.timedelta(
                # Get a random amount of seconds between `start` and `end`
                seconds=random.randint(0, int((end - start).total_seconds())),
            )

        start_date = datetime.datetime.fromisoformat(start_date_iso)
        end_date = datetime.datetime.fromisoformat(end_date_iso)
        return random_date(start_date, end_date)

    @staticmethod
    def get_compressed_date(start_date_iso: str, end_date_iso: str, today_date_irl: datetime, compression_factor: int) -> datetime.datetime:
        start_date = datetime.datetime.fromisoformat(start_date_iso)
        end_date = datetime.datetime.fromisoformat(end_date_iso)
        num_days = (end_date - start_date).days
        irl_day_of_year = today_date_irl.timetuple().tm_yday
        chosen_day_number = (irl_day_of_year * compression_factor) % num_days
        result_date = start_date + datetime.timedelta(days=chosen_day_number)
        return result_date
