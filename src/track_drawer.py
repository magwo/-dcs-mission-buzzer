from dataclasses import dataclass
from dcs import task
from dcs.drawing.drawing import LineStyle
from dcs.drawing.drawings import StandardLayer
from dcs.unitgroup import Group
from drawing import add_oblong

from utils import Distance
from dcs.mission import Mission
from dcs.drawing import Rgba


INCLUDED_TASKS = set([task.Refueling, task.AWACS])


@dataclass
class TrackDrawer:
    m: Mission
    settings: dict

    def draw_tracks(self) -> None:
        m = self.m
        excluded_group_names = self.settings.get("excluded_drawing_group_names", "").split(",")

        for coalition_name in m.coalition:
            for country_name in m.coalition[coalition_name].countries:
                country = m.coalition[coalition_name].countries[country_name]
                for group in country.plane_group:
                    if group.name not in excluded_group_names:
                        for plane in group.units:
                            if len(set(plane.unit_type.tasks) & INCLUDED_TASKS) > 0:
                                self.draw_track(group, 1, 2)
                                break

    def draw_track(self, group: Group, wp1_index: int, wp2_index: int) -> None:
        altitude = Distance(group.points[wp1_index].alt).feet
        altitude_rounded = round(altitude / 1000)
        path_name = f"{group.name} {altitude_rounded} 000'"
        layer = self.m.drawings.get_layer(StandardLayer.Common)
        polygon = add_oblong(
            layer,
            group.points[wp1_index].position,
            group.points[wp2_index].position,
            Distance.from_nautical_miles(5).meters,
            Rgba(50, 50, 50, 255),
            3,
            Rgba(50, 50, 50, 30),
            path_name,
        )
        polygon.line_style = LineStyle.Dot
