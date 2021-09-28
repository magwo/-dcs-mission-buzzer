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
        print("Relocating", group)
        radius = Distance.from_nautical_miles(self.settings.get("carrier_relocation_radius_nm", 50))
        while len(group.points) < 2:
            print_warning(f"Carrier group {group.name} missing waypoint")
            group.add_point(MovingPoint())
        
        # TODO: More sophisticated heading+speed selection
        wind_speed = Speed.from_meters_per_second(self.wind_0m.speed)
        wind_heading = Heading(self.wind_0m.direction)
        carrier_heading = wind_heading.opposite
        carrier_speed = Speed.from_knots(max(10, 25 - wind_speed.knots))

        carrier_start_pos = group.position.point_from_heading(carrier_heading.opposite.degrees, radius.meters)
        carrier_end_pos = group.position.point_from_heading(carrier_heading.degrees, radius.meters)

        group.points[0].position = carrier_start_pos
        group.points[1].position = carrier_end_pos
        group.points[1].ETA_locked = False
        group.points[1].speed = carrier_speed.meters_per_second
        group.points[1].speed_locked = True
        