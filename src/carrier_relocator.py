from dataclasses import dataclass
from typing import List
from dcs.drawing.drawings import StandardLayer
from dcs.mapping import Point
from dcs.point import MovingPoint

from dcs.ships import CVN_71, CVN_72, CVN_73, CVN_75, LHA_Tarawa, Stennis, Forrestal
from dcs.unitgroup import Group, ShipGroup
from drawing import add_oblong
from trigonometric_carrier_cruise import get_ship_course_and_speed

from utils import Distance, Heading, Speed, knots
from dcs.weather import Wind
from loggin_util import print_bold, print_warning
from dcs.mission import Mission
from dcs.drawing import Rgba


carrier_type_ids = [
    Stennis.id,
    Forrestal.id,
    CVN_71.id,
    CVN_72.id,
    CVN_73.id,
    CVN_75.id,
    LHA_Tarawa.id,
]

carrier_deck_angles: dict[str, float] = {
    Stennis.id: -9.12,
    Forrestal.id: -9.12,
    CVN_71.id: -9.12,
    CVN_72.id: -9.12,
    CVN_73.id: -9.12,
    CVN_75.id: -9.12,
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
        radius = Distance.from_nautical_miles(
            self.settings.get("carrier_relocation_radius_nm", 50)
        )
        while len(group.points) < 4:
            print_warning(f"Carrier group {group.name} missing waypoint")
            group.add_point(MovingPoint())

        carrier = group.units[0]
        cruise = CarrierRelocator.get_carrier_cruise(
            self.wind_0m, carrier_deck_angles[carrier.type], Speed.from_knots(25)
        )
        print(f"Wind is {self.wind_0m.speed}m/s {self.wind_0m.direction}deg")
        print("Cruise is", cruise)

        carrier_start_pos = group.position.point_from_heading(
            cruise.heading.opposite.degrees, radius.meters
        )
        carrier_end_pos = group.position.point_from_heading(
            cruise.heading.degrees, radius.meters
        )

        group_heading_before_change = group.points[0].position.heading_between_point(
            group.points[1].position
        )
        group_position_before_change = group.points[0].position

        group.points[0].position = carrier_start_pos
        group.points[0].speed = cruise.speed.meters_per_second
        
        group.points[1].position = carrier_end_pos
        group.points[1].ETA_locked = False
        group.points[1].speed = cruise.speed.meters_per_second
        group.points[1].speed_locked = True

        group.points[2].position = carrier_start_pos
        group.points[2].speed = knots(50)
        group.points[2].ETA_locked = False
        group.points[2].speed_locked = True

        group.points[3].position = carrier_end_pos
        group.points[3].ETA_locked = False
        group.points[3].speed = cruise.speed.meters_per_second
        group.points[3].speed_locked = True

        # These are probably not needed anymore
        # carrier.position = carrier_start_pos
        # carrier.heading = cruise.heading.degrees

        position_change = carrier_start_pos - group_position_before_change
        for unit in group.units:
            unit.position = unit.position + position_change

        print(f"Heading before {group_heading_before_change}")
        heading_change = cruise.heading.degrees - group_heading_before_change
        print(f"Heading change {heading_change}")
        CarrierRelocator.rotate_group_around(
            group, group.points[0].position, heading_change
        )
        print(
            "Heading after change",
            group.points[0].position.heading_between_point(group.points[1].position),
        )

        path_name = group.name + " carrier group"
        layer = self.m.drawings.get_layer(StandardLayer.Common)
        add_oblong(
            layer,
            carrier_start_pos,
            carrier_end_pos,
            Distance.from_nautical_miles(3).meters,
            Rgba(50, 50, 50, 255),
            1,
            Rgba(50, 50, 50, 30),
            path_name,
        )
        layer.add_arrow(
            carrier_start_pos,
            carrier_start_pos.heading_between_point(carrier_end_pos) - 90,
            Distance.from_nautical_miles(5).meters,
            fill=Rgba(50, 50, 50, 90),
            line_thickness=0,
        )

    @staticmethod
    def get_carrier_cruise(
        wind: Wind, deck_angle: float, desired_apparent_wind: Speed
    ) -> HeadingAndSpeed:
        wind_speed = Speed.from_meters_per_second(wind.speed)

        heading, speed, apparent_wind_angle = get_ship_course_and_speed(
            wind.direction, wind_speed.knots, desired_apparent_wind.knots
        )

        # Quick hack for Tarawa
        if deck_angle == 0:
            wind_heading = Heading(wind.direction)
            heading = wind_heading.opposite.degrees
            print("Tara Heading is", heading)

        solution = HeadingAndSpeed(
            Heading.from_degrees(heading), Speed.from_knots(speed)
        )

        print("Trig cruise is", solution)

        return solution

    @staticmethod
    def rotate_group_around(group: Group, pivot: Point, degrees_change: int):
        # My fear was that using sin/cos would result in incorrect
        # transforms when not near equator. Polar coordinates (heading + distance)
        # should resolve that, if the Point functions are implemented correctly.
        # I think they're not, but this code at least doesn't prevent correct transform.
        # Maybe DCS doesn't even use mercator projection.
        for unit in group.units:
            distance = pivot.distance_to_point(unit.position)
            heading = pivot.heading_between_point(unit.position)
            new_heading = Heading.from_degrees(heading + degrees_change).degrees

            unit.position = pivot.point_from_heading(new_heading, distance)
            unit.heading = Heading.from_degrees(unit.heading + degrees_change).degrees
