from typing import List
from dcs.drawing.layer import Layer
from dcs.mapping import Point
from dcs.drawing import Rgba


def add_oblong(
    layer: Layer,
    p1: Point,
    p2: Point,
    radius: float,
    color: Rgba,
    thickness: float,
    fill: Rgba,
    text: str,
):
    hdg_p1_p2 = p1.heading_between_point(p2)
    points: List[Point] = []
    resolution = 30

    for i in range(0, resolution + 1):
        hdg = hdg_p1_p2 - 90 + i * (180 / resolution)
        points.append(p2.point_from_heading(hdg, radius))

    for i in range(0, resolution + 1):
        hdg = hdg_p1_p2 + 90 + i * (180 / resolution)
        points.append(p1.point_from_heading(hdg, radius))

    points.append(points[0] * 1)  # Copy

    # Transform points to local coordinates
    startPoint = points[0] * 1  # Copy
    for point in points:
        point.x -= startPoint.x
        point.y -= startPoint.y

    polygon = layer.add_freeform_polygon(
        startPoint, points, color=color, fill=fill, line_thickness=thickness
    )
    if text:
        polygon.name = text
        text_point = p1 * 0.7 + p2 * 0.3
        angle = hdg_p1_p2 - 90
        if angle > 90 or angle < -90:
            angle = (angle + 180) % 360
            text_point = p1 * 0.3 + p2 * 0.7
        layer.add_text_box(
            text_point,
            text,
            angle=angle,
            font_size=16,
            border_thickness=0,
            color=color,
            fill=Rgba(0, 0, 0, 0),
        )
    return polygon
