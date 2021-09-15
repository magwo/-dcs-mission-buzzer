import datetime
import random
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

class Buzzer:
    def buzz(self, m: Mission, settings: dict):
        seasonal_conditions = Buzzer.get_seasonal_conditions(m.terrain)
        date = Buzzer.get_random_date(settings.get("random_date_range").get("start"), settings.get("random_date_range").get("end"))
        day_time_chances = settings.get("day_time_chances")
        time_of_day = random.choices(
            list(day_time_chances.keys()), weights=list(day_time_chances.values())
        )[0]
        time_of_day = TimeOfDay[time_of_day]
        conditions = Conditions.generate(seasonal_conditions, date, time_of_day)
        
        print_bold("Conditions as follows!")
        print("Date and time:", conditions.start_time)
        print("Wind at 0m:", conditions.weather.wind.at_0m.__dict__)
        print("Wind at 2000m:", conditions.weather.wind.at_2000m.__dict__)
        print("Wind at 8000m:", conditions.weather.wind.at_8000m.__dict__)
        print("Clouds:", conditions.weather.clouds)
        if conditions.weather.clouds:
            print("Cloud preset:", conditions.weather.clouds.preset.__dict__)
        print("Fog:", conditions.weather.fog)
        print("Atmospheric:", conditions.weather.atmospheric)
        EnvironmentGenerator(m, conditions).generate()


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
    def get_random_date(start_date_iso: str, end_date_iso: str) -> SeasonalConditions:
        def random_date(start, end):
            """Generate a random datetime between `start` and `end`"""
            return start + datetime.timedelta(
                # Get a random amount of seconds between `start` and `end`
                seconds=random.randint(0, int((end - start).total_seconds())),
            )
        start_date = datetime.datetime.fromisoformat(start_date_iso)
        end_date = datetime.datetime.fromisoformat(end_date_iso)
        return random_date(start_date, end_date)