from dataclasses import dataclass
from dcs.point import MovingPoint

from dcs.ships import CVN_71, CVN_72, CVN_73, CVN_75, LHA_Tarawa, Stennis
from dcs.unitgroup import ShipGroup

from utils import Distance, Heading, Speed
from dcs.weather import Wind
from loggin_util import print_bold, print_warning
from dcs.mission import Mission



carrier_type_ids = [
    Stennis.id,
    CVN_71.id,
    CVN_72.id,
    CVN_73.id,
    CVN_75.id,
    LHA_Tarawa.id,
]

carrier_deck_angles: dict[str, int] = {
    Stennis.id: -9,
    CVN_71.id: -9,
    CVN_72.id: -9,
    CVN_73.id: -9,
    CVN_75.id: -9,
    LHA_Tarawa.id: 0,
}

@dataclass
class HeadingAndSpeed:
    heading: Heading
    speed: Speed


@dataclass
class CarrierRelocator:
    m: Mission
    wind_0m: Wind
    settings: dict

    def relocate_carrier_groups(self) -> None:
        m = self.m

        for coalition_name in m.coalition:
            for country_name in m.coalition[coalition_name].countries:
                country = m.coalition[coalition_name].countries[country_name]

                for shipGroup in country.ship_group:
                    for ship in shipGroup.units:
                        if ship.type in carrier_type_ids:
                            self.relocate_group(shipGroup)
                            break

                    
    def relocate_group(self, group: ShipGroup) -> None:
        print("Relocating", group.name)
        radius = Distance.from_nautical_miles(self.settings.get("carrier_relocation_radius_nm", 50))
        while len(group.points) < 2:
            print_warning(f"Carrier group {group.name} missing waypoint")
            group.add_point(MovingPoint())
        
        carrier = group.units[0]
        cruise = CarrierRelocator.get_carrier_cruise(self.wind_0m, carrier_deck_angles.get(carrier.type), Speed.from_knots(10), Speed.from_knots(25))
        print(f"Wind is {self.wind_0m.speed}m/s {self.wind_0m.direction}deg")
        print("Cruise is", cruise)

        carrier_start_pos = group.position.point_from_heading(cruise.heading.opposite.degrees, radius.meters)
        carrier_end_pos = group.position.point_from_heading(cruise.heading.degrees, radius.meters)

        group.points[0].position = carrier_start_pos
        group.points[1].position = carrier_end_pos
        group.points[1].ETA_locked = False
        group.points[1].speed = cruise.speed.meters_per_second
        group.points[1].speed_locked = True

        carrier.position = carrier_start_pos
        carrier.heading = cruise.heading.degrees

        # TODO: Preserve group formation when moving
        group.formation_star(cruise.heading.degrees, Distance.from_nautical_miles(1).meters)
        

    @staticmethod
    def get_carrier_cruise(wind: Wind, deck_angle: int, s_min: Speed, s_max: Speed) -> HeadingAndSpeed:
        print("Computing carrier cruise configuration")
        # TODO: More sophisticated heading+speed selection
        wind_speed = Speed.from_meters_per_second(wind.speed)
        carrier_speed = max(s_min, s_max - wind_speed)

        speed_factor = carrier_speed.knots / s_max.knots
        angle_offset = deck_angle * (1.0 - speed_factor)

        wind_heading = Heading(wind.direction)
        carrier_heading = Heading(wind_heading.opposite.degrees - angle_offset)

        return HeadingAndSpeed(carrier_heading, carrier_speed)